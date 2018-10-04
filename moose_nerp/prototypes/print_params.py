import moose

print ('moose version', moose.__version__)

def print_elem_params(model, neur, param_sim):
    ''' neuron ->  output of neurons from cell_proto.neuronclasses(model)
        ntype -> 'D1' Provide neuron type to print moose compartment values for
        a single neuron type.
    '''

    print('*#*#*#* Parameters for simulation of', neur)
    if param_sim.hsolve==1:
        comptype='ZombieCompartment'
        chantype='ZombieHHChannel'
        catypes=['ZombieCaConc']
        hs=moose.element(neur+'/hsolve')
        print ('hsolve: ', hs.name, 'dt=',hs.dt, 'tick=',hs.tick, 'vtable', hs.vDiv,hs.vMax,hs.vMin,'catab',
               hs.caDiv,hs.caMax,hs.caMin)
    else:
        comptype='Compartment'
        chantype='HHChannel'
        catypes=['CaConc']

    print(param_sim, 'cal=',model.calYN,'syn=',model.synYN,'spine=',model.spineYN,'ca type',
          model.param_ca_plas.CaShellModeDensity)
    
    if model.calYN and max(list(model.param_ca_plas.CaShellModeDensity.values()))>0:
        catypes = catypes+['DifShell', 'DifBuffer', 'MMPump']

    for comp in moose.wildcardFind('{}/#[TYPE={}]'.format(neur, comptype)):
        print('comp:',comp.name, 'Rm',comp.Rm, 'Cm=',comp.Cm, 'Ra=', comp.Ra, 'tick',comp.tick,'dt',comp.dt, comp.className)
        for chan in moose.wildcardFind('{}/#[TYPE={}]'.format(comp.path,chantype)): # compartnents
          print ('chan:', chan.name, 'Gbar',chan.Gbar,'X,Y power', chan.Xpower,chan.Ypower,'Ek',chan.Ek, 'class',
                 chan.className,'tick', chan.tick, 'dt',chan.dt)

        for caclass in catypes:
            for pool in moose.wildcardFind('{}/#[TYPE={}]'.format(comp.path, caclass)):
                if 'CaConc' in pool.className:
                    print('CaConc: ',pool.name, pool.className, 'caBasal', pool.CaBasal, 'B', pool.B, 'Tau', pool.tau,
                          'thickness', pool.thick,'tick',pool.tick, 'dt', pool.dt)
                elif 'DifShell' in pool.className:
                    print('DiffShell: ', pool.name, pool.className, 'Ceq', pool.Ceq,'D', pool.D, 'volume', pool.volume,
                          'thickness', pool.thickness, 'innerArea', pool.innerArea, 'outerArea', pool.outerArea,
                          'diameter', pool.diameter,'tick',pool.tick, 'dt', pool.dt)
                elif 'Buffer' in pool.className:
                    print('Buff shell: ', pool.name, pool.className, 'bTot', pool.bTot, 'kb',pool.kb, 'kf',pool.kf, 'D',
                          pool.D,'volume', pool.volume, 'thickness',pool.thickness, 'innerArea',pool.innerArea,
                          'outerArea',pool.outerArea, 'diameter', pool.diameter, 'tick',pool.tick, 'dt', pool.dt)
                else:
                    print ('Pump: ', pool.name, pool.className, 'tick', pool.tick,'dt', pool.dt, 'kd', pool.kd, 'Vmax',
                           pool.Vmax)
