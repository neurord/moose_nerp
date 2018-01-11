"""\
Make a plasticity device in that compartment/synapse
"""
from __future__ import print_function, division
import os
import re
import moose
import numpy as np

from moose_nerp.prototypes import logutil, util, spines

log = logutil.Logger()
NAME_PLAS='/plas'
NAME_CUM='Cum'

def desensitization(synchan,SynParams):
    sh = moose.element(synchan).children[0]
    
    deppath = synchan.path +'/dep'
    weightpath = synchan.path +'/weight'
    dep = moose.Func(deppath)
    weight = moose.Func(weightpath)
    help_dep = moose.Func(deppath+"/help")

    activation = moose.Func(deppath+"/activation")
    activation_help = moose.Func(deppath+"/activation/help")

    y = moose.Func(deppath+"/y")
    condition = moose.Func(deppath+"/condition")
    
    help_dep.tick = synchan.tick
    dep.tick = synchan.tick
    weight.tick = synchan.tick
    activation.tick = synchan.tick
    activation_help.tick = synchan.tick
    y.tick = synchan.tick
    condition.tick = synchan.tick
    
    
    dep_const = np.exp(-synchan.dt/SynParams.dep_tau)
    dep.expr = "x*"+str(dep_const)+"+y*"+str(SynParams.dep_per_spike)
    help_dep.expr = "x"
    weight.expr = "z*(1./(1+x))/"+str(synchan.dt)
    activation.expr = "x+y"
    activation_help.expr = "x"
    y.expr = "x"
    condition.expr = "x&&(x==y)"
    
    moose.connect(dep,"valueOut",weight,"xIn")
    moose.connect(condition,'valueOut',dep,'yIn')
    moose.connect(condition,'valueOut',weight,'zIn')
    moose.connect(condition,'valueOut',activation,'zIn')
    moose.connect(sh,'activationOut',activation,'yIn')
    moose.connect(sh,'activationOut',y,'xIn')
    
    moose.connect(activation,"valueOut",condition,"xIn")
    moose.connect(y,"valueOut",condition,"yIn")
    moose.connect(condition,"valueOut",y,"zIn")
    moose.connect(activation, "valueOut",activation_help,"xIn")
    moose.connect(activation_help,"valueOut",activation,"xIn")
    moose.connect(dep,'valueOut',help_dep,'xIn')
    moose.connect(help_dep,'valueOut',dep,'xIn')
    
    moose.connect(weight,"valueOut",synchan,'activation')
    moose.showmsg(synchan)
    return condition, activation

def plasticity(synchan,plas_params):

    
    comp = synchan.parent
    for child in comp.children:
        if child.className == 'CaConc' or child.className == 'ZombieCaConc':
            cal = child
            CaMSG = 'concOut'
            break
        elif child.className == 'DifShell':
            cal = child
            CaMSG = 'concentrationOut'
            break
    else:
        print('Could not find calcium objects')
        return
    

    shname = synchan.path+'/SH'
    sh = moose.element(shname)
    log.debug("{} {} {}", synchan.path, sh.synapse[0], cal.path)

    plasname=comp.path+'/'+NAME_PLAS
    plas=moose.Func(plasname)

    #FIRST: calculate the amount of plasticity
    #y is input plasticity trigger (e.g. Vm or Ca) 
    moose.connect(cal,CaMSG,plas,'yIn')
    
    #x is the high threshold, z is the low threshold
    #This gives parabolic shape to plasticity between the low and high threshold
    #highfac and lowfac scale the weight change (set in SynParams.py)
    
    highfac = plas_params.highFactor
    lowfac = plas_params.lowFactor

    expression = highfac*"(y>x)*(y-x)+(y>z)*(x>y)*(y-z)*(x-y)"*lowfac

    plas.expr = expression
    
    #Must define plasticity expression first, else these next assignments do nothing

    plas.x = plas_params.highThreshold
    plas.z = plas_params.lowThreshold
    #SECOND: accumulate all the changes, as percent increase or decrease
    plasCum = moose.Func(plasname+NAME_CUM)
    #need input from the plasticity thresholding function to y 
    moose.connect(plas,'valueOut',plasCum,'xIn')
    moose.connect(plasCum,'valueOut',plasCum, 'yIn')
    plasCum.expr = "x+y*z"
    plasCum.z = sh.synapse[0].weight
    plasCum.y = 1.0
    moose.connect(plasCum,'valueOut',sh.synapse[0],'setWeight')
    
    return {'cum':plasCum,'plas':plas, 'syn': synchan}

def addPlasticity(cell_pop,caplas_params):
    log.info("{} ", cell_pop)
    plascum={}
    
    for cell in cell_pop:
        
        plascum[cell] = {}
        allsyncomp_list = moose.wildcardFind(cell+'/##/'+caplas_params.Plas_syn.Name+'[ISA=SynChan]')

        for synchan in allsyncomp_list:
            #if synapse exists
            if moose.exists(synchan.path+'/SH'):
                log.debug("{} {} {}", cell, synchan.path, moose.element(synchan.path+'/SH'))
                synname = util.syn_name(synchan.path, spines.NAME_HEAD)
                plascum[cell][synname] = plasticity(synchan, caplas_params.Plas_syn)
  
    return plascum
