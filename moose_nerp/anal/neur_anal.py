import numpy as np
import glob
import neur_anal_class as nac
import plot_utils as pu
import net_anal_utils as nau

filedir='/home/avrama/moose/moose_nerp/moose_nerp/ep/output/'
file_root='epPSP_'
param1=['str','GPe']
param2=[{'_freq': '10'},{'_freq': '20'},{'_freq': '40'},{'_freq': '5'}]#,{'_freq': '1'}]
param3=[{'_plas':'1','_inj':'-1e-11'}]
vmtab_index=0
start_stim=2.0#0.2
end_stim=2.0
transient=0.1
plot_cal=False
plot_traces=False
cal_measure='mean'
write_output=True
'''
#for calcium outputs
start_stim=1.0
filedir='/home/avrama/moose/moose_nerp/moose_nerp/ep/'
file_root='epAP_'
param1=['none']
param2=[{'_freq': '10'},{'_freq': '20'},{'_freq': '40'},{'_freq': '50'}]
param3=[{'_plas':'0','_inj':'0.00'}]
plot_cal=False
end_stim=4.0
'''
'''
to do:
1. cross_corr
'''
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
                vfiles=sorted(glob.glob(pattern+'*Vm.txt'))
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
            ################ text files with calcium concentration
            cfiles=sorted(glob.glob(pattern+'Ca.txt'))
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
        print([(data_set.spike_freq[p], data_set.inst_spike_freq[p]) for p in data_set.inst_spike_freq.keys()])
    if 'cdata' in globals():
        print('CALCIUM for ',cond)
        for k,v in cal_summary.items():
            line=sorted({comp:v[comp][cal_measure] for comp in v}.items(),key=lambda x:len(x[0]))
            print('    ',k[1:],line[0:4])
        columns=sorted(list(cdata.column_map.keys()),key=lambda x:len(x))
        soma_index=columns.index(cdata.soma_name)
        columns.insert(soma_index-1,columns.pop(soma_index))
        xdata=[float(list(p.values())[0]) for p in param2]
        cal_mean={col:[cal_summary[p][col][cal_measure] for p in cal_summary.keys()] for col in columns}
        pu.plot_dict(cal_mean,xdata,xlabel='Freq (Hz)',ftitle='calcium '+cal_measure)
    else:
        print('No CALCIUM files found for', cond)
#################### plot the set of results from single neuron simulations, range of input frequencies
    if 'neurtypes' in data_set.__dict__:
        if len(data_set.psp_amp[cond]):
            #pu.plot_freq_dep(data_set.psp_amp,data_set.stim_tt,'PSP amp (mV)',suffix,len(data_set.neurtypes),xlabel='stim number',scale=1000,offset=0.01)
            pu.plot_freq_dep(data_set.psp_norm,data_set.stim_tt,'norm PSP amp',suffix,len(data_set.neurtypes),xlabel='stim number',offset=0.02)
        if len(data_set.traces[cond]):
            pu.plot_freq_dep(data_set.traces,data_set.time,'Vm (mV)',suffix,len(data_set.neurtypes),scale=1000,offset=0.1)
        if plot_isis:
            pu.plot_freq_dep(data_set.isis,data_set.isi_x,'ISI (sec)',suffix,len(data_set.neurtypes),xlabel='Spike time (sec)')
    else:
        pu.plot_dict_of_dicts(data_set.psp_amp,ylabel='PSP amp',xlabel='stim number',ftitle=suffix)
        pu.plot_dict_of_dicts(data_set.psp_norm,ylabel='NORM PSP amp',xlabel='stim number',ftitle=suffix)
    if write_output:
        #transpose dictionaries
        import pandas as pd
        dfy=pd.DataFrame(data_set.psp_norm)
        output_dict=dfy.transpose().to_dict()
        dfx=pd.DataFrame(data_set.stim_tt)
        xvals=dfx.transpose().to_dict()
        for k1 in output_dict.keys():
            fname='psp_norm_'+k1
            header='  '.join(['psp_norm_'+k2+'_'+k1 for k2 in output_dict[k1].keys() ])
            outputdata=nau.choose_xvals(xvals[k1])
            for k2 in output_dict[k1].keys():
                outputdata=np.column_stack((outputdata,output_dict[k1][k2]['ep']))
            f=open(fname+".txt",'w')
            f.write(header+'\n')
            np.savetxt(f,outputdata,fmt='%.5f')
            f.close()
        if 'spike_freq' in data_set.__dict__:
            nau.write_dict_of_dicts(data_set.spike_freq,'fI'+suffix,'freq'+suffix)
        if 'cal_mean' in globals():
            nau.write_dict_of_dicts(cal_mean,xdata,'calcium'+suffix,'calcium'+suffix)


