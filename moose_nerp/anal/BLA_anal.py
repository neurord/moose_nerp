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

region=['DMS','DLS']
suffix=sys.argv[1]


#for spn in ['Mat3', 'Mat2']:
for spn in ['0','16']:    
    isis={reg:[] for reg in region}
    num_spikes={reg:[] for reg in region}
    inst_freq={}
    for reg in region:
        #pattern='D1'+spn+'BLA_'+reg+suffix+'*0Vm.txt'
        pattern='D1*BLA_'+reg+suffix+spn+'*0Vm.txt'
        fnames=glob.glob(pattern)
        if len(fnames):
            print('files for ',spn,reg,':', fnames)
            plot_traces(fnames,reg,spn) 
            for fn in fnames:
                data=neur_text(fn)
                data.spikes(0)
                spk_tm=data.spiketime[data.soma_name[0]]
                num_spikes[reg].append(len(spk_tm[spk_tm<0.5]))
                if len(data.spiketime[data.soma_name[0]])>1:
                    isis[reg].append(np.diff(data.spiketime[data.soma_name[0]]))
            inst_freq[reg]=np.mean([np.mean(1/isi) for isi in isis[reg]])
            print(reg,spn, 'spikes=',np.mean(num_spikes[reg]),'+/-',round(np.std(num_spikes[reg]),2),'freq=',round(inst_freq[reg],2), 'from', len(isis[reg]), 'trials')
            #plot_traces(fnames,reg)
        else:
            print('no files found using pattern',pattern, 'with parameters',spn,reg)

