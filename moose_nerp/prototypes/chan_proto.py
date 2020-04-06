"""\
Create general Channel Proto, pass in name, x and y power, and params

Also, create the library of channels
chan_proto requires alpha and beta params for both activation and inactivation
If channel does not have inactivation, just send in empty Yparam array.
"""

from __future__ import print_function, division
import moose
import numpy as np
import logging

from moose_nerp.prototypes import constants, logutil
from moose_nerp.prototypes.util import NamedList
log = logutil.Logger()

StandardMooseTauInfChannelParams = NamedList('StandardMooseTauInfChannelParams', '''
                                T_rate
                                T_B
                                T_C
                                T_vhalf
                                T_vslope
                                SS_rate
                                SS_B
                                SS_C
                                SS_vhalf
                                SS_vslope''')

TauInfMinChannelParams = NamedList('TauInfMinChannelParams', '''
                                T_min
                                T_vdep
                                T_vhalf
                                T_vslope
                                SS_min
                                SS_vdep
                                SS_vhalf
                                SS_vslope
                                T_power=1''')


AlphaBetaChannelParams = NamedList('AlphaBetaChannelParams', '''
                                A_rate
                                A_B
                                A_C
                                A_vhalf
                                A_vslope
                                B_rate
                                B_B
                                B_C
                                B_vhalf
                                B_vslope''')

ZChannelParams = NamedList('ZChannelParams', 'Kd power tau taumax=0 tau_power=0 cahalf=0')
BKChannelParams=NamedList('BKChannelParams', 'alphabeta K delta')


ChannelSettings = NamedList('ChannelSettings', 'Xpow Ypow Zpow Erev name')

def sigmoid(x,xmin,xmax,xvhalf,xslope):
    return xmin+xmax/(1+np.exp((x-xvhalf)/xslope))
#notice the x-xvhalf in sigmoid, but x+xvhalf used by MOOSE
def quadratic(x,xmin,xmax,xvhalf,xslope):
    tau1 = xmax/(1+np.exp((x-xvhalf)/xslope))
    tau2 = 1/(1+np.exp((x-xvhalf)/-xslope))
    tau_x = xmin+tau1*tau2
    return tau_x

def make_sigmoid_gate(model,params,Gate):
    v = np.linspace(model.VMIN, model.VMAX, model.VDIVS)
    if params.T_power==2:
        print('making quadratic gate', Gate.path)
        tau = quadratic(v,params.T_min,params.T_vdep,params.T_vhalf,params.T_vslope)
    else:
        tau = sigmoid(v,params.T_min,params.T_vdep,params.T_vhalf,params.T_vslope)
    minf = sigmoid(v,params.SS_min,params.SS_vdep,params.SS_vhalf,params.SS_vslope)
    Gate.min = model.VMIN
    Gate.max = model.VMAX
    Gate.divs = model.VDIVS
    Gate.tableA = minf/tau
    Gate.tableB = 1/tau

def interpolate_values_in_table(model, tabA, V_0, l=40):
    '''This function interpolates values in the table
    around tabA[V_0]. '''
    V = np.linspace(model.VMIN, model.VMAX, len(tabA))
    idx =  abs(V-V_0).argmin()
    min_idx=max(idx-l,0)
    max_idx=min(idx+l,len(tabA)-1)
    #print('in interp, len of tabA',len(tabA),'V0',V_0,'idx',idx,'+l',idx+l,'min',min_idx,'max',max_idx)
    A_min = tabA[min_idx]
    V_min = V[min_idx]
    A_max = tabA[max_idx]
    V_max = V[max_idx]
    a = (A_max-A_min)/(V_max-V_min)
    b = A_max - a*V_max
    tabA[min_idx:max_idx] = V[min_idx:max_idx]*a+b
    return tabA

def  calc_V0(rate,B,C,vhalf,vslope,Params):
        delta = rate - B * vhalf
        if delta > 1e-10 or delta < -1e-10:
            log.warning("Fixing Singularities. Please verify constraint on Beta: A = B * vhalf {}", Params)
            rate= B * vhalf
        V_0 = vslope*np.log(-C)-vhalf
        return rate,V_0

def fix_singularities(model, Params, Gate):
    #This needs to be extended to work with standardMooseTauInfparams
    if Params.A_C < 0:
        #print('fix_sing for',Params,'len of table',len(Gate.tableA))
        Params.A_rate,V_0=calc_V0(Params.A_rate,Params.A_B,Params.A_C,Params.A_vhalf,Params.A_vslope, Params)
        if model.VMIN < V_0 < model.VMAX:
            #change values in tableA and tableB, because tableB contains sum of alpha and beta
            Gate.tableA = interpolate_values_in_table(model, Gate.tableA, V_0)
            Gate.tableB = interpolate_values_in_table(model, Gate.tableB, V_0)

    if Params.B_C < 0:
        Params.B_rate,V_0=calc_V0(Params.B_rate,Params.B_B,Params.B_C,Params.B_vhalf,Params.B_vslope, Params)
        if model.VMIN < V_0 < model.VMAX:
            #change values in tableB (alpha is stored in tableA)
            Gate.tableB = interpolate_values_in_table(model, Gate.tableB, V_0)

def make_gate(params,model,gate):
    if isinstance(params,AlphaBetaChannelParams):
        gate.setupAlpha(params + [model.VDIVS, model.VMIN, model.VMAX])
        fix_singularities(model, params, gate)
    elif isinstance(params,StandardMooseTauInfChannelParams):
        gate.setupTau(params + [model.VDIVS, model.VMIN, model.VMAX])
        fix_singularities(model, params, gate)
    elif isinstance(params,TauInfMinChannelParams):
        make_sigmoid_gate(model,params,gate)

