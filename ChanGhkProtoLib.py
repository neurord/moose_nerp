##------create general Channel Proto, pass in name, x and y power, and params
#Also, create the library of channels
#Might need a few other chan_proto types, such as
#     inf-tau channels
#     Ca dep channels
# chan_proto quires alpha and beta params for both activation and inactivation
#If no inactivation, just send in empty Yparam array

VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3400
CAMIN=0.01e-3   #10 nM
CAMAX=40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS=3999 #10 nM steps

#may need a CaV channel if X gate uses alpha,beta and Ygate uses inf tau
#Or, have Y form an option - if in tau, do something like NaF
def chan_proto(chanpath,params,Xparams,Yparams,Zparams=[]):
    #print params
    chan = moose.HHChannel('%s' % (chanpath))
    chan.Xpower = params['Xpow']
    if (params['Xpow'] > 0):
        xGate = moose.HHGate(chan.path + '/gateX') 
        xGate.setupAlpha(Xparams +
                      [VDIVS, VMIN, VMAX])
#    moose.showfield(xGate)
    chan.Ypower = params['Ypow']
    if (params['Ypow'] > 0):
        yGate = moose.HHGate(chan.path + '/gateY')
        yGate.setupAlpha(Yparams + 
                      [VDIVS, VMIN, VMAX])
    if (params['Zpow'] > 0):
        chan.Zpower = params['Zpow']
        zgate = moose.HHGate(chan.path + '/gateZ') 
        ca_array = np.linspace(CAMIN, CAMAX, CADIVS+1)
        zgate.min=CAMIN
        zgate.max=CAMAX
        caterm=(ca_array/Zparams[0])**Zparams[1]
        inf_z=caterm/(1+caterm)
        tau_z=Zparams[2]*ones(len(ca_array))
        zgate.tableA=inf_z / tau_z
        zgate.tableB=1 / tau_z
        chan.useConcentration=True
        #moose.showfield(zgate)
    #end if Zpow
    chan.Ek = params['Erev'] 
    return chan

def NaFchan_proto(chanpath,params,Xparams,Yparams):
    v_array = np.linspace(VMIN, VMAX, VDIVS+1)
    chan = moose.HHChannel('%s' % (chanpath))
    chan.Xpower = params['Xpow'] #creates the m gate
    mgate = moose.HHGate(chan.path + '/gateX') 
    mgate.min=VMIN
    mgate.max=VMAX
    inf_x=Xparams['Arate']/(Xparams['A_C'] + exp(( v_array+Xparams['Avhalf'])/Xparams['Avslope']))
    tau1=(Xparams['tauVdep']/(1+exp((v_array+Xparams['tauVhalf'])/Xparams['tauVslope'])))
    tau2=(Xparams['tauVdep']/(1+exp((v_array+Xparams['tauVhalf'])/-Xparams['tauVslope'])))
    tau_x=(Xparams['taumin']+1000*tau1*tau2)/qfactNaF
#    print  "mgate:", mgate, 'tau1:', tau1, "tau2:", tau2, 'tau:', tau_x

    mgate.tableA = inf_x / tau_x
    mgate.tableB =  1 / tau_x
#    moose.showfield(mgate)

    chan.Ypower = params['Ypow'] #creates the h gate
    hgate = moose.HHGate(chan.path + '/gateY') 
    hgate.min=VMIN
    hgate.max=VMAX
    tau_y=(Yparams['taumin']+(Yparams['tauVdep']/(1+exp((v_array+Yparams['tauVhalf'])/Yparams['tauVslope']))))/qfactNaF
    inf_y=Yparams['Arate']/(Yparams['A_C'] + exp(( v_array+Yparams['Avhalf'])/Yparams['Avslope'])) 
#    print  "hgate:", hgate, 'inf:', inf_y, 'tau:', tau_y
    hgate.tableA = inf_y / tau_y
    hgate.tableB = 1 / tau_y 
    chan.Ek=params['Erev']
    return chan

#def BKchan_proto(chanpath,params,Zparams):
#    #Need to implement 2D table
#    return chan

def chanlib(plotchan,plotpow):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    #na chan uses special format
    chanpath='/library/'+NaFparam['name']
    nachan=NaFchan_proto(chanpath,NaFparam,Na_m_params,Na_h_params)
    #
    chan=list()
    for key in ChanDict.keys():
        chanpath='/library/'+key
        if (ChanDict[key]['Zpow']==0):
            chan.append(chan_proto(chanpath,ChanDict[key],XChanDict[key],YChanDict[key]))
        else:
            chan.append(chan_proto(chanpath,ChanDict[key],XChanDict[key],YChanDict[key],ZChanDict[key]))
    #
    if ghkYesNo:
        ghk=moose.GHK('/library/ghk')
        ghk.T=Temp
        ghk.Cout=ConcOut
        ghk.valency=2
    #
    if (plotchan==1):
        plot_gate_params(nachan,plotpow)
        for libchan in chan:
            plot_gate_params(libchan,plotpow)

