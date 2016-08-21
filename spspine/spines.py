from __future__ import print_function, division
import numpy as np
import moose

from spspine import param_sim

NAME_NECK = "neck"
NAME_HEAD = "head"

def setSpineCompParams(model, comp,compdia,complen):
    comp.diameter=compdia
    comp.length=complen
    XArea=np.pi*compdia*compdia/4
    circumf=np.pi*compdia
    if param_sim.printMoreInfo:
        print("Xarea,circumf of",comp.path, XArea,circumf,"CM", model.SpineParams.spineCM*complen*circumf)
    comp.Ra = model.SpineParams.spineRA*complen/XArea
    comp.Rm = model.SpineParams.spineRM/(complen*circumf)
    cm = model.SpineParams.spineCM*compdia*circumf
    if cm<1e-15:
        cm=1e-15
    comp.Cm = cm
    comp.Em = model.SpineParams.spineELEAK
    comp.initVm = model.SpineParams.spineEREST

def makeSpine(model, parentComp, compName,index, frac, necklen, neckdia, headdia):
    #frac is where along the compartment the spine is attached
    #unfortunately, these values specified in the .p file are not accessible
    neck_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_NECK)
    neck = moose.Compartment(neck_path)
    if param_sim.printMoreInfo:
        print(neck.path,"at",frac, "x,y,z=", parentComp.x,parentComp.y,parentComp.z)
    moose.connect(parentComp,'raxial',neck,'axial','Single')
    x=parentComp.x0+ frac * (parentComp.x - parentComp.x0)
    y=parentComp.y0+ frac * (parentComp.y - parentComp.y0)
    z=parentComp.z0+ frac * (parentComp.z - parentComp.z0)
    neck.x0, neck.y0, neck.z0 = x, y, z
    #could pass in an angle and use cos and sin to set y and z
    neck.x, neck.y, neck.z = x, y + necklen, z
    setSpineCompParams(model, neck,neckdia,necklen)

    head_path = '{}/{}{}{}'.format(parentComp.path, compName, index, NAME_HEAD)
    head = moose.Compartment(head_path)
    moose.connect(neck, 'raxial', head, 'axial', 'Single')
    head.x0, head.y0, head.z0 = neck.x, neck.y, neck.z
    head.x, head.y, head.z = head.x0, head.y0 + headdia, head.z0

    setSpineCompParams(model, head,neckdia,necklen)

    return head

def addSpines(model, container,ghkYN):
    headarray=[]
    SpineParams = model.SpineParams
    for comp in moose.wildcardFind(container + '/#[TYPE=Compartment]'):
        if 'soma' not in comp.path:
            numSpines=int(np.round(SpineParams.spineDensity*comp.length))
            spineSpace=comp.length/(numSpines+1)
            for index in range(numSpines):
                frac=(index+0.5)/numSpines
                #print comp.path,"Spine:", index, "located:", frac
                head=makeSpine(model, comp, 'spine',index, frac, SpineParams.necklen, SpineParams.neckdia, SpineParams.headdia)
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
    if param_sim.printinfo:
        print(len(headarray),"spines created in",container)
    return headarray
