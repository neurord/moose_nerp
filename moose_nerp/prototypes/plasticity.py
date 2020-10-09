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

'''
key expressions for short term plasticity
y_d -> y*d (multiplicative depression) or
y_f -> y+f (additive facilitation)
Meanwhile, decay of depression or facilitation given by:
dy/dt=(ss-y)/tau =  (ss/tau) - y*(1/tau) = A - B*y
A=ss/tau, B=1/tau, A/B= ss
y(t2) = y(t1) * exp(-B*dt) + ss*(1-exp(-B*dt))
where ss is the initial value or the basal weight multiplier in absence of short term plasticity
Final weight = y_d*y_f when both depression and facilitation
'''

def facil_depress(name,stp_params,simdt,presyn,msg):
    #The constants must be defined before setting the expression
    plas=moose.Function(name)
    plas.c['delta']=stp_params.change_per_spike
    plas.c['dt']=simdt 
    plas.c['tau']= np.exp(-simdt/stp_params.change_tau)
    plas.c['equil']=1 
    #x0 is spike time! not a 0 or 1 spike event
    initial_value_expr = '(t<2*dt) ? equil : '
    decay_to_initial_expr='(x0*tau+equil*(1-tau))'
    #NOTE that input from time table is TIME of spike, thus divide by t
    #NOTE that input from time table STAYS at the time of last spike; thus
    #need to test for spike occurence
    if stp_params.change_operator=='*':
        no_change=1
        #if using D -> D*d when spike occurs, d=1 when no spike
    else:
        no_change=0
        #if using D -> D+d when spike occurs, d=0 when no spike
    #This probably won't work if presyn is a spikgen, as time table objects send in the time of their spikes
    #for spikegens, change (x1<=t && x1>t-dt) to x1
    #ideally, if the synhandler can send the spike message, then can use x1 for either timetable or spikegen inputs
    change_per_spike_expr='((x1<=t && x1>t-dt) ? delta : '+str(no_change)+')'
    plas.expr='{} {}{}{}'.format(initial_value_expr, decay_to_initial_expr,stp_params.change_operator,change_per_spike_expr)
    plas.x.num=2
    moose.connect(plas,'valueOut',plas.x[0],'input')
    moose.connect(presyn, msg, plas.x[1], 'input')
    return plas

def ShortTermPlas(synapse,index,stp_params,simdt,presyn,msg):
    #implements short term plasticity - depression and/or facilitation 
    synchan=synapse.parent.parent
    num_inputs=0
    if stp_params.depress is not None:
        dep=facil_depress(synchan.path+NAME_DEPRESS+str(index),stp_params.depress,simdt,presyn,msg)
        log.debug(' ***depress={} {} presyn {}',dep.path, dep.expr,presyn.path)
        num_inputs+=1
        source0=dep
        plas_expr='(init*x0)'
    if stp_params.facil is not None:
        fac=facil_depress(synchan.path+NAME_FACIL+str(index),stp_params.facil,simdt,presyn,msg)
        log.debug(' ***facil={} {} presyn {}',fac.path,fac.expr,presyn.path)
        num_inputs+=1
        if num_inputs==1:
            source0=fac
            plas_expr='(init*x0)'
        else:
            source1=fac
            plas_expr='(init*x0*x1)'
    #
    log.debug('**** STP={} x[0]={} ****',plas_expr,source0.path)
    plaspath=synchan.path+NAME_STP+str(index)
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

def desensitization(synchan,SynParams):
    '''
    Key equations to be implemented
    dep.expression = "x = x*"+str(dep_constant)+"y*"+str(SynParams.dep_per_spike)
    weight.expression = "weight*1/(1+x)/simdt"
    facsynchan uses:  (1+fac)/(1+dep)/simdt
    x above is dep, and we didn't have fac, hence 1/(1+x)
    weight is the current synaptic weight
    '''
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

