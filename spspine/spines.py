from __future__ import print_function, division
import numpy as np
import moose

from param_spine import SpineParams
from param_sim import printinfo, printMoreInfo

def setSpineCompParams(comp,compdia,complen):
    comp.diameter=compdia
    comp.length=complen
    XArea=np.pi*compdia*compdia/4
    circumf=np.pi*compdia
    if printMoreInfo:
        print("Xarea,circumf of",comp.path, XArea,circumf,"CM",SpineParams.spineCM*complen*circumf)
    comp.Ra=SpineParams.spineRA*complen/XArea
    comp.Rm=SpineParams.spineRM/(complen*circumf)
    cm=SpineParams.spineCM*compdia*circumf
    if cm<1e-15:
        cm=1e-15
    comp.Cm=cm
    comp.Em=SpineParams.spineELEAK
    comp.initVm=SpineParams.spineEREST

def makeSpine (parentComp, compName,index, frac, necklen, neckdia, headdia):
    #frac is where along the compartment the spine is attached
    #unfortunately, these values specified in the .p file are not accessible
    neckName=compName+str(index)+SpineParams.nameneck
    neck=moose.Compartment(parentComp.path+'/'+neckName)
    if printMoreInfo:
        print(neck.path,"at",frac, "x,y,z=", parentComp.x,parentComp.y,parentComp.z)
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
    setSpineCompParams(neck,neckdia,necklen)
    
    headName=compName+str(index)+SpineParams.namehead
    head=moose.Compartment(parentComp.path+'/'+headName)
    moose.connect(neck, 'raxial', head, 'axial', 'Single' )
    head.x0=neck.x
    head.y0=neck.y
    head.z0=neck.z
    head.x=head.x
    head.y=head.y+headdia
    head.z=head.z
    setSpineCompParams(head,neckdia,necklen)
    #
    return head

def addSpines(container,ghkYN):
    headarray=[]
    for comp in moose.wildcardFind('%s/#[TYPE=Compartment]' %(container)):
        if 'soma' not in comp.path:
            numSpines=int(np.round(SpineParams.spineDensity*comp.length))
            spineSpace=comp.length/(numSpines+1)
            for index in range(numSpines):
                frac=(index+0.5)/numSpines
                #print comp.path,"Spine:", index, "located:", frac
                head=makeSpine (comp, 'spine',index, frac, SpineParams.necklen, SpineParams.neckdia, SpineParams.headdia)
                headarray.append(head)
                if SpineParams.spineChanList:
                    if ghkYN:
                        ghkproto=moose.element('/library/ghk')
                        ghk=moose.copy(ghkproto,comp,'ghk')[0]
                        moose.connect(ghk,'channel',comp,'channel')
                    for chanpath,cond in zip(SpineParams.spineChanlist,SpineParams.spineCond):
                        addOneChan(chanpath,cond,head,ghkYN)
            #end for index
    #end for comp
    if printinfo:
        print(len(headarray),"spines created in",container)
    return headarray
