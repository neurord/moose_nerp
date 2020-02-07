import numpy as np
import elephant
import network_analysis as na
import ep_plot_utils as pu
import os

from matplotlib import pyplot as plt
plt.ion()
colors=plt.get_cmap('viridis')

numbins=100 #subdivide time into bins to calculate spike frequency
fname='bg_net/output/bg_osc' #output spikes
inputs=['bg_net/Ctx10000_osc_freq10.0_osc0.7','bg_net/STN2000_lognorm_freq18.0'] #input spikes
max_rasters=1000

dat= np.load(fname+'.npz','r',allow_pickle=True)
spiketime_dict=dat['spike_time'].item()
max_time=dat['params'].item()['simtime']
binsize=max_time/numbins
bins=[i*binsize for i in range(numbins)]

spike_rate={k:np.zeros(numbins) for k in spiketime_dict.keys()}
fft_wave={}

for ntype in spiketime_dict.keys():
    flat_spikes=na.flatten(spiketime_dict[ntype])
    numneurs=len(spiketime_dict[ntype])
    for i,sbin in enumerate(bins):
        spike_rate[ntype][i]=np.sum([st for st in flat_spikes if st>sbin and st<sbin+binsize])/numneurs/binsize
    plt.plot(bins,spike_rate[ntype],label=ntype)
plt.legend()

pre_spikes={}
for f in inputs:
    pre_spikes[os.path.basename(f)]=np.load(f+'.npz','r',allow_pickle=True)['spikeTime']

fig,axes =plt.subplots(len(inputs), 1,sharex=True)
fig.suptitle('input raster ')
axis=fig.axes
for ax,(key,spikeset) in enumerate(pre_spikes.items()):
    numtrains=max_rasters if len(spikeset)>max_rasters else len(spikeset)
    color_num=[pu.colornum(cellnum,spikeset) for cellnum in range(numtrains)]
    color_set=np.array([colors.__call__(color) for color in color_num])
    axis[ax].eventplot(spikeset[0:numtrains],color=color_set)
    axis[ax].set_ylabel(key)
axis[-1].set_xlim([0,max_time])
axis[-1].set_xlabel('time (s)')


connect=dat['params'].item()['connect_dict']
#for line in connect:
#    print(line['neur'],line['syn'],line['pre'],line['params'])
