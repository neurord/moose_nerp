#Functions for calculating ISI, latency, psp_amplitude for a set of files
import glob
import numpy as np
import moose
import detect

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def find_somatabs(tabset,soma_name,tt=None,print_comp=True):
    #find the table(s) with vm from the soma
    comp_names=[tab.neighbors['requestOut'][0].name for tab in tabset]
    soma_tabs=[tab for tab in tabset if tab.neighbors['requestOut'][0].name==soma_name]
    if print_comp:
        print ('ISI_ANAL: vm tables {}, soma vmtab={}, comp={}'.format(comp_names,soma_tabs,[st.neighbors['requestOut'][0].path for st in soma_tabs]))
    #if no soma tables found (perhaps wrong name) use the last one, which might be soma
    #or send back number of tables equal to number of time tables 
    ######## Needs more debugging for network simulation #################3
    if len(soma_tabs)==0:
        if tt:
            num_tabs=len(tt)
        else:
            num_tabs=1
        soma_tabs=comp_names[-num_tabs:]
    return soma_tabs
    
def spike_isi_from_vm(vmtab,simtime,soma='soma',print_comp=True):
    spike_time={key:[] for key in vmtab.keys()}
    numspikes={key:[] for key in vmtab.keys()}
    isis={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        soma_tabs=find_somatabs(tabset,soma,print_comp=print_comp)
        for tab in soma_tabs:
            spike_time[neurtype].append(detect.detect_peaks(tab.vector)*tab.dt)
            isis[neurtype].append(np.diff(spike_time[neurtype][-1]))
            numspikes[neurtype]=[len(st) for st in spike_time[neurtype]]
        print(neurtype,'mean spikes:',np.mean(numspikes[neurtype]),', spike rate',np.mean(numspikes[neurtype])/simtime)
        if print_comp:
            print('   calculated from',numspikes[neurtype],'spikes, \nISI mean&STD: ',[np.mean(isi) for isi in isis[neurtype]], [np.std(isi) for isi in isis[neurtype]])
    return spike_time,isis

def stim_spikes(spike_time,timetables,soma='soma'):
    stim_spikes={key:[] for key in spike_time.keys()}
    for neurtype, tabset in spike_time.items():
        for tab,tt in zip(tabset,timetables[neurtype].values()):
            stim_spikes[neurtype].append([st for st in spike_time[neurtype][-1] if st>np.min(tt.vector) and st<np.max(tt.vector)])
    return stim_spikes

def psp_amp(vmtab,timetables,soma='soma',peak='min'):
    psp_amp={key:[] for key in vmtab.keys()}
    psp_norm={key:[] for key in vmtab.keys()}
    for neurtype, tabset in vmtab.items():
        soma_tabs=find_somatabs(tabset,soma,tt=timetables[neurtype].values())
        for tab,tt in zip(soma_tabs,timetables[neurtype].values()):
            vm_init=[tab.vector[int(t/tab.dt)] for t in tt.vector]
            print('PSPAMP, vm_init',vm_init)
            #use np.min for IPSPs and np.max for EPSPs
            if peak=='min':
                vm_peak=[np.min(tab.vector[int(tt.vector[i]/tab.dt):int(tt.vector[i+1]/tab.dt)]) for i in range(len(tt.vector)-1)]
            else:
                vm_peak=[np.max(tab.vector[int(tt.vector[i]/tab.dt):int(tt.vector[i+1]/tab.dt)]) for i in range(len(tt.vector)-1)]
            print('PSPAMP, vm_peak',vm_peak)
            psp_amp[neurtype].append([(vm_peak[i]-vm_init[i]) for i in range(len(vm_peak))])
            psp_norm[neurtype].append([amp/psp_amp[neurtype][-1][0] for amp in psp_amp[neurtype][-1]])
    return psp_amp,psp_norm

############# Call this from multisim, after import ISI_anal
#  ISI_anal.save_tt(connections)
def save_tt(connections,param_sim):
    import moose
    used_tt={}
    for syntype in connections['ep']['/ep'].keys():
        used_tt[syntype]={}
        for ext in connections['ep']['/ep'][syntype].keys():
            used_tt[syntype][ext]={}
            for syn in connections['ep']['/ep'][syntype][ext].keys():
                tt=moose.element(connections['ep']['/ep'][syntype][ext][syn])
                used_tt[syntype][ext][syn]=tt.vector
    np.save('tt'+param_sim.fname,used_tt)

