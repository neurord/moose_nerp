#!/usr/bin/env python
# coding: utf-8

import matplotlib
#matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)
plt.ion()

import seaborn as sns
import numpy as np
plt.style.use(['seaborn-paper',
                {'axes.spines.right':False,
                 'axes.spines.top': False,
                 'figure.constrained_layout.use': True,
                 'pdf.fonttype': 3,#42
                 'ps.fonttype': 3,
                 'savefig.dpi': 300,
                 'savefig.pad_inches': 0,
                 'figure.figsize':[8,8/1.333],#[11.32,11.32/1.3333],
                 }])
import sys
import glob

from quantities import s,Hz
import elephant
import neo
import pandas as pd
from scipy.stats import pearsonr
import plas_sim_anal_utils as psau #from moose_nerp.anal 
import plas_sim_plots as plas_plot

#### Control which analyses and graphs to generate
#path = '/home/dbd/ResearchNotebook/IBAGS2019/FiguresSrc/'
figure_path='/home/avrama/moose/NSGPlas_2022jun23_ran0_220_uni/'
#figure_path='C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\'#'/home/avrama/python/DormanAnal/'
#'/home/dbd/Dissertation/plasChapterFigs/'
#data file directory: need to allow this to be specified with args
ddir = figure_path+'NSGPlasticity/testdata/'
#'/home/dbd/moose_nerp/'
#'/home/avrama/moose/moose_nerp/moose_nerp/plas_simD1PatchSample5_str_net/'
#'/run/media/Seagate/ExternalData/plasticity_full_output/NSGPlasticity/testdata/'
csvdir=figure_path+'NSGPlasticity/'
#csvdir='C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\'#'/home/dbd/ResearchNotebook/'#
spine_soma_dist_file='/home/avrama/python/DormanAnal/spine_soma_distance.csv'
spine_to_spine_dist_file=csvdir+'D1_short_patch_8753287_D1_17_s2sdist.npz'
#spine_to_spine_dist_file=figure_path+'spine_to_spine_dist_D1PatchSample5.csv'
param_file=csvdir+'testparams.pickle'

plot_input=False
plot_hist=False
regression_all=False #this takes a long time
other_plots=False
RF_use_binned_weight=False
RF_plots=False
linear_reg=False
plot_neighbor_image=False
combined_presyn_cal=False
combined_spatial=False
savefig=True
fontsize=12
warnings=5
dW=True

#ARGS='seed'

try:
    commandline = ARGS.split() #in python: define space-separated ARGS string
    do_exit = False
except NameError: #if you are not in python, read in filename and other parameters
    commandline = sys.argv[1:]
    do_exit = True
sim_files=commandline[0] #'trunc_normal' #choices: 'nmda_block','moved','trunc_normal', 'seed_1'
#
if len(commandline)>1:
    fstart=float(commandline[1])
    fend=float(commandline[2])
else:
    fstart=0
    fend=1
#
tt_names={}
sigma={}
############################ Specify Files ############################33
if sim_files=='trunc_normal':
    ###### 1. Truncated Normal, control using glob
    files = {k:glob.glob(ddir+'plas_sim*'+fn+'*simtime_21.5*thresh_mod_1.158*')[0] for k,fn in zip(['low','medium','intermediate','high'],['LowV','MediumV','HighV','HigherV'])}
    #files = {k:glob.glob(ddir+'*'+fn+'*')[0] for k,fn in zip(['low','medium','intermediate'],['LowV','MediumV','HighV'])}
    if plot_input:
        tt_names={k:glob.glob(ddir+'FullTrial'+fn+'*TruncatedNormal.npz')[0] for k,fn in zip(['low','medium','intermediate','high'],['LowV','MediumV','HighV','HigherV'])}
    wt_change_title=''
elif sim_files=='nmda_block':
    ###### 2. Truncated Normal, nmda block using glob
    files = {k:glob.glob(ddir+'*'+fn+'*nonmda*')[0] for k,fn in zip(['low','medium','intermediate','high'],['LowV','MediumV','HighV','HigherV'])}
    ## input time tables for truncated normal simulations
    if plot_input:
        tt_names={k:glob.glob(ddir+'FullTrial'+fn+'*TruncatedNormal.npz')[0] for k,fn in zip(['low','medium','intermediate','high'],['LowV','MediumV','HighV','HigherV'])}
    wt_change_title='nmda block'
elif sim_files=='moved':
    ###### 3. Alternative method of introducing variability
    files = {int(f.split('Prob_')[-1].split('_Percent')[0]):f for f in glob.glob(ddir+'*MovedSpikes*.npy')}
    files = {k:f for k,f in sorted(files.items())} #sort by move probability
    ## input time tables for moved spikes
    if plot_input:
        tt_names={k:glob.glob(ddir+'MovedSpikesToOtherTrains_Prob_'+str(k)+'_Percent.npz')[0] for k in range(10,101,10)}
    #low=list(tt_names.keys())[0]
    #high=list(tt_names.keys())[-1] 
    wt_change_title='Moved Spikes'
elif sim_files.startswith('seed'):
    ###### 4. single trials, with each trial having different random assignment of spike trains
    #
    all_files=glob.glob(ddir+'plas_simD1PatchSample5*'+sim_files+'*.npy')
    if fstart>0 or fend<1:
        file_start=int(fstart*len(all_files))
        file_end=int(fend*len(all_files))
        files=all_files[file_start:file_end]
        print(sim_files,'num files', len(files))
        sim_files=sim_files+str(file_start)+'_'+str(file_end)
    else:
        files=all_files
    files = {f.split('seed_')[-1].split('.')[0]:f for f in files}
    wt_change_title='Clusters'
#########################################################################

