import pymel.core as pm
import inspect

import bdRig.ui.widgets.moduleWidget as moduleWidget

reload(moduleWidget)

import bdRig.utils.mayaDecorators as decorators

reload(decorators)

import _old.bdRig.modules.arm as arm

reload(arm)

from bdRig.utils import ui_utils as utils

reload(utils)


class armWidget(moduleWidget.ModuleAttrWidget):
    def __init__(self, *args, **kargs):
        super(armWidget, self).__init__(*args, **kargs)
        self.rollJntLayout = utils.HorBox()

        self.upRollJnt = utils.SpinBox(label='Upper Roll Jnt')
        self.lowRollJnt = utils.SpinBox(label='Lower Roll Jnt')
        self.rollJntLayout.addWidget(self.upRollJnt)
        self.rollJntLayout.addWidget(self.lowRollJnt)
        self.attrlayout.addLayout(self.rollJntLayout)
        self.createModuleBtn.clicked.connect(self.buildModule)

    @decorators.undoable
    def buildModule(self, *args):
        moduleName = str(self.moduleNameEdit.edit.text())
        upperRollJnt = int(self.upRollJnt.spin.text())
        lowerRollJnt = int(self.lowRollJnt.spin.text())
        if moduleName:
            moduleExists = self.checkForModule(moduleName)
            if not moduleExists:
                newModule = arm.ArmModule(name=moduleName, upperRollJnt=upperRollJnt, lowerRollJnt=lowerRollJnt)
                newModule.createModule()

                self.parentWin.currentCharacter.addModule(newModule)
                self.parentWin.mt_appendModulesList(newModule.name)

                self.parentWin.modulesTree.show()
                self.parentWin.moduleAttributes.deleteLater()
                self.parentWin.moduleAttributes = None
            else:
                pm.warning('There is a module already with this name')
        else:
            pw.warning('No module name was entered')
