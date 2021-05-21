import numpy as np
import glob
import sys
import neur_anal_class as nac
import plot_utils as pu
import net_anal_utils as nau

try:
    args = ARGS.split(" ")
    print("ARGS =", ARGS, "commandline=", args)
    do_exit = False
except NameError: #NameError refers to an undefined variable (in this case ARGS)
    args = sys.argv[1:]
    print("commandline =", args)
    do_exit = True

if args[0]=='PSP':
    filedir=args[1] #'/home/avrama/moose/moose_nerp/moose_nerp/ep/output/'
    file_root=args[2] #'epPSP_'
    param1=['str','GPe']
    param2=[{'_freq': '10'},{'_freq': '20'},{'_freq': '40'},{'_freq': '5'}]#,{'_freq': '1'}]
    param3=[{'_plas':'1','_inj':'-1e-11'}]
    vmtab_index=0
    start_stim=2.0#0.2
    end_stim=2.0
else:
    #for different types of current injection
    filedir=args[1] #'/home/avrama/moose/moose_nerp/moose_nerp/ep/output/'
    file_root=args[2] #'epAP_'
    PSP=False
    param1=['none']
    #param2=[{'_freq': '10'},{'_freq': '20'},{'_freq': '40'},{'_freq': '50'}]
    #param3=[{'_plas':'0','_inj':'0.00'}]#,{'_plas':'1','_inj':'0.00'}]
    param2=[{'_freq': '0','_plas':'0'}]
    ##param3=[{'_inj':'0'},{'_inj':'0.025'},{'_inj':'0.05'},{'_inj':'-0.1'},{'_inj':'-0.2'}]
    param3=[{'_inj':'00'},{'_inj':'00.025'},{'_inj':'00.05'},{'_inj':'00.075'},{'_inj':'00.1'},{'_inj':'00.15'},{'_inj':'00.2'}]
    start_stim=0.2 #start time for stimulation
    end_stim=0.6 #end time for stimulation, or set equal to start_stim to avoid analyzing firing rate during stim
    transient=0.1

