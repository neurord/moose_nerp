#This is simplified clocks/hsolve setup for Moose 3.0.  
#No need to assign clocks except for output elements
"""\
Simulation time step. Note that there are no default clocks.

Information on how to use clocks can be read by typing: help("moose") in python.
"""

from __future__ import print_function, division
import param_sim as sim
import moose 

def assign_clocks(model_container_list, dataName, simdt, plotdt,hsolve):
    if sim.printinfo:
        print('SimDt=%g, PlotDt=%g' % (sim.simdt, sim.plotdt))
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
            if sim.printinfo:
                print("USING HSOLVE")
                print("hsolve clock", hsolve.path, hsolve.dt,hsolve.tick)
            moose.useClock( 1, '%s/hsolve' % (path), 'process' )
            hsolve.dt=simdt
    moose.useClock(9, '%s/##[TYPE=Table]' % (dataName), 'process')
    moose.reinit()
