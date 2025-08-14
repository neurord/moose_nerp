import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
#import scikit_posthocs as sp
import pandas as pd
import glob

spc=4
filenames=glob.glob('clustered_exp50/patch4_Rm5_Ra0.34_2025*2nd_submit/D1Pat4BLA_DLS_0*.out') #FIXME: read in subset of .out files

data=[]
for fn in filenames:
    data.append(pd.read_csv(fn,sep='\s+'))
#concatenate multiple files of data
alldata = pd.concat(data,ignore_index=True)
#eliminate duplicates
alldata.drop_duplicates()

#mean of all columns that are values:
alldata.mean(numeric_only=True)
alldata.std(numeric_only=True)

#means of different groups
#1. how to create subsets of data or exclude rows
#nodrug=alldata[alldata.drug=='none']
print(alldata.groupby(['region','num_disp','num_clust','naf','spc']).mean()[['plateauVm','decay10','num_spk','inst_freq','duration']])

no_naf=alldata[(alldata.naf==0)]
dms=alldata[(alldata.region=='DMS') & (alldata.naf==0)]
dls=alldata[(alldata.region=='DLS') & (alldata.naf==0)]
for df in [no_naf,dms,dls]:
    df.drop(axis=1,columns=['num_spk','inst_freq','duration'],inplace=True)
dms_naf=alldata[(alldata.region=='DMS') & (alldata.naf==1)]
dls_naf=alldata[(alldata.region=='DLS') & (alldata.naf==1)]

'''
#D1Rtest=pd.concat([d1test,DLmales]) #example of concatenation

#stats on grouped data
grouped_data=nodrug_theta10.groupby(['sex'])
print('group means', grouped_data.mean()[['PSmean1','PSmean2']], grouped_data.std()[['PSmean1','PSmean2']], grouped_data.count()['PSmean1'])
'''
#2.how to do ANOVA
print('\n######################################### Simulations with NaF blocked, maximum spines per compartment = ',spc, '########################################')
opposite={'num_disp':'num_clust', 'num_clust':'num_disp'}
for dat,region in zip([dms,dls],['DMS','DLS']):
    if len(dat):
        for indep in ['num_disp','num_clust']:
            exclude=opposite[indep]
            dfsubset=dat[(dat[exclude]==dat[exclude].min())] 
            if len(np.unique(dfsubset[indep]))>1:           
                print('\n********************************* analying ',region, 'for',indep,'*********************************\n')
                for depvar in ['plateauVm','decay10']:
                    results=ols(depvar+' ~ C('+indep+')',data=dfsubset).fit()
                    table=sm.stats.anova_lm(results,typ=2) #coefficients
                    print('\n*** depvar=',depvar, ',',exclude,'=',dfsubset[exclude][dfsubset.index[0]],'\n',table)
                    indep_var=list(table['PR(>F)'].keys())[0]
                    if table['PR(>F)'][indep_var]<0.05:
                        print(results.summary()) #overall anova result

print('\n######################################## Simulations with NaF, maximum spines per compartment = ',spc, '########################################')
for dat,region in zip([dms_naf,dls_naf],['DMS','DLS']):
    if len(dat):
       for indep in ['num_disp','num_clust']:
            exclude=opposite[indep]
            dfsubset=dat[(dat[exclude]==dat[exclude].min())] 
            if len(np.unique(dfsubset[indep]))>1:           
                print('\n********************************* analying ',region, 'for',indep,'*********************************\n')
                for depvar in ['num_spk', 'inst_freq']:
                    results=ols(depvar+' ~ C('+indep+')',data=dfsubset).fit()
                    table=sm.stats.anova_lm(results,typ=2) #coefficients
                    print('\n*** depvar=',depvar, ',',exclude,'=',dfsubset[exclude][dfsubset.index[0]],'********\n',table)
                    indep_var=list(table['PR(>F)'].keys())[0]
                    if table['PR(>F)'][indep_var]<0.05:
                        print(results.summary()) #overall anova result

print('\n########################################## two way ANOVA ###################################')
#2way anova with interaction term
model=ols('decay10 ~ num_clust+C(region)+num_clust*C(region)',data=no_naf).fit()
table=sm.stats.anova_lm(model,typ=2) #coefficients
print(table,'\n',model.summary())
##### Cannot do post-hoc tests for 2 way anova in python

################# Paired data #######################
dfs=[]
for nclust in no_naf['num_clust'].unique():
    dfs.append(no_naf[(no_naf.num_clust==nclust)])
paired_df=pd.merge(dfs[0],dfs[1],how='left',on=['seed','region','num_disp', 'maxdist','naf','spc'])
paired_df['delta_decay']=paired_df['decay10_x']-paired_df['decay10_y']
paired_df['add_inputs']=paired_df['num_clust_x']-paired_df['num_clust_y']
paired_df['delta_plateau']=paired_df['plateauVm_x']-paired_df['plateauVm_y']

print('\n########################################## paired ###################################')
model=ols('delta_decay ~ C(region)',data=paired_df).fit()
table=sm.stats.anova_lm(model,typ=2) #coefficients
print(table,'\n',model.summary())

print(paired_df.groupby(['region','add_inputs','naf','spc']).mean()[['delta_plateau','delta_decay']])
#
#print('post-hoc on sex\n', sp.posthoc_ttest(nodrug_theta10, val_col='PSmean1', group_col='sex', p_adjust='holm'))
