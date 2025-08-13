import numpy as np
import glob
import sys
from moose_nerp.anal.neur_anal_class import neur_text
import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)
import os
from scipy.signal import find_peaks

def plot_traces(fnames,reg,spn,startime,endtime):
    from matplotlib import pyplot as plt
    plt.ion()
    fig=plt.figure()
    fig.suptitle(reg+'_'+spn)
    for fn in fnames:
        data=neur_text(fn)
        data.seed=fn.split('_')[-1].split('0Vm.txt')[0]
        plt.plot(data.time,data.traces[data.soma_name[0]], label=data.seed)
    plt.legend()
    plt.xlabel('Time (sec)')
    plt.ylabel('Vm (mV)')
    plt.axvspan(startime, endtime, facecolor="gray", alpha=0.3, zorder=-10)
    return fig

def plot_one_file(fn,dat,startime,endtime):
    from matplotlib import pyplot as plt
    plt.ion()
    fig=plt.figure()
    seed=fn.split('_')[-1].split('0Vm.txt')[0]
    title=fn.split('_')[1]+fn.split('_')[2]+fn.split('_')[3]
    fig.suptitle(title+'_'+seed)
    for  col in dat.traces.keys():
        plt.plot(dat.time,dat.traces[col], label=col)
    plt.legend()
    plt.xlabel('Time (sec)')
    plt.ylabel('Vm (mV)')
    plt.axvspan(startime, endtime, facecolor="gray", alpha=0.1, zorder=-10)
    
def mean_Vm(dat,time_vals):
    points=[]
    for bt in time_vals:
        points.append(np.where(dat.time>=bt)[0][0])
    baseVm=np.mean(dat.traces[dat.soma_name[0]][points[0]:points[1]])
    peakVm=np.max(dat.traces[dat.soma_name[0]][points[0]:points[1]])
    return baseVm,points[1],peakVm

def decay_time(dat,base_val,plateau_val,pt):
    amp=plateau_val-base_val
    #amp=dat.traces[dat.soma_name[0]][pt] -base_val #use value at end stim to determine amplitude
    thresh=0.2*amp+base_val #80% decayed to baseline
    decay_pt= np.where(dat.traces[dat.soma_name[0]][pt:]<thresh) #start search at end of plateau
    if len(decay_pt[0]):
        decay=dat.time[decay_pt[0][0]+pt] #add in pt because np.where indexes start of search at 0
        #return decay
    else:
        decay=dat.sim_time
        #return None
    return decay

def duration(dat,baseVm,start,end_stim):
    start_pt=np.min(np.where(dat.time>=start)) #start of stimulation
    end_pt = np.min(np.where(dat.traces[dat.soma_name[0]][end_stim:]-baseVm<.0001))+end_stim#1 mV, return to basal
    auc=np.sum(dat.traces[dat.soma_name[0]][start_pt:end_pt]-baseVm)*dat.time[1] #this is dt
    mean=np.mean(dat.traces[dat.soma_name[0]][start_pt:end_pt]-baseVm)
    dur=auc/mean #issue: mean is sensitive to end point
    dur = dat.time[end_pt]-dat.time[end_stim]
    return dur

def risetime(dat,start,stim_stop,base):
    stop_pt=np.min(np.where(dat.time>stim_stop))
    early_amp=np.max(dat.traces[dat.soma_name[0]][start:stop_pt])-base
    rise_pt=np.min(np.where(dat.traces[dat.soma_name[0]][start:stop_pt]>0.8*early_amp+base))+start
    return rise_pt*dat.time[1] #dt

def remove_fn(fnames,key):
    remove=[]
    for fn in fnames:
        if key in fn:
            remove.append(fn)
    for fn in remove:
        fnames.remove(fn)
    return fnames

def dep_vars(fn,ftype='0Vm'):
    parts=os.path.basename(fn).split('_')
    root=parts[0]
    reg=parts[1]
    ndisp=parts[2]
    nclust=parts[3]
    endtime=parts[4]
    maxdist=parts[6]
    spc=parts[7] #this will not be correct for files generated prior to 2024 aug 5
    if 'NaF' in fn:
        naf='1'
    else: 
        naf='0'
    seed=parts[-1].split(ftype)[0]
    depend_vars=[root,reg,ndisp,nclust,maxdist,naf,spc, endtime,seed]
    return depend_vars

