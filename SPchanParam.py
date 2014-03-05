#chanDictSP.py
#contains all gating parameters and reversal potentials
# Gate equations have the form:
#
# y(x) = (rate + B * x) / (C + exp((x + vhalf) / vslope))
#
# OR
# y(x) = tau_min + tau_vdep / (1 + exp((x + vhalf) / vslope))
# 
# where x is membrane voltage and y is the rate constant
#KDr params used by Sriram, RE paper1, Krp params used by RE paper 2
krev=-87e-3
narev=50e-3
carev=48e-3 #assumes CaExt=2 mM and CaIn=50e-3 
ZpowCDI=2

#mtau: Ogata fig 5, no qfactor accounted in mtau, 1.2 will improve spike shape
#activation minf fits Ogata 1990 figure 3C (which is cubed root)
#inactivation hinf fits Ogata 1990 figure 6B
#htau fits the main -50 through -10 slope of Ogata figure 9 (log tau), but a qfact of 2 is already taken into account.

qfactNaF=1.3
Na_m_params = {'Arate':1.0,               
                'A_B':0.0,                
                'A_C':1.0,                
                'Avhalf':25e-3,           
               'Avslope':-10e-3,          
                'taumin':0.1e-3,          
                'tauVdep':1.45e-3,        
                'tauPow':2,               
                'tauVhalf':62e-3,           
                'tauVslope':8e-3            
               }
Na_h_params = { 'Arate':1.0,           
                'A_B':0.0,             
                'A_C':1.0,             
                'Avhalf':60e-3,        
                'Avslope':6e-3,        
                'taumin':0.2754e-3,    
                'tauVdep':1.2e-3,      
                'tauPow':1,            
                'tauVhalf':42e-3,        
                'tauVslope':3e-3         
                } 
NaFparam={'Xpow':3, 'Ypow':1, 'Zpow':0, 'Erev':narev,'name': 'NaF'}

#This is from Migliore.  
KDrparam={'Xpow':1, 'Ypow':0, 'Zpow':0, 'Erev':krev, 'name': 'KDr'}
KDr_X_params = [28.2,                       # 'A_rate':
                0,                          # 'A_B':
                0.0,                        # 'A_C':
                0,                          # 'Avhalf':
                -12.5e-3,                   # 'A_vslope':
                6.78,                       # 'B_rate':
                0.0,                        # 'B_B':
                0.0,                        # 'B_C':
                0.0,                        # 'Bvhalf':
                33.5e-3                     # 'B_vslope':    
               ]
KDr_Y_params = []

Krpparam={'Xpow':2, 'Ypow':1, 'Zpow':0, 'Erev':krev, 'name': 'Krp'}
#Act tuned to fit Nisenbaum 1996 fig6C (minf^2) and fig 8C (mtau)
qfactKrp=3  #Used by RE
Krp_X_params = [16*qfactKrp,               # 'A_rate':
                0,                         # 'A_B':
                0.0,                       # 'A_C':
                0,                         # 'Avhalf':
                -24e-3,                     # 'A_vslope':
                2.4*qfactKrp,               # 'B_rate':
                0.0,                        # 'B_B':
                0.0,                        # 'B_C':
                0.0,                        # 'Bvhalf':
                45e-3                       # 'B_vslope':    
                ]
# tuned to fit Nisenbaum 1996 fig 9D (hinf, 87% inactivating) and 9B (htau)
Krp_Y_params = [0.01*qfactKrp,             # 'A_rate':
                0,                         # 'A_B':
                0.0,                       # 'A_C':
                0,                         # 'Avhalf':
                100e-3,                    # 'A_vslope':
                0.4*qfactKrp,              # 'B_rate':
                0.0,                        # 'B_B':
                0.0,                        # 'B_C':
                0.0,                        # 'Bvhalf':
                -18e-3                      # 'B_vslope':    
               ]

