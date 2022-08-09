# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 10:07:34 2021

@author: kblackw1
"""
import numpy as np
import glob
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
plt.ion()

def flatten(list_of_lists):
    return [l for lst in list_of_lists for l in lst ]

def create_barplot_means(df):
    means={}
    stderr={}
    for feat in np.unique(df.other_feature):
        mn=df[df['other_feature']==feat].groupby('numbins').mean()['score'].values
        std=df[df['other_feature']==feat].groupby('numbins').std()['score'].values
        count=df[df['other_feature']==feat].groupby('numbins').count()['score'].values
        means[feat]=mn
        stderr[feat]=std/np.sqrt(count)
    return means,stderr

def bar_plot_mean_score(data_set,xvalues,stderr_set,title,label_dict={}):
    if len(title):
        fs=12
    else:
        fs=14
    ########### Plot regression scores #######            
    width=1/(len(data_set)+1) #2 bars, width=1/3, put tick at 1/6; 4 bars, width=1/5, put tick at 0.3 
    colors = plt.cm.magma([int(i*(len(plt.cm.magma.colors)/len(data_set))) for i in range(len(data_set))])
    fig,ax=plt.subplots(1,1)
    for i,(k,data) in enumerate(data_set.items()):
        if k in label_dict.keys():
            lbl=label_dict[k]
        else:
            lbl=k
        offset=i*width
        plt.bar(np.arange(len(data))+offset,data,yerr=stderr_set[k],label=k,width=width,color=colors[i])
    ax.set_ylabel('Prediction score')
    ax.set_xlabel('Time samples')
    fig.suptitle(title)
    ax.set_xticks(list(np.arange(len(xvalues))+width*((len(data_set)-1)/2)))
    ax.set_xticklabels(xvalues)
    ax.tick_params(axis='y', labelsize=fs)
    ax.tick_params(axis='x', labelsize=fs)
    ylim=ax.get_ylim()
    ax.set_ylim(ylim[0],max(round(1.2*ylim[1],1),round(ylim[1]+0.1,1)))
    if len(data_set)>1:
        #ax.legend(loc='upper center')
        ax.legend()
    return fig
    
def endwt_histogram(endwt):
    ######### Plot distrubtion of ending synapse weight measuares
    fig,axes=plt.subplots(len(endwt),1)
    for ax,em in enumerate(endwt.keys()):
        axes[ax].hist(endwt[em],bins=50,rwidth=0.9)
        #ax.set_yscale('log')
        axes[ax].set_ylabel('Number of synapses')
        axes[ax].set_xlabel(em+' Ending Synaptic weight')
    #2way histogram
    jg = sns.jointplot(endwt['mean'],endwt['no change'],ratio=5,s=10,alpha=.8,edgecolor='0.2',linewidth=.2,color='k',marginal_kws=dict(bins=50))
    #xlim=(np.min(endwt['mean'])*0.9,np.max(endwt['mean'])*1.1),ylim=(0,np.max(endwt['no change'])*1.1)
    jg.set_axis_labels('mean end weight','synapses with no change')
    fig.tight_layout()
    return fig  

def importance_plot(feat_import,testset_scores):
    figs=[]
    bin_set=[k[0] for k in feat_import.keys() if k[0].isdigit()]
    feature_types=[k[1:] for k in feat_import.keys() if not k.endswith('features') and k[0].isdigit()]
    for numbins in np.unique(bin_set):
        f,ax = plt.subplots(1,1)
        for feat_type in np.unique(feature_types):
            key=numbins+feat_type
            vals=feat_import[key]
            score=round(np.mean(testset_scores[key]),3)
            #if isinstance(feat_import[key],np.ndarray):
            ax.errorbar(range(np.shape(vals)[1]),np.mean(vals,axis=0),yerr=np.std(vals,axis=0),label=key+', mean score='+str(score))
            print(key,'mean_score=',score)
        ax.set_xlabel('feature name')
        ax.legend()
        if numbins+'_feature' in feat_import.keys():
            xticks=feat_import[numbins+'_features']
            ax.set_xticks(list(range(len(xticks))))
            ax.set_xticklabels(xticks)
            ax.set_ylabel('feature importance')
    figs.append(f)
    return figs

def read_data(files,endwt_measures): 
    testset_scores={}
    endwt={}
    feat_import={}    
    for f in files:
        data=np.load(f,allow_pickle=True)
        for key,values in data['reg_score'].item().items():
            if key not in testset_scores.keys():
                testset_scores[key]=[]
            if isinstance(values,list) and len(testset_scores[key]): #generated from leave_one_out
                for v in values:
                    testset_scores[key].append(v['test'])
            elif isinstance(values,list):
                testset_scores[key]=[v['test'] for v in values]
            else:
                testset_scores[key].append(values['test'])
        if 't1_endwt' in data.keys():
            for em in endwt_measures:
                if em not in endwt.keys():
                    endwt[em]=[]
                endwt[em].append(data['t1_endwt'].item()[em])
        if 'feature_import' in data.keys():
            for key,values in data['feature_import'].item().items():
                if key not in feat_import.keys():
                    feat_import[key]=[]
                if isinstance(values,list): #generated from iterated random forest
                    feat_import[key]=values
                else: #generated from seed - single random forest per file
                    feat_import[key].append(values)
    if 'ca_reg_score' in data.keys(): #only need to check the last file?
        ca_keys=[k for k in data['ca_reg_score'].item().keys() if k.endswith('cal')]
    else:
        ca_keys=[]
    linreg=False
    if 'linreg' in data.keys():
        if np.sum([len(x) for x in data['linreg'].item().values()]):
            linreg=True    
    return testset_scores,endwt,feat_import,ca_keys,linreg

def create_df(pattern,testset_scores,binary_features):
    import os
    rows=[]
    fname=os.path.basename(pattern).split('.')[0]
    for key in testset_scores.keys():
        if key[0].isdigit():
            numbins=int(key[0])
            start_char=2
        else:
            numbins=1
            start_char=0
        ####### separate number of bins from other features used for RF
        bin_feat=np.zeros(len(binary_features))
        if len(key)>1:
            other_feature=key[start_char:]
            #create binary variables indicating whether correlation or spine to soma distance was used
            for ii,feat in enumerate(binary_features):
                if feat in other_feature:
                    bin_feat[ii]=1
        else:
            other_feature='None'
        for score in testset_scores[key]:
            rows.append([fname,numbins,other_feature,score]+[bf for bf in bin_feat])
        testscore_df=pd.DataFrame(rows,columns=['fname','numbins','other_feature','score']+[bf for bf in binary_features])
    return testscore_df

def read_linreg_data(files,newkeys):
    linreg={'train':{k:[] for k in newkeys},'test':{k:[] for k in newkeys},'coef':{k:[] for k in newkeys}}
    for f in files:
        data=np.load(f,allow_pickle=True)
        linreg_score=data['linreg'].item()
        for key,values in linreg_score.items():
            if len(values):
                for v in values:
                    linreg['train'][key].append(v['train'])
                    linreg['test'][key].append(v['test'])
                linreg['coef'][key].append(v['coef'])                   
            elif key in linreg['train']:
                del linreg['train'][key]
                del linreg['test'][key]
                del linreg['coef'][key]
    return linreg

def create_linreg_df(pattern,testset_scores):
    rows=[]
    for key in testset_scores.keys():
        numbins=int(key[0])
        ####### separate number of bins from other features used for RF
        if len(key)>1:
            other_feature=key[2:]
        else:
            other_feature='None'
        for score in testset_scores[key]:
            rows.append([pattern,numbins,other_feature,score])
        score_df=pd.DataFrame(rows,columns=['fname','numbins','other_feature','score'])
    return score_df

def plot_lin_features(binset,good_features,linreg):
    figs=[]
    for numbins in binset:
        f,ax = plt.subplots(1,1)
        for feat_type in [numbins,numbins+'_'+good_features]:
            vals=linreg['coef'][feat_type]
            ax.errorbar(range(np.shape(vals)[1]),np.abs(np.mean(vals,axis=0)),yerr=np.std(vals,axis=0),label=feat_type)
        ax.set_xlabel('time sample')
        ax.set_ylabel('coefficient')
        f.suptitle('Linear Regression Coefficients, abs value')
        ax.legend()
        xticks=feat_import[numbins+'_features'][:-2]+[good_features]
        ax.set_xticks(list(range(len(xticks))))
        ax.set_xticklabels(xticks)
        figs.append(f)
    return figs

def read_careg_data(files,ca_keys):
    careg={'train':{k:[] for k in ca_keys},'test':{k:[] for k in ca_keys}}
    ca_import={k[0]+'import':[] for k in ca_keys}  
    for f in files:
        data=np.load(f,allow_pickle=True)
        careg_score=data['ca_reg_score'].item()
        for key in ca_keys:
            for v in careg_score[key]:
                careg['train'][key].append(v['train'])
                careg['test'][key].append(v['test'])
            import_key=key[0]+'import'
            ca_import[import_key].append(careg_score[import_key])
    return ca_import,careg

def ca_plots(ca_import,careg):
    ca_means=[np.mean(v) for v in careg['test'].values()]
    ca_ste=[np.std(v)/np.sqrt(len(v)-1) for v in careg['test'].values()]
    xvalues=[int(k[0]) for k in careg['test'].keys()]
    f1,ax = plt.subplots(1,1)
    ax.bar(list(np.arange(len(xvalues))),ca_means,yerr=ca_ste) 
    ax.set_ylabel('Prediction score')
    ax.set_xlabel('Calcium time samples')
    ax.set_xticks(list(np.arange(len(xvalues))))
    ax.set_xticklabels(xvalues)
    ylim=ax.get_ylim()
    ax.set_ylim(ylim[0],max(round(1.1*ylim[1],1),round(ylim[1]+0.1,1)))
    f2,ax = plt.subplots(1,1)
    import itertools
    marker = itertools.cycle(( '+', 'o', '*')) 
    for k in ca_import.keys():
        x=range(np.shape(ca_import[k])[1])
        plt.plot(x,np.mean(ca_import[k],axis=0),marker=next(marker),label=k[0])
    ax.set_xlabel('Calcium time sample')
    ax.set_ylabel('feature importance')
    ax.set_xticks(x)
    ax.legend()
    return f1,f2

######################### MAIN #############################

plot_importance=True
do_stats=True
#pattern='/home/avrama/moose/NSGPlas_2022may23/seed*.npz'#'trunc_normal.npz'#'moved.npz'#
pattern='C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\ClusterAnal2022jun23_ran0_220_uni\seed*dW.npz'#'trunc_normal.npz'#'moved.npz'#
pattern2='' #if empty, not used.  otherwise, will read in another dataset and combine
files=glob.glob(pattern)
fnames=['seed0_24.npz','seed24_49.npz','seed49_73.npz','seed73_98.npz','seed98_123.npz']
files=['C:\\Users\\kblackw1\\Documents\\StriatumCRCNS\\SPmodelCalcium\\DormanPlasticity\\ClusterAnal2022jun23_ran0_220_uni\\'+f for f in fnames]
#### Specify some measures and features
endwt_measures=['mean','std','no change']
binary_features=[]#['clust','dist','spines']
label_dict={'None':'Direct','corr':'+Correlation','dist':'+Distance','dist_clust':'+Both','clust':'cluster length','spines':'spine/cluster','spines_clustLen':'cluster Len&Sp'}
order_dict={'None':0,'clust':1,'spines':2,'spines_clustLen':3,'dist':4,'dist_clust':5} #order of features in RF plut
good_features='clust'

#### read feature importance, regression scores and measures of ending synapse weight
testset_scores,endwt,feat_import,ca_keys,linreg=read_data(files,endwt_measures)
testscore_df=create_df(pattern,testset_scores,binary_features)
newkeys=list(testset_scores.keys())

### flatten the ending synapse weight measures if list of lists
## Then create histogram of mean, and std
if len(files)>1:
    flat_endwt={}
    for em in endwt.keys():
        flat_endwt[em]=flatten(endwt[em])
        endwt[em]=flat_endwt[em]
if len(endwt):
    if np.std(endwt['mean'])>0:
        fig=endwt_histogram(endwt)
        print('MEAN WEIGHT=',np.mean(endwt['mean']))
    else:
        print('No histogram - all ending weights identical')
                                                                                                     
######### Plot feature importance values
if plot_importance:
    figs=importance_plot(feat_import,testset_scores)
    if 'dW' in feat_import.keys():
        axes=figs[0].axes
        vals=feat_import['dW']
        score=round(np.mean(testset_scores['dW']),3)
        axes[0].errorbar(range(np.shape(vals)[1]),np.mean(vals,axis=0),yerr=np.std(vals,axis=0),label='dW, mean score='+str(score))
        axes[0].legend()

######### linear regresion
if linreg:
    linreg=read_linreg_data(files,newkeys)
    binset=list(set([nk[0] for nk in newkeys])) 
    for regtype in ['test','train']:
        lin_test_df=create_linreg_df(pattern.split('.')[0]+regtype,linreg[regtype])
        means,stderr=create_barplot_means(lin_test_df)
        print('linear regresion', means)
        figlin=bar_plot_mean_score(means,np.unique(lin_test_df.numbins),stderr,'linear Regression: '+regtype)
    print('coef',np.mean(linreg['coef'][binset[-1]],axis=0),'\nadj',np.mean(linreg['coef'][binset[-1]+'_'+good_features],axis=0))
    flinfeat=plot_lin_features(binset,good_features,linreg)

############ Calcium RF
if len(ca_keys):
    ca_import,careg=read_careg_data(files,ca_keys)
    fca1,fca2=ca_plots(ca_import,careg)

########### Possibly read second set of data #################
if len(pattern2):
    files=glob.glob(pattern2)
    feat_import={k:[] for k in newkeys}
    testset_scores={k:[] for k in newkeys} #reinitialize testset_scores
    endwt={k:[] for k in endwt_measures}
    read_data(files,testset_scores,endwt_measures,feat_import) #ignore endwt and feat_import (for now)
    testscore2_df=create_df(pattern2,testset_scores)
    testscore_df= pd.concat([testscore_df,testscore2_df])

############ Create dataframes with subsets of data for bar plots ##############      
#create dataframe to test whether using adjacent bins helps
if len(binary_features):
    test_adj_df=testscore_df.loc[(testscore_df[binary_features[0]]==0)&(testscore_df[binary_features[1]]==0)]
    means,stderr=create_barplot_means(test_adj_df)
    figadj=bar_plot_mean_score(means,np.unique(test_adj_df.numbins),stderr,pattern.split('.')[0])

#create dataframe for testing other features in 3 way ANOVA
test_features=testscore_df[(testscore_df.other_feature != 'adj')]
single_features=test_features[(test_features.other_feature != 'dist_clust') & (test_features.other_feature != 'spines_clustLen')]

if len(np.unique(test_features.other_feature))>1:
    means,stderr=create_barplot_means(test_features)
    if list(means.keys())[0] in order_dict:
        means=  {k: v for k, v in sorted(means.items(), key=lambda item: order_dict[item[0]])}
    figfeat=bar_plot_mean_score(means,np.unique(test_features.numbins),stderr,'')
'''
ax=figfeat.axes
ax[0].set_ylabel('prediction score', fontsize=14)
ax[0].set_xlabel('Time bins', fontsize=14)
ax[0].tick_params(axis='x', labelsize=14 )
ax[0].tick_params(axis='y', labelsize=14 )
ax[0].set_ylim([0,0.7])
'''
if len(single_features) != len(test_features):
    means,stderr=create_barplot_means(single_features)
    if list(means.keys())[0] in order_dict:
        means=  {k: v for k, v in sorted(means.items(), key=lambda item: order_dict[item[0]])}
    bar_plot_mean_score(means,np.unique(single_features.numbins),stderr,pattern.split('.')[0])

###### Statistical analysis ############
if do_stats:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    import scikit_posthocs as sp

    ############# ANOVA to assess number of bins and othe features
    base_model='score ~ C(numbins)'
    if len(pattern2):
        base_model+='+C(fname)'

    print('############## All Data, OTHER FEATURE ############### ')
    model=ols(base_model+'+C(other_feature)',data=testscore_df).fit()
    anova2way = sm.stats.anova_lm(model)
    print(anova2way)
    print(model.summary())

    print('## All Data - number of bins only ### ')
    model=ols(base_model,data=testscore_df).fit()
    print(model.summary())

    if not len(pattern2):
        print('post-hoc on numbins\n', sp.posthoc_ttest(testscore_df, val_col='score', group_col='numbins', p_adjust='holm'))
    
    if len(binary_features):
        print('\n############## Does adjacent help? No. Compare adjacent to numbins only ############### ')
        #two-way ANOVA - does firing rate of adjacent spines help?
        model=ols(base_model+'+C(other_feature)',data=test_adj_df).fit()
        anova2way = sm.stats.anova_lm(model)
        print(anova2way)

        print('\n### cluster info and spine distance? exclude adjacent from this data set ##### ')
        #three-way ANOVA- does cluster info or spine distance from soma help?
        model=ols(base_model+'+'+binary_features[0]+'+'+binary_features[1]+'+'+binary_features[2],data=test_features).fit()
        anova2way = sm.stats.anova_lm(model)
        print(anova2way)
        print(model.summary())
    '''
    model=ols(base_model+'+C(other_feature)',data=test_features).fit()
    anova2way = sm.stats.anova_lm(model)
    print(anova2way)
    print(model.summary())
    print('post-hoc on clust,dist\n', sp.posthoc_ttest(test_features, val_col='score', group_col='other_feature', p_adjust='holm'))
    #ANCOVA - WORSE MODEL
    ancova=ols('score ~ numbins+C(other_feature)',data=testscore_df).fit()
    print(ancova.summary())
    '''
    if 'dist' in test_features.columns:
        cluster_features=test_features[(test_features.dist == 0.0)]

        model=ols(base_model+'+C(other_feature)',data=cluster_features).fit()
        anova2way = sm.stats.anova_lm(model)
        print(anova2way)
        print(model.summary())
        print('post-hoc on clust,dist\n', sp.posthoc_ttest(cluster_features, val_col='score', group_col='other_feature', p_adjust='holm'))


