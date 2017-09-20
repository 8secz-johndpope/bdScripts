import pymel.core as pm
import pymel.core.datatypes as dt
import re, os, shutil, glob, sys, inspect

import logging

# import shiboken
import sip
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

import maya.OpenMayaUI

from .. import ui_utils as utils

reload(utils)

from ...system import characterX as character

reload(character)


class ModulesBtntWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ModulesBtntWidget, self).__init__(parent)
        self.buttonsList = []
        self.currentCharacter = None
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        box = utils.TitledBox(title='Create Modules')
        self.addmodulesBtns(box.groupBoxLayout)
        layout.addWidget(box)
        self.setLayout(layout)

    def setCurrentCharacter(self, currentCharacter):
        self.currentCharacter = currentCharacter

    def addmodulesBtns(self, modulesGroupLayout):
        uiScriptFile = os.path.realpath(__file__)
        uiScriptPath, _ = os.path.split(uiScriptFile)
        modulesPath = uiScriptPath.replace('ui\widgets', 'modules')

        moduleFiles = [py for py in os.listdir(modulesPath) if py.endswith('.py') and '__init__' not in py]

        if moduleFiles:
            modulesLayout = QtGui.QVBoxLayout()
            modulesLayout.setContentsMargins(10, 0, 10, 0)
            btnGridLayout = QtGui.QGridLayout()
            modulesLayout.addLayout(btnGridLayout)
            modulesGroupLayout.addLayout(modulesLayout)

            numBtn = len(moduleFiles)
            # build a button grid with 3 columns
            for i in range(numBtn):
                name = moduleFiles[i][:-3]
                btn = QtGui.QPushButton(name)
                row = i / 3
                col = i % 3
                btnGridLayout.addWidget(btn, row, col)
                btn.clicked.connect(self.importModule)

    def importModule(self):
        yartWindow = self.parent().parent()
        moduleName = str(self.sender().text())
        toImport = 'bdRig.ui.modules.' + moduleName + 'UI'

        if yartWindow.charWidget.currentCharacter:
            try:
                mod = __import__(toImport, {}, {}, [moduleName])
                reload(mod)
                for name, obj in inspect.getmembers(mod):
                    if inspect.isclass(obj):
                        baseclass = obj.__bases__[0].__name__
                        if 'UI' in baseclass:
                            mod.createUI(yartWindow)
            except:
                pm.warning("Did not find any modules")
        else:
            pm.warning('No character to add modules too !!!')
