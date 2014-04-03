######TestSynPlas.py##########
"""\
Can add single synapse to single neuron model to test calcium and plasticity
"""
from __future__ import print_function, division

def TestSynPlas(syncomp,calYN,plasYN,inpath):
    syn={}
    plas={}
    stimtab={}
    if (calYN==1 and plasYN==1):
        gluChans=['ampa','nmda']
        moose.Neutral(inpath)
        for neurtype in neurontypes:
            stimtab[neurtype]=moose.TimeTable('%s/TimTab%s' %(inpath,neurtype))
            stimtab[neurtype].vec=stimtimes
            for syntype in gluChans:
                synchan=moose.element(MSNsyn[neurtype][syntype][syncomp])
                if printinfo:
                    print("Synapse added to", synchan.path)
                synchan.synapse.num=1
                synchan.synapse[0].delay=0.001
                m = moose.connect(stimtab[neurtype], 'event', moose.element(synchan.path + '/synapse'),  'addSpike')
                if syntype=='nmda':
                    synchanCa=moose.element(MSNsyn[neurtype][syntype][syncomp].path+'/CaCurr')
                    if printinfo:
                        print("Synapse added to", synchanCa.path)
                    synchanCa.synapse.num=1
                    synchanCa.synapse[0].delay=0.001
                    m = moose.connect(stimtab[neurtype], 'event', moose.element(synchanCa.path + '/synapse'),  'addSpike')
            syn[neurtype]=moose.SynChan(MSNsyn[neurtype]['ampa'][syncomp])
            ###Synaptic Plasticity
            if plasYN:
                plas[neurtype]=plasticity(MSNsyn[neurtype]['ampa'][syncomp],highThresh,lowThresh,highfactor,lowfactor)
    return syn, plas, stimtab

