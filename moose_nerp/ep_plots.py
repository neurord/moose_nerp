import numpy as np
import os
import elephant
#must import elephant prior to matplotlib else plt.ion() doesn't work properly
from matplotlib import pyplot as plt
plt.ion()
import ISI_anal
colors=['r','k','b']

def plot_latency(rootname,lat_mean_dict,lat_std_dict,filesuffix):
    #plot the latency from network neuron simulations with one regular input train, multiple trials
    fig,axes =plt.subplots(len(lat_mean_dict),1,sharex=True)
    axis=fig.axes
    for i,synstim in enumerate(lat_mean_dict.keys()):
        presyn=synstim.split('_')[0]
        freq=synstim.split('_')[1]
        for k,key in enumerate(lat_mean_dict[synstim].keys()):
            xvals=range(len(lat_mean_dict[synstim][key]))
            axis[i].plot(xvals,lat_mean_dict[synstim][key],label=key+' mean',color=colors[k])
            axis[i].plot(xvals,lat_std_dict[synstim][key],label=key+' std',linestyle='dashed',color=colors[k])
        axis[i].set_xlabel('stim number')
        axis[i].set_ylabel(presyn+' input, latency (sec)')
        fig.suptitle('Latency: '+rootname+filesuffix.split('.')[0])
        axis[i].legend()

def plot_ISI(rootname,isi_mean_dict,isi_std_dict,bins,filesuffix):
    #plot the ISI from network neuron simulations, one regular input train, multiple trials
    fig,axes =plt.subplots(len(isi_mean_dict),1,sharex=True)
    axis=fig.axes
    for i,synstim in enumerate(isi_mean_dict.keys()):
        presyn=synstim.split('_')[0]
        freq=synstim.split('_')[1]
        for k,key in enumerate(bins.keys()):
            axis[i].plot(bins[key],isi_mean_dict[synstim][key],label=key+' mean',color=colors[k])
            axis[i].plot(bins[key],isi_std_dict[synstim][key],label=key+' std',linestyle='dashed',color=colors[k])
        axis[i].set_xlabel('time (sec)')
        axis[i].set_ylabel(presyn+' input, isi (sec)')
        fig.suptitle('ISI: '+rootname+filesuffix.split('.')[0])
        axis[i].legend()

def plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info):
    ####### Raster plot of spikes in post-synaptic neuron #############
    fig,axes =plt.subplots(len(spiketime_dict), 1,sharex=True)
    fig.suptitle('output '+rootname+suffix)
    axis=fig.axes
    for ax,key in enumerate(spiketime_dict.keys()):
        axis[ax].eventplot(spiketime_dict[key])
        axis[ax].set_ylabel(key+' trial')
        if len(syntt_info[key]):
            xstart=syntt_info[key]['xstart']
            xend=syntt_info[key]['xend']
            maxt=syntt_info[key]['maxt']
            axis[ax].annotate('stim onset',xy=(xstart,0),xytext=(xstart/maxt, -0.2),
                              textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05))
            axis[ax].annotate('offset',xy=(xend,0),xytext=(xend/maxt, -0.2),
                              textcoords='axes fraction', arrowprops=dict(facecolor='red', shrink=0.05))
    axis[-1].set_xlabel('time (sec)')
    return

#################### plot the set of results from single neuron simulations, range of input frequencies
##### either normalized PSPs if no spikes, or ISIs if spikes
def plot_freq_dep_psp(fileroot,presyn_set,suffix,neurtype):
    all_results={};all_xvals={}
    for i,presyn in enumerate(presyn_set):
        numplots,results,xval_set,xlabel,ylabel=ISI_anal.freq_dependence(fileroot,presyn,suffix)    
        all_results[presyn]=results
        all_xvals[presyn]=xval_set
    fig,axes =plt.subplots(numplots, len(presyn_set),sharex=True, sharey=True)
    fig.suptitle(neurtype+suffix)
    axis=fig.axes
    for i,presyn in enumerate(presyn_set):
        for freq in sorted(all_results[presyn].keys()):
            for j,ntype in enumerate(all_results[presyn][freq].keys()):
                axisnum=i*len(all_results[presyn][freq].keys())+j
                for yval in all_results[presyn][freq][ntype]:
                    axis[axisnum].scatter(all_xvals[presyn][freq][ntype][0:len(yval)],yval,label=str(ntype)+str(freq),marker='.')
                axis[axisnum].set_ylabel(str(presyn)+' '+ylabel)
            axis[axisnum].legend()
        axis[axisnum].set_xlabel(xlabel)
    return all_results,all_xvals

