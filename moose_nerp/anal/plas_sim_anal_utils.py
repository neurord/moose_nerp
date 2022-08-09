import numpy as np
import neo
import elephant
from quantities import Hz,s
import pandas as pd
from scipy.signal import find_peaks

#naming convention for calcium compartments from spine names
#may need to be changed if table names change in moose_nerp
def get_shellname(syn):
    if '-sp' in syn:
        shellnum=syn.split('_3-')[0].split('_to_')[-1]
        spnum=syn.split('-sp')[-1].split('headplas')[0]
        shell='/data/D1_sp'+spnum+shellnum+'_3Shell_0'
    else:
        shellnum=syn.split('_to_')[-1].split('_')[0]
        shell='/data/D1_'+shellnum+'Shell_0'
    return shell
############## Create weight_change_event array, then binned spike train array, for calculating weight change triggered average ########
def dW(data,syn,dt,spiketimes,tr,inst_weightchange,peaktimes,nochangedW):
    #NEW - instantaneous weight change    
    all_dW=np.diff(data[syn]) #instantaneous weight change (instead of trial)
    dWpeaks,_=find_peaks(np.abs(all_dW),prominence=nochangedW/2)  #time of weight change
    dWtime=dWpeaks*dt
    ''' #for debugging
    if len(dWpeaks): 
        if np.max(all_dW)>1e-5:
            from matplotlib import pyplot as plt
            plt.plot(dt*np.arange(len(all_dW)),all_dW)
            plt.scatter(dWtime,all_dW[dWpeaks])
    '''
    #NEW - determine time of post-synaptic and pre-synaptic spikes for each change in weight
    for dWindex,dWt in zip(dWpeaks,dWtime):
        all_post_spikes=(dWt-spiketimes)[np.where(dWt-spiketimes>0)] #
        if len(all_post_spikes):
            postsyn_spike=np.min(all_post_spikes)               
        else:
            postsyn_spike=np.nan
            #print('no postsyn spike:', syn.split('/')[-1],dWindex,dWt)
        all_pre_spikes=(dWt-peaktimes)[np.where(dWt-peaktimes>0)]
        if len(all_pre_spikes):
            presyn_spike=np.min(all_pre_spikes)
            if len(all_pre_spikes)>1:
                presyn_spike2=sorted(all_pre_spikes)[1]
            else:
                presyn_spike2=np.nan
        else:
            presyn_spike=np.nan
            presyn_spike2=np.nan
            #print('no presyn spike:', syn.split('/')[-1],dWindex,dWt)
        isi=presyn_spike-postsyn_spike #gives postsyn_time - presyn_time for closest spikes prior to weight change
        isi2=presyn_spike2-postsyn_spike
        pre_interval=presyn_spike2-presyn_spike
        if ~np.isnan(isi):
            inst_weightchange.append([tr,syn,all_dW[dWindex],dWt,postsyn_spike,presyn_spike,isi,presyn_spike2,pre_interval,isi2])
    iwc_cols=['trial','synapse','dW','dWt','post_spike_dt','pre_spike_dt','isi','pre_spike2_dt','pre_interval','isi2']
    return inst_weightchange,iwc_cols

