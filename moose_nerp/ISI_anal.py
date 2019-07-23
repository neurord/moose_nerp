#Functions for calculating ISI, latency, psp_amplitude for a set of files
import glob
import numpy as np
import moose
from scipy import fftpack, signal

import detect

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def file_set(pattern):
    files=sorted(glob.glob(pattern))
    if len(files)==0:
        print('********* no files found for ',pattern)
    return files

def find_somatabs(tabset,soma_name,tt=None):
    #find the table(s) with vm from the soma
    comp_names=[tab.neighbors['requestOut'][0].name for tab in tabset]
    soma_tabs=[tab for tab in tabset if tab.neighbors['requestOut'][0].name==soma_name]
    print ('ISI_ANAL: vm tables {}, soma vmtab={}, comp={}'.format(comp_names,soma_tabs,[st.neighbors['requestOut'][0].path for st in soma_tabs]))
    #if no soma tables found (perhaps wrong name) use the last one, which might be soma
    #or send back number of tables equal to number of time tables 
    ######## Needs more debugging for network simulation #################3
    if len(soma_tabs)==0:
        if tt:
            num_tabs=len(tt)
        else:
            num_tabs=1
        soma_tabs=comp_names[-num_tabs:]
    return soma_tabs
    
def spike_isi_from_vm(vmtab,simtime,soma='soma'):
    spike_time={key:[] for key in vmtab.keys()}
    numspikes={key:[] for key in vmtab.keys()}
    isis={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        soma_tabs=find_somatabs(tabset,soma)
        for tab in soma_tabs:
            spike_time[neurtype].append(detect.detect_peaks(tab.vector)*tab.dt)
            isis[neurtype].append(np.diff(spike_time[neurtype][-1]))
            numspikes[neurtype]=[len(st) for st in spike_time[neurtype]]
        print(neurtype,'mean:',np.mean(numspikes[neurtype]),'rate',np.mean(numspikes[neurtype])/simtime,'from',numspikes[neurtype],
              'spikes, ISI mean&STD: ',[np.mean(isi) for isi in isis[neurtype]], [np.std(isi) for isi in isis[neurtype]] )
    return spike_time,isis

def stim_spikes(spike_time,timetables,soma='soma'):
    stim_spikes={key:[] for key in spike_time.keys()}
    for neurtype, tabset in spike_time.items():
        for tab,tt in zip(tabset,timetables[neurtype].values()):
            stim_spikes[neurtype].append([st for st in spike_time[neurtype][-1] if st>np.min(tt.vector) and st<np.max(tt.vector)])
    return stim_spikes

def psp_amp(vmtab,timetables,soma='soma'):
    psp_amp={key:[] for key in vmtab.keys()}
    psp_norm={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        soma_tabs=find_somatabs(tabset,soma,tt=timetables[neurtype].values())
        for tab,tt in zip(soma_tabs,timetables[neurtype].values()):
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
        #'syn_tt' has one tuple (but could have multiple), 
        #1st [0] selects the 1st tuple
        #2nd [1] selects stim_times (array of spike times) from tuple (synapse,stim_times), 
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

def latency(files,freq,neurtype,numbins):
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
            print ('freq dep fname', fname, dat.keys())
            numplots=len(dat['norm'].item().keys())
            results[params['freq']]={ntype:[] for ntype in dat['norm'].item().keys()}
            for neurtype in dat['norm'].item().keys():
                results[params['freq']][neurtype]=dat['norm'].item()[neurtype]
                #'syn_tt' has one tuple (but could have multiple), 
                #1st [0] selects the 1st tuple
                #2nd [1] selects stim_times (array of spike times) from tuple (synapse,stim_times), 
                xval_set[params['freq']][neurtype]=dat['params'].item()['ep']['syn_tt'][0][1]
            ylabel='normalized PSP amp'
            xlabel='pulse'
        elif 'isi' in dat.keys():
            print ('freq dep fname', fname, dat.keys())
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

def get_spiketimes(files,neurtype):
    spiketimes=[]
    #creates list of spike times from set of trials
    if len(files)>0:
        for fname in files:
            dat=np.load(fname,'r')
            spiketimes.append(dat['spike_time'].item()[neurtype][0])
        #Get start and end of stimulation only from last file
        #'syn_tt' has one tuple (but could have multiple), 1st item is comp, 2nd item is array of spike times
        if neurtype in dat['params'].item().keys():
            xstart=dat['params'].item()[neurtype]['syn_tt'][0][1][0]
            xend=dat['params'].item()[neurtype]['syn_tt'][0][1][-1]
            maxt=max([max(st) for st in spiketimes])
            syntt_info={'xstart':xstart,'xend':xend,'maxt':maxt}
        else:
            syntt_info={}
    return spiketimes,syntt_info

def ISI_histogram(files,stim_freq,neurtype):
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

def sta_set(files,spike_time,neurtype,sta_start,sta_end):
    vmdat=[]
    sta_list=[]
    for trial,fname in enumerate(files):
        dat=np.load(fname,'r')
        params=dat['params'].item()
        plotdt=params['dt']
        window=(int(sta_start/plotdt),int(sta_end/plotdt))
        if 'vm' in dat.keys():
            vmdat.append(dat['vm'].item()[neurtype])
            #if (dat['vm'] has multiple traces, choose the last one
            trace=np.shape(vmdat)[1]-1
            xvals,sta=calc_sta(spike_time[trial],window,vmdat[trial][trace],plotdt)
            sta_list.append(sta)
            '''
            vmsignal=AnalogSignal(vmdat[trial][1],units='V',sampling_rate=plotdt*q.Hz)
            spikes=SpikeTrain(spike_time*q.s,t_stop=vmsignal.times[-1])
            e_sta=elephant.sta.spike_triggered_average(vmsignal,spikes,(-window*q.s,0*q.s))
            plt.plot(xvals,e_sta.magnitude,label='e_sta') 
            '''
        else:
            print('wrong spike file')
    #calculate mean over trials
    return sta_list,xvals,plotdt,vmdat

def input_raster(files):
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
            trace=np.shape(vmdat)[1]-1
            xvals,sta=calc_sta(spikes,window,vmdat[trial][trace],plotdt)
            post_sta[key].append(sta)
    mean_sta={}
    for ax,key in enumerate(post_sta.keys()):
        mean_sta[key]=np.mean(post_sta[key],axis=0)
    return post_sta,mean_sta,xvals

def sta_fire_freq(inst_rate,spike_list,sta_start,sta_end,weights,xbins):
    binsize=xbins[1]-xbins[0]
    window=(int(sta_start/binsize),int(sta_end/binsize))
    weighted_inst_rate=[np.zeros(len(xbins)) for trial in range(len(inst_rate))] 
    prespike_sta=[{} for t in range(len(inst_rate))]
    for trial in range(len(inst_rate)):
        spike_time=spike_list[trial]
        for key in inst_rate[trial].keys():
            weighted_inst_rate[trial]+=weights[key]*inst_rate[trial][key] 
            xbins,prespike_sta[trial][key]=calc_sta(spike_time,window,inst_rate[trial][key],binsize)
        xbins,prespike_sta[trial]['sum']=calc_sta(spike_time,window,weighted_inst_rate[trial],binsize)
    mean_sta={k:np.zeros(len(prespike_sta[0][k])) for k in prespike_sta[0]}
    for ax,key in enumerate(prespike_sta[0].keys()):
        for trial in range(len(prespike_sta)):
            mean_sta[key]+=prespike_sta[trial][key]
        mean_sta[key]=mean_sta[key]/len(prespike_sta)
    return prespike_sta,mean_sta,xbins

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

def fft_func(wave_array,ts,init_time,endtime):
    fft_wave=[]
    phase=[]
    init_point=np.min(np.where(ts>init_time))
    endpoint=np.max(np.where(ts<endtime))
    for wave in wave_array:
        #wave is an analog signal - either Vm or binary spike signal.  Do not use spiketime
        fft_wave.append(np.fft.rfft(wave[0][init_point:endpoint]))
        #Note that maximum frequency for fft is fs/2; the frequency unit is cycles/time units.
        #freqs is x axis. Two ways to obtain correct frequencies:
        #specify sampling spacing as 2nd parameter, note that fs=1/ts
        #freqs = np.fft.fftfreq(len(wave))*fs
        #multiply by sample spacing by max frequency (=1/ts):
        phase.append(np.arctan2(fft_wave[-1].imag,fft_wave[-1].real))
    freqs=np.fft.rfftfreq(len(wave[0][init_point:endpoint]),ts[1])
    mean_wave=np.mean(wave_array,axis=0)[0]
    mean_fft=np.fft.rfft(mean_wave[init_point:endpoint])
    mean_phase=np.arctan2(mean_fft.imag,mean_fft.real)
    return fft_wave,phase,freqs,mean_wave,{'mag':mean_fft,'phase':mean_phase}

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