if 'low' in files.keys():
    titles = ['$\sigma=1$ ms','$\sigma=10 $ ms','$\sigma=100 $ ms','$\sigma=200 $ ms']
    sigma={'low':1,'medium':10,'intermediate':100,'high':200}
    keys=list(files.keys())
    low='low'
    high='higher'
elif len(files)==4:              
    keys=list(files.keys())
    titles=['P(move)='+str(k)+'%' for k in keys]
    low=keys[0]
    high=keys[-1]
elif len(files)<=10:
    #[::3] is to select a subset of the inputs - weight_vs_variability only has room for 4 panels
    keys=[k for k in files.keys()][::3]
    titles=['P(move)='+str(k)+'%' for k in files.keys()][::3]
    low=keys[0]
    high=keys[-1]
else: #if many files, randomly select 4 of them
    keys=list(np.random.choice(list(files.keys()),4, replace=False))
    titles=['seed='+str(k) for k in keys]
    low=keys[0]

## load subset of data, determine some parameters ##
data = {k:np.load(files[k],mmap_mode='r') for k in keys} #subset of data, used for weight_vs_variability plot
datalow=data[low]
simtime=round(datalow['time'][-1])+1
dt=datalow['time'][1] 
nochangedW=0.00001

params={'neighbors':20,
        'bins_per_sec':100,
        'samp_rate':int(1/dt), 
        'ITI':2, #inter-trial interval - not sure how to read from data  
        'dt':dt,
        'length_of_firing_rate_vector':100,
        'ca_downsamp':10,
        'simtime':simtime,
        'nochangedW':nochangedW}

if plot_input: ######### fcombined is Figure 1 in manuscript
    from plas_sim_anal_utils import input_plot
    ############ Input spike trains ##################
    tt_Ctx_SPN={k:np.load(f,allow_pickle=True) for k,f in tt_names.items()}
    
    fraster,fcombined=input_plot(tt_Ctx_SPN,datalow,low,high)
    if savefig:
        fraster.savefig(figure_path+sim_files+'initialTrialRasterPSTH.pdf')
        fcombined.savefig(figure_path+sim_files+'RasterPSTHSomaVmCombined.pdf')

#### For Fig 2 - Find spine that potentiates the most and that depresses the most
spine_weight_dict = {}
for n in datalow.dtype.names:
    if n.endswith('headplas'):
        weight = (datalow[n][int(1.1/dt)])
        spine_weight_dict[n]=weight
spine_weights = pd.Series(spine_weight_dict)

pd.DataFrame(spine_weights).sort_values(0)
print('min=',pd.DataFrame(spine_weights).sort_values(0).iloc[0],'\nmax=',pd.DataFrame(spine_weights).sort_values(0).iloc[-1])
#potentiated: '/data/D1-extern1_to_228_3-sp1headplas' for random, "/data/D1-extern1_to_312_3-sp0headplas" for truncated normal
#depressed: '/data/D1-extern1_to_259_3-sp1headplas' for random, "/data/D1-extern1_to_154_3-sp0headplas" for truncated normal
pot_ex=pd.DataFrame(spine_weights).sort_values(0).iloc[-1].name 
dep_ex=pd.DataFrame(spine_weights).sort_values(0).iloc[0].name 

############## Create weight_change_event array, binned spike train array, calcium traces array for calculating weight change triggered average ########

df,weight_change_event_df,inst_rate_array,trains,binned_trains_index,ca_trace_array,ca_index,t1weight_distr,inst_weight_change=psau.weight_change_events_spikes_calcium(files,params,warnings)

trial1_stimdf=weight_change_event_df[weight_change_event_df.time==params['ITI']]
trial1_stim_distr={'mean':trial1_stimdf.groupby('trial').mean().weightchange.values,
                'std':trial1_stimdf.groupby('trial').std().weightchange.values,
                'files':np.unique(trial1_stimdf.trial),
                'no change':np.array([np.sum(g.weightchange==0) for k,g in trial1_stimdf.groupby('trial')])}

print('wce df', weight_change_event_df.head())

######### spine to spine distance, spine to soma distance, and cluster information ######
import os

if len(param_file) and sim_files.startswith('seed'):
    weight_change_event_df,df,inst_weight_change=psau.add_cluster_info(weight_change_event_df,df,inst_weight_change,param_file)

filename, file_extension = os.path.splitext(spine_to_spine_dist_file)
if file_extension == '.csv':
    sp2sp = pd.read_csv(spine_to_spine_dist_file,index_col=0)
else:
    sp2sp_data=np.load(spine_to_spine_dist_file,allow_pickle=True)
    spine_to_spine_dist_array=sp2sp_data['s2sd']
    allspines=sp2sp_data['index'].item().keys()
    sp2sp = pd.DataFrame(spine_to_spine_dist_array,columns=allspines,index=allspines)
newindex = [s.replace('[0]','').replace('/','_').replace('D1','').lstrip('_') for s in sp2sp.index]
sp2sp.index = newindex
sp2sp.columns = newindex

if 'soma' in sp2sp.columns:
    weight_change_event_df,df=psau.add_spine_soma_dist(weight_change_event_df,df, sp2sp.soma,warnings=warnings)
else:   
    weight_change_event_df,df=psau.add_spine_soma_dist(weight_change_event_df,df, spine_soma_dist_file,warnings=warnings)

df['spine'] = df['spine'].apply(lambda s: s.replace('ecdend','secdend'))
grouped=df.groupby('trial') ## for sim with spine clusters, need to groupby seed
stimspinetospinedist={};sorted_other_stim_spines={}
for grp in grouped.groups.keys():
    dfx=grouped.get_group(grp)
    stimspinetospinedist=sp2sp.filter(items = dfx.loc[dfx['stim']==True].spine.drop_duplicates(),axis=0).filter(items = dfx.loc[dfx['stim']==True].spine.drop_duplicates(),axis=1)
    sorted_other_stim_spines[grp] = pd.concat([pd.Series(stimspinetospinedist[c].sort_values().index, name=c) for c in stimspinetospinedist.columns ], axis=1)

