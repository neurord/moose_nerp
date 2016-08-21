"""\
Create table for spike generators of network, and Vm when not graphing.
"""
from __future__ import print_function, division
import numpy as np
import moose

from spspine import param_sim

def SpikeTables(model, single,MSNpop,showgraphs,vmtab):
    spiketab=[]
    if not single:
        for typenum,neurtype in enumerate(model.neurontypes()):
            spiketab.append([])
            for tabnum,neurpath in enumerate(MSNpop['pop'][typenum]):
                neurnum=int(neurpath[find(neurpath,'_')+1:])
                sg=moose.element(neurpath+'/soma/spikegen')
                spiketab[typenum].append(moose.Table('/data/outspike%s_%d' % (neurtype,neurnum)))
                if param_sim.printinfo:
                    print(neurtype,neurnum,neurpath,sg.path,spiketab[typenum][tabnum])
                m=moose.connect(sg, 'event', spiketab[typenum][tabnum],'spike')
                if not showgraphs:
                    vmtab[typenum].append(moose.Table('/data/soma%s_%s'%(neurtype,neurnum)))
                    plotcomp=moose.element(neurpath+'/soma')
                    m=moose.connect(vmtab[typenum][tabnum], 'requestOut', plotcomp, 'getVm')
    return spiketab, vmtab

def writeOutput(model, outfilename,spiketab,vmtab,MSNpop):
    outvmfile='Vm'+outfilename
    outspikefile='Spike'+outfilename
    if param_sim.printinfo:
        print("SPIKE FILE", outspikefile, "VM FILE", outvmfile)
    outspiketab=list()
    outVmtab=list()
    for typenum,neurtype in enumerate(model.neurontypes()):
        outspiketab.append([])
        outVmtab.append([])
        for tabnum,neurname in enumerate(MSNpop['pop'][typenum]):
            underscore=find(neurname,'_')
            neurnum=int(neurname[underscore+1:])
            print(neurname.split('_')[1])
            if param_sim.printinfo:
                print(neurname,"is", neurtype,", num=",neurnum,spiketab[typenum][tabnum].path,vmtab[typenum][tabnum])
            outspiketab[typenum].append(insert(spiketab[typenum][tabnum].vector,0, neurnum))
            outVmtab[typenum].append(insert(vmtab[typenum][tabnum].vector,0, neurnum))
    savez(outspikefile,D1=outspiketab[0],D2=outspiketab[1])
    savez(outvmfile,D1=outVmtab[0],D2=outVmtab[1])
