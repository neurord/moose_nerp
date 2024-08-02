import numpy as np
import glob
import sys
from moose_nerp.anal.neur_anal_class import neur_text
import warnings
warnings.simplefilter("ignore", category=RuntimeWarning)
import os

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

#may need to add NMDA, celltype, distance or other parameters at some point
def parsarg(commandline):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('-dur', type=float, default=0.05, help='duration for measuring plateau, in sec')
    parser.add_argument('-num_dispersed', nargs="+", type=int, default=[75], help='number of dispersed inputs')
    parser.add_argument('-num_clustered', nargs="+", type=int, default=[16], help='number of clustered inputs')
    parser.add_argument('-end_time', nargs="+", type=float, default=[0.3], help='time to begin measuring decay, in sec')
    parser.add_argument('-start', type=float, default=0.1, help='time that stimulation begins, in sec')
    parser.add_argument('-seed', type=int, help='seed for file to plot all compartments')
    parser.add_argument('-dir', type=str, help='directory with files')
    parser.add_argument('-naf', type=bool, help='analyze files with NaF (specify -naf 1) or without (do not use this argument)')
    parser.add_argument('-dist', type=int, help='max_dist of dispersed')
    parser.add_argument('-output', type=bool,help='Y or 1 to write output file')
    args=parser.parse_args(commandline)
    return args

args = sys.argv[1:]
#args='-num_clustered 0 -num_dispersed 36 48 60 72 -dist 200'.split()
par=parsarg(args)
print('disp',par.num_dispersed,'clust',par.num_clustered)

if len(par.num_clustered)>=1 and len(par.num_dispersed)==1:
    num_stim=par.num_clustered
    num_disp=par.num_dispersed[0]
elif len(par.num_clustered)==1 and len(par.num_dispersed)>=1:
    num_clust=par.num_clustered[0]
    num_stim=par.num_dispersed
else:
    print('ERROR: either specify one value for num_clustered or one value for num_dispersed')

region=['DMS','DLS']
base_time=[par.start-par.dur,par.start]

isis={reg:{str(c):[] for c in num_stim} for reg in region}
num_spikes={reg:{str(c):[] for c in num_stim} for reg in region}
plateauVm={reg:{str(c):[] for c in num_stim} for reg in region}
decay10={reg:{str(c):[] for c in num_stim} for reg in region}
dur={reg:{str(c):[] for c in num_stim} for reg in region}
plat_trials={reg:{str(c):0 for c in num_stim} for reg in region} #number of trials used to calculate plateau and decay
inst_freq={reg:{str(c):[] for c in num_stim} for reg in region}
#rise_time={reg:{str(c):[] for c in num_stim} for reg in region}
trials={reg:{} for reg in region}
rows=[]

