import moose
import importlib

from moose_nerp.prototypes import (create_model_sim,
                                   cell_proto,
                                   calcium,
                                   util,
                                   standard_options)

def multi_modules(neuron_modules,model,buf_cap,change_syn={}):
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
    for neur in list(set(model.neurons.keys())&set(change_syn.keys())):
        for syntype,factor in change_syn[neur].items():
            model.param_syn.NumSyn[neur][syntype]={k:int(v*factor) for k,v in model.param_syn.NumSyn[neur][syntype].items()}
        print ('>>>>>> updated NumSyn for',neur,model.param_syn.NumSyn[neur])
    return buf_cap
