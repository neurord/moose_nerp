import numpy as np
from matplotlib import pyplot as plt
plt.ion()
import ISI_anal
colors=['r','k','b']

def latency_plot(fileprefix,filesuffix,stim_freq,neurtype,presyn_set,numbins):
    #plot the ISI and latency from network neuron simulations, one frequency, multiple trials
    fig1,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis1=fig1.axes
    for i,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+suffix
        lat_mean,lat_std,isi_mean,isi_std,bins=ISI_anal.latency(pattern,stim_freq,neurtype,numbins)
        for k,key in enumerate(lat_mean.keys()):
            axis1[i].plot(range(len(lat_mean[key])),lat_mean[key],label=key+' mean',color=colors[k])
            axis1[i].plot(range(len(lat_std[key])),lat_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis1[i].set_xlabel('stim number')
        axis1[i].set_ylabel(presyn+'input, latency (sec)')
        fig1.suptitle('Latency: '+filesuffix.split('.')[0])
        axis1[i].legend()

def ISI_plot(fileprefix,filesuffix,stim_freq,neurtype,presyn_set,numbins):
    fig2,axes =plt.subplots(len(presyn_set),1,sharex=True)
    axis2=fig2.axes
    for i,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+suffix
        lat_mean,lat_std,isi_mean,isi_std,bins=ISI_anal.latency(pattern,stim_freq,neurtype,numbins)
        for k,key in enumerate(bins.keys()):
            axis2[i].plot(bins[key],isi_mean[key],label=key+' mean',color=colors[k])
            axis2[i].plot(bins[key],isi_std[key],label=key+' std',linestyle='dashed',color=colors[k])
        axis2[i].set_xlabel('time (sec)')
        axis2[i].set_ylabel(presyn+'input, isi (sec)')
        fig2.suptitle('ISI: '+filesuffix.split('.')[0])
        axis2[i].legend()

def raster_plot(fileroot,suffix,presyn_set,stim_freq):
    ####### Raster plot from results #############
    fig,axes =plt.subplots(len(presyn_set), 1,sharex=True)
    fig.suptitle('output '+suffix)
    axis=fig.axes
    for ax,presyn in enumerate(presyn_set):
        pattern=fileroot+presyn+suffix
        files=ISI_anal.file_set(pattern)
        spiketimes=[]
        if len(files)>0:
            for fname in files:
                dat=np.load(fname,'r')
                spiketimes.append(dat['spike_time'].item()[neurtype][0])
            axis[ax].eventplot(spiketimes)
            xstart=dat['params'].item()['ep']['syn_tt'][0][1][0]
            xend=dat['params'].item()['ep']['syn_tt'][0][1][-1]
            maxt=max([max(st) for st in spiketimes])
            axis[ax].annotate('stim onset',xy=(xstart,0),xytext=(xstart/maxt, -0.2), textcoords='axes fraction', arrowprops=dict(facecolor='black', shrink=0.05))
            axis[ax].annotate('offset',xy=(xend,0),xytext=(xend/maxt, -0.2), textcoords='axes fraction', arrowprops=dict(facecolor='red', shrink=0.05))
        axis[ax].set_ylabel(presyn+' trial')
    axis[-1].set_xlabel('time (sec)')

#plot the set of results from single neuron simulations, all frequencies
#either normalized PSPs if no spikes, or ISIs if spikes
def freq_dep_plot(fileroot,presyn_set,suffix,neurtype):
    all_results=[];all_xvals=[]
    for i,presyn in enumerate(presyn_set):
        numplots,results,xval_set,xlabel,ylabel=ISI_anal.freq_dependence(fileroot,presyn,suffix)    
        all_results.append(results)
        all_xvals.append(xval_set)
    fig,axes =plt.subplots(numplots, len(presyn_set),sharex=True, sharey=True)
    fig.suptitle(neurtype+suffix)
    axis=fig.axes
    for i,presyn in enumerate(presyn_set):
        for freq in sorted(all_results[i].keys()):
            for j,ntype in enumerate(all_results[i][freq].keys()):
                axisnum=i*len(all_results[i][freq].keys())+j
                for yval in all_results[i][freq][ntype]:
                    axis[axisnum].scatter(all_xvals[i][freq][ntype][0:len(yval)],yval,label=str(freq),marker='o')
                axis[axisnum].set_ylabel(str(ntype)+' '+ylabel)
            axis[axisnum].legend()
        axis[axisnum].set_xlabel(xlabel)

def freq_dep_vm(fileroot,presyn_set,plasYN,inj,neurtype):
####### Membrane potential  #############
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

def flatten(isiarray):
    return [item for sublist in isiarray for item in sublist]

####################################
# Parameters of set of files to analyze
neurtype='ep'
plasYN=1
inj='0.0'
#inj='-1.5e-11'
stim_freq=40
presyn_set=['GPe']#,'str']
presyn='GPe'
numbins=10
############################################################
#specify file name pattern
fileroot='epGABA_syn'
suffix='_freq'+str(stim_freq)+'_plas'+str(plasYN)+'_inj'+inj+'*.npz'

#plots for network simulations:
latency_plot(fileroot,suffix,stim_freq,neurtype,presyn_set,numbins)
#latency not too meaningfull if spikes occur only every few IPSPs, e.g. with 40 Hz stimulation
ISI_plot(fileroot,suffix,stim_freq,neurtype,presyn_set,numbins)
raster_plot(fileroot,suffix,presyn_set,stim_freq)

#plots for single neuron simulations:
#freq_dep_plot(fileroot,presyn_set,suffix,neurtype)
#freq_dep_vm(fileroot,presyn_set,plasYN,inj,neurtype)

############### Next analysis: ISI histogram
#def ISI_histogram(fileroot,presyn,suffix,stim_freq):
pattern=fileroot+presyn+suffix
files=ISI_anal.file_set(pattern)
if len(files)==0:
    print('no files found')

#set-up pre, during and post-stimulation time frames (bins)
with np.load(files[0],'r') as dat:
    params=dat['params'].item()
    stim_tt=params[neurtype]['syn_tt'][0][1]
binsize=stim_tt[-1]+1/float(stim_freq)-stim_tt[0]
bins={'stim':stim_tt[0],'pre':stim_tt[0]-binsize,'post':stim_tt[-1]+1/float(stim_freq)}
isi_set={'pre':[],'post':[],'stim':[]}

#read in ISI data and separate into 3 time frames
for fname in files:
    dat=np.load(fname,'r')
    if 'spike_time' in dat.keys() and params['freq']==stim_freq:
        spike_time=dat['spike_time'].item()[neurtype][0]
        isi_vals=dat['isi'].item()[neurtype][0]
        #separate into pre, post and during stimulation (optional)
        st_isi=dict(zip(spike_time[1:],isi_vals))
        for pre_post,binmin in bins.items():
            binmax=binmin+binsize
            isi_set[pre_post].append([isi_val for st, isi_val in st_isi.items() if st>=binmin and st<binmax])

#Calculate and plot histograms

mins=[np.min(flatten(isi_set[k])) for k in isi_set.keys()]
maxs=[np.max(flatten(isi_set[k])) for k in isi_set.keys()]
min_max=[np.min(mins),np.max(maxs)]
histbins=10 ** np.linspace(np.log10(min_max[0]), np.log10(min_max[1]), numbins)
histbins=np.linspace(min_max[0],min_max[1], numbins)
plt.figure()
plt.title('histogram '+suffix.split('.')[0])
hist_ep={};CV={}
symbol={'stim':'o-','pre':'.--','post':'.--'}
for pre_post,ISIs in isi_set.items():
    hist_ep[pre_post],tmp=np.histogram(flatten(ISIs),bins=histbins,range=min_max)
    CV[pre_post]=np.std(flatten(ISIs))/np.mean(flatten(ISIs))
    print(pre_post,': ISI mean, std=', np.mean(flatten(ISIs)),np.std(flatten(ISIs)),' CV=',CV[pre_post])
    plot_bins=[(histbins[i]+histbins[i+1])/2 for i in range(len(histbins)-1)]
    #plt.bar(plot_bins,hist_ep[pre_post], label=pre_post)#,color=colors.__call__(color_num[i]),width=binwidth)
    plt.plot(plot_bins,hist_ep[pre_post],symbol[pre_post], label=pre_post)
plt.legend()
plt.xlabel('ISI')
plt.ylabel('num events')

#################### Spike triggered averages
#raster plot of input spike times
infile='ttepPSP_str_freq10_plas1_inj0.0.npy'
tt=np.load(infile).item()
fig,axes =plt.subplots(len(tt.keys()), 1,sharex=True)
fig.suptitle('input raster '+infile.split('.')[0])
axis=fig.axes
colors=plt.get_cmap('viridis')
#colors=plt.get_cmap('gist_heat')
for ax,syntype in enumerate(tt.keys()):
    for presyn in tt[syntype].keys():
        spiketimes=[]
        num_in=len(tt[syntype][presyn].keys())
        color_num=[int(cellnum*(colors.N/num_in)) for cellnum in range(num_in)]
        color_set=np.array([colors.__call__(color) for color in color_num])
        for branch in sorted(tt[syntype][presyn].keys()):
            #axis[ax].eventplot(tt[syntype][presyn][branch])
            spiketimes.append(tt[syntype][presyn][branch])
        axis[ax].eventplot(spiketimes,color=color_set)
    axis[ax].set_ylabel(syntype)
axis[-1].set_xlabel('time (s)')

#Next: use both pre-synaptic and post-synaptic spikes and Vm
#for each post-syn spike, look at vm prior to spike (e.g. 20 ms), and average over input spikes:
# give +1 for ampa and -1*weight for gaba?  Or calculate separate traces for ampa and gaba
# for each pre-synaptic spike, look at vm after spike (e.g. 20 ms)
