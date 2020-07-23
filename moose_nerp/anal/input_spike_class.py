import numpy as np
from net_anal_utils import calc_mean_std

class input_spikes():
    def __init__(self,files,maxtime):
        self.files=files
        self.spiketimes=[{} for f in files]
        self.maxtime=maxtime
        for trial,infile in enumerate(files):
            tt=np.load(infile,allow_pickle=True).item()
            for ax,syntype in enumerate(tt.keys()): #ampa vs gaba
                for presyn in tt[syntype].keys(): #extern2, extern3, etc
                    spiketimes=[]
                    for branch in sorted(tt[syntype][presyn].keys()):
                        spiketimes.append(tt[syntype][presyn][branch])
                        #flatten the spiketime array to use for prospective STA
                    self.spiketimes[trial][syntype+presyn]=spiketimes
        #THIS AND THE NEXT FUNCTION ASSUME ONLY A SINGLE NEURON - NEED TO FIX WITH NETWORK SIMULATIONS

    def input_fire_freq(self,ntype,binsize,elphYN=False):
        import elephant
        from neo.core import AnalogSignal,SpikeTrain
        import quantities as q
        self.inst_rate_elph={syn:[] for syn in self.spiketimes[0].keys()}
        self.inst_rate={syn:[] for syn in self.spiketimes[0].keys()}
        for trial in range(len(self.spiketimes)):
            print('input firing rate for trial',trial,'inst rate using elephant:',elphYN)
            for syn,spike_set in self.spiketimes[trial].items():
                if isinstance(spike_set, list):
                    spikes = np.sort(np.concatenate([st for st in spike_set])) #1D array, spikes of all input synapses
                else:
                    spikes=spike_set
                if elphYN==True:
                    train=SpikeTrain(spikes*q.s,t_stop=np.ceil(spikes[-1])*q.s)
                    self.inst_rate_elph[syn].append(elephant.statistics.instantaneous_rate(train,binsize*q.s).magnitude[:,0])
                self.xbins=np.arange(0,self.maxtime[ntype],binsize)
                self.inst_rate[syn].append(np.zeros(len(self.xbins)))
                for i,binmin in enumerate(self.xbins):
                    self.inst_rate[syn][trial][i]=len(set(np.where(spikes<(binmin+binsize))[0]) &  set(np.where(spikes>binmin)[0]))/binsize #118.49s
                    #self.inst_rate[syn][trial][i]=len([st for st in spikes if st>=binmin and st<binmin+binsize])/binsize #196.73s
        self.inputrate_mean={};self.inputrate_elphmean={}
        self.inputrate_std={};self.inputrate_elphstd={}
        for syn in self.inst_rate.keys():
            self.inputrate_mean[syn],self.inputrate_std[syn]=calc_mean_std(self.inst_rate[syn],axisnum=0)
            if elphYN==True:
                self.inputrate_elphmean[syn],self.inputrate_elphstd[syn]=calc_mean_std(self.inst_rate_elph[syn],axisnum=0)
        if elphYN==True:
            self.accum_list=[self.inputrate_elphmean,self.inputrate_elphstd,self.inputrate_mean,self.inputrate_std]
            self.accum_names=['inputrate_elphmean','inputrate_elphstd','inputrate_mean','inputrate_std']
        else:
            self.accum_list=[self.inputrate_mean,self.inputrate_std]
            self.accum_names=['inputrate_mean','inputrate_std']

           
