import numpy as np
from matplotlib import pyplot as plt
plt.ion()
import ISI_anal
colors=['r','k','b']

def ISI_plot(stim_freq,neurtype,presyn_set,plasYN,inj,numbins):
    #plot the ISI and latency from network neuron simulations, one frequency, multiple trials
    fig1,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis1=fig1.axes
    for i,presyn in enumerate(presyn_set):
        lat_mean,lat_std,isi_mean,isi_std,bins=ISI_anal.latency(stim_freq,neurtype,presyn,plasYN,inj,numbins)
        for k,key in enumerate(lat_mean.keys()):
            axis1[i].plot(range(len(lat_mean[key])),lat_mean[key],label=key+' mean',color=colors[k])
            axis1[i].plot(range(len(lat_std[key])),lat_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis1[i].set_xlabel('stim number')
        axis1[i].set_ylabel(presyn+'input, latency (sec)')
        fig1.suptitle('Latency: frequency='+str(stim_freq)+' stp='+str(plasYN))
        axis1[i].legend()

def latency_plot(stim_freq,neurtype,presyn_set,plasYN,inj,numbins):
    fig2,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis2=fig2.axes
    for i,presyn in enumerate(presyn_set):
        lat_mean,lat_std,isi_mean,isi_std,bins=ISI_anal.latency(stim_freq,neurtype,presyn,plasYN,inj,numbins)
        for k,key in enumerate(bins.keys()):
            axis2[i].plot(bins[key],isi_mean[key],label=key+' mean',color=colors[k])
            axis2[i].plot(bins[key],isi_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis2[i].set_xlabel('time (sec)')
        axis2[i].set_ylabel(presyn+'input, isi (sec)')
        fig2.suptitle('ISI: frequency='+str(stim_freq)+' stp='+str(plasYN))
        axis2[i].legend()

def raster_plot(presyn_set,stim_freq,plasYN):
    ####### Raster plot from results #############
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle('frequency='+str(stim_freq)+' plasticity='+str(plasYN))
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern='epnet_syn'+presyn+'_freq'+str(stim_freq)+'_plas'+str(plasYN)+'_inj'+inj+'*.npz'
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

#plot the set of results from single neuron simulations, all frequencies
#either normalized PSPs if no spikes, or ISIs if spikes
def freq_dep_plot(presyn_set,plasYN,inj,neurtype):
    all_results=[];all_xvals=[]
    for i,presyn in enumerate(presyn_set):
        numplots,results,xval_set,xlabel,ylabel=ISI_anal.freq_dependence(presyn,plasYN,inj)    
        all_results.append(results)
        all_xvals.append(xval_set)
    fig,axes =plt.subplots(numplots, len(presyn_set),sharex=True, sharey=True)
    fig.suptitle(neurtype+' stp='+str(plasYN)+', inject='+inj)
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

def freq_dep_vm(presyn_set,plasYN,inj,neurtype):
####### Membrane potential  #############
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle(' plasticity='+str(plasYN))
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern='ep_syn'+presyn+'*_plas'+str(plasYN)+'_inj'+inj+'*Vm.txt'
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


####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
inj='2.5e-11'
#inj='-1.5e-11'
stim_freq=20
numbins=10
presyn_set=['GPe','str']
############################################################
#plots for network simulations:
latency_plot(stim_freq,neurtype,presyn_set,plasYN,inj,numbins)
ISI_plot(stim_freq,neurtype,presyn_set,plasYN,inj,numbins)
raster_plot(presyn_set,stim_freq,plasYN)

#plots for single neuron simulations:
#freq_dep_plot(presyn_set,plasYN,inj,neurtype)
#freq_dep_vm(presyn_set,plasYN,inj,neurtype)
