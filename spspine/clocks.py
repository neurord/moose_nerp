#This is simplified clocks/hsolve setup for Moose 3.0.  
#No need to assign clocks except for output elements
"""\
Simulation time step. Note that there are no default clocks.

Information on how to use clocks can be read by typing: help("moose") in python.
"""

from __future__ import print_function, division

import moose 

def assign_clocks(model_container_list, dataName, simdt, plotdt,hsolveYN, printinfo):
    if printinfo:
        print('SimDt=%g, PlotDt=%g' % (simdt, plotdt))
    for tab in moose.wildcardFind(dataName+ '/##[TYPE=Table]'):
        moose.setClock(tab.tick,plotdt)
    moose.setClock(0, simdt)
    moose.setClock(1, simdt) 
    moose.setClock(2, simdt) #channels
    moose.setClock(3, simdt)
    moose.setClock(4, simdt) #compartments
    moose.setClock(5, simdt)
    moose.setClock(6, simdt) #hsolver
    for path in model_container_list:
        if hsolveYN:
            hsolve = moose.HSolve( '%s/hsolve' % (path))
            #hsolve.dt=simdt
            if printinfo:
                print("USING HSOLVE for", hsolve.path, "clock", hsolve.dt,hsolve.tick)
    moose.reinit()
