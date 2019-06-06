import numpy as np
import elephant
#must import elephant prior to matplotlib else plt.ion() doesn't work properly
import ISI_anal
import ep_plot_utils as pu

from matplotlib import pyplot as plt
plt.ion()
colors=['r','k','b']


####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
inj='0'
stim_freqs=[5,10,20,40]
presyn=['str','GPe']
numbins=10
condition=['POST-NoDa', 'POST-HFS', 'GABA'] #will be used later
#presyn_set=[(freq,syn) for freq in stim_freqs for syn in presyn]
presyn_set=[(20,'str'),(40,'GPe'),(0,'non')]
show_plots=1
############################################################
##### 1st set of analyses ignores the input spikes
#specify file name pattern
mean_prespike_sta1={};mean_prespike_sta2={}
mean_sta_vm={};all_isi_mean={}
for cond in condition:
    filedir='ep_net/output/'
    rootname='ep'+cond+'_syn'
    #filedir='ep/output/'
    #rootname='ep_syn'
    fileroot=filedir+rootname
    suffix='_plas'+str(plasYN)+'_inj'+inj+'*.npz'
    #
    ####### plots for single neuron simulations, multiple frequencies, single trials:
    #all_results,all_xvals=pu.plot_freq_dep_psp(fileroot,presyn,suffix,neurtype)
    #pu.plot_freq_dep_vm(fileroot,presyn,plasYN,inj,neurtype)
    #
    ######### most of these analyses,except for sta, assume multiple trials
    #time points for spike triggered average
    sta_start=-30e-3
    sta_end=0
    spiketime_dict={};syntt_info={}
    lat_mean={};lat_std={}
    isi_mean={};isi_std={}
    isi_set={}
    sta_list={};vmdat={}
    mean_sta_vm[cond]={}
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
    all_isi_mean[cond]=isi_mean
    #
    #####1st set of graphs
    if show_plots:
        pu.plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info)
        #pu.plot_latency(rootname,lat_mean,lat_std,suffix)
        #latency not too meaningful if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
        pu.plot_ISI(rootname,isi_mean,isi_std,bins,suffix)
        #ISI histogram
        #pu.plot_isi_hist(rootname,isi_set,numbins,suffix)
        #ep spike triggered average of vm before the spike (the standard sta)
        pu.plot_sta_vm(pre_xvals,sta_list,fileroot,suffix)
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
    #
    #3. use both pre-synaptic and post-synaptic spikes for spike triggered average input:
    #1st calculate instantaneous input firing frequency for each type of input
    #2nd calculate sta using input fire freq instead of vmdat
    #weights used to sum the different external inputs - values are weights from param_net
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
        for synfreq in pre_spikes:
            pu.plot_inst_firing(inst_rate1[synfreq],xbins,title=cond+synfreq+' smoothed')
            #pu.plot_inst_firing(inst_rate2[synfreq],xbins,title=cond+synfreq)
            pu.plot_prespike_sta(prespike_sta1[synfreq],mean_pre_sta1[synfreq],bins1,title=cond+synfreq+' smoothed')
            pu.plot_prespike_sta(prespike_sta2[synfreq],mean_pre_sta2[synfreq],bins2,title=cond+synfreq)
            #pu.plot_input_raster(pre_spikes[synfreq],pattern,maxplots=1)

#####Plots of means compared across conditions
fig,axis=plt.subplots(len(mean_prespike_sta1[cond][synfreq].keys()),len(mean_prespike_sta1[cond].keys()),sharex=True) 
fig.suptitle('mean spike triggered average pre-synaptic firing')
#need titles for each of the three columns
for cond in mean_prespike_sta1.keys():
    for axy,synfreq in enumerate(mean_prespike_sta1[cond].keys()):
        for axx,(key,sta) in enumerate(mean_prespike_sta1[cond][synfreq].items()):
            axis[axx,axy].plot(bins1,sta,label=cond)
            axis[axx,0].set_ylabel(key)
        axis[-1,axy].set_xlabel('time (s)')
        axis[0,axy].title.set_text(synfreq)
    axis[0,0].legend()
#
fig,axes=plt.subplots(len(sta_list.keys()),sharex=True) 
axis=fig.axes
fig.suptitle('mean sta vm')
for cond in mean_sta_vm.keys():
    for i,(synfreq,mean_sta) in enumerate(mean_sta_vm[cond].items()):
        axis[i].plot(pre_xvals,mean_sta,label=cond)
        axis[i].set_ylabel(synfreq+' Vm (V)')
axis[-1].set_xlabel('time (s)')
axis[-1].legend()
#
fig,axes =plt.subplots(len(all_isi_mean[cond]),1,sharex=True)
axis=fig.axes
fig.suptitle('ISI mean: all conditions')
for j,cond in enumerate(all_isi_mean.keys()): 
    for i,synstim in enumerate(all_isi_mean[cond].keys()):
        presyn=synstim.split('_')[0]
        freq=synstim.split('_')[1]
        for k,key in enumerate(bins.keys()):
            label=cond if k==0 else ""
            axis[i].plot(bins[key],all_isi_mean[cond][synstim][key],label=label,color=colors[j])
        axis[i].set_xlabel('time (sec)')
        axis[i].set_ylabel(presyn+' input, isi (sec)')
axis[i].legend(loc='lower left')

