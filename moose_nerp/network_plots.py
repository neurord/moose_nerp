import numpy as np
import elephant
import network_analysis as na
import ep_plot_utils as pu
import os

from matplotlib import pyplot as plt
plt.ion()
colors=plt.get_cmap('viridis')

numbins=100 #subdivide time into bins to calculate spike frequency
files=['bg_net/output/bg_osc'] #list of files with output spikes
inputs=['bg_net/Ctx10000_osc_freq10.0_osc0.7','bg_net/STN2000_lognorm_freq18.0'] #input spikes
max_rasters=1000
save_txt=False

def simple_raster(spikes,max_time,max_rasters=np.inf):
    fig,axes =plt.subplots(len(spikes), 1,sharex=True)
    fig.suptitle('input raster ')
    axis=fig.axes
    for ax,(key,spikeset) in enumerate(spikes.items()):
        numtrains=max_rasters if len(spikeset)>max_rasters else len(spikeset)
        color_num=[pu.colornum(cellnum,spikeset) for cellnum in range(numtrains)]
        color_set=np.array([colors.__call__(color) for color in color_num])
        axis[ax].eventplot(spikeset[0:numtrains],color=color_set)
        axis[ax].set_ylabel(key)
    axis[-1].set_xlim([0,max_time])
    axis[-1].set_xlabel('time (s)')

all_spike_rate={}
for fname in files:
    dat= np.load(fname+'.npz','r',allow_pickle=True)
    spiketime_dict=dat['spike_time'].item()
    max_time=dat['params'].item()['simtime']
    simple_raster(spiketime_dict,max_time) #plot rasters of inputs
    binsize=max_time/numbins
    bins=[i*binsize for i in range(numbins)]
    spike_rate={k:np.zeros(numbins) for k in spiketime_dict.keys()}
    for ntype in spiketime_dict.keys():
        numneurs=len(spiketime_dict[ntype])
        time_hist,tmp=np.histogram(na.flatten(spiketime_dict[ntype]),bins=bins)
        spike_rate[ntype]=time_hist/numneurs
    all_spike_rate[os.path.basename(fname)]=spike_rate

#plot spike rate for each neuron type and each input file
plot_bins=[(bins[i]+bins[i+1])/2 for i in range(len(bins)-1)]
fig,axes =plt.subplots(len(files), 1,sharex=True)
fig.suptitle(+' rate')
axis=fig.axes
for i,(cond,spike_rate) in enumerate(all_spike_rate.items()):
    axis[i].plot(plot_bins,spike_rate[ntype],label=ntype)
    axis[ax].set_ylabel(cond, 'Hz')
axis[-1].set_xlabel('time (sec)')
axis[-1].set_xlim(0.0,max_time)
plt.legend()

#plot raster of input spikes-update to work with different sets of inputs, e.g. slow and fast ramp
pre_spikes={}
for f in inputs:
    pre_spikes[os.path.basename(f)]=np.load(f+'.npz','r',allow_pickle=True)['spikeTime']
simple_raster(pre_spikes)

if save_txt:
    for cond in all_spike_rate.keys():
        outfname=cond+'hist.txt'
        header='time   '+'   '.join(all_spike_rate[cond].keys())
        matrix=np.concatenate([np.array(vals)[:,None] for vals in all_spike_rate[cond].values()],axis=1)
        np.savetxt(outfname,np.column_stack((plot_bins,matrix)),header=header)

connect=dat['params'].item()['connect_dict']
#for line in connect:
#    print(line['neur'],line['syn'],line['pre'],line['params'])
