#Functions for calculating ISI, latency, psp_amplitude for a set of files
import glob
import numpy as np

import detect

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

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

def set_up_bins(file0,freq,numbins,neurtype):
    bins={}
    with np.load(file0,'r') as dat:
        params=dat['params'].item()
        #1st [0] below because could have multiple synapses stimulated
        #each item is tuple of (synapse,stim_times)
        stim_tt=params[neurtype]['syn_tt'][0][1]
        #simtime=params[simtime]
        simtime=4.0
    bin_size=(stim_tt[-1]+1/float(freq)-stim_tt[0])/numbins
    #bins['stim']={stim_tt[0]+i*bin_size : stim_tt[0]+(i+1)*bin_size for i in range(numbins)}
    bins['stim']=[stim_tt[0]+i*bin_size for i in range(numbins)]
    num_bins=min(numbins,int(stim_tt[0]/bin_size))
    bins['pre']=[bins['stim'][0]-(i+1)*bin_size for i in range(num_bins)]
    bins['post']=[bins['stim'][-1]+(i+1)*bin_size for i in range(num_bins)]
    return bins,bin_size,stim_tt,simtime

def setup_stimtimes(freq,stim_tt,isi,simtime):
    pre_post_stim={}
    pre_post_stim['stim']=stim_tt
    num_pre=int(stim_tt[0]/isi)
    pre_post_stim['pre']=[stim_tt[0]-(i+1)*isi for i in range(min(num_pre-1,freq))]
    num_post=int((simtime-stim_tt[-1])/isi)
    pre_post_stim['post']=[stim_tt[-1]+(i+1)*isi for i in range(min(num_post-1,freq))]
    return pre_post_stim

def latency(pattern,freq,neurtype,numbins):
    files=file_set(pattern)
    if len(files)==0:
        return
    isi=1.0/freq
    latency={'pre':np.zeros((freq,len(files))),'post':np.zeros((freq,len(files))), 'stim':np.zeros((freq,len(files)))}
    bins,bin_size,stim_tt,simtime=set_up_bins(files[0],freq,numbins,neurtype)
    isi_set={'pre':{k:[] for k in bins['pre']},'post':{k:[] for k in bins['post']},'stim':{k:[] for k in bins['stim']}}
    pre_post_stim=setup_stimtimes(freq,stim_tt,isi,simtime)
    for fnum,fname in enumerate(files):
        dat=np.load(fname,'r')
        params=dat['params'].item()
        if 'spike_time' in dat.keys() and params['freq']==freq:
            spike_time=dat['spike_time'].item()[neurtype][0]
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
    files=sorted(glob.glob(pattern))
    if len(files)==0:
        print('********* no files found for ',pattern)
    return files

def ISI_histogram(fileroot,presyn,suffix,stim_freq,neurtype):
    pattern=fileroot+presyn+suffix
    files=file_set(pattern)
    if len(files)==0:
        print('no files found')

    #set-up pre, during and post-stimulation time frames (bins)
    bins,binsize,stim_tt,simtime=set_up_bins(files[0],stim_freq,1,neurtype)
    isi_set={'pre':[],'post':[],'stim':[]}
    #read in ISI data and separate into 3 time frames
    for fname in files:
        dat=np.load(fname,'r')
        params=dat['params'].item()
        if 'spike_time' in dat.keys() and params['freq']==stim_freq:
            spike_time=dat['spike_time'].item()[neurtype][0]
            isi_vals=dat['isi'].item()[neurtype][0]
            #separate into pre, post and during stimulation (optional)
            st_isi=dict(zip(spike_time[1:],isi_vals))
            for pre_post,binlist in bins.items():
                binmin=binlist[0]
                binmax=binmin+binsize
                isi_set[pre_post].append([isi_val for st, isi_val in st_isi.items() if st>=binmin and st<binmax])
        else:
            print('wrong frequency')
    return isi_set

