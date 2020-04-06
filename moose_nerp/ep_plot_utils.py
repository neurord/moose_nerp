import numpy as np
import os
from matplotlib import pyplot as plt
import ISI_anal
#colors=['r','k','b','m']
colors=plt.get_cmap('viridis')
num_colors=(len(colors.colors)-1)*0.75 #avoid the light colors by using only partial scale
colors2D=[colors,plt.get_cmap('magma'),plt.get_cmap('Blues'),plt.get_cmap('gist_heat')]
offset=[0,0,63]  #avoid the light colors in low indices for the 'Blues' map

def colornum(list_index,whole_list):
    return int(list_index*(colors.N/len(whole_list)))

def plot_dict_of_dicts(rootname,mean_dict,filesuffix,ylabel,std_dict={},xarray=[],xlabel='time (sec)'):
    fig,axes =plt.subplots(len(mean_dict),1,sharex=True)
    axis=fig.axes
    for i,synstim in enumerate(mean_dict.keys()):
        for k,key in enumerate(mean_dict[synstim].keys()):
            if len(xarray):
                xvals=xarray[key]
            else:
                xvals=range(len(mean_dict[synstim][key]))
            axis[i].plot(xvals,mean_dict[synstim][key],label=str(key)+' mean',color=colors.__call__(colornum(k,mean_dict[synstim].keys())))
            if len(std_dict):
                axis[i].plot(xvals,std_dict[synstim][key],label=str(key)+' std',linestyle='dashed',color=colors.__call__(colornum(k,mean_dict[synstim].keys())))
        axis[i].set_xlabel(xlabel)
        axis[i].set_ylabel(synstim+' sec')
        fig.suptitle(ylabel+' '+rootname+filesuffix.split('.')[0][0:30])
        axis[i].legend()

def plot_ISI_cond(all_isi_mean,bins,group_by_presyn_set):
    if group_by_presyn_set:
        num_rows=len(all_isi_mean.keys())
    else:
        num_rows=np.max([len(d) for d in all_isi_mean.values()])
    fig,axes =plt.subplots(num_rows,1,sharex=True)
    axis=fig.axes
    fig.suptitle('ISI mean: all conditions')
    for j,cond in enumerate(all_isi_mean.keys()): 
        for i,synstim in enumerate(all_isi_mean[cond].keys()):
            presyn=synstim.split('_')[0]
            freq=synstim.split('_')[1]
            if group_by_presyn_set:
                ax=j
                color_index=i;all_items=all_isi_mean[cond].keys()
                plotlabel=synstim
            else:
                ax=i
                color_index=j;all_items=all_isi_mean.keys()
                plotlabel=cond
            for k,key in enumerate(bins.keys()):
                label=plotlabel if k==0 else ""
                axis[ax].plot(bins[key],all_isi_mean[cond][synstim][key],label=label,color=colors.__call__(colornum(color_index,all_items)))
            axis[ax].set_xlabel('time (sec)')
            axis[ax].set_ylabel(presyn+' input, isi (sec)')
    axis[ax].legend(loc='lower left')
    
def plot_postsyn_raster(rootname,suffix,spiketime_dict,syntt_info):
    ####### Raster plot of spikes in post-synaptic neuron #############
    fig,axes =plt.subplots(len(spiketime_dict), 1,sharex=True)
    fig.suptitle('output '+rootname+suffix)
    axis=fig.axes
    maxtime=0
    for ax,key in enumerate(spiketime_dict.keys()):
        maxtime=max(maxtime,np.max([np.max(m) for m in spiketime_dict[key]]))
        print(key,'max time=',np.round(maxtime,3), 'mean freq',np.round(np.mean([len(m)/maxtime for m in spiketime_dict[key]]),3))
        axis[ax].eventplot(spiketime_dict[key])
        axis[ax].set_ylabel(key+' trial')
        if len(syntt_info[key]):
            xstart=syntt_info[key]['xstart']
            xend=syntt_info[key]['xend']
            maxt=syntt_info[key]['maxt']
            axis[ax].annotate('stim onset',xy=(xstart,0),xytext=(xstart/maxt, -0.2),
                              textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05))
            axis[ax].annotate('offset',xy=(xend,0),xytext=(xend/maxt, -0.2),
                              textcoords='axes fraction', arrowprops=dict(facecolor='red', shrink=0.05))
    axis[-1].set_xlabel('time (sec)')
    axis[0].set_xlim(1.0,np.round(maxtime))
    return

