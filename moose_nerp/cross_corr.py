import numpy as np
import elephant
from neo.core import AnalogSignal,SpikeTrain
import quantities as q
from elephant.conversion import BinnedSpikeTrain
from matplotlib import pyplot as plt

def plot_cross_corr(pre_spikes,spiketime_dict,presyn,binsize,maxtime=0):
    mean_cc={};mean_cc_shuffle={};cc_shuffle_corrected={}
    for key in pre_spikes.keys(): #key indexes the simulation condition, e.g. stpYN
        numtrials=len(pre_spikes[key])
        if maxtime==0:
            last_spike=[train[-1] for train in pre_spikes[key][0][presyn]]
            t_end=max(np.round(np.max(last_spike),maxtime))
            maxtime=t_end
        else:
            t_end=maxtime
        cc_hist=[[] for t in range(numtrials)]
        fig,axes =plt.subplots(numtrials,numtrials,sharex=True)
        fig.suptitle('cross correlograms '+key)
        for trial_in in range(numtrials):
            for trial_out in range(numtrials):
                if isinstance(pre_spikes[key][trial_in][presyn], list):
                    spikes = np.sort(np.concatenate(pre_spikes[key][trial_in][presyn]))
                else:
                    spikes=pre_spikes[key][trial_in][presyn]
                train=SpikeTrain(spikes*q.s,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
                in_train=BinnedSpikeTrain(train,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
                train=SpikeTrain(spiketime_dict[key][trial_out]*q.s,t_stop=t_end*q.s)
                out_train=BinnedSpikeTrain(train,t_start=0*q.s,t_stop=t_end*q.s,binsize=binsize*q.s)
                #print('trial_in,trial_out', trial_in, trial_out)
                cc_hist[trial_in].append(elephant.spike_train_correlation.cross_correlation_histogram(in_train,out_train))
                axes[trial_in,trial_out].plot(cc_hist[trial_in][trial_out][0].magnitude[:,0])
            axes[trial_in,0].set_ylabel('input '+str(trial_in))
        for trial_out in range(trial_in,numtrials):
            axes[-1,trial_out].set_xlabel('output '+str(trial_out))
        #shuffle corrected mean cross-correlogram
        #initialize these to accumulate across conditions, e.g. pre and post-HFS, and possibly across keys (str freq)
        cc_same=[cc_hist[a][a][0].magnitude[:,0] for a in range(numtrials)]
        mean_cc[key]=np.mean(cc_same,axis=0)
        cc_diff=[cc_hist[a][b][0].magnitude[:,0] for a in range(numtrials) for b in range(numtrials) if b != a ]
        mean_cc_shuffle[key]=np.mean(cc_diff,axis=0)
        cc_shuffle_corrected[key]=mean_cc[key]-mean_cc_shuffle[key]
    #PLOT mean cc and shuffle corrected for each key on one figure
    xbins=np.linspace(-t_end,t_end,len(mean_cc[key]))
    fig,axes =plt.subplots(3,1,sharex=True)
    fig.suptitle('cross correlograms '+presyn)
    for key in mean_cc.keys():
        axes[0].plot(xbins,mean_cc[key],label=key)
        axes[1].plot(xbins,mean_cc_shuffle[key],label=key)
        axes[2].plot(xbins,cc_shuffle_corrected[key],label=key)
    axes[0].set_ylabel('mean cc')
    axes[1].set_ylabel('mean cc shuffled')
    axes[2].set_ylabel('mean cc shuffled-corrected')
    axes[2].legend()
    return
