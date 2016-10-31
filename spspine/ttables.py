#ttables.py
#object to associate name of time tables with filename containing data

class TableSet:
    ALL = []

    def __init__(self, tablename, filename):
        self.tablename = tablename
        self.filename = filename
        self.ALL.append(self)

#    def create(self):
#        #table = moose.Table(self.tablename)
#        #table.fill(...)
#        print('creating', self, self.tablename, self.filename)
#
#    @classmethod
#    def create_all(cls):
#        for obj in cls.ALL:
#            obj.create()

#table2 = TableSet('cortical_inputs2', 'cortical_inputs2.npz')

#>>> t.TableSet.create_all()
#creating <t.TableSet object at 0x7feb08695c88> cortical_inputs1 cortical_inputs1.npz
#creating <t.TableSet object at 0x7feb0a12ffd0> cortical_inputs2 cortical_inputs2.npz
