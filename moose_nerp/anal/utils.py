"""
same as anal.py used in brian sims, except for addition of spiktime_from_vm
"""
import numpy as np
import detect

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def spikerate_func(spiketime_dict,simtime,binsize):
    import elephant as elph
    from neo.core import AnalogSignal,SpikeTrain
    import quantities as q
    spike_rate_elph={};spike_rate_mean={};spike_rate_xvals={}
    for ntype in spiketime_dict.keys():
        spike_rate_elph[ntype]=np.zeros((len(spiketime_dict[ntype]),int(simtime/binsize)))
        for i,spiketrain in enumerate(spiketime_dict[ntype]):
            train=SpikeTrain(spiketrain*q.s,t_stop=simtime*q.s)
            #NOTE, instantaneous_rate fails with kernel=auto and small number of spikes
            kernel=elph.kernels.GaussianKernel(sigma=binsize*q.s)
            spike_rate_elph[ntype][i,:]=elph.statistics.instantaneous_rate(train,binsize*q.s,kernel=kernel).magnitude[:,0]
        spike_rate_mean[ntype]=np.mean(spike_rate_elph[ntype],axis=0)
        spike_rate_xvals[ntype]=np.linspace(0,simtime,len(spike_rate_mean[ntype]))
    return spike_rate_elph,spike_rate_mean,spike_rate_xvals

def spiketime_from_vm(vmtab,dt):
    spike_time={key:[] for key in vmtab.keys()}
    numspikes_mean={key:[] for key in vmtab.keys()};numspikes_ste={key:[] for key in vmtab.keys()}
    numspikes={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        for tab in tabset:
            spike_time[neurtype].append(detect.detect_peaks(tab)*dt)
            numspikes[neurtype]=[len(st) for st in spike_time[neurtype]]
        print(neurtype,'mean spikes:',np.mean(numspikes[neurtype]), 'ste',np.std(numspikes[neurtype])/np.sqrt(len(numspikes[neurtype])) )
    return spike_time

def fft_func(spike_rate,dt,init_time=0,maxfreq=None,window=11):
    fft_wave={k:[] for k in spike_rate.keys()}
    freqs={}
    for ntype in spike_rate.keys():
        data_length=np.shape(spike_rate[ntype])[1]
        init_point=int(init_time/dt)
        freqs[ntype]=np.fft.rfftfreq(data_length-init_point,dt)
        maxpoint=None
        if maxfreq is not None:
            X=np.where(freqs[ntype]>maxfreq)
            if len(X):
                maxpoint=np.min(X)
                freqs[ntype]=freqs[ntype][0:maxpoint]
        for wave in spike_rate[ntype]:
            data=wave[init_point:]
            fft_wave[ntype].append(np.fft.rfft(data)[0:maxpoint])
        mean_fft={ntype:np.mean([np.abs(ft**2) for ft in fftset],axis=0) for ntype,fftset in fft_wave.items()} #PSD
        std_fft={ntype:np.std([np.abs(ft**2) for ft in fftset],axis=0) for  ntype,fftset in fft_wave.items()}
    return mean_fft,std_fft,freqs

def shuffle(spikes,num_shuffles):
    shuffle_spikes={ntype:[] for ntype in spikes.keys()}
    for ntype in spikes.keys():
        for i,spiketrain in enumerate(spikes[ntype]):
            if len(spiketrain):
                dT=np.zeros(len(spiketrain))
                dT[1:]=np.diff(spiketrain)
                dT[0]=spiketrain[0]
                for j in range(num_shuffles):
                    np.random.shuffle(dT)
                    shuffle_spikes[ntype].append(np.cumsum(dT))
        print('num spiketrains',len(spikes[ntype]),', num shuffles', np.shape(shuffle_spikes[ntype]))
    return shuffle_spikes

def isi(spikes,numbins,min_max=None):
    spike_isi={k:[] for k in spikes.keys()}
    isi_stats={};isi_hist={}
    for ntype in spikes.keys():
        for i,spiketrain in enumerate(spikes[ntype]):
            spike_isi[ntype].append(np.diff(spiketrain))
        isi_stats[ntype]={'mean':np.mean(flatten(spike_isi[ntype])), 
                          'std':np.std(flatten(spike_isi[ntype])),
                          'median':np.median(flatten(spike_isi[ntype]))}
    mins=[np.min(flatten(isis)) for isis in spike_isi.values()]
    maxs=[np.max(flatten(isis)) for isis in spike_isi.values()]
    print('min isi',mins,maxs)
    if not min_max:
        min_max[0]=np.min(mins)
        min_max[1]=np.max(maxs)
    histbins=np.linspace(min_max[0],min_max[1], numbins)
    for ntype,spikeset in spike_isi.items():
        isi_hist[ntype],tmp=np.histogram(flatten(spikeset),bins=histbins,range=min_max)
    return spike_isi,isi_stats,isi_hist,histbins      
