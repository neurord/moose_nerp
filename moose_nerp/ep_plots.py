import numpy as np
import os
from matplotlib import pyplot as plt
plt.ion()
import ISI_anal
colors=['r','k','b']

def plot_latency(fileprefix,filesuffix,stim_freq,neurtype,presyn_set,numbins):
    #plot the latency from network neuron simulations with one regular input train, multiple trials
    fig1,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis1=fig1.axes
    for i,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+suffix
        lat_mean,lat_std,isi_mean,isi_std,bins=ISI_anal.latency(pattern,stim_freq,neurtype,numbins)
        for k,key in enumerate(lat_mean.keys()):
            axis1[i].plot(range(len(lat_mean[key])),lat_mean[key],label=key+' mean',color=colors[k])
            axis1[i].plot(range(len(lat_std[key])),lat_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis1[i].set_xlabel('stim number')
        axis1[i].set_ylabel(presyn+'input, latency (sec)')
        fig1.suptitle('Latency: '+filesuffix.split('.')[0])
        axis1[i].legend()

def plot_ISI(fileprefix,filesuffix,stim_freq,neurtype,presyn_set,numbins):
    #plot the ISI from network neuron simulations, one regular input train, multiple trials
    fig2,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis2=fig2.axes
    for i,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+suffix
        lat_mean,lat_std,isi_mean,isi_std,bins=ISI_anal.latency(pattern,stim_freq,neurtype,numbins)
        for k,key in enumerate(bins.keys()):
            axis2[i].plot(bins[key],isi_mean[key],label=key+' mean',color=colors[k])
            axis2[i].plot(bins[key],isi_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis2[i].set_xlabel('time (sec)')
        axis2[i].set_ylabel(presyn+'input, isi (sec)')
        fig2.suptitle('ISI: '+filesuffix.split('.')[0])
        axis2[i].legend()

def plot_postsyn_raster(fileroot,suffix,presyn_set,stim_freq):
    ####### Raster plot of spikes in post-synaptic neuron #############
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle('output '+suffix)
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+suffix
        files=ISI_anal.file_set(pattern)
        spiketimes=[]
        if len(files)>0:
            for fname in files:
                dat=np.load(fname,'r')
                spiketimes.append(dat['spike_time'].item()[neurtype][0])
            axis[ax].eventplot(spiketimes)
            xstart=dat['params'].item()['ep']['syn_tt'][0][1][0]
            xend=dat['params'].item()['ep']['syn_tt'][0][1][-1]
            maxt=max([max(st) for st in spiketimes])
            axis[ax].annotate('stim onset',xy=(xstart,0),xytext=(xstart/maxt, -0.2), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05))
            axis[ax].annotate('offset',xy=(xend,0),xytext=(xend/maxt, -0.2), textcoords='axes fraction', arrowprops=dict(facecolor='red', shrink=0.05))
        axis[ax].set_ylabel(presyn+' trial')
    axis[-1].set_xlabel('time (sec)')
    return

#################### plot the set of results from single neuron simulations, range of input frequencies
##### either normalized PSPs if no spikes, or ISIs if spikes
def plot_freq_dep_psp(fileroot,presyn_set,suffix,neurtype):
    all_results=[];all_xvals=[]
    for i,presyn in enumerate(presyn_set):
        numplots,results,xval_set,xlabel,ylabel=ISI_anal.freq_dependence(fileroot,presyn,suffix)    
        all_results.append(results)
        all_xvals.append(xval_set)
    fig,axes =plt.subplots(numplots, len(presyn_set),sharex=True, sharey=True)
    fig.suptitle(neurtype+suffix)
    axis=fig.axes
    for i,presyn in enumerate(presyn_set):
        for freq in sorted(all_results[i].keys()):
            for j,ntype in enumerate(all_results[i][freq].keys()):
                axisnum=i*len(all_results[i][freq].keys())+j
                for yval in all_results[i][freq][ntype]:
                    axis[axisnum].scatter(all_xvals[i][freq][ntype][0:len(yval)],yval,label=str(freq),marker='o')
                axis[axisnum].set_ylabel(str(ntype)+' '+ylabel)
            axis[axisnum].legend()
        axis[axisnum].set_xlabel(xlabel)

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
def plot_input_raster(pre_spikes,fileroot,presyn,suffix):
    colors=plt.get_cmap('viridis')
    #colors=plt.get_cmap('gist_heat')
    for trial in range(len(pre_spikes)):
        fig,axes =plt.subplots(len(pre_spikes[trial].keys()), 1,sharex=True)
        fig.suptitle('input raster '+os.path.basename(fileroot+presyn+suffix).split('.')[0]+'_'+str(trial))
        axis=fig.axes
        for ax,(key,spikes) in enumerate(pre_spikes[trial].items()):
            color_num=[int(cellnum*(colors.N/len(spikes))) for cellnum in range(len(spikes))]
            color_set=np.array([colors.__call__(color) for color in color_num])
            axis[ax].eventplot(spikes,color=color_set)
            axis[ax].set_ylabel(key)
        axis[-1].set_xlabel('time (s)')

def plot_sta_post_vm(pre_spikes,post_sta,mean_sta,post_xvals):
    fig,axes=plt.subplots(len(pre_spikes[0].keys()),1) 
    fig.suptitle('post sta')
    axis=fig.axes
    for ax,(key,post_sta_list) in enumerate(post_sta.items()):
        for sta in post_sta_list:
            axis[ax].plot(post_xvals,sta,label=str(trial))
            axis[ax].set_ylabel(key+' trig')
            axis[ax].plot(post_xvals,mean_sta[key],'k--',lw=3)
    axis[-1].set_xlabel('time (s)')
    fig.tight_layout()

def plot_sta_vm(pre_xvals,sta_list,fileroot,presyn,suffix):
    plt.figure()
    plt.title('ep STA '+os.path.basename(fileroot+presyn+suffix).split('.')[0])
    for trial in range(len(sta_list)):
        plt.plot(pre_xvals,sta_list[trial],label='sta'+str(trial))
    plt.legend(loc='upper left')
    plt.xlabel('time (s)')
    plt.ylabel('Vm (V)')

def plot_prespike_sta(prespike_sta,pre_xvals):
    fig,axes=plt.subplots(len(prespike_sta[0].keys()),1) 
    fig.suptitle('prespike sta')
    axis=fig.axes
    for trial in range(len(prespike_sta)):
        for ax,(key,sta) in enumerate(prespike_sta[trial].items()):
            axis[ax].plot(pre_xvals,sta,label=str(trial))
            axis[ax].set_ylabel(key)
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

def plot_inst_firing(inst_rate,xbins):
    fig,axes=plt.subplots(len(inst_rate[0].keys()),1) 
    fig.suptitle('instaneous pre-synaptic firing rate')
    axis=fig.axes
    for trial in range(len(inst_rate)):
        for ax,(key,frate) in enumerate(inst_rate[trial].items()):
            axis[ax].plot(xbins,frate,label=str(trial))
            axis[ax].set_ylabel(key)
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
inj='0.0'
stim_freq=20
presyn_set=['str']#,'str']
presyn='str'
numbins=10
status=['POST-NoDa', 'POST-HFS', 'GABA']
presyn_set=[('non',0),('GPe',40),('str',20)]
############################################################
#specify file name pattern
filedir='ep_net/output/'
rootname='epGABA_syn'
fileroot=filedir+rootname
suffix='_freq'+str(stim_freq)+'_plas'+str(plasYN)+'_inj'+inj+'*.npz'

#for (syn,freq) in presyn_set:
#plots for network simulations
plot_postsyn_raster(fileroot,suffix,presyn_set,stim_freq)
plot_latency(fileroot,suffix,stim_freq,neurtype,presyn_set,numbins)
#latency not too meaningfull if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
plot_ISI(fileroot,suffix,stim_freq,neurtype,presyn_set,numbins)

#plots for single neuron simulations:
#plot_freq_dep_psp(fileroot,presyn_set,suffix,neurtype)
#plot_freq_dep_vm(fileroot,presyn_set,plasYN,inj,neurtype)

############### Next analysis: ISI histogram
isi_set=ISI_anal.ISI_histogram(fileroot,presyn,suffix,stim_freq,neurtype)

#Calculate and plot histograms
#plot_isi_hist(isi_set,numbins,suffix):
mins=[np.min(flatten(isi_set[k])) for k in isi_set.keys()]
maxs=[np.max(flatten(isi_set[k])) for k in isi_set.keys()]
min_max=[np.min(mins),np.max(maxs)]
histbins=10 ** np.linspace(np.log10(min_max[0]), np.log10(min_max[1]), numbins)
histbins=np.linspace(min_max[0],min_max[1], numbins)
plt.figure()
plt.title('histogram '+suffix.split('.')[0])
hist_ep={};CV={}
symbol={'stim':'o-','pre':'.--','post':'.--'}
for pre_post,ISIs in isi_set.items():
    hist_ep[pre_post],tmp=np.histogram(flatten(ISIs),bins=histbins,range=min_max)
    CV[pre_post]=np.std(flatten(ISIs))/np.mean(flatten(ISIs))
    print(pre_post,': ISI mean, std=', np.mean(flatten(ISIs)),np.std(flatten(ISIs)),' CV=',CV[pre_post])
    plot_bins=[(histbins[i]+histbins[i+1])/2 for i in range(len(histbins)-1)]
    #plt.bar(plot_bins,hist_ep[pre_post], label=pre_post)#,color=colors.__call__(color_num[i]),width=binwidth)
    plt.plot(plot_bins,hist_ep[pre_post],symbol[pre_post], label=pre_post)
plt.legend()
plt.xlabel('ISI')
plt.ylabel('num events')

######################################## ep spike triggered average of vm before the spike
#parameters: how much time prior to spike to evaluate
sta_start=-20e-3
sta_end=0
sta_list,pre_xvals,plotdt,vmdat,spike_list=ISI_anal.sta_set(fileroot,presyn,suffix,neurtype,sta_start,sta_end)

plot_sta_vm(pre_xvals,sta_list,fileroot,presyn,suffix)

############# raster plot of input spike times and instantaneous rate
fileroot=filedir+'tt'+rootname
suffix=suffix.split('npz')[0]+'npy'
pre_spikes=ISI_anal.input_raster(fileroot,presyn,suffix)

plot_input_raster(pre_spikes,fileroot,presyn,suffix)

############################ input Spike triggered average Vm after the spike
sta_start=0e-3
sta_end=20e-3
post_sta,mean_sta,post_xvals=ISI_anal.post_sta_set(pre_spikes,sta_start,sta_end,plotdt,vmdat)

plot_sta_post_vm(pre_spikes,post_sta,mean_sta,post_xvals)

#################### use both pre-synaptic and post-synaptic spikes for spike triggered average input:
#1st calculate instantaneous input firing frequency for each type of input
binsize=plotdt#*100
def input_fire_freq(pre_spikes,binsize):
    import elephant
    from neo.core import AnalogSignal,SpikeTrain
    import quantities as q
    inst_rate1=[{} for t in range(len(pre_spikes))]
    inst_rate2=[{} for t in range(len(pre_spikes))]
    for trial in range(len(pre_spikes)):
        print('inst firing rate for trial',trial)
        for key,spike_set in pre_spikes[trial].items():
            if isinstance(spike_set, list):
                spikes = np.sort(np.concatenate([st for st in spike_set]))
            else:
                spikes=spike_set
            train=SpikeTrain(spikes*q.s,t_stop=np.ceil(spikes[-1])*q.s)
            inst_rate1[trial][key]=elephant.statistics.instantaneous_rate(train,binsize*q.s).magnitude[:,0]
            xbins=np.arange(0,np.ceil(spikes[-1]),binsize)
            inst_rate2[trial][key]=np.zeros(len(xbins))
            for i,binmin in enumerate(xbins):
                inst_rate2[trial][key][i]=len([st for st in spikes if st>=binmin and st<binmin+binsize])/binsize
    return inst_rate1,inst_rate2,xbins

#2nd calculate sta using input fire freq instead of vmdat
#weights used to sum the different external inputs - values are weights from param_net
sta_start=-20e-3
sta_end=0
weights={'gabaextern2':-2,'gabaextern3':-1,'ampaextern1':1}
prespike_sta1=ISI_anal.sta_fire_freq(inst_rate1,sta_start,sta_end,weights,xbins)
prespike_sta2=ISI_anal.sta_fire_freq(inst_rate2,sta_start,sta_end,weights,xbins)

########### Now plot instaneous pre-synaptic firing rate as well as firing rate sta 
plot_inst_firing(inst_rate1,xbins)
plot_inst_firing(inst_rate2,xbins)
plot_prespike_sta(prespike_sta1,pre_xvals)
plot_prespike_sta(prespike_sta2,pre_xvals)

plt.figure()