Kirparam={'Xpow':1, 'Ypow':0, 'Zpow':0, 'Erev':krev, 'name': 'Kir'}
qfactKir=3
Kir_X_params = [0.01*qfactKir,             # 'A_rate':
                0,                         # 'A_B':
                0.0,                       # 'A_C':
                0,                         # 'Avhalf':
                11e-3,                     # 'A_vslope':
                1.2e3*qfactKir,            # 'B_rate':
                0.0,                        # 'B_B':
                1.0,                        # 'B_C':
                -30e-3,                     # 'Bvhalf':
                -50e-3                      # 'B_vslope':    
               ]

KaFparam={'Xpow':2, 'Ypow':1, 'Zpow':0, 'Erev':krev,'name':'KaF'}
#ativation constants for alphas and betas (obtained by matching m2 to Tkatch et al., 2000 Figs 2c, and mtau to fig 2b)
qfactKaF=1.5
KaF_X_params = [1.8e3*qfactKaF,            # 'A_rate':
                0,                         # 'A_B':
                1.0,                       # 'A_C':
                18e-3,                     # 'Avhalf':
                -13.0e-3,                   # 'A_vslope':
                0.45e3*qfactKaF,            # 'B_rate':
                0.0,                        # 'B_B':
                1.0,                        # 'B_C':
                -2.0e-3,                      # 'Bvhalf':
                11.0e-3                       # 'B_vslope':    
               ]
#inactivation consts for alphas and betas obtained by matching Tkatch et al., 2000 Fig 3b, 
#and tau voltage dependence consistent with their value for V=0 in fig 3c.
#slowing down inact improves spike shape tremendously
KaF_Y_params = [0.105e3/qfactKaF,          # 'A_rate':
                0,                        # 'A_B':
                1.0,                       # 'A_C':
                121e-3,                    # 'Avhalf':
                22.0e-3,                    # 'A_vslope':
                0.065e3/qfactKaF,           # 'B_rate':
                0.0,                        # 'B_B':
                1.0,                        # 'B_C':
                55.0e-3,                    # 'Bvhalf':
                -11.0e-3                     # 'B_vslope':    
               ]

KaSparam={'Xpow':2, 'Ypow':1, 'Zpow':0, 'Erev':krev,'name':'KaS'}
qfactKaS=2
KaS_X_params = [250*qfactKaS,              # 'A_rate':
                0,                         # 'A_B':
                1.0,                       # 'A_C':
                -54e-3,                    # 'Avhalf':
                -22.0e-3,                   # 'A_vslope':
                50*qfactKaS,                # 'B_rate':
                0.0,                        # 'B_B':
                1.0,                        # 'B_C':
                100e-3,                     # 'Bvhalf':
                35e-3                       # 'B_vslope':    
               ]
KaS_Y_params = [2.5*qfactKaS,              # 'A_rate':
                0,                         # 'A_B':
                1.0,                       # 'A_C':
                95e-3,                     # 'Avhalf':
                16.0e-3,                   # 'A_vslope':
                2.0*qfactKaS,              # 'B_rate':
                0.0,                        # 'B_B':
                1.0,                        # 'B_C':
                -50.0e-3,                   # 'Bvhalf':
                -70.0e-3                    # 'B_vslope':    
               ]

#SS values from Churchill and MacVicar, assuming Xpow = 1
##time constants extrapolated from scarce measurements - Song & Surmeier 
#SS values measured by Kasai and Neher are quite similar, except
#they use Xpow=2 to fit, thus params would be different
#they have nice time constant measurements which are ~2x slower than above
#but they measured at room temp, so qfact=1 on S&S and qfact=2 on K&N would equate them
#Vdep inact by Kasai ~10% and very slow (>50 ms). For now, have no Vdep inact.
# CDI measured by Kasai
#Note that CaL13 for D1 has mvhalf 10 mV more negative than for D2
#CaL12 does not differ between D1 and D2.
CaL12param={'Xpow':1, 'Ypow':0, 'Zpow':ZpowCDI, 'Erev':carev,'name':'CaL12'}
qfactCaL=1
CaL12_X_params = [-880*qfactCaL,           # 'A_rate':
                -220e3*qfactCaL,           # 'A_B':
                -1.0,                       # 'A_C':
                4.00003e-3,                 # 'Avhalf':
                -7.5e-3,                    # 'A_vslope':
                -284*qfactCaL,              # 'B_rate':
                71e3*qfactCaL,              # 'B_B':
                -1.0,                        # 'B_C':
                -4.00003e-3,                 # 'Bvhalf':
                5e-3                         # 'B_vslope':    
               ]