def weight_change_events_spikes_calcium(files,params,warnings):
    #### This loops over every data file ######
    from elephant import kernels
    neighbors=params['neighbors']
    bins_per_sec=params['bins_per_sec']
    samp_rate=params['samp_rate']
    simtime=params['simtime']
    length_of_firing_rate_vector=params['length_of_firing_rate_vector']
    ca_downsamp=params['ca_downsamp']
    ITI=params['ITI']
    down_samp=int(samp_rate/bins_per_sec)
    
    binned_trains_index=[]
    trains = []
    all_ca_array=[];ca_index=[]

    # dt = 0.1e-3 (.1 ms) so a stepsize of 100 data points is equivalent to 10 ms, step size of 1000 datapoints = 100 ms
    t1weight_dist={'mean':[],'std':[],'no change':[],'files':[]}
    # ## Detect weight change events
    #stepsize = 1000
    weight_at_times = np.arange(0.,simtime,ITI) #first trial starts at time=0.0
    weight_at_index = (weight_at_times*samp_rate).astype(np.int64)
    df=[];wce_df=[]
    inst_weightchange=[]
    for i,(trial,f) in enumerate(files.items()):  
        weightchangelist=[]; dframelist = []
        missing=0
        d= np.load(f,mmap_mode='r')  
        print(i, 'analyzing',trial)
        index_for_weight = (np.abs(d['time'] - 2)).argmin() #1st trial ending weight = weight just prior to next trial; 2 = ITI? 
        t1weight = [d[n][index_for_weight] for n in d.dtype.names if 'plas' in n]
        t1weight_dist['mean'].append(np.mean(t1weight))
        t1weight_dist['std'].append(np.std(t1weight))
        t1weight_dist['no change'].append(t1weight.count(1.0))
        t1weight_dist['files'].append(trial)
        #extract post-syn spikes
        somaVm=d['/data/VmD1_0']
        spikes,_=find_peaks(somaVm,height=0.0,distance=200) #index of time of post-syn spikes
        spiketimes= spikes*(1.0/samp_rate)
        #plas_names=[nm for nm in d.dtype.names if 'plas' in nm ] #includes synaptic inputs directly onto dendrites
        plas_names=[nm for nm in d.dtype.names if 'plas' in nm and 'head' in nm] #plas names may differ for each file if using different seeds
        extern_names=[nm for nm in plas_names if 'extern1' in nm]
        for n in plas_names:
            #print(n,d[n][-1])
            endweight = d[n][-1]
            if '_to_' in n:
                spine = n.split('_to_')[-1].replace('-','_').strip('plas')
                stim=True
                spikecount = len(find_peaks(d[n.rstrip('plas')])[0])
            elif 'ampa' in n:
                spine = '_'.join(n.split('/')[-1].split('_')[1:-1])
                stim=False
                spikecount = 0
            weight_change_variance = np.var(np.diff(d[n]))
            spinedist = np.nan#[v for k2,v in spinedistdict.items() if spine in '_'.join(k2.split('/')[-2:]).replace('[0]','')][0]
            #print(n,spine,endweight,stimvariability,spinedist)
            dframelist.append((spine,endweight,trial,spinedist,stim,spikecount,weight_change_variance))
        for jj,syn in enumerate(extern_names):        
            weightchange=np.diff(d[syn][weight_at_index])
            startingweight = d[syn][weight_at_index]
            for k,w in enumerate(weightchange):
                weightchangelist.append((trial,syn,weight_at_times[k+1],startingweight[k],w))                
            peaks,_ = find_peaks(d[syn.rpartition('plas')[0]]) 
            peaktimes = d['time'][peaks]
            ### create SpikeTrain for every trial/synapse
            train = neo.SpikeTrain(peaktimes,t_stop=simtime*s,units=s)
            trains.append(train)
            binned_trains_index.append((trial,syn))
            #extract calcium traces.  Must edit to match naming convention
            shell=get_shellname(syn)
            if shell in d.dtype.names:
                ca_index.append((trial,shell))
                #jj=i*len(ca_names)+j
                all_ca_array.append(d[shell][::ca_downsamp])
            else:
                missing+=1
                if missing<warnings:
                    print(missing,syn,shell,' NOT IN FILE',trial)
            inst_weightchange,iwc_cols=dW(d,syn,(1.0/samp_rate),spiketimes,trial,inst_weightchange,peaktimes,params['nochangedW'])
            if missing>warnings-1:
                print(missing, 'extern_names have no calcium conc')
        df.append(pd.DataFrame(dframelist,columns = ['spine','endweight','trial','spinedist','stim','spikecount','weight_change_variance']))
        wce_df.append(pd.DataFrame(weightchangelist,columns = ['trial','synapse','time','startingweight','weightchange']))
    alldf = pd.concat(df).reset_index()
    weight_change_event_df = pd.concat(wce_df).reset_index()
    inst_weight_change_df=pd.DataFrame(inst_weightchange,columns=iwc_cols)
    ### instantaneous weight array - created from spikeTrains
    kernel = kernels.GaussianKernel(sigma=100e-3*s)
    numtrains=len(trains) #use extern_names
    inst_rate_array = np.zeros((numtrains,int(simtime*bins_per_sec)))
    for jj,train in enumerate(trains):
        train.sampling_rate=samp_rate*Hz
        inst_rate_array[jj,:] = elephant.statistics.instantaneous_rate(train,train.sampling_period,kernel=kernel)[::down_samp,0].flatten()
    return alldf,weight_change_event_df,inst_rate_array,trains,binned_trains_index,np.array(all_ca_array),ca_index,t1weight_dist,inst_weight_change_df

