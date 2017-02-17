import moose
from spspine import (cell_proto,
                     create_network,
                     inject_func,
                     tables,
                     d1d2, param_net)

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
@pytest.mark.parametrize("plasticity", ["", "plasticity"])
@pytest.mark.usefixtures("remove_objects")
def test_single_injection(calcium, synapses, spines, ghk, plasticity):
    "Create the neuron and run a very short simulation"

    if ghk and not hasattr(moose, 'GHK'):
        pytest.skip("GHK is missing")

    d1d2.calYN = bool(calcium)
    d1d2.plasYN = bool(plasticity)
    d1d2.ghkYN = bool(ghk)
    d1d2.spineYN = bool(spines)
    d1d2.synYN = bool(synapses)
    d1d2.single = True

    MSNsyn,neuron = \
        cell_proto.neuronclasses(d1d2)

    all_neurons={}
    for ntype in neuron.keys():
        all_neurons[ntype]=list([neuron[ntype].path])
    pg = inject_func.setupinj(d1d2, 0.02, 0.01, all_neurons)
    pg.firstLevel = 1e-8

    data = moose.Neutral('/data')

    vmtab,catab,plastab,currtab = \
        tables.graphtables(d1d2, neuron, False, 'getGk', {})

    moose.reinit()
    moose.start(0.05)

    vm1 = vmtab[0][0].vector
    vm2 = vmtab[1][0].vector

    # Quick sanity check that the values are not outlandish.
    # We do not check at the beginning because of the initial fluctuation.
    exp = (0.174
           - 0.025 * bool(spines)
           - 0.043 * bool(calcium))

    assert exp - 0.01 < vm1[250] < exp + 0.02
    assert exp - 0.01 < vm2[250] < exp + 0.02

    assert -0.01 < vm1[499] < 0.05
    assert -0.01 < vm2[499] < 0.05

@pytest.mark.parametrize("calcium", ["", "calcium"])
@pytest.mark.parametrize("synapses", ["", "synapses"])
@pytest.mark.parametrize("spines", ["", "spines"])
@pytest.mark.parametrize("single", ["", "single"])
@pytest.mark.parametrize("ghk", ["", "ghk"])
@pytest.mark.parametrize("plasticity", ["", "plasticity"])
@pytest.mark.usefixtures("remove_objects")
def test_net_injection(calcium, synapses, spines, single, ghk, plasticity):
    "Create the neuron and run a very short simulation"

    #pytest.skip("skipping network tests")

    if ghk and not hasattr(moose, 'GHK'):
        pytest.skip("GHK is missing")

    if spines and not single:
        pytest.skip("spines are too much with multiple neurons")

    d1d2.calYN = bool(calcium)
    d1d2.plasYN = bool(plasticity)
    d1d2.ghkYN = bool(ghk)
    d1d2.spineYN = bool(spines)
    d1d2.synYN = bool(synapses)
    d1d2.single = bool(single)

    MSNsyn,neuron = cell_proto.neuronclasses(d1d2)

    population,connection, plas = create_network.create_network(d1d2, param_net, neuron)

    pg = inject_func.setupinj(d1d2, 0.02, 0.01, population['pop'])
    pg.firstLevel = 1e-9

    data = moose.Neutral('/data')

    vmtab,catab,plastab,currtab = \
        tables.graphtables(d1d2, neuron, False, 'getGk', {})

    moose.reinit()
    moose.start(0.05)

    vm1 = vmtab[0][0].vector
    vm2 = vmtab[1][0].vector

    # Quick sanity check that the values are not outlandish.
    # We do not check at the beginning because of the initial fluctuation.
    assert -0.01 < vm1[250] < 0.05
    assert -0.01 < vm2[250] < 0.05
    assert -0.01 < vm1[499] < 0.05
    assert -0.01 < vm2[499] < 0.05
    return vm1, vm2
