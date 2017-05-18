import numpy as np
import matplotlib.pyplot as plt
#from spspine import chan_proto
import moose

def plot_gate_params(chan,plotpow, VMIN=-0.1, VMAX=0.05, CAMIN=0, CAMAX=1):
    #print "PLOT POWER", plotpow, chan.path,chan.Xpower
    """Plot the gate parameters like m and h of the channel."""
    if chan.className == 'HHChannel':
        cols=1
        #n=range(0,2,1)
        if chan.Zpower~=0 and chan.Xpower~=0 and chan.Ypower~=0 and chan.useConcentration == True:
            rows=3
        else:
            rows=2
        fig,axes=plt.subplots(rows,cols,sharex=True)
        plt.title(chan.path)
        if chan.Xpower > 0:
            gate=moose.element(chan.path + '/gateX')
            ma = gate.tableA
            mb = gate.tableB
            varray = np.linspace(gate.min, gate.max, len(ma))
            axes[0].plot(varray, 1e3 / mb, label='mtau ' + chan.path)
            if plotpow:
                label = '(minf)**{}'.format(chan.Xpower)
                inf = (ma / mb) ** chan.Xpower
            else:
                label = 'minf'
                inf = ma / mb
            axes[1].plot(varray, inf, label=label)
            axes[1].axis([gate.min, gate.max, 0, 1])
        if chan.Ypower > 0:
            gate=moose.element(chan.path + '/gateY')
            ha = gate.tableA
            hb = gate.tableB
            varray = np.linspace(gate.min, gate.max, len(ha))
            axes[0].plot(varray, 1e3 / hb, label='htau ' + chan.path)
            axes[1].plot(varray, ha / hb, label='hinf ' + chan.path)
            axes[1].axis([gate.min, gate.max, 0, 1])
        #
        if chan.Zpower~=0:
            gate=moose.element(chan.path + '/gateZ')
            za = gate.tableA
            zb = gate.tableB
            xarray=np.linspace(gate.min,gate.max,len(za))
            if (chan.Xpower==0 and chan.Ypower==0) or chan.useConcentration == False:
                axes[0].plot(xarray,1e3/zb,label='ztau ' + chan.path)
                axes[1].plot(xarray, za / zb, label='zinf' + chan.path)
                axnum=1
            else:
                axes[2].plot(xarray,1e3/zb,label='ztau ' + chan.path)
                axes[2].plot(xarray, za / zb, label='zinf' + chan.path)
                axnum=2
        else:
            axnum=1
        if chan.useConcentration == True:
            axes[axnum].set_xlabel('Calcium')
        else:
            axes[axnum].set_xlabel('voltage')
        axes[0].set_ylabel('tau, ms')
        axes[1].set_ylabel('steady state')
        axes[0].legend(loc='best', fontsize=8)
        axes[1].legend(loc='best', fontsize=8)
    else:  #Must be two-D tab channel
        plt.figure()

        ma = moose.element(chan.path + '/gateX').tableA
        mb = moose.element(chan.path + '/gateX').tableB
        ma = np.array(ma)
        mb = np.array(mb)

        plt.subplot(211)

        plt.title(chan.path+'/gateX top: tau (ms), bottom: ss')
        plt.imshow(1e3/mb,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto',origin='lower')
        plt.colorbar()

        plt.subplot(212)
        if plotpow:
            inf = (ma/mb)**chan.Xpower
        else:
            inf = ma/mb

        plt.imshow(inf,extent=[CAMIN,CAMAX,VMIN,VMAX],aspect='auto',origin='lower')
        plt.xlabel('Ca [mM]')
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
    return
