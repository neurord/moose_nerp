from __future__ import print_function, division
import numpy as np
from matplotlib import pyplot as plt

def spineFig(model,spinecatab,spinevmtab,simtime):
    plt.figure()
    t = np.linspace(0, simtime, len(spinevmtab[0][0].vector))
    if model.calYN:
        plt.subplot(211)
    for neurnum in range(len(model.neurontypes())):
        for oid in spinevmtab[neurnum]:
            print(oid.name,len(t),len(oid.vector))
            plt.plot(t,oid.vector,label=oid.path[oid.path.rfind('_')-2:])
        plt.ylabel('Vm')
    if model.calYN:
        plt.subplot(212)
        for neurnum in range(len(model.neurontypes())):
            for oid in spinecatab[neurnum]:
                plt.plot(t,1000*oid.vector,label=oid.path[oid.path.rfind('_')-2:])
            plt.ylabel('calcium, uM')
    plt.legend()
    plt.show()