def add_spine_soma_dist(wce_df,df, spine_soma_dist_file,warnings=5):
    if isinstance(spine_soma_dist_file,pd.core.series.Series):
        spine_soma_dist=spine_soma_dist_file
    else:
        spine_soma_dist_df=pd.read_csv(spine_soma_dist_file,index_col=0)
        spine_soma_dist=spine_soma_dist_df.distance
    wce_df['spine_soma_dist']=np.nan
    missing=0
    for wce in wce_df.index:
        syn = wce_df.synapse[wce]
        spine = syn.split('_to_')[-1].replace('plas','').replace('-sp','_sp')
        if 'head' in spine: #need to add distance to soma for non-spine plasticity
            wce_df.loc[wce,'spine_soma_dist']=spine_soma_dist.loc[spine]
        else:
            branch_dist=[spine_soma_dist[i] for i in spine_soma_dist.index if i.startswith(spine)]
            wce_df.loc[wce,'spine_soma_dist']=np.mean(branch_dist)
            if np.std(branch_dist)>1e-12:  #if distances of all spines the same, branch dist is well defined
                missing+=1
            if missing<warnings:
                print('wce in add_spine_soma_dist',syn,':::',spine,'not spine head, use mean of spine distances for that compartment')
    if missing>warnings-1:
        print('wce, add_spine_soma_dist', missing, 'syn are not spine head, use mean of spine distances for that compartment')
    missing=0
    for syn in df.spine:
        if 'head' in syn:
            df.loc[df.spine==syn,'spinedist']=1e6*spine_soma_dist.loc[syn] #distance in um
        else:
            branch_dist=[spine_soma_dist[i] for i in spine_soma_dist.index if i.startswith(syn)]
            df.loc[df.spine==syn,'spinedist']=1e6*np.mean(branch_dist)
            if np.std(branch_dist)>1e-12:
                missing+=1
            if missing<warnings:
                print('df in add_spine_soma_dist',syn,'::: not spine head, use mean of spine distances for that compartment')
    if missing>warnings-1:
        print('df, add_spine_soma_dist', missing, 'syn are not spine head, use mean of spine distances for that compartment')
    return wce_df,df

