import numpy as np
import elephant
#must import elephant prior to matplotlib else plt.ion() doesn't work properly
import network_analysis as na
import ep_plot_utils as pu
import cross_corr as cc
exec(open('/home/avrama/ephys_anal/fft_utils.py').read())

from matplotlib import pyplot as plt
plt.ion()
colors=['r','k','b']

####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
presyn=['str','GPe']
numbins=20
binsize_factor=10
networksim=1
spike_sta=0
show_sta=0
show_plots=0
savetxt=False
#key in weights dictionary must equal names of inputs in connect_dict in param_net.py
weights={'gabaextern2':-1,'gabaextern3':-1,'ampaextern1':1}#, 'gabaextern4':-1}

#customize the following according to file naming convention and parameters
def file_pattern(fileroot,suffix,params,filetype):
    #file pattern when using correlated trains
    '''
    freq,syn,plasYN,corr=params
    key=corr 
    fname=syn+'_'+'freq'+str(freq)+'_plas'+str(plasYN)+suffix
    pattern=fileroot+fname+key+filetype
    '''
    #file pattern when using oscillatory trains
    freq,syn,plasYN=params
    #key=syn+'_'+'freq'+str(freq)
    key=syn+'_'+'freq'+str(freq)+'_plas'+str(plasYN)
    fname=key+suffix
    pattern=fileroot+fname+filetype
    return pattern,key,freq

if networksim:
    #presyn_set overrides plasYN and presyn
    condition=['GABA']#,'POST-HFS','POST-NoDa']
    #condition=['POST-HFS_DMDLam', 'GABA_DMDLam'] #'POST-NoDaosc', 
    #tuples of (freq,syntype,plasYN,striatal correlation) for some synaptic input
    presyn_set=[(20,'GPe',10),(20,'GPe',11),(20,'str',11),(20,'str',10)]#(20,'str'),(40,'GPe')
    #location of files to analyze
    filedir='/home/avrama/moose/moose_nerp/moose_nerp/ep_net/output/'
    #filenames constructed from pattern constructed from presyn_set and the suffix below
    #may need to adjust fname pattern in file_pattern above depending on parameters and file naming convention
    inj='0.0'
    suffix='_inj'+inj
    #GPe_input='lognorm_freq29' #18 or 29
    suffix='_tg_GPe_lognorm*_ts_SPN_lognorm_ts_STN_lognorm'#'_tg_GPe_'#+GPe_input +'_ts_str_exp_corr'
else:
    stim_freqs=[5,10,20,40]
    condition=['-1e-11']#'0.0',
    presyn_set=[(freq,syn) for freq in stim_freqs for syn in presyn]
    rootname='ep_syn'
    filedir='ep/output/'
############################################################
####### plots for single neuron simulations, multiple frequencies, single trials:
if not networksim:
    for inj in condition:
        #specify file name pattern
        suffix='_plas'+str(plasYN)+'_inj'+inj+'*.npz'
        fileroot=filedir+rootname
        all_results,all_xvals=pu.plot_freq_dep_psp(fileroot,presyn,suffix,neurtype)
        pu.plot_freq_dep_vm(fileroot,presyn,plasYN,inj,neurtype)