# Using Xpow=1 produced too high a basal calcium, 
# so used Xpow=2 and retuned params - much better basal calcium
CaL13param={'Xpow':2, 'Ypow':0, 'Zpow':ZpowCDI, 'Erev':carev,'name':'CaL13'}
CaL13_X_params = [1500*qfactCaL,                     # 'A_rate':
                   0,                       # 'A_B':
                 1.0,                       # 'A_C':
                 -5.0e-3,                   # 'Avhalf':
                -25.0e-3,                   # 'A_vslope':
                 2000*qfactCaL,             # 'B_rate':
                  0,                        # 'B_B':
                1.0,                        # 'B_C':
                52e-3,                      # 'Bvhalf':
                6.5e-3                       # 'B_vslope':    
               ]
#Params from McRory J Biol Chem, alpha1I subunit
CaTparam={'Xpow':3, 'Ypow':1, 'Zpow':ZpowCDI, 'Erev':carev,'name':'CaT'}
qfactCaT=2
CaT_X_params = [ 1000*qfactCaT,             # 'A_rate':
                  0.0,                      # 'A_B':
                  0.0,                      # 'A_C':
                  0.0,                      # 'Avhalf':
                 -19e-3,                    # 'A_vslope':
                 1340*qfactCaT,             # 'B_rate':
                16500*qfactCaT,             # 'B_B':
                -1.0,                       # 'B_C':
                81e-3,                      # 'Bvhalf':
               7.12e-3                      # 'B_vslope':    
               ]
#Original inactivation ws too slow compared to activation, made closder the alpha1G
CaT_Y_params = [ 3840*qfactCaT,             # 'A_rate':
                34000*qfactCaT,             # 'A_B':
                -1.0,                       # 'A_C':
                 113.0e-3,                  # 'Avhalf':
                 5.12e-3,                   # 'A_vslope':
                 320*qfactCaT,              # 'B_rate':
                  0,                        # 'B_B':
                0.0,                        # 'B_C':
                0.0,                        # 'Bvhalf':
               -17e-3                        # 'B_vslope':    
               ]

# CaN SS parameters tuned so m2 fits Bargas and Surmeier 1994 boltzmann curve
# CaN tau from kasai 1992.
# Kasai measures calcium dependent inactivation
#McNaughton has act and inact, tau and ss for human CaN
CaNparam={'Xpow':2, 'Ypow':0, 'Zpow':ZpowCDI, 'Erev':carev,'name':'CaN'}
qfactCaN=2
CaN_X_params = [ 304.2*qfactCaN,            # 'A_rate':
                   0,                       # 'A_B':
                 0.0,                       # 'A_C':
                 0.0,                       # 'Avhalf':
                -14.0e-3,                   # 'A_vslope':
                  749*qfactCaN,             # 'B_rate':
                52800*qfactCaN,             # 'B_B':
                -1.0,                        # 'B_C':
               14.2e-3,                      # 'Bvhalf':
                10e-3                        # 'B_vslope':    
               ]

