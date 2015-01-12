######TestSynPlas.py##########
"""\
Can add single synapse to single neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import plasticity as plas
from param_cond import neurontypes
from param_sim import printinfo, stimtimes
import param_ca_plas as parcal
import plasticity as plas
from extern_conn import synconn 
import moose 

def test_plas(syncomp,calYN,plasYN,inpath,syn_pop):
    syn={}
    plast={}
    stimtab={}
    if (calYN==1 and plasYN==1):
        gluChans=['ampa','nmda']
        moose.Neutral(inpath)
        for neurtype in neurontypes:
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' %(inpath,neurtype))
            stimtab[neurtype].vector=stimtimes
            for syntype in gluChans:
                synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
                if printinfo:
                    print("Synapse added to", synchan.path)
                synconn(synchan,0,stimtab[neurtype],calYN)
                if syntype=='nmda':
                    synchanCa=moose.element(syn_pop[neurtype][syntype][syncomp].path+'/CaCurr')
                    if printinfo:
                        print("Synapse added to", synchanCa.path)
                    synconn(synchanCa,0,stimtab[neurtype],calYN)
            syn[neurtype]=moose.SynChan(syn_pop[neurtype]['ampa'][syncomp])
            ###Synaptic Plasticity
            if plasYN:
                print (syn_pop[neurtype]['ampa'][syncomp],parcal.highThresh,parcal.lowThresh,parcal.highfactor,parcal.lowfactor,parcal.caName)
                plast[neurtype]=plas.plasticity(syn_pop[neurtype]['ampa'][syncomp],parcal.highThresh,parcal.lowThresh,parcal.highfactor,parcal.lowfactor,parcal.caName)
    return syn, plast, stimtab

