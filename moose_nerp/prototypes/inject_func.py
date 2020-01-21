#Eventually, update this for trains and bursts from Sriram's genesis functions

from __future__ import print_function, division
import numpy as np
import moose
import random
from moose_nerp.prototypes.util import NamedList
from moose_nerp.prototypes.util import NamedDict
from moose_nerp.prototypes import connect, plasticity, util, spines


ParadigmParams = NamedList('ParadigmParams','''
f_pulse
n_pulse
A_inject
f_burst
n_burst
f_train
n_train
width_AP
AP_interval
n_AP
ISI
name''')


'''
which_spines -- which spines get stimulated.
If 'all' -- spines are randomly chosen with a probability of spine_density
if a sequencea list -- stimulated spines are randomly chosen from the list
stim_delay -- delay of the stimulation onset
pulse_sequence -- which spine gets which pulses
syntype specifies type of synchan, e.g. gaba or AMPA, if not stimulating spines
'''

StimLocParams = NamedList('PresynapticLocation','''
which_spines
spine_density
pulse_sequence
stim_dendrites
syntype=None
weight=None
''')

StimParams = NamedList('PresynapticStimulation','''
Paradigm
StimLoc
stim_delay''')


def MakeGenerators(container,Stimulation):

    StimParams = Stimulation.Paradigm

    pulse0 = moose.PulseGen(container.path+'/pulse')
    pulse0.level[0] = StimParams.A_inject
    pulse0.width[0] = StimParams.width_AP
    pulse0.delay[0] = 0
    pulse0.delay[1] = StimParams.AP_interval
    pulse0.baseLevel = 0
    pulse0.trigMode = 2

    burst_gate = moose.PulseGen(container.path+'/burst_gate')
    burst_gate.level[0] = 1
    burst_gate.delay[0] = 0
    burst_gate.delay[1] = 1./StimParams.f_burst
    burst_gate.width[0] = StimParams.n_AP*StimParams.AP_interval
    burst_gate.baseLevel = 0
    burst_gate.trigMode = 2

    moose.connect(burst_gate,'output',pulse0,'input')

    train_gate = moose.PulseGen(container.path+'/train_gate')
    train_gate.level[0] = 1
    train_gate.delay[0] = 0
    train_gate.delay[1] = 1./StimParams.f_train
    train_gate.width[0] = StimParams.n_burst/StimParams.f_burst
    train_gate.baseLevel = 0
    train_gate.trigMode = 2

    moose.connect(train_gate,'output',burst_gate,'input')

    experiment_gate = moose.PulseGen(container.path+'/experiment_gate')
    experiment_gate.level[0] = 1
    experiment_gate.delay[0] = Stimulation.stim_delay+StimParams.ISI
    experiment_gate.delay[1] = 1e9
    experiment_gate.width[0] = StimParams.n_train/StimParams.f_train
    experiment_gate.baseLevel = 0
    experiment_gate.trigMode = 0

    moose.connect(experiment_gate,'output',train_gate,'input')

# data = moose.Neutral('/data')
    # pulse0_tab = moose.Table('/data/pulse0_tab')
    # burst_gate_tab = moose.Table('/data/burst_gate_tab')
    # train_gate_tab = moose.Table('/data/train_gate_tab')
    # experiment_gate_tab = moose.Table('/data/experiment_gate_tab')

    # moose.connect(pulse0_tab,'requestOut',pulse0,'getOutputValue')
    # moose.connect(burst_gate_tab,'requestOut',burst_gate,'getOutputValue')
    # moose.connect(train_gate_tab,'requestOut',train_gate,'getOutputValue')
    # moose.connect(experiment_gate_tab,'requestOut',experiment_gate,'getOutputValue')

    return [pulse0,burst_gate,train_gate,experiment_gate]

def loop_through_spines(i,j,k,my_spines,time_tables,delay,StimParams):
    
    for spine in my_spines:
        if spine not in time_tables:
            time_tables[spine] = []
        time_tables[spine].append(delay+i*1./StimParams.f_train+j*1./StimParams.f_burst+k*1./StimParams.f_pulse)

