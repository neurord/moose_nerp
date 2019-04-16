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
    latency=[[] for i in range(freq)]
    pre_post_lat={'pre':[[] for i in range(freq)],'post':[[] for i in range(freq)]}
    pre_post_stim={}
    with np.load(files[0],'r') as dat:
        params=dat['params'].item()
        stim_tt=params[neurtype]['syn_tt'][0][1]
    bin_interval=(stim_tt[-1]+1/float(stim_freq)-stim_tt[0])/numbins
    bins={stim_tt[0]+i*bin_interval: stim_tt[0]+(i+1)*bin_interval for i in range(numbins*2)}
    #bins=[(stim_tt[0]+i*bin_interval, stim_tt[0]+(i+1)*bin_interval) for i in range(numbins)]
    isi_set={k:[] for k in bins.keys()}
    for fname in files:
        dat=np.load(fname,'r')
        params=dat['params'].item()
        if 'spike_time' in dat.keys() and params['freq']==freq:
            spike_time=dat['spike_time'].item()[neurtype][0]
            #1st [0] below because could have multiple synapses stimulated
            #each item is tuple of (synapse,stim_times)
            stim_tt=params[neurtype]['syn_tt'][0][1]
            num_pre=int(stim_tt[0]/isi)
            pre_post_stim['pre']=[stim_tt[0]-(i+1)*isi for i in range(min(num_pre-1,freq))]
            num_post=int((spike_time[-1]-stim_tt[-1])/isi)
            pre_post_stim['post']=[stim_tt[-1]+(i+1)*isi for i in range(min(num_pre-1,freq))]
            for i,time in enumerate(stim_tt):
                next_spike=np.min(spike_time[np.where(spike_time>time)])
                latency[i].append(next_spike-time)
            for pre_post in pre_post_stim.keys():
                for i,time in enumerate(pre_post_stim[pre_post]):
                    next_spike=np.min(spike_time[np.where(spike_time>time)])
                    pre_post_lat[pre_post][i].append(next_spike-time)
            isi_vals=dat['isi'].item()[neurtype][0]
            st_isi=dict(zip(spike_time[1:],isi_vals))
            #for (binmin,binmax) in bins:
            for binmin,binmax in bins.items():
                isi_set[binmin].append([isi_val for st, isi_val in st_isi.items() if st>=binmin and st<binmax])
        else:
            print('whoops, wrong file',fname,'for freq', freq,'file contains', dat.keys())
    mean_lat={}
    std_lat={}
    mean_lat['stim']=np.mean(latency,axis=1)
    std_lat['stim']=np.std(latency,axis=1)
    print('latency: mean {} \n std {}'.format(mean_lat['stim'],std_lat['stim']))
    for pre_post in pre_post_lat.keys():
        mean_lat[pre_post]=np.mean(pre_post_lat[pre_post],axis=1)
        std_lat[pre_post]=np.std(pre_post_lat[pre_post],axis=1)
        print('latency {}: mean {} \n std {}'.format(pre_post,mean_lat[pre_post],std_lat[pre_post]))
    for binmin,isilist in isi_set.items():
        isi_set[binmin]=[item for sublist in isilist for item in sublist]
    print(isi_set)
    isi_mean=[np.mean(isi_set[binmin]) for binmin in isi_set.keys()]
    isi_std=[np.std(isi_set[binmin]) for binmin in isi_set.keys()]
    return mean_lat,std_lat,isi_mean,isi_std,bins

def freq_dependence(presyn,plasYN,inj):
    pattern='ep_syn'+presyn+'*_plas'+str(plasYN)+'_inj'+inj+'*.npz'
    files=glob.glob(pattern)
    if len(files)==0:
        print('********* no files found for ',pattern)
        return
    frequency_set=np.unique([int(fname.split('freq')[-1].split('_')[0]) for fname in files])
    results={freq:{} for freq in frequency_set}
    xval_set={}
    for fname in files:
        dat=np.load(fname,'r')
        params=dat['params'].item()
        if 'norm' in dat.keys():
            numplots=len(dat['norm'].item().keys())
            results[params['freq']]={ntype:[] for ntype in dat['norm'].item().keys()}
            for neurtype in dat['norm'].item().keys():
                results[params['freq']][neurtype]=dat['norm'].item()[neurtype]
                xval_set[params['freq']]=range(len(dat['norm']))
            ylabel='normalized PSP amp'
            xlabel='pulse'
        elif 'isi' in dat.keys():
            numplots=len(dat['isi'].item().keys())
            results[params['freq']]={ntype:[] for ntype in dat['isi'].item().keys()}
            for neurtype in dat['isi'].item().keys():
                results[params['freq']][neurtype]=dat['isi'].item()[neurtype]
                xval_set[params['freq']]=dat['spike_time'].item()[neurtype][0]
            ylabel='isi (sec)'
            xlabel='time (sec)'
        else:
            print('issue with file {} keys {}'.format(fname,dat.keys))
    return numplots,results,xval_set,xlabel,ylabel

if __name__ == "__main__": 
    ####################################
    # Parameters of set of files to analyze
    neurtype='ep'
    presyn='GPe'
    plasYN=1
    #inj='-2.5e-11'
    inj='0.0'
    stim_freq=20
    numbins=5
    ############################################################

    mean_lat,std_lat,isi_mean,isi_std,bins=latency(stim_freq,neurtype,presyn,plasYN,inj,numbins)

    numplots,results,xval_set,xlabel,ylabel=freq_dependence(presyn,plasYN,inj)    

    #plot the set of results:
    from matplotlib import pyplot as plt
    plt.ion()
    fig,axes =plt.subplots(numplots, 1,sharex=True)
    fig.suptitle('synapse type='+presyn+', inject='+inj)
    axis=fig.axes
    for freq in sorted(results.keys()):
        for axisnum,ntype in enumerate(results[freq].keys()):
            for yval in results[freq][ntype]:
                axis[axisnum].scatter(xval_set[freq][0:len(yval)],yval,label=str(ntype)+' '+str(freq),marker='o')
        axis[axisnum].set_ylabel(ylabel)
    axis[-1].set_xlabel(xlabel)
    axis[axisnum].legend()

    plt.figure()
    for key in mean_lat.keys():
       plt.plot(range(len(mean_lat[key])),mean_lat[key],label=key)
    plt.xlabel('stim number')
    plt.ylabel('latency')
    plt.title(presyn+' frequency='+str(stim_freq))
    plt.legend()

    plt.figure()
    plt.plot(list(bins.keys()),isi_mean)
    plt.xlabel('time (sec)')
    plt.ylabel('mean isi (sec)')
    plt.title(presyn+' frequency='+str(stim_freq))


#ToDo: raster plot of results, plot set of vm, mean isi for pre and post
