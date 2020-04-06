import numpy as np
from scipy import fftpack, signal,stats
from synth_trains import sig_filter as filt

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def file_set(pattern):
    files=sorted(glob.glob(pattern))
    if len(files)==0:
        print('********* no files found for ',pattern)
    return files

def isi_vs_time(spike_time,isi_vals,bins,binsize,isi_set):
    st_isi=dict(zip(spike_time[1:],isi_vals))
    for pre_post in bins.keys():
        for binmin in bins[pre_post]:
            binmax=binmin+binsize
            isi_set[pre_post][binmin].append([isi_val for st, isi_val in st_isi.items() if st>=binmin and st<binmax])
    return isi_set

def set_up_bins(freq,numbins,neurtype,syntt_info):
    bins={}
    stim_tt=syntt_info['syn_tt']
    simtime=syntt_info['maxt']
    bin_size=(stim_tt[-1]+1/float(freq)-stim_tt[0])/numbins
    #bins['stim']={stim_tt[0]+i*bin_size : stim_tt[0]+(i+1)*bin_size for i in range(numbins)}
    bins['stim']=[stim_tt[0]+i*bin_size for i in range(numbins)]
    num_bins=min(numbins,int(stim_tt[0]/bin_size))
    bins['pre']=sorted([bins['stim'][0]-(i+1)*bin_size for i in range(num_bins)])
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

def calc_lat_shift(lat,stimTimes,numBinsForEnt,freq):
    entropy={}
    for numBins_perStim in numBinsForEnt:
        binSize_ent=1/(freq*numBins_perStim) #units are sec
        nStim=np.sum([len(st) for st in stimTimes.values()])
        spikeMat=np.zeros((nStim,numBins_perStim))
        stim_num=0
        for jj,pre_post in enumerate(lat.keys()):
            for i,latency_set in enumerate(lat[pre_post]):
                spikeBin=[np.floor(lat/binSize_ent) for lat in latency_set]
                for binnum in range(numBins_perStim):
                    spikeMat[stim_num,binnum]=spikeBin.count(binnum)
                stim_num=stim_num+1
        p_for_entropy=np.array([sm/np.sum(sm) for sm in spikeMat])
        entropy[numBins_perStim]=[stats.entropy(ent) for ent in p_for_entropy]
    return entropy
            
def latency(files,freq,neurtype,numbins,syntt_info,numBinsForEnt=[]):
    isi=1.0/freq
    simtime=syntt_info['maxt']
    latency={'pre':np.zeros((freq,len(files))),'post':np.zeros((freq,len(files))), 'stim':np.zeros((freq,len(files)))}
    bins,bin_size,stim_tt=set_up_bins(files[0],freq,numbins,neurtype,syntt_info)
    isi_set={'pre':{k:[] for k in bins['pre']},'post':{k:[] for k in bins['post']},'stim':{k:[] for k in bins['stim']}}
    pre_post_stim=setup_stimtimes(freq,stim_tt,isi,simtime)
    for fnum,fname in enumerate(files):
        dat=np.load(fname,'r',allow_pickle=True)
        params=dat['params'].item()
        if 'spike_time' in dat.keys() and params['freq']==freq:
            spike_time=dat['spike_time'].item()[neurtype][0]
            for pre_post in pre_post_stim.keys():
                for i,time in enumerate(pre_post_stim[pre_post]):
                    next_spike=np.min(spike_time[np.where(spike_time>time)])
                    latency[pre_post][i,fnum]=(next_spike-time) if next_spike<(time+isi) else np.nan
            isi_vals=dat['isi'].item()[neurtype][0]
            isi_set=isi_vs_time(spike_time,isi_vals,bins,bin_size,isi_set)
        else:
            print('whoops, wrong file',fname,'for freq', freq,'file contains', dat.keys())
    if len(numBinsForEnt):
        entropy=calc_lat_shift(latency,pre_post_stim,numBinsForEnt,freq)
    else:
        entropy=[]
    lat_mean={}
    lat_std={}
    latency_phase={}
    for pre_post in latency.keys():
        #print('latency',np.shape(latency[pre_post]))
        latency_phase[pre_post]=[ lat % isi for lat in latency[pre_post]]
        lat_mean[pre_post]=np.nanmean(latency[pre_post],axis=1)
        lat_std[pre_post]=np.nanstd(latency[pre_post],axis=1)
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
    return lat_mean,lat_std,isi_mean,isi_std,bins,bin_size,latency_phase,entropy

