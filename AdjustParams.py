#This adjusts conductance of several channels using multiplicative factor
#List of factors contains the change to apply to each channel
def adjustParams(container,GnaCond,Cond,factlist,chanlist):
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        length=moose.Compartment(comp).length
        diam=moose.Compartment(comp).diameter
        xloc=moose.Compartment(comp).x
        yloc=moose.Compartment(comp).y
        dist=sqrt(xloc*xloc+yloc*yloc)
        SA=pi*length*diam
        if chanlist.__contains__('NaF'):
            fact=factlist[chanlist.index('NaF')]
            chan=moose.element(comp.path+'NaF')
            if (dist<distTable['prox']):
                nachan.Gbar =GnaCond[0]*SA*fact
            else:
                if (dist<distTable['mid']):
                    nachan.Gbar = GnaCond[1]*SA*fact
                else:
                    nachan.Gbar = GnaCond[2]*SA*fact
        for channame in chanlist:
            fact=factlist[chanlist.index(channame)]
            chan=moose.element(comp.path+'/'+channame)
            print "Channel GBAR adjustment:",chan.path,fact
            if channame != 'NaF':
                if (dist<distTable['prox']):
                    chan.Gbar = Cond[channame][0]*SA*fact
                else:
                    if (dist<distTable['mid']):
                        chan.Gbar = Cond[channame][1]*SA*fact
                    else:
                        chan.Gbar = Cond[channame][2]*SA*fact
#No return
