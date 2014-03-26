def spinetabs():
    spcatab=[]
    spvmtab=[]
    for typenum, neurtype in enumerate(sorted(neurontypes)):
        spcatab.append([])
        spvmtab.append([])
    for typenum, neurtype in enumerate(sorted(neurontypes)):
        for headnum,head in enumerate(spineHeads[neurtype]):
            print head.path, neurtype
            spvmtab[neurtype].append(moose.Table('/data/SpVm%s_%s' % (neurtype,split(head.path,'/')[compNameNum])))
            moose.connect(spvmtab[neurtype][headnum], 'requestData', head, 'get_Vm')
            if calcium:
                spcatab[typenum].append(moose.Table('/data/SpCa%s_%s' % (neurtype,split(head.path,'/')[compNameNum])))
                spcal=moose.element(head.path+'/'+caName)
                moose.connect(spcatab[typenum][headnum], 'requestData', spcal, 'get_Ca')
    return spcatab,spvmtab

def spineFig(spinecatab,spinevmtab):
    figure()
    t = np.linspace(0, simtime, len(spinevmtab[0].vec))
    if calcium:
        subplot(211)
    for neurnum in range(len(neurontypes)):
        plt.plot(t,spinevmtab[neurnum].vec,label=neurontypes[neurnum])
    if calcium:
        subplot(212)
        for neurnum in range(len(neurontypes)):
            plt.plot(t,spinecatab[neurnum].vec,label=neurontypes[neurnum])
    plt.legend()
    plt.show()
