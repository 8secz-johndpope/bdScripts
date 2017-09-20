import pymel.core as pm

import bdRig.system.module as module

reload(module)

import bdRig.ui.moduleUI as moduleUI

reload(moduleUI)

import bdRig.utils.mayaDecorators as decorators

reload(decorators)


# moduleWin = 'moduleWindow'

class SingleModule(module.Module):
    def __init__(self, *args, **kargs):
        super(SingleModule, self).__init__(*args, **kargs)
        self.nJnt = 1
        self.moduleType = 'single'
        print self.name
        self.moduleGuidesData = {0: {'name': self.name + 'Guide', 'pos': [0, 0, 0], 'orient': 0}}

    @decorators.undoable
    def createModule(self):
        self.createGroups()
        self.createGuides()
        pm.select(cl=1)
