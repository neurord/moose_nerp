import numpy as np
import sys
import pandas as pd
import glob

args=['D1_short_patch_187463_D1_108_ab_s2sdist', 'D1Pat4BLA_DLS']
#args = sys.argv[1:]
sp2sp_file=args[0] #s2s distance file
input_spine=args[1] #root name of stimulated spine files,with single num dispersed and num clustered

sp2sp=np.load(sp2sp_file+'.npz',allow_pickle=True)
spines=sp2sp['index'].item()
spine_list=[s.replace('[0]','') for s in spines.keys()]
sp2sp_dist=sp2sp['s2sd']

files=glob.glob(input_spine+'*.npz')
mean_dist=[]
for fn in files:
    num_disp=int(fn.split('_')[2])
    num_clust=int(fn.split('_')[3])
    seed=fn.split('_')[-1].split('.npz')[0]
    inputs=np.load(fn,allow_pickle=True)
    clust_spines=[i.replace('[0]','') for i in inputs['orig']]
    disp_spines=[i.replace('[0]','') for i in inputs['extra']]

    distance_list=[]
    for ds in disp_spines:
        for cs in clust_spines:
            ds_index=spine_list.index(ds)
            cs_index=spine_list.index(cs)
            ds2cs_dist=sp2sp_dist[ds_index,cs_index]
            distance_list.append({'disp':ds,'clust':cs,'dist':ds2cs_dist})
    df=pd.DataFrame.from_dict(distance_list)
    mean_dist.append({'seed':seed,'num_disp':num_disp,'num_clust':num_clust,'mean_dist':df['dist'].mean()})
mean_df=pd.DataFrame.from_dict(mean_dist)
print(mean_df) #write this to file?  include seed?

import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
#
print(mean_df.groupby(['num_disp','num_clust']).mean()[['mean_dist']])
results=ols('mean_dist ~ C(num_disp)',data=mean_df).fit()
table=sm.stats.anova_lm(results,typ=2) #coefficients
print(results.summary()) #overall anova result


