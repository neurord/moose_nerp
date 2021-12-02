"""
Avrama Blackwell
2021 November 14
Subset of analyses and slight modification from net_anal
   no regular stimulation
   don't calculate sta
   don't plot input rasters
   calculate PSD from multiple neuron types
   
"""
import numpy as np
import glob
import utils as u
import net_anal_utils as nau #must be imported prior to na and isc - which import stuff from it
import plot_utils as pu

filedir='/home/avrama/moose/moose_nerp/moose_nerp/networks/'
param1=['matrix1s','striosome1s','strios2.5_1.5']
labels={'matrix1s': 'matrix','striosome1s':'striosome','strios2.5_1.5':'striosome\nstrong dSPN->iSPN'}
suffix="_out"
dt=0.1e-3
simtime=1.0
numtraces=0 #set to zero to avoid plotting traces
plot_fft_isi=True #set to false to avoid plotting fft and isi histogram

numbins=100 #number of bins (for histograms) if no overlap of bins
min_max=[0.0,0.6]#1.2]#sec
smooth_window=2e-3 #for instantaneous firing rate
maxfreq=100 #only save PSD from FFT from frequencies up to this number
init_time=0.200 #msec
shuffle_correct=False #set to false to calculate uncorrected FFT
num_shuffles=5

alldata={m:{} for m in ['spike_time','spike_rate','spike_rate_t','isis','histbins','fft','freqs']}
mean_spikes={m:{} for m in param1};ste_spikes={m:{} for m in param1}
norm_mean={}
def plot_traces(vmdat,dt,numtraces,ftitle=''):
    from matplotlib import pyplot as plt
    fig,ax=plt.subplots(len(vmdat),1,sharex=True)
    fig.suptitle(ftitle)
    for ii,ntype in enumerate(vmdat.keys()):
        time=np.linspace(0,dt*len(vmdat[ntype][0]),len(vmdat[ntype][0]),endpoint=False)
        for tracenum in range(numtraces):
            ax[ii].plot(time,vmdat[ntype][tracenum])
        ax[ii].set_ylabel(ntype+' Vm (mV)')
    ax[ii].set_xlabel('Time (sec)')

def bar_plots(spike_rate_mean,spike_rate_std,labels):
    from matplotlib import pyplot as plt
    plt.figure()
    x=np.arange(2)
    for ii,cond in enumerate(spike_rate_mean.keys()):
        plt.bar(x+ii/4.0,spike_rate_mean[cond].values(),yerr=spike_rate_std[cond].values(),
                ecolor='black',width=0.25,label=labels[cond])
    plt.xlabel('Neuron Type')
    plt.legend(fontsize=10, loc='upper left')

for cond in param1:
    accum_key=cond
    pattern=filedir+cond+suffix
    files=sorted(glob.glob(pattern+'*.npz'))
    if len(files)==0:
        print('************ no files found using',pattern)
    elif len(files)>1:
        print(' ####### Too many files, refine pattern')
    else:
        for f in files:
            print('************  analyzing', f)
            dat=np.load(f,'r',allow_pickle=True)
            vmdat=dat['vm'].item()
        spike_time=u.spiketime_from_vm(vmdat,dt)
        maxtime=np.max([np.max(u.flatten(st)) for st in spike_time.values()]) #time of last spike
        simtime = round(max(simtime, maxtime),1) #update simtime if needed
        spike_rate,spike_rate_mean,spike_rate_tvals=u.spikerate_func(spike_time,simtime,smooth_window)
        isi,isi_stats,isi_hist,histbins = u.isi(spike_time,numbins,min_max)
        mean_fft,std_fft,freqs=u.fft_func(spike_rate,smooth_window,init_time,maxfreq)
        shuffled_spikes=u.shuffle(spike_time,num_shuffles)
        shuffle_rate,_,_=u.spikerate_func(shuffled_spikes,simtime,smooth_window)
        shuffled_fft,shuffled_std,shuffle_freqs=u.fft_func(shuffle_rate,smooth_window,init_time,maxfreq)
        correct_fft={ntype: mean_fft[ntype]-shuffled_fft[ntype] for ntype in  mean_fft.keys()}
        alldata['spike_time'][cond]=spike_time
        alldata['spike_rate'][cond]=spike_rate_mean
        alldata['spike_rate_t'][cond]=spike_rate_tvals
        alldata['isis'][cond]=isi_hist
        alldata['histbins'][cond]=histbins
        if shuffle_correct:
            alldata['fft'][cond]= correct_fft
        else:
            alldata['fft'][cond]= mean_fft
        alldata['freqs'][cond]=freqs
        for ntype in spike_time.keys():
            time=np.linspace(0,smooth_window*len(spike_rate_mean[ntype]),len(spike_rate_mean[ntype]),endpoint=False)
            start_index=np.min(np.where(time>init_time))
            mean_spikes[cond][ntype]=np.mean(spike_rate_mean[ntype][start_index:])
            ste_spikes[cond][ntype]=np.std(spike_rate_mean[ntype][start_index:])/np.sqrt(len(spike_rate[ntype]))
        norm_mean[cond]=np.mean(mean_spikes[cond]['D1']/mean_spikes[cond]['D2'])

        ###################################################
        ######## Single parameter set plots
        ###################################################
        pu.plot_raster(spike_time,simtime,ftitle=cond)
        print('******** ISI stats for', cond,isi_stats)
        if numtraces>0:
            plot_traces(vmdat,dt,numtraces,ftitle=cond)
###################################################
# plots comparing data across cond
###################################################
from matplotlib import pyplot as plt
plt.figure()
plt.bar(labels.values(),norm_mean.values(), ecolor='black')

pu.plot_dict_of_dicts(alldata['spike_rate'],alldata['spike_rate_t'],ylabel='rate (Hz)')
bar_plots(mean_spikes,ste_spikes,labels)
if plot_fft_isi:
    pu.plot_dict_of_dicts(alldata['fft'],alldata['freqs'],ylabel='PSD',xlabel='Freq (Hz)')
    hist_xvals= {p:[(bins[i]+bins[i+1])/2 for i in range(len(bins)-1)] for p,bins in alldata['histbins'].items()}
    pu.plot_dict_of_dicts(alldata['isis'],hist_xvals,xlabel='ISI (sec)', ylabel='number')

for cond in param1:
    confile_name=filedir+cond+'*_connect.npz'
    nau.print_con(confile_name)


'''         
np.save(outfname,alldata)
if savetxt:
    nau.write_dict_of_dicts(spikerate_mean,rate_xvals,'spike_rate_'+out_fname,'rate',spikerate_std) 
    nau.write_dict_of_dicts(spikerate_elphmean,elph_xvals,'elph_spike_rate_'+out_fname,'Erate',spikerate_elphstd)
    nau.write_triple_dict(isihist_mean,'isi_histogram_'+out_fname,'isiN',isihist_std,xdata=hist_xvals,xheader='isi_bin') #possibly delete triple dict and loop over neur type?
    nau.write_dict_of_dicts(mean_fft,alldata.freqs,'fft_'+out_fname,'fft',std_fft,xheader='freq') #this may need triple dict if do fft for multiple neur types
'''
