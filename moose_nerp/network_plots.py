import numpy as np
import elephant
import network_analysis as na
import ep_plot_utils as pu
import os
import glob

from matplotlib import pyplot as plt
plt.ion()
colors=plt.get_cmap('viridis')

print_con=False
binsize=0.02 #sec; subdivide time into bins to calculate spike frequency
overlap=0.2 #sliding window moves this fraction of binsize, show be 1/integer
max_rasters=500
save_txt=True

#root='EPampa1.5_ramp*pulsedur0.05*ep88*' #'Ctx_*pulsedur0.1_freq73*'
root='Ctx_osc*' 
files=sorted(glob.glob('bg_net/output/bg_'+root+'.npz')) #list of files with output spikes
#files=['bg_net/output/bg_Ctx10000_ramp_freq5.0_30dur0.5_STN2000_lognorm_freq28.0_feedbackNpas-2_Lhx6-4.npz']
inputs=['bg_net/STN500_pulse_freq1.0_73dur0.05',
        'bg_net/Ctx10000_ramp_freq5.0_50dur0.3',
        'bg_net/Ctx10000_ramp_freq5.0_30dur0.5'] #input spikes
inputs=[]

#since filenames are long, find the pieces that are different to use as labels and titles
def find_fig_title(filenames):
    files=[f.split('.npz')[0] for f in filenames]
    if len(files)>1:
        diffs=[]
        for i in range(len(files)):
            a=set(files[i%len(files)].split('_'))
            b=set(files[(i+1)%len(files)].split('_'))
            diffs.append(list(b.difference(a)))
        keywords=np.unique(na.flatten(diffs))
        print(keywords)
        titlelist=[];locations=[]
        for i,f in enumerate(files):
            titlelist.append('-'.join([key for key in keywords if key in f]))
            locations.append(sorted([(f.find(key),len(key)) for key in keywords if key in f]))
    else:
        titlelist=files
        locations=[]
    return titlelist,locations

def simple_raster(spikes,max_time,max_rasters=np.inf,ftitle=''):
    fig,axes =plt.subplots(len(spikes), 1,sharex=True)
    fig.suptitle('raster \n'+ftitle)
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
titlelist,loc=find_fig_title(files)
if len(loc):
    i=0
    common_name=''
    for j in range(len(loc[i]))[1:-1]:
        common_name+=files[i][loc[i][j][0]+loc[i][j][1]:loc[i][j+1][0]]
else:
    common_name=files[0].split('/')[-1]
for ff,fname in enumerate(files):
    dat= np.load(fname,'r',allow_pickle=True)
    spiketime_dict=dat['spike_time'].item()
    max_time=dat['params'].item()['simtime']
    simple_raster(spiketime_dict,max_time,ftitle=titlelist[ff]) #plot rasters of inputs
    numbins=int(max_time/binsize/overlap-(1./overlap-1))
    binlow=[i*binsize*overlap for i in range(numbins)]
    binhigh=[bl+binsize for bl in binlow]
    spike_rate={k:np.zeros(numbins) for k in spiketime_dict.keys()}
    for ntype in spiketime_dict.keys():
        numneurs=len(spiketime_dict[ntype])
        #time_hist,tmp=np.histogram(na.flatten(spiketime_dict[ntype]),bins=bins) #NOT WORKING
        #spike_rate[ntype]=time_hist/numneurs
        for bb,(bl,bh) in enumerate(zip(binlow,binhigh)):
            spike_rate[ntype][bb]=len([st for st in  na.flatten(spiketime_dict[ntype]) if st>bl and st<bh])/binsize/numneurs
    all_spike_rate[titlelist[ff]]=spike_rate

#plot spike rate for each neuron type and each input file
plot_bins=[(binlow[i]+binhigh[i])/2 for i in range(numbins)]
fig,axes =plt.subplots(len(spiketime_dict.keys()), 1,sharex=True)
fig.suptitle('firing rate')
axis=fig.axes
for cond,spike_rate in all_spike_rate.items():
    fig.suptitle('firing rate '+common_name)
    for i,ntype in enumerate(spike_rate.keys()):
        axis[i].plot(plot_bins,spike_rate[ntype],label=cond)
        axis[i].set_ylabel(ntype+ ' Hz')
axis[-1].set_xlabel('time (sec)')
axis[-1].set_xlim(0.0,max_time)
axis[-1].legend()

#plot raster of input spikes-update to work with different sets of inputs, e.g. slow and fast ramp
pre_spikes={}
for f in inputs:
    pre_spikes[os.path.basename(f)]=np.load(f+'.npz','r',allow_pickle=True)['spikeTime']
if len(inputs):
    simple_raster(pre_spikes,max_time,max_rasters=max_rasters)

if save_txt:
    for cond in all_spike_rate.keys():
        outfname=cond+'hist.txt'
        header='time   '+'   '.join(all_spike_rate[cond].keys())
        matrix=np.concatenate([np.array(vals)[:,None] for vals in all_spike_rate[cond].values()],axis=1)
        np.savetxt(outfname,np.column_stack((plot_bins,matrix)),header=header)

if print_con:
    confiles=glob.glob('bg_connect'+root+'*.npz')
    for f in confiles:
        data=np.load(f,'r',allow_pickle=True)
        print ('########### ', f,' ##############')
        for ntype,conns in data['summary'].item().items():
            for syn in conns['intra']:
                for presyn in conns['intra'][syn].keys():
                    print(ntype,syn,'presyn=',presyn,'mean inputs=',np.round(np.mean(conns['intra'][syn][presyn]),2) )
            print('shortarge',data['summary'].item()[ntype]['shortage'].values())
'''
for fname in files:
    dat=np.load(fname,'r',allow_pickle=True)
    connect=dat['params'].item()['connect_dict']
    print ('########### ', fname,' ##############')
    for row in connect:
        print(row)
'''
