#Eventually, update this for trains and bursts from Sriram's genesis functions

from __future__ import print_function, division
import moose 

def setupinj(model, delay,width,neuron):
    """Setup injections

    Note that the actual injected current is proportional to dt of the clock
    So, you need to use the same dt for stimulation as for the model
    Strangely, the pulse gen in compartment_net refers to  firstdelay, etc.
    """
    pg = moose.PulseGen('pulse')
    pg.firstDelay = delay
    pg.firstWidth = width
    pg.secondDelay = 1e9
    if model.single:
        for neurtype in model.neurontypes():
            print("INJECT:",neurtype, neuron[neurtype].keys(),neuron[neurtype]['comps'][0])
            moose.connect(pg, 'output', neuron[neurtype]['comps'][0], 'injectMsg')  
    else:
        for num, name in enumerate(model.neurontypes()):
            for ii in range(len(MSNpop['pop'][num])):
                injectcomp=moose.element(MSNpop['pop'][num][ii]+'/soma')
                print("INJECT:", name, injectcomp.path)
                moose.connect(pg, 'outputOut', injectcomp, 'injectMsg')  
    return pg
