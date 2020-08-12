import numpy as np
mM_to_uM=1000

class neur_npz():
    def __init__(self,fname,table_index=None):
        dat=np.load(fname,'r',allow_pickle=True)
        self.fname=fname
        if 'spike_time' in dat.keys():
            self.isis={neur:st[0][0:-1] for neur,st in dat['isi'].item().items()}
            #try:
            #    self.spiketime={neur:st[0][0:-1] for neur,st in dat['spike_time'].items()}
            #except
            self.spiketime={neur:st[0][0:-1] for neur,st in dat['spike_time'].item().items()}
        else:
            print('no spike times or isi in', fname)
            self.isis={}
            self.spiketime={neur:[] for neur in dat['vm'].item()}
        self.traces=dat['vm'].item()
        self.neurtypes=list(self.traces.keys())
        if table_index:
            self.somatab=table_index
        else:
            self.somatab=0
        self.sim_time=dat['params'].item()['simtime']
        self.syntt_info={}
        self.freq=dat['params'].item()['freq']
        self.inj=dat['params'].item()['inj']
        neur=self.neurtypes[0]
        if 'dt' in dat['params'].item():
            self.dt=dat['params'].item()['dt']
        else:
            self.dt=self.sim_time/len(self.traces[neur][0])
        self.time=np.linspace(0,self.dt*len(self.traces[neur][0]),len(self.traces[neur][0]),endpoint=False)
        for neur in self.neurtypes:
            if 'syn_tt' in dat['params'].item().keys():
                print('syn_tt info',dat['params'].item()['syn_tt'])
                ############### Preferred, but new way, of storing regular time-table data for ep simulations #######
                stim_tt=dat['params'].item()['syn_tt'][neur][0][1] #take stim times from 1st item in list, could be multiple branches stimulated
                stim_loc=[stim[0] for stim in dat['params'].item()['syn_tt'][neur]]
            elif neur in dat['params'].item().keys():
                if 'syn_tt' in dat['params'].item()[neur].keys():
                    #OLD WAY of storing time-table data for ep simulations - use this for simulations prior to may 20
                    stim_tt=dat['params'].item()[neur]['syn_tt'][0][1] #take stim times from 1st item in list
                    stim_loc=[stim[0] for stim in dat['params'].item()[neur]['syn_tt']]
            if 'stim_tt' in locals():
                xstart=stim_tt[0]
                xend=stim_tt[-1]
                self.syntt_info[neur]={'xstart':xstart,'xend':xend,'stim_tt':stim_tt,'loc':stim_loc}

    def psp_amp(self,peak='min'):
        self.psp_amp={neur:[] for neur in self.traces.keys()}
        self.psp_norm={neur:[] for neur in self.traces.keys()}
        for ntype in self.traces.keys():
            if len(self.spiketime[ntype])==0:
                vmtab=self.traces[ntype][self.somatab]
                stim_tt=self.syntt_info[ntype]['stim_tt']
                vm_init=[vmtab[int(t/self.dt)] for t in stim_tt] #find Vm at the time of stim
                if peak=='min':
                    vm_peak=[np.min(vmtab[int(t/self.dt):int((t+1/self.freq)/self.dt)]) for t in stim_tt] #find peak between pair of stims
                elif peak=='max':
                    vm_peak=[np.mmax(vmtab[int(t/self.dt):int((t+1/self.freq)/self.dt)]) for t in stim_tt]
                else:
                    print('!!!!!!!!!! specify min (for IPSPs) or max (for EPSPs)')
                self.psp_amp[ntype]=np.array(vm_peak)-np.array(vm_init)  #calculate diff between init and peak
                self.psp_norm[ntype]=[amp/self.psp_amp[ntype][0] for amp in self.psp_amp[ntype]] #normalize to 1st one in train
            else:
                print('psp not calculated, spikes found')

