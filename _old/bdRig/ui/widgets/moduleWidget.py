import bdRig.utils.qt_handlers as qt_handlers

reload(qt_handlers)

from bdRig.utils.qt_handlers import QtCore, QtGui

from bdRig.utils import ui_utils as utils

reload(utils)

import bdRig.system.module as module

reload(module)


class ModuleAttrWidget(QtGui.QWidget):
    def __init__(self, *args, **kargs):
        super(ModuleAttrWidget, self).__init__(*args, **kargs)
        self.parentWin = self.parent()
        self.moduleType = ''
        self.setupUI()

    def setupUI(self):
        mainLayout = QtGui.QVBoxLayout()
        self.attrlayout = utils.VertBox()

        self.moduleNameEdit = utils.LabelEdit(label='Module Name:')

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.HLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)

        self.createModuleBtn = QtGui.QPushButton('Create')

        self.attrlayout.addWidget(self.moduleNameEdit)

        mainLayout.addLayout(self.attrlayout)
        mainLayout.addWidget(separator)
        mainLayout.addWidget(self.createModuleBtn)

        # self.createModuleBtn.clicked.connect(self.createModule)
        self.setLayout(mainLayout)

    def setDefaultName(self, defaultName):
        self.moduleNameEdit.edit.setText(defaultName.capitalize())

    def checkForModule(self, moduleName):
        for mod in self.parentWin.currentCharacter.characterModulesInfo:
            if moduleName == mod['name'].replace('_module', ''):
                return 1

        return 0

    def closeEvent(self, event):
        event.accept()  # let the window close
