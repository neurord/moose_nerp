import numpy as np
import glob
import importlib
from matplotlib import pyplot as plt
plt.ion()

def plot_opt_waves(wavemodule=None,dataname=None,waveset=None):
    optdir='tmp*/*.npy'
    prior_sim_files=glob.glob(optdir)
    for file in prior_sim_files:
        dat=np.load(file,'r')
        simtime=1.25
        ts=np.linspace(0,simtime,len(dat))
        plt.plot(ts,dat)

    if wavemodule and dataname:
        wavedir=importlib.import_module(wavemodule)
        exp_to_fit = wavedir.alldata[dataname]
        if not waveset:
            waveset=range(len(exp_to_fit))
        for wave in exp_to_fit[waveset].waves:
            plt.plot(wave.wave.x,wave.wave.y)
