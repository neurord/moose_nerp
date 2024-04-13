import numpy as np
import glob
import sys
from moose_nerp.anal.neur_anal_class import neur_text

def plot_traces(fnames,reg):
    from matplotlib import pyplot as plt
    plt.ion()
    fig=plt.figure()
    fig.suptitle(reg)
    for fn in fnames:
        data=neur_text(fn)
        data.seed=fn.split('_')[-1].split('0Vm.txt')[0]
        plt.plot(data.time,data.traces[data.soma_name[0]], label=data.seed)
        plt.legend()
    return fig   

region=['DMS','DLS']
suffix=sys.argv[1]

isis={reg:[] for reg in region}
num_spikes={reg:[] for reg in region}
inst_freq={}

for reg in region:
    fnames=glob.glob('BLA_'+reg+'_dispersed*'+suffix+'*0Vm.txt')
    plot_traces(fnames,reg) 
    for fn in fnames:
        data=neur_text(fn)
        data.spikes(0)
        num_spikes[reg].append(len(data.spiketime[data.soma_name[0]]))
        if len(data.spiketime[data.soma_name[0]])>1:
            isis[reg].append(np.diff(data.spiketime[data.soma_name[0]]))
    inst_freq[reg]=np.mean([np.mean(1/isi) for isi in isis[reg]])
    print(reg,'spikes=',np.mean(num_spikes[reg]),round(np.std(num_spikes[reg]),2),'freq=',round(inst_freq[reg],2), 'from', len(isis[reg]), 'trials')
    #plot_traces(fnames,reg)
    
