import numpy as np
import elephant
#must import elephant prior to matplotlib else plt.ion() doesn't work properly
import ISI_anal
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
show_plots=1
savetxt=True
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
    presyn_set=[(20,'str',1),(20,'GPe',1)]#,(20,'str',0),(20,'GPe',0)]#(20,'str'),(40,'GPe')
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
    mean_sta_vm={};vmdat={};sta_list={}
    spiketime_dict={};syntt_info={}
    lat_mean={};lat_std={}
    isi_mean={};isi_std={}
    isi_set={};all_isi_mean={}
    fft_wave={};phase={};freqs={};mean_fft_phase={};fft_env={}
    for cond in condition:
        #time points for spike triggered average
        sta_start=-40e-3
        sta_end=0
        #construct file name pattern
        rootname='ep'+cond+ 'PSP_'#'_syn'#
        fileroot=filedir+rootname
        ##### 1st set of analyses ignores the input spikes; most analyses,except for sta, assume multiple trials
        mean_sta_vm[cond]={}
        fft_wave[cond]={};phase[cond]={};mean_fft_phase[cond]={};fft_env[cond]={}
        for params in presyn_set:
            pattern,key,freq=file_pattern(fileroot,suffix,params,'*.npz')
            files=ISI_anal.file_set(pattern)
            numtrials=len(files)
            if len(files):
                spiketime_dict[key],syntt_info[key]=ISI_anal.get_spiketimes(files,neurtype)
                max_time= np.max([np.max(spikes) for spikes in spiketime_dict[key]])
                if freq>0:
                    #latency: time from simulation of specific synapse to spike
                    #not defined if no regular (periodic) stimulation
                    #isi in these two functions is separated into pre and post stimulation - requires regular stimulation
                    lat_mean[key],lat_std[key],isi_mean[key],isi_std[key], isibins,isi_binsize=ISI_anal.latency(files,freq,neurtype,numbins)
                    isi_set[key]=ISI_anal.ISI_histogram(files,freq,neurtype)
                if sta_start != sta_end:
                    #ep spike triggered average of vm before the spike (the standard sta)
                    sta_list[key],pre_xvals,plotdt,vmdat[key]=ISI_anal.sta_set(files,spiketime_dict[key],neurtype,sta_start,sta_end)
                    mean_sta_vm[cond][key]=np.mean(sta_list[key],axis=0)
                    time_wave=np.linspace(0,plotdt*len(vmdat[key][0][0]),len(vmdat[key][0][0]),endpoint=False)
                    fft_wave[cond][key],phase[cond][key],freqs[cond],mean_vm,mean_fft_phase[cond][key],fft_env[cond][key]=ISI_anal.fft_func(vmdat[key],time_wave,init_time=1.0,endtime=time_wave[-1]-0.5)
                    max_time=max(max_time,time_wave[-1])
        all_isi_mean[cond]=isi_mean
        #
        #####1st set of graphs
        if show_plots:
            pu.plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info)
            if len(lat_mean):
                pu.plot_latency(rootname,lat_mean,lat_std,suffix)
                #latency not too meaningful if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
                pu.plot_ISI(rootname,isi_mean,isi_std,isibins,suffix)
                #ISI histogram
                histbins,plotbins=pu.plot_isi_hist(rootname,isi_set,numbins,suffix)
            if sta_start != sta_end and show_sta:
                #ep spike triggered average of vm before the spike (the standard sta)
                pu.plot_sta_vm(pre_xvals,sta_list,fileroot,suffix)
            for key in vmdat.keys():
                fft_plot(time_wave,vmdat[key],freqs[cond],fft_wave[cond][key],phase=phase[cond][key],title=cond+key)#,mean_fft=mean_fft_phase[cond])
        if savetxt:
            for synstim in isi_set.keys():
                hist=plotbins
                header="bins     "
                for pre_post,ISIs in isi_set[synstim].items():
                    hist1,tmp=np.histogram(pu.flatten(ISIs),bins=histbins)
                    hist=np.column_stack((hist,hist1))
                    header=header+pre_post+'      '
                f=open(cond+synstim+"_isi_hist.txt",'w')
                f.write(header+'\n')
                np.savetxt(f,hist,fmt='%.5f')
                f.close()
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
    presyn_types=weights.keys()
    #even better, get presyn_types from pre_spikes[key][0].keys()
    #for presyn in presyn_types:
    #    cc.plot_cross_corr(pre_spikes,spiketime_dict,presyn,binsize,maxtime=20)
    ################################### End cross correlogram ##################### 
    ##### Plots of means compared across conditions or across presyn_set
    #1st STA
    if len(condition)>1:
        pu.plot_sta_vm_cond(pre_xvals,sta_list,mean_sta_vm)
    elif len(presyn_set)>1:
        cond=condition[0]
        plt.figure()
        plt.suptitle('mean sta vm')
        for i,(key,mean_sta) in enumerate(mean_sta_vm[cond].items()):
            plt.plot(pre_xvals,mean_sta,label=key)
        plt.legend()
        plt.xlabel('time (s)')
        plt.ylabel('Vm (V)')
    #else do nothing
    #2nd FFT
    colors=plt.get_cmap('viridis')
    num_colors=(len(colors.colors)-1)*0.75 #avoid the light colors by using only partial scale
    colors2D=[colors,plt.get_cmap('magma'),plt.get_cmap('Blues'),plt.get_cmap('gist_heat')]
    offset=[0,0,63]  #avoid the light colors in low indices for the 'Blues' map
    if len(condition)>len(presyn_set):
        cmap=[i%len(colors2D) for i in range(len(presyn_set))]
        color_index=[int(j*num_colors/(len(condition)-1)) for j in range(len(condition))]
        color_tuple=[(cm,ci) for ci in color_index for cm in cmap]
        plot_set=1
    elif len(presyn_set)>1:
        cmap=[i%len(colors2D) for i in range(len(condition))]
        color_index=[int(j*num_colors/(len(presyn_set)-1)) for j in range(len(presyn_set))]
        color_tuple=[(cm,ci) for cm in cmap for ci in color_index]
        plot_set=1
        #pu.plot_fft_cond(freqs,fft_mean,fft_wave)
    else:
        plot_set=0
    if plot_set:
        fig,axes=plt.subplots(2,1,sharex=True)
        fig.suptitle('Mean fft')
        for i,(cond,fft_set) in enumerate(mean_fft_phase.items()):
            maxval=np.max([np.max(np.abs(f['mag'][1:])) for f in mean_fft_phase[cond].values()])
            maxfreq=np.min(np.where(freqs[cond]>500))
            for j,(key,fft) in enumerate(fft_set.items()):
                ti=i*len(presyn_set)+j
                mycolor=colors2D[color_tuple[ti][0]].__call__(color_tuple[ti][1]+offset[color_tuple[ti][0]])
                #axes.plot(freqs[cond][0:maxfreq], np.abs(fft['mag'])[0:maxfreq], '--', label=cond+' '+key+' mean',color=colors[i])
                mean_of_fft=np.mean([np.abs(fft) for fft in fft_wave[cond][key]],axis=0)
                axes[0].plot(freqs[cond][0:maxfreq], mean_of_fft[0:maxfreq],label='mean of '+cond+' '+key,color=mycolor)
                mean_of_fft_env=np.mean([np.abs(fft) for fft in fft_env[cond][key]],axis=0)
                axes[1].plot(freqs[cond][0:maxfreq], mean_of_fft_env[0:maxfreq],label='mean of '+cond+' '+key,color=mycolor)
        axes[1].set_xlabel('Frequency in Hertz [Hz]')
        axes[0].set_ylabel('FFT Magnitude')
        axes[1].set_ylabel('FFT of envelope')
        axes[0].set_xlim(0 , freqs[cond][maxfreq] )
        axes[0].set_ylim(0,np.round(maxval) )
        axes[1].set_ylim(0,np.round(maxval) )
        axes[1].legend()
    ####### Output data for plotting #######
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
    if len(lat_mean) and plot_set:
        pu.plot_ISI_cond(all_isi_mean,isibins)
    #
    if len(inst_rate1) and plot_set:
        pu.plot_prespike_sta_cond(mean_prespike_sta1,bins1)
    #

