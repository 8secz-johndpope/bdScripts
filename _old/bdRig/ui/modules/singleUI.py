import pymel.core as pm

import bdRig.system.module as module

reload(module)

import bdRig.ui.moduleUI as moduleUI

reload(moduleUI)

moduleWin = 'moduleWindow'


class SingleModule_UI(moduleUI.ModuleUI):
    def __init__(self, parent=None, title='', moduleName=''):
        super(SingleModule_UI, self).__init__(parent, title='Create Single Module', moduleName='single')
        self.jointNumberWidget.hide()


def createUI(parent):
    if pm.window(moduleWin, exists=True, q=True):
        pm.deleteUI(moduleWin)
    ui = SingleModule_UI(parent)