def freq_dependence(fileroot,presyn,suffix):
    pattern=fileroot+presyn+'*'+suffix
    files=file_set(pattern)
    if len(files)==0:
        return
    frequency_set=np.unique([int(fname.split('freq')[-1].split('_')[0]) for fname in files])
    results={freq:{} for freq in frequency_set}
    xval_set={freq:{} for freq in frequency_set}
    for fname in files:
        dat=np.load(fname,'r',allow_pickle=True)
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
            dat=np.load(fname,'r',allow_pickle=True)
            spiketimes.append(dat['spike_time'].item()[neurtype][0])
        #Get start and end of stimulation only from last file
        #'syn_tt' has one tuple (but could have multiple), 1st item is comp, 2nd item is array of spike times
        if neurtype in dat['params'].item().keys():
            stim_tt=dat['params'].item()[neurtype]['syn_tt'][0][1]
            xstart=stim_tt[0]
            xend=stim_tt[-1]
            maxt=max([max(st) for st in spiketimes])
            if 'simtime' in dat['params']:
                maxt=dat['params']['simtime']
            syntt_info={'xstart':xstart,'xend':xend,'maxt':maxt,'stim_tt':stim_tt}
        else:
            syntt_info={}
    return spiketimes,syntt_info

def ISI_histogram(files,stim_freq,neurtype):
    #set-up pre, during and post-stimulation time frames (bins)
    bins,binsize,stim_tt,simtime=set_up_bins(files[0],stim_freq,1,neurtype)
    isi_set={'pre':[],'post':[],'stim':[]}
    #read in ISI data and separate into 3 time frames
    for fname in files:
        dat=np.load(fname,'r',allow_pickle=True)
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
        if endpt<len(vmdat) and st>0:
            startpt=endpt-samplesize
            if startpt<0:
                sta_start=-startpt
                startpt=0
            else:
                sta_start=0
            #print('line 228',numspikes,samplesize,np.round(st,4),sta_start,startpt,endpt)
            sta_array[i,sta_start:]=vmdat[startpt:endpt]
    sta=np.mean(sta_array,axis=0)
    xvals=np.arange(window[0]*plotdt,window[1]*plotdt,plotdt)
    return xvals,sta

def sta_set(files,spike_time,neurtype,sta_start,sta_end):
    vmdat=[]
    sta_list=[]
    for trial,fname in enumerate(files):
        dat=np.load(fname,'r',allow_pickle=True)
        params=dat['params'].item()
        plotdt=params['dt']
        window=(int(sta_start/plotdt),int(sta_end/plotdt))
        if 'vm' in dat.keys():
            vmdat.append(dat['vm'].item()[neurtype])
            #if (dat['vm'] has multiple traces, choose the last one
            trace=np.shape(vmdat)[1]-1
            xvals,sta=calc_sta(spike_time[trial],window,vmdat[trial][trace],plotdt)
            sta_list.append(sta)
        else:
            print('wrong spike file')
    #calculate mean over trials
    return sta_list,xvals,plotdt,vmdat

def input_raster(files):
    pre_spikes=[{} for f in files]
    for trial,infile in enumerate(files):
        ######### End temp stuff
        tt=np.load(infile,allow_pickle=True).item()
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