'''
from matplotlib import pyplot as plt
condition=['POST-HFS_STNosc', 'GABA_STNosc','POST-HFS_GPeOsc', 'GABA_GPeOsc']
colors=plt.get_cmap('viridis')
presyn_set=[(0,'non',1)]
num_colors=(len(colors.colors)-1)*0.75 #avoid the light colors by using only partial scale
colors2D=[plt.get_cmap('gist_heat'),plt.get_cmap('summer'),plt.get_cmap('Blues')]
offset=[0,0,63]  #avoid the light colors in low indices for the 'Blues' map
if len(condition)>len(presyn_set):
    cmap=[i%len(colors2D) for i in range(len(presyn_set))]
    color_index=[int(j*num_colors/(len(condition)-1)) for j in range(len(condition))]
    color_tuple=[(cm,ci) for ci in color_index for cm in cmap ]
    print ('cond>presyn',color_tuple)
else:
    cmap=[i%len(colors2D) for i in range(len(condition))]
    color_index=[int(j*num_colors/(len(presyn_set)-1)) for j in range(len(presyn_set))]
    color_tuple=[(cm,ci) for cm in cmap for ci in color_index]
    print ('preyn>cond',color_tuple)
for i,cond in enumerate(condition):
    for j,presyn in enumerate(presyn_set):
        ti=i*len(presyn_set)+j
        print (cond,presyn,ti,color_tuple[ti][0],color_tuple[ti][1])

'''
#Need to move these spike_freq calulations into function that is called once per condition
from neo.core import AnalogSignal,SpikeTrain
import quantities as q
ratebins=np.arange(0,np.ceil(max_time),isi_binsize)
#spike_rate: across entire time
spike_rate={key:np.zeros((len(spike_set),len(ratebins))) for key,spike_set in spiketime_dict.items()}
spike_rate_mean={};spike_rate_std={}
#spike_freq: segmented into pre,stim,post
spike_freq={key:{} for key in spiketime_dict.keys()}
spike_freq_mean={key:{} for key in spiketime_dict.keys()}
spike_freq_std={key:{} for key in spiketime_dict.keys()}
for key,spike_set in spiketime_dict.items():
    for i in range(len(spike_set)):
        train=SpikeTrain(spike_set[i]*q.s,t_stop=np.ceil(max_time)*q.s)
        spike_rate[key][i]=elephant.statistics.instantaneous_rate(train,isi_binsize*q.s).magnitude[:,0]#/len(spike_set)
