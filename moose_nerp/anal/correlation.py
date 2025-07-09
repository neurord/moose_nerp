###################### Correlation between plateau and distance ################
## this reads in the output of 
#       (1) anal/BLA_anal.py  - .out file
#       (2) anal/dispersed_dist.py - distance.csv file
import pandas as pd
from scipy.stats import pearsonr
import glob
import sys

def calc_corr(dfsub,region):
    pvalues={r:{} for r in dfsub.columns if not r.endswith('_sd')}
    for i,r in enumerate(dfsub.columns[1:]):
        for c in dfsub.columns[i+1:]:
            #print(i, r,c)
            corr=pearsonr(dfsub[r],dfsub[c])
            pvalues[r][c]=(round(corr[0],4),round(corr[1],5))

    print ('region=',region,list(pvalues.keys())[1:])
    for i,r in enumerate(list(pvalues.keys())[1:]):
        print(r,[('...','...') for j in range(i)],end="")
        for c in pvalues[r].keys():
            print(pvalues[r][c],end="")
        print('\n')
    for i,r in enumerate(list(pvalues.keys())[1:]):
        for c in pvalues[r].keys():
            if pvalues[r][c][1]<0.05 and pvalues[r][c][0]<1.0:
                print(r,c,pvalues[r][c])
    return pvalues

def plots(combined,region=False):
    from matplotlib import pyplot as plt
    def plot_traces(data,axes,color=None,region=''):
        for ax,yvarl in zip(axes,['plateauVm','decay10']):
            ax.plot(data['soma_dist'].to_numpy()*1e6, data[yvarl].to_numpy(),'*',color=color,label='soma'+' '+region)
            ax.plot(data['spine_dist'].to_numpy()*1e6, data[yvarl].to_numpy(),'.',color=color,label='cluster'+' '+region)
            ax.set_ylabel(yvarl)
        return

    fig,axes=plt.subplots(2,1,sharex=True)
    axes=fig.axes
    if region:
        for reg,col in zip(combined.region.unique(),['r','k']): #NOTE will not generalized to more than 2 regions
            data=combined[combined['region']==reg]
            plot_traces(data,axes,color=col,region=reg)
    else:
        plot_traces(combined,axes,color='b')
    axes[-1].legend()
    axes[-1].set_xlabel('spine distance to')

    fig,axes=plt.subplots(1,1,sharex=True)
    if region:
        for reg in combined.region.unique():
            data=combined[combined['region']==reg]
            axes.scatter(data['min_soma_dist'].to_numpy()*1e6, data['spine_dist'].to_numpy()*1e6, label=reg)
            axes.legend()
    else:
            axes.scatter(combined['min_soma_dist'].to_numpy()*1e6, combined['spine_dist'].to_numpy()*1e6)        
    axes.set_xlabel('min_soma_dist')
    axes.set_ylabel('spine_dist')
    plt.show()
    return

def parsarg(commandline):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('out', type=str, help='name of .out file with plateau and spike analysis')
    parser.add_argument('csv', type=str, help='name of .csv file with spine to cluster distances')
    parser.add_argument('merge_col', type=str, choices=['num_disp','num_clust'], help='merge out and csv files on num_disp if the simulations varied num_clust and vice versa')
    parser.add_argument('paired_stim', type=int, help='number of dispersed (if merge on num_clust) or cluster (if merge on num_disp) with added inputs')
    parser.add_argument('-dir', type=str, help='directory with files')
    parser.add_argument('-naf', type=bool, help='analyze files with NaF (specify -naf 1) or without (do not use this argument)')
 
    args=parser.parse_args(commandline)
    return args

combine=True

if combine:
    args = sys.argv[1:]
    args='D1Pat4BLA_DLS_0_10_350_0_4_disp_2025-07-08 D1Pat4BLA_disp4_clust10_2025-07-08_distance num_clust 4'.split()
    args='D1Mat2BLA_DLS_0_24_350_0_4_clust_2025-07-09  D1Mat2BLA_disp0_clust32_2025-07-09_distance num_disp 32'.split()
    args='D1Mat2BLA_DLS_0_24_350_0_4_disp_2025-07-09  D1Mat2BLA_disp8_clust24_2025-07-09_distance num_clust 8'.split()
    #args='D1Pat4BLA_DLS_0_10_350_0_4_clust_2025-07-08 D1Pat4BLA_disp0_clust14_2025-07-08_distance num_disp 14'.split()
    #args='D1Mat2BLA_DLS_8_24_350_0_4_disp  clustered_exp50/matrix2_disp/D1Mat2BLA_disp8_clust24_distance num_clust 8'.split()
    par=parsarg(args)
    newdata=pd.read_csv(par.out+'.out',sep='\s+') 
    distdata=pd.read_csv(par.csv+'.csv')
    combined=pd.merge(newdata,distdata,on=['seed','region',par.merge_col],suffixes=[None,'_drop'])
    drop_names=[cn for cn in combined.columns if cn.endswith('_drop')]+['Unnamed: 0']
    combined.drop(axis=1,columns=drop_names,inplace=True)

    if not par.naf:
        combined.drop(axis=1,columns=['num_spk','inst_freq','duration'],inplace=True)

    combined.to_csv(par.out+'_combined.csv') 

    if par.merge_col=='num_clust':
        dfsubset=combined[(combined.num_disp==par.paired_stim)]
    else:
        dfsubset=combined[(combined.num_clust==par.paired_stim)]
    dfsubset.drop(axis=1,columns=['num_clust','maxdist','num_disp','naf','spc','seed','soma_dist_sd','spine_dist_sd'],inplace=True)

    if par.merge_col=='num_clust':
        pvalues=calc_corr(dfsubset,'all')
    else:
        for region in ['DMS','DLS']:
            dfsub=dfsubset[dfsubset['region']==region]
            pvalues=calc_corr(dfsub,region)

    plots(combined,region=True)
else:
    ####################################################################
    ##### now read in all the combined.csv files and analyze
    filenames=glob.glob('D1Pat4BLA_DLS_*2025-07-08_combined.csv')
    df=[]
    for f in filenames:
        df.append(pd.read_csv(f))
    whole_df=pd.concat(df)
    dfsubset=whole_df[(whole_df.num_disp==whole_df.num_disp.max()) | (whole_df.num_clust==whole_df.num_clust.max())] #FIXME: will this work for all  conditions?
    dfsubset.drop(axis=1,columns=['Unnamed: 0','naf','spc','seed','soma_dist_sd','spine_dist_sd','maxdist'],inplace=True)
    calc_corr(dfsubset,'all')
    for region in ['DMS','DLS']:
        dfsub=dfsubset[dfsubset['region']==region]
        pvalues=calc_corr(dfsub,region)

    plots(dfsubset,region=True)

    import scipy.stats as stats
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm

    for depvar in ['plateauVm','decay10']:
        results=ols(depvar+' ~ C(num_clust)',data=dfsubset).fit()
        table=sm.stats.anova_lm(results,typ=2) #coefficients
        print('\n*** depvar=',depvar, '\n',table)
        indep_var=list(table['PR(>F)'].keys())[0]
        if table['PR(>F)'][indep_var]<0.05:
            print(results.summary()) #overall anova result
