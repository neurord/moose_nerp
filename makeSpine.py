spineDensity=0.1e6      #should make this distance dependent
necklen=0.3e-6          #define all these parameters elsewhere
neckdia=0.1e-6
headdia=0.5e-6
nameneck='neck'
namehead='head'

def makeSpine (parentComp, compName,index, frac, necklen, neckdia, headdia):
    #frac is where along the compartment the spine is attached
    #unfortunately, these values specified in the .p file are not accessible
    RA=4*4    #additional factor of 4 due to exptl higher than expected Ra Spine
    RM=2.8
    CM=0.01
    ELEAK=-50e-3
    EREST=-80e-3
    neckName=compName+str(index)+nameneck
    neck=moose.Compartment(parentComp.path+'/'+neckName)
    if printinfo:
        print neck.path,"at",frac, "x,y,z=", parentComp.x,parentComp.y,parentComp.z
    moose.connect(parentComp,'raxial',neck,'axial','Single')
    x=parentComp.x0+ frac * (parentComp.x - parentComp.x0)
    y=parentComp.y0+ frac * (parentComp.y - parentComp.y0)
    z=parentComp.z0+ frac * (parentComp.z - parentComp.z0)
    neck.x0=x
    neck.y0=y
    neck.z0=z
    #could pass in an angle and use cos and sin to set y and z
    neck.x=x
    neck.y=y + necklen
    neck.z=z
    neck.diameter=neckdia
    neck.length=necklen
    XArea=math.pi*neckdia*neckdia/4
    circumf=math.pi*neckdia
    #print "NECK Xarea,circumf",XArea,circumf,"CM",CM*necklen*circumf
    neck.Ra=RA*necklen/XArea
    neck.Rm=RM/(necklen*circumf)
    cm=CM*neckdia*circumf
    if cm<1e-15:
        cm=1e-15
    neck.Cm=cm
    neck.Em=ELEAK
    neck.initVm=EREST
    
    headName=compName+str(index)+namehead
    head=moose.Compartment(parentComp.path+'/'+headName)
    moose.connect(neck, 'raxial', head, 'axial', 'Single' )
    head.x0=neck.x
    head.y0=neck.y
    head.z0=neck.z
    head.x=head.x
    head.y=head.y+headdia
    head.z=head.z
    head.diameter=headdia
    head.length=headdia
    XArea=math.pi*headdia*headdia/4
    circumf=math.pi*headdia
    #print "HEAD Xarea,circumf",XArea,circumf,"CM",CM*headdia*circumf
    head.Ra=RA*headdia/XArea
    head.Rm=RM/(headdia*circumf)
    cm=CM*headdia*circumf
    if cm<1e-15:
        cm=1e-15
    head.Cm=cm
    head.Em=ELEAK
    head.initVm=EREST
    #
    return head

def addChansSpines(comp,chanlist,condlist):
    #Note that this is mostly redundant with ~14 lines that add channels to compartments
    #Consider merging them into a single addChans function
    length=moose.Compartment(comp).length
    diam=moose.Compartment(comp).diameter
    SA=pi*length*diam
    if ghkYN:
        ghkproto=moose.element('/library/ghk')
        ghk=moose.copy(ghkproto,comp,'ghk')[0]
        moose.connect(ghk,'channel',comp,'channel')
    for chanpath,cond in zip(chanlist,condlist):
        proto = moose.HHChannel('/library/'+ chanpath)
        chan = moose.copy(proto, comp, chanpath)[0]
        chan.Gbar=cond*SA
        channame=chan.path[rfind(chan.path,'/')+1:]
            #If we are using GHK AND it is a calcium channel, connect it to GHK
        if ghkYN and isCaChannel(channame):
            moose.connect(chan,'permeability',ghk,'addPermeability')
            moose.connect(comp,'VmOut',chan,'Vm')
        else:
            moose.connect(chan, 'channel', comp, 'channel')

def addSpines(container):
    headarray=[]
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        if 'soma' not in comp:
            numSpines=int(np.round(spineDensity*comp.length))
            spineSpace=comp.length/(numSpines+1)
            for index in range(numSpines):
                frac=(index+0.5)/numSpines
                #print comp.path,"Spine:", index, "located:", frac
                head=makeSpine (comp, 'spine',index, frac, necklen, neckdia, headdia)
                headarray.append(head)
                if spineChanList:
                  addChansSpines(head,spineChanList,spineCond)
            #end for index
    #end for comp
    print len(headarray),"spines created in",container
    return headarray
