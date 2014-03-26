##------create general Channel Proto, pass in name, x and y power, and params
#Also, create the library of channels
#Might need a few other chan_proto types, such as
#     inf-tau channels
#     Ca dep channels
# chan_proto quires alpha and beta params for both activation and inactivation
#If no inactivation, just send in empty Yparam array


VMIN = -120e-3
VMAX = 50e-3
VDIVS = 3401
CAMIN=0.01e-3   #10 nM
CAMAX=40e-3  #40 uM, might want to go up to 100 uM with spines
CADIVS=4001 #10 nM steps



#may need a CaV channel if X gate uses alpha,beta and Ygate uses inf tau
#Or, have Y form an option - if in tau, do something like NaF
def chan_proto(chanpath,params,Xparams,Yparams,Zparams=None):
    if printinfo:
        print chanpath, ":", params
    chan = moose.HHChannel('%s' % (chanpath))
    chan.Xpower = params.Xpow
    if params.Xpow > 0:
        xGate = moose.HHGate(chan.path + '/gateX')
        xGate.setupAlpha(Xparams + (VDIVS, VMIN, VMAX))
        #Check for singularities
        #Find if denominator might be 0, find where is the singularity, interpolate for crazy values
        if Xparams.A_C < 0:
            V_0 = Xparams.A_vslope*np.log(-Xparams.A_C)-Xparams.Avhalf
            if V_0 > VMIN and V_0 < VMAX:
                #change values in tableA
                tabA = xGate.tableA
                V = np.linspace(VMIN, VMAX, len(tabA))
                idx =  abs(V-V_0).argmin()
                A_min = tabA[idx-30]
                V_min = V[idx-30]
                A_max = tabA[idx+30]
                V_max = V[idx+30]
                a = (A_max-A_min)/(V_max-V_min)
                b = A_max - a*V_max
                tabA[idx-40:idx+40] = V[idx-40:idx+40]*a+b
                xGate.tableA = tabA
                #change values in tableB, because tableB contains sum of alpha and beta
                tabB = xGate.tableB
                tabB = xGate.tableB
                B_min = tabB[idx-30]
                V_min = V[idx-30]
                B_max = tabB[idx+30]
                V_max = V[idx+30]
                a = (B_max-B_min)/(V_max-V_min)
                b = B_max - a*V_max
                tabB[idx-40:idx+40] = V[idx-40:idx+40]*a+b
                xGate.tableB = tabB
        if Xparams.B_C < 0:
            V_0 = Xparams.B_vslope*np.log(-Xparams.B_C)-Xparams.Bvhalf
            if V_0 > VMIN and V_0 < VMAX:
                #change values in tableB
                tabB = xGate.tableB
                V = np.linspace(VMIN, VMAX, len(tabB))
                idx =  abs(V-V_0).argmin()
                B_min = tabB[idx-30]
                V_min = V[idx-30]
                B_max = tabB[idx+30]
                V_max = V[idx+30]
                a = (B_max-B_min)/(V_max-V_min)
                b = B_max - a*V_max
                tabB[idx-40:idx+40] = V[idx-40:idx+40]*a+b
                xGate.tableB = tabB

 
    chan.Ypower = params.Ypow
    if params.Ypow > 0:
        yGate = moose.HHGate(chan.path + '/gateY')
        yGate.setupAlpha(Yparams + (VDIVS, VMIN, VMAX))
        if Yparams.A_C < 0:
            V_0 = Yparams.A_vslope*np.log(-Yparams.A_C)-Yparams.Avhalf

            if V_0 > VMIN and V_0 < VMAX:
                #change values in tableA
                ytabA = yGate.tableA
                V = np.linspace(VMIN, VMAX, len(ytabA))
                idx =  abs(V-V_0).argmin()
                A_min = ytabA[idx-30]
                V_min = V[idx-30]
                A_max = ytabA[idx+30]
                V_max = V[idx+30]
                a = (A_max-A_min)/(V_max-V_min)
                b = A_max - a*V_max

                ytabA[idx-30:idx+30] = V[idx-30:idx+30]*a+b
                yGate.tableA = ytabA
                #change values in tableB, because tableB contains sum of alpha and beta
                ytabB = yGate.tableB
                B_min = ytabB[idx-30]
                V_min = V[idx-30]
                B_max = ytabB[idx+30]
                V_max = V[idx+30]
                a = (B_max-B_min)/(V_max-V_min)
                b = B_max - a*V_max
                ytabB[idx-30:idx+30] = V[idx-30:idx+30]*a+b
                yGate.tableB = ytabB

        if Yparams.B_C < 0:
            V_0 = Yparams.B_vslope*np.log(-Yparams.B_C)-Yparams.Bvhalf
           
            if V_0 > VMIN and V_0 < VMAX:
                #change values in tableB
                ytabB = yGate.tableB
                V = np.linspace(VMIN, VMAX, len(ytabB))
                idx =  abs(V-V_0).argmin()
                B_min = ytabB[idx-30]
                V_min = V[idx-30]
                B_max = ytabB[idx+30]
                V_max = V[idx+30]
                a = (B_max-B_min)/(V_max-V_min)
                b = B_max - a*V_max
                ytabB[idx-30:idx+30] = V[idx-30:idx+30]*a+b
                yGate.tableB = ytabB
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
    if printMoreInfo:
        print  "NaF mgate:", mgate, 'tau1:', tau1, "tau2:", tau2, 'tau:', tau_x

    mgate.tableA = inf_x / tau_x
    mgate.tableB =  1 / tau_x
