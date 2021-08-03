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
import pandas as pd
from scipy.stats import pearsonr
from moose_nerp.anal import plas_sim_anal_utils as psau 
from moose_nerp.anal import plas_sim_plots as plas_plot

#### Control which analyses and graphs to generate
#path = '/home/dbd/ResearchNotebook/IBAGS2019/FiguresSrc/'
figure_path='/home/avrama/moose/moose_nerp/moose_nerp/plas_simD1PatchSample5_str_net/'#'C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\'#'/home/dbd/Dissertation/plasChapterFigs/'
#data file directory: can be overwritten with args
ddir = '/home/dbd/moose_nerp/'#'/home/avrama/moose/moose_nerp/moose_nerp/plas_simD1PatchSample5_str_net/'#'/run/media/Seagate/ExternalData/plasticity_full_output/NSGPlasticity/testdata/'#'C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\'#
csvdir='/home/dbd/ResearchNotebook/'#'C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\'#
spine_soma_dist_file='/home/avrama/python/DormanAnal/spine_soma_distance.csv'
spine_to_spine_dist_file=csvdir+'spine_to_spine_dist_D1PatchSample5.csv'

plot_input=False
plot_hist=False
regression_all=False #this takes a long time
other_plots=True
RF_use_binned_weight=False
RF_plots=False
linear_reg=False
plot_neighbor_image=False
combined_presyn_cal=False
combined_spatial=False
savefig=False
fontsize=12 

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
    wt_change_title='Random Assignment'
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
params={'neighbors':20,
        'bins_per_sec':100,
        'samp_rate':int(1/dt), 
        'ITI':2, #inter-trial interval - not sure how to read from data  
        'dt':dt,
        'length_of_firing_rate_vector':100,
        'ca_downsamp':10}

### plas names from one trial.  
plas_names=[nm for nm in datalow.dtype.names if 'plas' in nm]
extern_names=[nm for nm in plas_names if 'extern1' in nm]
#syndata = np.load(ddir+'str_connect_plas_simD1PatchSample5_FullTrialMediumVariabilitySimilarTrialsTruncatedNormal_corticalfraction_0.8.npz',allow_pickle=True)

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


'''
import pickle
with open('/run/media/dbd/My Book/2019_09_27_backup/dbd/moose_nerp/spinedistdict.pkl','rb') as f:
    spinedistdict = pickle.load(f)

'_'.join(list(spinedistdict.keys())[0].split('/')[-2:]).replace('[0]','')
'''
############## Create weight_change_event array, binned spike train array, calcium traces array for calculating weight change triggered average ########
df,weight_change_event_df,inst_rate_array,trains,binned_trains_index,ca_trace_array,ca_index,t1weight_distr=psau.weight_change_events_spikes_calcium(files,simtime,params,extern_names)
trial1_stimdf=weight_change_event_df[weight_change_event_df.time==params['ITI']]
trial1_stim_distr={'mean':trial1_stimdf.groupby('trial').mean().weightchange.values,
                'std':trial1_stimdf.groupby('trial').std().weightchange.values,
                'files':np.unique(trial1_stimdf.trial),
                'no change':np.array([np.sum(g.weightchange==0) for k,g in trial1_stimdf.groupby('trial')])}

weight_change_event_df,df=psau.add_spine_soma_dist(weight_change_event_df,df, spine_soma_dist_file)
print('wce df', weight_change_event_df.head())

###### What is this used for ???
'''
(df[df['endweight']<.99].groupby('Variability').count()['spine']/205*100).plot()
(df[df['endweight']>1.01].groupby('Variability').count()['spine']/205*100).plot()
'''

##################### Figure 3: Show synaptic weight ending histogram after first trial for example
### Since first trial, results are same for all variabilities
if plot_hist:
    fhist=plas_plot.weight_histogram(datalow)
    endweight_dist={}
else:
    print('********* trial1 end weight for all synapses ************ ')
    for k,d in data.items():
        index_for_weight = (np.abs(d['time'] - 2)).argmin() #1st trial ending weight.  2 = ITI?  get weight just prior to next trial
        t1weight = [d[n][index_for_weight] for n in d.dtype.names if 'plas' in n]
        print(k,round(np.mean(t1weight),3),'+/-',round(np.std(t1weight),3),', no change:',t1weight.count(1.0))