# CaR SS (Act and Inact) parameters from Foerhing et al., 2000
# Was Xpow=3 taken into account during fit?
# CaR tau from a few measurements from pyramidal neurons by Foerhing
# CaR inact tau from Brevi 2001
#Inact params are a bit too steep for ss, and not steep enough for tau
CaRparam={'Xpow':3, 'Ypow':1, 'Zpow':ZpowCDI, 'Erev':carev,'name':'CaN'}
qfactCaR=2
CaR_X_params = [ 240*qfactCaR,              # 'A_rate':
                   0,                       # 'A_B':
                 0.0,                       # 'A_C':
                 0.0,                       # 'Avhalf':
                -28.0e-3,                   # 'A_vslope':
                1.26e6*qfactCaR,            # 'B_rate':
                8e6*qfactCaR,               # 'B_B':
                -1.0,                        # 'B_C':
               158e-3,                       # 'Bvhalf':
                13.6e-3                      # 'B_vslope':    
               ]
CaR_Y_params = [ 1100*qfactCaR,             # 'A_rate':
                 10000*qfactCaR,            # 'A_B':
                 -1.0,                      # 'A_C':
                 0.11,                      # 'Avhalf':
                17e-3,                      # 'A_vslope':
                 20*qfactCaR,               # 'B_rate':
                  0,                        # 'B_B':
                0.0,                        # 'B_C':
                0.0,                        # 'Bvhalf':
                -30.0e-3                     # 'B_vslope':    
               ]
#Reference: Maylie Bond Herson Lee Adelman 2004, Fig 2 steady state
#Fast component has tau~4 ms; not used: slow tau = 70 ms 
#Fast component, tau=4.9ms from Hirschberg et al., 1998 figure 13.
SKparam={'Xpow':0, 'Ypow':0, 'Zpow':1, 'Erev':krev,'name':'SKCa'}
SK_Z_params = [ 0.57e-3,           #Kd
                5.2,               #power
                4.9e-3             #tau
                ]

BKparam={'Xpow': 1, 'Ypow':0,'Zpow':0, 'Erev':krev,'name':'BKCa'}
BK_X_params=[480,0.18,-0.84,280,0.011,-1.0]
#These CDI params can be used with every channel, make ZpowCDI=2
#If ZpowCDI=0 the CDI will not be used, power=-4 is to transform
#(Ca/Kd)^pow/(1+(Ca/Kd)^pow) to 1/(1+(ca/Kd)^-pow) 
CDI_Z_params = [ 0.12e-3,           #Kd
                 -4,               #power
                142e-3             #tau
                ]
#
#Dictionary of "standard" channels, to create channels using a loop
#NaF doesn't fit since it uses different prototype form
#will need separate dictionary for BK
XChanDict={'Krp':Krp_X_params,
           'KaF':KaF_X_params, 
           'KaS':KaS_X_params, 
           'Kir': Kir_X_params, 
           'CaL12': CaL12_X_params, 
           'CaL13': CaL13_X_params, 
           'CaN': CaN_X_params, 
           'CaR': CaR_X_params,
           'CaT': CaT_X_params,
           'SKCa': []}
#
YChanDict={'Krp':Krp_Y_params,
           'KaF':KaF_Y_params, 
           'KaS':KaS_Y_params, 
           'Kir': [], 
           'CaL12': [], 
           'CaL13': [], 
           'CaN': [], 
           'CaR': CaR_Y_params,
           'CaT': CaT_Y_params,
           'SKCa': []}
#
ZChanDict={'SKCa':SK_Z_params,
           'CaL12': CDI_Z_params, 
           'CaL13': CDI_Z_params, 
           'CaN': CDI_Z_params,
           'CaR': CDI_Z_params,
           'CaT': CDI_Z_params
           }
#
ChanDict={'Krp':Krpparam,
          'KaF':KaFparam, 
          'KaS':KaSparam, 
          'Kir': Kirparam, 
          'CaL12': CaL12param, 
          'CaL13': CaL13param, 
          'CaN': CaNparam, 
          'CaR': CaRparam, 
          'CaT': CaTparam,
          'SKCa': SKparam
          }

