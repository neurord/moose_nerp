import numpy as np

class neur_output():
    def __init__(self,fname,table_index=None):
        dat=np.load(fname,'r',allow_pickle=True)
        self.fname=fname
        if 'spike_time' in dat.keys():
            self.isis=dat['isi'].item()
            self.spiketime={neur:st[0][0:-1] for neur,st in dat['spike_time'].items()}
        else:
            print('no spike times or isi in', fname)
            self.isis={}
            self.spiketime={neur:[] for neur in dat['vm'].item()}
        self.vmdat=dat['vm'].item()
        self.neurtypes=list(self.vmdat.keys())
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
            self.dt=self.sim_time/len(self.vmdat[neur][0])
        self.time=np.linspace(0,self.dt*len(self.vmdat[neur][0]),len(self.vmdat[neur][0]),endpoint=False)
        for neur in self.neurtypes:
            if 'syn_tt' in dat['params'].item().keys():
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

    def psp_amp(self):
        self.psp_amp={neur:[] for neur in self.vmdat.keys()}
        self.psp_norm={neur:[] for neur in self.vmdat.keys()}
        for ntype in self.vmdat.keys():
            if len(self.spiketime[ntype])==0:
                vmtab=self.vmdat[ntype][self.somatab]
                stim_tt=self.syntt_info[ntype]['stim_tt']
                vm_init=[vmtab[int(t/self.dt)] for t in stim_tt] #find Vm at the time of stim
                vm_peak=[np.min(vmtab[int(t/self.dt):int((t+1/self.freq)/self.dt)]) for t in stim_tt] #find peak between pair of stims
                self.psp_amp[ntype]=np.array(vm_init)-np.array(vm_peak)  #calculate diff between init and peak
                self.psp_norm[ntype]=[amp/self.psp_amp[ntype][0] for amp in self.psp_amp[ntype]] #normalize to 1st one in train
            else:
                print('psp not calculated, spikes found')

class neur_set():
    def __init__(self,param1):
        self.psp_norm={c:{} for c in param1}
        self.psp_amp={c:{} for c in param1}
        self.vmdat={c:{} for c in param1}
        self.isis={c:{} for c in param1}
        self.stim_tt={c:{} for c in param1}
        self.time={c:{} for c in param1}
        self.params={c:{} for c in param1}
        self.spiketime={c:{} for c in param1}
        
    def add_data(self,data,par1,key):
        self.spiketime[par1][key]=data.spiketime
        self.psp_norm[par1][key]=data.psp_norm
        self.psp_amp[par1][key]=data.psp_amp
        self.vmdat[par1][key]=data.vmdat
        self.isis[par1][key]=data.isis
        self.time[par1][key]={neur:data.time for neur in data.syntt_info}
        self.stim_tt[par1][key]={neur:range(len(data.syntt_info[neur]['stim_tt'])) for neur in data.syntt_info}
        self.neurtypes=data.neurtypes
        self.params[par1][key]={'freq':data.freq,'inj':data.inj}

    def freq_inj_curve(self,start,end):
        stim_spikes={c:{} for c in self.spiketime.keys()} 
        self.stim_isis={c:{} for c in self.spiketime.keys()}
        self.inst_spike_freq={c:{} for c in self.spiketime.keys()}
        self.spike_freq={c:{} for c in self.spiketime.keys()}
        for p in self.spiketime.keys():
            for k in self.spiketime[p].keys():
                stim_spikes[p][k]={n:[st for st in spikeset if st > start_stim and st < end_stim]
                                   for n,spikeset in self.spiketime[p][k].items()}
                self.spike_freq[p][k]={n:len(spikes)/(end-start) for n,spikes in stim_spikes[p][k].items()}
                self.stim_isis[p][k]={n:[spikeset[i+1]-spikeset[i] for i in range(len(spikeset)-1)]
                                    for n,spikeset in self.spiketime[p][k].items()}
                self.inst_spike_freq[p][k]={n:[np.round(np.mean([1/isi for isi in isiset]),2)] for n,isiset in self.stim_isis[p][k].items()}
mM_to_uM=1000

class neur_calcium():
    def __init__(self,fname,soma='soma'):
        self.column_dict={}
        with open(fname) as fo:
            header=fo.readline().split()
            time_index=header.index('time')-1  #-1 here and column_dict because header begins with '# time'
            columns=[head.split('/')[-2]+head[2:].split('/')[-1] for head in header[2:]]
            self.column_map={col:i+1 for i, col in enumerate(columns)}
            self.soma_name=[col for col in columns if soma in col][0] 
        dat=np.loadtxt(fname)
        self.time=dat[:,time_index]
        self.calcium={col:mM_to_uM*dat[:,i+1] for i,col in enumerate(self.column_map.keys())}
    def cal_stats(self,start_stim,settle_time):
        start_search=np.min(np.where(self.time>start_stim+settle_time)) 
        self.cal_min_max_mn={comp:{'max':np.max(cal[start_search:]),'min':np.min(cal[start_search:])} for comp,cal in self.calcium.items()}
        for comp,cal in self.calcium.items():
            self.cal_min_max_mn[comp]['mean_trace']=np.round(np.mean(cal[start_search:]),4) 
            self.cal_min_max_mn[comp]['mean']=np.round((self.cal_min_max_mn[comp]['min']+self.cal_min_max_mn[comp]['max'])/2,4) 

