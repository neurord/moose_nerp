def setupinj(delay,width):
#Note that the actual injected current is proportional to dt of the clock
#So, you need to use the same dt for stimulation as for the model
#Strangely, the pulse gen in compartment_net refers to  firstdelay, etc.
    pg = moose.PulseGen('pulse')
    pg.firstDelay = delay
    pg.firstWidth = width
    if single:
        for neurtype in neurontypes:
            print "INJECT:",neurtype, neuron[neurtype].keys(),neuron[neurtype]['comps'][0]
            moose.connect(pg, 'outputOut', neuron[neurtype]['comps'][0], 'injectMsg')  
    else:
        for neurnum in range(len(neurontypes)):
            for ii in range(len(MSNpop['pop'][neurnum])):
                injectcomp=moose.element(MSNpop['pop'][neurnum][ii]+'/soma')
                print "INJECT:", neurontypes[neurnum],injectcomp.path
                moose.connect(pg, 'outputOut', injectcomp, 'injectMsg')  
    return pg
