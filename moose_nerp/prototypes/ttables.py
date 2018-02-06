#ttables.py
#object to associate name of time tables with filename containing data
import numpy as np
import moose 

class TableSet(object):
    ALL = []

    def __init__(self, tablename, filename, syn_per_tt):
        self.tablename = tablename
        self.filename = filename
        self.syn_per_tt=syn_per_tt
        self.numtt=int(0)
        self.needed=int(0)
        self.ALL.append(self)

    def create(self):
        path="/input"
        if not moose.exists('/input'):
            moose.Neutral('/input')
        spike_file = np.load(self.filename+'.npz', encoding='latin1')
        spike_times = spike_file['spikeTime']
        self.numtt = len(spike_times)
        print('creating', self, self.tablename, self.filename, 'AVAILABLE trains: ', self.numtt)
        self.stimtab=[]
        for ii,stimtimes in enumerate(spike_times):
            self.stimtab.append([moose.TimeTable('{}/{}_TimTab{}'.format(path, self.tablename, ii)),self.syn_per_tt])
            self.stimtab[ii][0].vector=stimtimes

    @classmethod
    def create_all(cls):
        for obj in cls.ALL:
            obj.create()

