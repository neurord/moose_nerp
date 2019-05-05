#Functions for calculating ISI, latency, psp_amplitude for a set of files
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

def isi_vs_time(spike_time,isi_vals,bins,binsize,isi_set):
    st_isi=dict(zip(spike_time[1:],isi_vals))
    for pre_post in bins.keys():
        for binmin in bins[pre_post]:
            binmax=binmin+binsize
            isi_set[pre_post][binmin].append([isi_val for st, isi_val in st_isi.items() if st>=binmin and st<binmax])
    return isi_set

def latency(pattern,freq,neurtype,numbins):
    files=file_set(pattern)
    if len(files)==0:
        return
    isi=1.0/freq
    latency={'pre':np.zeros((freq,len(files))),'post':np.zeros((freq,len(files))), 'stim':np.zeros((freq,len(files)))}
    pre_post_stim={}
    bins={}
    with np.load(files[0],'r') as dat:
        params=dat['params'].item()
        stim_tt=params[neurtype]['syn_tt'][0][1]
    bin_size=(stim_tt[-1]+1/float(freq)-stim_tt[0])/numbins
    #bins['stim']={stim_tt[0]+i*bin_size : stim_tt[0]+(i+1)*bin_size for i in range(numbins)}
    bins['stim']=[stim_tt[0]+i*bin_size for i in range(numbins)]
    num_bins=int(stim_tt[0]/bin_size)
    bins['pre']=[bins['stim'][0]-(i+1)*bin_size for i in range(num_bins)]
    bins['post']=[bins['stim'][-1]+(i+1)*bin_size for i in range(num_bins)]
    isi_set={'pre':{k:[] for k in bins['pre']},'post':{k:[] for k in bins['post']},'stim':{k:[] for k in bins['stim']}}
    for fnum,fname in enumerate(files):
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
                    latency[pre_post][i,fnum]=next_spike-time
            isi_vals=dat['isi'].item()[neurtype][0]
            isi_set=isi_vs_time(spike_time,isi_vals,bins,bin_size,isi_set)
        else:
            print('whoops, wrong file',fname,'for freq', freq,'file contains', dat.keys())
    lat_mean={}
    lat_std={}
    for pre_post in latency.keys():
        lat_mean[pre_post]=np.mean(latency[pre_post],axis=1)
        lat_std[pre_post]=np.std(latency[pre_post],axis=1)
        #print('latency {}: mean {} \n std {}'.format(pre_post,lat_mean[pre_post],lat_std[pre_post]))
    isi_mean={}
    isi_std={}
    for pre_post in isi_set.keys():
        for binmin,isilist in isi_set[pre_post].items():
            isi_set[pre_post][binmin]=[item for sublist in isilist for item in sublist]
    for pre_post in isi_set.keys():
        isi_mean[pre_post]=[np.mean(isis) for isis in isi_set[pre_post].values()]
        isi_std[pre_post]=[np.std(isis) for isis in isi_set[pre_post].values()]
        #print('isi {}: mean {} \n std {}'.format(pre_post,isi_mean[pre_post],isi_std[pre_post]))
    return lat_mean,lat_std,isi_mean,isi_std,bins

def freq_dependence(fileroot,presyn,suffix):
    pattern=fileroot+presyn+'*'+suffix
    files=file_set(pattern)
    if len(files)==0:
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

def file_set(pattern):
    files=glob.glob(pattern)
    if len(files)==0:
        print('********* no files found for ',pattern)
    return files

############# Call this from multisim, after import ISI_anal
#  ISI_anal.save_tt(connections)
def save_tt(connections):
    used_tt={}
    for syntype in connections['ep']['/ep'].keys():
        used_tt[syntype]={}
        for ext in connections['ep']['/ep'][syntype].keys():
            used_tt[syntype][ext]={}
            for syn in connections['ep']['/ep'][syntype][ext].keys():
                tt=moose.element(connections['ep']['/ep'][syntype][ext][syn])
                used_tt[syntype][ext][syn]=tt.vector
    np.save('tt'+param_sim.fname,used_tt)