##################### Figure 3: Show synaptic weight ending histogram after first trial for example
### Since first trial, results are same for all variabilities
if plot_hist:
    fhist=plas_plot.weight_histogram(datalow)
    endweight_dist={}
else:
    print('********* trial1 end weight for all synapses ************ ')
    for i in range(len(t1weight_distr['mean'])):
        print('file:',t1weight_distr['files'][i], 'mean weight=',round(t1weight_distr['mean'][i],3),'+/-',
              round(t1weight_distr['std'][i],3),', no change:',t1weight_distr['no change'][i])
    print('overall mean weight change=',np.mean(t1weight_distr['mean']))
    #for k,d in data.items():
        #index_for_weight = (np.abs(d['time'] - 2)).argmin() #1st trial ending weight.  2 = ITI?  get weight just prior to next trial
        #t1weight = [d[n][index_for_weight] for n in d.dtype.names if 'plas' in n]
        #print(k,round(np.mean(t1weight),3),'+/-',round(np.std(t1weight),3),', no change:',t1weight.count(1.0))

changedf=df[(df['endweight']<.99) | (df['endweight']>1.01)]

if other_plots:
    ####### Unused Figure #######
    #weight_change_plots(weight_change_event_df)
    
    ############# Figure 2 in manuscript - illustrates calcium based learning rule
    if not sim_files.startswith('seed'):
        fig=plas_plot.plot_spine_calcium_and_weight(datalow,pot_ex,dep_ex)
    
        ########## Figure 4 top panels in manuscript
        f4top,f4bot=plas_plot.weight_vs_variability(data,df,titles,keys,sigma=sigma)

    ################ Figure 5 in manuscript - end weight vs presyn is shaped like BCM curve, only use 4 data files
    f_bcm=plas_plot.endwt_plot(df,'spikecount','Total Presynaptic Spike Count',titles)
    
    #### Figure 5-supplement in manuscript - end weight vs spine location
    if 'spinedist' in changedf.columns:
        f_spinedist=plas_plot.endwt_plot(df,'spinedist','Distance to Soma ($\mu$ M)',titles)
        #Maybe this one is better?
        f_spinedist=plas_plot.endwt_plot(changedf,'spinedist','Distance to Soma ($\mu$ M)',titles)
        print('########### Spine distance correlation ########')
        if len(np.unique(changedf['trial']))<=10:
            for var,group in changedf.groupby('trial'):
                print(var,pearsonr(group['spinedist'],group['endweight']))
        print('spinedist corr, all',pearsonr(changedf['spinedist'],changedf['endweight']))
    if savefig:
        if plot_hist:
            fhist.savefig(figure_path+sim_files+'WeightHistAfterInitialTrial.pdf')
        if not sim_files.startswith('seed'):
            #fig.savefig(figure_path+sim_files+'ca_plas_example_fig.eps')
             #fig.savefig(figure_path+sim_files+'CaPlasExample.pdf')
            #fractional_size(f4top,[1,.75])
            #f4top.savefig(figure_path+sim_files+'combined_synaptic_weight_figure.eps')
            f4top.savefig(figure_path+sim_files+'CombinedSynapticWeightFullTrialVariability.pdf')
            plas_plot.fractional_size(f4bot,[1,.75])
            f4bot.savefig(figure_path+sim_files+'EndweightDistByLTPandLTDvsSigma.pdf')
        plas_plot.fractional_size(f_bcm,[1,1])
        f_bcm.savefig(figure_path+sim_files+'EndingWeightVsPresynSpikeCount.pdf')
        plas_plot.fractional_size(f_spinedist,[1,1])
        f_spinedist.savefig(figure_path+sim_files+'EndingWeightVsSpine2somaDistance.pdf')

    if 'cluster_length' in changedf.columns:
        f_clusterL=plas_plot.endwt_plot(df,'cluster_length','cluster length', titles)
        f_clusterS=plas_plot.endwt_plot(df,'spines_per_cluster','cluster length', titles)
        if savefig:
            f_clusterL.savefig(figure_path+sim_files+'EndWeight_vs_clust_length.pdf')
            f_clusterS.savefig(figure_path+sim_files+'EndWeight_vs_spines_cluster.pdf')

if 'cluster_length' in changedf.columns:
    print('cluster length corr, changedf:',pearsonr(changedf['cluster_length'],changedf['endweight']),
          'all synapses',pearsonr(df['cluster_length'],df['endweight']))
    print('spines_per_cluster corr, changedf:',pearsonr(changedf['spines_per_cluster'],changedf['endweight']),
          'all synapses',pearsonr(df['spines_per_cluster'],df['endweight']))
###################################################################################################################
###################### Weight change triggered average of pre-synaptic firing and of calcium dynamics #################
# ## Generate the 2d array for binned spike times and synaptic distance for a given synapses around a given weight change event
## Run this to create arrays with instantaneous firing rate, will be averaged over synapses with similar weight change
# ## Also, combined neighboring spike trains into one, to look at neighboring firing rate

params['tstart']=1.9  #input spikes begin 1.9 sec prior to weight change time.  I.e., trials are 0.1-1.1 sec for the 2 sec weight time
params['tend']=0.9 #not used
params['duration']=1.0#tstart-tend  #evaluate 1 sec of firing
if 'cluster_length' in changedf.columns:
    params['max_dist']=np.max(weight_change_event_df['cluster_length'])  #~200 microns
else:
    params['max_dist']=np.max(np.max(sp2sp))
