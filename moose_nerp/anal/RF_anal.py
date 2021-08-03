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

def bar_plot_mean_score(data_set,xvalues,stderr_set,title):
    ########### Plot regression scores #######            
    width=1/(len(data_set)+1)
    colors = plt.cm.magma([int(i*(len(plt.cm.magma.colors)/len(data_set))) for i in range(len(data_set))])
    fig,ax=plt.subplots(1,1)
    for i,(k,data) in enumerate(data_set.items()):
        offset=i*width
        plt.bar(np.arange(len(data))+offset,data,yerr=stderr_set[k],label=k,width=width,color=colors[i])
    ax.set_ylabel('prediction score')
    ax.set_xlabel('')
    fig.suptitle(title)
    ax.set_xticks(list(range(len(xvalues))))
    ax.set_xticklabels(xvalues)
    if len(data_set)>1:
        ax.legend()
    
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

def importance_plot(feat_import):
    bin_set=[k[0] for k in feat_import.keys()]
    feature_types=[k[1:] for k in feat_import.keys() if not k.endswith('features')]
    for numbins in np.unique(bin_set):
        f,ax = plt.subplots(1,1)
        for feat_type in np.unique(feature_types):
            key=numbins+feat_type
            vals=feat_import[key]
            score=round(np.mean(testset_scores[key]),3)
            #if isinstance(feat_import[key],np.ndarray):
            ax.errorbar(range(np.shape(vals)[1]),np.mean(vals,axis=0),yerr=np.std(vals,axis=0),label=key+', mean score='+str(score))
        ax.set_xlabel('feature name')
        ax.set_ylabel('feature importance')
        ax.legend()
        xticks=feat_import[numbins+'_features']
        ax.set_xticks(list(range(len(xticks))))
        ax.set_xticklabels(xticks)

def read_data(files,testset_scores,endwt_measures,feat_import):        
    for f in files:
        data=np.load(f,allow_pickle=True)
        for key,values in data['reg_score'].item().items():
            if isinstance(values,list): #generated from leave_one_out
                testset_scores[key]=[v['test'] for v in values]
            else:
                testset_scores[key].append(values['test'])
        for em in endwt_measures:
            endwt[em].append(data['t1_endwt'].item()[em])
        for key,values in data['feature_import'].item().items():
            if isinstance(values,list): #generated from iterated random forest
                feat_import[key]=values
            else: #generated from seed - single random forest per file
                feat_import[key].append(values)
    return #testset_scores,endwt_measures,feat_import

def create_df(pattern,testset_scores):
    rows=[]
    fname=pattern.split('.')[0]
    for key in testset_scores.keys():
        numbins=int(key[0])
        ####### separate number of bins from other features used for RF
        if len(key)>1:
            other_feature=key[2:]
            #create binary variables indicating whether correlation or spine to soma distance was used
            if 'corr' in other_feature:
                corr=1
            else:
                corr=0
            if 'dist' in other_feature:
                dist=1
            else:
                dist=0
        else:
            other_feature='None'
            corr=0
            dist=0
        for score in testset_scores[key]:
            rows.append([fname,numbins,other_feature,score,corr,dist])
        testscore_df=pd.DataFrame(rows,columns=['fname','numbins','other_feature','score','correl','dist'])
    return testscore_df

######################### MAIN #############################

plot_importance=False
pattern='seed*.npz'#'trunc_normal.npz'#'moved.npz'#
pattern2='' #if empty, not used.  otherwise, will read in another dataset and combine
files=glob.glob(pattern)

####  read in the regression scores for one file to determine random forets variations ##
newkeys=[]
data=np.load(files[0],allow_pickle=True)
for k in data['reg_score'].item().keys():
    newkeys.append(k)
data.close()

#### Initialize dictionaries for holding data
testset_scores={k:[] for k in newkeys}
feat_import={k:[] for k in newkeys}
endwt_measures=['mean','std','no change']
endwt={k:[] for k in endwt_measures}

#### read feature importance, regression scores and measures of ending synapse weight
read_data(files,testset_scores,endwt_measures,feat_import)
testscore_df=create_df(pattern,testset_scores)
### flatten the ending synapse weight measures if list of lists
## Then create histogram of mean, and std
if len(files)>1:
    flat_endwt={}
    for em in endwt.keys():
        flat_endwt[em]=flatten(endwt[em])
        endwt[em]=flat_endwt[em]