def paired_files(fnames,dir,nclust,ndisp,paired,reg,ftype='0Vm'): #for each file in fnames, find the one with same seed and one parameter different
    paired_fnames=[];diff=[];remove_fn=[]
    for fn in fnames:
        depend_vars=dep_vars(fn,ftype)
        seed=depend_vars[-1]
        if paired=='ndisp': #need to specify whether paired file differs by ndisp of nclust
            input_str='_'.join(['*',str(nclust),depend_vars[-2]])
        else: #paired files vary in num_clustered
            input_str='_'.join([str(ndisp),'*',depend_vars[-2]])
        paired_pattern='D1*BLA_'+reg+'_'+input_str+'_*'+'_'+seed+ftype+'.txt'  #find all files that match input string - should be two
        if dir:
            paired_pattern=dir+paired_pattern
        paired_file=sorted(glob.glob(paired_pattern))
        if len(paired_file)==2:
            #find the difference - that is new parameter
            var0=paired_file[0].split('_')
            var1=paired_file[1].split('_')
            one_diff=[(x,y) for x,y in zip(var0,var1) if x != y ] #save both params
            if len(one_diff)==1:
                diff.append(one_diff[0])
            else:
                print('multiple parameter differences between', paired_file)
            paired_file.remove(fn)
            new_fn=paired_file[0] #new file is the one that was not in the original fnames list
            paired_fnames.append(new_fn)                        
        else:
            print('unable to determine  correct file from', paired_file, 'removing from the list')
            remove_fn.append(fn)
    for fn in remove_fn:
        fnames.remove(fn)
    return paired_fnames, list(set(diff))
        
def construct_pattern(par,num_input_string,reg): #depending on input args, construct pattern to find files using glob
    if len(par.end_time)==1:
        et=par.end_time[0]
    elif len(par.end_time)==len(par.num_clustered):
        et=par.end_time[ii]
    else:
        print('ERROR: specify either 1 end_time or 1 per num_clustered, instead of', par.end_time)
    pattern='D1*BLA_'+reg+'_'+num_input_string
    if par.dir:
        pattern=par.dir+pattern
    if par.dist:
        pattern=pattern+'*'+str(par.dist)
    else:
        pattern=pattern+'*'
    if par.spc:
        pattern=pattern+'_'+str(par.spc)+'_'
    return pattern, et
 
class BLA_anal():
    def __init__(self,region,num_stim):
        self.isis={reg:{str(c):[] for c in num_stim} for reg in region}
        self.num_spikes={reg:{str(c):[] for c in num_stim} for reg in region}
        self.plateauVm={reg:{str(c):[] for c in num_stim} for reg in region}
        self.decay10={reg:{str(c):[] for c in num_stim} for reg in region}
        self.dur={reg:{str(c):[] for c in num_stim} for reg in region}
        self.plat_trials={reg:{str(c):0 for c in num_stim} for reg in region} #number of trials used to calculate plateau and decay
        self.inst_freq={reg:{str(c):[] for c in num_stim} for reg in region}
        #rise_time={reg:{str(c):[] for c in num_stim} for reg in region}
        self.trials={reg:{} for reg in region}
        self.min_isi=0.002#msec
        self.spike_height=0 #threshold in volts
        self.rows=[]

    def paired_init(self,reg, new_stim):
        #add another dictionary to hold results of paired files
        self.isis[reg][new_stim]=[]
        self.num_spikes[reg][new_stim]=[]
        self.plateauVm[reg][new_stim]=[]
        self.decay10[reg][new_stim]=[]
        self.dur[reg][new_stim]=[]
        self.plat_trials[reg][new_stim]=0
        self.inst_freq[reg][new_stim]=[]


    def analyze_file(self,fn,reg,nc): #extract spikes, plateau, decay rate, etc from single Vm trace
        self.data=neur_text(fn)
        trace=self.data.traces[self.data.soma_name[0]]
        spikes=find_peaks(trace,height=self.spike_height,distance=int(self.min_isi/self.data.time[1] ))
        self.spk_tm=spikes[0]*self.data.time[1] #take 1st array of points, convert to time
        self.num_spikes[reg][nc].append(len(self.spk_tm))
        isi=np.nan #initialize as nan
        baseVm,start_pt,_=mean_Vm(self.data,base_time) #baseline Vm
        plateau,plat_start,peakVm=mean_Vm(self.data,plateau_time) #plateau Vm
        if not len(self.spk_tm): #if no spikes, measure plateau and decay time
            #rise_time[reg][nc].append(1000*risetime(data,start_pt,0.15,baseVm))
            self.dur[reg][nc].append(np.nan)#(1000*duration(data,baseVm,par.start,plat_start))
            self.plateauVm[reg][nc].append(peakVm-baseVm) #plateau amplitude defined using peak.  If use plateau-baseVm, then could define it even with spikes
            decay=decay_time(self.data,baseVm,peakVm, plat_start) #time to decay
            self.decay10[reg][nc].append(1000*(decay-plateau_time[1])) #decay duration, in msec
            self.plat_trials[reg][nc]+=1
        else:
            self.decay10[reg][nc].append(np.nan)
            self.plateauVm[reg][nc].append(np.nan) #plateau-baseVm - test this with example files
            print('spikes for', fn)
        if len(self.spk_tm)>1: #if more than 1 spike, calculate mean ISI
            isi=np.diff(self.spk_tm)
            self.isis[reg][nc].append(isi)
            self.inst_freq[reg][nc].append(np.mean(1/isi))
            self.dur[reg][nc].append(self.spk_tm[-1]-self.spk_tm[0]) #time between 1st and last spike
        else:
            self.dur[reg][nc].append(np.nan)
        results=[str(round(self.plateauVm[reg][nc][-1],3)), str(round(self.decay10[reg][nc][-1],1)),
                 str(round(self.dur[reg][nc][-1],1)), str(len(self.spk_tm)),str(round(np.nanmean(1/isi),2))]
        return results

