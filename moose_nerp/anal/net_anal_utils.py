import numpy as np
from mnerp_net_output import calc_one_sta

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def calc_mean_std(data_input,axisnum=0):
    meanval=np.nanmean(data_input,axis=axisnum)
    stdval=np.nanstd(data_input,axis=axisnum)
    return meanval,stdval

def time_stuff(xbins,spikes):
    import time
    start_time=time.clock()
    inst_rate=np.zeros(len(xbins))
    for i,binmin in enumerate(xbins):
        inst_rate[i]=len(set(np.where(spikes<(binmin+binsize))[0]) &  set(np.where(spikes>binmin)[0]))/binsize
    print('method np.where',time.clock()-start_time)
    start_time=time.clock()
    inst_rate=np.zeros(len(xbins))
    for i,binmin in enumerate(xbins):
        inst_rate[i]=len([st for st in spikes if st>=binmin and st<binmin+binsize])/binsize
    print('method list',time.clock()-start_time)

def accumulate_over_params(newdata,datadict,param):
    for neur in newdata.keys():
        if neur in datadict.keys():
            datadict[neur][param]=newdata[neur]
        else:
            datadict[neur]={param:newdata[neur]}
    return datadict

def sta_fire_freq(input_spike_rate,spike_list,sta_start,sta_end,xbins,weights=None):
    #both input_spike_rate and spike_list must have same number of trials (each is list)
    binsize=xbins[1]
    window=(int(sta_start/binsize),int(sta_end/binsize))
    if weights is None:
        weights={syn:-1 if syn.startswith('gaba') else 1 for syn in input_spike_rate.keys()}
    weighted_input_spike_rate=[np.zeros(len(xbins)) for trial in range(len(spike_list))]
    prespike_sta={syn:[] for syn in list(input_spike_rate.keys())+['sum']}
    for trial in range(len(spike_list)):
        spike_times=spike_list[trial][0] #THIS ASSUMES ONLY A SINGLE NEURON - NEED TO FIX WITH NETWORK SIMULATIONS
        for syn in input_spike_rate.keys():
            weighted_input_spike_rate[trial]+=weights[syn]*input_spike_rate[syn][trial] 
            prespike_sta[syn].append(calc_one_sta(spike_times,window,input_spike_rate[syn][trial],binsize))
        prespike_sta['sum'].append(calc_one_sta(spike_times,window,weighted_input_spike_rate[trial],binsize))
        xvals=np.arange(sta_start,sta_end,binsize)
    prespike_sta_mean={};prespike_sta_std={}
    for key in prespike_sta.keys():
        prespike_sta_mean[key],prespike_sta_std[key]=calc_mean_std(prespike_sta[key],axisnum=0)
    return prespike_sta,prespike_sta_mean,prespike_sta_std,xvals

def choose_xvals(xvals):
    if isinstance(xvals,dict):
        param1=list(xvals.keys())[0]
        if isinstance(xvals[param1],dict):
            param2=list(xvals[param1].keys())[0]
            x=xvals[param1][param2]
            print('xvals are dict of dict ', xvals.keys(),xvals[param1].keys())
        else:
            print('xvals are dict ', xvals.keys())
            x=xvals[param1]
    else:
        print('xvals is list or array or length',len(xvals))
        x=xvals
    return x

