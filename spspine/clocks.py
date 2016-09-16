# -*- coding:utf-8 -*-

#This is simplified clocks/hsolve setup for Moose 3.0.  
#No need to assign clocks except for output elements
"""\
Simulation time step. Note that there are no default clocks.

Information on how to use clocks can be read by typing: help("moose") in python.
"""

from __future__ import print_function, division

from . import logutil
log = logutil.Logger()

import moose 

def assign_clocks(model_container_list, simdt, plotdt,hsolveYN):
    log.info('SimDt={}, PlotDt={}', simdt, plotdt)
    for tab in moose.wildcardFind('/data/##[TYPE=Table]'):
        moose.setClock(tab.tick,plotdt)
    for tick in range(0, 7):
        moose.setClock(tick, simdt)
        # 2 — channels
        # 4 — compartments
        # 6 — hsolver
    for path in model_container_list:
        if hsolveYN:
            hsolve = moose.HSolve(path + '/hsolve')
            #hsolve.dt=simdt
            log.info("Using HSOLVE for {} clock {}", hsolve.path, hsolve.tick)
    moose.reinit()