#    moose.showfield(mgate)

    chan.Ypower = params.Ypow #creates the h gate
    hgate = moose.HHGate(chan.path + '/gateY')
    hgate.min=VMIN
    hgate.max=VMAX
    tau_y=(Yparams.taumin+(Yparams.tauVdep/(1+exp((v_array+Yparams.tauVhalf)/Yparams.tauVslope))))/qfactNaF
    inf_y=Yparams.Arate/(Yparams.A_C + exp(( v_array+Yparams.Avhalf)/Yparams.Avslope))
    if printMoreInfo:
        print  "NaF hgate:", hgate, 'inf:', inf_y, 'tau:', tau_y
    hgate.tableA = inf_y / tau_y
    hgate.tableB = 1 / tau_y
    chan.Ek=params.Erev
    return chan

def BKchan_proto(chanpath,params,gateParams):

    ZFbyRT=2*Farady/(R*(Temp+273.15))
    v_array = np.linspace(VMIN, VMAX, VDIVS)
    ca_array = np.linspace(CAMIN, CAMAX, CADIVS)
    if (VDIVS<=5 and CADIVS<=5 and printinfo):
        print v_array,ca_array
    gatingMatrix = []
    for i,pars in enumerate(gateParams):
        Vdepgating=pars.K*np.exp(pars.delta*ZFbyRT*v_array)
        if i == 0:
            gatingMatrix.append(pars.alphabeta*ca_array[None,:]/(ca_array[None,:]+pars.K*Vdepgating[:,None]))
            #table.tableVector2D=gatingMatrix
        else:
            gatingMatrix.append(pars.alphabeta/(1+ca_array[None,:]/pars.K*Vdepgating[:,None]))
            gatingMatrix[i] += gatingMatrix[0]
            #table.tableVector2D=gatingMatrix


    chan = moose.HHChannel2D('%s' % (chanpath))
    chan.Xpower = params.Xpow
    xGate = moose.HHGate2D(chan.path + '/gateX')
    tablenames=['/tableA','/tableB']
    for i,tname in enumerate(tablenames):
        table=moose.element(xGate.path+tname)
        table.xmin=VMIN
        table.xmax=VMAX
        table.xdivs=VDIVS
        table.ymin=CAMIN
        table.ymax=CAMAX
        table.ydivs=CADIVS
        table.tableVector2D = gatingMatrix[i]

        if (VDIVS<=5 and CADIVS<=5 and printinfo):
            print chan.path,tname,table.tableVector2D
    return chan
#Moved ChanDict from SPChanParam.py to include channel function name in the dictionary


def make_channel(chanpath,params):
    if params[0] == 'typical_1D_alpha':
        return chan_proto(chanpath,*params[1:])
    elif params[0] == 'untypical_1D':
        return NaFchan_proto(chanpath,*params[1:])
    elif params[0] == '2D':
        return BKchan_proto(chanpath,*params[1:])
    else:
        sys.exit('Exiting. Could not find channel '+params[0] +' proto function for channel '+chanpath)

def chanlib(plotchan,plotpow):
    if not moose.exists('/library'):
        lib = moose.Neutral('/library')
    #Adding all the channels to the library. *list removes list elements from the list,
    #so they can be used as function arguments
    chan = [make_channel('/library/'+key,ChanDict[key])for key in ChanDict]
    if ghkYesNo:
        ghk=moose.GHK('/library/ghk')
        ghk.T=Temp
        ghk.Cout=ConcOut
        ghk.valency=2
    #
    if plotchan:
        for libchan in chan:
            plot_gate_params(libchan,plotpow)