def config_loop(par):
    loop_over='ndisp'
    if len(par.num_clustered)>=1 and len(par.num_dispersed)==1:  #loop_over num_clustered
        if par.paired=='nclust' or par.paired is None:
            num_stim=par.num_clustered #if paired, use (num_disp,*) - num_disp correct, num_clust NOT USED
            loop_over='nclust'
        elif len(par.num_clustered)==1 and par.paired=='ndisp':
            num_stim=par.num_dispersed #if paired, use (*,num_clust) - num_clust correct,num_disp NOT USE
        else:
            print('paired param must be num_clust if num_clustered>1')
            sys.exit()
    elif len(par.num_clustered)==1 and len(par.num_dispersed)>=1: # loop_over num_dispersed
        if par.paired=='ndisp' or par.paired is None:
            num_stim=par.num_dispersed   #if paired, use (*,num_clust) , num_clust correct, num_disp does NOT USE
        else:
            print('must have only single num_clustered if paired parameter is num_disp')
            sys.exit()
    else:
        print('ERROR: either specify one value for num_clustered or one value for num_dispersed')
    return loop_over, num_stim

#may need to add NMDA, celltype, distance or other parameters at some point
def parsarg():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('-dur', type=float, default=0.05, help='duration for measuring plateau, in sec')
    parser.add_argument('-num_dispersed', nargs="+", type=int, default=[0], help='number of dispersed inputs')
    parser.add_argument('-num_clustered', nargs="+", type=int, default=[0], help='number of clustered inputs')
    parser.add_argument('-spc', type=int, help='spines per cluster')
    parser.add_argument('-end_time', nargs="+", type=float, default=[0.3], help='time to begin measuring decay, in sec')
    parser.add_argument('-start', type=float, default=0.1, help='time that stimulation begins, in sec')
    parser.add_argument('-seed', nargs="+", type=int, help='seed for file to plot all compartments')
    parser.add_argument('-dir', type=str, help='directory with files')
    parser.add_argument('-naf', type=bool, help='analyze files with NaF (specify -naf 1) or without (do not use this argument)')
    parser.add_argument('-dist', type=int, help='max_dist of dispersed')
    parser.add_argument('-output', type=bool,help='Y or 1 to write output file')
    parser.add_argument('-paired', type=str,help='Specify which parameter to pair (ndisp or nclust)',choices=['ndisp','nclust'])

    return parser

