import numpy as np
import glob
import sys
import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)
import os
import moose_nerp.anal.BLA_anal as ba
from matplotlib import pyplot as plt

def load_spine_file(fn,pattern):
    dependent_vars=ba.dep_vars(fn,ftype='0Ca')
    seed=dependent_vars[-1]
    spine_file=glob.glob(pattern+'*'+seed+'.npz')
    inputs=np.load(spine_file[0],allow_pickle=True)
    #clust_spines=[os.path.dirname(i) for i in inputs['orig']]
    #extra_spines=[os.path.dirname(i) for i in inputs['extra']]
    return list(inputs['orig']),list(inputs['extra'])

def plot_traces(data,columns,fn,labels,orig_data):
    plt.ion()
    fig=plt.figure()
    time=data[:,0]
    for comp,col in columns.items():
        if labels[comp].endswith('sp2sp'):
            labl=os.path.dirname(comp)+' '+labels[comp]
            linestyle='--'
        else:
            labl=os.path.dirname(comp)+' '+labels[comp]+'u'
            linestyle='-'
        p=plt.plot(time,data[:,col]*1000,label=labl)
        color=p[-1].get_color()
        plt.plot(time,orig_data[:,col]*1000,color=color,linestyle=':')
    plt.legend()
    plt.xlabel('Time (sec)')
    plt.ylabel(fn)
    return fig

def calc_distance(orig,extra,spines,sp2sp_dist):

    #If extra inputs are clustered, than sp2sp distance not interesting.  Instead, sp2soma is relevant
    #If extra inputs are dispersed, then sp2sp distance might be interesting for extra, and sp2soma is interesting for orig
    #so, sp2soma should be used for all orig, and sp2sp if there are extra dispersed, but sp2soma for extra clustered
    shell0=list(np.unique([os.path.dirname(sp)+'/Shell_0' for sp in orig+extra]))
    shell_extra=list(np.unique([os.path.dirname(sp)+'/Shell_0' for sp in extra]))

    soma_dist={s:[] for s in shell0}
    sp_dist={s:[] for s in shell_extra}
    for sp in orig+extra: #find distance to soma of all spines
        sp_index=spines.index(sp.replace('[0]',''))
        comp=os.path.dirname(sp)+'/Shell_0'
        soma_dist[comp].append(sp2sp_dist[sp_index,-1])
    orig_dist={c:np.mean(soma_dist[c])*1e6 for c in soma_dist.keys()} #distance of comp to soma is mean of the spines in that comp
    od_sorted={k: v for k, v in sorted(orig_dist.items(), key=lambda item: item[1])}
    for ex in extra: #find distance to closest cluster for extra spines
        ex_index=spines.index(ex.replace('[0]',''))
        comp=os.path.dirname(ex)+'/Shell_0'
        sp_dist_dict={}
        for sp in orig:
            sp_index=spines.index(sp.replace('[0]',''))
            sp_dist_dict[sp]=sp2sp_dist[sp_index,ex_index]
        min_key=min(sp_dist_dict, key=sp_dist_dict.get)
        sp_dist[comp].append(sp_dist_dict[min_key])
    extra_dist={c:np.mean(sp_dist[c])*1e6 for c in sp_dist.keys()} #distance of comp to cluster is mean of the spines in that comp
    ed_sorted={k: v for k, v in sorted(extra_dist.items(), key=lambda item: item[1])}
    return od_sorted,ed_sorted

if __name__ == '__main__':
    #args = sys.argv[1:]
    #args='-dir clustered_exp50/spc4_again/ -num_clustered 32 -paired nclust'.split()
    args='-dir clustered_exp50/matrix2_disp/ -num_clustered 24 -num_dispersed 8 -paired ndisp'.split()
    par=ba.parsarg(args)
    print('disp',par.num_dispersed,'clust',par.num_clustered)

    num_clust=par.num_clustered[0]
    num_disp=par.num_dispersed[0]
    loop_over, num_stim=ba.config_loop(par)

    sp2sp_file='D1_long_matrix_84362_D1_15_ab_s2sdist'
    sp2sp=np.load(sp2sp_file+'.npz',allow_pickle=True)
    spines=sp2sp['index'].item()
    spine_list=[s.replace('[0]','') for s in spines.keys()]
    sp2sp_dist=sp2sp['s2sd']

    region=['DMS','DLS']
    shell='Shell_0'

    data_set=ba.BLA_anal(region,num_stim)

    base_time=[par.start-par.dur,par.start]

    #for spn in ['Mat3', 'Mat2']:
    for reg in region:
        for ii,nstim in enumerate(num_stim):
            nc=str(nstim)
            if loop_over=='nclust': 
                num_inputs='_'.join([str(num_disp),nc])
            else:
                num_inputs='_'.join([nc,str(num_clust)])
            pattern,et=ba.construct_pattern(par,num_inputs,reg)
            fnames=glob.glob(pattern+'*0Ca.txt') #identify files with calcium traces
            paired_fnames,nc2=ba.paired_files(fnames,par.dir, num_clust,num_disp, par.paired,reg, ftype='0Ca')
            for idx,fn in enumerate(fnames):
                data=np.loadtxt(fn)
                orig_data=np.loadtxt(paired_fnames[idx])
                with open(fn) as f:
                    header=f.readline().split()
                if '#' in header:
                    header.remove('#')
                orig,extra=load_spine_file(fn,pattern) #load file with list of spines used in simulation
                orig_dist,extra_dist=calc_distance(orig,extra,spine_list,sp2sp_dist) #extract distance for spines in simulation
                labels={k:str(round(v)) for k,v in orig_dist.items()}
                if par.paired=='ndisp':
                    for k,v in extra_dist.items():
                        labels[k]=str(round(v))+' sp2sp'
                shell0=orig_dist.keys()
                comp_col={c:header.index(c) for c in shell0 if c in header}
                #sort comp_col by distance to soma (orig_dist)
                #triplets=[(k,comp_col[k],orig_dist[k]) for k in comp_col.keys()]
                #trip_sorted=sorted(triplets,key=lambda x:x[2])
                #cc_sorted={k: v for (k, v,d) in trip_sorted}
                plot_traces(data,comp_col,os.path.basename(fn), labels,orig_data) 
                #analysis possibilities
                #1. calculate peak and/or AUC, especially of comp in "extra"
                #1b. correlate peak/AUC with distance of extra comp from soma
                #1c. calculate DIFFERENCE between orig and extra, correlate with distance
                #2. read in Vm, calculate decay10 or plateau, and correlate with ca



