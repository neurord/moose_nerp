import moose
import numpy as np

def chirp(gen_name="chirp", amp=1, f0=1, f1=50, T=0.8, start=0.1, end=0.5, simdt=10E-5, phase=0, amp_offset=0):
    ''' Chirp injection stimultus
    '''
    chirper = moose.element('/chirpgen') if moose.exists('/chirpgen') else moose.Neutral('/chirpgen')
    func_1 = moose.Func(chirper.path+'/'+gen_name)
    func_1.mode = 3
    func_1.expr = '{A}*cos(2*pi*(({f1}-{f0})/{T})*x^2 + 2*pi*{f1}*x + {p})+{o}'.format(f0=f0, f1=f1, T=T, A=amp, p=phase, o=amp_offset)
    input = moose.StimulusTable(chirper.path+'/xtab')
    xarr = np.arange(start, end, simdt)
    input.vector = xarr
    input.startTime = 0.0
    input.stepPosition = xarr[0]
    input.stopTime = xarr[-1] - xarr[0]
    moose.connect(input, 'output', func_1, 'xIn')
    moose.useClock(0, '%s/##[TYPE=StimulusTable]' % (chirper.path), 'process')
    moose.useClock(0,'%s/##[TYPE=Func]' % (chirper.path), 'process')
    return func_1

def connect_chirp_to_compartment(chrip_obj, comp_element):
    moose.connect(chirp_obj, 'valueOut', comp_element, 'injectMsg')
