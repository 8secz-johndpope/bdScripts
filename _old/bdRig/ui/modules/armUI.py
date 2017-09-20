import pymel.core as pm

import bdRig.system.module as module

reload(module)

import bdRig.ui.moduleUI as moduleUI

reload(moduleUI)

from bdRig.utils import ui_utils as utils

reload(utils)

moduleWin = 'moduleWindow'


class Arm_UI(moduleUI.ModuleUI):
    def __init__(self, parent=None, title='', moduleName=''):
        super(Arm_UI, self).__init__(parent, title='Create Arm Module', moduleName='arm')
        self.jointNumberWidget.hide()
        self.appendUI()

    def appendUI(self):
        self.upperRollJnt = utils.LabelEdit(label='Upper Roll Joints')
        self.attrlayout.addWidget(self.upperRollJnt)


def createUI(parent):
    if pm.window(moduleWin, exists=True, q=True):
        pm.deleteUI(moduleWin)
    print parent
    ui = Arm_UI(parent)
