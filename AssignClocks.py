#AssignClocks.py
"""\
Simulation time step. Note that there are no default clocks.

Information on how to use clocks can be read by typing: help("moose") in python.
"""

from __future__ import print_function, division

try:
    inited
except NameError:
    inited = False
def assign_clocks(model_container_list, inname, dataName, simdt, plotdt,hsolve):
    global inited
    # `inited` is for avoiding double scheduling of the same object
    if not inited:
        if printinfo:
            print('SimDt=%g, PlotDt=%g' % (simdt, plotdt))
        moose.setClock(0, simdt)
        moose.setClock(1, simdt)
        moose.setClock(2, simdt)
        moose.setClock(3, simdt)
        moose.setClock(4, simdt)
        moose.setClock(5, simdt)
        moose.setClock(6, plotdt)
        for path in model_container_list:
            if printinfo:
                print('Scheduling elements under:', path)
            if hsolve:
                if printinfo:
                    print("USING HSOLVE")
                hsolve = moose.HSolve( '%s/hsolve' % (path))
                moose.useClock( 1, '%s/hsolve' % (path), 'process' )
                hsolve.dt=simdt
            moose.useClock(0, '%s/##[ISA=Compartment]' % (path), 'init')
            moose.useClock(1, '%s/##[ISA=Compartment],%s/##[TYPE=CaConc]' % (path,path), 'process')
            moose.useClock(2, '%s/##[TYPE=SynChan],%s/##[TYPE=HHChannel],%s/##[TYPE=HHChannel2D]' % (path,path,path), 'process')
            moose.useClock(3, '%s/##[TYPE=Func],%s/##[TYPE=MgBlock],%s/##[TYPE=GHK]' % (path,path,path), 'process')
            moose.useClock(4, '%s/##[TYPE=SpikeGen],%s/##[TYPE=TimeTable]' % (path,inname), 'process')
        moose.useClock(5, '/##[TYPE=PulseGen]', 'process')
        moose.useClock(6, '%s/##[TYPE=Table]' % (dataName), 'process')
        inited = True
    moose.reinit()

def printclocks(begin,end):
    tk = moose.element('/clock/tick')
    for ii in range(begin,end):
        print('Elements on tick ', ii)
        for e in tk.neighbours['proc%s' % (ii)]:
            print(' ->', e.path)
