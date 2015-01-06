import numpy as np
import matplotlib.pyplot as plt
import moose

def plot_gate_params(chan,plotpow, VMIN, VMAX, CAMIN, CAMAX):
    #print "PLOT POWER", plotpow, chan.path,chan.Xpower
    """Plot the gate parameters like m and h of the channel."""
    if chan.Xpower > 0:
        plt.figure()
        if chan.className == 'HHChannel':
            ma = moose.element('%s/gateX' % (chan.path)).tableA
            mb = moose.element('%s/gateX' % (chan.path)).tableB
            if chan.Ypower > 0:
                ha = moose.element('%s/gateY' % (chan.path)).tableA
                hb = moose.element('%s/gateY' % (chan.path)).tableB
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
                "INF RAISED TO POWER", chan.path,chan.Xpower
                inf=(ma/mb)**chan.Xpower
            else:
                inf=(ma/mb)
            plt.plot(varray,inf, label='m ' + chan.path)
            plt.axis([-0.12,0.05,0,1])
            if chan.Ypower > 0:
                plt.plot(varray,ha/hb, label='h ' + chan.path)
                plt.legend(loc='best', fontsize=8)
        else:
            
            ma = moose.element('%s/gateX/tableA' % (chan.path))
            mb = moose.element('%s/gateX/tableB' % (chan.path))

            plt.subplot(211)
            
            plt.title(chan.path+'/gateX tau')
            new_ma = np.array(ma.tableVector2D)
            new_mb = np.array(mb.tableVector2D)
            plt.imshow(1e3/new_mb,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')
          
            plt.colorbar()
            plt.subplot(212)
            if plotpow:
                inf = (new_ma/new_mb)**chan.Xpower
                "INF RAISED TO POWER", chan.path,chan.Xpower

            else:
                inf = new_ma/new_mb

            plt.imshow(inf,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')
            plt.xlabel('Ca [nM]')
            plt.ylabel('Vm [V]')
            plt.colorbar()
            if chan.Ypower > 0:
                ha = moose.element('%s/gateY/tableA' % (chan.path))
                hb = moose.element('%s/gateY/tableB' % (chan.path))
                plt.figure()
                plt.subplot(211)
                plt.title(chan.path+'/gateY tau')
                new_ha = np.array(ha.tableVector2D)
                new_hb = np.array(hb.tableVector2D)
                plt.imshow(1e3/new_hb,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')

                plt.colorbar()
                plt.subplot(212)
                if plotpow:
                    inf = (new_ha/new_hb)**chan.Ypower
                else:
                    inf = new_ha/new_hb

                plt.imshow(inf,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto')
                plt.xlabel('Ca [nM]')
                plt.ylabel('Vm [V]')
                plt.colorbar()
                
        plt.show()
    #

    
