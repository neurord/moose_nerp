import moose


def MakeGenerators(container,Stimulation):
    
    StimParams = Stimulation.Paradigm
    pulse0 = moose.PulseGen(container+'/pulse0')
    pulse0.level[0] = StimParams.inject
    pulse0.width[0] = StimParams.width_AP
    pulse0.delay[0] = 0
    pulse0.delay[1] = StimParams.AP_interval
    pulse0.baseLevel = StimParams.0
    pulse0.trigMode = 2

    burst_gate = moose.PulseGen(container+'/burst_gate')
    burst_gate.level[0] = StimParams.inject
    burst_gate.delay[0] = 0
    burst_gate.delay[1] = 1./StimParams.f_burst
    burst_gate.width[0] = StimParams.n_AP*StimParams.AP_interval
    burst_gate.baseLevel = 0
    burst_gate.trigMode = 2

    moose.connect(burst_gate,'output',pulse0,'input')

    train_gate = moose.PulseGen(container+'/train_gate')
    train_gate.level[0] = StimParams.inject
    train_gate.delay[0] = 0
    train_gate.delay[1] = 1./StimParams.f_train
    train_gate.width[0] = StimParams.n_burst/StimParams.f_burst
    train_gate.baseLevel = 0
    train_gate.trigMode = 2

    moose.connect(train_gate,'output',burst_gate,'input')
    
    experiment_gate = moose.PulseGen(container+'/experiment_gate')
    experiment_gate.level[0] = StimParams.inject
    experiment_gate.delay[0] = Stimulation.stim_delay+StimParams.ISI
    experiment_gate.delay[1] = 1e9
    experiment_gate.width[0] = StimParams.n_train/StimParams.f_train
    experiment_gate.baseLevel = 0
    experiment_gate.trigMode = 0

    moose.connect(experiment_gate,'output',train_gate,'input')

    return [pulse0,burst_gate,train_gate,experiment_gate]

def loop_through_spines(spines,time_tables,delay,StimParams):
    for spine in spines:
        if spine not in time_tables:
            time_tables[spine] = []
            
        time_tables[spine].append(delay+i*1./StimParams.f_train+j*1./StimParams.f_burst+k*1./StimParams.f_pulse)

def MakeTimeTables(Stimulation,spine_no):

    StimParams = Stimulation.Paradigm
       
    if not StimParams.PreStim:
        return

    AP_delay = Stimulation.stim_delay+StimParams.ISI
    delay = Stimulation.stim_delay
    
    time_tables = {}
    if Stimulation.which_spines in ['all','ALL','All']:
        how_many  = round(Stimulation.spine_density*spine_no)
    elif Stimulation.which_spines:
        how_many  = round(Stimulation.spine_density*len(Stimulation.which_spines))
    for i in range(StimParams.n_trains):
        for j in range(StimParams.n_bursts):
            for k in range(StimParam.n_pulses):
                if Stimulation.spine_sequence:
                    spines = Stimulation.spine_sequence[k]
                    loop_through_spines(spines,time_tables,delay,StimParams)

                elif Stimulation.which_spines in ['all','ALL','All']:
                    spines = []
                    how_man_spines = 0
                    while True:
                        spine = randint(0,spine_no-1)
                        if spine not in spines:
                            spines.append(spine)
                            how_many_spines += 1
                            if how_many_spines == how_many:
                                break
                    
                    loop_through_spines(spines,time_tables,delay,StimParams)
                        
                elif  Stimulation.which_spines:
                    spines = []
                    how_man_spines = 0
                    while True:
                        r = randint(0,len(Stimulation.which_spines)-1)
                        spine = Stimulation.which_spines[r]
                        if spine not in spines:
                            spines.append(spine)
                            how_many_spines += 1
                            if how_many_spines == how_many:
                                break
                        
                    loop_through_spines(spines,time_tables,delay,StimParams)
                    
        return timetables
    
def StimulationHookUp(model):

    pass
