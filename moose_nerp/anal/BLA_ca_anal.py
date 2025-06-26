import numpy as np
import glob
import sys
import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)
import os
import moose_nerp.anal.BLA_anal as ba
from matplotlib import pyplot as plt
import pandas as pd
plt.ion()

m2um=1e6
mM2uM=1e3

def load_spine_file(fn,pattern):
    dependent_vars=ba.dep_vars(fn,ftype='0Ca')
    seed=dependent_vars[-1]
    spine_file=glob.glob(pattern+'*'+seed+'.npz')
    inputs=np.load(spine_file[0],allow_pickle=True)
    #clust_spines=[os.path.dirname(i) for i in inputs['orig']]
    #extra_spines=[os.path.dirname(i) for i in inputs['extra']]
    return list(inputs['orig']),list(inputs['extra']), dependent_vars

class BLA_anal():
    def __init__(self,region,locations,onset):
        self.region=region
        self.onset=onset
        self.auc={reg:{loc:[] for loc in locations} for reg in region} #expand to include nstim
        self.auc_diff={reg:{loc:[] for loc in locations} for reg in region}
        self.auc_ratio={reg:{loc:[] for loc in locations} for reg in region}
        self.distances={reg:{loc:[] for loc in locations} for reg in region}
        self.rows=[]
        return
                
    def calc_auc(self,extra_data,orig_data,columns,dist_dict,reg):
        def map_distance(dist): #FIXME somewhat arbitrary distances
            if dist<80:
                return 'prox'
            elif dist>160:
                return 'dist'
            else:
                return 'mid'
        
        dt=extra_data[1,0]
        onset_pt=int(self.onset/dt)
        for comp,col in columns.items():
            dist=dist_dict[comp]
            key=map_distance(dist)
            diff=(extra_data[:,col]-orig_data[:,col])
            basal=np.mean(orig_data[0:onset_pt,col])
            auc_orig=np.sum(orig_data[:,col]-basal)*dt
            basal=np.mean(extra_data[0:onset_pt,col])
            self.auc[reg][key].append(np.sum(extra_data[:,col]-basal)*dt)
            basal=np.mean(diff[0:onset_pt])
            self.auc_diff[reg][key].append(np.sum(diff)*dt)
            self.auc_ratio[reg][key].append(np.sum(diff)*dt/auc_orig)
            self.distances[reg][key].append(dist)
        return 
    
    def output_results(self,data,columns):
        results=[]
        dt=data[1,0]
        onset_pt=int(self.onset/dt)
        for comp,col in columns.items():
            basal=np.mean(data[0:onset_pt,col])
            auc=np.sum(data[:,col]-basal)*dt*mM2uM
            peak=(np.max(data[:,col])-basal)*mM2uM
            results.append(round(auc,2))
            results.append(round(peak,2))
        return results

    def calc_distance(self,orig,extra):

        #If extra inputs are clustered, than sp2sp distance not interesting.  Instead, sp2soma is relevant
        #If extra inputs are dispersed, then sp2sp distance might be interesting for extra, and sp2soma is interesting for orig
        #so, sp2soma should be used for all orig, and sp2sp if there are extra dispersed, but sp2soma for extra clustered
        shell0=list(np.unique([os.path.dirname(sp)+'/Shell_0' for sp in orig]))
        shell_extra=list(np.unique([os.path.dirname(sp)+'/Shell_0' for sp in extra]))

        soma_dist={s:[] for s in shell0+shell_extra}
        sp_dist={s:[] for s in shell_extra}
        sp_dist_distal={s:[] for s in shell_extra}
        for sp in orig+extra: #find distance to soma of all spines
            sp_index=self.spine_list.index(sp.replace('[0]',''))
            comp=os.path.dirname(sp)+'/Shell_0'
            soma_dist[comp].append(self.sp2sp_dist[sp_index,-1])
        soma_dist={c:np.mean(soma_dist[c])*m2um for c in soma_dist.keys()} #distance of comp to soma is mean of the spines in that comp
        soma_sorted={k: v for k, v in sorted(soma_dist.items(), key=lambda item: item[1])}
        for ex in extra: #find distance to closest cluster for extra spines
            ex_index=self.spine_list.index(ex.replace('[0]',''))
            excomp=os.path.dirname(ex)+'/Shell_0'
            sp_dist_temp={}
            sp_distal_temp={}
            for sp in orig:
                sp_index=self.spine_list.index(sp.replace('[0]',''))
                sp_dist_temp[sp]=self.sp2sp_dist[sp_index,ex_index]
                spcomp=os.path.dirname(sp)+'/Shell_0'
                if soma_dist[spcomp] >150: #FIXME arbitrary distance for defining distal spines
                    sp_distal_temp[sp]=self.sp2sp_dist[sp_index,ex_index]
            min_key=min(sp_dist_temp, key=sp_dist_temp.get) #distance to closest cluster
            sp_dist[excomp].append(sp_dist_temp[min_key])
            #maybe distance to most distal cluster is more important?
            if len(sp_distal_temp):
                min_key=min(sp_distal_temp, key=sp_distal_temp.get) #distance to closest cluster
                sp_dist_distal[excomp].append(sp_distal_temp[min_key])
        extra_dist={c:np.mean(sp_dist[c])*m2um for c in sp_dist.keys()} #distance of comp to cluster is mean of the spines in that comp
        distal_dist={c:np.mean(sp_dist_distal[c])*m2um for c in sp_dist_distal.keys()} 
        #ed_sorted={k: v for k, v in sorted(extra_dist.items(), key=lambda item: item[1])}
        return soma_sorted,extra_dist, shell0, distal_dist
    
    def load_spines(self,sp2sp_file):
        sp2sp=np.load(sp2sp_file+'.npz',allow_pickle=True)
        self.spines=sp2sp['index'].item()
        self.spine_list=[s.replace('[0]','') for s in self.spines.keys()]
        self.sp2sp_dist=sp2sp['s2sd']

    def calc_means(self):
        self.means={name: {reg:{} for reg in self.region} for name in ['auc','diff','ratio']}

        for reg in self.region:
            for key in self.auc[reg].keys():
                self.means['auc'][reg][key]=np.mean(self.auc[reg][key])
                print(reg,key,', num samples:',len(self.auc[reg][key]))
                self.means['diff'][reg][key]=np.mean(self.auc_diff[reg][key])
                self.means['ratio'][reg][key]=np.mean(self.auc_ratio[reg][key])
        fig,axs=plt.subplots(3,1,sharex=True)
        for ax,(ylbl,auc) in zip(axs,self.means.items()):
            for reg in self.region:
                ax.scatter(list(auc[reg].keys()),auc[reg].values(),label=reg)
            ax.set_ylabel(ylbl+' Calcium')
        ax.legend()
        ax.set_xlabel('compartment location')
        
    def corr_plot(self):
        from scipy.stats import pearsonr

        def flatten(list_2d):
            return [i for sl in list_2d for i in sl]
        
        all_dist={}
        fig,axs=plt.subplots(3,1,sharex=True)
        for reg in self.region:
            all_dist[reg]=flatten(self.distances[reg].values())
        for ax, auc,ylbl in zip(axs,[self.auc,self.auc_diff,self.auc_ratio],['auc Ca','auc diff', 'auc ratio']):
            for reg in self.region:
                ca_auc=flatten(auc[reg].values())
                corr=pearsonr(all_dist[reg],ca_auc)
                pvalues=(round(corr[0],3),round(corr[1],4))
                ax.scatter(all_dist[reg],ca_auc,label=reg+' '+' ,'.join([str(p) for p in pvalues]))
                
            ax.set_ylabel(ylbl)
            ax.legend()
        ax.set_xlabel('distance to soma')

