import moose
from moose_nerp.prototypes import (cell_proto,
                     create_network,
                     inject_func,
                     tables)
from moose_nerp import (d1d2, str_net)

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

    MSNsyn, neurons = cell_proto.neuronclasses(d1d2)
    neuron_paths = {ntype:[neuron.path]
                    for ntype, neuron in neurons.items()}
    pg = inject_func.setupinj(d1d2, 0.02, 0.01, neuron_paths)
    pg.firstLevel = 1e-8

    data = moose.Neutral('/data')

    vmtab, catab, plastab, currtab = tables.graphtables(d1d2, neurons, False, 'getGk')

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
    str_net.single = bool(single)

    MSNsyn, neurons = cell_proto.neuronclasses(d1d2)

    population,connection, plas = create_network.create_network(d1d2, str_net, neurons)

    pg = inject_func.setupinj(d1d2, 0.02, 0.01, population['pop'])
    pg.firstLevel = 1e-9

    data = moose.Neutral('/data')

    vmtab, catab, plastab, currtab = tables.graphtables(d1d2, neurons, False, 'getGk')

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
