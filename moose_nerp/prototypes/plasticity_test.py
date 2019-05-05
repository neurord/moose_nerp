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

            print('**** plasticity test ********',syntype,neurtype,syncomp)
            #synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
            synchan=moose.element(syncomp.path+'/'+syntype)
            sh = synchan.children[0]
            log.info('Synapse added to {.path}', synchan)
            connect.synconn(sh,0,stimtab[neurtype], model.param_syn)

            ###Synaptic Plasticity
            plast[neurtype] = plasticity.plasticity2(synchan,model.CaPlasticityParams.Plas_syn)
    return plast, stimtab

def short_term_plasticity_test(tt_syn_tuple,syn_delay=0,simdt=None,stp_params=None):
    tt=tt_syn_tuple[0]
    syn=tt_syn_tuple[1]
    synnum=tt_syn_tuple[2]
    synchan=moose.element(syn.parent)
    syntype=synchan.name
    neurtype=synchan.parent.parent.name
    syntab=moose.Table(tables.DATA_NAME+'/'+neurtype+'-'+tt.name+'_to_'+syntype)
    moose.connect(syntab,'requestOut',synchan,'getGk')
    if stp_params is not None:
        tabset=[]
        synapse=syn.synapse[synnum]
        existing_stp=[neigh.name for neigh in synchan.neighbors['childOut'] if 'stp' in neigh.name ]
        if existing_stp:
            index= int(sorted(existing_stp)[-1].split('stp')[-1])+1
        else:
            index=0
        print('****** STPT******** existing',existing_stp,'synapse',synnum,'stp index',index)
        plasticity.ShortTermPlas(synapse,index,stp_params,simdt,tt,'eventOut')
        tables.create_plas_tabs(synchan,syntab.name,tabset,['fac'+str(index),'dep'+str(index),'stp'+str(index)])
        return syntab,tabset
    else:
        return syntab

