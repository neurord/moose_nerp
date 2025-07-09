import numpy as np
import sys
import pandas as pd
import glob
import os

args=['D1_long_matrix_84362_D1_15_ab_s2sdist', 'D1Mat2BLA_D?S_0_32']  
#args=['D1_short_patch_187463_D1_108_ab_s2sdist', 'D1Pat4BLA_D?S_4_10'] 
#args=['D1_short_patch_187463_D1_108_ab_s2sdist', './D1Pat4BLA_'] #'clustered_exp50/patch4_Rm5_Ra0.34_disp/D1Pat4BLA_'] #
#args = sys.argv[1:]
sp2sp_file=args[0] #s2s distance file
input_spine=args[1] #root name of stimulated spine files,with single num dispersed and num clustered

sp2sp=np.load(sp2sp_file+'.npz',allow_pickle=True)
spines=sp2sp['index'].item()
spine_list=[s.replace('[0]','') for s in spines.keys()]
sp2sp_dist=sp2sp['s2sd']

files=glob.glob(input_spine+'*.npz')
#files=['D1Pat4BLA_DLS_4_10_4_2717.npz']
mean_dist=[];disp=[]; clust=[]
for fn in files:
    base_fn=os.path.basename(fn)
    print('spines for file:', base_fn)
    num_disp=int(base_fn.split('_')[2])
    num_clust=int(base_fn.split('_')[3])
    region=base_fn.split('_')[1]
    seed=base_fn.split('_')[-1].split('.npz')[0]
    inputs=np.load(fn,allow_pickle=True)
    clust_spines=[i.replace('[0]','') for i in inputs['orig']]
    disp_spines=[i.replace('[0]','') for i in inputs['extra']]
    disp.append(num_disp)
    clust.append(num_clust)

    distance_list=[]
    for ds in disp_spines: #additional spines, either dispersed or clustered
        ds_index=spine_list.index(ds)
        dist_dict={}
        for cs in clust_spines:
            cs_index=spine_list.index(cs)
            dist_dict[cs]=sp2sp_dist[ds_index,cs_index]
        min_key=min(dist_dict, key=dist_dict.get)
        print('ds=',ds,', closest=',min_key,', dist2clust=',dist_dict[min_key],', dist2soma=',sp2sp_dist[ds_index,-1])
        distance_list.append({'disp':ds,'closest_clust':min_key,'dist2clust':dist_dict[min_key], 'dist2soma':sp2sp_dist[ds_index,-1]})
    df=pd.DataFrame.from_dict(distance_list)
    mean_dist.append({'region':region,'num_disp':num_disp,'num_clust':num_clust,'seed':seed,'spine_dist':df['dist2clust'].mean(),
                      'spine_dist_sd':df['dist2clust'].std(),'soma_dist':df['dist2soma'].mean(),'soma_dist_sd':df['dist2soma'].mean(),
                      'max_clust_dist':df['dist2clust'].max(),'min_clust_dist':df['dist2clust'].min(),
                      'max_soma_dist':df['dist2soma'].max(),'min_soma_dist':df['dist2soma'].min()})
    fdisp=np.unique(disp)
    fclust=np.unique(clust)
mean_df=pd.DataFrame.from_dict(mean_dist)
print(mean_df) 
from datetime import datetime
outfname=input_spine+'disp'+str(fdisp[0])+'_clust'+str(fclust[0])+'_'+datetime.today().strftime('%Y-%m-%d')
mean_df.to_csv(outfname+'_distance.csv')

import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
#
groups=mean_df.groupby(['num_disp','num_clust','region'])[['spine_dist','soma_dist']]
print('MEAN:\n',groups.mean(),'\nSEM:\n',groups.sem()) #write this to file, combine with clustered?
results=ols('spine_dist ~ C(region)',data=mean_df).fit()
print(results.summary()) #overall anova result
table=sm.stats.anova_lm(results,typ=2) #coefficients

results=ols('soma_dist ~ C(region)',data=mean_df).fit()
print(results.summary()) #overall anova result
table=sm.stats.anova_lm(results,typ=2) #coefficients

