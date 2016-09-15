"""\
Add a single synapse to the neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import moose

from spspine import (param_sim,
                     extern_conn,
                     plasticity,
                     logutil)
log = logutil.Logger()

def plastic_synapse(model, syncomp, syn_pop):
    syn={}
    plast={}
    stimtab={}
    if model.calYN and model.plasYN:
        neu = moose.Neutral('/input')
        for neurtype in model.neurontypes():
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' % (neu.path, neurtype))
            stimtab[neurtype].vector = param_sim.stimtimes
            for syntype in ('ampa','nmda'):
                synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
                log.info('Synapse added to {.path}', synchan)
                extern_conn.synconn(synchan,0,stimtab[neurtype],model.calYN)
                if syntype=='nmda':
                    synchanCa=moose.element(syn_pop[neurtype][syntype][syncomp].path+'/CaCurr')
                    log.info('Synapse added to {.path}', synchanCa)
                    extern_conn.synconn(synchanCa,0,stimtab[neurtype],model.calYN)
            syn[neurtype]=moose.SynChan(syn_pop[neurtype]['ampa'][syncomp])
            ###Synaptic Plasticity
            print(syn_pop[neurtype]['ampa'][syncomp], model.CaPlasticityParams)
            plast[neurtype] = plasticity.plasticity(syn_pop[neurtype]['ampa'][syncomp],
                                                    model.CaPlasticityParams.highThresh,
                                                    model.CaPlasticityParams.lowThresh,
                                                    model.CaPlasticityParams.highfactor,
                                                    model.CaPlasticityParams.lowfactor)

    return syn, plast, stimtab
