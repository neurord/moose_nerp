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
from moose_nerp.prototypes.tables import DATA_NAME

def assign_clocks(model_container_list, simdt, plotdt,hsolveYN, name_soma):
    log.info('SimDt={}, PlotDt={}', simdt, plotdt)
    for tab in moose.wildcardFind(DATA_NAME+'/##[TYPE=Table]'):
        moose.setClock(tab.tick,plotdt)
    for tick in range(0, 13):
        moose.setClock(tick, simdt)
        # 1 - CaConc, DifShell, DifBuffer
        # 2 — channels and synchans
        # 4 — compartments
        # 5 - SpikeGen
        # 6 — hsolver
        # 7 - TimeTables for moose_nerp (see ttables.py)
        # 8 - Tables
        # 12 - Function
    #problem if TimeTable uses plotdt?
    moose.setClock(8, plotdt)
    # 8 — hdf5datawriter, tables

    for path in model_container_list:
        if hsolveYN:
            hsolve = moose.HSolve(path + '/hsolve')
            hsolve.dt=simdt
            # Compartment is transformed into zombiecompartment after below statement.
            hsolve.target = path+'/'+name_soma
            log.info("Using HSOLVE for {} clock {}", hsolve.path, hsolve.tick)
    moose.reinit()