if np.std(endwt['mean'])>0:
    endwt_histogram(endwt)
else:
    print('No histogram - all ending weights identical')
                                                                                                     
######### Plot feature importance values
if plot_importance:
    importance_plot(feat_import)

########### RECODE DATA #################
if len(pattern2):
    files=glob.glob(pattern2)
    feat_import={k:[] for k in newkeys}
    testset_scores={k:[] for k in newkeys} #reinitialize testset_scores
    endwt={k:[] for k in endwt_measures}
    read_data(files,testset_scores,endwt_measures,feat_import) #ignore endwt and feat_import (for now)
    testscore2_df=create_df(pattern2,testset_scores)
    testscore_df= pd.concat([testscore_df,testscore2_df])

#Create dataframe with all data        
#create dataframe for testing correlation and spine distance in 3way ANOVA
test_adj_df=testscore_df.loc[(testscore_df.correl==0)&(testscore_df.dist==0)]
#create dataframe to test whether using adjacent bins helps
test_corr_dist=testscore_df[(testscore_df.other_feature != 'adj')]

means,stderr=create_barplot_means(test_adj_df)
bar_plot_mean_score(means,np.unique(test_adj_df.numbins),stderr,pattern.split('.')[0])

means,stderr=create_barplot_means(test_corr_dist)
bar_plot_mean_score(means,np.unique(test_corr_dist.numbins),stderr,pattern.split('.')[0])

###### Statistical analysis ############
import statsmodels.api as sm
from statsmodels.formula.api import ols
import scikit_posthocs as sp

############# ANOVA to assess number of bins and othe features
base_model='score ~ C(numbins)'
if len(pattern2):
    base_model+='+C(fname)'

print('############## All Data, use spatial ############### ')
model=ols(base_model+'+C(other_feature)',data=testscore_df).fit()
anova2way = sm.stats.anova_lm(model)
print(anova2way)
print(model.summary())

print('## All Data - no spatial  ### ')
model=ols(base_model,data=testscore_df).fit()
print(model.summary())

if not len(pattern2):
    print('post-hoc on numbins\n', sp.posthoc_ttest(testscore_df, val_col='score', group_col='numbins', p_adjust='holm'))

print('\n############## Does adjacent help? No.  Compare adjacent to numbins only ############### ')
#two-way ANOVA - does firing rate of adjacent spines help?
model=ols(base_model+'+C(other_feature)',data=test_adj_df).fit()
anova2way = sm.stats.anova_lm(model)
print(anova2way)

print('### correlation and spine distance? exclude adjacent from this data set ##### ')
#three-way ANOVA- does correlation to adjacent spines or spine distance from soma help?
model=ols(base_model+'+correl+dist',data=test_corr_dist).fit()
anova2way = sm.stats.anova_lm(model)
print(anova2way)
print(model.summary())


print('\n############ Exclude 3 & 5 bin data ################')
bins2df=testscore_df.loc[(testscore_df.numbins<=2) & (testscore_df.other_feature !='adj')]
model=ols(base_model+'+C(other_feature)',data=bins2df).fit()
anova1way = sm.stats.anova_lm(model)
print(anova1way)
print(model.summary())

######## Only by using corr_dist with numbins=1 and 2 can we see that it helps.  Possibly using more trials (10 isntead of 4) would help
## Alternatively, combining moved and trunc_normal, then using numbins<5 shows the having neither corr nor dist is worse, though

