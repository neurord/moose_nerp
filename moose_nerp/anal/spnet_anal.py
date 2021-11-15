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
param1=['mat','patch']
suffix="_out"
dt=0.1e-3
simtime=1.5

numbins=100 #number of bins (for histograms) if no overlap of bins
min_max=[0.0,0.6]#1.2]#sec
smooth_window=2e-3 #for instantaneous firing rate
maxfreq=100 #only save PSD from FFT from frequencies up to this number
init_time=0.200 #msec
shuffle_correct=True
num_shuffles=5

alldata={m:{} for m in ['spike_time','spike_rate','spike_rate_t','isis','histbins','fft','freqs']}

for cond in param1:
    accum_key=cond
    pattern=filedir+cond+suffix
    files=sorted(glob.glob(pattern+'*.npz'))
    if len(files)==0:
        print('************ no files found using',pattern)
    elif len(files)>1:
        print(' ####### Too many files, refine pattern')
    for f in files:
        dat=np.load(f,'r',allow_pickle=True)
        vmdat=dat['vm'].item()
    spike_time=u.spiketime_from_vm(vmdat,dt)
    maxtime=np.max([np.max(u.flatten(st)) for st in spike_time.values()]) #time of last spike
    simtime = round(max(simtime, maxtime),1) #update simtime if needed
    time=np.linspace(0,simtime,int(simtime/dt)+1,endpoint=True)
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

    ###################################################
    ######## Single parameter set plots
    ###################################################
    pu.plot_raster(spike_time,simtime,ftitle=cond)
    print('ISI stats for', cond,isi_stats)

###################################################
# plots comparing data across cond
###################################################
pu.plot_dict_of_dicts(alldata['fft'],alldata['freqs'],ylabel='PSD',xlabel='Freq (Hz)')
pu.plot_dict_of_dicts(alldata['spike_rate'],alldata['spike_rate_t'],ylabel='spike rate (Hz)')
hist_xvals= {p:[(bins[i]+bins[i+1])/2 for i in range(len(bins)-1)] for p,bins in alldata['histbins'].items()}
pu.plot_dict_of_dicts(alldata['isis'],hist_xvals,xlabel='ISI (sec)', ylabel='number')

for cond in param1:
    confile_name=filedir+cond+'_connect.npz'
    nau.print_con(confile_name)

'''         
if savetxt:
    nau.write_dict_of_dicts(spikerate_mean,rate_xvals,'spike_rate_'+out_fname,'rate',spikerate_std) 
    nau.write_dict_of_dicts(spikerate_elphmean,elph_xvals,'elph_spike_rate_'+out_fname,'Erate',spikerate_elphstd)
    nau.write_triple_dict(isihist_mean,'isi_histogram_'+out_fname,'isiN',isihist_std,xdata=hist_xvals,xheader='isi_bin') #possibly delete triple dict and loop over neur type?
    nau.write_dict_of_dicts(mean_fft,alldata.freqs,'fft_'+out_fname,'fft',std_fft,xheader='freq') #this may need triple dict if do fft for multiple neur types
'''
