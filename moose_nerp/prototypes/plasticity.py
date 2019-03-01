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
NAME_DEPRESS='/dep'
NAME_FACIL='/fac'
NAME_STP='/stp'

def facil_depress(name,stp_params,simdt,presyn,msg):
    #The constants must be defined before setting the expression
    plas=moose.Function(name)
    plas.c['f']=stp_params.change_per_spike
    plas.c['dt']=simdt # TODO: Put simdt variable here
    plas.c['tau']= np.exp(-simdt/stp_params.change_tau)
    plas.c['equil']=1
    #x0 is spike time!  not a 0 or 1 spike event
    initial_value_expr = '(t<2*dt) ? (equil) : '
    decay_to_initial_expr='x0+(equil-x0)*tau'
    #NOTE that input from time table is TIME of spike, thus divide by t
    change_per_spike_expr='f'+stp_params.change_operator+'x1/t'
    plas.expr='{} ({}+{})'.format(initial_value_expr, decay_to_initial_expr,change_per_spike_expr)
    plas.x.num=2
    moose.connect(plas,'valueOut',plas.x[0],'input')
    moose.connect(presyn, msg, plas.x[1], 'input')
    return plas

def ShortTermPlas(synapse,index,stp_params,simdt,presyn,msg):
    synchan=synapse.parent.parent
    num_inputs=0
    if stp_params.depress is not None:
        dep=facil_depress(synchan.path+NAME_DEPRESS+str(index),stp_params.depress,simdt,presyn,msg)
        print('depress=',dep.path, end='')
        num_inputs+=1
        source0=dep
        plas_expr='(init*x0)'
    if stp_params.facil is not None:
        fac=facil_depress(synchan.path+NAME_FACIL+str(index),stp_params.facil,simdt,presyn,msg)
        print(' facil=',fac.path,end='')
        num_inputs+=1
        if num_inputs==1:
            source0=fac
            plas_expr='(init*x0)'
        else:
            source1=fac
            plas_expr='(init*x0*x1)'
    #
    print(' STP=',plas_expr,'x[0]=',source0.path)
    plaspath=synchan.path+NAME_STP
    plas_func=moose.Function(plaspath)
    plas_func.c['init']=synapse.weight
    plas_func.c['dt']=simdt
    plas_func.expr='(t<2*dt) ? (init) :'+plas_expr
    plas_func.x.num=num_inputs
    moose.connect(source0,'valueOut', plas_func.x[0],'input')
    if num_inputs==2:
        moose.connect(source1,'valueOut', plas_func.x[1],'input')
    # Output the updated weight computed by plasticity function to the synapse
    moose.connect(plas_func,'valueOut',synapse,'setWeight')

    return
'''
#specify presyn as tt explicitly and test.  If doesn't work, re-peat outside of cuntion
simdt =  model.param_sim.simdt
synchan=moose.element('/squid[0]/axon[0]/ampa')
sh=moose.element(synchan.path+'/SH')
sh.numSynapses=1
tt=moose.TimeTable('tt')
tt.vector=[simdt,0.001,0.01]
moose.connect(tt,'eventOut', sh.synapse[0], 'addSpike')
sh.synapse[0].weight=1
stp_params=model.param_syn.short_term_plas_params['gaba']
from moose_nerp.prototypes import plasticity
plasticity.ShortTermPlas(sh.synapse[0],stp_params,simdt,tt)
for ii in range(32):
    moose.setClock(ii, simdt)

#evaluate result:
facil_tab = moose.Table('/faciltab')
facil=moose.element(synchan.path+'/fac')
moose.connect(facil_tab, 'requestOut', facil, 'getValue')
plas_tab = moose.Table('/plastab')
plas=moose.element(synchan.path+'/stp')
moose.connect(plas_tab, 'requestOut', plas, 'getValue')

moose.reinit()
moose.start(0.0001)
from matplotlib import pyplot as plt
plt.ion()
time=np.arange(0,simdt*len(facil_tab.vector),simdt)
plt.plot(time,facil_tab.vector,label='facil')
plt.plot(time,plas_tab.vector,label='plas')
plt.legend()
'''
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
    
    #x*exp(dt/tau)+y*dep_per_spike, where x is output of self!
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
