from moose_nerp.prototypes import (create_model_sim,
                                   util,
                                   net_sim_graph)
from moose_nerp.graph import net_graph, neuron_graph, spine_graph

def sim_plot(model,net,connections,population,pg=None):
    traces, names = [], []
    for inj in model.param_sim.injection_current:
        print('ready to simulation with', inj)
        if pg is None:
            create_model_sim.runOneSim(model, simtime=model.param_sim.simtime, injection_current=inj)
        else:
            pg.firstLevel = inj
            create_model_sim.runOneSim(model, simtime=model.param_sim.simtime)
        if net.single and len(model.vmtab):
            for neurnum,neurtype in enumerate(model.neurons.keys()):
                traces.append(model.vmtab[neurtype][0].vector)
                names.append('{} @ {}'.format(neurtype, inj))
            if model.synYN:
                net_graph.syn_graph(connections, model.syntab, model.param_sim)
                if model.stpYN and len(model.stp_tab):
                    net_graph.syn_graph(connections, model.stp_tab,model.param_sim,graph_title='short term plasticity')
            if model.spineYN:
                spine_graph.spineFig(model,model.spinecatab,model.spinevmtab, model.param_sim.simtime)
        else:
            if net.plot_netvm:
                net_graph.graphs(population['pop'], model.param_sim.simtime, model.vmtab,model.catab,model.plastab)
            if model.synYN and model.param_sim.plot_synapse:
                net_graph.syn_graph(connections, model.syntab, model.param_sim)
                if model.stpYN and len(model.stp_tab):
                    net_graph.syn_graph(connections, model.stp_tab,model.param_sim,graph_title='stp',factor=1)
            #net_output.writeOutput(model, net.outfile,model.spiketab,model.vmtab,population)

    if net.single:
        neuron_graph.SingleGraphSet(traces, names, model.param_sim.simtime)
        # block in non-interactive mode
    util.block_if_noninteractive()
    return