for key,rate_set in spike_rate.items():
    for pre_post,binlist in isibins.items():
        binmin_idx=np.abs(ratebins-binlist[0]).argmin()
        binmax_idx=np.abs(ratebins-(binlist[-1]+isi_binsize)).argmin()
        spike_freq[key][pre_post]=spike_rate[key][:,binmin_idx:binmax_idx]
    spike_rate_mean[key]=np.mean(spike_rate[key],axis=0)
    spike_rate_std[key]=np.std(spike_rate[key],axis=0)
    for pre_post,binlist in isibins.items():
        spike_freq_mean[key][pre_post]=np.mean(spike_freq[key][pre_post],axis=0)
        spike_freq_std[key][pre_post]=np.std(spike_freq[key][pre_post],axis=0)

#create spike_freq_plot function that is called once per condition
fig,axes =plt.subplots(len(spike_rate),1,sharex=True)
for i,key1 in enumerate(spike_rate.keys()):
    axes[i].plot(ratebins,spike_rate_mean[key1],label='eleph')
    for key2 in spike_freq_mean[key1].keys():
        axes[i].plot(isibins[key2],spike_freq_mean[key1][key2],label=key2)
    axes[i].set_ylabel(key1)
axes[0].set_xlim([1,max_time-1])
axes[-1].set_xlabel('time')
axes[0].legend()
fig.suptitle('firing rate')
#this shows that std increases during stim with str
#data good for bar plot
f=open("spike_rate_stats.txt",'w')
header='spike frequencies: condition, epoch mean, std, CV\n'
f.write(header)
print(header)
for k1 in spike_freq_mean.keys():
    for k2 in spike_freq_mean[k1].keys():
        mean_firing=np.mean(spike_freq_mean[k1][k2])
        std_firing=np.std(np.mean(spike_freq[k1][k2],axis=1))
        summary='   '.join([k1,k2,str(np.round(mean_firing,3)),str(np.round(std_firing,3))])+'\n'
        f.write(summary)
        print(summary)
f.close()
#for stat analysis, output all values of spike_freq_mean for each condition, read into SAS

#to plot spike rate vs time, with error bars
f=open('spike_rate.txt','w')
header='time'
outputdata=ratebins
for key in spike_rate_mean.keys():
    outputdata=np.column_stack((outputdata,spike_rate_mean[key],spike_rate_std[key]))
    header=header+'   mean_'+key+'   std_'+key
f.write(header)
np.savetxt(f,outputdata,fmt='%.5f')
'''
to plot changes in ISI and firing frequency, need to smooth the results or use sliding window?

mean ISI:
str_freq20_plas1 pre : ISI mean, std= 0.0518993031358885 0.018427844015360285  CV= 0.35506919942856385
str_freq20_plas1 post : ISI mean, std= 0.05157269624573378 0.02108436503773002  CV= 0.40882805384591797
str_freq20_plas1 stim : ISI mean, std= 0.06322468085106382 0.02890873363219657  CV= 0.4572381108620519
GPe_freq20_plas1 pre : ISI mean, std= 0.05002173913043478 0.020325038407665655  CV= 0.4063241054987485
GPe_freq20_plas1 post : ISI mean, std= 0.05011362126245847 0.0194870733330019  CV= 0.38885781633985045
GPe_freq20_plas1 stim : ISI mean, std= 0.05332419928825622 0.019155711026434277  CV= 0.3592311048663605

firing frequency          mean     std
str_freq20_plas1   stim   15.981   1.728
str_freq20_plas1   pre   19.338   1.581
str_freq20_plas1   post   19.123   1.796
GPe_freq20_plas1   stim   18.86   1.751
GPe_freq20_plas1   pre   20.114   2.194
GPe_freq20_plas1   post   19.932   1.987
'''