#################### Spike triggered averages
def calc_sta(spike_time,window,vmdat,plotdt):
    numspikes=len(spike_time)
    samplesize=window[-1]-window[0]
    sta_array=np.zeros((numspikes,samplesize))
    for i,st in enumerate(spike_time):
        endpt=int(st/plotdt)+window[1]
        if endpt<len(vmdat):
            startpt=endpt-samplesize
            if startpt<0:
                sta_start=-startpt
                startpt=0
            else:
                sta_start=0
            sta_array[i,sta_start:]=vmdat[startpt:endpt]
    sta=np.mean(sta_array,axis=0)
    xvals=np.arange(window[0]*plotdt,window[1]*plotdt,plotdt)
    return xvals,sta

def sta_set(fileroot,presyn,suffix,neurtype,sta_start,sta_end):
    pattern=fileroot+presyn+suffix
    files=file_set(pattern)
    vmdat=[]
    sta_list=[]
    spike_set=[]
    for trial,fname in enumerate(files):
        dat=np.load(fname,'r')
        params=dat['params'].item()
        plotdt=params['dt']
        window=(int(sta_start/plotdt),int(sta_end/plotdt))
        if 'spike_time' in dat.keys():# and ['freq']==stimfreq:
            spike_time=dat['spike_time'].item()[neurtype][0]
            vmdat.append(dat['vm'].item()[neurtype])
            xvals,sta=calc_sta(spike_time,window,vmdat[trial][1],plotdt)
            sta_list.append(sta)
            spike_set.append(spike_time)
            '''
            vmsignal=AnalogSignal(vmdat[trial][1],units='V',sampling_rate=plotdt*q.Hz)
            spikes=SpikeTrain(spike_time*q.s,t_stop=vmsignal.times[-1])
            e_sta=elephant.sta.spike_triggered_average(vmsignal,spikes,(-window*q.s,0*q.s))
            plt.plot(xvals,e_sta.magnitude,label='e_sta') 
            '''
        else:
            print('wrong spike file')
    return sta_list,xvals,plotdt,vmdat,spike_set

def input_raster(fileroot,presyn,suffix):
    pattern=fileroot+presyn+suffix
    files=file_set(pattern)
    pre_spikes=[{} for f in files]
    for trial,infile in enumerate(files):
        ######### End temp stuff
        tt=np.load(infile).item()
        for ax,syntype in enumerate(tt.keys()):
            for presyn in tt[syntype].keys():
                spiketimes=[]
                for branch in sorted(tt[syntype][presyn].keys()):
                    #axis[ax].eventplot(tt[syntype][presyn][branch])
                    spiketimes.append(tt[syntype][presyn][branch])
                #flatten the spiketime array to use for prospective STA
                pre_spikes[trial][syntype+presyn]=spiketimes
    return pre_spikes

def post_sta_set(pre_spikes,sta_start,sta_end,plotdt,vmdat):
    window=(int(sta_start/plotdt),int(sta_end/plotdt))
    post_sta={key:[] for key in pre_spikes[0]}
    for trial in range(len(pre_spikes)):
        for ax,(key,spiketimes) in enumerate(pre_spikes[trial].items()):
            spikes=flatten(spiketimes)
            xvals,sta=calc_sta(spikes,window,vmdat[trial][1],plotdt)
            post_sta[key].append(sta)
    mean_sta={}
    for ax,key in enumerate(post_sta.keys()):
        mean_sta[key]=np.mean(post_sta[key],axis=0)
    return post_sta,mean_sta,xvals

############# Call this from multisim, after import ISI_anal
#  ISI_anal.save_tt(connections)
def save_tt(connections,param_sim):
    import moose
    used_tt={}
    for syntype in connections['ep']['/ep'].keys():
        used_tt[syntype]={}
        for ext in connections['ep']['/ep'][syntype].keys():
            used_tt[syntype][ext]={}
            for syn in connections['ep']['/ep'][syntype][ext].keys():
                tt=moose.element(connections['ep']['/ep'][syntype][ext][syn])
                used_tt[syntype][ext][syn]=tt.vector
    np.save('tt'+param_sim.fname,used_tt)

