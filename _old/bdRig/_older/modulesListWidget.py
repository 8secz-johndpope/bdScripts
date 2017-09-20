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


class ModulesListWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        self.yartWindow = parent
        super(ModulesListWidget, self).__init__(parent)
        self.items = []
        self.modulesList = None
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        box = utils.TitledBox(title='Modules List')

        self.modulesList = QtGui.QListWidget()
        box.groupBoxLayout.addWidget(self.modulesList)

        layout.addWidget(box)
        self.setLayout(layout)
        pass

    def appendModulesList(self, moduleName):
        self.modulesList.addItem(moduleName)
        pass

    def updateModulesList(self, currentCharacter):
        self.modulesList.clear()
        modulesList = currentCharacter.characterInfo['modulesList']
        for module in modulesList:
            self.modulesList.addItem(module['name'])
