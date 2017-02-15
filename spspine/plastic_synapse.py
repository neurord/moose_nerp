"""\
Add a single synapse to the neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import moose

from spspine import (connect,
                     plasticity,
                     logutil)
from spspine.d1d2.param_syn import NAME_AMPA
log = logutil.Logger()

def plastic_synapse(model, syncomp, syn_pop, stimtimes):
    plast={}
    stimtab={}
    if model.calYN  and model.plasYN:
        neu = moose.Neutral('/input')
        for neurtype in model.neurontypes():
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' % (neu.path, neurtype))
            stimtab[neurtype].vector = stimtimes

            syntype = model.CaPlasticityParams.syntype
            print(syntype,neurtype,syncomp)
            synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
            log.info('Synapse added to {.path}', synchan)
            connect.synconn(synchan,0,stimtab[neurtype])

            ###Synaptic Plasticity
            plast[neurtype] = plasticity.plasticity(synchan,model.CaPlasticityParams.NAME_CALCIUM,
                                                    model.CaPlasticityParams.highThresh,
                                                    model.CaPlasticityParams.lowThresh,
                                                    model.CaPlasticityParams.highfactor,
                                                    model.CaPlasticityParams.lowfactor)
    return plast, stimtab
