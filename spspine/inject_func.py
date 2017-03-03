#Eventually, update this for trains and bursts from Sriram's genesis functions

from __future__ import print_function, division
import numpy as np
import moose 

def setupinj(model, delay,width,neuron_pop):
    """Setup injections

    Note that the actual injected current is proportional to dt of the clock
    So, you need to use the same dt for stimulation as for the model
    Strangely, the pulse gen in compartment_net refers to  firstdelay, etc.
    """
    pg = moose.PulseGen('pulse')
    pg.firstDelay = delay
    pg.firstWidth = width
    pg.secondDelay = 1e9
    for ntype in neuron_pop.keys():
        for num, name in enumerate(neuron_pop[ntype]):
            injectcomp=moose.element(name +'/'+model.param_cond.NAME_SOMA)
            print("INJECT:", name, injectcomp.path)
            moose.connect(pg, 'output', injectcomp, 'injectMsg')
    return pg

###Voltage Clamp (incomplete)
def Vclam(delay,width,delay_2,r,c,gain,sat,gain_p,tau_1,tau_2,psat):
    pulseg=moose.PulseGen('pulse')
    pulseg.firstDelay=delay
    pulseg.firstWidth=width
    pulseg.secondDelay=delay_2
    lp=moose.RC('lowpass')
    lp.R=r
    lp.C=c
    DA=moose.DiffAmp('diffamp')
    DA.gain=gain
    DA.saturation=sat
    pid=moose.PIDController('PID')
    pid.gain=gain_p
    pid.tauI=tau_1
    pid.tauD=tau_2
    pid.saturation=psat
    comp=moose.element("/proto")
    moose.connect(pulseg,"output",lp,"injectIn")
    moose.connect(lp, "output", DA, "plusIn")
    moose.connect(DA,"output",pid,"commandIn")
    moose.connect(comp, "VmOut",pid, "sensedIn")
    moose.connect(pid,"output",comp,"injectMsg")
    tab=moose.Table("/data/Im")
    moose.connect(tab,"requestOut",comp,"getIm")
    return tab

def inject_pop(population, num_inject):
    #select subset of neurons for injection
    choice_neurs={}
    for neurtype in population.keys():
       choice_neurs[neurtype]=list(np.random.choice(population[neurtype],num_inject,replace=False))
    return choice_neurs
    

