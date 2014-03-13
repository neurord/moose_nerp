
def plot_gate_params(chan,plotpow):
    #print "PLOT POWER", plotpow, chan.path,chan.Xpower
    """Plot the gate parameters like m and h of the channel."""
    if chan.Xpower > 0:
        ma = moose.element('%s/gateX' % (chan.path)).tableA
        mb = moose.element('%s/gateX' % (chan.path)).tableB
        if chan.Ypower > 0:
            ha = moose.element('%s/gateY' % (chan.path)).tableA
            hb = moose.element('%s/gateY' % (chan.path)).tableB
        #
        varray=np.linspace(VMIN,VMAX,len(ma))
        subplot(211)
        plt.title(chan.path)
        plt.plot(varray,1e3/mb, label='m ' + chan.path)
        plt.ylabel('tau, ms')
        if chan.Ypower > 0:
            plt.plot(varray,1e3/hb, label='h ' + chan.path)
        plt.legend(loc='best', fontsize=8)
        #
        subplot(212)
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
        plt.show()
    #

    
