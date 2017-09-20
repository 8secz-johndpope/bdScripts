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


class ModulesTreeWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        self.yartWindow = parent
        super(ModulesTreeWidget, self).__init__(parent)
        self.modulesTree = None
        self.rootItem = None
        self.setupUi()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        box = utils.TitledBox(title='Modules Tree')

        self.modulesTree = QtGui.QTreeWidget()
        self.modulesTree.setColumnCount(1)
        self.modulesTree.setHeaderHidden(1)
        self.modulesTree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        # spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)

        box.groupBoxLayout.addWidget(self.modulesTree)
        layout.addWidget(box)
        self.setLayout(layout)
        pass

    def setRoot(self, rootName):
        self.rootItem = QtGui.QTreeWidgetItem(self.modulesTree)
        self.rootItem.setText(0, rootName)
        pass

    def appendModulesList(self, moduleName):
        item = QtGui.QTreeWidgetItem(self.rootItem)
        item.setText(0, moduleName)
        self.modulesTree.expandItem(self.rootItem)
        pass

    def updateModulesList(self, currentCharacter):
        self.modulesTree.clear()
        rootModuleInfo = currentCharacter.characterInfo['rootModule']
        self.setRoot(rootModuleInfo['name'])
        modulesList = currentCharacter.characterInfo['modulesList']
        for module in modulesList:
            self.appendModulesList(module['name'])

        self.modulesTree.expandItem(self.rootItem)