params['dist_thresh']=50e-6 #max_dist ~200 microns, try 50 or 100 microns
print('>>>>>>>>>> Calculating weight change triggered calcium and pre-synaptic firing rate ')
weight_change_alligned_array,weight_change_weighted_array,combined_neighbors_array,weight_change_alligned_ca=psau.weight_changed_aligned_array(params,weight_change_event_df,ca_index,sorted_other_stim_spines,binned_trains_index,ca_trace_array,sp2sp,inst_rate_array,trains)

############# create bins of weight change
## option 1 - 9 evenly spaced bins
numbins=9
nochange=0.01
weight_change_event_df.sort_values('weightchange')
binned_weight_change_index = np.linspace(weight_change_event_df.weightchange.min(),weight_change_event_df.weightchange.max(),numbins)

## Alternative binning: 7 groups: Strong LTD, Moderate LTD, Weak LTD, NO Change, Weak LTP, Moderate LTP, Strong LTP
binned_weight_change_dict,binned_weight_change_index=psau.binned_weight_change(weight_change_event_df,numbins,'weightchange',nochange)

#### calculate mean value within each bin
binned_means = {};binned_std={}
binned_weighted_means = {}
binned_calcium={};binned_calcium_std={}
binned_max={}
for k,v in binned_weight_change_dict.items():
    binned_means[k],binned_std[k],_ = psau.mean_std(weight_change_alligned_array,v)
    binned_calcium[k]=np.nanmean(weight_change_alligned_ca[:,v],axis=1)
    binned_calcium_std[k]=np.nanstd(weight_change_alligned_ca[:,v],axis=1)
    binned_weighted_means[k]=np.nanmean(weight_change_weighted_array[:,:,v],axis=2)
    print('wt bin',k,len(v))

#Binned means for instantaneous weight change
dW_aligned_array,inst_weight_change=psau.calc_dW_aligned_array(inst_weight_change,sorted_other_stim_spines,params,binned_trains_index,inst_rate_array,duration=0.050)
variables=['post_spike_dt','pre_spike_dt','isi','pre_rate','pre_spike2_dt','isi2','pre_interval']
binned_dW_dict,binned_dW_index=psau.binned_weight_change(inst_weight_change,numbins,'dW',nochangedW)
binned_spiketime,binned_spiketime_std=psau.bin_spiketime(binned_dW_dict,inst_weight_change,variables)
print('dW weight change bins')
binned_dW_means={}
binned_dW_std={}
for k,v in binned_dW_dict.items():
    print(k,len(v))
    binned_dW_means[k],binned_dW_std[k],_=psau.mean_std(dW_aligned_array,v)