def weight_changed_aligned_array(params,weight_change_event_df,ca_index,sorted_other_stim_spines,binned_trains_index,ca_trace_array,sp2sp,inst_rate_array,trains):
    from elephant import kernels
    cabins_per_sec=int(params['samp_rate']/params['ca_downsamp'])
    weight_change_alligned_array = np.zeros((params['neighbors'],params['length_of_firing_rate_vector'],len(weight_change_event_df.index)))
    weight_change_weighted_array = np.zeros((params['neighbors'],params['length_of_firing_rate_vector'],len(weight_change_event_df.index)))
    combined_neighbors_array = np.zeros((int(round(params['duration']*params['bins_per_sec'])),weight_change_alligned_array.shape[2]))
    weight_change_alligned_ca=np.zeros((int(round(cabins_per_sec*params['duration'])),len(weight_change_event_df.index)))
    kernel = kernels.GaussianKernel(sigma=100e-3*s)
    sampling_resolution=1.0/params['samp_rate']
    down_samp=int(params['samp_rate']/params['bins_per_sec'])
    branch_wce={}
    for wce in weight_change_event_df.index:
        tr = weight_change_event_df.trial[wce]
        syn = weight_change_event_df.synapse[wce]
        t = weight_change_event_df.time[wce] 
        if t >= 2:  #if t<2: continue  
            spine = syn.split('_to_')[-1].replace('plas','').replace('-sp','_sp')
            #### calcium part ###
            shell=get_shellname(syn)
            if (tr,shell)  in ca_index:   
                index=ca_index.index((tr,shell))
                #weight_change_alligned_ca[:,wce]=ca_trace_array[index,int(round((t-tstart)*cabins_per_sec)):int(round((t-tend)*cabins_per_sec))]
                weight_change_alligned_ca[:,wce]=ca_trace_array[index,int(round((t-params['tstart'])*cabins_per_sec)):int(round((t-params['tstart']+params['duration'])*cabins_per_sec))]
            else:
                weight_change_alligned_ca[:,wce]=np.nan
                print(tr,shell,'not in ca_index')
             ### end calcium part
            temp_array = [];sumdist=0
            if spine in sorted_other_stim_spines[tr]:
                for i,other in enumerate(sorted_other_stim_spines[tr][spine][0:params['neighbors']]):
                    distance=sp2sp[spine][other] #convert from meters to mm, further is smaller
                    othername = '/data/D1-extern1_to_{}plas'.format(other.replace('_sp','-sp'))
                    if (tr,othername) not in binned_trains_index:
                        print(tr,syn,t,spine,i,other,'not in list',othername)
                    #else:
                    index = binned_trains_index.index((tr,othername))
                    #weight_change_alligned_array[i,:,wce] = inst_rate_array[index,int(round((t-tstart)*params['bins_per_sec'])):int(round((t-tend)*params['bins_per_sec']))]
                    #what about weighting the neighbors by distance?

                    weight_change_alligned_array[i,:,wce] = inst_rate_array[index,int(round((t-params['tstart'])*params['bins_per_sec'])):int(round((t-params['tstart']+params['duration'])*params['bins_per_sec']))]
                    weight_change_weighted_array[i,:,wce] = (1-distance/params['max_dist'])*inst_rate_array[index,int(round((t-params['tstart'])*params['bins_per_sec'])):int(round((t-params['tstart']+params['duration'])*params['bins_per_sec']))]
                    #for combined_neighbors_array
                    if i>0 and distance<=params['dist_thresh']:
                        temp_train = trains[index].copy()
                        #temp_train_cut = temp_train[(temp_train>(t-tstart)) & (temp_train<(t-tend))]
                        temp_train_cut = temp_train[(temp_train>(t-params['tstart'])) & (temp_train<(t-params['tstart']+params['duration']))]
                        temp_array.append(temp_train_cut)#,int(round((ta-2)*100)):int(round((t-1)*100))]
                #combined_array = elephant.statistics.instantaneous_rate(temp_array,.1e-3*s,kernel=kernel,t_start=(t-tstart)*s, t_stop = (t-tend)*s)
                #### new version of elephant.statistics.instantaneous_rate provides 2D array with 1 column for each list in temp_array.  Need to flatten first
                train_list=sorted([round(i,4) for ta in temp_array for i in ta.as_array() ])
                temp_array=neo.SpikeTrain(train_list,t_stop=params['simtime']*s,units=s)
                combined_array = elephant.statistics.instantaneous_rate(temp_array,sampling_resolution*s,kernel=kernel,t_start=(t-params['tstart'])*s, t_stop = (t-params['tstart']+params['duration'])*s)
                combined_neighbors_array[:,wce] = combined_array.as_array().flatten()[::down_samp]
            else: #branch, not spine. cannot determine neighbors from sorted_other_stim_spines. possible use all spines on branch?
                index = binned_trains_index.index((tr,syn))
                weight_change_alligned_array[0,:,wce] = inst_rate_array[index,int(round((t-tstart)*params['bins_per_sec'])):int(round((t-tstart+duration)*params['bins_per_sec']))]
                weight_change_alligned_array[1:params['neighbors'],:,wce]=np.nan
                weight_change_weighted_array[1:params['neighbors'],:,wce]=np.nan
                combined_neighbors_array[:,wce]=np.nan
                branch_wce[syn]={'trial':tr,'index':wce,'weight change':weight_change_event_df.weightchange[wce],'firing':np.mean(weight_change_alligned_array[0,:,wce]),'shell':shell,'cal':np.mean(weight_change_alligned_ca[:,wce])}
    print('   > finished weight change triggered calcium and pre-synaptic firing rate <  ')
    print(len(branch_wce), '***** branches, not spine - no neighbors or calcium.')
    if len(branch_wce):
        print('mean calcium=', np.mean([bwce['cal'] for bwce in branch_wce.values()]),
              'mean weight change=',np.mean([bwce['weight change'] for bwce in branch_wce.values()]))
    return weight_change_alligned_array,weight_change_weighted_array,combined_neighbors_array,weight_change_alligned_ca

def mean_std(weight_change_alligned_array,indices):
    #mean and std uses all spines and averages across events
    #absmean only use direct spine (not neighbors) and average across time
    #absmean of the nochange events used for mean-subtracted instantaneous firing rate
    mn=np.nanmean(weight_change_alligned_array[:,:,indices],axis=2)
    std=np.nanstd(weight_change_alligned_array[:,:,indices],axis=2)
    absmean = np.nanmean(weight_change_alligned_array[0,:,indices],axis=0)
    return mn,std,absmean

def add_cluster_info(wce_df,df, inst_df,cluster_file):
    import pickle
    f=open(cluster_file,'rb')
    mydata=pickle.load(f)
    clusterlist=[[str(m['seed']),m['ClusteringParams']['cluster_length'],m['ClusteringParams']['n_spines_per_cluster']] for m in mydata]
    clusterdf=pd.DataFrame(clusterlist,columns=['trial','cluster_length','spines_per_cluster'])
    print('cluster correlations',clusterdf['cluster_length'].corr(clusterdf['spines_per_cluster']))
    wce_df=pd.merge(wce_df,clusterdf,on='trial',validate='many_to_one')
    df=pd.merge(df,clusterdf,on='trial',validate='many_to_one')
    inst_df=pd.merge(inst_df,clusterdf,on='trial',validate='many_to_one')
    return wce_df,df,inst_df

