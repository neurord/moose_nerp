#inject_func.py
#Eventually, update this for trains and bursts from Sriram's genesis functions

from __future__ import print_function, division
import moose 
import param_cond as parcond
import param_sim as parsim

def setupinj(delay,width,neuron):
    """Setup injections

    Note that the actual injected current is proportional to dt of the clock
    So, you need to use the same dt for stimulation as for the model
    Strangely, the pulse gen in compartment_net refers to  firstdelay, etc.
    """
    pg = moose.PulseGen('pulse')
    pg.firstDelay = delay
    pg.firstWidth = width
    pg.secondDelay = 1e9
    if parsim.single:
        for neurtype in parcond.neurontypes:
            print("INJECT:",neurtype, neuron[neurtype].keys(),neuron[neurtype]['comps'][0])
            moose.connect(pg, 'output', neuron[neurtype]['comps'][0], 'injectMsg')  
    else:
        for neurnum in range(len(parcond.neurontypes)):
            for ii in range(len(MSNpop['pop'][neurnum])):
                injectcomp=moose.element(MSNpop['pop'][neurnum][ii]+'/soma')
                print("INJECT:", parcond.neurontypes[neurnum],injectcomp.path)
                moose.connect(pg, 'outputOut', injectcomp, 'injectMsg')  
    return pg
