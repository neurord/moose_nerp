#ttables.py
#object to associate name of time tables with filename containing data
import numpy as np
import moose 

class TableSet:
    ALL = []

    def __init__(self, tablename, filename):
        self.tablename = tablename
        self.filename = filename
        self.ALL.append(self)

    def create(self):
        path="/input"
        if not moose.exists('/input'):
            moose.Neutral('/input')
        spike_file=np.load(self.filename+'.npz')
        spike_set = spike_file.keys()[0]
        print('creating', self, self.tablename, self.filename, 'AVAILABLE trains: {} ', len(spike_file[spike_set]))
        self.stimtab=[]
        #make dictionary of stimtabs?  With key = tablename?
        for ii,stimtimes in enumerate(spike_file[spike_set]):
            self.stimtab.append(moose.TimeTable('{}/{}_TimTab{}'.format(path, self.tablename, ii)))
            self.stimtab[ii].vector=stimtimes

    @classmethod
    def create_all(cls):
        for obj in cls.ALL:
            obj.create()

#table2 = TableSet('cortical_inputs2', 'cortical_inputs2.npz')
#table2.TableSet.create()
#>>> t.TableSet.create_all()
#creating <t.TableSet object at 0x7feb08695c88> cortical_inputs1 cortical_inputs1.npz
#creating <t.TableSet object at 0x7feb0a12ffd0> cortical_inputs2 cortical_inputs2.npz
