import moose
import inject_func
import cell_proto
import neuron_graph

import pytest

@pytest.yield_fixture
def remove_objects():
    print ("setup before yield")
    yield
    print ("teardown after yield")
    for i in ('/data', '/pulse', '/D1', '/D2', '/library'):
        try:
            moose.delete(i)
        except ValueError:
            pass

@pytest.mark.parametrize("calcium", ["", "calcium"])
@pytest.mark.parametrize("synapses", ["", "synapses"])
@pytest.mark.parametrize("spines", ["", "spines"])
@pytest.mark.parametrize("ghk", ["", "ghk"])
def test_single_injection(calcium, synapses, spines, ghk, remove_objects):
    "Create the neuron and run a very short simulation"

    if ghk and not hasattr(moose, 'GHK'):
        pytest.xfail("GHK is missing")

    MSNsyn,neuron,capools,synarray,spineHeads = \
        cell_proto.neuronclasses(False, False, calcium, synapses, spines, ghk)

    pg = inject_func.setupinj(0.02, 0.01, neuron)
    pg.firstLevel = 1e-8

    data = moose.Neutral('/data')

    vmtab,catab,plastab,currtab = \
        neuron_graph.graphtables(neuron, False, 'getGk', capools, {}, {})

    moose.reinit()
    moose.start(0.05)

    vm1 = vmtab[0][0].vector
    vm2 = vmtab[1][0].vector

    # Quick sanity check that the values are not outlandish.
    # We do not check at the beginning because of the initial fluctuation.
    assert 0.15 < vm1[250] < 0.25
    assert 0.15 < vm2[250] < 0.25
    assert 0.00 < vm1[499] < 0.05
    assert 0.00 < vm2[499] < 0.05
