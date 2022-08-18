#%%
from matplotlib import pyplot as plt 
import numpy as np 
#%%
v = np.linspace(-100e-3,50e-3,100)

mcrory_data_CaT32_Act_SS = np.array([
    [-0.09019008019008024, 0.004247104247104616],
    [-0.08513216513216515, 0.003667953667954027],
    [-0.07968517968517969, 0.0030442530442531535],
    [-0.07501633501633503, 0.002509652509652849],
    [-0.06957231957231957, -0.0019305019305018156],
    [-0.06490050490050492, 0.0013513513513516706],
    [-0.06021681021681019, 0.019899019899019876],
    [-0.05473418473418473, 0.06507276507276538],
    [-0.04995841995841993, 0.201930501930502],
    [-0.044728244728244715, 0.4227056727056726],
    [-0.04028512028512027, 0.632120582120582],
    [-0.03510840510840507, 0.7841995841995839],
    [-0.030359370359370308, 0.8867092367092364],
    [-0.025250965250965207, 0.9510098010098007],
    [-0.020561330561330526, 0.9771903771903769],
    [-0.015889515889515815, 0.9804722304722304],
    [-0.01083457083457079, 0.976076626076626],
    ])

mcrory_data_CaT32_Inact_SS = np.array([
    [-0.08999999999999997, 0.9985001485001481],
    [-0.08514404514404517, 0.9884021384021384],
    [-0.08016335016335019, 0.8885951885951884],
    [-0.07493614493614492, 0.6055539055539056],
    [-0.06981288981288986, 0.18893673893673935],
    [-0.06487971487971489, 0.028066528066528207],
    [-0.059833679833679876, 0.012221562221562454],
    [-0.0547846747846748, 0.00019305019305049242],
    ])


mcrory_data_CaT32_Act_Tau = np.array([
    [-0.04468750000000002, 0.004896385542168674],
    [-0.039687500000000014, 0.00357590361445783],
    [-0.034375000000000044, 0.002882228915662652],
    [-0.030000000000000027, 0.0021153614457831323],
    [-0.02468750000000003, 0.0016626506024096377],
    [-0.019687500000000024, 0.001414457831325303],
    [-0.01468750000000002, 0.001202409638554218],
    [-0.009687500000000043, 0.0011228915662650583],
    [-0.004687500000000011, 0.0010313253012048194],
    [0.00015624999999999667, 0.001011897590361445],
    ])

mcrory_data_CaT32_Inact_Tau = np.array([
    [-0.05014199268384409, 0.057808002188009244],
    [-0.045261706419300135, 0.04223142756207901],
    [-0.04009680801358395, 0.02677621907442651],
    [-0.03509999886041196, 0.02212020375836171],
    [-0.030111451721348048, 0.02094414878462922],
    [-0.02498102585725534, 0.020008774828776887],
    ])

alpha = 160.e3 * (v + 0.112) / (np.exp((v + 0.112)/0.011) - 1)
beta = 8500*np.exp(v/0.0125)
CaT32_mtau = 1/(alpha+beta) + 0.0009

mvhalfCaT32 = -43.15e-3
mkCaT32 = -5.34e-3

CaT32_minf = 1. / ( 1. + np.exp((v - mvhalfCaT32)/mkCaT32))


CaT32_htau = 22.25e-3 + 0.0455e-3 * np.exp(-v/7.46e-3)


hvhalfCaT32 = -79e-3
hkCaT32 = 2.76e-3
CaT32_hinf = 1. / (1. + np.exp((v-hvhalfCaT32)/hkCaT32))

f,axs = plt.subplots(1,2)
axs[0].plot(v,CaT32_minf)
axs[0].plot(v,CaT32_hinf)
axs[1].plot(v,CaT32_mtau)
axs[1].plot(v,CaT32_htau)

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
def alphabetafunction(X,ssx,taux):
    #sigmoid form only:
    arate,avslope,brate,bvhalf,bvslope,=X
    avhalf= 0
    aB = 0
    aC=0
    bB=brate/bvhalf
    bC=-1
    taumin=0
    ## General Form:
    v = np.linspace(-100e-3,50e-3,100)
    alpha = (arate + aB * v) / (aC + np.exp((v + avhalf) / avslope))
    beta = (brate + bB * v) / (bC + np.exp((v + bvhalf) / bvslope))
    tau = taumin + (1.0/(alpha+beta))
    tau = np.interp(taux,v,tau)
    ss = alpha/(alpha+beta)
    ss = ss**3
    ss = np.interp(ssx,v,ss)
    return alpha, beta, tau,ss

