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
        if 'NaF' in chanlist:
            fact=factlist[chanlist.index('NaF')]
            chan=moose.element(comp.path+'NaF')
            nachan.Gbar = GnaCond[dist_num(distTable, dist)] * SA * fact
        for channame in chanlist:
            fact=factlist[chanlist.index(channame)]
            chan=moose.element(comp.path+'/'+channame)
            print "Channel GBAR adjustment:",chan.path,fact
            if channame != 'NaF':
                chan.Gbar = Cond[channame][dist_num(distTable, dist)] * SA * fact
#No return