if dW:
    cs = plt.cm.coolwarm(np.linspace(0,1,len(binned_dW_means)-1))
    cs =list(cs)
    cs.insert(len(binned_means)//2,plt.cm.gray(0.5))
    f_dW,ax=plt.subplots(1,1,constrained_layout=True,sharey=True)
    x = np.linspace(0,0.05,params['bins_per_sec']) #only plot 50 ms
    for i,(k,v) in enumerate(binned_dW_means.items()):
        m=v[1:,:].mean(axis=0)
        err = v[1:,:].std(axis=0)
        #ax.fill_between(x[0:len(m)],m-err, m+err,alpha=.5,color=cs[i])
        lbl=' '.join([str(round(float(k[0]),5)),'to',str(round(float(k[1]),5))])
        ax.plot(x[0:len(m)],m,c=cs[i],label=lbl)
    ax.set_ylabel('dW Neighbros Instantaneous Firing Rate (Hz)')
    ax.set_xlabel('Time (s)')
    #if cbar:
    #    plas_plot.colorbar7(cs,binned_weight_change_index,ax)
    #else:
    ax.legend()
    f_im= plas_plot.nearby_synapse_image(np.nanmean(dW_aligned_array,axis=2),binned_dW_means,tmax=0.05)

all_mean = np.nanmean(weight_change_alligned_array,axis=2)
pot_index = weight_change_event_df.loc[weight_change_event_df.weightchange>nochange].index.to_numpy()
pot_mean,pot_std,pot_absmean=psau.mean_std(weight_change_alligned_array,pot_index)
dep_index = weight_change_event_df.loc[weight_change_event_df.weightchange<-nochange].index.to_numpy()
dep_mean,dep_std,dep_absmean=psau.mean_std(weight_change_alligned_array,dep_index)
nochange_index = weight_change_event_df.loc[weight_change_event_df.weightchange==0].index.to_numpy()#[::100]
nochange_mean,nochange_std,nochange_absmean=psau.mean_std(weight_change_alligned_array,nochange_index)
mean_firing_3bins={'Potentiation':pot_mean,'Depression':dep_mean,'No-change':nochange_mean}

calcium_fft,fft_freq=psau.fft_anal(binned_calcium)

###################################################################################################################
######################## Plots of Weight Change Triggered Average Pre-Syn firing #####################
if other_plots:
    print('begin plots of wcta')
    # Bin the colorbar
    if matplotlib.__version__>'3.0.0':
        cbar=True
    else:
        cbar=False
    if combined_presyn_cal:
        f_7bins,cs=plas_plot.combined_figure(binned_means,binned_calcium,binned_weight_change_index,params['duration'],std=[binned_std,binned_calcium_std])
    else:
        f_7bins,cs=plas_plot.weight_change_trig_avg(binned_means,binned_weight_change_index,params['duration'],std=binned_std,title=wt_change_title,colorbar=cbar)
        f_ca,cs=plas_plot.weight_change_trig_avg(binned_calcium,binned_weight_change_index,params['duration'],std=binned_calcium_std,ylabel='Mean Calcium Concentration (mM)',colorbar=cbar)
        #f_cafft,cs=plas_plot.weight_change_trig_avg(calcium_fft,binned_weight_change_index,max(fft_freq),ylabel='FFT Calcium Concentration (mM)',colorbar=cbar)
    
    #### Use 3 bins - potentiate, depress, no change
    cs3=[plt.cm.tab10(0),plt.cm.tab10(2),plt.cm.tab10(1)]
    f3bins,_=plas_plot.weight_change_trig_avg(mean_firing_3bins,binned_weight_change_index,params['duration'],cs=cs3,title='Weight-change triggered average presynaptic firing rate')
    
    ################### Nearby Synapses, using 7 bins
    f_near,ax=plt.subplots(1,1,constrained_layout=True,sharey=True)
    x = np.linspace(0,1,params['bins_per_sec'])
    for i,(k,v) in enumerate(binned_means.items()):
        #f,ax=plt.subplots(1,1,constrained_layout=True,sharey=True)
        #ax.plot(x,v[0,:],c=cs[i],label=k)
        m=v[1:,:].mean(axis=0)-nochange_absmean
        err = v[1:,:].std(axis=0)
        #ax.fill_between(x,m-err, m+err,alpha=.5,color=cs[i])
        lbl=' '.join([str(round(float(k[0]),3)),'to',str(round(float(k[1]),3))])
        ax.plot(x,m,c=cs[i],label=lbl)
    ax.set_ylabel('Mean-Subtracted Instantaneous Firing Rate (Hz)')
    ax.set_xlabel('Time (s)')
    if cbar:
        plas_plot.colorbar7(cs,binned_weight_change_index,ax)
    else:
        ax.legend()
    ax.set_title('Nearby Synapses '+wt_change_title)
    
    ################### Nearby Synapses, using 7 bins
    # ## Combined neighboring spike trains into one
    fig_comb_neighbors,ax = plt.subplots(1,1,constrained_layout=False)
    x = np.linspace(0,1,len(combined_neighbors_array))
    for i,(k,v) in enumerate(binned_weight_change_dict.items()):
        lbl=' '.join([str(round(k[0],3)),'to',str(round(k[1],3))])
        ax.plot(x,np.mean(combined_neighbors_array[:,v],axis=1),label=lbl,c = cs[i])
    #ax.plot(x,np.mean(combined_neighbors_array[:,:],axis=1),label='all',c='k',alpha=.5)
    ax.set_ylabel('Combined Instantaneous Firing\n Rate of Neighboring Synapses (Hz)',fontsize=fontsize)
    ax.set_xlabel('Time (s)',fontsize=fontsize)
    if cbar:
        plas_plot.colorbar7(cs,binned_weight_change_index,ax,fontsize=fontsize)
    else:
        plt.legend()
    
    if savefig:
        plas_plot.fractional_size(f3bins,[1.5/2., .6])
        plas_plot.new_fontsize(f_7bins,fontsize) 
        if combined_presyn_cal:
            f_7bins.savefig(figure_path+sim_files+'BinnedWeightChangeTriggeredAverageCalcium.pdf')
        else:
            f_7bins.savefig(figure_path+sim_files+'BinnedWeightChangeTriggeredAverage.pdf')
            plas_plot.new_fontsize(f_ca,fontsize) 
            f_ca.savefig(figure_path+sim_files+'BinnedWeightChangeTriggeredCalcium.pdf')
        #f3bins.tight_layout()
        #f3bins.savefig(figure_path+sim_files+'weight_change_triggered_average_firingrate_figure.eps')
        #f_near.savefig(figure_path+sim_files+'nearby_synapses_weight_change_average_figure.svg')
        f_near.savefig(figure_path+sim_files+'nearby_synapses_weight_change_average_figure.pdf')
        plt.savefig(figure_path+sim_files+'CombinedNeigboringFiringRate_'+str(round(params['dist_thresh']*1e6))+'um.pdf')

############### Image plot of firing rate input to nearby synapses.
#### One image per weight change bin
if plot_neighbor_image:
    #f_im= plas_plot.nearby_synapse_image(all_mean,binned_means)
    f_im= plas_plot.nearby_synapse_1image(all_mean,binned_means)
    #f_im= plas_plot.nearby_synapse_image(all_mean,binned_means,mean_sub=True,title='')
    #f_im= plas_plot.nearby_synapse_image(all_mean,binned_means,mean_sub=False,title='')
    wf_im= plas_plot.nearby_synapse_1image(all_mean,binned_weighted_means,mean_sub=True,title='wgt,')
    plas_plot.fractional_size(f_im,[1.5/2,.6])
    if savefig :
        if isinstance(f_im,list): 
            for i,fim in enumerate(f_im):
                fim.savefig(figure_path+sim_files+'NeighboringSynapse_Average_Heatmap'+str(i)+'.tif')
        else:
            #f_im.savefig(figure_path+sim_files+'NeighboringSynapse_WeightedAverage_Heatmap.svg')
            f_im.savefig(figure_path+sim_files+'NeighboringSynapse_Average_Heatmap.tif')
            wf_im.savefig(figure_path+sim_files+'NeighboringSynapse_WeightedAverage_Heatmap.tif')

if dW :
    if len(keys)>3:
        subset_df=inst_weight_change[(inst_weight_change.trial == keys[0]) | (inst_weight_change.trial == keys[1]) | (inst_weight_change.trial == keys[2]) | (inst_weight_change.trial == keys[3])  ]
        f_isi1=plas_plot.inst_wt_change_plot(subset_df)
        f_isi3=plas_plot.dW_2Dcolor_plot(subset_df)
    else:
        f_isi1=plas_plot.inst_wt_change_plot(inst_weight_change)
        f_isi3=plas_plot.dW_2Dcolor_plot(inst_weight_change)
    f_isi2=plas_plot.spiketime_plot(binned_spiketime,binned_spiketime_std)
    if savefig:
        for f in f_isi1.keys():
            f_isi1[f].savefig(figure_path+sim_files+f+'.pdf')
        for f in f_isi2.keys():
            f_isi2[f].savefig(figure_path+sim_files+f+'binned.pdf')
        for f in f_isi3.keys():
            f_isi3[f].savefig(figure_path+sim_files+f+'_2Dcolor.pdf')

###################################################################################################################
####################### Covariance of spine input with neighboring spines #################################
'''
##calculating covariance separately for each weight_change bin
cov_dict={k:[] for k in binned_weight_change_dict.keys()}
for weight_change_bin,indices in binned_weight_change_dict.items():
    for i in indices:
        temp_cov = np.cov(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i] , bias=True)
        cov_dict[weight_change_bin].append(temp_cov[0,1])
pot_cov = np.cov(combined_neighbors_array[::100,pot_index], weight_change_alligned_array[0,:,pot_index].T , bias=True)
'''
all_cov = []
all_xcor = []
all_cor = []
for i in range(combined_neighbors_array.shape[1]):
    if not any(np.isnan(combined_neighbors_array[:,i])):
        temp_cov = np.cov(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i] , bias=True)
        all_cov.append(temp_cov[0,1])
        temp_cor = np.correlate(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i])
        all_xcor.append(temp_cor[0])
        #print('shape=',np.shape(temp_cov),', cor=',round(temp_cor[0],3),', cov=',round(temp_cov[0,1],1))
        temp_corr = np.corrcoef(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i])
        if np.isnan(temp_corr[0,1]):
            print ('NAN in temp_corr',i,binned_trains_index[i])
            all_cor.append(0)#FIXME
        else:
            all_cor.append(temp_corr[0,1])
