import numpy as np
import glob
import sys
from moose_nerp.anal.neur_anal_class import neur_text

def plot_traces(fnames,reg,spn):
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
    return fig   

def mean_Vm(dat,time_vals):
    points=[]
    for bt in time_vals:
        points.append(np.where(dat.time>=bt)[0][0])
    baseVm=np.mean(dat.traces[dat.soma_name[0]][points[0]:points[1]])
    return baseVm,points[1]

def decay_time(dat,base_val,plateau_val,pt):
    amp=plateau_val-base_val
    thresh=0.1*amp+base_val #90% decayed to baseline
    decay_pt= np.where(dat.traces[dat.soma_name[0]][pt:]<thresh) #start search at end of plateau
    if len(decay_pt[0]):
        decay=dat.time[decay_pt[0][0]+pt] #add in pt because np.where indexes start of search at 0
    else:
        decay=dat.simtime
    return decay

suffix=sys.argv[1]
end_disp=sys.argv[2]
#suffix='_70_' #for debugging, number of dispersed inputs
#end_disp='0.39'

region=['DMS','DLS']
clust=['0','16', '20']
dur=0.05 #measure Vm over 50 msec for baseline
base_time=[0.1-dur,0.1]
plateau_time=[float(end_disp)-dur,float(end_disp)] #measure Vm over 50 msec during plateau

isis={reg:{c:[] for c in clust} for reg in region}
num_spikes={reg:{c:[] for c in clust} for reg in region}
plateauVm={reg:{c:[] for c in clust} for reg in region}
decay10={reg:{c:[] for c in clust} for reg in region}
plat_trials={reg:{c:0 for c in clust} for reg in region} #number of trials used to calculate plateau and decay
inst_freq={reg:{} for reg in region}
trials={reg:{} for reg in region}
#for spn in ['Mat3', 'Mat2']:
for reg in region:
    for spn in clust:    
        #pattern='D1'+spn+'BLA_'+reg+suffix+'*0Vm.txt'
        pattern='D1*BLA_'+reg+suffix+spn+'*0Vm.txt'
        fnames=glob.glob(pattern)
        trials[reg][spn]=len(fnames)
        if len(fnames):
            print('files for ',spn,reg,':', fnames)
            plot_traces(fnames,reg,spn) 
            for fn in fnames:
                data=neur_text(fn)
                data.spikes(0) #calculate spike times, using 0 mV as threshold
                spk_tm=data.spiketime[data.soma_name[0]] #extract spike times of soma
                num_spikes[reg][spn].append(len(spk_tm)) 
                if not len(data.spiketime[data.soma_name[0]]): #if no spikes, measure plateau and decay time
                    baseVm,_=mean_Vm(data,base_time) #baseline Vm
                    plateau,plat_start=mean_Vm(data,plateau_time) #plateau Vm
                    plateauVm[reg][spn].append(plateau-baseVm) #plateau amplitude
                    decay=decay_time(data,baseVm,plateau, plat_start) #time to decay
                    decay10[reg][spn].append(1000*(decay-plateau_time[1]))
                    plat_trials[reg][spn]+=1
                if len(data.spiketime[data.soma_name[0]])>1: #if more than 1 spike, calculate mean ISI
                    isis[reg][spn].append(np.diff(data.spiketime[data.soma_name[0]]))
            if len(isis[reg][spn]):
                inst_freq[reg][spn]=np.mean([np.mean(1/isi) for isi in isis[reg][spn]])  #from ISIs, calculate mean instaneous frequency
        else:
            print('no files found using pattern',pattern, 'with parameters',spn,reg)

################## Results ###################33
for reg in region:
    print('**', reg,'trials=',[trials[reg][c] for c in clust])
    for spn in clust:    
        print( '  ', spn,'inputs, spikes=',round(np.mean(num_spikes[reg][spn]),3),'+/-',round(np.std(num_spikes[reg][spn])/np.sqrt(len(fnames)),3))
        if len(isis[reg][spn]):
            print('        freq=',round(inst_freq[reg],2), 'from', len(isis[reg][spn]), 'trials')
        else:
            print('        no frequency, only 1 spike per trace')
        if len(decay10[reg][spn]):
            print('        mean plateau',round(np.mean(plateauVm[reg][spn]),1),'+/-',round(np.std(plateauVm[reg][spn])/np.sqrt(plat_trials[reg][spn]),2), 'in mV, n=',plat_trials[reg][spn])
            print('        mean decay',round(np.mean(decay10[reg][spn]),1),'+/-',round(np.std(decay10[reg][spn])/np.sqrt(plat_trials[reg][spn]),2), 'in msec, n=',plat_trials[reg][spn])
        else:
            print('all traces had spikes')