changedf=df[(df['endweight']<.99) | (df['endweight']>1.01)]
print('******** Correlation of weight vs spine distance *********')
#f_spinedist=plas_plot.endwt_plot(changedf,'spinedist','Distance to Soma ($\mu$ M)',titles)
print(pearsonr(changedf['spinedist'],changedf['endweight']))

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
    f_spinedist=plas_plot.endwt_plot(df,'spinedist','Distance to Soma ($\mu$ M)',titles)
    #Maybe this one is better?
    #f_spinedist=plas_plot.endwt_plot(changedf,'spinedist','Distance to Soma ($\mu$ M)',titles)
    print('########### Spine distance correlation ########')
    if len(np.unique(changedf['Variability']))<=10:
        for var,group in changedf.groupby('Variability'):
            print(var,pearsonr(group['spinedist'],group['endweight']))
    else:
        print(pearsonr(changedf['spinedist'],changedf['endweight']))

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

######### Weight change triggered average of firing rate of neighbors requires spine to spine distance ######
sp2sp = pd.read_csv(spine_to_spine_dist_file,index_col=0)
newindex = [s.replace('[0]','').replace('/','_').replace('D1','').lstrip('_') for s in sp2sp.index]
sp2sp.index = newindex
sp2sp.columns = newindex
df['spine'] = df['spine'].apply(lambda s: s.replace('ecdend','secdend'))
grouped=df.groupby('Variability')
stimspinetospinedist={};sorted_other_stim_spines={}
for grp in grouped.groups.keys():
    dfx=grouped.get_group(grp)
    stimspinetospinedist=sp2sp.filter(items = dfx.loc[dfx['stim']==True].spine.drop_duplicates(),axis=0).filter(items = dfx.loc[dfx['stim']==True].spine.drop_duplicates(),axis=1)
    sorted_other_stim_spines[grp] = pd.concat([pd.Series(stimspinetospinedist[c].sort_values().index, name=c) for c in stimspinetospinedist.columns ], axis=1)

#dfhighplas = df.loc[df['endweight']>1.5] #not used

###################################################################################################################
###################### Weight change triggered average of pre-synaptic firing and of calcium dynamics #################
# ## Generate the 2d array for binned spike times and synaptic distance for a given synapses around a given weight change event
## Run this to create arrays with instantaneous firing rate, will be averaged over synapses with similar weight change
# ## Also, combined neighboring spike trains into one, to look at neighboring firing rate
weight_change_alligned_array = np.zeros((params['neighbors'],params['length_of_firing_rate_vector'],len(weight_change_event_df.index)))

tstart=1.9
tend=0.9
duration=tstart-tend
combined_neighbors_array = np.zeros((params['bins_per_sec'],weight_change_alligned_array.shape[2]))

cabins_per_sec=int(params['samp_rate']/params['ca_downsamp'])
weight_change_alligned_ca=np.zeros((round(cabins_per_sec*(tstart-tend)),len(weight_change_event_df.index)))

print('>>>>>>>>>> Calculating weight change triggered calcium and pre-synaptic firing rate ')
from elephant import kernels
kernel = kernels.GaussianKernel(sigma=100e-3*s)
down_samp=int(params['samp_rate']/params['bins_per_sec'])

