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

from spspine import param_cond, param_chan, param_sim

def interpolate_values_in_table(tabA,V_0,l=40):
    '''This function interpolates values in the table
    around tabA[V_0]. '''
    V = np.linspace(param_chan.VMIN, param_chan.VMAX, len(tabA))
    idx =  abs(V-V_0).argmin()
    A_min = tabA[idx-l]
    V_min = V[idx-l]
    A_max = tabA[idx+l]
    V_max = V[idx+l]
    a = (A_max-A_min)/(V_max-V_min)
    b = A_max - a*V_max
    tabA[idx-l:idx+l] = V[idx-l:idx+l]*a+b
    return tabA

def fix_singularities(Params,Gate):
    
    if Params.A_C < 0:

        V_0 = Params.A_vslope*np.log(-Params.A_C)-Params.Avhalf

        if V_0 > param_chan.VMIN and V_0 < param_chan.VMAX:
            #change values in tableA and tableB, because tableB contains sum of alpha and beta
            tabA = interpolate_values_in_table(Gate.tableA,V_0)
            tabB = interpolate_values_in_table(Gate.tableB,V_0)
            Gate.tableA = tabA
            Gate.tableB = tabB

    if Params.B_C < 0:

        V_0 = Params.B_vslope*np.log(-Params.B_C)-Params.Bvhalf

        if V_0 > param_chan.VMIN and V_0 < param_chan.VMAX:
            #change values in tableB
            tabB = interpolate_values_in_table(Gate.tableB,V_0)
            Gate.tableB = tabB

    return Gate

#may need a CaV channel if X gate uses alpha,beta and Ygate uses inf tau
#Or, have Y form an option - if in tau, do something like NaF
def chan_proto(chanpath, params):
    if param_sim.printinfo:
        print(chanpath, ":", params)
    chan = moose.HHChannel(chanpath)
    chan.Xpower = params.channel.Xpow
    if params.channel.Xpow > 0:
        xGate = moose.HHGate(chan.path + '/gateX')
        xGate.setupAlpha(params.X + [param_chan.VDIVS, param_chan.VMIN, param_chan.VMAX])
        xGate = fix_singularities(params.X, xGate)

    chan.Ypower = params.channel.Ypow
    if params.channel.Ypow > 0:
        yGate = moose.HHGate(chan.path + '/gateY')
        yGate.setupAlpha(params.Y + [param_chan.VDIVS, param_chan.VMIN, param_chan.VMAX])
        yGate = fix_singularities(params.Y, yGate)
    if params.channel.Zpow > 0:
        chan.Zpower = params.channel.Zpow
        zgate = moose.HHGate(chan.path + '/gateZ')
        ca_array = np.linspace(param_chan.CAMIN, param_chan.CAMAX, param_chan.CADIVS)
        zgate.min = param_chan.CAMIN
        zgate.max = param_chan.CAMAX
        caterm = (ca_array/params.Z.Kd) ** params.Z.power
        inf_z = caterm / (1 + caterm)
        tau_z = params.Z.tau * np.ones(len(ca_array))
        zgate.tableA = inf_z / tau_z
        zgate.tableB = 1 / tau_z
        chan.useConcentration = True
    chan.Ek = params.channel.Erev
    return chan

def NaFchan_proto(chanpath, params):
    v_array = np.linspace(param_chan.VMIN, param_chan.VMAX, param_chan.VDIVS)
    chan = moose.HHChannel(chanpath)
    chan.Xpower = params.channel.Xpow #creates the m gate
    mgate = moose.HHGate(chan.path + '/gateX')
    #probably can replace the next 3 lines with mgate.setupTau (except for problem with tau_x begin quadratic)
    mgate.min=param_chan.VMIN
    mgate.max=param_chan.VMAX
    inf_x = params.X.Arate/(params.X.A_C + np.exp(( v_array+params.X.Avhalf)/params.X.Avslope))
    tau1 = params.X.tauVdep/(1+np.exp((v_array+params.X.tauVhalf)/params.X.tauVslope))
    tau2 = params.X.tauVdep/(1+np.exp((v_array+params.X.tauVhalf)/-params.X.tauVslope))
    tau_x = (params.X.taumin+1000*tau1*tau2)/param_chan.qfactNaF
    if param_sim.printMoreInfo:
        print("NaF mgate:", mgate, 'tau1:', tau1, "tau2:", tau2, 'tau:', tau_x)

    mgate.tableA = inf_x / tau_x
    mgate.tableB =  1 / tau_x
