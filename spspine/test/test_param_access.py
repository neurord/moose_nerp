from spspine import param_chan
import pytest

def test_param_access():
    "Just test that the accessors work"
    param_chan.ChanDict.Krp
    param_chan.ChanDict.CaT
    param_chan.ChanDict['Krp']
    param_chan.ChanDict['CaT']
    assert 'CaT' in param_chan.ChanDict.keys()
    assert 'Krp' in param_chan.ChanDict.keys()

def test_channel_params_sanity():
    "Just test that the accessors work"
    param_chan.ChanDict.KaF.channel.Xpow
    param_chan.ChanDict.KaF.channel.Ypow
    param_chan.ChanDict.KaF.channel.Zpow
    assert param_chan.ChanDict.KaF.channel.name == 'KaF'
    param_chan.ChanDict.KaF.X
    assert param_chan.ChanDict.KaF.X.A_rate > 0

@pytest.mark.parametrize("channel",
                         param_chan.ChanDict.keys())
def test_channel_params(channel):
    params = param_chan.ChanDict[channel]
    assert params == getattr(param_chan.ChanDict, channel)
    assert params.channel.name == channel