for wce in weight_change_event_df.index:
    k = weight_change_event_df.trial[wce]
    syn = weight_change_event_df.synapse[wce]
    t = weight_change_event_df.time[wce]
    if t >= 2:  #if t<2: continue
        spine = syn.split('_to_')[-1].replace('plas','').replace('-sp','_sp')
        #### calcium part ###
        shellnum=syn.split('_3-')[0].split('_to_')[-1]
        spnum=syn.split('-sp')[-1][0]          
        shell='/data/D1_sp'+spnum+shellnum+'_3Shell_0'
        if (k,shell)  in ca_index:   
            index=ca_index.index((k,shell))
            weight_change_alligned_ca[:,wce]=ca_trace_array[index,int(round((t-tstart)*cabins_per_sec)):int(round((t-tend)*cabins_per_sec))]
        ### end calcium part
        temp_array = []
        for i,other in enumerate(sorted_other_stim_spines[k][spine]):
            if i==params['neighbors']: break
            othername = '/data/D1-extern1_to_{}plas'.format(other.replace('_sp','-sp'))
            if (k,othername) not in binned_trains_index:
                print(k,syn,t,spine,i,other,'not in list',othername)
            else:
                index = binned_trains_index.index((k,othername))
                weight_change_alligned_array[i,:,wce] = inst_rate_array[index,int(round((t-tstart)*params['bins_per_sec'])):int(round((t-tend)*params['bins_per_sec']))]
                #for combined_neighbors_array
                if i>0:
                    temp_train = trains[index].copy()
                    temp_train_cut = temp_train[(temp_train>(t-tstart)) & (temp_train<(t-tend))]
                    temp_array.append(temp_train_cut)#,int(round((ta-2)*100)):int(round((t-1)*100))]
        combined_array = elephant.statistics.instantaneous_rate(temp_array,.1e-3*s,kernel=kernel,t_start=(t-tstart)*s, t_stop = (t-tend)*s)
        combined_neighbors_array[:,wce] = combined_array.as_array().flatten()[::down_samp]
weight_change_event_df.sort_values('weightchange')
print('   > finished weight change triggered calcium and pre-synaptic firing rate <  ')

############# create bins of weight change
## option 1 - 9 evenly spaced bins
numbins=9
nochange=0.01
binned_weight_change_index = np.linspace(weight_change_event_df.weightchange.min(),weight_change_event_df.weightchange.max(),numbins)