def plasticity2(synchan,plas_params):
    '''
    Compute calcium-based amplitude and duration plasticity rule using Moose Function objects.

    Plasticity function requires 2 amplitude thresholds and 2 duration thresholds,
    computes weight change, and returns the weight change to the synapse.

    Moose.Functions:
        1. Calcium amplitude threshold detector and duration accumulator
            - Input: calcium concentration from synapse/spine; output form self
            - Constants: LTP amplitude threshold; LTD amplitude threshold
            - Function: - If calcium greater than LTP amplitude threshold, accumulate
                          positive values for duration above threshold.
                        - Else if greater than LTD threshold but less than LTP threshold,
                          accumulate negative values for duration above threshold.
                        - Else, return 0/reset accumulation to zero.
                        - Note that a threshold change (i.e. LTP to LTD) will reset accumulator
            - Output: Send output to plasticity function object.
        2. Duration threshold detector and weight change calculator:
            - Input: Calcium Duration accumulator; calcium concentration; synaptic weight
            - Constants: LTP duration threshold; LTD duration threshold; LTP amplitude threshold;
                         LTD amplitude threshold; LTP gain; LTD gain; min weight; max weight;
                         max change; dt
            - Function: If accumulator input is positive and greater than LTP duration threshold,
                            Output is positive weight change
                        if input is negative and less than (negative) LTD duration threshold,
                            Output is negative weight change
                        Else, weight change output is zero.
    '''
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

    # Allow plasticity function in unconnected synapses to track heterosynaptic plasticity?
    if sh.synapse.num == 0:
        sh.synapse.num +=1
        #print('No synapses on {}, adding a synapse and plasticity function'.format(sh))
        #return
    else:
        pass
        #print('{} synapses on {}, adding plasticity function to existing synapses'.format(sh.synapse.num,sh))


    ###  Plasticity Function

    # First Function object: detect calcium level/duration compared to amplitude thresholds.
    # if calcium meets LTD threshold, accumulate duration above LTD as negative value;
    # if it meets LTP threshold, accumulate duration above LTP as positive value;
    # else return 0

    NAME_DUR = 'CaThreshDurAccumulator'
    durname = synchan.path+'/'+NAME_DUR
    dur=moose.Function(durname)
    dur.tick=1
    # Set expression constants
    dur.c['LTP_amp_thresh'] = 0.46e-3 # TODO: Change to a parameter
    dur.c['LTD_amp_thresh'] = 0.2e-3 # TODO: Change to a parameter
    dur.c['dt'] = dur.dt # TODO: Put simdt variable here
    dur.x.num = 2 # Required?

    # Expression: x0 is calcium input; x1 is input from self
    # Accumulates value by dt (positive for LTP, negative for LTD)
    dur.expr = '( (x0 >= LTP_amp_thresh) && (x1 >= 0) ) * (x1+dt) + ( (x0 >= LTD_amp_thresh && x0 < LTP_amp_thresh) && (x1 <= 0) ) * (x1-dt)'
    # Connect calcium input to variable x0
    moose.connect(cal,CaMSG,dur.x[0],'input')
    # Connect dur value output to variable x1 of itself
    moose.connect(dur,'valueOut',dur.x[1],'input')


    #######################
    #Second Function object: Calculate plasticity. Uses equations from Asia's code/paper
    plasname=synchan.path+'/'+NAME_PLAS
    plas=moose.Function(plasname)
    plas.tick=1
    # Constants:
    plas.c['LTP_dur_thresh'] = 0.002 # TODO: Parameterize
    plas.c['LTD_dur_thresh'] = 0.032 # TODO: Parameterize
    plas.c['LTP_amp_thresh'] = 0.46e-3 # TODO: Parameterize
    plas.c['LTD_amp_thresh'] = 0.2e-3 # TODO: Parameterize
    plas.c['LTP_gain'] = 1100 # TODO: Parameterize
    plas.c['LTD_gain'] = 4500*2 # TODO: Parameterize
    min_weight = 0.0
    max_weight = 2.0
    plas.c['min_weight'] = min_weight
    plas.c['max_weight'] = max_weight
    plas.c['max_change'] = (max_weight - min_weight)/1000.0
    plas.c['dt'] = plas.dt # TODO: Put simdt variable here


    # Expression: x0 is input from duration accumulator; x1 is calcium concentration amplitude
    # Current synaptic weight as input y0

    # Note: due to complexity of expression strings, the final expression is built up
    # from separate expression strings

    # max change: compute change based on level of calcium above threshold, but limit to the max_change value
    max_change_LTP_expr =        'min( ( (x1-LTP_amp_thresh) * (LTP_gain) * dt ), max_change)'
    max_change_LTD_expr = '(-1) * min( ( (x1-LTD_amp_thresh) * (LTD_gain) * dt ), max_change)'

    # Normalize the synaptic weight on a range from min to max weight
    norm_expr_LTP = 'sqrt( 1 - ( (y0 - min_weight)/(max_weight - min_weight) ) )'
    norm_expr_LTD = 'sqrt(     ( (y0 - min_weight)/(max_weight - min_weight) ) )'

    # LTP condition: If x0 input from duration accumulator is above LTP threshold, change weight accordingly:
    # limit the total weight to the max weight parameter
    LTPexpr = '(x0 > LTP_dur_thresh) * min(y0 +  {} * {}, max_weight)'.format(max_change_LTP_expr, norm_expr_LTP)
    ##LTPexpr = '(x0 > LTP_dur_thresh) * 3'# For Testing

    # LTD condition: If x0 input from duration accumulator is above LTD threshold, change weight accordingly:
    # limit the total weight to the min weight parameter
    LTDexpr = '(x0 < (-1*LTD_dur_thresh) ) * max(y0 + {} * {}, min_weight)'.format(max_change_LTD_expr, norm_expr_LTD)
    #LTDexpr = '2 * (x0 < -1*LTD_dur_thresh) + (0 * x1)'#Testing

    # If neither LTP or LTD thresholds are met, don't change weight; maintain current weight (y0 variable)
    nochange_expr = '(y0) * ( (x0 > -LTD_dur_thresh) && (x0 < LTP_dur_thresh) )'
    #nochange_expr = '(5) * ( (x0 > -LTD_dur_thresh) && (x0 < LTP_dur_thresh) )'#Testing

    # Annoyingly, have to force first 2 timesteps to initial synaptic weight value of 1 so
    # moose.reinit doesn't cause the output of plas expression to force synaptic weight
    # to go to zero (Since synaptic weight is both an input to the expression and its output).
    # Note: recent github commit to Moose may fix this; it adds Function variable "doEvalAtReinit".
    # But I have't updated to it yet so haven't tried testing it.
    # Expression is an if-then-else statemet with syntax ((condition) ? (Value if True) : (Value if False))
    initial_value_expr = '(t<2*dt) ? (1) : '

    # Put the expression all together:
    plas.expr = '{} ({} + {} + {})'.format(initial_value_expr, LTPexpr, LTDexpr, nochange_expr)

    # Connect Duration accumululator output to variable x0
    moose.connect(dur,'valueOut',plas.x[0],'input')
    # Connect calcium amplitude to variable x1
    moose.connect(cal,CaMSG,plas.x[1],'input')
    # Get the current synaptic weight of the synapse as variable y0
    moose.connect(plas,'requestOut',sh.synapse[0],'getWeight')

    # Output the updated weight computed by plasticity function to each synapse
    for synapse in range(sh.synapse.num):
        #sh.synapse.num+=1
        log.debug("{} {} {}", synchan.path, sh.synapse[synapse], cal.path)
        moose.connect(plas,'valueOut',sh.synapse[synapse],'setWeight')

    ################################################################################

    return {'plas':plas, 'syn': synchan}


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

    expression = highfac+"*(y>x)*(y-x)+(y>z)*(x>y)*(y-z)*(x-y)*"+lowfac

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
                plascum[cell][synname] = plasticity2(synchan, caplas_params.Plas_syn)

    return plascum
