import numpy as np
import matplotlib.pyplot as plt
#from spspine import chan_proto
import moose

def plot_gate_params(chan,plotpow, VMIN, VMAX, CAMIN, CAMAX):
    #print "PLOT POWER", plotpow, chan.path,chan.Xpower
    """Plot the gate parameters like m and h of the channel."""
    if chan.className == 'HHChannel':
        #f = plt.figure()
        cols=1
        #n=range(0,2,1)
        rows=2
        fig,axes=plt.subplots(rows,cols,sharex=True)
        plt.title(chan.path)
        if chan.Xpower > 0:
            ma = moose.element(chan.path + '/gateX').tableA
            mb = moose.element(chan.path + '/gateX').tableB
            varray = np.linspace(VMIN, VMAX, len(ma))
            axes[0].plot(varray, 1e3 / mb, label='m ' + chan.path)
            if plotpow:
                label = '(minf)**{}'.format(chan.Xpower)
                inf = (ma / mb) ** chan.Xpower
            else:
                label = 'minf'
                inf = ma / mb
            axes[1].plot(varray, inf, label=label)
            axes[1].axis([-0.12, 0.05, 0, 1])
        if chan.Ypower > 0:
                ha = moose.element(chan.path + '/gateY').tableA
                hb = moose.element(chan.path + '/gateY').tableB
                varray = np.linspace(VMIN, VMAX, len(ha))
                axes[0].plot(varray, 1e3 / hb, label='h ' + chan.path)
                axes[1].plot(varray, ha / hb, label='hinf ' + chan.path)
                axes[1].axis([-0.12, 0.05, 0, 1])
        #
        if chan.Zpower>0:
            za = moose.element(chan.path + '/gateZ').tableA
            zb = moose.element(chan.path + '/gateZ').tableB
            if chan.useConcentration == True:
                carray=np.linspace(CAMIN,CAMAX,len(za))
                axes[0].plot(carray,1e3/zb,label='m ' + chan.path)
                axes[1].plot(carray, za / zb, label='minf' + chan.path)
        #
        #
        axes[1].set_xlabel('voltage')
        axes[0].set_ylabel('tau, ms')
        axes[0].legend(loc='best', fontsize=8)
        axes[1].legend(loc='best', fontsize=8)
    else:  #Must be two-D tab channel

        ma = moose.element(chan.path + '/gateX').tableA
        mb = moose.element(chan.path + '/gateX').tableB
        ma = np.array(ma)
        mb = np.array(mb)



        axes[0].title(chan.path+'/gateX tau')
        axes[0].imshow(1e3/mb,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')

        plt.colorbar()
        plt.subplot(212)
        if plotpow:
            inf = (ma/mb)**chan.Xpower
        else:
            inf = ma/mb

        plt.imshow(inf,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')
        plt.xlabel('Ca [nM]')
        plt.ylabel('Vm [V]')
        plt.colorbar()
        if chan.Ypower > 0:
            ha = moose.element(chan.path + '/gateY').tableA
            hb = moose.element(chan.path + '/gateY').tableB
            ha = np.array(ha)
            hb = np.array(hb)

            plt.figure()
            plt.subplot(211)
            plt.title(chan.path+'/gateY tau')
            plt.imshow(1e3/hb,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')

            plt.colorbar()
            plt.subplot(212)
            if plotpow:
                inf = (ha/hb)**chan.Ypower
            else:
                inf = ha/hb
            plt.imshow(inf,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')
            plt.xlabel('Ca [nM]')
            plt.ylabel('Vm [V]')
            plt.colorbar()
    return fig,axes
