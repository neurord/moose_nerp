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
CADIVS=4000 #10 nM steps



#may need a CaV channel if X gate uses alpha,beta and Ygate uses inf tau
#Or, have Y form an option - if in tau, do something like NaF
def chan_proto(chanpath,params,Xparams,Yparams,Zparams=None):
    #print params
    chan = moose.HHChannel('%s' % (chanpath))
    chan.Xpower = params.Xpow
    if params.Xpow > 0:
        xGate = moose.HHGate(chan.path + '/gateX')
        xGate.setupAlpha(Xparams + (VDIVS, VMIN, VMAX))
#    moose.showfield(xGate)
    chan.Ypower = params.Ypow
    if params.Ypow > 0:
        yGate = moose.HHGate(chan.path + '/gateY')
        yGate.setupAlpha(Yparams + (VDIVS, VMIN, VMAX))
    if params.Zpow > 0:
        chan.Zpower = params.Zpow
        zgate = moose.HHGate(chan.path + '/gateZ')
        ca_array = np.linspace(CAMIN, CAMAX, CADIVS)
        zgate.min=CAMIN
        zgate.max=CAMAX
        caterm=(ca_array/Zparams.Kd)**Zparams.power
        inf_z=caterm/(1+caterm)
        tau_z=Zparams.tau*ones(len(ca_array))
        zgate.tableA=inf_z / tau_z
        zgate.tableB=1 / tau_z
        chan.useConcentration=True
        #moose.showfield(zgate)
    #end if Zpow
    chan.Ek = params.Erev
    return chan

def NaFchan_proto(chanpath,params,Xparams,Yparams):
    v_array = np.linspace(VMIN, VMAX, VDIVS)
    chan = moose.HHChannel('%s' % (chanpath))
    chan.Xpower = params.Xpow #creates the m gate
    mgate = moose.HHGate(chan.path + '/gateX')
    #probably can replace the next 3 lines with mgate.setupTau (except for problem with tau_x begin quadratic)
    mgate.min=VMIN
    mgate.max=VMAX
    inf_x=Xparams.Arate/(Xparams.A_C + exp(( v_array+Xparams.Avhalf)/Xparams.Avslope))
    tau1=(Xparams.tauVdep/(1+exp((v_array+Xparams.tauVhalf)/Xparams.tauVslope)))
    tau2=(Xparams.tauVdep/(1+exp((v_array+Xparams.tauVhalf)/-Xparams.tauVslope)))
    tau_x=(Xparams.taumin+1000*tau1*tau2)/qfactNaF
#    print  "mgate:", mgate, 'tau1:', tau1, "tau2:", tau2, 'tau:', tau_x

    mgate.tableA = inf_x / tau_x
    mgate.tableB =  1 / tau_x
#    moose.showfield(mgate)

    chan.Ypower = params.Ypow #creates the h gate
    hgate = moose.HHGate(chan.path + '/gateY')
    hgate.min=VMIN
    hgate.max=VMAX
    tau_y=(Yparams.taumin+(Yparams.tauVdep/(1+exp((v_array+Yparams.tauVhalf)/Yparams.tauVslope))))/qfactNaF
    inf_y=Yparams.Arate/(Yparams.A_C + exp(( v_array+Yparams.Avhalf)/Yparams.Avslope))
#    print  "hgate:", hgate, 'inf:', inf_y, 'tau:', tau_y
    hgate.tableA = inf_y / tau_y
    hgate.tableB = 1 / tau_y
    chan.Ek=params.Erev
    return chan

def BKchan_proto(chanpath,params,gateParams):
    chan = moose.HHChannel2D('%s' % (chanpath))
    chan.Xpower = params.Xpow
    xGate = moose.HHGate2D(chan.path + '/gateX')
    tablenames=['/tableA','/tableB']
    ZFbyRT=2*Farady/(R*(Temp+273.15))
    v_array = np.linspace(VMIN, VMAX, VDIVS)
    ca_array = np.linspace(CAMIN, CAMAX, CADIVS)
    if (VDIVS<=5 and CADIVS<=5 and printinfo):
        print v_array,ca_array
   
    for tname,pars in zip(tablenames,gateParams):
        table=moose.element(xGate.path+tname)
        table.xmin=VMIN
        table.xmax=VMAX
        table.xdivs=VDIVS
        table.ymin=CAMIN
        table.ymax=CAMAX
        table.ydivs=CADIVS
        Vdepgating=pars.K*np.exp(pars.delta*ZFbyRT*v_array)
        if tname=='/tableA':
            gatingMatrix=pars.alphabeta*ca_array[None,:]/(ca_array[None,:]+Vdepgating[:,None])
            table.tableVector2D=gatingMatrix
        else:
            gatingMatrix=pars.alphabeta/(1+ca_array[None,:]/Vdepgating[:,None])
            table.tableVector2D=gatingMatrix
        if (VDIVS<=5 and CADIVS<=5 and printinfo):
            print chan.path,tname,table.tableVector2D
    return chan
#Moved ChanDict from SPChanParam.py to include channel function name in the dictionary

ChanDict={'Krp':[chan_proto,Krpparam,Krp_X_params,Krp_Y_params],
          'KaF':[chan_proto,KaFparam,KaF_X_params,KaF_Y_params],
          'KaS':[chan_proto,KaSparam,KaS_X_params,KaS_Y_params],
          'Kir': [chan_proto,Kirparam, Kir_X_params,[]],
          'CaL12':[chan_proto,CaL12param,CaL12_X_params,[],CDI_Z_params],
          'CaL13':[chan_proto,CaL13param,CaL13_X_params,[],CDI_Z_params],
          'CaN': [chan_proto,CaNparam,CaN_X_params,[],CDI_Z_params],
          'CaR': [chan_proto,CaRparam,CaR_X_params,CaR_Y_params,CDI_Z_params],
          'CaT': [chan_proto,CaTparam,CaT_X_params,CaT_Y_params,CDI_Z_params],
          'SKCa':[chan_proto,SKparam,[],[],SK_Z_params],
          'NaF':[NaFchan_proto,NaFparam,Na_m_params,Na_h_params],
          'BKCa':[BKchan_proto,BKparam,BK_X_params]
}

def chanlib(plotchan,plotpow):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    #Adding all the channels to the library. *list removes list elements from the list,
    #so they can be used as function arguments
    chan = [ChanDict[key][0]('/library/'+key,*ChanDict[key][1:])for key in ChanDict]
    if ghkYesNo:
        ghk=moose.GHK('/library/ghk')
        ghk.T=Temp
        ghk.Cout=ConcOut
        ghk.valency=2
    #
    if plotchan:
        plot_gate_params(nachan,plotpow)
        for libchan in chan:
            plot_gate_params(libchan,plotpow)