def plot_traces(data,orig_data,columns,fn,labels,title=''):
    fig=plt.figure()
    time=data[:,0]
    for comp,col in columns.items():
        if labels[comp].endswith('sp2sp'):
            labl=os.path.dirname(comp)+' '+labels[comp]
            linestyle='--'
        else:
            labl=os.path.dirname(comp)+' '+labels[comp]+'u'
            linestyle='-'
        p=plt.plot(time,data[:,col]*mM2uM,label=labl, linestyle=linestyle)
        color=p[-1].get_color()
        plt.plot(time,orig_data[:,col]*mM2uM,color=color,linestyle=':')
    plt.title(title)
    plt.legend()
    plt.xlabel('Time (sec)')
    plt.ylabel(fn)
    return fig

def sorted_comp_col(shell0,header,soma_dist):
    comp_col={c:header.index(c) for c in shell0 if c in header}
    #sort comp_col by distance to soma (orig_dist)
    triplets=[(k,comp_col[k],soma_dist[k]) for k in comp_col.keys()]
    trip_sorted=sorted(triplets,key=lambda x:x[2])
    comp_col={k: v for (k, v,d) in trip_sorted}
    return  comp_col

def create_title(soma_dist,extra_comp,paired,sp_dist,sp_dist_distal):
    distance_par1=np.mean([soma_dist[k+'/Shell_0'] for k in extra_comp])
    title='soma '+str(round(distance_par1))
    if paired=='ndisp':
        distance_par2=np.mean(list(sp_dist.values()))
        title=title+' sp2sp '+str(round(distance_par2))
        distance_par3=np.nanmean(list(sp_dist_distal.values()))
        if np.isnan(distance_par3):
            title=title+' no distal clusters'
        else:
            title=title+' sp2distal '+str(round(distance_par3))
    return title