plot_cal=False
plot_traces=True
cal_measure='mean' #could also plot 'max' or 'min'
write_output=False
fI={} #accumulate firing rate vs inject.  Only needed if len(param3)>1
for parset in param3: #generate new fig each time through this loop
    #initialize structures to hold data
    plot_isis=False
    data_set=nac.neur_set(param1)
    cal_summary={}
    for cond in param1:
        for params in param2:
            #construct filename and key for data_set dictionaries
            key=''.join([str(k)+str(v) for k,v in params.items()])
            suffix=''.join([str(k)+str(v) for k,v in parset.items()])
            pattern=filedir+file_root+cond+key+suffix
            ################ npz files, with Vm, and possibly spiketimes and ISIs, synaptic stim time
            nfiles=sorted(glob.glob(pattern+'*.npz'))
            if len(nfiles)==0:
                print('******* no npz files found using',pattern)
                vfiles=sorted(glob.glob(pattern+'Vm.txt'))
                if len(vfiles):
                    print('----->analyzing txt files')
                    ## Extract parameters from file name
                    if '_inj' in parset.keys():
                        inj=parset['_inj']
                    elif '_inj' in params.keys():
                        inj=params['_inj']
                    else:
                        inj=0
                    if '_freq' in params.keys():
                        freq=params['_freq']
                    else:
                        freq=0
                    ### store data in structure similar to calcium
                    data=nac.neur_text(vfiles[0])
                    data.spikes(inj)
                    if int(freq)>0:
                        data.psp_amp(start_stim,freq)
                    data_set.add_data(data,cond,key)
                    if plot_traces:
                        pu.plot_dict(data.traces,data.time,ylabel='Vm (V)',ftitle=suffix+key)
                else:
                    print('************ !!!!!!!!!!! no files found using',pattern)
                   
            elif len(nfiles)>1:
                print('***** multiple npz files found using',pattern)
            else:
                fname=nfiles[0]
                ##### create neur_output object for each file, add to data_set
                data=nac.neur_npz(fname)
                if len(data.isis):
                    plot_isis=True
                data.psp_amp()
                data_set.add_data(data,cond,key)
                freq=data.freq
                inj=data.inj
            ################ text files with calcium concentration
            cfiles=sorted(glob.glob(pattern+'Ca.txt')) #+str(float(parset['_inj'])*1e9)
            if len(cfiles)==0:
                print('************ no txt files for calcium found using',pattern+'Ca.txt')
            elif len(cfiles)>1:
                print('***** multiple txt files found using',pattern+'Ca.txt')
            else:
                fname=cfiles[0]
                cdata=nac.neur_text(fname)
                cdata.cal_stats(start_stim,transient)
                cal_summary[key+suffix]=cdata.cal_min_max_mn
                if plot_cal:
                    pu.plot_dict(cdata.traces,cdata.time,ylabel='Calcium (uM)',ftitle=suffix+key)
    if end_stim>start_stim:
        data_set.freq_inj_curve(start_stim,end_stim)
        print(suffix,[(data_set.spike_freq[p], data_set.inst_spike_freq[p]) for p in data_set.inst_spike_freq.keys()])
        fI[suffix]=data_set.inst_spike_freq
    if 'cdata' in globals():
        print('CALCIUM for ',cond)
        for k,v in cal_summary.items():
            line=sorted({comp:v[comp][cal_measure] for comp in v}.items(),key=lambda x:len(x[0]))
            print('    ',k[1:],line[0:4])
        columns=sorted(list(cdata.column_map.keys()),key=lambda x:len(x))
        soma_index=columns.index(cdata.soma_name[0]) #FIXME for multiple neuron types in simulation
        columns.insert(soma_index-1,columns.pop(soma_index))
        xdata=[float(list(p.values())[0]) for p in param2]
        cal_mean={col:[cal_summary[p][col][cal_measure] for p in cal_summary.keys()] for col in columns}
        if len(xdata)>1:
            pu.plot_dict(cal_mean,xdata,xlabel='Freq (Hz)',ftitle='calcium '+cal_measure)
    else:
        print('No CALCIUM files found for', cond)
    #################### plot the set of results from single neuron simulations, range of input frequencies
    if args[0]=='PSP':
        if 'neurtypes' in data_set.__dict__:
            #pu.plot_freq_dep(data_set.psp_amp,data_set.stim_tt,'PSP amp (mV)',suffix,len(data_set.neurtypes),xlabel='stim number',scale=1000,offset=0.01)
            pu.plot_freq_dep(data_set.psp_norm,data_set.stim_tt,'norm PSP amp',suffix,len(data_set.neurtypes),xlabel='stim number',offset=0.02)
        else:
            pu.plot_dict_of_dicts(data_set.psp_amp,ylabel='PSP amp',xlabel='stim number',ftitle=suffix)
            pu.plot_dict_of_dicts(data_set.psp_norm,ylabel='NORM PSP amp',xlabel='stim number',ftitle=suffix)
    if len(data_set.traces[cond]) and plot_traces and int(freq)>0:
        ####### Doesn't work if file has data for multiple compartments per neuron ######
        pu.plot_freq_dep(data_set.traces,data_set.time,'Vm (mV)',suffix,len(data_set.neurtypes),scale=1000,offset=0.1)
    if plot_isis:
        pu.plot_freq_dep(data_set.isis,data_set.spiketime,'ISI (sec)',suffix,len(data_set.neurtypes),xlabel='Spike time (sec)')
    if write_output:
        if args[0]=='PSP':
            nau.write_transpose(data_set.psp_norm,data_set.stim_tt,'ep','psp_norm')
        if 'spike_freq' in data_set.__dict__:
            nau.write_dict_of_dicts(data_set.spike_freq,xdata,'fI'+suffix,'freq'+suffix)
        if 'cal_mean' in globals() and len(cal_mean)>1:
            header='stimfreq   '+' '.join(['cal_'+k.split('[')[0] for k in cal_mean.keys()])
            outputdata=xdata
            for k,vals in cal_mean.items():
                outputdata=np.column_stack((outputdata,vals))
            nau.write_data_header('calcium'+suffix,header,outputdata)

'''
to do:
1. cross_corr
'''
