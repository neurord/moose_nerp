"""\
Can add single synapse to single neuron model to test calcium and plasticity
"""
from __future__ import print_function, division
import param_cond
import param_sim
import param_ca_plas as parcal
import plasticity
from spspine import extern_conn
import moose 

def test_plas(syncomp,calYN,plasYN,inpath,syn_pop):
    syn={}
    plast={}
    stimtab={}
    if calYN and plasYN:
        moose.Neutral(inpath)
        for neurtype in param_cond.neurontypes:
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' %(inpath,neurtype))
            stimtab[neurtype].vector = param_sim.stimtimes
            for syntype in ('ampa','nmda'):
                synchan=moose.element(syn_pop[neurtype][syntype][syncomp])
                if param_sim.printinfo:
                    print("Synapse added to", synchan.path)
                extern_conn.synconn(synchan,0,stimtab[neurtype],calYN)
                if syntype=='nmda':
                    synchanCa=moose.element(syn_pop[neurtype][syntype][syncomp].path+'/CaCurr')
                    if param_sim.printinfo:
                        print("Synapse added to", synchanCa.path)
                    extern_conn.synconn(synchanCa,0,stimtab[neurtype],calYN)
            syn[neurtype]=moose.SynChan(syn_pop[neurtype]['ampa'][syncomp])
            ###Synaptic Plasticity
            if plasYN:
                print(syn_pop[neurtype]['ampa'][syncomp],parcal.highThresh,parcal.lowThresh,parcal.highfactor,parcal.lowfactor,parcal.caName)
                plast[neurtype] = plasticity.plasticity(syn_pop[neurtype]['ampa'][syncomp],
                                                        parcal.highThresh,
                                                        parcal.lowThresh,
                                                        parcal.highfactor,
                                                        parcal.lowfactor,
                                                        parcal.caName)
    return syn, plast, stimtab