all_cov = np.array(all_cov)
all_xcor = np.array(all_xcor)
all_cor = np.array(all_cor)
############ histogram figure from manuscript ####################
if other_plots:
    print('plot histogram of neighbor correlations')
    f_cov,ax = plt.subplots(constrained_layout=False)
    for i,(k,v) in enumerate(binned_weight_change_dict.items()):
        #plt.figure()
        lbl=' '.join([str(round(k[0],3)),'to',str(round(k[1],3))])
        ax.hist(all_cor[v],histtype='step',bins=21,range=(-1,1),density=True,label=k,linewidth=2,color=cs[i],alpha=.8)
        ax.set_xlim(-1,1)
    ax.set_xlabel('Correlation Coefficient between Direct and Neighboring Input')
    ax.set_ylabel('Normalized Histogram')
    #ax.hist(all_cor,histtype='step',bins=20,range=(-1,1),density=True,label=k,linewidth=2,color='k',alpha=.9,zorder=-10,linestyle='--')
    if cbar:
        plas_plot.colorbar7(cs,binned_weight_change_index,ax)
    elif not cbar:
        ax.legend()

    f_cov5,ax = plt.subplots(constrained_layout=False)
    histlist = [all_cor[v] for v in binned_weight_change_dict.values()]
    histlist.append(all_cor)
    histcolors=list(cs)
    histcolors.append('k')
    ax.hist(histlist,histtype='bar',bins=5,range=(-1,1),density=True,linewidth=2,color=histcolors,stacked=False)
    ax.set_xlabel('Correlation Coefficient between Direct and Neighboring Input')
    ax.set_ylabel('Normalized Histogram')
       
    if cbar:
        plas_plot.colorbar7(cs,binned_weight_change_index,ax)
    else:
        labels=[' '.join([str(round(k[0],3)),'to',str(round(k[1],3))]) for k in binned_weight_change_dict.keys()]+['all bins']
        ax.legend(labels)
        
    if savefig:
        plas_plot.fractional_size(f_cov,(1,1))
        plas_plot.new_fontsize(f_cov,fontsize) 
        f_cov.savefig(figure_path+sim_files+'CorrelationHistDirectNeighbors.pdf')
        plas_plot.fractional_size(f_cov5,(1,1))
        f_cov5.savefig(figure_path+sim_files+'Correl_5binsHistDirectNeighbors.pdf')
        if combined_spatial:
            fig_corr_space=plas_plot.combined_spatial(combined_neighbors_array,binned_weight_change_dict,binned_weight_change_index,all_cor,cs)
            plas_plot.new_fontsize(fig_corr_space,fontsize)
            fig_corr_space.savefig(figure_path+sim_files+'neighborsCorrelation.pdf')
    else:
        f_cov.suptitle('Distribution of Correlation Coefficients Between Direct and Neighboring Inputs')
        f_cov5.suptitle('Distribution of Correlation Coefficients Between Direct and Neighboring Inputs')


'''
############## colormap when no other figures created ###################
cs = plt.cm.coolwarm(np.linspace(0,1,len(binned_means)-1))
cs =list(cs)
cs.insert(len(binned_means)//2,plt.cm.gray(0.5))

fig3D=plas_plot.plot_3D_scatter(inst_weight_change,'isi','pre_rate','dW',binned_dW_dict,cs)
fig3D.savefig(figure_path+sim_files+'_3DdW.pdf')
'''
###################################################################################################################
###############################################################
# ## Random Forest using average firing rate in 10 bins for both direct and n nearest neighbors + starting weight
######## X = weight_change_alligned_array

import RF_utils as rfu

num_events = weight_change_alligned_array.shape[2]
if RF_use_binned_weight:
    y=weight_change_event_df.weight_bin
    save_name=figure_path+sim_files+'weight_bin.npz'
else:
    y = weight_change_event_df.weightchange
    save_name=figure_path+sim_files
    print('SAVE NAME', save_name)
    if linear_reg:
        save_name=save_name+'lin_reg'

