"""\
Add a single synapse to the neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import moose

from moose_nerp.prototypes import (connect,
                     plasticity,
                     logutil)
log = logutil.Logger()

def plasticity_test(model, syncomp, syn_pop, stimtimes):
    plast={}
    stimtab={}
    if model.calYN  and model.plasYN:
        neu = moose.Neutral('/input')
        for neurtype in model.neurontypes():
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' % (neu.path, neurtype))
            stimtab[neurtype].vector = stimtimes

            syntype = model.CaPlasticityParams.Plas_syn.Name
            print(syntype,neurtype,syncomp)
            synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
            log.info('Synapse added to {.path}', synchan)
            connect.synconn(synchan,0,stimtab[neurtype], model.param_syn)

            ###Synaptic Plasticity
            plast[neurtype] = plasticity.plasticity(synchan,model.CaPlasticityParams.Plas_syn)
    return plast, stimtab
