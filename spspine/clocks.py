#This is simplified clocks/hsolve setup for Moose 3.0.  
#No need to assign clocks except for output elements
"""\
Simulation time step. Note that there are no default clocks.

Information on how to use clocks can be read by typing: help("moose") in python.
"""

from __future__ import print_function, division

import moose 
from spspine import param_sim

def assign_clocks(model_container_list, dataName, simdt, plotdt,hsolve):
    if param_sim.printinfo:
        print('SimDt=%g, PlotDt=%g' % (param_sim.simdt, param_sim.plotdt))
    moose.setClock(0, simdt)
    moose.setClock(1, simdt)
    moose.setClock(2, simdt)
    moose.setClock(3, simdt)
    moose.setClock(4, simdt)
    moose.setClock(5, simdt)
    moose.setClock(9, plotdt)
    for path in model_container_list:
        if hsolve:
            hsolve = moose.HSolve( '%s/hsolve' % (path))
            if param_sim.printinfo:
                print("USING HSOLVE")
                print("hsolve clock", hsolve.path, hsolve.dt,hsolve.tick)
            moose.useClock( 1, path + '/hsolve', 'process' )
            hsolve.dt=simdt
    moose.useClock(9, dataName + '/##[TYPE=Table]', 'process')
    moose.reinit()