class neur_set():
    def __init__(self,param1):
        self.psp_norm={c:{} for c in param1}
        self.psp_amp={c:{} for c in param1}
        self.traces={c:{} for c in param1}
        self.isis={c:{} for c in param1}
        self.stim_tt={c:{} for c in param1}
        self.time={c:{} for c in param1}
        self.params={c:{} for c in param1}
        self.spiketime={c:{} for c in param1}
        
    def add_data(self,data,par1,key):
        if key.startswith('_'):
            newkey=key[1:]
        else:
            newkey=key
        self.spiketime[par1][newkey]=data.spiketime
        if 'psp_norm' in data.__dict__:
            self.psp_norm[par1][newkey]=data.psp_norm
            self.psp_amp[par1][newkey]=data.psp_amp
        self.traces[par1][newkey]=data.traces
        if 'isis' in data.__dict__:
            self.isis[par1][newkey]=data.isis
        if 'neurtypes' in data.__dict__:
            self.neurtypes=data.neurtypes
            self.time[par1][newkey]={neur:data.time for neur in data.neurtypes}
        else:
            self.time[par1][newkey]=data.time
        if 'syntt_info' in data.__dict__:
            if 'stim_tt' in data.syntt_info.keys():
                self.stim_tt[par1][newkey]=data.syntt_info['stim_tt']
            else:
                self.stim_tt[par1][newkey]={neur:range(len(data.syntt_info[neur]['stim_tt'])) for neur in data.syntt_info.keys()}
        self.params[par1][newkey]={'freq':data.freq,'inj':data.inj}

    def freq_inj_curve(self,start,end):
        stim_spikes={c:{} for c in self.spiketime.keys()} 
        self.stim_isis={c:{} for c in self.spiketime.keys()}
        self.inst_spike_freq={c:{} for c in self.spiketime.keys()}
        self.spike_freq={c:{} for c in self.spiketime.keys()}
        for p in self.spiketime.keys():
            for k in self.spiketime[p].keys():
                if len(self.spiketime[p][k]):
                    stim_spikes[p][k]={n:[st for st in spikeset if st > start and st < end]
                                       for n,spikeset in self.spiketime[p][k].items()}
                    print('freq_inj_curve, stim spikes',len(stim_spikes[p][k]),stim_spikes[p][k])
                    self.spike_freq[p][k]={n:len(spikes)/(end-start) for n,spikes in stim_spikes[p][k].items()}
                    self.stim_isis[p][k]={n:[spikeset[i+1]-spikeset[i] for i in range(len(spikeset)-1)]
                                        for n,spikeset in self.spiketime[p][k].items()}
                    self.inst_spike_freq[p][k]={n:[np.round(np.mean([1/isi for isi in isiset]),2)] for n,isiset in self.stim_isis[p][k].items()}

class neur_text():
    def __init__(self,fname,soma='soma'):
        self.column_dict={}
        with open(fname) as fo:
            header=fo.readline().split()
            time_index=header.index('time')-1  #-1 here and column_dict because header begins with '# time'
            columns=[head.split('/')[-2]+head[2:].split('/')[-1] for head in header[2:]]
            self.column_map={col:i+1 for i, col in enumerate(columns)}
            self.soma_name=[col for col in columns if soma in col]
            self.neurtypes=[sn.split('[')[0] for sn in self.soma_name]
        dat=np.loadtxt(fname)
        self.time=dat[:,time_index]
        self.traces={col:mM_to_uM*dat[:,i+1] for i,col in enumerate(self.column_map.keys())}
        self.dt=self.time[1]
        self.sim_time=self.time[-1]
        self.freq=0 #initalize.  Overwrite later if > 0
        
    def cal_stats(self,start_stim,settle_time):
        start_search=np.min(np.where(self.time>start_stim+settle_time)) 
        self.cal_min_max_mn={comp:{'max':np.max(cal[start_search:]),'min':np.min(cal[start_search:])} for comp,cal in self.traces.items()}
        for comp,cal in self.traces.items():
            self.cal_min_max_mn[comp]['mean_trace']=np.round(np.mean(cal[start_search:]),4) 
            self.cal_min_max_mn[comp]['mean']=np.round((self.cal_min_max_mn[comp]['min']+self.cal_min_max_mn[comp]['max'])/2,4) 

    def spikes(self,inj):
        import detect
        self.inj=inj
        self.spiketime={}
        for sn in self.soma_name:
            vmtab=self.traces[sn]
            self.spiketime[sn]=detect.detect_peaks(vmtab)*self.dt
            
    def psp_amp(self,start_stim,freq,peak='min'):
        self.freq=int(freq)
        self.psp_amp={}
        self.psp_norm={}
        stim_tt=[start_stim+float(n)/self.freq for n in range(self.freq)]
        for sn in self.soma_name:
            vmtab=self.traces[sn]
            vm_init=[vmtab[int(t/self.dt)] for t in stim_tt] #find Vm at the time of stim
            if peak=='min':
                vm_peak=[np.min(vmtab[int(t/self.dt):int((t+1/self.freq)/self.dt)]) for t in stim_tt] #find peak between pair of stims
            elif peak=='max':
                vm_peak=[np.max(vmtab[int(t/self.dt):int((t+1/self.freq)/self.dt)]) for t in stim_tt] #
            else:
                print('!!!!!!!!!! specify min (for IPSPs) or max (for EPSPs)')
        self.psp_amp[sn.split('[')[0]]=np.array(vm_peak)-np.array(vm_init)  #calculate diff between init and peak
        self.psp_norm[sn.split('[')[0]]=[amp/self.psp_amp[sn.split('[')[0]][0] for amp in self.psp_amp[sn.split('[')[0]]] #normalize to 1st in train
        xstart=stim_tt[0]
        xend=stim_tt[-1]
        self.syntt_info={'xstart':xstart,'xend':xend,'stim_tt':stim_tt}
