"""\
Make a plasticity device in that compartment/synapse
"""
from __future__ import print_function, division
import os
import re
import moose

from spspine import logutil, util, spines

log = logutil.Logger()
NAME_PLAS='/plas'
NAME_CUM='Cum'

def plasticity(synchan,synapse_params):

    
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
    
    highfac = synapse_params.highFactor
    lowfac = synapse_params.lowFactor

    expression = highfac+"(y>x)*(y-x)+(y>z)*(x>y)*(y-z)*(x-y)"+lowfac

    plas.expr = expression
    
    #Must define plasticity expression first, else these next assignments do nothing

    plas.x = synapse_params.highThreshold
    plas.z = synapse_params.lowThreshold
    #SECOND: accumulate all the changes, as percent increase or decrease
    plasCum = moose.Func(plasname+NAME_CUM)
    #need input from the plasticity thresholding function to y 
    moose.connect(plas,'valueOut',plasCum,'xIn')
    moose.connect(plasCum,'valueOut',plasCum, 'yIn')
    plasCum.expr = "(x+1.0)*y*z"
    plasCum.z = sh.synapse[0].weight
    plasCum.y = 1.0
    moose.connect(plasCum,'valueOut',sh.synapse[0],'setWeight')
    
    return {'cum':plasCum,'plas':plas, 'syn': synchan}

def addPlasticity(cell_pop,caplas_params):
    log.info("{} ", cell_pop)
    plascum={}
    
    for cell in cell_pop:
        
        plascum[cell] = {}
        allsyncomp_list = moose.wildcardFind(cell+'/##/'+caplas_params.Synapse.Name+'[ISA=SynChan]')

        for synchan in allsyncomp_list:
            #if synapse exists
            if moose.exists(synchan.path+'/SH'):
                log.debug("{} {} {}", cell, synchan.path, moose.element(synchan.path+'/SH'))
                synname = util.syn_name(synchan.path, spines.NAME_HEAD)
                plascum[cell][synname] = plasticity(synchan, caplas_params.Synapse)
    return plascum