#################### plot the set of results from single neuron simulations, range of input frequencies
##### either normalized PSPs if no spikes, or ISIs if spikes
def plot_freq_dep_psp(fileroot,presyn_set,suffix,neurtype):
    all_results={};all_xvals={}
    for i,presyn in enumerate(presyn_set):
        numplots,results,xval_set,xlabel,ylabel=ISI_anal.freq_dependence(fileroot,presyn,suffix)    
        all_results[presyn]=results
        all_xvals[presyn]=xval_set
    fig,axes =plt.subplots(numplots, len(presyn_set),sharex=True, sharey=True)
    fig.suptitle(neurtype+suffix)
    axis=fig.axes
    for i,presyn in enumerate(presyn_set):
        for k,freq in enumerate(sorted(all_results[presyn].keys())):
            for j,ntype in enumerate(all_results[presyn][freq].keys()):
                axisnum=i*len(all_results[presyn][freq].keys())+j
                for yval in all_results[presyn][freq][ntype]:
                    axis[axisnum].scatter(all_xvals[presyn][freq][ntype][0:len(yval)]-k*0.02,yval,label=str(ntype)+str(freq),marker='.')
                axis[axisnum].set_ylabel(str(presyn)+' '+ylabel)
            axis[axisnum].legend()
        axis[axisnum].set_xlabel(xlabel)
    return all_results,all_xvals

####### Membrane potential  #############
def plot_freq_dep_vm(fileroot,presyn_set,plasYN,inj,neurtype):
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle(' plasticity='+str(plasYN))
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+'*_plas'+str(plasYN)+'_inj'+inj+'*Vm.txt'
        files=ISI_anal.file_set(pattern)
        if len(files)>0:
            vm_set={}
            for fname in sorted(files):
                data=np.loadtxt(fname,skiprows=0)
                freq=fname.split('freq')[-1].split('_')[0]
                vm_set[freq]=(data[:,0],data[:,1])
            offset=0
            for freq,(tim,vm) in vm_set.items():
                offset=offset+2 #mV
                axis[ax].plot(tim,1000*vm+offset,label=freq)
        axis[ax].set_ylabel(presyn+' Vm (mV)')
        axis[ax].legend()
    axis[-1].set_xlabel('Time (sec)')

#################### Raster plot of pre-synaptic inputs 
def plot_input_raster(pre_spike_set,suffix,maxplots=None):
    colors=plt.get_cmap('viridis')
    #colors=plt.get_cmap('gist_heat')
    for param,pre_spikes in pre_spike_set.items():
        if maxplots:
            numplots=min(maxplots,len(pre_spikes))
        else:
            numplots=len(pre_spikes)
        for trial in range(numplots):
            fig,axes =plt.subplots(len(pre_spikes[trial].keys()), 1,sharex=True)
            fig.suptitle('input raster '+suffix+'_'+param+'_'+str(trial))
            axis=fig.axes
            for ax,(key,spikes) in enumerate(pre_spikes[trial].items()):
                color_num=[colornum(cellnum,spikes) for cellnum in range(len(spikes))]
                color_set=np.array([colors.__call__(color) for color in color_num])
                axis[ax].eventplot(spikes,color=color_set)
                axis[ax].set_ylabel(key)
            axis[-1].set_xlabel('time (s)')

def plot_sta_post_vm(pre_spikes,post_sta_dict,mean_sta_dict,post_xvals):
    for i,(synstim,sta_list) in enumerate(post_sta_dict.items()):
        fig,axes=plt.subplots(len(pre_spikes[synstim][0].keys()),1) 
        fig.suptitle('post sta '+synstim)
        axis=fig.axes
        for ax,(key,post_sta) in enumerate(sta_list.items()):
            for trial,sta in enumerate(post_sta):
                axis[ax].plot(post_xvals,sta,label=str(trial))
                axis[ax].set_ylabel(key+' trig')
            axis[ax].plot(post_xvals,mean_sta_dict[synstim][key],'k--',lw=3)
        axis[-1].set_xlabel('time (s)')
        #fig.tight_layout()