#    moose.showfield(mgate)

    chan.Ypower = params.channel.Ypow #creates the h gate
    hgate = moose.HHGate(chan.path + '/gateY')
    hgate.min = param_chan.VMIN
    hgate.max = param_chan.VMAX
    tau_y = (params.Y.taumin + (params.Y.tauVdep/(1+np.exp((v_array+params.Y.tauVhalf)/params.Y.tauVslope)))) / param_chan.qfactNaF
    inf_y = params.Y.Arate / (params.Y.A_C + np.exp(( v_array+params.Y.Avhalf)/params.Y.Avslope))
    if param_sim.printMoreInfo:
        print("NaF hgate:", hgate, 'inf:', inf_y, 'tau:', tau_y)
    hgate.tableA = inf_y / tau_y
    hgate.tableB = 1 / tau_y
    chan.Ek=params.channel.Erev
    return chan

def BKchan_proto(chanpath, params):
    ZFbyRT=2*param_cond.Faraday/(param_cond.R*(param_cond.Temp+273.15))
    v_array = np.linspace(param_chan.VMIN, param_chan.VMAX, param_chan.VDIVS)
    ca_array = np.linspace(param_chan.CAMIN, param_chan.CAMAX, param_chan.CADIVS)
    if param_chan.VDIVS<=5 and param_chan.CADIVS<=5 and param_sim.printinfo:
        print(v_array,ca_array)
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
    xGate.xminA=xGate.xminB=param_chan.VMIN
    xGate.xmaxA=xGate.xmaxB=param_chan.VMAX
    xGate.xdivsA=xGate.xdivsB=param_chan.VDIVS
    xGate.yminA=xGate.yminB=param_chan.CAMIN
    xGate.ymaxA=xGate.ymaxB=param_chan.CAMAX
    xGate.ydivsA=xGate.ydivsB=param_chan.CADIVS
    xGate.tableA=gatingMatrix[0]
    xGate.tableB=gatingMatrix[1]
    if param_sim.printinfo:
        print(chan.path)
        for ii in np.arange(0, param_chan.VDIVS,1000):
            print("V=", param_chan.VMIN+ii*(param_chan.VMAX-param_chan.VMIN)/(param_chan.VDIVS-1))
            for jj in np.arange(0,param_chan.CADIVS,1000):
                print("    Ca=", param_chan.CAMIN+jj*(param_chan.CAMAX-param_chan.CAMIN)/(param_chan.CADIVS-1), "A,B=", xGate.tableA[ii][jj],xGate.tableB[ii][jj])
    return chan
#ChanDict (param_chan.py) includes channel function name in the dictionary

_FUNCTIONS = {
    param_chan.TypicalOneDalpha: chan_proto,
    param_chan.AtypicalOneD: NaFchan_proto,
    param_chan.TwoD: BKchan_proto,
}

#*params... passes the set of values not as a list but as individuals
def make_channel(chanpath, params):
    func = _FUNCTIONS[params.__class__]
    return func(chanpath, params)

def chanlib():
    if not moose.exists('/library'):
        moose.Neutral('/library')
    #Adding all the channels to the library. *list removes list elements from the list,
    #so they can be used as function arguments
    chan = [make_channel('/library/'+key, value) for key, value in param_chan.ChanDict.items()]
    if param_sim.ghkYesNo:
        ghk=moose.GHK('/library/ghk')
        ghk.T=param_cond.Temp
        ghk.Cout=param_cond.ConcOut
        ghk.valency=2
    #
