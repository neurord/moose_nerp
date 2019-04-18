#Analyze set of files
import glob
import numpy as np
import detect

def spike_isi_from_vm(vmtab,simtime):
    spike_time={key:[] for key in vmtab.keys()}
    numspikes={key:[] for key in vmtab.keys()}
    isis={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        for tab in tabset:
            spike_time[neurtype].append(detect.detect_peaks(tab.vector)*tab.dt)
            isis[neurtype].append(np.diff(spike_time[neurtype][-1]))
            numspikes[neurtype]=[len(st) for st in spike_time[neurtype]]
        print(neurtype,'mean:',np.mean(numspikes[neurtype]),'rate',np.mean(numspikes[neurtype])/simtime,'from',numspikes[neurtype],
              'spikes, ISI mean&STD: ',[np.mean(isi) for isi in isis[neurtype]], [np.std(isi) for isi in isis[neurtype]] )
    return spike_time,isis

def stim_spikes(spike_time,timetables):
    stim_spikes={key:[] for key in spike_time.keys()}
    for neurtype, tabset in spike_time.items():
        for tab,tt in zip(tabset,timetables[neurtype].values()):
            stim_spikes[neurtype].append([st for st in spike_time[neurtype][-1] if st>np.min(tt.vector) and st<np.max(tt.vector)])
    return stim_spikes

def psp_amp(vmtab,timetables):
    psp_amp={key:[] for key in vmtab.keys()}
    psp_norm={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        for tab,tt in zip(tabset,timetables[neurtype].values()):
            vm_init=[tab.vector[int(t/tab.dt)] for t in tt.vector]
            #use np.min for IPSPs and np.max for EPSPs
            vm_peak=[np.min(tab.vector[int(tt.vector[i]/tab.dt):int(tt.vector[i+1]/tab.dt)]) for i in range(len(tt.vector)-1)]
            psp_amp[neurtype].append([(vm_init[i]-vm_peak[i]) for i in range(len(vm_peak))])
            psp_norm[neurtype].append([amp/psp_amp[neurtype][-1][0] for amp in psp_amp[neurtype][-1]])
    return psp_amp,psp_norm

def latency(freq,neurtype,presyn,plasYN,inj,numbins):
    pattern='epnet_syn'+presyn+'_freq'+str(freq)+'_plas'+str(plasYN)+'_inj'+inj+'*.npz'
    files=glob.glob(pattern)
    if len(files)==0:
        print('********* no files found for ',pattern)
        return
    isi=1.0/freq
    latency={'pre':[[] for i in range(freq)],'post':[[] for i in range(freq)], 'stim':[[] for i in range(freq)]}
    pre_post_stim={}
    bins={}
    with np.load(files[0],'r') as dat:
        params=dat['params'].item()
        stim_tt=params[neurtype]['syn_tt'][0][1]
    bin_size=(stim_tt[-1]+1/float(stim_freq)-stim_tt[0])/numbins
    #bins['stim']={stim_tt[0]+i*bin_size : stim_tt[0]+(i+1)*bin_size for i in range(numbins)}
    bins['stim']=[stim_tt[0]+i*bin_size for i in range(numbins)]
    num_bins=int(stim_tt[0]/bin_size)
    bins['pre']=[bins['stim'][0]-(i+1)*bin_size for i in range(num_bins)]
    bins['post']=[bins['stim'][-1]+(i+1)*bin_size for i in range(num_bins)]
    isi_set={'pre':{k:[] for k in bins['pre']},'post':{k:[] for k in bins['post']},'stim':{k:[] for k in bins['stim']}}
    for fname in files:
        dat=np.load(fname,'r')
        params=dat['params'].item()
        if 'spike_time' in dat.keys() and params['freq']==freq:
            spike_time=dat['spike_time'].item()[neurtype][0]
            #1st [0] below because could have multiple synapses stimulated
            #each item is tuple of (synapse,stim_times)
            stim_tt=params[neurtype]['syn_tt'][0][1]
            pre_post_stim['stim']=stim_tt
            num_pre=int(stim_tt[0]/isi)
            pre_post_stim['pre']=[stim_tt[0]-(i+1)*isi for i in range(min(num_pre-1,freq))]
            num_post=int((spike_time[-1]-stim_tt[-1])/isi)
            pre_post_stim['post']=[stim_tt[-1]+(i+1)*isi for i in range(min(num_pre-1,freq))]
            for pre_post in pre_post_stim.keys():
                for i,time in enumerate(pre_post_stim[pre_post]):
                    next_spike=np.min(spike_time[np.where(spike_time>time)])
                    latency[pre_post][i].append(next_spike-time)
            isi_vals=dat['isi'].item()[neurtype][0]
            st_isi=dict(zip(spike_time[1:],isi_vals))
            for pre_post in bins.keys():
                for binmin in bins[pre_post]:
                    binmax=binmin+bin_size
                    isi_set[pre_post][binmin].append([isi_val for st, isi_val in st_isi.items() if st>=binmin and st<binmax])
        else:
            print('whoops, wrong file',fname,'for freq', freq,'file contains', dat.keys())
    lat_mean={}
    lat_std={}
    for pre_post in latency.keys():
        lat_mean[pre_post]=np.mean(latency[pre_post],axis=1)
        lat_std[pre_post]=np.std(latency[pre_post],axis=1)
        print('latency {}: mean {} \n std {}'.format(pre_post,lat_mean[pre_post],lat_std[pre_post]))
    isi_mean={}
    isi_std={}
    for pre_post in isi_set.keys():
        for binmin,isilist in isi_set[pre_post].items():
            isi_set[pre_post][binmin]=[item for sublist in isilist for item in sublist]
    for pre_post in isi_set.keys():
        isi_mean[pre_post]=[np.mean(isis) for isis in isi_set[pre_post].values()]
        isi_std[pre_post]=[np.std(isis) for isis in isi_set[pre_post].values()]
        print('isi {}: mean {} \n std {}'.format(pre_post,isi_mean[pre_post],isi_std[pre_post]))
    return lat_mean,lat_std,isi_mean,isi_std,bins

def freq_dependence(presyn,plasYN,inj):
    pattern='ep_syn'+presyn+'*_plas'+str(plasYN)+'_inj'+inj+'*.npz'
    files=glob.glob(pattern)
    if len(files)==0:
        print('********* no files found for ',pattern)
        return
    frequency_set=np.unique([int(fname.split('freq')[-1].split('_')[0]) for fname in files])
    results={freq:{} for freq in frequency_set}
    xval_set={freq:{} for freq in frequency_set}
    for fname in files:
        dat=np.load(fname,'r')
        params=dat['params'].item()
        if 'norm' in dat.keys():
            numplots=len(dat['norm'].item().keys())
            results[params['freq']]={ntype:[] for ntype in dat['norm'].item().keys()}
            for neurtype in dat['norm'].item().keys():
                results[params['freq']][neurtype]=dat['norm'].item()[neurtype]
                xval_set[params['freq']][neurtype]=range(len(dat['norm']))
            ylabel='normalized PSP amp'
            xlabel='pulse'
        elif 'isi' in dat.keys():
            numplots=len(dat['isi'].item().keys())
            results[params['freq']]={ntype:[] for ntype in dat['isi'].item().keys()}
            for neurtype in dat['isi'].item().keys():
                results[params['freq']][neurtype]=dat['isi'].item()[neurtype]
                xval_set[params['freq']][neurtype]=dat['spike_time'].item()[neurtype][0]
            ylabel='isi (sec)'
            xlabel='time (sec)'
        else:
            print('issue with file {} keys {}'.format(fname,dat.keys))
    return numplots,results,xval_set,xlabel,ylabel

if __name__ == "__main__": 
    ####################################
    # Parameters of set of files to analyze
    neurtype='ep'
    plasYN=0
    #inj='-2.5e-11'
    inj='0.0'
    stim_freq=20
    numbins=10
    presyn_set=['GPe','str']
    ############################################################
    all_results=[];all_xvals=[]
    for i,presyn in enumerate(presyn_set):
        numplots,results,xval_set,xlabel,ylabel=freq_dependence(presyn,plasYN,inj)    
        all_results.append(results)
        all_xvals.append(xval_set)
        
    #plot the set of results from single neuron simulations, all frequencies
    from matplotlib import pyplot as plt
    plt.ion()
    colors=['r','k','b']
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

    #plot the set of results from network neuron simulations, one frequency, multiple trials
    fig,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis=fig.axes
    for i,presyn in enumerate(presyn_set):
        lat_mean,lat_std,isi_mean,isi_std,bins=latency(stim_freq,neurtype,presyn,plasYN,inj,numbins)
        for k,key in enumerate(lat_mean.keys()):
            axis[i].plot(range(len(lat_mean[key])),lat_mean[key],label=key+' mean',color=colors[k])
            axis[i].plot(range(len(lat_std[key])),lat_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis[i].set_xlabel('stim number')
        axis[i].set_ylabel(presyn+'input, latency (sec)')
        fig.suptitle('Latency: frequency='+str(stim_freq)+' stp='+str(plasYN))
        axis[i].legend()

    fig,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis=fig.axes
    for i,presyn in enumerate(presyn_set):
        lat_mean,lat_std,isi_mean,isi_std,bins=latency(stim_freq,neurtype,presyn,plasYN,inj,numbins)
        for k,key in enumerate(bins.keys()):
            axis[i].plot(bins[key],isi_mean[key],label=key+' mean',color=colors[k])
            axis[i].plot(bins[key],isi_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis[i].set_xlabel('time (sec)')
        axis[i].set_ylabel(presyn+'input, isi (sec)')
        fig.suptitle('ISI: frequency='+str(stim_freq)+' stp='+str(plasYN))
        axis[i].legend()

    ####### Raster plot from results #############
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle('frequency='+str(stim_freq)+' plasticity='+str(plasYN))
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern='epnet_syn'+presyn+'_freq'+str(stim_freq)+'_plas'+str(plasYN)+'_inj'+inj+'*.npz'
        files=glob.glob(pattern)
        if len(files)==0:
            print('********* no files found for ',pattern)
        spiketimes=[]
        for fname in files:
            dat=np.load(fname,'r')
            spiketimes.append(dat['spike_time'].item()[neurtype][0])
        axis[ax].eventplot(spiketimes)
        xstart=dat['params'].item()['ep']['syn_tt'][0][1][0]
        xend=dat['params'].item()['ep']['syn_tt'][0][1][-1]
        maxtime=max([max(st) for st in spiketimes])
        axis[ax].annotate('stim onset',xy=(xstart,0),xytext=(xstart/maxtime, -0.2), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05))
        axis[ax].annotate('offset',xy=(xend,0),xytext=(xend/maxtime, -0.2), textcoords='axes fraction', arrowprops=dict(facecolor='red', shrink=0.05))
        axis[ax].set_ylabel(presyn+' trial')
    axis[-1].set_xlabel('time (sec)')
#ToDo: plot set of vm