if __name__ == '__main__':
    args = sys.argv[1:]
    #args='-num_clustered 18 -num_dispersed 0 -paired nclust '.split()
    parser=parsarg()
    par=parser.parse_args(args)
    print('disp',par.num_dispersed,'clust',par.num_clustered)

    num_clust=par.num_clustered[0]
    num_disp=par.num_dispersed[0]
    loop_over, num_stim=config_loop(par)

    region=['DMS','DLS']

    data_set=BLA_anal(region,num_stim)

    base_time=[par.start-par.dur,par.start]

    #for spn in ['Mat3', 'Mat2']:
    for reg in region:
        for ii,nstim in enumerate(num_stim):
            nc=str(nstim)
            if loop_over=='nclust': 
                num_inputs='_'.join([str(num_disp),nc])
            else:
                num_inputs='_'.join([nc,str(num_clust)])
            pattern,et=construct_pattern(par,num_inputs,reg)
            if par.naf:
                fnames=glob.glob(pattern+'*NaF*0Vm.txt')
            else:
                fnames=glob.glob(pattern+'*0Vm.txt')
                fnames=remove_fn(fnames,'NaF')
            data_set.trials[reg][nc]=len(fnames)
            if len(fnames):
                if par.paired: #find additional files that have different clust or disp inputs, but same random seed
                    paired_fnames,nc2=paired_files(fnames,par.dir, num_clust,num_disp, par.paired, reg) #nc2 is list of tuples containing both paired parameters.  
                    if len(nc2)==1: #Should only be one list 
                        paired_param=list(nc2[0])
                        for p in paired_param:
                            if p not in data_set.isis[reg].keys():#identify which parameter in the tuple is the "new" one
                                data_set.paired_init(reg,p)
                                new_par=p #this will only work if there is only one paired param
                                data_set.trials[reg][p]=len(paired_fnames)
                    else:
                        print('too many parameter differences beween paired files')
                    print('### paired files for',nc,nc2,reg,':',paired_fnames)
                print('### files for ',nc,reg,':', fnames)
                #Plot the data
                plot_traces(fnames,reg,nc,par.start,et)
                if par.paired: 
                    plot_traces(paired_fnames,reg,new_par,par.start,et)
                #Next, extract some measurements
                plateau_time=[float(et)-par.dur,float(et)] #measure Vm over 50 msec during plateau
                for i,fn in enumerate(fnames):
                    results=data_set.analyze_file(fn,reg,nc)
                    if par.seed:
                        for sd in par.seed:
                            if str(sd) in fn:
                                plot_one_file(fn,data_set.data, par.start,et)
                    #output for stat analysis
                    dependent_vars=dep_vars(fn)
                    del dependent_vars[-2]
                    data_set.rows.append(dependent_vars[1:]+results)
                    if par.paired:
                        results2=data_set.analyze_file(paired_fnames[i],reg,new_par)
                        dependent_vars=dep_vars(paired_fnames[i])
                        del dependent_vars[-2]                  
                        data_set.rows.append(dependent_vars[1:]+results2)
            else:
                print('no files found using pattern',pattern, 'with parameters',nc,reg)
    #output for stat analysis, export and then read in and combine multiple files
    if par.output:
        from datetime import datetime
        outfname='_'.join(dependent_vars[0:-1]+[par.paired[1:],datetime.today().strftime('%Y-%m-%d')])
        header='region    num_disp  num_clust  maxdist     naf    spc   seed  plateauVm  decay10  duration num_spk  inst_freq'
        np.savetxt(outfname+'.out',data_set.rows,fmt='%7s',header=header,comments='')  
    
    ################## Results ###################
    import scipy.stats as sps
    for reg in region:
        if loop_over=='nclust':
            print('***', num_disp, 'dispersed, ', reg,'trials for nclust =',[data_set.trials[reg]])
        else:
            print('***', num_clust, 'clustered, ', reg,'trials for ndisp =',[data_set.trials[reg]])
        for nstim in sorted(data_set.num_spikes[reg]): 
            nc=str(nstim)
            print( '  ', nc,'inputs, spikes=',np.round(np.mean(data_set.num_spikes[reg][nc]),3),'+/-',np.round(sps.sem(data_set.num_spikes[reg][nc],nan_policy='omit'),3))
            if len(data_set.isis[reg][nc]):
                print('        freq=',np.round(np.nanmean(data_set.inst_freq[reg][nc]),2),'+/-',np.round(sps.sem(data_set.inst_freq[reg][nc],nan_policy='omit'),2), 'from', len(data_set.isis[reg][nc]), 'trials')
                print('        mean dur of spiking',np.round(np.nanmean(data_set.dur[reg][nc]),3),'+/-',np.round(sps.sem(data_set.dur[reg][nc],nan_policy='omit'),3), 'in sec')
            else:
                print('        no frequency or spike dur, only 0 or 1 spike per trace')
            if not np.all(np.isnan(data_set.decay10[reg][nc])):
                print('        mean plateau',np.round(np.nanmean(data_set.plateauVm[reg][nc]),1),'+/-',np.round(sps.sem(data_set.plateauVm[reg][nc],nan_policy='omit'),1), 'in mV, n=',data_set.plat_trials[reg][nc])
                print('        mean decay',np.round(np.nanmean(data_set.decay10[reg][nc]),1),'+/-',np.round(sps.sem(data_set.decay10[reg][nc],nan_policy='omit'),1), 'in msec, n=',data_set.plat_trials[reg][nc])
                #print('        mean rise_time',np.round(np.nanmean(rise_time[reg][nc]),1),'+/-',np.round(sps.sem(rise_time[reg][nc],nan_policy='omit'),1), 'in sec, n=',plat_trials[reg][nc])


