#%%
from matplotlib import pyplot as plt 
import numpy as np 
#%%
v = np.linspace(-150e-3,50e-3,100)

mcrory_data_CaT33_Act_SS = np.array([
    [-0.09012315605950066, 0.019966490670558112],
    [-0.08504964574085291, 0.021706873740308552],
    [-0.08016828855118519, 0.03866247078753071],
    [-0.07508773014479492, 0.07652430353764572],
    [-0.06999270461093321, 0.18853016457903093],
    [-0.06507907459844448, 0.3708839785837048],
    [-0.05997143669704348, 0.5475282232636354],
    [-0.05486862117146635, 0.6994577918464757],
    [-0.04996723257453041, 0.8190743511431502],
    [-0.04487814227245185, 0.9006621492958091],
    [-0.03979647101010225, 0.9442273688375593],
    [-0.03471813831563064, 0.9706824280044026],
    [-0.02983603922199002, 0.9914402829127154],
    [-0.024762157951355793, 0.9950817949130117],
    ])

mcrory_data_CaT33_Inact_SS = np.array([
    [-0.11998145240067759, 0.996197742138909],
    [-0.11490979684196206, 0.9884324805559328],
    [-0.11003734249996906, 0.9597609832700655],
    [-0.10497421883694186, 0.9082697562845445],
    [-0.09992185278152163, 0.801645790313207],
    [-0.09508167126234957, 0.6075760760698876],
    [-0.09005861041385875, 0.35076292458546066],
    [-0.08502479195776091, 0.14908251208685197],
    [-0.08016309522337489, 0.06527827581516688],
    [-0.07509552013651032, 0.036600595996191476],
    [-0.07002423552978126, 0.026934205482670226],
    [-0.06495109616311993, 0.02677345962187694],
    ])


mcrory_data_CaT33_Act_Tau = np.array([
    [-0.06026775363673758, 0.020365917504954943],
    [-0.05521035114618001, 0.013356830335439968],
    [-0.05022624434389139, 0.008913092255338248],
    [-0.04530645824763471, 0.0067205788863542865],
    [-0.04041210126771623, 0.005418084589207589],
    [-0.03524101566882315, 0.004430088627949601],
    [-0.030078905052167065, 0.0037562170449871035],
    [-0.02520997718858682, 0.0033437418196776564],
    [-0.020061329045286264, 0.0031410568041584097],
    [-0.014921655884222715, 0.003252496166934682],
    [-0.010064694663625112, 0.0032588534460192345],
    [-0.004913054859578936, 0.002951460304401486],
    [-0.00007404360345530936, 0.0035860663400770418],
    [0.005068621218353844, 0.0035927975767548054],
    ])

mcrory_data_CaT33_Inact_Tau = np.array([
    [-0.06542442813853142, 0.3826529686921434],
    [-0.060373457466504445, 0.20848289516439822],
    [-0.05551594108712244, 0.16162992798361664],
    [-0.05045711133445678, 0.13228759701052661],
    [-0.045198177297836484, 0.121251634159796],
    [-0.04039748811691897, 0.11179806696843508],
    [-0.035380976490769364, 0.11030635300874314],
    [-0.030136551526097455, 0.10881917313403511],
    [-0.02512608534659301, 0.11130611874768559],
    [-0.02011561916708858, 0.11379306436133607],
    [-0.01510394389825516, 0.11548427806031802],
    [-0.010092268629421683, 0.11717549175930042],
])

alpha = 160.e3 * (v + 0.112) / (np.exp((v + 0.112)/0.011) - 1)
beta = 8500*np.exp(v/0.0125)
CaT33_mtau = 1/(alpha+beta) + 0.0009

mvhalfCaT33 = -43.15e-3
mkCaT33 = -5.34e-3

CaT33_minf = 1. / ( 1. + np.exp((v - mvhalfCaT33)/mkCaT33))


CaT33_htau = 22.25e-3 + 0.0455e-3 * np.exp(-v/7.46e-3)


hvhalfCaT33 = -79e-3
hkCaT33 = 2.76e-3
CaT33_hinf = 1. / (1. + np.exp((v-hvhalfCaT33)/hkCaT33))

f,axs = plt.subplots(1,2)
axs[0].plot(v,CaT33_minf)
axs[0].plot(v,CaT33_hinf)
axs[1].plot(v,CaT33_mtau)
axs[1].plot(v,CaT33_htau)

#%%

alpha = 14552 * (v + 0.0845) / (np.exp((v + 0.0845)/0.00712) - 1)
beta = 4984.2*np.exp(v/0.013)
CaT33_mtau = 1/(alpha+beta) + 0.0025

mvhalfCaT33 = -70e-3
mkCaT33 = -8e-3

CaT33_minf = 1. / ( 1. + np.exp((v - mvhalfCaT33)/mkCaT33))


alpha = 2652*(v + 0.0945) / (np.exp((v + 0.0945)/0.00512)-1)
beta = 684.2*np.exp(v/0.013)
CaT33_htau = 1/(alpha+beta)+.1


hvhalfCaT33 = -93e-3
hkCaT33 = 5e-3
CaT33_hinf = 1. / (1. + np.exp((v-hvhalfCaT33)/hkCaT33))

f,axs = plt.subplots(1,2)
axs[0].plot(v,CaT33_minf)
axs[0].plot(v,CaT33_hinf)
axs[1].plot(v,CaT33_mtau)
axs[1].plot(v,CaT33_htau)

