"""\
Add a single synapse to the neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import moose

from moose_nerp.prototypes import (connect,
                                   tables,
                                   plasticity,
                                   logutil,
                                   util)
log = logutil.Logger()

def plasticity_test(model, syncomp=None, syn_pop=None, stimtimes=None):
    syntype = model.CaPlasticityParams.Plas_syn.Name
    if stimtimes is None:
        stimtimes = [.1,.12]
    if syncomp is None:
        path = model.neurons[list(model.neurons)[0]].path
        syncomp = moose.wildcardFind(path+'/##/'+syntype+'[ISA=SynChan]')[0].parent
    plast={}
    stimtab={}
    if model.calYN  and model.plasYN:
        neu = moose.Neutral('/input')
        for neurtype in util.neurontypes(model.param_cond):
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' % (neu.path, neurtype))
            stimtab[neurtype].vector = stimtimes

            print(syntype,neurtype,syncomp)
            #synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
            synchan=moose.element(syncomp.path+'/'+syntype)
            sh = synchan.children[0]
            log.info('Synapse added to {.path}', synchan)
            connect.synconn(sh,0,stimtab[neurtype], model.param_syn)

            ###Synaptic Plasticity
            plast[neurtype] = plasticity.plasticity2(synchan,model.CaPlasticityParams.Plas_syn)
    return plast, stimtab

def short_term_plasticity_test(syn,tt,syn_delay=0,simdt=None,stp_params=None):
    synchan=moose.element(syn.parent)
    synname=synchan.name
    syntab=moose.Table(tables.DATA_NAME+'/'+synname+'_syntab')
    moose.connect(syntab,'requestOut',synchan,'getGk')
    if stp_params is not None:
        tabset=[]
        jj=syn.synapse.num-1
        synapse=syn.synapse[jj]
        index=0  #need to detect existance of other fac, dep or stp elements and update index accordingly
        plasticity.ShortTermPlas(synapse,index,stp_params,simdt,tt,'eventOut')
        tables.create_plas_tabs(synchan,syntab.name,tabset,['fac','dep','stp'])
        return syntab,tabset
    else:
        return syntab

