import numpy as np
from scipy import fftpack, signal,stats
from net_anal_utils import calc_mean_std, flatten
#from synth_trains import sig_filter as filt  - look into this if want to use butterworth filer
#
class network_fileset(): #set of files, same condition, different trials
    def __init__(self,fileset,neurtypes):
        self.fileset=fileset
        self.spiketimes={neur:[] for neur in neurtypes}
        self.spikerate={neur:[] for neur in neurtypes}
        self.spikerate_elph={neur:[] for neur in neurtypes}
        self.vmdat={neur:[] for neur in neurtypes}
        self.sta={neur:[] for neur in neurtypes}
        self.timebins={};self.ratebins={}
        self.sim_time={}
        self.pre_post_stim={}
        self.num_neurs={}
        self.freq={}
        self.accum_list=[]
        self.accum_names=[]

    def st_arrays(self,data):
        for neur in data.neurtypes:
            self.spiketimes[neur].append(data.spiketime_dict[neur])
            self.spikerate[neur].append(data.spike_rate[neur])
            self.spikerate_elph[neur].append(data.spike_rate_mean[neur])
            if neur in data.vmdat.keys():
                self.vmdat[neur].append(data.vmdat[neur])
            if len(data.vmdat):
                self.time=data.time
                self.dt=data.dt
            self.timebins[neur]=data.timebins[neur]
            self.ratebins[neur]=sorted([binpair for binset in self.timebins[neur].values() for binpair in binset])
            if len(data.syntt_info):
                if neur in data.syntt_info.keys():
                    self.pre_post_stim[neur]=data.pre_post_stim[neur]
            self.freq[neur]=data.freq[neur]
            self.sim_time[neur]=data.sim_time
            if neur in self.num_neurs:
                self.num_neurs[neur]+=data.num_neurs[neur]
            else:
                self.num_neurs[neur]=data.num_neurs[neur]

    def spikerate_mean(self):
        self.spikerate_mean={};self.spikerate_elphmean={}
        self.spikerate_std={};self.spikerate_elphstd={}
        for ntype in self.num_neurs.keys():
            self.spikerate_mean[ntype],self.spikerate_std[ntype]=calc_mean_std(self.spikerate[ntype],axisnum=0)
            self.spikerate_elphmean[ntype],self.spikerate_elphstd[ntype]=calc_mean_std(self.spikerate_elph[ntype],axisnum=0)
        accum_list=[self.spikerate_mean,self.spikerate_std,self.spikerate_elphmean,self.spikerate_elphstd]
        accum_names=['spikerate_mean','spikerate_std','spikerate_elphmean','spikerate_elphstd']
        self.add_to_accum(accum_list,accum_names)
    
    def add_to_accum(self,accum_list,accum_names):
        for al,an in zip(accum_list,accum_names):
            self.accum_list.append(al)
            self.accum_names.append(an)
    
    def sta_array(self,data):
        for neur in data.sta.keys():
            self.sta[neur].append(data.sta[neur])
    
    def sta_mean(self):
        self.sta_mean={};self.sta_std={}
        for ntype in self.sta.keys():
            self.sta_mean[ntype],self.sta_std[ntype]=calc_mean_std(self.sta[ntype],axisnum=0)
        self.add_to_accum([self.sta_mean,self.sta_std],['sta_mean','sta_std'])
        
    def ISI_histogram(self,numbins):
        self.isi_epoch={neur:{epoch:[[] for f in self.fileset] for epoch in self.timebins[neur].keys()} for neur in self.num_neurs.keys()}
        self.isi_hist={neur:{epoch:[] for epoch in self.timebins[neur].keys()} for neur in self.num_neurs.keys()}
        self.isi_hist_mean={neur:{} for neur in self.num_neurs.keys()}
        self.isi_hist_std={neur:{} for neur in self.num_neurs.keys()}
        self.isihist_bins={neur:{} for neur in self.num_neurs.keys()}
        for neur in self.spiketimes.keys():
            for fil,spike_set in enumerate(self.spiketimes[neur]): #loop over files  
                for neur_spikes in spike_set: #loop over neurons in file 
                    for pre_post,binlist in self.timebins[neur].items():
                        bmin=binlist[0][0]
                        bmax=binlist[-1][1]
                        self.isi_epoch[neur][pre_post][fil].append([neur_spikes[i+1]-st for i,st in enumerate(neur_spikes[0:-1]) if st>=bmin and st<bmax])
        for neur in self.isi_epoch.keys():
            mins=[np.min(flatten(isis)) for isiset in self.isi_epoch[neur].values() for isis in isiset] 
            maxs=[np.max(flatten(isis)) for isiset in self.isi_epoch[neur].values() for isis in isiset]
            min_max=[np.min(mins),np.max(maxs)]
            #histbins=10 ** np.linspace(np.log10(min_max[0]), np.log10(min_max[1]), numbins)
            histbins=np.linspace(min_max[0],min_max[1], numbins)
            for pre_post,ISIs in self.isi_epoch[neur].items():
                for isis in ISIs:
                    hist,tmp=np.histogram(flatten(isis),bins=histbins,range=min_max)
                    self.isi_hist[neur][pre_post].append(hist)
                #average over fileset.  Probably do not need to save isi_epoch or isi_hist
                self.isi_hist_mean[neur][pre_post],self.isi_hist_std[neur][pre_post]=calc_mean_std(self.isi_hist[neur][pre_post],axisnum=0)
                self.isihist_bins[neur][pre_post]=[(histbins[i]+histbins[i+1])/2 for i in range(len(histbins)-1)] 
        self.add_to_accum([self.isi_hist_mean,self.isi_hist_std],['isihist_mean','isihist_std'])

    def ISI_vs_time(self,neurtype):       #isi vs time for stimulated neuron only
        self.isi_time_epoch={epoch:{k[0]:[] for k in self.timebins[neurtype][epoch]} for epoch in self.timebins[neurtype].keys()}
        for spike_set in self.spiketimes[neurtype]: #loop over files
            for neur_spikes in spike_set: #loop over neurons in file
                for pre_post,binlist in self.timebins[neurtype].items():
                    for bmin,bmax in binlist:
                        self.isi_time_epoch[pre_post][bmin].append([neur_spikes[i+1]-st for i,st in enumerate(neur_spikes[0:-1]) if st>=bmin and st<bmax])
        
    def latency(self,neurtype):
        self.latency={epoch:np.zeros((len(self.pre_post_stim[neurtype][epoch]),len(self.spiketimes[neurtype]))) for epoch in self.pre_post_stim[neurtype].keys()}
        for setnum,spikeset in enumerate(self.spiketimes[neurtype]): #loop over files
            for pre_post in self.pre_post_stim[neurtype].keys(): 
                isi=self.pre_post_stim[neurtype][pre_post][1]-self.pre_post_stim[neurtype][pre_post][0]
                for i,time in enumerate(self.pre_post_stim[neurtype][pre_post]):
                    next_spike=[]
                    for neurspikes in spikeset:#could be more than one neuron of each neurtype
                        ns=np.min(neurspikes[np.where(neurspikes>time)])
                        next_spike.append((ns-time) if ns<(time+isi) else np.nan)
                    if np.all(np.isnan(next_spike)):
                        self.latency[pre_post][i,setnum]=np.nan
                    else:
                        self.latency[pre_post][i,setnum]=np.nanmean(next_spike)

    def lat_isi_mean(self):
        self.lat_mean={}
        self.lat_std={}
        for pre_post in self.latency.keys():
            self.lat_mean[pre_post], self.lat_std[pre_post]=calc_mean_std(self.latency[pre_post],axisnum=1)
        self.isi_time_mean={}
        self.isi_time_std={}
        for pre_post in self.isi_time_epoch.keys():
            for binmin,isilist in self.isi_time_epoch[pre_post].items():
                self.isi_time_epoch[pre_post][binmin]=[np.mean(ix) for ix in isilist]
            self.isi_time_mean[pre_post]=[np.nanmean(self.isi_time_epoch[pre_post][bm]) for bm in self.isi_time_epoch[pre_post].keys()]
            self.isi_time_std[pre_post]=[np.nanstd(self.isi_time_epoch[pre_post][bm]) for bm in self.isi_time_epoch[pre_post].keys()]
            #print('isi {}: mean {} \n std {}'.format(pre_post,isi_time_mean[pre_post],isi_time_std[pre_post]))
        accum_list=[self.lat_mean,self.lat_std,self.isi_time_mean,self.isi_time_std]
        accum_names=['lat_mean','lat_std','isi_time_mean','isi_time_std']
        self.add_to_accum(accum_list,accum_names)
    
    def calc_lat_shift(self,neur,entropy_bin_size):
        if entropy_bin_size>0:
            numBinsForEnt=[int((1./self.freq[neur])/entropy_bin_size)]
        else:
            numBinsForEnt=[]
        self.entropy={}
        for numBins_perStim in numBinsForEnt:
            binSize_ent=1/(self.freq[neur]*numBins_perStim) #units are sec
            nStim=np.sum([len(st) for st in self.pre_post_stim[neur].values()])
            spikeMat=np.zeros((nStim,numBins_perStim))
            for jj,pre_post in enumerate(self.latency.keys()):
                for i,latency_set in enumerate(self.latency[pre_post]):
                    stim_num=i+jj*len(self.latency[pre_post])
                    spikeBin=[np.floor(lat/binSize_ent) for lat in latency_set]
                    for binnum in range(numBins_perStim):
                        spikeMat[stim_num,binnum]=spikeBin.count(binnum)
            p_for_entropy=np.array([sm/np.sum(sm) for sm in spikeMat])
            self.entropy[numBins_perStim]=[stats.entropy(ent) for ent in p_for_entropy]
            self.add_to_accum([self.entropy],['entropy'])
    
    def fft_func(self,ntype,init_time=0,endtime=0,maxfreq=None):
        #extend, to allow specification of spike_rate instead of using vmdat for fft
        #MODIFY - what if there are multiple neurons per neuron type??  Possibly need a third loop (but not always)
        #init_time - if you want to calculate fft after some initial period
        #endtime - if you want to stop fft calculation, in case end departs from ergodicity
        #these will also allow you to avoid transition periods
        self.fft_wave={k:[] for k in self.timebins[ntype].keys()}
        self.fft_env={k:[] for k in self.timebins[ntype].keys()}
        self.fft_of_mean={}
        for epoch,bins in self.timebins[ntype].items(): #bins are in pairs of low value and high value
            init_point=int((bins[0][1]+init_time)/self.dt) #in case of bin overlap, use upper value of bin to start 
            endpoint=int((bins[-1][0]+endtime)/self.dt) #
            for wave in self.vmdat[ntype]: #waveset is set of VM traces or spikefrequency for single neurontype
                data=wave[init_point:endpoint]
                self.freqs=np.fft.rfftfreq(len(data),self.dt)
                if maxfreq is not None:
                    maxpoint=np.min(np.where(self.freqs>maxfreq))
                    self.freqs=self.freqs[0:maxpoint]
                else:
                    maxpoint=None
               #wave is an analog signal - either Vm or binary spike signal.  Do not use spiketime
                self.fft_wave[epoch].append(np.fft.rfft(data)[0:maxpoint])
                norm_data=np.abs(data-np.mean(data))
                self.fft_env[epoch].append(np.fft.rfft(norm_data)[0:maxpoint])
                cutoff=3
                #fft_lowpas=filt.butter_lowpass_filter(self.fft_env[-1], cutoff, 1/self.dt, order=6)
                #self.fft_filt.append(fft_lowpass)
            #Note that maximum frequency for fft is fs/2; the frequency unit is cycles/time units.
            #freqs is x axis. Two ways to obtain correct frequencies:
            #specify sampling spacing as 2nd parameter to rfftfreq, note that fs=1/dt
            #     freqs = np.fft.fftfreq(len(wave))*fs
            #multiply sample spacing by max frequency (=1/dt):
            mean_wave=np.mean(self.vmdat[ntype],axis=0)
            self.fft_of_mean[epoch]=np.fft.rfft(mean_wave[init_point:endpoint])[0:maxpoint]
        self.mean_fft={epoch:np.mean(np.abs([ft**2 for ft in fft]),axis=0) for epoch,fft in self.fft_wave.items()} #PSD
        self.std_fft={epoch:np.std(np.abs([ft**2 for ft in fft]),axis=0) for epoch,fft in self.fft_wave.items()}
        self.add_to_accum([self.mean_fft,self.std_fft],['mean_fft','std_fft'])
