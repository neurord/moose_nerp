import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
#import scikit_posthocs as sp
import pandas as pd
import glob

filenames=glob.glob('*.out')


data=[]
for fn in filenames:
    data.append(pd.read_csv(fn,sep='\s+'))
#concatenate multiple files of data
alldata = pd.concat(data,ignore_index=True)
if not 'spc' in alldata.columns:
    alldata['spc']=6    
#eliminate duplicates
alldata.drop_duplicates()

#mean of all columns that are values:
alldata.mean(numeric_only=True)
alldata.std(numeric_only=True)

#means of different groups
#1. how to create subsets of data or exclude rows
#nodrug=alldata[alldata.drug=='none']
print(alldata.groupby(['region','ndisp','nclust','naf','spc']).mean()[['plateauVm','decay10','num_spk','inst_freq','duration']])

no_naf=alldata[(alldata.naf==0)]
dms=alldata[(alldata.region=='DMS') & (alldata.naf==0)]
dls=alldata[(alldata.region=='DLS') & (alldata.naf==0)]
dms_naf=alldata[(alldata.region=='DMS') & (alldata.naf==1)]
dls_naf=alldata[(alldata.region=='DLS') & (alldata.naf==1)]

'''
#D1Rtest=pd.concat([d1test,DLmales]) #example of concatenation

#stats on grouped data
grouped_data=nodrug_theta10.groupby(['sex'])
print('group means', grouped_data.mean()[['PSmean1','PSmean2']], grouped_data.std()[['PSmean1','PSmean2']], grouped_data.count()['PSmean1'])
'''
#2.how to do ANOVA
for dat in [dms,dls]:
    if len(dat):
        for depvar in ['plateauVm','decay10']:
            results=ols(depvar+' ~ C(nclust)',data=dat).fit()
            table=sm.stats.anova_lm(results,typ=2) #coefficients
            print('\n*** depvar=',depvar, 'region=',dat.region[dat.index[0]],'dispersed=',dat.ndisp[dat.index[0]],'********\n',table)
            indep_var=list(table['PR(>F)'].keys())[0]
            if table['PR(>F)'][indep_var]<0.05:
                print(results.summary()) #overall anova result

for dat in [dms_naf,dls_naf]:
    if len(dat):
        for depvar in ['num_spk', 'inst_freq']:
            results=ols(depvar+' ~ C(nclust)',data=dat).fit()
            table=sm.stats.anova_lm(results,typ=2) #coefficients
            print('\n*** depvar=',depvar, 'region=',dat.region[dat.index[0]], 'dispersed=',dat.ndisp[dat.index[0]],'********\n',table)
            indep_var=list(table['PR(>F)'].keys())[0]
            if table['PR(>F)'][indep_var]<0.05:
                print(results.summary()) #overall anova result

#print('post-hoc on sex\n', sp.posthoc_ttest(nodrug_theta10, val_col='PSmean1', group_col='sex', p_adjust='holm'))

#2way anova with interaction term
##### Cannot do post-hoc tests for 2 way anova in python
'''for depvar in ['plateauVm','decay10']:
    results=ols(depvar+' ~ C(region)*nclust',data=no_naf).fit()
    table=sm.stats.anova_lm(results,typ=2) #coefficients
    print(table)
    #if table['PR(>F)']['nclust']<0.05:
    print(results.summary()) #overall anova result

'''