#for spn in ['Mat3', 'Mat2']:
for reg in region:
    for ii,nstim in enumerate(num_stim):
        nc=str(nstim)
        if len(par.end_time)==1:
            et=par.end_time[0]
        elif len(par.end_time)==len(par.num_clustered):
            et=par.end_time[ii]
        else:
            print('ERROR: specify either 1 end_time or 1 per num_clustered, instead of', par.end_time)
        if len(par.num_dispersed)==1:
            pattern='D1*BLA_'+reg+'_'+'_'.join([str(num_disp),nc])
        else:
            pattern='D1*BLA_'+reg+'_'+'_'.join([nc,str(num_clust)])
        if par.dir:
            pattern=par.dir+pattern
        if par.dist:
            pattern=pattern+'*'+str(par.dist)
        if par.naf:
            fnames=glob.glob(pattern+'*NaF*0Vm.txt')
        else:
            fnames=glob.glob(pattern+'*0Vm.txt')
            fnames=remove_fn(fnames,'NaF')
        trials[reg][nc]=len(fnames)
        if len(fnames):
            print('files for ',nc,reg,':', fnames)
            plot_traces(fnames,reg,nc,par.start,et) 
            plateau_time=[float(et)-par.dur,float(et)] #measure Vm over 50 msec during plateau
            for fn in fnames:
                data=neur_text(fn)
                data.spikes(0) #calculate spike times, using 0 mV as threshold
                spk_tm=data.spiketime[data.soma_name[0]] #extract spike times of soma
                num_spikes[reg][nc].append(len(spk_tm))
                isi=np.nan #initialize as nan
                baseVm,start_pt,_=mean_Vm(data,base_time) #baseline Vm
                plateau,plat_start,peakVm=mean_Vm(data,plateau_time) #plateau Vm
                if not len(data.spiketime[data.soma_name[0]]): #if no spikes, measure plateau and decay time
                    #rise_time[reg][nc].append(1000*risetime(data,start_pt,0.15,baseVm))
                    dur[reg][nc].append(np.nan)#(1000*duration(data,baseVm,par.start,plat_start))
                    plateauVm[reg][nc].append(peakVm-baseVm) #plateau amplitude defined using peak.  If use plateau-baseVm, then could define it even with spikes
                    decay=decay_time(data,baseVm,peakVm, plat_start) #time to decay
                    decay10[reg][nc].append(1000*(decay-plateau_time[1])) #decay duration, in msec
                    plat_trials[reg][nc]+=1
                else:
                    decay10[reg][nc].append(np.nan)
                    plateauVm[reg][nc].append(np.nan) #plateau-baseVm - test this with example files
                    print('spikes for', fn)
                if len(data.spiketime[data.soma_name[0]])>1: #if more than 1 spike, calculate mean ISI
                    isi=np.diff(data.spiketime[data.soma_name[0]])
                    isis[reg][nc].append(isi)
                    inst_freq[reg][nc].append(np.mean(1/isi))
                    dur[reg][nc].append(data.spiketime[data.soma_name[0]][-1]-data.spiketime[data.soma_name[0]][0]) #time between 1st and last spike
                else:
                    dur[reg][nc].append(np.nan)
                if par.seed:
                    if str(par.seed) in fn:
                        plot_one_file(fn,data, par.start,et)
                #output for stat analysis
                parts=os.path.basename(fn).split('_')
                ndisp=parts[2]
                nclust=parts[3]
                maxdist=parts[6]
                if parts[7]=='NaF':
                    naf='1'
                    seed=parts[8].split('0Vm')[0]
                else: 
                    naf='0'
                    seed=parts[7].split('0Vm')[0]
                rows.append([reg,ndisp,nclust,maxdist,naf,seed,str(round(plateauVm[reg][nc][-1],3)),str(round(decay10[reg][nc][-1],1)), str(round(dur[reg][nc][-1],1)), str(len(spk_tm)),str(round(np.nanmean(1/isi),2))])
        else:
            print('no files found using pattern',pattern, 'with parameters',nc,reg)

#output for stat analysis, export and then read in and combine multiple files
if par.output:
    if parts[7]=='NaF':
       outfname='_'.join(parts[0:7])
    else:
       outfname='_'.join(parts[0:6])
    f=open(outfname+'.out','w')
    header='region  ndisp  nclust  maxdist   naf   seed  plateauVm  decay10  duration num_spk  inst_freq'
    np.savetxt(f,rows,fmt='%7s',header=header,comments='')  
    f.close()         
 
################## Results ###################
import scipy.stats as sps
for reg in region:
    if len(par.num_clustered)>=1 and len(par.num_dispersed)==1:
        print('***', num_disp, 'dispersed, ', reg,'trials=',[trials[reg]])
    else:
         print('***', num_clust, 'clustered, ', reg,'trials=',[trials[reg]])
    for nstim in num_stim:    
        nc=str(nstim)
        print( '  ', nc,'inputs, spikes=',np.round(np.mean(num_spikes[reg][nc]),3),'+/-',np.round(sps.sem(num_spikes[reg][nc],nan_policy='omit'),3))
        if len(isis[reg][nc]):
            print('        freq=',np.round(np.nanmean(inst_freq[reg][nc]),2),'+/-',np.round(sps.sem(inst_freq[reg][nc],nan_policy='omit'),2), 'from', len(isis[reg][nc]), 'trials')
            print('        mean dur of spiking',np.round(np.nanmean(dur[reg][nc]),1),'+/-',np.round(sps.sem(dur[reg][nc],nan_policy='omit'),1), 'in sec')
        else:
            print('        no frequency or spike dur, only 1 spike per trace')
        if not np.all(np.isnan(decay10[reg][nc])):
            print('        mean plateau',np.round(np.nanmean(plateauVm[reg][nc]),1),'+/-',np.round(sps.sem(plateauVm[reg][nc],nan_policy='omit'),1), 'in mV, n=',plat_trials[reg][nc])
            print('        mean decay',np.round(np.nanmean(decay10[reg][nc]),1),'+/-',np.round(sps.sem(decay10[reg][nc],nan_policy='omit'),1), 'in msec, n=',plat_trials[reg][nc])
            #print('        mean rise_time',np.round(np.nanmean(rise_time[reg][nc]),1),'+/-',np.round(sps.sem(rise_time[reg][nc],nan_policy='omit'),1), 'in sec, n=',plat_trials[reg][nc])