def plot_dict_of_lists(fileroot,list_dict,suffix,title,pre_xvals,std_dict=[]):
    fig,axes =plt.subplots(len(list_dict),1,sharex=True)
    axis=fig.axes
    fig.suptitle(title+' '+os.path.basename(fileroot+suffix).split('_')[0])
    for i,(synstim,trial_list) in enumerate(list_dict.items()):
        if np.ndim(trial_list)==2:
            for trial in range(len(trial_list)):
                axis[i].plot(pre_xvals,trial_list[trial],label='sta'+str(trial))
        else:
            axis[i].plot(pre_xvals,trial_list,label='spike_freq, Hz')
        if len(std_dict):
            summary=std_dict[synstim]
            label='std'
        else:
            summary=np.mean(trial_list,axis=0)
            label='mean'
        axis[i].plot(pre_xvals,summary,'k--',lw=2,label=label)
        axis[i].set_ylabel(synstim)
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

def plot_list_of_dict(yvalues,xvalues,mean_values=[],title=''):
    fig,axes=plt.subplots(len(yvalues[0].keys()),1) 
    fig.suptitle(title)
    axis=fig.axes
    for trial in range(len(yvalues)):
        for ax,(key,frate) in enumerate(yvalues[trial].items()):
            axis[ax].plot(xvalues,frate,label=str(trial))
            axis[ax].set_ylabel(key)
    if len(mean_values):
        for ax,(key,sta) in enumerate(mean_values.items()):
            axis[ax].plot(xvals,sta,'k--',lw=3)
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()

def plot_prespike_sta_cond(mean_prespike_sta,bins):
    fig,axis=plt.subplots(len(mean_prespike_sta[cond][synfreq].keys()),len(mean_prespike_sta[cond].keys()),sharex=True) 
    fig.suptitle('mean spike triggered average pre-synaptic firing')
    #need titles for each of the three columns
    for cond in mean_prespike_sta.keys():
        for axy,synfreq in enumerate(mean_prespike_sta[cond].keys()):
            for axx,(key,sta) in enumerate(mean_prespike_sta[cond][synfreq].items()):
                axis[axx,axy].plot(bins,sta,label=cond)
                axis[axx,0].set_ylabel(key)
            axis[-1,axy].set_xlabel('time (s)')
            axis[0,axy].title.set_text(synfreq)
        axis[0,0].legend()
    
def plot_sta_vm_cond(pre_xvals,sta_list_dict,mean_sta_vm):
    fig,axes=plt.subplots(len(sta_list_dict.keys()),sharex=True) 
    axis=fig.axes
    fig.suptitle('mean sta vm')
    for cond in mean_sta_vm.keys():
        for i,(synfreq,mean_sta) in enumerate(mean_sta_vm[cond].items()):
            axis[i].plot(pre_xvals,mean_sta,label=cond)
            axis[i].set_ylabel(synfreq+' Vm (V)')
    axis[-1].set_xlabel('time (s)')
    axis[-1].legend()
    
