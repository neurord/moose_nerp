import numpy as np
import elephant
import network_analysis as na
import ep_plot_utils as pu
import os
import glob

from matplotlib import pyplot as plt
plt.ion()
colors=plt.get_cmap('viridis')

print_con=True
binsize=0.02 #sec; subdivide time into bins to calculate spike frequency
overlap=0.2 #sliding window moves this fraction of binsize, show be 1/integer
max_rasters=0
trial_end='umt' #or None; would have been better to use -tr or _tr in file naming
save_txt=True

#root='EPampa1.5_ramp*puls edur0.05*ep88*' #'Ctx_*pulsedur0.1_freq73*'
root='ep1.4_Ctx_ramp*dur0.05_freq73-fb_npas*_lhx?*umt*'
#root='bg_Ctx_osc*umt*'
if 'ramp' in root:
    start_plot=1.0
else:
    start_plot=0
files=sorted(glob.glob('bg_net/output/'+root+'.npz')) #list of files with output spikes

#files=['bg_net/output/bg_Ctx10000_ramp_freq5.0_30dur0.5_STN2000_lognorm_freq28.0_feedbackNpas-2_Lhx6-4.npz']
inputs=['bg_net/STN500_pulse_freq1.0_73dur0.05',
        'bg_net/Ctx10000_ramp_freq5.0_50dur0.3',
        'bg_net/Ctx10000_ramp_freq5.0_30dur0.5'] #input spikes
inputs=[]

#since filenames are long, find the pieces that are different to use as labels and titles
def find_fig_title(filenames,trial_ending=None):
    if trial_ending:
        splitword=trial_ending
    else:
        splitword='.npz'
    files=[f.split(splitword)[0] for f in filenames]
    cond=np.unique(files)
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
    return titlelist,locations,cond

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

def plot_hist_dict(hist_dict,plot_bins,num_neur,title,max_time,std_dict={},start=0):
    fig,axes =plt.subplots(num_neur, 1,sharex=True)
    fig.suptitle('firing rate')
    axis=fig.axes
    for cond,spike_rate in hist_dict.items():
        fig.suptitle('firing rate '+title)
        for i,ntype in enumerate(spike_rate.keys()):
            axis[i].plot(plot_bins,spike_rate[ntype],label=cond)
            if len(std_dict):
                axis[i].plot(plot_bins,std_dict[cond][ntype]+spike_rate[ntype],linestyle='dashed')
            axis[i].set_ylabel(ntype)
    axis[-1].set_xlabel('time (sec)')
    axis[-1].set_xlim(start,max_time)
    axis[-1].legend()

def save_output(spike_rate,plot_bins,spike_std={}):
    for cond in spike_rate.keys():
        outfname=cond+'hist.txt'
        header='time   '+'   '.join(spike_rate[cond].keys())
        matrix=np.concatenate([np.array(vals)[:,None] for vals in spike_rate[cond].values()],axis=1)
        if len(spike_std):
            std_matrix=np.concatenate([np.array(vals)[:,None] for vals in spike_std[cond].values()],axis=1)
            matrix=np.column_stack((matrix,std_matrix))
            header=header+' std_'.join(spike_std[cond].keys())
        np.savetxt(outfname,np.column_stack((plot_bins,matrix)),header=header)

all_spike_rate={}
titlelist,loc,conditions=find_fig_title(files,trial_ending=trial_end)
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
    if max_rasters:
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
    if len(titlelist)>len(conditions): #numerous trials per condition
        #convert the items in dictionary into list of arrays
        if titlelist[ff] in all_spike_rate.keys():
            for ntype in all_spike_rate[titlelist[ff]]:
                all_spike_rate[titlelist[ff]][ntype].append(spike_rate[ntype])
        else:
            spike_hist={ntype:[hist] for ntype,hist in spike_rate.items()}
        all_spike_rate[titlelist[ff]]=spike_hist
    else:
        all_spike_rate[titlelist[ff]]=spike_rate

#### calculate mean and std over the set of trials
if len(files)>len(conditions):
    spike_rate_mean={c:{} for c in all_spike_rate.keys()}
    spike_rate_std={c:{} for c in all_spike_rate.keys()}
    for cond in all_spike_rate.keys():
        for ntype in all_spike_rate[cond].keys():
            spike_rate_mean[cond][ntype]=np.mean(all_spike_rate[cond][ntype],axis=0)
            spike_rate_std[cond][ntype]=np.std(all_spike_rate[cond][ntype],axis=0)

#plot spike rate for each neuron type and each input file
numneurs=len(spiketime_dict.keys())
plot_bins=[(binlow[i]+binhigh[i])/2 for i in range(numbins)]
if len(files)>len(conditions):
    #plot_hist_dict(spike_rate_mean,plot_bins,numneurs,common_name,max_time,spike_rate_std)
    plot_hist_dict(spike_rate_mean,plot_bins,numneurs,common_name,max_time,start=start_plot)
else:
    plot_hist_dict(all_spike_rate,plot_bins,numneurs,common_name,max_time,start=start_plot)

#plot raster of input spikes-update to work with different sets of inputs, e.g. slow and fast ramp
pre_spikes={}
for f in inputs:
    pre_spikes[os.path.basename(f)]=np.load(f+'.npz','r',allow_pickle=True)['spikeTime']
if len(inputs) and max_rasters:
    simple_raster(pre_spikes,max_time,max_rasters=max_rasters)

##### fix this to save mean and std as appropriate
if save_txt:
    if len(files)>len(conditions):
        save_output(spike_rate_mean,plot_bins,spike_rate_std)
    else:
        save_output(all_spike_rate,plot_bins)

if print_con:
    confiles=glob.glob('bg_connect'+root.split(trial_end)[0]+'*.npz')
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
for fname in files:
    dat=np.load(fname,'r',allow_pickle=True)
    connect=dat['params'].item()['connect_dict']
    print ('########### ', fname,' ##############')
    for row in connect:
        print(row)
'''
