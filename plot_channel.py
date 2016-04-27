import numpy as np
import matplotlib.pyplot as plt
import moose

def plot_gate_params(chan,plotpow, VMIN, VMAX, CAMIN, CAMAX):
    #print "PLOT POWER", plotpow, chan.path,chan.Xpower
    """Plot the gate parameters like m and h of the channel."""
    if chan.Xpower > 0:
        plt.figure()
        if chan.className == 'HHChannel':
            ma = moose.element(chan.path + '/gateX').tableA
            mb = moose.element(chan.path + '/gateX').tableB
            if chan.Ypower > 0:
                ha = moose.element(chan.path + '/gateY').tableA
                hb = moose.element(chan.path + '/gateY').tableB
        #
            varray=np.linspace(VMIN,VMAX,len(ma))
            plt.subplot(211)
            plt.title(chan.path)
            plt.plot(varray,1e3/mb, label='m ' + chan.path)
            plt.ylabel('tau, ms')
            if chan.Ypower > 0:
                plt.plot(varray,1e3/hb, label='h ' + chan.path)
            plt.legend(loc='best', fontsize=8)

            plt.subplot(212)
            if plotpow:
                label = '(ma/mb)**{}'.format(chan.Xpower)
                inf = (ma/mb)**chan.Xpower
            else:
                label = 'ma/mb'
                inf = ma/mb
            plt.plot(varray, inf, label=label)
            plt.axis([-0.12,0.05,0,1])
            if chan.Ypower > 0:
                plt.plot(varray,ha/hb, label='h ' + chan.path)
            plt.legend(loc='best', fontsize=8)
        else:

            ma = moose.element(chan.path + '/gateX').tableA
            mb = moose.element(chan.path + '/gateX').tableB
            ma = np.array(ma)
            mb = np.array(mb)

            plt.subplot(211)

            plt.title(chan.path+'/gateX tau')
            plt.imshow(1e3/mb,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')

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

        plt.show()