def chan_proto(model, chanpath, params):
    log.info("{}: {}", chanpath, params)
    chan = moose.HHChannel(chanpath)

    chan.Xpower = params.channel.Xpow
    if params.channel.Xpow > 0:
        xGate = moose.HHGate(chan.path + '/gateX')
        make_gate(params.X,model,xGate)

    chan.Ypower = params.channel.Ypow
    if params.channel.Ypow > 0:
        yGate = moose.HHGate(chan.path + '/gateY')
        make_gate(params.Y,model,yGate)

    if params.channel.Zpow > 0:
        chan.Zpower = params.channel.Zpow
        zGate = moose.HHGate(chan.path + '/gateZ')
        if params.Z.__class__==ZChannelParams:
            #
            ca_array = np.linspace(model.CAMIN, model.CAMAX, model.CADIVS)
            zGate.min = model.CAMIN
            zGate.max = model.CAMAX
            caterm = (ca_array/params.Z.Kd) ** params.Z.power
            inf_z = caterm / (1 + caterm)
            if params.Z.taumax>0:
                tauterm=(ca_array/params.Z.cahalf)**params.Z.tau_power
                taumax_z=(params.Z.taumax-params.Z.tau)/(1+tauterm)
                taumin_z= params.Z.tau * np.ones(len(ca_array))
                tau_z = taumin_z+taumax_z
            else:
                tau_z = params.Z.tau * np.ones(len(ca_array))
            #
            zGate.tableA = inf_z / tau_z
            zGate.tableB = 1 / tau_z
            chan.useConcentration = True
        else:
            chan.useConcentration = False
            make_gate(params.Z,model,zGate)

    chan.Ek = params.channel.Erev
    chan.tick=-1
    return chan

def BKchan_proto(model, chanpath, params):
    ZFbyRT= 2 * constants.Faraday / (constants.R * constants.celsius_to_kelvin(model.Temp))
    v_array = np.linspace(model.VMIN, model.VMAX, model.VDIVS)
    ca_array = np.linspace(model.CAMIN, model.CAMAX, model.CADIVS)
    if model.VDIVS<=5 and model.CADIVS<=5:
        log.info("{}, {}", v_array, ca_array)
    gatingMatrix = []
    for i,pars in enumerate(params.X):
        Vdepgating=pars.K*np.exp(pars.delta*ZFbyRT*v_array)
        if i == 0:
            gatingMatrix.append(pars.alphabeta*ca_array[None,:]/(ca_array[None,:]+pars.K*Vdepgating[:,None]))
            #table.tableVector2D=gatingMatrix
        else:
            gatingMatrix.append(pars.alphabeta/(1+ca_array[None,:]/pars.K*Vdepgating[:,None]))
            gatingMatrix[i] += gatingMatrix[0]
            #table.tableVector2D=gatingMatrix


    chan = moose.HHChannel2D(chanpath)
    chan.Xpower = params.channel.Xpow
    chan.Ek=params.channel.Erev
    chan.Xindex="VOLT_C1_INDEX"
    xGate = moose.HHGate2D(chan.path + '/gateX')
    xGate.xminA=xGate.xminB=model.VMIN
    xGate.xmaxA=xGate.xmaxB=model.VMAX
    xGate.xdivsA=xGate.xdivsB=model.VDIVS
    xGate.yminA=xGate.yminB=model.CAMIN
    xGate.ymaxA=xGate.ymaxB=model.CAMAX
    xGate.ydivsA=xGate.ydivsB=model.CADIVS
    xGate.tableA=gatingMatrix[0]
    xGate.tableB=gatingMatrix[1]
    if log.isEnabledFor(logging.INFO):
        for ii in np.arange(0, model.VDIVS,1200):
            log.info("{} V={}", chan.path,model.VMIN+ii*(model.VMAX-model.VMIN)/(model.VDIVS-1))
            for jj in np.arange(0,model.CADIVS,2000):
                log.info("    Ca={} A,B={},{}",
                         model.CAMIN+jj*(model.CAMAX-model.CAMIN)/(model.CADIVS-1),
                         xGate.tableA[ii][jj], xGate.tableB[ii][jj])
    chan.tick=-1
    return chan
#Channels (model.py) includes channel function name in the dictionary


TypicalOneD = NamedList('TypicalOneD',
                             '''channel X Y Z=[] calciumPermeable=False calciumDependent=False''')
TwoD             = NamedList('TwoD',
                             '''channel X        calciumPermeable=False calciumDependent=False''')

_FUNCTIONS = {
    TypicalOneD: chan_proto,
    TwoD: BKchan_proto,
}

def make_channel(model, chanpath, params):
    func = _FUNCTIONS[params.__class__]
    return func(model, chanpath, params)

def chanlib(model,module=None):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    else:
        lib=moose.element('/library')

    if module is not None and not moose.exists('/library/'+module):
        lib=moose.Neutral('/library/'+module)
        print('new chan library for',module, lib.path)
    #Adding all the channels to the library.
    
    chan = [make_channel(model, lib.path + '/'+key, value) for key, value in model.Channels.items()]
    if model.ghkYN:
        ghk = moose.GHK('/library/ghk')
        ghk.T = model.Temp
        ghk.Cout = model.ConcOut
        ghk.valency=2
