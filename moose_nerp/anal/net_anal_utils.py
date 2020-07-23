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

############ 
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
    f=open(fname+".txt",'w')
    f.write(header+'\n')
    np.savetxt(f,outputdata,fmt='%.5f')
    f.close()
    
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
    f=open(fname+".txt",'w')
    f.write(header+'\n')
    np.savetxt(f,outputdata,fmt='%.5f')
    f.close()
    
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
    f=open(fname+".txt",'w')
    f.write(header+'\n')
    np.savetxt(f,outputdata,fmt='%.5f')
    f.close()

