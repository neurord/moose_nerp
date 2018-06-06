from __future__ import print_function, division
import numpy as np
from matplotlib import pyplot as plt
from moose_nerp.prototypes.util import neurontypes

def spineFig(model,spinecatab,spinevmtab,simtime):
    f=plt.figure()
    f.canvas.set_window_title('Spines')
    t = np.linspace(0, simtime, len(spinevmtab[0][0].vector))
    if model.calYN:
        plt.subplot(211)
    for neurnum in range(len(neurontypes(model.param_cond))):
        for oid in spinevmtab[neurnum]:
            #find()-2 removes Vm from name, split and join removes dend from name
            name = ''.join(oid.name[oid.name.find('_')-2:].split('dend'))
            plt.plot(t,oid.vector,label=name)
        plt.ylabel('Vm')
    if model.calYN:
        plt.subplot(212)
        for neurnum in range(len(neurontypes(model.param_cond))):
            for oid in spinecatab[neurnum]:
                name=''.join(oid.name[oid.name.find('_')-2:].split('dend'))
                plt.plot(t,1000*oid.vector,label=name)
            plt.ylabel('calcium, uM')
    plt.legend()
    plt.show()
