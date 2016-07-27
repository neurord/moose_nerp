from spspine import param_chan, util
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

def test_distance_mapping():
    near = (0, 20)
    far = (20, 30)
    map = {near:5, far:6}

    assert util.distance_mapping(map,  0) == 5
    assert util.distance_mapping(map, 10) == 5
    assert util.distance_mapping(map, 20) == 6
    assert util.distance_mapping(map, 25) == 6
    assert util.distance_mapping(map, 30) == 0
    assert util.distance_mapping(map, 35) == 0