def cross_corr(pre_spikes,post_spikes,t_end,binsize):
    import elephant
    from neo.core import AnalogSignal,SpikeTrain
    from elephant.conversion import BinnedSpikeTrain
    import quantities as q
    #
    def elph_train(spike_set,t_end,binsize):
        if isinstance(spike_set, list):
            spikes = np.sort(np.concatenate([st for st in spike_set])) #1D array, spikes of all input synapses
        else:
            spikes=spike_set
        train=SpikeTrain(spikes*q.s,t_stop=np.ceil(spikes[-1])*q.s)
        return BinnedSpikeTrain(train,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
    #
    numtrials=len(post_spikes)
    cc_hist={k:[[] for t in range(numtrials)] for k in pre_spikes[0].keys()}
    for trial_in in range(len(pre_spikes)): 
        for pre,spike_set in pre_spikes[trial_in].items():
            in_train=elph_train(spike_set,t_end,binsize)
            for trial_out in range(numtrials):
                out_train=elph_train(post_spikes[trial_out],t_end,binsize)
                #print('trial_in,trial_out', trial_in, trial_out)
                cc_hist[pre][trial_in].append(elephant.spike_train_correlation.cross_correlation_histogram(in_train,out_train)[0].magnitude[:,0])
    mean_cc={};mean_cc_shuffle={};cc_shuffle_corrected={}
    for pre in cc_hist.keys():
        #shuffle corrected mean cross-correlogram
        cc_same=[cc_hist[pre][a][a] for a in range(numtrials)]
        mean_cc[pre]=np.mean(cc_same,axis=0)
        cc_diff=[cc_hist[pre][a][b] for a in range(numtrials) for b in range(numtrials) if b != a ]
        mean_cc_shuffle[pre]=np.mean(cc_diff,axis=0)
        cc_shuffle_corrected[pre]=mean_cc[pre]-mean_cc_shuffle[pre]
    xbins=elephant.spike_train_correlation.cross_correlation_histogram(in_train,out_train)[0].times
    return mean_cc,mean_cc_shuffle,cc_shuffle_corrected,xbins
############
def write_data_header(fname,header,outputdata):
    f=open(fname+".txt",'w')
    f.write(header+'\n')
    np.savetxt(f,outputdata,fmt='%.5f')
    f.close()

def write_dict_of_dicts(meandata,xdata, fname,varname,stddata=None,xheader='Time'):
    header=xheader+' '
    outputdata=choose_xvals(xdata)
    for key1 in meandata.keys():
        for key2 in meandata[key1].keys():
            if len(meandata.keys())>1:
                colname=key1+'_'+key2+'_'
            else:
                colname=key2+'_'
            if stddata is not None:
                header=header+colname+varname+'_mean '+colname+varname+'_std '
            else:
                header=header+colname+varname+'_mean '
            outputdata=np.column_stack((outputdata,meandata[key1][key2]))
            if stddata is not None:
                outputdata=np.column_stack((outputdata,stddata[key1][key2]))
    write_data_header(fname,header,outputdata)   
############ 
def write_dict_of_epochs(meandata,xdata,fname,varname,num_keys,stddata=None,xheader='Time'):
    header=xheader+' '
    outputdata=[v for val in xdata.values() for v in val]
    reshaped_mean=np.zeros((len(outputdata),num_keys))
    if stddata is not None:
        reshaped_std=np.zeros((len(outputdata),num_keys))
    for i,key1 in enumerate(meandata.keys()):
        for j,key2 in enumerate(meandata[key1].keys()):
            reshaped_mean[i*len(xdata[key1]):(i+1)*len(xdata[key1]),j]=meandata[key1][key2]
            header=header+key2+'_'+varname+'_mean '
            if stddata is not None:
                header=header+key2+'_'+varname+'_std '
                reshaped_std[i*len(xdata[key1]):(i+1)*len(xdata[key1]),j]=stddata[key1][key2]
    outputdata=np.column_stack((outputdata,reshaped_mean))
    if stddata is not None:
        outputdata=np.column_stack((outputdata,reshaped_std))
    write_data_header(fname,header,outputdata)   
    
############ 
def write_triple_dict(meandata,fname,varname,stddata=None,xdata=None,xheader='Time'):
    header=xheader+' '
    if xdata is not None:
        outputdata=choose_xvals(xdata)
    else:
        outputdata=range(len(ydata))
        header='stim_num'
    for key1 in meandata.keys():
        for key2 in meandata[key1].keys():
            for key3 in meandata[key1][key2].keys():
                if len(meandata.keys())>1:
                    header=header+key1+'_'+key2+'_'+key3+'_'+varname+'_mean '+key1+'_'+key2+'_'+key3+'_'+varname+'_std '
                else:
                    header=header+key2+'_'+key3+'_'+varname+'_mean '+key2+'_'+key3+'_'+varname+'_std '
                outputdata=np.column_stack((outputdata,meandata[key1][key2][key3],stddata[key1][key2][key3]))
    write_data_header(fname,header,outputdata)   

def write_transpose(psp_norm,stim_tt,ntype,varname):
    import pandas as pd
    dfy=pd.DataFrame(psp_norm)
    output_dict=dfy.transpose().to_dict()
    dfx=pd.DataFrame(stim_tt)
    xvals=dfx.transpose().to_dict()
    for k1 in output_dict.keys():
        fname=varname+'_'+k1
        header='  '.join([varname+'_'+k2+'_'+k1 for k2 in output_dict[k1].keys() ])
        outputdata=schoose_xvals(xvals[k1])
        for k2 in output_dict[k1].keys():
            outputdata=np.column_stack((outputdata,output_dict[k1][k2][ntype]))
        write_data_header(fname,header,outputdata)

def print_con(confile_name):
    import glob
    confiles=glob.glob(confile_name)
    for f in confiles:
        data=np.load(f,'r',allow_pickle=True)
        print ('########### ', f,' ##############')
        for ntype,conns in data['summary'].item().items():
            for syn in conns['intra']:
                for presyn in conns['intra'][syn].keys():
                    print(ntype,syn,'presyn=',presyn,'mean inputs=',np.round(np.mean(conns['intra'][syn][presyn]),2) )
                    short=[y for y in conns['shortage'][syn].values()]
                    print_short=np.mean(short) if np.mean(short)==0 else short
                    print('shortage',print_short)
'''  
#Possibly add this to mnerp_net_output?                  
connect=dat['params'].item()['connect_dict']
print ('########### ', fname,' ##############')
for row in connect:
    print(row)
'''
