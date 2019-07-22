import numpy as np
import elephant
#must import elephant prior to matplotlib else plt.ion() doesn't work properly
import ISI_anal
import ep_plot_utils as pu
exec(open('/home/avrama/ephys_anal/fft_utils.py').read())

from matplotlib import pyplot as plt
plt.ion()
colors=['r','k','b']

#TO DO: why is FFT magnitude not symmetric?  Perhaps use realFFT
#plot meanFFT in different color, compare with fft of mean VM
#analyze data for periodic inputs
####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
presyn=['str','GPe']
numbins=10
networksim=1

if networksim:
    #condition=['POST-NoDa', 'POST-HFS', 'GABA'] 
    condition=['GABA']
    inj='0.0'
    presyn_set=[(0,'non')]#(20,'str'),(40,'GPe'),
    filedir='ep_net/output/'
else:
    stim_freqs=[5,10,20,40]
    condition=['-1e-11']#'0.0',
    presyn_set=[(freq,syn) for freq in stim_freqs for syn in presyn]
    rootname='ep_syn'
    filedir='ep/output/'
show_plots=1
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
    #time points for spike triggered average
    sta_start=-30e-3
    sta_end=0
    mean_prespike_sta1={};mean_prespike_sta2={}
    mean_sta_vm={};vmdat={};sta_list={}
    spiketime_dict={};syntt_info={}
    lat_mean={};lat_std={}
    isi_mean={};isi_std={}
    isi_set={};all_isi_mean={}
    fft_wave={};phase={};freqs={}
    for cond in condition:
        #specify file name pattern
        rootname='ep'+cond+'_syn'
        suffix='_plas'+str(plasYN)+'_inj'+inj+'*.npz'
        fileroot=filedir+rootname
        ##### 1st set of analyses ignores the input spikes; most analyses,except for sta, assume multiple trials
        mean_sta_vm[cond]={}
        fft_wave[cond]={};phase[cond]={}
        for (freq,syn) in presyn_set:
            key=syn+'_'+'freq'+str(freq)
            pattern=fileroot+key+suffix
            files=ISI_anal.file_set(pattern)
            spiketime_dict[key],syntt_info[key]=ISI_anal.get_spiketimes(files,neurtype)
            if freq>0 and len(files)>1:
                #latency not defined if no regular stimulation
                #isi in these two functions is separated into pre and post stimulation - requires regulator stimulation
                lat_mean[key],lat_std[key],isi_mean[key],isi_std[key], bins=ISI_anal.latency(files,freq,neurtype,numbins)
                isi_set[key]=ISI_anal.ISI_histogram(files,freq,neurtype)
            if sta_start != sta_end:
                #ep spike triggered average of vm before the spike (the standard sta)
                sta_list[key],pre_xvals,plotdt,vmdat[key]=ISI_anal.sta_set(files,spiketime_dict[key],neurtype,sta_start,sta_end)
                mean_sta_vm[cond][key]=np.mean(sta_list[key],axis=0)
                time_wave=np.linspace(0,plotdt*len(vmdat[key][0][0]),len(vmdat[key][0][0]))
                fft_wave[cond][key],phase[cond][key],freqs[cond],mean_vm=ISI_anal.fft_func(vmdat[key],time_wave,init_time=1.0)
        all_isi_mean[cond]=isi_mean
        #
        #####1st set of graphs
        if show_plots:
            pu.plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info)
            if len(lat_mean):
                #pu.plot_latency(rootname,lat_mean,lat_std,suffix)
                #latency not too meaningful if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
                pu.plot_ISI(rootname,isi_mean,isi_std,bins,suffix)
                #ISI histogram
                #pu.plot_isi_hist(rootname,isi_set,numbins,suffix)
            if sta_start != sta_end:
                #ep spike triggered average of vm before the spike (the standard sta)
                pu.plot_sta_vm(pre_xvals,sta_list,fileroot,suffix)
                fft_plot(time_wave,vmdat[key],freqs[cond],fft_wave[cond][key],phase=phase[cond][key],title=cond+key)
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
        suffix=suffix.split('npz')[0]+'npy'
        for (freq,syn) in presyn_set:
            pattern=fileroot+syn+'_freq'+str(freq)+suffix
            files=ISI_anal.file_set(pattern)
            print('tt files',pattern, 'num files',len(files))
            synfreq=syn+'_'+'freq'+str(freq)
            #calculate raster of pre-synaptic spikes
            pre_spikes[synfreq]=ISI_anal.input_raster(files)
            # input Spike triggered average Vm after the spike
            post_sta[synfreq],mean_sta[synfreq],post_xvals=ISI_anal.post_sta_set(pre_spikes[synfreq],sta_start,sta_end,plotdt,vmdat[synfreq])
        if show_plots:
            pu.plot_sta_post_vm(pre_spikes,post_sta,mean_sta,post_xvals)
            for synfreq in pre_spikes:
                pu.plot_input_raster(pre_spikes[synfreq],pattern,maxplots=1)
        #
        #3. use both pre-synaptic and post-synaptic spikes for spike triggered average input:
        #1st calculate instantaneous input firing frequency for each type of input
        #2nd calculate sta using input fire freq instead of vmdat
        #weights used to sum the different external inputs - values are weights from param_net
        '''
        weights={'gabaextern2':-2,'gabaextern3':-1,'ampaextern1':1}
        binsize=plotdt*10#*100
        sta_start=-20e-3
        sta_end=0
        inst_rate1={}; inst_rate2={}
        prespike_sta1={}; prespike_sta2={}
        mean_pre_sta1={}; mean_pre_sta2={}
        #
        for synfreq in pre_spikes:
            inst_rate1[synfreq],inst_rate2[synfreq],xbins=ISI_anal.input_fire_freq(pre_spikes[synfreq],binsize)
            prespike_sta1[synfreq],mean_pre_sta1[synfreq],bins1=ISI_anal.sta_fire_freq(inst_rate1[synfreq],spiketime_dict[synfreq],sta_start,sta_end,weights,xbins)
            prespike_sta2[synfreq],mean_pre_sta2[synfreq],bins2=ISI_anal.sta_fire_freq(inst_rate2[synfreq],spiketime_dict[synfreq],sta_start,sta_end,weights,xbins)
        mean_prespike_sta1[cond]=mean_pre_sta1
        mean_prespike_sta2[cond]=mean_pre_sta2
        ######## second set of graphs
        if show_plots:
            for synfreq in inst_rate1:
                pu.plot_inst_firing(inst_rate1[synfreq],xbins,title=cond+synfreq+' smoothed')
                #pu.plot_inst_firing(inst_rate2[synfreq],xbins,title=cond+synfreq)
                pu.plot_prespike_sta(prespike_sta1[synfreq],mean_pre_sta1[synfreq],bins1,title=cond+synfreq+' smoothed')
                pu.plot_prespike_sta(prespike_sta2[synfreq],mean_pre_sta2[synfreq],bins2,title=cond+synfreq)
    #
    '''
    #####Plots of means compared across conditions
    plot_sta_vm_cond(pre_xvals,sta_list,mean_sta_vm)
    #
    plot_ISI_cond(all_isi_mean,bins)
    #
    #plot_prespike_sta_cond(mean_prespike_sta1,bins1)
    #