def sigmoid(x,xmin,xmax,xvhalf,xslope):
    return xmin+xmax/(1+np.exp((x-xvhalf)/xslope))

def tauinfminfunction(X,ssx,taux,power,qfactor):
    T_min, T_vdep, T_vhalf, T_vslope, SS_vhalf, SS_vslope, = X 
    SS_min = 0
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
    tauerror = (tau-taufit)/np.max(taufit)
    sserror=(ss-ssfit)/np.max(ssfit)
    taurms = np.sqrt(np.mean(tauerror**2))
    ssrms = np.sqrt(np.mean(sserror**2))
    error=2*taurms+ssrms
    return error

### Parameter boundaries for fitting function:
minbound = (0,10000)
vdep_bound = (0,10000)
vhalf_bound = (-200e-3,100e-3)
vslope_bound = (-100,100)
bounds = [minbound,vdep_bound, vhalf_bound, vslope_bound,vhalf_bound,vslope_bound]

ratebound=(-20000000,200000000.)
bbound=(-20000000000,20000000000)
vhalfbound=(-30000,30000)
vslopebound=(-20000,20000)

#bounds=[ratebound,vslopebound,ratebound,vhalfbound,vslopebound]

#v = v_CaT32Taus = np.linspace(-50e-3,0e-3,50)
### Fitting Function, passing yInf/yTau equations to fit yGate:
resX=scipy.optimize.differential_evolution(fit,bounds,args=(mcrory_data_CaT32_Act_SS,mcrory_data_CaT32_Act_Tau,3,1),tol=1e-35,maxiter=2000,workers=12,popsize=12)#,mutation=1.9,seed=12,popsize=60,recombination=0.2)
#%%
# Get best alpha,beta,tau,and ss values using the outcome of fitting procedure:
tau,ss = tauinfminfunction(resX.x,v,v,3,1)

# Compare the fit
plt.figure()
ax = plt.subplot(1,2,1)
plt.plot(mcrory_data_CaT32_Act_SS[:,0],mcrory_data_CaT32_Act_SS[:,1],label='minf',marker = '.')
plt.plot(v,ss,label='minffit')
plt.legend()
ax = plt.subplot(1,2,2)
plt.plot(mcrory_data_CaT32_Act_Tau[:,0], mcrory_data_CaT32_Act_Tau[:,1], label='mtau',marker='.')
plt.plot(v,tau,label='taufit')
plt.legend()

#%%
### Fitting Function, passing xInf/xTau equations to fit xGate:
resY=scipy.optimize.differential_evolution(fit,bounds,args=(mcrory_data_CaT32_Inact_SS,mcrory_data_CaT32_Inact_Tau,1,1),tol=1e-35,maxiter=2000,workers=12,popsize=12)#,mutation=1.9,seed=12,popsize=60,recombination=0.2)
#%%
# Get best alpha,beta,tau,and ss values using the outcome of fitting procedure:
tau,ss = tauinfminfunction(resY.x,v,v,1,1)

# Compare the fit
plt.figure()
ax = plt.subplot(1,2,1)
plt.plot(mcrory_data_CaT32_Inact_SS[:,0],mcrory_data_CaT32_Inact_SS[:,1],label='minf',marker = '.')
plt.plot(v,ss,label='minffit')
plt.legend()
ax = plt.subplot(1,2,2)
plt.plot(mcrory_data_CaT32_Inact_Tau[:,0], mcrory_data_CaT32_Inact_Tau[:,1], label='mtau',marker='.')
plt.plot(v,tau,label='taufit')
plt.legend()


#%%
