from __future__ import division
import moose
import matplotlib.pyplot as plt
import numpy as np

isi = 0.01
width_AP = 0.005
n_AP = 3
f_AP = 50.

n_burst = 5
f_burst = 5.

n_train = 3
f_train = 0.3

inject = 1
stim_delay = 0.5

width_burst = n_AP/f_AP
dt_burst = 1/f_burst 
dt_f = 1/f_AP
width_train = n_burst/f_burst
dt_train = 1/f_train
exp_duration = n_train/f_train
stim_delay = .5
AP_delay = stim_delay + isi


base_current = 0
if __name__ == '__main__':
    model = moose.Neutral('/model')
    print dt_f
    dt = 5e-5
    steps = 200000
    simtime = dt * steps
    print simtime
    moose.setClock(0, dt)
    moose.reinit()



    pulse0 = moose.PulseGen('/model/pulse0')
    pulse0.level[0] = inject
    pulse0.width[0] = width_AP
    pulse0.delay[0] = 0
    pulse0.delay[1] = dt_f
    pulse0.baseLevel = base_current
    pulse0.trigMode = 2

    burst_gate = moose.PulseGen('/model/burst_gate')
    burst_gate.level[0] = inject
    burst_gate.delay[0] = 0
    burst_gate.delay[1] = dt_burst
    burst_gate.width[0] = width_burst
    burst_gate.baseLevel = base_current
    burst_gate.trigMode = 2

    moose.connect(burst_gate,'output',pulse0,'input')

    train_gate = moose.PulseGen('/model/train_gate')
    train_gate.level[0] = inject
    train_gate.delay[0] = 0
    train_gate.delay[1] = dt_train
    train_gate.width[0] = width_train
    train_gate.baseLevel = base_current
    train_gate.trigMode = 2

    moose.connect(train_gate,'output',burst_gate,'input')
    
    experiment_gate = moose.PulseGen('/model/experiment_gate')
    experiment_gate.level[0] = inject
    experiment_gate.delay[0] = AP_delay
    experiment_gate.delay[1] = 1e9
    experiment_gate.width[0] = exp_duration
    experiment_gate.baseLevel = base_current
    experiment_gate.trigMode = 0

    moose.connect(experiment_gate,'output',train_gate,'input')

    
    data = moose.Neutral('/data')
    pulse0_tab = moose.Table('/data/pulse0_tab')
    burst_gate_tab = moose.Table('/data/burst_gate_tab')
    train_gate_tab = moose.Table('/data/train_gate_tab')
    experiment_gate_tab = moose.Table('/data/experiment_gate_tab')

    moose.connect(pulse0_tab,'requestOut',pulse0,'getOutputValue')
    moose.connect(burst_gate_tab,'requestOut',burst_gate,'getOutputValue')
    moose.connect(train_gate_tab,'requestOut',train_gate,'getOutputValue')
    moose.connect(experiment_gate_tab,'requestOut',experiment_gate,'getOutputValue')


    moose.start(simtime)

    f = plt.figure()
    ax = []
    
    ax.append(f.add_subplot(1,1,1))
    #ax.append(f.add_subplot(2,1,2))
    #ax.append(f.add_subplot(3,1,3))
    
    t = np.linspace(0.,simtime,len(pulse0_tab.vector))
    print len(t)
    #ax[0].plot(t,pulse0_tab.vector,'k')
    ax[0].plot(t,pulse0_tab.vector,'b',t,burst_gate_tab.vector,'r',t,train_gate_tab.vector,'g',t,experiment_gate_tab.vector,'k')
    #ax[2].plot(t,pulse2_tab.vector,'k',t,gate_tab.vector,'r')
    plt.show()
    

