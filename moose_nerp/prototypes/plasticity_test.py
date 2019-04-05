"""\
Add a single synapse to the neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import moose

from moose_nerp.prototypes import (connect,
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

def short_term_plasticity_test(synchan,tt,syn_delay=0,simdt=None,stp_params=None):
    syntab=moose.Table('/syntab')
    moose.connect(syntab,'requestOut',synchan,'getGk')
    syn=moose.element(synchan.path+'/SH')
    if stp_params is not None:
        tabset={}
        #Connect time table of synaptic inputs to synapse, and create stp
        connect.plain_synconn(syn,tt,syn_delay,simdt=simdt,stp_params=stp_params)
        #create output table for the synaptic response
        if stp_params.depress is not None:
            deptab = moose.Table('/deptab')
            dep=moose.element(synchan.path+'/dep0')
            moose.connect(deptab, 'requestOut', dep, 'getValue')
            tabset['dep']=deptab
        if stp_params.facil is not None:
            factab = moose.Table('/factab')
            fac=moose.element(synchan.path+'/fac0')
            moose.connect(factab, 'requestOut', fac, 'getValue')
            tabset['fac']=factab
        plas_tab = moose.Table('/plastab')
        plas=moose.element(synchan.path+'/stp0')
        moose.connect(plas_tab, 'requestOut', plas, 'getValue')
        tabset['plas']=plas_tab
        return syntab,tabset
    else:
        return syntab

#Next, add in to this stp test creation of time tables, TEST
#add to multisim TEST
#add to network sim