def MakeTimeTables(Stimulation,spine_no):

    StimParams = Stimulation.Paradigm
    delay = Stimulation.stim_delay
    location=Stimulation.StimLoc
    print('maketimetab location',location)

    time_tables = {}
    if location.spine_density==0.0:
        how_many=spine_no
    else:
        if location.which_spines in ['all','ALL','All']:
            how_many  = round(location.spine_density*spine_no)
        elif location.which_spines:
            how_many  = round(location.spine_density*len(location.which_spines))

    for i in range(StimParams.n_train):
        for j in range(StimParams.n_burst):
            for k in range(StimParams.n_pulse):
                if location.spine_density==0:
                    my_spines=location.stim_dendrites
                elif location.pulse_sequence:
                    my_spines = location.pulse_sequence[k]

                #The next two elif blocks need work.  Eliminate infinite loop, combine into one block since mostly similar
                elif location.which_spines in ['all','ALL','All']:
                    my_spines = []
                    how_many_spines = 0
                    while True:
                        spine = random.randint(0,spine_no-1)
                        if spine not in my_spines:
                            my_spines.append(spine)
                            how_many_spines += 1
                            if how_many_spines == how_many:
                                break

                elif  location.which_spines:
                    my_spines = []
                    how_many_spines = 0
                    while True:
                        r = random.randint(0,len(location.which_spines)-1)
                        spine = location.which_spines[r]
                        if spine not in my_spines:
                            my_spines.append(spine)
                            how_many_spines += 1
                            if how_many_spines == how_many:
                                break
                #ANOTHER ISSUE: This will create identical time_tables for each spine, instead of hooking up same tt to multiples
                loop_through_spines(i,j,k,my_spines,time_tables,delay,StimParams)

    return time_tables

def enumerate_spine_synchans(model,dendrite):
    #for dend in model.Stimulation.StimParams.which_dendrites:
    my_spines = list(set(moose.element(dendrite).neighbors['handleAxial']).intersection(set(moose.element(dendrite).children)))
    num_spines = len(my_spines)

    if not num_spines:
        return

    synapses = {}
    for spine in my_spines:
        spine_no = int(''.join(c for c in spine.name if c.isdigit()))
        synapses[spine_no] = []
        heads = moose.element(spine).neighbors['handleAxial']
        for head in heads:
            moose_head = moose.element(head)
            for child in moose_head.children:
                moose_child = moose.element(child)
                if moose_child.className == 'SynChan' or moose_child.className == 'NMDAChan':
                    synapses[spine_no].append(moose_child)

    return num_spines,synapses    

def HookUpDend(model,dendrites,container,dendpath):
    if model.Stimulation.StimLoc.spine_density>0:
        num_spines,synchans=enumerate_spine_synchans(model,dendrites)
        tt_root_name=container.path+'/TimTab'+dendrite.name
    else:
        num_spines=1
        synchans={dend:[dendpath+dend+'/'+model.Stimulation.StimLoc.syntype] for dend in dendrites}
        tt_root_name=container.path+'/TimTab'
        print('HookUpDend, syn:', synchans,num_spines)
    if getattr(model.Stimulation.StimLoc,'weight',None):
        weight=model.Stimulation.StimLoc.weight
    else:
        weight=1
    time_tables = MakeTimeTables(model.Stimulation,num_spines)
    freq=model.Stimulation.Paradigm.f_pulse
    print('HookUpDend, tt:', time_tables)
    stimtab = {}
    stim_syn = {}
    for spine in time_tables.keys():
        stimtab[spine] = moose.TimeTable('%s_%s_%s' % (tt_root_name,str(spine),str(int(freq))))
        stimtab[spine].vector = np.array(time_tables[spine])
        stimtab[spine].tick=7#moose.element(synchans[spine][0]).tick
        print('HUD, stimtab {} tick {} synchans {}'.format(stimtab,stimtab[spine].tick,synchans[spine]))

        for synchan in synchans[spine]:  #if neuron has spines, is this syntax needed?
              synapse = moose.element(synchan+'/SH')
              print('**** ready to connect',synapse.path,stimtab[spine].vector,model.Stimulation.Paradigm.name,'weight=',weight)
              connect.synconn(synapse.path,0,stimtab[spine],model.param_syn,weight=weight)
              stim_syn[synchan]=(stimtab[spine],synapse,synapse.synapse.num-1)
            
    return stimtab,synchans,stim_syn

def ConnectPreSynapticPostSynapticStimulation(model,ntype):
    container_name = '/input'
    container = moose.Neutral(container_name)
    SP = model.Stimulation.Paradigm
    print ('CPSPSS:Stim Paradigm', SP)
    exp_duration = (SP.n_train-1)/SP.f_train+(SP.n_burst-1)/SP.f_burst+(SP.n_pulse-1)/SP.f_pulse+SP.n_AP*SP.AP_interval+2*\
                   model.Stimulation.stim_delay

    if SP.A_inject:
        pg = MakeGenerators(container,model.Stimulation)
        injectcomp = '/'+ntype+'/'+model.param_cond.NAME_SOMA
        moose.connect(pg[0], 'output', injectcomp, 'injectMsg')

    stimtabs = {};stim_syn_set={};#synchans={}
    #ISSUE WITH THIS LOOP: potentially creating independent but identical timetables for multiple dendrites
    if SP.n_train*SP.n_burst*SP.n_pulse>0:
        print('CPSPSS: dends',model.Stimulation.StimLoc.stim_dendrites)
        dendpath='/'+ntype+'/'
        stimtab,synchan,stim_syn = HookUpDend(model,model.Stimulation.StimLoc.stim_dendrites,container,dendpath)
        max_time=[np.max(st.vector) for st in stimtab.values()]
        exp_dur= np.max(max_time)+model.Stimulation.stim_delay
        print('EXP DUR',max_time,'max time:',exp_dur,'AP',exp_duration)
        exp_duration=(exp_dur if exp_dur>exp_duration else exp_duration)
        stimtabs.update(stimtab)
        stim_syn_set.update(stim_syn)

    if SP.A_inject:
        return exp_duration,stimtabs,stim_syn_set, pg
    else:
        return exp_duration,stimtabs, stim_syn_set, None

