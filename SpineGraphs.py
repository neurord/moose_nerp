def spinetabs():
    spinecatab=[]
    spinevmtab=[]
    for neurtype,neurnum in zip(neurontypes,range(len(neurontypes))):
        spinecatab.append(moose.Table('/data/SpCa%s' % (neurtype)))
        spinevmtab.append(moose.Table('/data/SpVm%s' % (neurtype)))
        spname=MSNsyn[neurtype]['ampa'][1].path[0:rfind(MSNsyn[neurtype]['ampa'][1].path,'/')+1]
        spine=moose.element(spname)
        moose.connect(spinevmtab[neurnum], 'requestData', spine, 'get_Vm')
        if calcium:
            cal=moose.element(spname+caName)
            moose.connect(spinecatab[neurnum], 'requestData', cal, 'get_Ca')
    return spinecatab,spinevmtab

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