#ANCOVA - WORSE MODEL
#ancova=ols('score ~ numbins+C(other_feature)',data=testscore_df).fit()
#print(ancova.summary())
'''
############################## MOVED #########################################
## All Data - no spatial  ### 
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                  score   R-squared:                       0.717
Model:                            OLS   Adj. R-squared:                  0.705
Method:                 Least Squares   F-statistic:                     64.03
Date:                Mon, 05 Jul 2021   Prob (F-statistic):           9.37e-21
Time:                        17:16:49   Log-Likelihood:                 143.99
No. Observations:                  80   AIC:                            -280.0
Df Residuals:                      76   BIC:                            -270.5
Df Model:                           3                                         
Covariance Type:            nonrobust                                         
===================================================================================
                      coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------
Intercept           0.3338      0.009     36.376      0.000       0.316       0.352
C(numbins)[T.2]     0.1159      0.013      8.930      0.000       0.090       0.142
C(numbins)[T.3]     0.1477      0.013     11.377      0.000       0.122       0.174
C(numbins)[T.5]     0.1618      0.013     12.464      0.000       0.136       0.188
==============================================================================
               1             2             3             5
1 -1.000000e+00  8.333459e-09  1.068438e-11  3.930669e-13
2  8.333459e-09 -1.000000e+00  2.043441e-02  6.558619e-04
3  1.068438e-11  2.043441e-02 -1.000000e+00  1.982853e-01
5  3.930669e-13  6.558619e-04  1.982853e-01 -1.000000e+00
############ Exclude 3 & 5 bin data ################
                    df    sum_sq   mean_sq          F        PR(>F)
C(numbins)         1.0  0.103144  0.103144  91.846572  3.507413e-10
C(other_feature)   3.0  0.025488  0.008496   7.565289  7.927936e-04
Residual          27.0  0.030321  0.001123        NaN           NaN
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                  score   R-squared:                       0.809
Model:                            OLS   Adj. R-squared:                  0.781
Method:                 Least Squares   F-statistic:                     28.64
Date:                Mon, 05 Jul 2021   Prob (F-statistic):           2.31e-09
Time:                        17:16:50   Log-Likelihood:                 65.980
No. Observations:                  32   AIC:                            -122.0
Df Residuals:                      27   BIC:                            -114.6
Df Model:                           4                                         
Covariance Type:            nonrobust                                         
=================================================================================================
                                    coef    std err          t      P>|t|      [0.025      0.975]
-------------------------------------------------------------------------------------------------
Intercept                         0.3014      0.013     22.757      0.000       0.274       0.329
C(numbins)[T.2]                   0.1135      0.012      9.584      0.000       0.089       0.138
C(other_feature)[T.corr]          0.0646      0.017      3.854      0.001       0.030       0.099
C(other_feature)[T.corr_dist]     0.0728      0.017      4.342      0.000       0.038       0.107
C(other_feature)[T.dist]          0.0423      0.017      2.526      0.018       0.008       0.077
==============================================================================
############################## Trunc Normal #########################################
## All Data - no spatial  ### 
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                  score   R-squared:                       0.159
Model:                            OLS   Adj. R-squared:                  0.125
Method:                 Least Squares   F-statistic:                     4.776
Date:                Mon, 05 Jul 2021   Prob (F-statistic):            0.00420
Time:                        17:20:36   Log-Likelihood:                 118.76
No. Observations:                  80   AIC:                            -229.5
Df Residuals:                      76   BIC:                            -220.0
Df Model:                           3                                         
Covariance Type:            nonrobust                                         
===================================================================================
                      coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------
Intercept           0.5438      0.013     43.232      0.000       0.519       0.569
C(numbins)[T.2]     0.0285      0.018      1.603      0.113      -0.007       0.064
C(numbins)[T.3]     0.0533      0.018      2.995      0.004       0.018       0.089
C(numbins)[T.5]     0.0608      0.018      3.420      0.001       0.025       0.096
==============================================================================

           1         2         3         5
1 -1.000000  0.324404  0.037331  0.003758
2  0.324404 -1.000000  0.407154  0.238963
3  0.037331  0.407154 -1.000000  0.680881
5  0.003758  0.238963  0.680881 -1.000000

############ Exclude 3 & 5 bin data ################
                    df    sum_sq   mean_sq        F    PR(>F)
C(numbins)         1.0  0.008406  0.008406  2.96206  0.096681
C(other_feature)   3.0  0.019964  0.006655  2.34480  0.095215
Residual          27.0  0.076627  0.002838      NaN       NaN
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                  score   R-squared:                       0.270
Model:                            OLS   Adj. R-squared:                  0.162
Method:                 Least Squares   F-statistic:                     2.499
Date:                Mon, 05 Jul 2021   Prob (F-statistic):             0.0661
Time:                        17:20:36   Log-Likelihood:                 51.147
No. Observations:                  32   AIC:                            -92.29
Df Residuals:                      27   BIC:                            -84.96
Df Model:                           4                                         
Covariance Type:            nonrobust                                         
=================================================================================================
                                    coef    std err          t      P>|t|      [0.025      0.975]
-------------------------------------------------------------------------------------------------
Intercept                         0.5027      0.021     23.874      0.000       0.460       0.546
C(numbins)[T.2]                   0.0324      0.019      1.721      0.097      -0.006       0.071
C(other_feature)[T.corr]          0.0578      0.027      2.172      0.039       0.003       0.113
C(other_feature)[T.corr_dist]     0.0609      0.027      2.288      0.030       0.006       0.116
C(other_feature)[T.dist]          0.0532      0.027      1.997      0.056      -0.001       0.108
==============================================================================
############################## SEED #########################################
## All Data - no spatial  ### 
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                  score   R-squared:                       0.643
Model:                            OLS   Adj. R-squared:                  0.637
Method:                 Least Squares   F-statistic:                     105.7
Date:                Mon, 05 Jul 2021   Prob (F-statistic):           3.64e-39
Time:                        17:24:01   Log-Likelihood:                 299.85
No. Observations:                 180   AIC:                            -591.7
Df Residuals:                     176   BIC:                            -578.9
Df Model:                           3                                         
Covariance Type:            nonrobust                                         
===================================================================================
                      coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------
Intercept           0.4971      0.007     72.085      0.000       0.483       0.511
C(numbins)[T.2]     0.0857      0.010      8.784      0.000       0.066       0.105
C(numbins)[T.3]     0.1440      0.010     14.767      0.000       0.125       0.163
C(numbins)[T.5]     0.1547      0.010     15.867      0.000       0.135       0.174
==============================================================================
Omnibus:                       15.218   Durbin-Watson:                   2.160
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               18.916
Skew:                          -0.575   Prob(JB):                     7.81e-05
Kurtosis:                       4.096   Cond. No.                         4.79
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
post-hoc on numbins
               1             2             3             5
1 -1.000000e+00  1.724761e-10  1.374565e-21  1.458202e-25
2  1.724761e-10 -1.000000e+00  2.608377e-08  3.580171e-12
3  1.374565e-21  2.608377e-08 -1.000000e+00  1.637668e-01
5  1.458202e-25  3.580171e-12  1.637668e-01 -1.000000e+00
### correlation and spine distance? exclude adjacent from this data set ##### 
               df    sum_sq   mean_sq          F        PR(>F)
C(numbins)    3.0  0.549381  0.183127  98.006199  4.944268e-34
correl        1.0  0.010112  0.010112   5.411572  2.146023e-02
dist          1.0  0.003564  0.003564   1.907590  1.694636e-01
Residual    138.0  0.257857  0.001869        NaN           NaN
                            OLS Regression Results                            
==============================================================================
Dep. Variable:                  score   R-squared:                       0.686
Model:                            OLS   Adj. R-squared:                  0.675
Method:                 Least Squares   F-statistic:                     60.27
Date:                Mon, 05 Jul 2021   Prob (F-statistic):           5.05e-33
Time:                        17:26:44   Log-Likelihood:                 251.08
No. Observations:                 144   AIC:                            -490.2
Df Residuals:                     138   BIC:                            -472.4
Df Model:                           5                                         
Covariance Type:            nonrobust                                         
===================================================================================
                      coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------
Intercept           0.5067      0.009     57.426      0.000       0.489       0.524
C(numbins)[T.2]     0.0832      0.010      8.163      0.000       0.063       0.103
C(numbins)[T.3]     0.1435      0.010     14.080      0.000       0.123       0.164
C(numbins)[T.5]     0.1562      0.010     15.334      0.000       0.136       0.176
correl             -0.0168      0.007     -2.326      0.021      -0.031      -0.003
dist               -0.0100      0.007     -1.381      0.169      -0.024       0.004
==============================================================================
Omnibus:                       23.341   Durbin-Watson:                   2.308
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               35.143
Skew:                          -0.839   Prob(JB):                     2.34e-08
Kurtosis:                       4.745   Cond. No.                         5.91
==============================================================================
'''