####### Membrane potential  #############
def plot_freq_dep_vm(fileroot,presyn_set,plasYN,inj,neurtype):
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle(' plasticity='+str(plasYN))
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+'*_plas'+str(plasYN)+'_inj'+inj+'*Vm.txt'
        files=ISI_anal.file_set(pattern)
        if len(files)>0:
            vm_set={}
            for fname in sorted(files):
                data=np.loadtxt(fname,skiprows=0)
                freq=fname.split('freq')[-1].split('_')[0]
                vm_set[freq]=(data[:,0],data[:,1])
            offset=0
            for freq,(tim,vm) in vm_set.items():
                offset=offset+2 #mV
                axis[ax].plot(tim,1000*vm+offset,label=freq)
        axis[ax].set_ylabel(presyn+' Vm (mV)')
        axis[ax].legend()
    axis[-1].set_xlabel('Time (sec)')

#################### Raster plot of pre-synaptic inputs 
def plot_input_raster(pre_spikes,pattern,maxplots=None):
    colors=plt.get_cmap('viridis')
    #colors=plt.get_cmap('gist_heat')
    if maxplots:
        numplots=min(maxplots,len(pre_spikes))
    else:
        numplots=len(pre_spikes)
    for trial in range(numplots):
        fig,axes =plt.subplots(len(pre_spikes[trial].keys()), 1,sharex=True)
        fig.suptitle('input raster '+os.path.basename(pattern).split('.')[0]+'_'+str(trial))
        axis=fig.axes
        for ax,(key,spikes) in enumerate(pre_spikes[trial].items()):
            color_num=[int(cellnum*(colors.N/len(spikes))) for cellnum in range(len(spikes))]
            color_set=np.array([colors.__call__(color) for color in color_num])
            axis[ax].eventplot(spikes,color=color_set)
            axis[ax].set_ylabel(key)
        axis[-1].set_xlabel('time (s)')

def plot_sta_post_vm(pre_spikes,post_sta_dict,mean_sta_dict,post_xvals):
    for i,(synstim,sta_list) in enumerate(post_sta_dict.items()):
        fig,axes=plt.subplots(len(pre_spikes[synstim][0].keys()),1) 
        fig.suptitle('post sta '+synstim)
        axis=fig.axes
        for ax,(key,post_sta) in enumerate(sta_list.items()):
            for trial,sta in enumerate(post_sta):
                axis[ax].plot(post_xvals,sta,label=str(trial))
                axis[ax].set_ylabel(key+' trig')
            axis[ax].plot(post_xvals,mean_sta[synstim][key],'k--',lw=3)
        axis[-1].set_xlabel('time (s)')
        #fig.tight_layout()

def plot_sta_vm(pre_xvals,sta_list_dict,fileroot,suffix):
    fig,axes =plt.subplots(len(sta_list_dict),1,sharex=True)
    axis=fig.axes
    fig.suptitle('ep STA '+os.path.basename(fileroot+suffix).split('_')[0])
    for i,(synstim,sta_list) in enumerate(sta_list_dict.items()):
        for trial in range(len(sta_list)):
            axis[i].plot(pre_xvals,sta_list[trial],label='sta'+str(trial))
        axis[i].set_ylabel(synstim+' Vm (V)')
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

def plot_prespike_sta(prespike_sta,mean_sta,pre_xvals,title=''):
    fig,axes=plt.subplots(len(prespike_sta[0].keys()),1) 
    fig.suptitle('prespike sta '+title)
    axis=fig.axes
    for trial in range(len(prespike_sta)):
        for ax,(key,sta) in enumerate(prespike_sta[trial].items()):
            axis[ax].plot(pre_xvals,sta,label=str(trial))
            axis[ax].set_ylabel(key)
    for ax,(key,sta) in enumerate(mean_sta.items()):
        axis[ax].plot(pre_xvals,sta,'k--',lw=3)
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

def plot_inst_firing(inst_rate,xbins,title=''):
    fig,axes=plt.subplots(len(inst_rate[0].keys()),1) 
    fig.suptitle('instaneous pre-syn firing rate '+title)
    axis=fig.axes
    for trial in range(len(inst_rate)):
        for ax,(key,frate) in enumerate(inst_rate[trial].items()):
            axis[ax].plot(xbins,frate,label=str(trial))
            axis[ax].set_ylabel(key)
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