#%%
import scipy.optimize
def alphabetafunction(X,ssx,taux,power,qfactor):
    #sigmoid form only:
    v = np.linspace(-150e-3,50e-3,100)
    arate,avhalf,avslope,brate,bvhalf,bvslope,=X
    aB = 0
    aC=1
    bB=0
    bC=1
    taumin=0
    ## General Form:
    alpha = (arate + aB * v) / (aC + np.exp((v + avhalf) / avslope))
    beta = (brate + bB * v) / (bC + np.exp((v + bvhalf) / bvslope))
    tau = taumin + (1.0/(alpha+beta))
    ss = alpha/(alpha+beta)
    tau = taumin + (1.0/(alpha+beta))
    tau = np.interp(taux,v,tau)
    ss = alpha/(alpha+beta)
    ss = ss**power
    ss = np.interp(ssx,v,ss)
    return tau,ss

def sigmoid(x,xmin,xmax,xvhalf,xslope):
    return xmin+xmax/(1+np.exp((x-xvhalf)/xslope))

def tauinfminfunction(X,ssx,taux,power,qfactor):
    T_min, T_vdep, T_vhalf, T_vslope, SS_min, SS_vhalf, SS_vslope, = X 
    #SS_min = 0
    SS_vdep = 1
    T_power = 1
    tau = sigmoid(v,T_min,T_vdep,T_vhalf,T_vslope)
    ss = sigmoid(v, SS_min, SS_vdep, SS_vhalf, SS_vslope)
    ss = ss**power
    ss = np.interp(ssx,v,ss)
    tau = np.interp(taux,v,tau)
    tau = tau/qfactor
    return tau,ss

### Fitting function to optimize alpha/beta parameters given in X:
def fit(X,*args):
    ssfit,taufit,power,qfactor = args
    ssx = ssfit[:,0]
    taux = taufit[:,0]
    ssfit = ssfit[:,1]
    taufit = taufit[:,1]
    tau, ss = tauinfminfunction(X,ssx,taux,power,qfactor)
    #tau, ss = alphabetafunction(X,ssx,taux,power,qfactor)
    
    tauerror = (tau-taufit)/np.max(taufit)
    sserror=(ss-ssfit)/np.max(ssfit)
    taurms = np.sqrt(np.mean(tauerror**2))
    ssrms = np.sqrt(np.mean(sserror**2))
    error=2*taurms+ssrms
    return error

### Parameter boundaries for fitting function:
minbound = (0,.2)
vdep_bound = (.201,1)
vhalf_bound = (-200e-3,100e-3)
vslope_bound = (-100,100)
bounds = [minbound,vdep_bound, vhalf_bound, vslope_bound,minbound, vhalf_bound,vslope_bound]

ratebound=(-20000000,200000000.)
bbound=(-20000000000,20000000000)
vhalfbound=(-30000,30000)
vslopebound=(-20000,20000)

#bounds=[ratebound,vhalfbound,vslopebound,ratebound,vhalfbound,vslopebound]

#v = v_CaT33Taus = np.linspace(-50e-3,0e-3,50)
### Fitting Function, passing yInf/yTau equations to fit yGate:
resX=scipy.optimize.differential_evolution(fit,bounds,args=(mcrory_data_CaT33_Act_SS,mcrory_data_CaT33_Act_Tau,3,1),tol=1e-35,maxiter=2000,workers=12,popsize=12)#,mutation=1.9,seed=12,popsize=60,recombination=0.2)
#%%
# Get best alpha,beta,tau,and ss values using the outcome of fitting procedure:
tau,ss = tauinfminfunction(resX.x,v,v,3,1)

# Compare the fit
plt.figure()
ax = plt.subplot(1,2,1)
plt.plot(mcrory_data_CaT33_Act_SS[:,0],mcrory_data_CaT33_Act_SS[:,1],label='minf',marker = '.')
plt.plot(v,ss,label='minffit')
plt.legend()
ax = plt.subplot(1,2,2)
plt.plot(mcrory_data_CaT33_Act_Tau[:,0], mcrory_data_CaT33_Act_Tau[:,1], label='mtau',marker='.')
plt.plot(v,tau,label='taufit')
plt.legend()

#%%
### Fitting Function, passing xInf/xTau equations to fit xGate:
resY=scipy.optimize.differential_evolution(fit,bounds,args=(mcrory_data_CaT33_Inact_SS,mcrory_data_CaT33_Inact_Tau,1,1),tol=1e-35,maxiter=2000,workers=12,popsize=12)#,mutation=1.9,seed=12,popsize=60,recombination=0.2)
#%%
# Get best alpha,beta,tau,and ss values using the outcome of fitting procedure:
tau,ss = tauinfminfunction(resY.x,v,v,1,1)

# Compare the fit
plt.figure()
ax = plt.subplot(1,2,1)
plt.plot(mcrory_data_CaT33_Inact_SS[:,0],mcrory_data_CaT33_Inact_SS[:,1],label='minf',marker = '.')
plt.plot(v,ss,label='minffit')
plt.legend()
ax = plt.subplot(1,2,2)
plt.plot(mcrory_data_CaT33_Inact_Tau[:,0], mcrory_data_CaT33_Inact_Tau[:,1], label='mtau',marker='.')
plt.plot(v,tau,label='taufit')
plt.legend()
plt.ylim(0,1)

#%%