if regression_all:
    from sklearn.model_selection import train_test_split
    ######### Divide into training and testing set
    ## Need to reduce weight_change_alligned_array to 2 dimensions, by stacking neighborings spines
    #weight_change_alligned_array dimensions: n+1 spines(1 direct path and n neighbors x trace length (100 bins) x trials (1 or 10 trials x number of spines assessed)
    X = weight_change_alligned_array.reshape((weight_change_alligned_array.shape[0]*weight_change_alligned_array.shape[1],num_events)).T
    X = X.reshape(num_events,params['neighbors']*10,10).mean(axis=2) #reduce number of temporal bins from 100 to 10, by taking mean of every 10 bins
    Xall=np.concatenate((X,weight_change_event_df.startingweight.to_numpy().reshape(num_events,1)),axis=1) #use all spines as is
    #from sklearn import linear_model
    #from sklearn.feature_selection import RFE
    X_train, X_test, y_train, y_test = train_test_split(Xall, y, test_size=0.1, random_state=42)
    ######### Does linear regression work?
    #reg = linear_model.LinearRegression(fit_intercept=True).fit(X_train_, y_train)
    #print(reg.score(X_train_, y_train),reg.coef_,reg.intercept_) 
    ##### Implement random forest on training set, look at predictions for train and test set
    print('########### not binned  ##############')
    reg,fit,pred=rfu.do_random_forest(X_train,y_train,X_test)
    rfu.rand_forest_plot(y_train,y_test,fit,pred,'no bins')
    #rfe = RFE(estimator=linear_model.LinearRegression(), n_features_to_select=1, step=1)
    #rfe.fit(X_train_, y_train)
    #ranking = rfe.ranking_
    #print([X.columns[ranking==i] for i in range(1,11)])
    ########## Plots of random forest results
    '''
    plt.plot(reg.feature_importances_[:-1].reshape(20,10).T[:,0:10]);
    from sklearn.inspection import permutation_importance
    result = permutation_importance(regr,X_test,y_test)
    plt.figure()
    plt.plot(result.importances_mean)
    '''

newX=weight_change_alligned_array[0,:,:].T #newX is single spine - transpose to become trials X length of trace 
adjacentX=weight_change_alligned_array[1:,:,:].mean(axis=0).T #average over neighboring spines

bin_set=[1,3,5]
### train on 90% of data, test on 10%, optionally do some plots, uses random seed of 42
#reg_score,feature_import,linreg_score=rfu.random_forest_variations(newX, adjacentX-np.mean(adjacentX,axis=0), y, weight_change_event_df,all_cor,bin_set,num_events,wt_change_title,RF_plots=False,linear=linear_reg)

### repeat n (trials) times: train on 1-1/trials % of data, test on 1/trials % of data
#reg_score,feature_import,linreg_score=rfu.random_forest_LeaveNout(newX, adjacentX-np.mean(adjacentX,axis=0), y, weight_change_event_df,all_cor,bin_set,num_events,trials=4,linear=linear_reg)

############ RF on calcium bins #############
#ca_reg_score=rfu.RF_calcium(weight_change_alligned_ca,y,bin_set,trials=4)

#np.savez(save_name+'.npz',reg_score=reg_score,t1_endwt=t1weight_distr,t1_endwt_stim=trial1_stim_distr,feature_import=feature_import,linreg=linreg_score,ca_reg_score=ca_reg_score)
        
#rfu.RF_oob(weight_change_alligned_array,all_cor,weight_change_event_df,y, RF_plots=False)

###### calculate linear correlation between weight change and input firing frequency ###############
numbins=1
Xbins,_=rfu.downsample_X(newX,numbins,weight_change_event_df,num_events,add_start_wt=False)
Xadj,_=rfu.downsample_X(adjacentX,numbins,weight_change_event_df,num_events,add_start_wt=False)
newdf=pd.DataFrame(data=np.column_stack([Xbins,Xadj,y]),columns=['synapse','adj','weight_change'])
print('ALL: correlation, direct firing:',pearsonr(newdf['synapse'],newdf['weight_change']),', adj firing:',pearsonr(newdf['adj'],newdf['weight_change']))
newchangedf=newdf[(newdf.weight_change>.01) | (newdf.weight_change<-0.01)]
print('CHANGE DF: correlation, direct firing:',pearsonr(newchangedf['synapse'],newchangedf['weight_change']),
      ', adj firing:',pearsonr(newchangedf['adj'],newchangedf['weight_change']))

if 'cluster_length' in weight_change_event_df:
    clust_len=weight_change_event_df['cluster_length'].to_numpy().reshape(num_events,1)
    clust_sp=weight_change_event_df['spines_per_cluster'].to_numpy().reshape(num_events,1)
    newdf=pd.DataFrame(data=np.column_stack([Xbins,Xadj,y,clust_len,clust_sp]),columns=['synapse','adj','weight_change','cluster_length','spines_per_cluster'])
    newchangedf=newdf[(newdf.weight_change>.01) | (newdf.weight_change<-0.01)]
    print('ALL: correlation, cluster length',pearsonr(newdf['cluster_length'],newdf['weight_change']))
    print('CHANGE DF: correlation, cluster length',pearsonr(newchangedf['cluster_length'],newchangedf['weight_change']))
    print('cluster length vs spines per cluster',pearsonr(newdf['cluster_length'],newdf['spines_per_cluster']))

