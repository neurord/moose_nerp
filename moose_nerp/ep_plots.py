import numpy as np
import elephant
#must import elephant prior to matplotlib else plt.ion() doesn't work properly
import ISI_anal
import ep_plot_utils as pu
exec(open('/home/avrama/ephys_anal/fft_utils.py').read())

from matplotlib import pyplot as plt
plt.ion()
colors=['r','k','b']

####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
presyn=['str','GPe']
numbins=10
networksim=1
spike_sta=0
#key in weights dictionary must equal names of inputs in connect_dict in param_net.py
weights={'gabaextern2':-2,'gabaextern3':-1,'ampaextern1':1}

#customize the following according to file naming convention and parameters
def file_pattern(fileroot,suffix,params,filetype):
    freq,syn,plasYN,corr=params
    #key=syn+'_'+'freq'+str(freq)
    #key=syn+'_'+'freq'+str(freq)+'_plas'+str(plasYN)
    fname=syn+'_'+'freq'+str(freq)+'_plas'+str(plasYN)+suffix
    key=corr
    pattern=fileroot+fname+key+filetype
    return pattern,key,freq

if networksim:
    condition=['POST-HFS', 'GABA'] #'POST-NoDaosc', 
    #condition=['Ctrl']#'GABAosc',
    #change 3 value from plasYN to Str corr value
    presyn_set=[(0,'non',1,'010'),(0,'non',1,'030'),(0,'non',1,'100'),(0,'non',1,'300')]#,(0,'non',0)]#(20,'str'),(40,'GPe'),
    filedir='ep_net/output/'
    #inj='0.0'
    #suffix='_inj'+inj+'*.npz'
    GPe_input='exp_freq18' #or 29
    suffix='_tg_GPe_'+GPe_input+'_ts_SPN_exp_corr'
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
    mean_prespike_sta1={};mean_prespike_sta2={}
    mean_sta_vm={};vmdat={};sta_list={}
    spiketime_dict={};syntt_info={}
    lat_mean={};lat_std={}
    isi_mean={};isi_std={}
    isi_set={};all_isi_mean={}
    fft_wave={};phase={};freqs={};mean_fft_phase={}
    for cond in condition:
        sta_start=-40e-3
        sta_end=0
        #specify file name pattern
        rootname='ep'+cond+'_syn'
        fileroot=filedir+rootname
        ##### 1st set of analyses ignores the input spikes; most analyses,except for sta, assume multiple trials
        mean_sta_vm[cond]={}
        fft_wave[cond]={};phase[cond]={};mean_fft_phase[cond]={}
        for params in presyn_set:
            pattern,key,freq=file_pattern(fileroot,suffix,params,'*.npz')
            files=ISI_anal.file_set(pattern)
            if len(files):
                spiketime_dict[key],syntt_info[key]=ISI_anal.get_spiketimes(files,neurtype)
                if freq>0:
                    #latency not defined if no regular stimulation
                    #isi in these two functions is separated into pre and post stimulation - requires regulator stimulation
                    lat_mean[key],lat_std[key],isi_mean[key],isi_std[key], bins=ISI_anal.latency(files,freq,neurtype,numbins)
                    isi_set[key]=ISI_anal.ISI_histogram(files,freq,neurtype)
                if sta_start != sta_end:
                    #ep spike triggered average of vm before the spike (the standard sta)
                    sta_list[key],pre_xvals,plotdt,vmdat[key]=ISI_anal.sta_set(files,spiketime_dict[key],neurtype,sta_start,sta_end)
                    mean_sta_vm[cond][key]=np.mean(sta_list[key],axis=0)
                    time_wave=np.linspace(0,plotdt*len(vmdat[key][0][0]),len(vmdat[key][0][0]),endpoint=False)
                    fft_wave[cond][key],phase[cond][key],freqs[cond],mean_vm,mean_fft_phase[cond][key]=ISI_anal.fft_func(vmdat[key],time_wave,init_time=1.0,endtime=19.0)
        all_isi_mean[cond]=isi_mean
        #
        #####1st set of graphs
        if show_plots:
            pu.plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info)
            if len(lat_mean):
                pu.plot_latency(rootname,lat_mean,lat_std,suffix)
                #latency not too meaningful if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
                pu.plot_ISI(rootname,isi_mean,isi_std,bins,suffix)
                #ISI histogram
                pu.plot_isi_hist(rootname,isi_set,numbins,suffix)
            if sta_start != sta_end:
                #ep spike triggered average of vm before the spike (the standard sta)
                pu.plot_sta_vm(pre_xvals,sta_list,fileroot,suffix)
                fft_plot(time_wave,vmdat[key],freqs[cond],fft_wave[cond][key],phase=phase[cond][key],title=cond+key)#,mean_fft=mean_fft_phase[cond])
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
            files=ISI_anal.file_set(pattern)
            print('tt files',pattern, 'num files',len(files))
            if len(files):
                #calculate raster of pre-synaptic spikes
                pre_spikes[key]=ISI_anal.input_raster(files)
                # input Spike triggered average Vm after the spike
                post_sta[key],mean_sta[key],post_xvals=ISI_anal.post_sta_set(pre_spikes[key],sta_start,sta_end,plotdt,vmdat[key])
        if show_plots:
            pu.plot_sta_post_vm(pre_spikes,post_sta,mean_sta,post_xvals)
            for key in pre_spikes:
                pu.plot_input_raster(pre_spikes[key],pattern,maxplots=1)
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
        binsize=plotdt*100#*10
        sta_start=-20e-3
        sta_end=0
        inst_rate1={}; inst_rate2={}
        prespike_sta1={}; prespike_sta2={}
        mean_pre_sta1={}; mean_pre_sta2={}
        if spike_sta:
            for key in pre_spikes:
                inst_rate1[key],inst_rate2[key],xbins=ISI_anal.input_fire_freq(pre_spikes[key],binsize)
                prespike_sta1[key],mean_pre_sta1[key],bins1=ISI_anal.sta_fire_freq(inst_rate1[key],spiketime_dict[key],sta_start,sta_end,weights,xbins)
                prespike_sta2[key],mean_pre_sta2[key],bins2=ISI_anal.sta_fire_freq(inst_rate2[key],spiketime_dict[key],sta_start,sta_end,weights,xbins)
            mean_prespike_sta1[cond]=mean_pre_sta1
            mean_prespike_sta2[cond]=mean_pre_sta2
            ######## second set of graphs
        if show_plots and spike_sta:
            for key in inst_rate1:
                pu.plot_inst_firing(inst_rate1[key],xbins,title=cond+key+' smoothed')
                #pu.plot_inst_firing(inst_rate2[key],xbins,title=cond+key)
                pu.plot_prespike_sta(prespike_sta1[key],mean_pre_sta1[key],bins1,title=cond+key+' smoothed')
                pu.plot_prespike_sta(prespike_sta2[key],mean_pre_sta2[key],bins2,title=cond+key)
    #
    ##################### calculate cross-correlogram from input and output rate histograms #####################
    #def plot_cross_corr(pre_spikes,post_spikes,presyn):
    import elephant
    from neo.core import AnalogSignal,SpikeTrain
    import quantities as q
    from elephant.conversion import BinnedSpikeTrain
    numtrials=len(pre_spikes[key])
    numtrials=3
    presyn='gabaextern3'
    last_spike=[train[-1] for train in pre_spikes[key][0][presyn]]
    t_end=np.round(np.max(last_spike))
    cc_hist=[[] for t in range(numtrials)]
    fig,axes =plt.subplots(numtrials,numtrials,sharex=True)
    fig.suptitle('cross correlograms '+key)
    for trial_in in range(numtrials):
        for trial_out in range(numtrials):
            if isinstance(pre_spikes[key][trial_in][presyn], list):
                spikes = np.sort(np.concatenate(pre_spikes[key][trial_in][presyn]))
            else:
                spikes=pre_spikes[key][trial_in][presyn]
            train=SpikeTrain(spikes*q.s,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
            in_train=BinnedSpikeTrain(train,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
            train=SpikeTrain(spiketime_dict[key][trial_out]*q.s,t_stop=t_end*q.s)
            out_train=BinnedSpikeTrain(train,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
            print('trial_in,trial_out', trial_in, trial_out)
            cc_hist[trial_in].append(elephant.spike_train_correlation.cross_correlation_histogram(in_train,out_train))
            axes[trial_in,trial_out].plot(cc_hist[trial_in][trial_out][0].magnitude[:,0])
        axes[trial_in,0].set_ylabel('input '+str(trial_in))
    for trial_out in range(trial_in,numtrials):
        axes[-1,trial_out].set_xlabel('output '+str(trial_out))
    #shuffle corrected mean cross-correlogram
    #initialize these to accumulate across conditions, e.g. pre and post-HFS, and possibly across keys (str freq)
    cc_same=[cc_hist[a][a][0].magnitude[:,0] for a in range(numtrials)]
    mean_cc=np.mean(cc_same,axis=0)
    cc_diff=[cc_hist[a][b][0].magnitude[:,0] for a in range(numtrials) for b in range(numtrials) if b != a ]
    mean_cc_shuffle=np.mean(cc_diff,axis=0)
    cc_shuffle_corrected=mean_cc-mean_cc_shuffle
    xbins=np.linspace(-t_end,t_end,len(mean_cc))
    fig,axes =plt.subplots(3,1,sharex=True)
    axes[0].plot(xbins,mean_cc)
    axes[1].plot(xbins,mean_cc_shuffle)
    axes[2].plot(xbins,cc_shuffle_corrected)
    axes[0].set_ylabel('mean cc')
    axes[1].set_ylabel('mean cc shuffled')
    axes[1].set_ylabel('mean cc shuffled-corrected')
    ################################### End cross correlogram ##################### 
    ##### Plots of means compared across conditions or across presyn_set
    if len(condition)>1:
        pu.plot_sta_vm_cond(pre_xvals,sta_list,mean_sta_vm)
        #pu.plot_fft_cond(freqs,fft_mean,fft_wave)
        fig,axes=plt.subplots(1,1)
        fig.suptitle('Mean fft')
        for i,(cond,fft_set) in enumerate(mean_fft_phase.items()):
            maxval=np.max([np.max(np.abs(f['mag'][1:])) for f in mean_fft_phase[cond].values()])
            maxfreq=np.min(np.where(freqs[cond]>500))
            for key,fft in fft_set.items():
                #axes.plot(freqs[cond][0:maxfreq], np.abs(fft['mag'])[0:maxfreq], '--', label=cond+' '+key+' mean',color=colors[i])
                mean_of_fft=np.mean([np.abs(fft) for fft in fft_wave[cond][key]],axis=0)
                axes.plot(freqs[cond][0:maxfreq], mean_of_fft[0:maxfreq],label='mean of '+cond+' '+key,color=colors[i])
        axes.set_xlabel('Frequency in Hertz [Hz]')
        axes.set_ylabel('FFT Magnitude')
        axes.set_xlim(0 , freqs[cond][maxfreq] )
        axes.set_ylim(0,np.round(maxval) )
        axes.legend()
        #
        if len(lat_mean):
            pu.plot_ISI_cond(all_isi_mean,bins)
        #
        if len(inst_rate1):
            pu.plot_prespike_sta_cond(mean_prespike_sta1,bins1)
        #
    else:
        if len(presyn_set)>1:
            cond=condition[0]
            plt.figure()
            plt.suptitle('mean sta vm')
            for i,(key,mean_sta) in enumerate(mean_sta_vm[cond].items()):
                plt.plot(pre_xvals,mean_sta,label=key)
            plt.legend()
            plt.xlabel('time (s)')
            plt.ylabel('Vm (V)')
            #
            fig,axes=plt.subplots(1,1)
            fig.suptitle('Mean fft')
            maxval=np.max([np.max(np.abs(f['mag'][1:])) for f in mean_fft_phase[cond].values()])
            maxfreq=np.min(np.where(freqs[cond]>500))
            for i,(key,fft) in enumerate(mean_fft_phase[cond].items()):
                axes.plot(freqs[cond][0:maxfreq], np.abs(fft['mag'])[0:maxfreq], label=cond+' '+key+' mean',color=colors[i])
            axes.set_xlabel('Frequency in Hertz [Hz]')
            axes.set_ylabel('FFT Magnitude')
            axes.set_xlim(0 , freqs[cond][maxfreq] )
            axes.set_ylim(0,np.round(maxval) )
            axes.legend()
