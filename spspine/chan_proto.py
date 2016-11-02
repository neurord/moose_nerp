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

from spspine import constants, logutil
from spspine.util import NamedList
log = logutil.Logger()

SSTauChannelParams = NamedList('SSTauChannelParams', '''
                                Arate
                                A_B
                                A_C
                                Avhalf
                                Avslope
                                taumin
                                tauVdep
                                tauPow
                                tauVhalf
                                tauVslope''')

AlphaBetaChannelParams = NamedList('AlphaBetaChannelParams', '''
                                A_rate
                                A_B
                                A_C
                                Avhalf
                                A_vslope
                                B_rate
                                B_B
                                B_C
                                Bvhalf
                                B_vslope''')

ZChannelParams = NamedList('ZChannelParams', 'Kd power tau')
BKChannelParams=NamedList('BKChannelParams', 'alphabeta K delta')

ChannelSettings = NamedList('ChannelSettings', 'Xpow Ypow Zpow Erev name')

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
        V_0 = Params.A_vslope*np.log(-Params.A_C)-Params.Avhalf

        if model.VMIN < V_0 < model.VMAX:
            #change values in tableA and tableB, because tableB contains sum of alpha and beta
            Gate.tableA = interpolate_values_in_table(model, Gate.tableA, V_0)
            Gate.tableB = interpolate_values_in_table(model, Gate.tableB, V_0)

    if Params.B_C < 0:
        V_0 = Params.B_vslope*np.log(-Params.B_C)-Params.Bvhalf

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
        xGate.setupAlpha(params.X + [model.VDIVS, model.VMIN, model.VMAX])
        fix_singularities(model, params.X, xGate)

    chan.Ypower = params.channel.Ypow
    if params.channel.Ypow > 0:
        yGate = moose.HHGate(chan.path + '/gateY')
        yGate.setupAlpha(params.Y + [model.VDIVS, model.VMIN, model.VMAX])
        fix_singularities(model, params.Y, yGate)

    if params.channel.Zpow > 0:
        chan.Zpower = params.channel.Zpow
        zGate = moose.HHGate(chan.path + '/gateZ')
        if params.Z.__class__==ZChannelParams:
            ca_array = np.linspace(model.CAMIN, model.CAMAX, model.CADIVS)
            zGate.min = model.CAMIN
            zGate.max = model.CAMAX
            caterm = (ca_array/params.Z.Kd) ** params.Z.power
            inf_z = caterm / (1 + caterm)
            tau_z = params.Z.tau * np.ones(len(ca_array))
            zGate.tableA = inf_z / tau_z
            zGate.tableB = 1 / tau_z
            chan.useConcentration = True
        else:
            zGate.setupAlpha(params.Z + [model.VDIVS, model.VMIN, model.VMAX])
            fix_singularities(model, params.Z, zGate)
            chan.useConcentration = False
    chan.Ek = params.channel.Erev
    return chan

def NaFchan_proto(model, chanpath, params):
    v_array = np.linspace(model.VMIN, model.VMAX, model.VDIVS)
    chan = moose.HHChannel(chanpath)
    chan.Xpower = params.channel.Xpow #creates the m gate
    mgate = moose.HHGate(chan.path + '/gateX')
    #probably can replace the next 3 lines with mgate.setupTau (except for problem with tau_x begin quadratic)
    mgate.min=model.VMIN
    mgate.max=model.VMAX
    inf_x = params.X.Arate/(params.X.A_C + np.exp(( v_array+params.X.Avhalf)/params.X.Avslope))
    tau1 = params.X.tauVdep/(1+np.exp((v_array+params.X.tauVhalf)/params.X.tauVslope))
    tau2 = params.X.tauVdep/(1+np.exp((v_array+params.X.tauVhalf)/-params.X.tauVslope))
    tau_x = (params.X.taumin+1000*tau1*tau2)/model.qfactNaF
    log.debug("NaF mgate:{} tau1:{} tau2:{} tau:{}", mgate, tau1, tau2, tau_x)

    mgate.tableA = inf_x / tau_x
    mgate.tableB =  1 / tau_x
#    moose.showfield(mgate)

    chan.Ypower = params.channel.Ypow #creates the h gate
    hgate = moose.HHGate(chan.path + '/gateY')
    hgate.min = model.VMIN
    hgate.max = model.VMAX
    tau_y = (params.Y.taumin + (params.Y.tauVdep/(1+np.exp((v_array+params.Y.tauVhalf)/params.Y.tauVslope)))) / model.qfactNaF
    inf_y = params.Y.Arate / (params.Y.A_C + np.exp(( v_array+params.Y.Avhalf)/params.Y.Avslope))
    log.debug("NaF hgate:{} inf:{} tau:{}", hgate, inf_y, tau_y)
    hgate.tableA = inf_y / tau_y
    hgate.tableB = 1 / tau_y
    chan.Ek=params.channel.Erev
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

TypicalOneDalpha = NamedList('TypicalOneDalpha',
                             '''channel X Y Z=[] calciumPermeable=False calciumDependent=False''')
AtypicalOneD     = NamedList('AtypicalOneD',
                             '''channel X Y      calciumPermeable=False calciumDependent=False''')
TwoD             = NamedList('TwoD',
                             '''channel X        calciumPermeable=False calciumDependent=False''')

_FUNCTIONS = {
    TypicalOneDalpha: chan_proto,
    AtypicalOneD: NaFchan_proto,
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