def create_output_header(output_dist):
    out_header='region    num_disp  num_clust  maxdist  naf spc   seed  '.split()
    out_header=out_header+['comp'+str(i)+'dist' for i in range(len(output_dist))]
    auc_peak=' '.join(['auc'+str(i)+ '_uM-s  peak'+str(i)+'_uM' for i in range(len(output_dist))])
    out_header=out_header+ auc_peak.split()
    out_header=out_header+['spine_dist','max_clust_dist','min_clust_dist','soma_dist','max_soma_dist','min_soma_dist']
    return out_header

if __name__ == '__main__':
    args = sys.argv[1:]
    #args='-dir clustered_exp50/spc4_again/ -num_clustered 32 -paired nclust -ntype matrix'.split() #matrix, clustered
    #args='-dir clustered_exp50/patch4_Rm5_Ra0.34/ -num_clustered 14 -paired nclust -ntype patch'.split() #patch clustered
    #args='-dir clustered_exp50/matrix2_disp/ -num_clustered 24 -num_dispersed 8 -paired ndisp -ntype matrix'.split()
    #args='-dir clustered_exp50/patch4_Rm5_Ra0.34_disp2/ -num_clustered 10 -num_dispersed 4 -paired ndisp -ntype patch'.split()
    args='-num_clustered 24 -num_dispersed 8 -paired ndisp -ntype matrix -output 1'.split()
    parser=ba.parsarg()
    parser.add_argument('-ntype', type=str,choices=['patch','matrix'],help='neuron type to determine sp2sdist file')
    par=parser.parse_args(args)
    print('disp',par.num_dispersed,'clust',par.num_clustered)

    num_clust=par.num_clustered[0]
    num_disp=par.num_dispersed[0]
    loop_over, num_stim=ba.config_loop(par)

    region=['DMS','DLS']
    locations=['prox','mid','dist']
    shell='Shell_0'
    trace_plots=1

    data_set=BLA_anal(region,locations,par.start)

    if par.ntype == 'patch':
        sp2sp_file='D1_short_patch_187463_D1_108_ab_s2sdist'
    elif par.ntype == 'matrix':
        sp2sp_file='D1_long_matrix_84362_D1_15_ab_s2sdist'
    #else:
    #    print('SELECT proper spine file')
    data_set.load_spines(sp2sp_file)

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
            fnames=ba.remove_fn(fnames,'NaF')
            paired_fnames,nc2=ba.paired_files(fnames,par.dir, num_clust,num_disp, par.paired,reg, ftype='0Ca')
            for idx,fn in enumerate(fnames):
                extra_data=np.loadtxt(fn)
                orig_data=np.loadtxt(paired_fnames[idx])
                with open(fn) as f:
                    header=f.readline().split()
                if '#' in header:
                    header.remove('#')
                #print(os.path.basename(fn),', orig clusters:',np.shape(orig_data),', added spines:',np.shape(extra_data)) #if not the same length, there is problem
                orig,extra,dep_vars=load_spine_file(fn,pattern) #load file with list of spines used in simulation
                soma_dist,sp_dist,shell0,sp_dist_distal=data_set.calc_distance(orig,extra) #extract distance for spines to soma and to closest cluster 
                labels={k:str(round(v)) for k,v in soma_dist.items()}
                if par.paired=='ndisp':
                    for k,v in sp_dist.items():
                        labels[k]=str(round(v))+' sp2sp'
                comp_col=sorted_comp_col(shell0,header,soma_dist)
                #Exclude files in which added spines are in same comp as original spines
                orig_comp=set([os.path.dirname(s) for s in orig])
                extra_comp=set([os.path.dirname(s) for s in extra])
                duplicate_comp=extra_comp & orig_comp
                if len(duplicate_comp) and par.paired=='ndisp':
                    print('PROBLEM', fn, 'added dispersed input in same comp as clustered',duplicate_comp,'skipping this file')
                    #plot_traces(extra_data,orig_data,comp_col,os.path.basename(fn), labels)
                    print('     sp2sp distances for this trace',[l for l in labels.values() if 'sp2sp' in l]) 
                    continue
                #only calculate AUC for comps that had synaptic input in original sims
                data_set.calc_auc(extra_data,orig_data,comp_col,soma_dist,reg)
                if par.output:
                  #one row of results for data WITH added spines
                    output_dist=[round(soma_dist[k],1) for k in comp_col.keys()] #distance of output shells (which are subset of clustered spine comps) to soma
                    spine2clust_dist=[np.mean(list(sp_dist.values())), np.max(list(sp_dist.values())),np.min(list(sp_dist.values()))] #mean, min, max distance of added spines to closest cluster
                    soma_dist_extra=[soma_dist[os.path.dirname(k)+'/Shell_0'] for k in extra] #distance of spine to soma for extra spines
                    spine2soma_dist=[np.mean(soma_dist_extra), np.max(soma_dist_extra),np.min(soma_dist_extra)] #mean, min, max distance of spine to soma for extra spines
                    
                    data_set.rows.append(dep_vars[1:]+output_dist+data_set.output_results(extra_data,comp_col)+spine2clust_dist+spine2soma_dist)
                    #one row of results for data without added spines
                    dep_vars=ba.dep_vars(paired_fnames[idx],ftype='0Ca')
                    data_set.rows.append(dep_vars[1:]+output_dist+data_set.output_results(orig_data,comp_col)+spine2clust_dist+spine2soma_dist)
                if idx<trace_plots:
                    title=create_title(soma_dist,extra_comp,par.paired,sp_dist,sp_dist_distal)
                    plot_traces(extra_data,orig_data,comp_col,os.path.basename(fn), labels,title) 
    
    out_header=create_output_header(output_dist)
    df=pd.DataFrame(data_set.rows,columns=out_header)

    if par.output:
        outfname='_'.join(dep_vars[0:-1]+['_Ca_combined'])
        df.to_csv(outfname+'.csv')

    data_set.calc_means()
    data_set.corr_plot()
    print('finished')

    #1. correlate peak/AUC with distance of extra comp from soma?
    #2. read in Vm, calculate decay10 or plateau, and correlate with ca?