else:
    #Network simulations
    #set up some dictionaries to hold results
    mean_prespike_sta1={};mean_prespike_sta2={}
    mean_sta_vm={cond:{} for cond in condition};vmdat={};sta_list={}
    spiketime_dict={};syntt_info={}
    lat_mean={};lat_std={}
    isi_mean={};isi_std={}
    isi_set={};all_isi_mean={}
    freqs={};latency_phase={};entropy={}
    fft_wave={cond:{} for cond in condition}
    phase={cond:{} for cond in condition}
    mean_fft_phase={cond:{} for cond in condition}
    fft_env={cond:{} for cond in condition}
    for cond in condition:
        #time points for spike triggered average
        sta_start=-40e-3
        sta_end=0
        #construct file name pattern
        rootname='ep'+cond+ 'PSP_'#'_syn'#
        fileroot=filedir+rootname
        ##### 1st set of analyses ignores the input spikes; most analyses,except for sta, assume multiple trials
        for params in presyn_set:
            pattern,key,freq=file_pattern(fileroot,suffix,params,'*.npz')
            files=na.file_set(pattern)
            ###################### stuff for entropy ######################
            entropy_bin_size=0.01 #Lavian J Neurosci used 10 ms bins
            numBinsForEnt=[int((1./freq)/entropy_bin_size)]#[2, 5, 10, 25] #set to [] to avoid calculating 
            if len(files):
                spiketime_dict[key],syntt_info[key]=na.get_spiketimes(files,neurtype)
                max_time= syntt_info[key]['maxt']
                if freq>0:
                    #latency: time from simulation of specific synapse to spike
                    #not defined if no regular (periodic) stimulation
                    #isi in these two functions is separated into pre and post stimulation - requires regular stimulation
                    lat_mean[key],lat_std[key],isi_mean[key],isi_std[key], isibins,isi_binsize,latency_phase[key],entropy[key]=na.latency(files,freq,neurtype,numbins,syntt_info[key],numBinsForEnt)
                    isi_set[key]=na.ISI_histogram(files,freq,neurtype)
                if sta_start != sta_end:
                    #ep spike triggered average of vm before the spike (the standard sta)
                    sta_list[key],pre_xvals,plotdt,vmdat[key]=na.sta_set(files,spiketime_dict[key],neurtype,sta_start,sta_end)
                    mean_sta_vm[cond][key]=np.mean(sta_list[key],axis=0)
                    time_wave=np.linspace(0,plotdt*len(vmdat[key][0][0]),len(vmdat[key][0][0]),endpoint=False)
                    ##### fft_wave[cond][key] is overwritten each epoch.  If make dict, need to fix plots ###
                    # option: make initt either list or value, and deal with that in fft_func
                    # other option: do it here
                    # still need to fix fft_plots
                    if freq>0:
                        for epoch in isibins.keys():
                            initt=isibins[epoch][0]
                            endt=isibins[epoch][-1]+isi_binsize
                            fft_wave[cond][key],phase[cond][key],freqs[cond],mean_fft_phase[cond][key],fft_env[cond][key]=na.fft_func(vmdat[key],time_wave,init_time=initt,endtime=endt)
                    else:
                        initt=0.5
                        endt=time_wave[-1]-0.5
                        fft_wave[cond][key],phase[cond][key],freqs[cond],mean_fft_phase[cond][key],fft_env[cond][key]=na.fft_func(vmdat[key],time_wave,init_time=initt,endtime=endt)
                    max_time=max(max_time,time_wave[-1])
        spike_freq_mean,spike_freq_std,spike_rate_vs_time_mean,spike_rate_vs_time_std,ratebins=na.output_fire_freq(spiketime_dict,isi_binsize,isibins,max_time)
        all_isi_mean[cond]=isi_mean
        #
        #####1st set of graphs
        if show_plots:
            pu.plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info)
            if len(lat_mean):
                pu.plot_dict_of_dicts(rootname,lat_mean,suffix,'Latency',std_dict=lat_std,xlabel='stim number')
                pu.plot_dict_of_dicts(rootname,isi_mean,suffix,'ISI',std_dict=isi_std,xarray=isibins)
                pu.plot_dict_of_dicts(rootname,entropy,suffix,'entropy',xlabel='stim number')
                pu.plot_dict_of_lists(rootname,spike_rate_vs_time_mean,suffix,'firing rate',ratebins,std_dict=spike_rate_vs_time_std)
                #ISI histogram
                histbins,plotbins=pu.plot_isi_hist(rootname,isi_set,numbins,suffix)
            if sta_start != sta_end and show_sta:
                #ep spike triggered average of vm before the spike (the standard sta)
                pu.plot_dict_of_lists(rootname,sta_list,suffix,'STA', pre_xvals)
            for key in vmdat.keys():
                fft_plot(time_wave,vmdat[key],freqs[cond],fft_wave[cond][key],phase=phase[cond][key],title=cond+key)#,mean_fft=mean_fft_phase[cond])
        if savetxt:
            hist=plotbins
            out_lat=range(freq)
            histheader="ISIbins     "
            lat_header=""
            for synstim in isi_set.keys():
                for pre_post,ISIs in isi_set[synstim].items():
                    hist1,tmp=np.histogram(pu.flatten(ISIs),bins=histbins)
                    hist=np.column_stack((hist,hist1))
                    histheader=histheader+'isi_'+synstim+'_'+pre_post+' '
                    out_lat=np.column_stack((out_lat,lat_mean[synstim][pre_post],lat_std[synstim][pre_post]))
                    lat_header=lat_header+'latmean_'+synstim+'_'+pre_post+' '+'latstd_'+synstim+'_'+pre_post+' '
            f=open(cond+"_isi_hist.txt",'w')
            f.write(histheader+'\n')
            np.savetxt(f,hist,fmt='%.5f')
            f.close()
            f=open(cond+'latency.txt','w')
            f.write(lat_header+'\n')
            np.savetxt(f,out_lat,fmt='%.5f')
            f.close()
            ############ entropy
            ent_header=""
            out_entropy=range(3*freq)
            for synstim in entropy.keys():
                for entbin in entropy[synstim].keys():
                    out_entropy=np.column_stack((out_entropy,entropy[synstim][entbin]))
                    ent_header=ent_header+'ent_'+synstim+'_'+str(entbin)+' '
            f=open(cond+'entropy.txt','w')
            f.write(ent_header+'\n')
            np.savetxt(f,out_entropy,fmt='%.5f')
            f.close()
            ############ data for bar plot
            f=open(cond+"spike_rate_stats.txt",'w')
            header='spike frequencies: condition, epoch mean, std, CV\n'
            f.write(header)
            for k1 in spike_freq_mean.keys():
                for k2 in spike_freq_mean[k1].keys():
                    mean_firing=np.mean(spike_freq_mean[k1][k2]) #average across epochs (i.e., stim events)
                    std_firing=np.mean(spike_freq_std[k1][k2]) #average across epoch stdevs to get estimate of stdev of firing
                    summary='   '.join([k1,k2,str(np.round(mean_firing,3)),str(np.round(std_firing,3))])
                    f.write(summary+'\n')
                    print(summary)
            f.close()
            ############# to plot spike rate vs time, with error bars
            f=open(cond+'spike_rate.txt','w')
            header='time'
            outputdata=ratebins
            for key in spike_rate_vs_time_mean.keys():
                outputdata=np.column_stack((outputdata,spike_rate_vs_time_mean[key],spike_rate_vs_time_std[key]))
                header=header+'   mean_'+key+'   std_'+key
            f.write(header+'\n')
            np.savetxt(f,outputdata,fmt='%.5f')
            #
        ################## additional spike triggered averages and raster plot of input spike times,
        ######## This next set of analyses requires the input spikes
        #2. spike triggered Vm after an input spike
        #uses different filenames and different sta start and end
        sta_start=0e-3
        sta_end=20e-3
        pre_spikes={}
        post_sta={}
        mean_sta={}
        fileroot=filedir+'tt'+rootname
        for params in presyn_set:
            pattern,key,freq=file_pattern(fileroot,suffix,params, '*.npy')
            files=na.file_set(pattern)
            print('tt files',pattern, 'num files',len(files))
            if len(files):
                #calculate raster of pre-synaptic spikes
                pre_spikes[key]=na.input_raster(files)
                # input Spike triggered average Vm after the spike
                post_sta[key],mean_sta[key],post_xvals=na.post_sta_set(pre_spikes[key],sta_start,sta_end,plotdt,vmdat[key])
        if show_plots:
            if len(suffix):
                pu.plot_input_raster(pre_spikes,suffix,maxplots=1)
            else:
                pu.plot_input_raster(pre_spikes,cond,maxplots=1)
            if show_sta:
                pu.plot_sta_post_vm(pre_spikes,post_sta,mean_sta,post_xvals)
        #
        #3. use both pre-synaptic and post-synaptic spikes for spike triggered average input:
        #1st calculate instantaneous input firing frequency for each type of input
        #2nd calculate sta using input fire freq instead of vmdat
        #Perhaps better to represent the input fire freq as vector across input types?
        #1. change the dict with keys ['gabaextern2', 'gabaextern3', 'ampaextern1' into array
        #2. adapt pre_spike_sta to use the array
        #3. plot the new prespike_sta array
        #4. alternative: adapt Dan's code which keeps spatial information, and group inputs by discretized distances from soma, e.g. soma, prox, middle, distal dendrites - either excite or inhib - array of 8xtimebins
        #5. calculate Spike triggered covariance also
        #6. calculate PCA on same set of 8xtimebins input patterns; test EP response to each component
        binsize=plotdt*binsize_factor
        sta_start=-20e-3
        sta_end=0
        inst_rate1={}; inst_rate2={}
        prespike_sta1={}; prespike_sta2={}
        mean_pre_sta1={}; mean_pre_sta2={}
        if spike_sta:
            for key in pre_spikes:
                #rate1 - calculated with elephant (smoothed), rate2 - calculated by hand, no smoothing
                inst_rate1[key],inst_rate2[key],xbins=na.input_fire_freq(pre_spikes[key],binsize) 
                prespike_sta1[key],mean_pre_sta1[key],bins1=na.sta_fire_freq(inst_rate1[key],spiketime_dict[key],sta_start,sta_end,weights,xbins)
                prespike_sta2[key],mean_pre_sta2[key],bins2=na.sta_fire_freq(inst_rate2[key],spiketime_dict[key],sta_start,sta_end,weights,xbins)
            mean_prespike_sta1[cond]=mean_pre_sta1
            mean_prespike_sta2[cond]=mean_pre_sta2
            ######## second set of graphs
        if show_plots and spike_sta:
            for key in inst_rate1:
                pu.plot_list_of_dict(inst_rate1[key],xbins,title='instaneous pre-syn firing rate '+cond+key+' smoothed')
                #pu.plot_inst_firing(inst_rate2[key],xbins,title=cond+key)
                pu.plot_list_of_dict(prespike_sta1[key],bins1,mean_values=mean_pre_sta1[key],title='prespike sta '+cond+key+' smoothed')
                pu.plot_list_of_dict(prespike_sta2[key],bins2,mean_values=mean_pre_sta2[key],title='prespike sta '+cond+key)
    #
    ############################## More analyses and graphs after looping over all conditions
    ##################### calculate cross-correlogram from input and output rate histograms #####################
    presyn_types=weights.keys()
    #even better, get presyn_types from pre_spikes[key][0].keys()
    #for presyn in presyn_types:
    #    cc.plot_cross_corr(pre_spikes,spiketime_dict,presyn,binsize,maxtime=20)
    ################################### End cross correlogram ##################### 
    ##### Plots of means compared across conditions or across presyn_set
    #1st STA
    if len(condition)>1:
        pu.plot_sta_vm_cond(pre_xvals,sta_list,mean_sta_vm)
        group_plot_by_presyn_set=0
    elif len(presyn_set)>1:
        cond=condition[0]
        plt.figure()
        plt.suptitle('mean sta vm')
        for i,(key,mean_sta) in enumerate(mean_sta_vm[cond].items()):
            plt.plot(pre_xvals,mean_sta,label=key)
        plt.legend()
        plt.xlabel('time (s)')
        plt.ylabel('Vm (V)')
        group_plot_by_presyn_set=1 if len(presyn_set)>len(condition) else 0
    # fft, ISI and sta across conditions
    pu.plot_fft(condition,presyn_set,mean_fft_phase,freqs,fft_wave,fft_env)
    if len(lat_mean):
        pu.plot_ISI_cond(all_isi_mean,isibins,group_plot_by_presyn_set)
    #
    if len(inst_rate1):
        pu.plot_prespike_sta_cond(mean_prespike_sta1,bins1)
    #
    ####### Output data for plotting #######
    #if savetxt:
    if savetxt:
        for i,(cond,fft_set) in enumerate(mean_fft_phase.items()):
            for j,(key,fft) in enumerate(fft_set.items()):        #
                if len(condition)>len(presyn_set):
                    colname=cond
                else:
                    colname=key
                mean_of_fft=np.mean([np.abs(fft) for fft in fft_wave[cond][key]],axis=0)
                mean_of_fft_env=np.mean([np.abs(fft) for fft in fft_env[cond][key]],axis=0)
                f=open(cond+key+"_fft_igor.txt",'w')
                header="freq    "+colname+"fft    "+colname+"fft_env    \n"
                output_data=np.column_stack((freqs[cond],mean_of_fft,mean_of_fft_env))
                f.write(header)
                np.savetxt(f,output_data,fmt='%.5f')
                f.close()

#create latency_phase_plot function that is called once per condition
fig,axes =plt.subplots(len(latency_phase),1,sharex=True)
for i,key1 in enumerate(latency_phase.keys()):
    for key2 in latency_phase[key1].keys():
        flat_array=np.array(pu.flatten(latency_phase[key1][key2]))
        phase_hist,tmpbins=np.histogram(flat_array[~np.isnan(flat_array)],bins=12)
        phase_hist_bins=[(tmpbins[i]+tmpbins[i+1])/2 for i in range(len(tmpbins)-1)]
        axes[i].plot(phase_hist_bins,phase_hist,label=key2)
    axes[i].set_ylabel(key1)
axes[-1].set_xlabel('latency (ms)')
axes[0].legend()
fig.suptitle('latency phase histogram')