################# Calculate correlation using maximum across neighbors
#adjacentX=weight_change_alligned_array[1:,:,:].max(axis=1).max(axis=0) # pearsonr(newdf['adj'],newdf['wc'])=(0.037644946344189606, 0.011199245773898055)
#adjacentX=weight_change_alligned_array[1:,:,:].mean(axis=1).max(axis=0)# pearsonr(newdf['adj'],newdf['wc'])=(0.02789514149579918, 0.060216871815671015)
Xinput=weight_change_alligned_array[1:,:,:]
adjbins=10# pearsonr(newdf['adj'],newdf['wc'])=(0.038146383424438976, 0.010163113730931867)
#adjbins=20# pearsonr(newdf['adj'],newdf['wc'])=(0.03781034055692676, 0.0108475656243252)
#adjbins=5# pearsonr(newdf['adj'],newdf['wc'])=(0.03541923162826019, 0.01701610633017229)
downsamp=np.shape(Xinput)[1]//adjbins
Adjbins=np.zeros((np.shape(Xinput)[0],adjbins,np.shape(Xinput)[2])) 
for b in range(adjbins):
    Adjbins[:,b,:]=np.mean(Xinput[:,b*downsamp:(b+1)*downsamp,:],axis=1)
adjacentX=Adjbins.max(axis=1).max(axis=0)
newdf=pd.DataFrame(data=np.column_stack([Xbins,adjacentX,y]),columns=['syn','adj','wc'])
print('correlation max adjacent vs weight=',pearsonr(newdf['adj'],newdf['wc']))

############# Try RF using maximum across all neighbors 
bin_set=[1,3,5]
trials=4
from sklearn.model_selection import train_test_split
reg_score={str(bn)+feat:[] for bn in bin_set for feat in ['_max_'+str(round(1/adjbins,2))+'secmean','_neighbor'+str(round(params['dist_thresh']*1e6))+'um']}
feature_import={str(bn)+feat:[] for bn in bin_set for feat in ['_max_'+str(round(1/adjbins,2))+'secmean','_neighbor'+str(round(params['dist_thresh']*1e6))+'um']}

for numbins in bin_set:
    Xbins,_=rfu.downsample_X(newX,numbins,weight_change_event_df,num_events,add_start_wt=False)
    neighbors,_=rfu.downsample_X(combined_neighbors_array.T,numbins,weight_change_event_df,num_events,add_start_wt=False)
    features={'_max_'+str(round(1/adjbins,2))+'secmean':adjacentX,'_neighbor'+str(round(params['dist_thresh']*1e6))+'um':neighbors}
    for feat,adjX in features.items():
        data=np.column_stack([Xbins,adjX])
        for i in range(trials):
            X_train, X_test, y_train, y_test = train_test_split(data, y, test_size=1/trials)
            reg,fit,pred,regscore,feat_vals=rfu.do_random_forest(X_train,y_train,X_test,y_test,feat=feat)
            reg_score[str(numbins)+feat].append(regscore)
            feature_import[str(numbins)+feat]=feat_vals
        feature_import[str(numbins)+'features']=[str(b) for b in range(numbins)]+['adj'+str(i) for i in range(numbins)]

############# Try RF on instantaneous weight change ##############
def dwsets_for_rf(df):
    features=['isi','pre_rate','neighbor'] #'pre_spike_dt',
    inst_data={'dW='+feat:np.column_stack([df[feat]]) for feat in features}
    for i in range(len(features)):
        for j in range(i+1,len(features)):
            inst_data['dW='+features[i]+','+features[j]]=np.column_stack([df[features[i]],df[features[j]]])

    '''if 'cluster_length' in df:
        inst_data['dW_clust']=np.column_stack([df.isi,df.cluster_length])'''
    #inst_data['dW_time']=np.column_stack([df.pre_rate,df.isi,df.dWt])
    df_nonan=df.dropna()
    features2=['isi2','pre_interval','cluster_length','neighbor']
    for feat1 in features:
        for feat2 in features2:
            if feat1 != feat2:
                inst_data['dW='+feat1+','+feat2]=np.column_stack([df_nonan[feat1],df_nonan[feat2]])
    feat0='isi';feat1='pre_rate'
    for feat2 in features2:
        inst_data['dW='+feat0+','+feat1+','+feat2]=np.column_stack([df_nonan[feat0],df_nonan[feat1],df_nonan[feat2]])
    feat1='pre_spike_dt'
    for feat2 in features2:
        inst_data['dW='+feat0+','+feat1+','+feat2]=np.column_stack([df_nonan[feat0],df_nonan[feat1],df_nonan[feat2]])
    y=df.dW
    yno_nan=df_nonan.dW
    print('\n****** dW correlation ******\n',df_nonan[['pre_spike_dt','pre_interval','isi','isi2','pre_rate','neighbor']].corr())
    return inst_data,y,yno_nan
    
if dW:
    adjacentX=dW_aligned_array[1:,:,:].mean(axis=0).T.mean(axis=1) #average over neighboring spines
    inst_weight_change['neighbor']=adjacentX
    dWchange_df=inst_weight_change.loc[(inst_weight_change.dW>=nochangedW)|(inst_weight_change.dW<=-nochangedW)]
    inst_data,all_y,y_nonan=dwsets_for_rf(dWchange_df) #or inst_weight_change
    for feat,idata in inst_data.items():
        reg_score[feat]=[]
        if len(idata)==len(all_y):
            y=all_y
        elif len(idata)==len(y_nonan):
            y=y_nonan
        else:
            print('PROBLEM!!!!! length of y data NE length of x data')
        for i in range(trials):
            X_train, X_test, y_train, y_test = train_test_split(idata, y, test_size=1/trials)
            reg,fit,pred,regscore,feat_vals=rfu.do_random_forest(X_train,y_train,X_test,y_test,feat=feat)
            reg_score[feat].append(regscore)
            feature_import[feat]=feat_vals
    #feature_import['dW_features']=['pre_rate','isi','key/isi2','pre_int/pre_dt']

    #np.savez(save_name+'_dW.npz',reg_score=reg_score,feature_import=feature_import)