#Need to move these spike_freq calulations into function that is called once per condition
def output_fire_freq(spiketime_dict,isi_binsize,isibins,max_time):
    import elephant
    from neo.core import AnalogSignal,SpikeTrain
    import quantities as q
    ratebins=np.arange(0,np.ceil(max_time),isi_binsize)
    #spike_rate: across entire time
    spike_rate={key:np.zeros((len(spike_set),len(ratebins))) for key,spike_set in spiketime_dict.items()}
    spike_rate_vs_time_mean={};spike_rate_vs_time_std={}
    #spike_freq: segmented into pre,stim,post
    spike_freq={key:{} for key in spiketime_dict.keys()}
    spike_freq_mean={key:{} for key in spiketime_dict.keys()}
    spike_freq_std={key:{} for key in spiketime_dict.keys()}
    for key,spike_set in spiketime_dict.items(): #iterate over different stimulation conditions
        for i in range(len(spike_set)): #iterate over trials
            train=SpikeTrain(spike_set[i]*q.s,t_stop=np.ceil(max_time)*q.s)
            spike_rate[key][i]=elephant.statistics.instantaneous_rate(train,isi_binsize*q.s).magnitude[:,0]#/len(spike_set)
    for key,rate_set in spike_rate.items(): #separate out the spike_rate into pre, post, and stimulation time frames
        for pre_post,binlist in isibins.items():
            binmin_idx=np.abs(ratebins-binlist[0]).argmin()
            binmax_idx=np.abs(ratebins-(binlist[-1]+isi_binsize)).argmin()
            spike_freq[key][pre_post]=spike_rate[key][:,binmin_idx:binmax_idx]
        spike_rate_vs_time_mean[key]=np.mean(spike_rate[key],axis=0) #average across trials
        spike_rate_vs_time_std[key]=np.std(spike_rate[key],axis=0) #std across trials
        for pre_post,binlist in isibins.items():
            spike_freq_mean[key][pre_post]=np.mean(spike_freq[key][pre_post],axis=0)
            spike_freq_std[key][pre_post]=np.std(spike_freq[key][pre_post],axis=0)
    return spike_freq_mean,spike_freq_std,spike_rate_vs_time_mean,spike_rate_vs_time_std,ratebins

def fft_func(wave_array,ts,init_time=0,endtime=np.inf):
    fft_wave=[]; phase=[]; fft_env=[]
    init_point=np.min(np.where(ts>init_time))
    endpoint=np.max(np.where(ts<endtime))
    for wave in wave_array:
        #wave is an analog signal - either Vm or binary spike signal.  Do not use spiketime
        data=wave[0][init_point:endpoint]
        fft_wave.append(np.fft.rfft(data))
        phase.append(np.arctan2(fft_wave[-1].imag,fft_wave[-1].real))
        meandata=np.mean(data)
        norm_data=np.abs(data-meandata)
        fft_env.append(np.fft.rfft(norm_data))
        cutoff=3
        fft_lowpas=filt.butter_lowpass_filter(fft_env[-1], cutoff, 1/ts[1], order=6)
        #fft_filt.append(fft_lowpass)
    #Note that maximum frequency for fft is fs/2; the frequency unit is cycles/time units.
    #freqs is x axis. Two ways to obtain correct frequencies:
    #specify sampling spacing as 2nd parameter to rfftfreq, note that fs=1/ts
    #     freqs = np.fft.fftfreq(len(wave))*fs
    #multiply sample spacing by max frequency (=1/ts):
    freqs=np.fft.rfftfreq(len(wave[0][init_point:endpoint]),ts[1])
    mean_wave=np.mean(wave_array,axis=0)[0]
    mean_fft=np.fft.rfft(mean_wave[init_point:endpoint])
    mean_phase=np.arctan2(mean_fft.imag,mean_fft.real)
    return fft_wave,phase,freqs,{'mag':mean_fft,'phase':mean_phase},fft_env