#Calculate and plot histograms
def plot_isi_hist(rootname,isi_set_dict,numbins,suffix):
    fig,axes =plt.subplots(len(isi_set_dict),1,sharex=True)
    axis=fig.axes
    fig.suptitle('histogram '+rootname+suffix.split('.')[0])
    symbol={'stim':'o-','pre':'.--','post':'.--'}
    for i,(synstim,isi_set) in enumerate(isi_set_dict.items()):
        presyn=synstim.split('_')[0]
        freq=synstim.split('_')[1]
        mins=[np.min(flatten(isi_set[k])) for k in isi_set.keys()]
        maxs=[np.max(flatten(isi_set[k])) for k in isi_set.keys()]
        min_max=[np.min(mins),np.max(maxs)]
        histbins=10 ** np.linspace(np.log10(min_max[0]), np.log10(min_max[1]), numbins)
        histbins=np.linspace(min_max[0],min_max[1], numbins)
        hist_ep={};CV={}
        for pre_post,ISIs in isi_set.items():
            hist_ep[pre_post],tmp=np.histogram(flatten(ISIs),bins=histbins,range=min_max)
            plot_bins=[(histbins[i]+histbins[i+1])/2 for i in range(len(histbins)-1)]
            #plt.bar(plot_bins,hist_ep[pre_post], label=pre_post)#,color=colors.__call__(color_num[i]),width=binwidth)
            axis[i].plot(plot_bins,hist_ep[pre_post],symbol[pre_post], label=pre_post)
            CV[pre_post]=np.std(flatten(ISIs))/np.mean(flatten(ISIs))
            print(synstim,pre_post,': ISI mean, std=', np.mean(flatten(ISIs)),np.std(flatten(ISIs)),' CV=',CV[pre_post])
        axis[i].set_ylabel(synstim+' events')
    axis[-1].legend()
    axis[-1].set_xlabel('ISI')
    return histbins,plot_bins

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

def plot_fft(condition,presyn_set,mean_fft_phase,freqs,fft_wave,fft_env):
    #2nd FFT
    colors=plt.get_cmap('viridis')
    num_colors=(len(colors.colors)-1)*0.75 #avoid the light colors by using only partial scale
    colors2D=[colors,plt.get_cmap('magma'),plt.get_cmap('Blues'),plt.get_cmap('gist_heat')]
    offset=[0,0,63]  #avoid the light colors in low indices for the 'Blues' map
    if len(condition)>len(presyn_set):
        cmap=[i%len(colors2D) for i in range(len(presyn_set))]
        color_index=[int(j*num_colors/(len(condition)-1)) for j in range(len(condition))]
        color_tuple=[(cm,ci) for ci in color_index for cm in cmap]
        plot_set=1
    elif len(presyn_set)>1:
        cmap=[i%len(colors2D) for i in range(len(condition))]
        color_index=[int(j*num_colors/(len(presyn_set)-1)) for j in range(len(presyn_set))]
        color_tuple=[(cm,ci) for cm in cmap for ci in color_index]
        plot_set=1
        #pu.plot_fft_cond(freqs,fft_mean,fft_wave)
    else:
        plot_set=0
    if plot_set:
        fig,axes=plt.subplots(2,1,sharex=True)
        fig.suptitle('Mean fft')
        for i,(cond,fft_set) in enumerate(mean_fft_phase.items()):
            maxval=np.max([np.max(np.abs(f['mag'][1:])) for f in mean_fft_phase[cond].values()])
            maxfreq=np.min(np.where(freqs[cond]>500))
            for j,(key,fft) in enumerate(fft_set.items()):
                ti=i*len(presyn_set)+j
                mycolor=colors2D[color_tuple[ti][0]].__call__(color_tuple[ti][1]+offset[color_tuple[ti][0]])
                #axes.plot(freqs[cond][0:maxfreq], np.abs(fft['mag'])[0:maxfreq], '--', label=cond+' '+key+' mean',color=colors[i])
                mean_of_fft=np.mean([np.abs(fft) for fft in fft_wave[cond][key]],axis=0)
                axes[0].plot(freqs[cond][0:maxfreq], mean_of_fft[0:maxfreq],label='mean of '+cond+' '+key,color=mycolor)
                mean_of_fft_env=np.mean([np.abs(fft) for fft in fft_env[cond][key]],axis=0)
                axes[1].plot(freqs[cond][0:maxfreq], mean_of_fft_env[0:maxfreq],label='mean of '+cond+' '+key,color=mycolor)
        axes[1].set_xlabel('Frequency in Hertz [Hz]')
        axes[0].set_ylabel('FFT Magnitude')
        axes[1].set_ylabel('FFT of envelope')
        axes[0].set_xlim(0 , freqs[cond][maxfreq] )
        axes[0].set_ylim(0,np.round(maxval) )
        axes[1].set_ylim(0,np.round(maxval) )
        axes[1].legend()