## Alternative binning: 7 groups: Strong LTD, Moderate LTD, Weak LTD, NO Change, Weak LTP, Moderate LTP, Strong LTP
numbins=7
binned_weight_change_index_LTD = np.linspace(weight_change_event_df.weightchange.min(),-nochange,(numbins+1)//2)#weight_change_event_df.weightchange.max(),numbins)
binned_weight_change_index_LTP = np.linspace(nochange,weight_change_event_df.weightchange.max(),(numbins+1)//2)
binned_weight_change_index = np.hstack((binned_weight_change_index_LTD,binned_weight_change_index_LTP))
print('       now average within weight change bins:',binned_weight_change_index )

### Assign weight_change_events to one of the bins
binned_weight_change_dict = {}
for i in range(len(binned_weight_change_index)-1):
    lower = binned_weight_change_index[i]
    upper = binned_weight_change_index[i+1]
    if i+1 == len(binned_weight_change_index)-1:
        binned_weight_change_dict[(lower,upper)] =  weight_change_event_df.loc[(weight_change_event_df.weightchange>=lower)&(weight_change_event_df.weightchange<=upper)].index.to_numpy()
    else:
        binned_weight_change_dict[(lower,upper)] =  weight_change_event_df.loc[(weight_change_event_df.weightchange>=lower)&(weight_change_event_df.weightchange<upper)].index.to_numpy()
### create a new variable - the binned weight change
weight_change_event_df['weight_bin']=np.nan
for binnum,indices in enumerate(binned_weight_change_dict.values()):
    weight_change_event_df.loc[indices,'weight_bin']=binnum-(numbins//2)
'''
'''
#### calculate mean value within each bin
binned_means = {}
binned_calcium={}
for k,v in binned_weight_change_dict.items():
    binned_means[k] = np.mean(weight_change_alligned_array[:,:,v],axis=2)
    binned_calcium[k]=np.mean(weight_change_alligned_ca[:,v],axis=1)

def mean_std(weight_change_alligned_array,indices):
    #mean and std are calculated in different places in original code
    #mean uses all spines and averages across events
    #std and absmean only use direct spine (not neighbors) and average across time
    #absmean of the nochange events used for mean-subtracted instantaneous firing rate
    mn=np.mean(weight_change_alligned_array[:,:,indices],axis=2)
    std=np.std(weight_change_alligned_array[0,:,indices],axis=0)
    absmean = np.mean(weight_change_alligned_array[0,:,indices],axis=0)
    return mn,std,absmean

all_mean = np.mean(weight_change_alligned_array,axis=2)
pot_index = weight_change_event_df.loc[weight_change_event_df.weightchange>nochange].index.to_numpy()
pot_mean,pot_std,pot_absmean=mean_std(weight_change_alligned_array,pot_index)
allpot = weight_change_alligned_array[0,:,pot_index]
dep_index = weight_change_event_df.loc[weight_change_event_df.weightchange<-nochange].index.to_numpy()
dep_mean,dep_std,dep_absmean=mean_std(weight_change_alligned_array,dep_index)
nochange_index = weight_change_event_df.loc[weight_change_event_df.weightchange==0].index.to_numpy()#[::100]
nochange_mean,nochange_std,nochange_absmean=mean_std(weight_change_alligned_array,nochange_index)
mean_firing_3bins={'Potentiation':pot_mean,'Depression':dep_mean,'No-change':nochange_mean}

########### vmin, vmax NEVER USED #########
vmin = np.min([pot_mean.min(),dep_mean.min(),nochange_mean.min()])
vmax = np.max([pot_mean.max(),dep_mean.max(),nochange_mean.max()])
if abs(vmin) > vmax:
    vmax=abs(vmin)
else:
    vmin=-1*(vmax)

###################################################################################################################
######################## Plots of Weight Change Triggered Average Pre-Syn firing #####################
if other_plots:
    # Bin the colorbar
    if matplotlib.__version__>'3.0.0':
        cbar=True
    else:
        cbar=False
    if combined_presyn_cal:
        f_7bins,cs=plas_plot.combined_figure(binned_means,binned_calcium,binned_weight_change_index,duration)
    else:
        f_7bins,cs=plas_plot.weight_change_trig_avg(binned_means,binned_weight_change_index,duration,title=wt_change_title,colorbar=cbar)
        f_ca,cs=plas_plot.weight_change_trig_avg(binned_calcium,binned_weight_change_index,duration,ylabel='Mean Calcium Concentration (mM)',colorbar=cbar)
    
    #### Use 3 bins - potentiate, depress, no change
    cs3=[plt.cm.tab10(0),plt.cm.tab10(2),plt.cm.tab10(1)]
    f3bins,_=plas_plot.weight_change_trig_avg(mean_firing_3bins,binned_weight_change_index,duration,cs=cs3,title='Weight-change triggered average presynaptic firing rate')
    
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
    ax.plot(x,np.mean(combined_neighbors_array[:,:],axis=1),label='all',c='k',alpha=.5)
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
        plt.savefig(figure_path+sim_files+'CombinedNeigboringFiringRate.pdf')

############### Image plot of firing rate input to nearby synapses.
#### One image per weight change bin
if plot_neighbor_image:
    #f_im= plas_plot.nearby_synapse_image(v,all_mean,binned_means)
    f_im= plas_plot.nearby_synapse_1image(v,all_mean,binned_means)
    #f_im= plas_plot.nearby_synapse_image(v,all_mean,binned_means,mean_sub=False,title=True)
    plas_plot.fractional_size(f_im,[1.5/2,.6])
    if savefig :
        if isinstance(f_im,list): 
            for i,fim in enumerate(f_im):
                fim.savefig(figure_path+sim_files+'NeighboringSynapse_WeightedAverage_Heatmap'+str(i)+'.tif')
        else:
            #f_im.savefig(figure_path+sim_files+'NeighboringSynapse_WeightedAverage_Heatmap.svg')
            f_im.savefig(figure_path+sim_files+'NeighboringSynapse_WeightedAverage_Heatmap.tif')

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
    temp_cov = np.cov(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i] , bias=True)
    all_cov.append(temp_cov[0,1])
    temp_cor = np.correlate(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i])
    all_xcor.append(temp_cor[0])
    #print('shape=',np.shape(temp_cov),', cor=',round(temp_cor[0],3),', cov=',round(temp_cov[0,1],1))
    temp_corr = np.corrcoef(combined_neighbors_array[:,i].T, weight_change_alligned_array[0,:,i])
    all_cor.append(temp_corr[0,1])
all_cov = np.array(all_cov)
all_xcor = np.array(all_xcor)
all_cor = np.array(all_cor)
############ histogram figure from manuscript ####################
if other_plots:
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

###################################################################################################################
###############################################################
# ## Random Forest using average firing rate in 10 bins for both direct and 20 nearest neighbors + starting weight

######## X = weight_change_alligned_array
num_events = weight_change_alligned_array.shape[2]
if RF_use_binned_weight:
    y=weight_change_event_df.weight_bin
    save_name=figure_path+sim_files+'weight_bin.npz'
else:
    y = weight_change_event_df.weightchange
    save_name=figure_path+sim_files
    if linear_reg:
        save_name=save_name+'lin_reg'

## Need to reduce weight_change_alligned_array to 2 dimensions, by stacking neighborings spines
#weight_change_alligned_array dimensions: 20 spines(1 direct path and 19 neighbors x trace length (100 bins) x trials (10 trials x number of spines assessed)
X = weight_change_alligned_array.reshape((weight_change_alligned_array.shape[0]*weight_change_alligned_array.shape[1],num_events)).T
X = X.reshape(num_events,200,10).mean(axis=2) #reduce number of temporal bins from 100 to 10, by taking mean of every 10 bins
Xall=np.concatenate((X,weight_change_event_df.startingweight.to_numpy().reshape(num_events,1)),axis=1) #use all spines as is
#X10bins=X[:,0:10] #1st 10 bins takes just direct input firing rate, drops neighbors
#Xbinned=np.concatenate((X10bins,weight_change_event_df.startingweight.to_numpy().reshape(num,1)),axis=1)))
#X10bins_corr = np.concatenate((X10bins,all_cor.reshape(num,1)),axis=1)
#X10bins_corr=np.concatenate((X10bins_corr,weight_change_event_df.startingweight.to_numpy().reshape(num,1)),axis=1)

if regression_all:
    ######### Divide into training and testing set
    from sklearn.model_selection import train_test_split
    #from sklearn import linear_model
    #from sklearn.feature_selection import RFE
    X_train, X_test, y_train, y_test = train_test_split(Xall, y, test_size=0.1, random_state=42)
    ######### Does linear regression work?
    #reg = linear_model.LinearRegression(fit_intercept=True).fit(X_train_, y_train)
    #print(reg.score(X_train_, y_train),reg.coef_,reg.intercept_) 
    ##### Implement random forest on training set, look at predictions for train and test set
    print('########### not binned  ##############')
    reg,fit,pred=psau.do_random_forest(X_train,y_train,X_test)
    psau.rand_forest_plot(y_train,y_test,fit,pred,'no bins')
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

######### Alternative X array #############
#take pre-syn firing across of synapse itself

newX=weight_change_alligned_array[0,:,:].T #newX is single spine - transpose to become trials X length of trace 
adjacentX=weight_change_alligned_array[1:,:,:].mean(axis=0).T #average over neighboring spines

bin_set=[1,2,3,5]
### train on 90% of data, test on 10%, optionally do some plots, uses random seed of 42
#reg_score,feature_import,linreg_score=psau.random_forest_variations(newX, adjacentX-np.mean(adjacentX,axis=0), y, weight_change_event_df,all_cor,bin_set,num_events,wt_change_title,RF_plots)

### repeat n (trials) times: train on 1-1/trials % of data, test on 1/trials % of data
reg_score,feature_import,linreg_score=psau.random_forest_LeaveNout(newX, adjacentX-np.mean(adjacentX,axis=0), y, weight_change_event_df,all_cor,bin_set,num_events,trials=4,linear=linear_reg)

np.savez(save_name+'.npz',reg_score=reg_score,t1_endwt=t1weight_distr,t1_endwt_stim=trial1_stim_distr,feature_import=feature_import,linreg=linreg_score)

#psau.RF_oob(weight_change_alligned_array,all_cor,weight_change_event_df,y, RF_plots=False)

###### calculate linear correlation between weight change and input firing frequency ###############
numbins=1
Xbins,_=psau.downsample_X(X,numbins,weight_change_event_df,num_events,add_start_wt=False)
Xadj,_=psau.downsample_X(adjacentX,numbins,weight_change_event_df,num_events,add_start_wt=False)
newdf=pd.DataFrame(data=np.column_stack([Xbins,Xadj,y]),columns=['synapse','adj','weight_change'])
print('correlation, direct:',pearsonr(newdf['synapse'],newdf['weight_change']),', adj:',pearsonr(newdf['adj'],newdf['weight_change']))
newchangedf=newdf[(newdf.weight_change>.01) | (newdf.weight_change<-0.01)]
print('correlation, direct:',pearsonr(newchangedf['synapse'],newchangedf['weight_change']),
      ', adj:',pearsonr(newchangedf['adj'],newchangedf['weight_change']))

