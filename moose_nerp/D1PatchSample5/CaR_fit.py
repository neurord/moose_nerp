#%%
from matplotlib import pyplot as plt 
import numpy as np 
#%%
## Lindroos model:

v = np.linspace(-100e-3,60e-3)

lind_minf = 1/(1+np.exp((v-(-29e-3))/(-9.6e-3)))
lind_minf = lind_minf**3
lind_mtau = 5.1e-3*3*np.ones(v.shape)
lind_hinf = 1/(1+np.exp((v-(-33.3e-3))/17e-3))
lind_htau = 22e-3+80e-3/(1+np.exp((v-(-19e-3))/5e-3))

f,axes = plt.subplots(2,1)
for y in [lind_minf,lind_hinf]:
    axes[0].plot(v,y)
for y in [lind_mtau, lind_htau]:
    axes[1].plot(v,y)
    
## Our model:



#%%