def fft_anal(binned_means):
    mags={}
    for key,values in binned_means.items():
        fft=np.fft.rfft(values/np.mean(values))
        mags[key]=np.abs(fft)
    freqs=np.fft.rfftfreq(len(values))
    return mags,freqs

def bin_spiketime(binned_weight_change_dict,wce_df,variables):
    binned_spiketime={kk:{} for kk in variables}
    binned_spiketime_std={kk:{} for kk in variables}
    for kk in binned_spiketime.keys():
        for k,v in binned_weight_change_dict.items():
            binned_spiketime[kk][k]=wce_df[kk].iloc[v].mean()
            binned_spiketime_std[kk][k]=wce_df[kk].iloc[v].std()/np.sqrt(len(wce_df[kk].iloc[v]))
    return binned_spiketime,binned_spiketime_std

def binned_weight_change(wce_df,numbins,weight_var,nochange):
    numbins=7
    binned_weight_change_index_LTD = np.linspace(wce_df[weight_var].min(),-nochange,(numbins+1)//2)#wce_df[weight_var].max(),numbins)
    binned_weight_change_index_LTP = np.linspace(nochange,wce_df[weight_var].max(),(numbins+1)//2)
    binned_weight_change_index = np.hstack((binned_weight_change_index_LTD,binned_weight_change_index_LTP))
    print('       now average within weight change bins:',binned_weight_change_index )

    ### Assign weight_change_events to one of the bins
    binned_weight_change_dict = {}
    for i in range(len(binned_weight_change_index)-1):
        lower = binned_weight_change_index[i]
        upper = binned_weight_change_index[i+1]
        if i+1 == len(binned_weight_change_index)-1:
            binned_weight_change_dict[(lower,upper)] =  wce_df.loc[(wce_df[weight_var]>=lower)&(wce_df[weight_var]<=upper)].index.to_numpy()
        else:
            binned_weight_change_dict[(lower,upper)] =  wce_df.loc[(wce_df[weight_var]>=lower)&(wce_df[weight_var]<upper)].index.to_numpy()
    ### create a new variable - the binned weight change
    wce_df['weight_bin']=np.nan
    for binnum,indices in enumerate(binned_weight_change_dict.values()):
        wce_df.loc[indices,'weight_bin']=binnum-(numbins//2)
    return binned_weight_change_dict,binned_weight_change_index

def calc_dW_aligned_array(inst_weight_change,sorted_other_stim_spines,params,binned_trains_index,inst_rate_array,duration=0.05):
    tstart=duration #: consider input spikes beginning duration sec prior to weight change time.
    #duration: tstart-tend  #evaluate 0.1 sec of firing for dW
    weight_change_alligned_array = np.zeros((params['neighbors'],int(duration*params['bins_per_sec']),len(inst_weight_change.index)))
    inst_weight_change['pre_rate']=np.nan
    for wce in inst_weight_change.index:
        tr = inst_weight_change.trial[wce]
        syn = inst_weight_change.synapse[wce]
        t = inst_weight_change.dWt[wce] 
        spine = syn.split('_to_')[-1].replace('plas','').replace('-sp','_sp')
        if spine in sorted_other_stim_spines[tr]:
            for i,other in enumerate(sorted_other_stim_spines[tr][spine][0:params['neighbors']]):
                othername = '/data/D1-extern1_to_{}plas'.format(other.replace('_sp','-sp'))
                index = binned_trains_index.index((tr,othername))
                #weight_change_alligned_array[i,wce] = inst_rate_array[index,int(round((t-tstart)*params['bins_per_sec'])):int(round((t-tstart+duration)*params['bins_per_sec']))].mean()
                if len(inst_rate_array[index,int(round((t-tstart)*params['bins_per_sec'])):int(round(t*params['bins_per_sec']))])!=int(duration*params['bins_per_sec']):
                    print('wrong size',wce, 'changing t',t,' by tiny amount',t-1e-6)
                    t=t-1e-6
                weight_change_alligned_array[i,:,wce]=inst_rate_array[index,int(round((t-tstart)*params['bins_per_sec'])):int(round(t*params['bins_per_sec']))]
        inst_weight_change.pre_rate[wce]=weight_change_alligned_array[0,:,wce].mean()
    return weight_change_alligned_array,inst_weight_change
