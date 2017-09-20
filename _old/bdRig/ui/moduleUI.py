# import shiboken
import inspect

import bdRig.utils.qt_handlers
from bdRig.utils.qt_handlers import QtCore, QtGui

import pymel.core as pm
import maya.OpenMayaUI

import bdRig.utils.ui_utils as utils

reload(utils)

import bdRig.system.module as module

reload(module)

import json

moduleWin = 'moduleWindow'


class ModuleUI(QtGui.QMainWindow):
    def __init__(self, parent=None, title='Create New Module', moduleName=''):
        super(ModuleUI, self).__init__(parent)
        self.yartWindow = parent

        self.moduleName = moduleName
        self.setObjectName(moduleWin)
        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setupUI()
        self.show()
        self.resize(300, 300)

    def setupUI(self):
        centralWidget = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()
        self.attrlayout = QtGui.QVBoxLayout()

        self.box = utils.TitledBox(title='Attributes', settings=1)

        self.moduleNameEdit = utils.LabelEdit(label='Module Name:')
        self.moduleNameEdit.edit.setText(self.moduleName.capitalize())

        self.jointNumberWidget = QtGui.QWidget()
        self.jointNumberLayout = QtGui.QHBoxLayout()
        self.jointNumberLayout.setContentsMargins(10, 0, 10, 0)
        jointNumberLabel = QtGui.QLabel('Joint Number: ')
        self.jointNumberSpin = QtGui.QSpinBox()
        self.jointNumberSpin.setMinimum(1)
        self.jointNumberLayout.addWidget(jointNumberLabel)
        self.jointNumberLayout.addWidget(self.jointNumberSpin)
        self.jointNumberWidget.setLayout(self.jointNumberLayout)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.HLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)

        createModuleBtn = QtGui.QPushButton('Create')

        # self.attrlayout.addLayout(templateNameLayout)
        self.attrlayout.addWidget(self.moduleNameEdit)
        self.attrlayout.addWidget(self.jointNumberWidget)
        self.box.groupBoxLayout.addLayout(self.attrlayout)

        self.box.groupBoxLayout.addWidget(separator)
        self.box.groupBoxLayout.addWidget(createModuleBtn)

        mainLayout.addWidget(self.box)

        createModuleBtn.clicked.connect(self.createModule)
        centralWidget.setLayout(mainLayout)

        self.setCentralWidget(centralWidget)

    def createModule(self):
        moduleName = str(self.moduleNameEdit.edit.text())
        moduleNumJnt = self.jointNumberSpin.value()

        if moduleName:
            moduleExists = self.checkForModule(moduleName)
            if not moduleExists:
                toImport = 'bdRig.modules.' + self.moduleName
                print toImport
                try:
                    mod = __import__(toImport, {}, {}, [moduleName])
                    reload(mod)
                    print 'adsadsadasdsad', mod
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj):
                            baseclass = obj.__bases__[0].__name__
                            if baseclass.lower() == 'module':
                                newModule = obj(name=moduleName)
                                newModule.createModule()
                                self.yartWindow.currentCharacter.addModule(newModule)
                                self.yartWindow.mt_appendModulesList(newModule.name)
                                if pm.window(moduleWin, exists=True, q=True):
                                    pm.deleteUI(moduleWin)
                except:
                    pm.warning("There was an error trying to load module %s" % mod)

            else:
                pm.warning('Module "%s" exists already' % moduleName)

        print self.yartWindow.currentCharacter.modulesList

    def checkForModule(self, moduleName):
        for mod in self.yartWindow.currentCharacter.modulesList:
            if moduleName == mod['name'].replace('_module', ''):
                return 1

        return 0

    def closeEvent(self, event):
        event.accept()  # let the window close


def createUI():
    if pm.window(moduleWin, exists=True, q=True):
        pm.deleteUI(moduleWin)

    ModuleUI()
