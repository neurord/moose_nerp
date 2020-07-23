import numpy as np
from scipy import fftpack, signal,stats
#from synth_trains import sig_filter as filt  - look into this if want to use butterworth filer
#
def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def calc_one_sta(spiketrain,window,vm_or_spikerate,dt):
    samplesize=window[-1]-window[0]
    numspikes=len(spiketrain)
    sta_array=np.zeros((numspikes,samplesize))
    for i,st in enumerate(spiketrain):
        endpt=int(st/dt)+window[1]
        if endpt<len(vm_or_spikerate) and st>0:
            startpt=endpt-samplesize
            if startpt<0:
                sta_start=-startpt
                startpt=0
            else:
                sta_start=0
            sta_array[i,sta_start:]=vm_or_spikerate[startpt:endpt]
    return np.mean(sta_array,axis=0)

class network_output():
    def __init__(self,fname,numbins,overlap,table_index=None):
        dat=np.load(fname,'r',allow_pickle=True)
        self.fname=fname
        self.spiketime_dict=dat['spike_time'].item()
        self.isis=dat['isi'].item()
        self.sim_time=dat['params'].item()['simtime']
        self.num_neurs={k:len(st) for k,st in self.spiketime_dict.items()}
        self.neurtypes=self.spiketime_dict.keys()
        self.syntt_info={}
        self.freq={}
        self.timebins={k:{} for k in self.neurtypes}
        self.binsize={}
        self.pre_post_stim={}
        self.vmdat={}
        if 'vm' in dat.keys():
            vmtabs=dat['vm'].item()
            for neur in self.neurtypes:
                if table_index:
                    self.vmdat[neur]=vmtabs[neur][table_index]
                else:
                    self.vmdat[neur]=vmtabs[neur][0] #KLUGE - just do the first neuron.  If remove [0], need to edit fft_func
            if 'dt' in dat['params'].item():
                self.dt=dat['params'].item()['dt']
            else:
                self.dt=self.sim_time/len(vmtabs[neur][0])
            #arbitrarily use 1st table of last neur to construct time wave
            self.time=np.linspace(0,self.dt*len(vmtabs[neur][0]),len(vmtabs[neur][0]),endpoint=False)
            self.sim_time=max(self.time[-1],self.sim_time)
            
        for neur in self.neurtypes:
            if 'syn_tt' in dat['params'].item().keys():
                ############### Preferred, but new way, of storing regular time-table data for ep simulations #######
                stim_tt=dat['params'].item()['syn_tt'][neur][0][1] #take stim times from 1st item in list, could be multiple branches stimulated
            elif neur in dat['params'].item().keys():
                if 'syn_tt' in dat['params'].item()[neur].keys():
                    #OLD WAY of storing time-table data for ep simulations - use this for simulations prior to may 20
                    stim_tt=dat['params'].item()[neur]['syn_tt'][0][1] #take stim times from 1st item in list
            if 'stim_tt' in locals():
                xstart=stim_tt[0]
                xend=stim_tt[-1]
                self.syntt_info[neur]={'xstart':xstart,'xend':xend,'stim_tt':stim_tt}
                self.timebins[neur],self.freq[neur],self.binsize[neur]=self.set_up_bins(numbins,stim_tt)
                isi=stim_tt[1]-stim_tt[0]
                self.pre_post_stim[neur]=self.setup_stim_epochs(isi,stim_tt,self.sim_time)
            else:
                self.freq[neur]=0
                self.binsize[neur]=self.sim_time/numbins
                nbins=int(self.sim_time/self.binsize[neur]/overlap-(1./overlap-1))
                binlow=[i*self.binsize[neur]*overlap for i in range(nbins)]
                self.timebins[neur]['all']=[(bl,bl+self.binsize[neur]) for bl in binlow]

    #
    def set_up_bins(self,numbins,stim_tt):
        bins={}
        freq=float(1/(stim_tt[1]-stim_tt[0]))
        bin_size=(stim_tt[-1]+1/freq-stim_tt[0])/numbins
        binlow=sorted([stim_tt[0]+i*bin_size for i in range(numbins)])
        bins['stim']=[(bl,bl+bin_size) for bl in binlow]
        #
        num_bins=min(numbins,int(stim_tt[0]/bin_size))
        binlow=sorted([bins['stim'][0][0]-(i+1)*bin_size for i in range(num_bins)])
        bins['pre']=[(bl,bl+bin_size) for bl in binlow]
        #
        num_bins=min(numbins,int((self.sim_time-stim_tt[-1])*freq))
        binlow=sorted([bins['stim'][-1][0]+(i+1)*bin_size for i in range(num_bins)])
        bins['post']=[(bl,bl+bin_size) for bl in binlow]
        return bins,freq,bin_size
    #
    def setup_stim_epochs(self,isi,stim_tt,simtime):
        pre_post_stim={}
        pre_post_stim['stim']=stim_tt
        num_pre=int(stim_tt[0]/isi)
        pre_post_stim['pre']=sorted([stim_tt[0]-(i+1)*isi for i in range(min(num_pre-1,len(stim_tt)))])
        num_post=int((simtime-stim_tt[-1])/isi)
        pre_post_stim['post']=sorted([stim_tt[-1]+(i+1)*isi for i in range(min(num_post-1,len(stim_tt)))])
        return pre_post_stim
    #
    def spikerate_func(self):
        import elephant as elph
        from neo.core import AnalogSignal,SpikeTrain
        import quantities as q
        self.spike_rate={};self.spike_rate_elph={};self.spike_rate_mean={}
        for ntype in self.neurtypes:
            ratebins=sorted([binpair for binset in self.timebins[ntype].values() for binpair in binset])
            binsize=self.binsize[ntype]
            self.spike_rate_elph[ntype]=np.zeros((len(self.spiketime_dict[ntype]),int(self.sim_time/binsize)))
            self.spike_rate[ntype]=np.zeros(len(ratebins))
            numneurs=self.num_neurs[ntype]
            for i,spiketrain in enumerate(self.spiketime_dict[ntype]):
                train=SpikeTrain(spiketrain*q.s,t_stop=self.sim_time*q.s)
                #NOTE, instantaneous_rate fails with kernel=auto and small number of spikes
                kernel=elph.kernels.GaussianKernel(sigma=binsize*q.s)
                self.spike_rate_elph[ntype][i,:]=elph.statistics.instantaneous_rate(train,binsize*q.s,kernel=kernel).magnitude[:,0]
            self.spike_rate_mean[ntype]=np.mean(self.spike_rate_elph[ntype],axis=0)
            #Compare spike_rate_mean (from elephant) with spike_rate 
            for bb,(bl,bh) in enumerate(ratebins):
                self.spike_rate[ntype][bb]=len([st for st in  flatten(self.spiketime_dict[ntype])
                                                if st>=bl and st<bh])/binsize/self.num_neurs[ntype]
        #separate into pre,post,stim epochs?  Or separate function - only do that if stim
    
    def calc_sta(self,sta_start,sta_end):
        self.sta={}
        window=(int(sta_start/self.dt),int(sta_end/self.dt))
        for ntype in self.vmdat.keys():
            sta_set=[]
            for i,spiketrain in enumerate(self.spiketime_dict[ntype]):
                sta_set.append(calc_one_sta(spiketrain,window,self.vmdat[ntype],self.dt)) #mean over spikes
            self.sta[ntype]=np.mean(sta_set,axis=0) #mean over neurons
        self.sta_xvals=np.arange(sta_start,sta_end,self.dt)
        #net_anal:calculate mean and std over trials
