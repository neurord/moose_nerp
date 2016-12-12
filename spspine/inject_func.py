#Eventually, update this for trains and bursts from Sriram's genesis functions

from __future__ import print_function, division
import moose 
from spspine.cell_proto import NAME_SOMA

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
            injectcomp=moose.element(name +'/'+NAME_SOMA)
            print("INJECT:", name, injectcomp.path)
            moose.connect(pg, 'output', injectcomp, 'injectMsg')  
    return pg
