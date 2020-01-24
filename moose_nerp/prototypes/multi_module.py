import moose
import importlib

from moose_nerp.prototypes import (create_model_sim,
                                   cell_proto,
                                   calcium,
                                   util,
                                   standard_options)

def multi_modules(neuron_modules,model,buf_cap):
    for neur_module in neuron_modules:
        nm=importlib.import_module('moose_nerp.'+neur_module)
        #probably a good idea to give synapses to all neurons (or no neurons)
        nm.synYN = model.synYN
        nm.param_cond.neurontypes = util.neurontypes(nm.param_cond)
        syn,neur=cell_proto.neuronclasses(nm,module=neur_module)
        for new_neur in neur.keys():
            if nm.synYN:
                model.syn[new_neur]=syn[new_neur]
            model.neurons[new_neur]=neur[new_neur]
            buf_cap[new_neur]=nm.param_ca_plas.BufferCapacityDensity
            model.param_syn.NumSyn[new_neur]=nm.param_syn.NumSyn[new_neur]
    return buf_cap