#Calculate and plot histograms
def plot_isi_hist(rootname,isi_set_dict,numbins,suffix):
    fig,axes =plt.subplots(len(isi_set_dict),1,sharex=True)
    axis=fig.axes
    fig.suptitle('histogram '+rootname+suffix.split('.')[0])
    symbol={'stim':'o-','pre':'.--','post':'.--'}
    for i,(synstim,isi_set) in enumerate(isi_set_dict.items()):
        presyn=synstim.split('_')[0]
        freq=synstim.split('_')[1]
        mins=[np.min(flatten(isi_set[k])) for k in isi_set.keys()]
        maxs=[np.max(flatten(isi_set[k])) for k in isi_set.keys()]
        min_max=[np.min(mins),np.max(maxs)]
        histbins=10 ** np.linspace(np.log10(min_max[0]), np.log10(min_max[1]), numbins)
        histbins=np.linspace(min_max[0],min_max[1], numbins)
        hist_ep={};CV={}
        for pre_post,ISIs in isi_set.items():
            hist_ep[pre_post],tmp=np.histogram(flatten(ISIs),bins=histbins,range=min_max)
            plot_bins=[(histbins[i]+histbins[i+1])/2 for i in range(len(histbins)-1)]
            #plt.bar(plot_bins,hist_ep[pre_post], label=pre_post)#,color=colors.__call__(color_num[i]),width=binwidth)
            axis[i].plot(plot_bins,hist_ep[pre_post],symbol[pre_post], label=pre_post)
            CV[pre_post]=np.std(flatten(ISIs))/np.mean(flatten(ISIs))
            print(synstim,pre_post,': ISI mean, std=', np.mean(flatten(ISIs)),np.std(flatten(ISIs)),' CV=',CV[pre_post])
        axis[i].set_ylabel(synstim+' events')
    axis[-1].legend()
    axis[-1].set_xlabel('ISI')

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

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
filedir='ep_net/output/'
rootname='ep'+condition[2]+'_syn'
#filedir='ep/output/'
#rootname='ep_syn'
fileroot=filedir+rootname
suffix='_plas'+str(plasYN)+'_inj'+inj+'*.npz'

####### plots for single neuron simulations, multiple frequencies, single trials:
#all_results,all_xvals=plot_freq_dep_psp(fileroot,presyn,suffix,neurtype)
#plot_freq_dep_vm(fileroot,presyn,plasYN,inj,neurtype)

######### most of these analyses,except for sta, assume multiple trials
#time points for spike triggered average
sta_start=-30e-3
sta_end=0

spiketime_dict={};syntt_info={}
lat_mean={};lat_std={}
isi_mean={};isi_std={}
isi_set={}
sta_list={};vmdat={}
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

#####1st set of graphs
if show_plots:
    #plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info)
    #plot_latency(rootname,lat_mean,lat_std,suffix)
    #latency not too meaningful if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
    #plot_ISI(rootname,isi_mean,isi_std,bins,suffix)
    #ISI histogram
    #plot_isi_hist(rootname,isi_set,numbins,suffix)
    #ep spike triggered average of vm before the spike (the standard sta)
    plot_sta_vm(pre_xvals,sta_list,fileroot,suffix)
    #accumulate the sta_list for each condition, plot all conditions on one panel

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
    key=syn+'_'+'freq'+str(freq)
    #calculate raster of pre-synaptic spikes
    pre_spikes[key]=ISI_anal.input_raster(files)
    # input Spike triggered average Vm after the spike
    post_sta[key],mean_sta[key],post_xvals=ISI_anal.post_sta_set(pre_spikes[key],sta_start,sta_end,plotdt,vmdat[key])
if show_plots:
    plot_sta_post_vm(pre_spikes,post_sta,mean_sta,post_xvals)

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

for key in pre_spikes:
    inst_rate1[key],inst_rate2[key],xbins=ISI_anal.input_fire_freq(pre_spikes[key],binsize)
    prespike_sta1[key],mean_pre_sta1[key],bins1=ISI_anal.sta_fire_freq(inst_rate1[key],spiketime_dict[key],sta_start,sta_end,weights,xbins)
    prespike_sta2[key],mean_pre_sta2[key],bins2=ISI_anal.sta_fire_freq(inst_rate2[key],spiketime_dict[key],sta_start,sta_end,weights,xbins)
######## second set of graphs
if show_plots:
    for key in pre_spikes:
        plot_inst_firing(inst_rate1[key],xbins,title=key+' smoothed')
        plot_inst_firing(inst_rate2[key],xbins,title=key)
        plot_prespike_sta(prespike_sta1[key],mean_pre_sta1[key],bins1,title=key+' smoothed')
        plot_prespike_sta(prespike_sta2[key],mean_pre_sta2[key],bins2,title=key)
        plot_input_raster(pre_spikes[key],pattern,maxplots=1)
    #accumulate the mean prespike_sta for each condition, plot all conditions on one panel to see the differences
    #smooth prespike_sta without using elephant