#Possibly replace this with MakeGenerators
def setupinj(model, delay,width,neuron_pop):
    """Setup injections

    Note that the actual injected current is proportional to dt of the clock
    So, you need to use the same dt for stimulation as for the model
    Strangely, the pulse gen in compartment_net refers to  firstdelay, etc.
    """
    pg = moose.PulseGen('pulse')
    pg.firstDelay = delay
    pg.firstWidth = width
    pg.secondDelay = 1e9
    for ntype in neuron_pop.keys():
        for num, name in enumerate(neuron_pop[ntype]):
            injectcomp=moose.element(name +'/'+model.param_cond.NAME_SOMA)
            print("INJECT:", name, injectcomp.path)
            moose.connect(pg, 'output', injectcomp, 'injectMsg')
    return pg

def inject_pop(population, num_inject):
    #select subset of neurons for injection
    choice_neurs={}
    for neurtype in population.keys():
        max_inject=min(num_inject,len(population[neurtype]))
        if max_inject>0:
            choice_neurs[neurtype]=list(np.random.choice(population[neurtype],max_inject,replace=False))
    return choice_neurs

def setup_stim(model,param_sim,neuron_paths):
    if model.param_stim.Stimulation.Paradigm.name is not 'inject':
        ### plasticity paradigms combining synaptic stimulation with optional current injection
        sim_time = []
        tt={ntype:[] for ntype in neuron_paths.keys()}
        stim_syn_set={ntype:[] for ntype in neuron_paths.keys()}
        pg=[]
        for ntype in neuron_paths.keys():
            #update how ConnectPreSynapticPostSynapticStimulation deals with param_stim
            dur,tt[ntype],stim_syn_set[ntype],pg = ConnectPreSynapticPostSynapticStimulation(model,ntype)
            sim_time.append( dur)
        model.tt,model.tuples=tt, stim_syn_set
        param_sim.simtime = max(sim_time)# + model.param_stim.Stimulation.stim_delay
        print('setup_stim, simtime={}'.format(param_sim.simtime))
        #param_sim.injection_current = [0]
    else:
        ### Current Injection alone, either use values from Paradigm or from command-line options
        #Dan: param_sim should update param_stim.Stimulation? only param_sim.injection_current should be used?
        #test for existence, not len of injection_current to determine over-writing?
        if not len(param_sim.injection_current):
            param_sim.injection_current = [model.param_stim.Stimulation.Paradigm.A_inject]
            param_sim.injection_delay = model.param_stim.Stimulation.stim_delay
            param_sim.injection_width = model.param_stim.Stimulation.Paradigm.width_AP
        pg=setupinj(model, param_sim.injection_delay, param_sim.injection_width,neuron_paths)
    return pg,param_sim

###Voltage Clamp (incomplete)
def Vclam(delay,width,delay_2,r,c,gain,sat,gain_p,tau_1,tau_2,psat):
    pulseg=moose.PulseGen('pulse')
    pulseg.firstDelay=delay
    pulseg.firstWidth=width
    pulseg.secondDelay=delay_2
    lp=moose.RC('lowpass')
    lp.R=r
    lp.C=c
    DA=moose.DiffAmp('diffamp')
    DA.gain=gain
    DA.saturation=sat
    pid=moose.PIDController('PID')
    pid.gain=gain_p
    pid.tauI=tau_1
    pid.tauD=tau_2
    pid.saturation=psat
    comp=moose.element("/proto")
    moose.connect(pulseg,"output",lp,"injectIn")
    moose.connect(lp, "output", DA, "plusIn")
    moose.connect(DA,"output",pid,"commandIn")
    moose.connect(comp, "VmOut",pid, "sensedIn")
    moose.connect(pid,"output",comp,"injectMsg")
    tab=moose.Table("/data/Im")
    moose.connect(tab,"requestOut",comp,"getIm")
    return tab

