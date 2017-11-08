"""\
Create general Channel Proto, pass in name, x and y power, and params

Also, create the library of channels
Might need a few other chan_proto types, such as
     inf-tau channels
     Ca dep channels
chan_proto quires alpha and beta params for both activation and inactivation
If no inactivation, just send in empty Yparam array.
"""

from __future__ import print_function, division
import moose
import numpy as np
import logging

from moose_nerp.prototypes import constants, logutil
from moose_nerp.prototypes.util import NamedList
log = logutil.Logger()

SSTauQuadraticChannelParams = NamedList('SSTauQuadraticChannelParams', '''
                                SS_min
                                SS_vdep
                                SS_vhalf
                                SS_vslope
                                taumin
                                tauVdep
                                tauVhalf
                                tauVslope''')

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
                                SS_vslope''')


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
    tau = sigmoid(v,params.T_min,params.T_vdep,params.T_vhalf,params.T_vslope)
    minf = sigmoid(v,params.SS_min,params.SS_vdep,params.SS_vhalf,params.SS_vslope)
    Gate.min = model.VMIN
    Gate.max = model.VMAX
    Gate.divs = model.VDIVS
    Gate.tableA = minf/tau
    Gate.tableB = 1/tau
    
def make_quadratic_gate(model,params,Gate):
    print('making quadratic gate', Gate.path)
    v = np.linspace(model.VMIN, model.VMAX, model.VDIVS)
    minf = sigmoid(v,params.SS_min,params.SS_vdep,params.SS_vhalf,params.SS_vslope)
    tau = quadratic(v,params.taumin,params.tauVdep,params.tauVhalf,params.tauVslope)
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
    A_min = tabA[idx-l]
    V_min = V[idx-l]
    A_max = tabA[idx+l]
    V_max = V[idx+l]
    a = (A_max-A_min)/(V_max-V_min)
    b = A_max - a*V_max
    tabA[idx-l:idx+l] = V[idx-l:idx+l]*a+b
    return tabA
 
def fix_singularities(model, Params, Gate):
    if Params.A_C < 0:
        V_0 = Params.A_vslope*np.log(-Params.A_C)-Params.A_vhalf

        if model.VMIN < V_0 < model.VMAX:
            #change values in tableA and tableB, because tableB contains sum of alpha and beta
            Gate.tableA = interpolate_values_in_table(model, Gate.tableA, V_0)
            Gate.tableB = interpolate_values_in_table(model, Gate.tableB, V_0)

    if Params.B_C < 0:
        V_0 = Params.B_vslope*np.log(-Params.B_C)-Params.B_vhalf

        if model.VMIN < V_0 < model.VMAX:
            #change values in tableB
            Gate.tableB = interpolate_values_in_table(model, Gate.tableB, V_0)

#may need a CaV channel if X gate uses alpha,beta and Ygate uses inf tau
#Or, have Y form an option - if in tau, do something like NaF
def chan_proto(model, chanpath, params):
    log.info("{}: {}", chanpath, params)
    chan = moose.HHChannel(chanpath)
    chan.Xpower = params.channel.Xpow
    if params.channel.Xpow > 0:
        
        xGate = moose.HHGate(chan.path + '/gateX')     

        if isinstance(params.X,AlphaBetaChannelParams):
            xGate.setupAlpha(params.X + [model.VDIVS, model.VMIN, model.VMAX])
            fix_singularities(model, params.X, xGate)
        elif isinstance(params.X,StandardMooseTauInfChannelParams):
            xGate.setupTau(params.X + [model.VDIVS, model.VMIN, model.VMAX])
            fix_singularities(model, params.X, xGate)
        elif isinstance(params.X,TauInfMinChannelParams):
            make_sigmoid_gate(model,params.X,xGate)
        elif isinstance(params.X,SSTauQuadraticChannelParams):
            make_quadratic_gate(model,params.X,xGate)
        
    chan.Ypower = params.channel.Ypow
    if params.channel.Ypow > 0:
        yGate = moose.HHGate(chan.path + '/gateY')
        if isinstance(params.Y,AlphaBetaChannelParams):
            yGate.setupAlpha(params.Y + [model.VDIVS, model.VMIN, model.VMAX])
            fix_singularities(model, params.Y, yGate)
        elif isinstance(params.Y,StandardMooseTauInfChannelParams):
            yGate.setupTau(params.Y + [model.VDIVS, model.VMIN, model.VMAX])
            fix_singularities(model, params.Y, yGate)
        elif isinstance(params.Y,TauInfMinChannelParams):
            make_sigmoid_gate(model,params.Y,yGate)
        elif isinstance(params.Y,SSTauQuadraticChannelParams):
            make_quadratic_gate(model,params.Y,yGate)

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
            if isinstance(params.Z,AlphaBetaChannelParams):
                zGate.setupAlpha(params.Z + [model.VDIVS, model.VMIN, model.VMAX])
                fix_singularities(model, params.Z, zGate)
            elif isinstance(params.Z,StandardMooseTauInfChannelParams):
                zGate.setupTau(params.Z + [model.VDIVS, model.VMIN, model.VMAX])
                fix_singularities(model, params.Z, zGate)
            elif isinstance(params.Z,TauInfMinChannelParams):
                make_sigmoid_gate(model,params.Z,zGate)
            elif isinstance(params.Z,SSTauQuadraticChannelParams):
                make_quadratic_gate(model,params.Z,zGate)

    chan.Ek = params.channel.Erev
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
        log.info("{}", chan.path)
        for ii in np.arange(0, model.VDIVS,1000):
            log.info("V={}", model.VMIN+ii*(model.VMAX-model.VMIN)/(model.VDIVS-1))
            for jj in np.arange(0,model.CADIVS,1000):
                log.info("    Ca={} A,B={},{}",
                         model.CAMIN+jj*(model.CAMAX-model.CAMIN)/(model.CADIVS-1),
                         xGate.tableA[ii][jj], xGate.tableB[ii][jj])
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

def chanlib(model):
    if not moose.exists('/library'):
        moose.Neutral('/library')
    #Adding all the channels to the library.
    chan = [make_channel(model, '/library/'+key, value) for key, value in model.Channels.items()]
    if model.ghkYN:
        ghk = moose.GHK('/library/ghk')
        ghk.T = model.Temp
        ghk.Cout = model.ConcOut
        ghk.valency=2

