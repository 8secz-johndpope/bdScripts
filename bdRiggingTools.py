import pymel.core as pm

import re, os, shutil, glob, sys, inspect, functools
from inspect import getmembers, isfunction

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from functools import partial
import maya.OpenMayaUI as mui
import shiboken2

import utils.libWidgets as UI
reload(UI)

import utils.libRig as rig_utils
reload(rig_utils)

import utils.libDso as dso_utils
reload(dso_utils)

import utils.libSkinning as skin_utils
reload(skin_utils)

import utils.libControllers as ctrls_utils
reload(ctrls_utils)

def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)

bdToolsWin = 'bdTools'


class dsoToolsUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(dsoToolsUI, self).__init__(parent)
        self.setObjectName(bdToolsWin)
        self.setWindowTitle('Bd Tools 0.1')

        self.rigFunctionsInfo = {}
        self.skinFunctionsInfo = {}
        self.ctrlsFunctionsInfo = {}

        self.setupUI()
        self.show()

        # self.resize(600,500)

    def setupUI(self):
        centralWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        tabsFrame = QtWidgets.QFrame()
        tabsLayout = QtWidgets.QVBoxLayout()
        tabsLayout.setAlignment(QtCore.Qt.AlignTop)
        tabsLayout.setContentsMargins(0, 0, 0, 0)
        tabsFrame.setLayout(tabsLayout)
        tabsFrame.setMinimumHeight(200)

        infoFrame = QtWidgets.QFrame()
        infoLayout = QtWidgets.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop)
        infoLayout.setContentsMargins(0, 0, 0, 0)
        infoFrame.setLayout(infoLayout)

        self.tabs = QtWidgets.QTabWidget()
        self.setupRiggingTab()
        self.setupControllersTab()
        self.setupSkinningTab()

        self.infoDisplay = QtWidgets.QTextEdit()
        self.infoDisplay.setMinimumHeight(50)
        self.infoDisplay.setReadOnly(1)

        tabsLayout.addWidget(self.tabs)
        infoLayout.addWidget(self.infoDisplay)

        mainLayout.addWidget(tabsFrame)

        dockWidget = QtWidgets.QDockWidget("Output Info ")
        dockWidget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        dockWidget.setWidget(infoFrame)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dockWidget)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def setupRiggingTab(self):
        self.rigFunctionsInfo = self.getFunctions(rig_utils)
        print self.rigFunctionsInfo

        self.riggingWidget = QtWidgets.QWidget()
        layout = UI.VertBox()

        layout.setContentsMargins(5, 5, 5, 5)

        for category in self.rigFunctionsInfo.keys():
            categoryWidget = QtWidgets.QWidget()

            categoryLayout = UI.VertBox()
            categoryWidget.setLayout(categoryLayout)

            label = QtWidgets.QLabel(category)
            label.setAlignment(QtCore.Qt.AlignRight)

            separator = UI.Separator()
            gridLayout = QtWidgets.QGridLayout()
            gridLayout.setAlignment(QtCore.Qt.AlignLeft)

            label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)

            for item in self.rigFunctionsInfo[category]:
                btnName = self.niceName(item[0])
                btn = QtWidgets.QPushButton(btnName)
                # btn.setFixedHeight(20)
                btn.clicked.connect(functools.partial(self.executeTool, item[1]))
                i = self.rigFunctionsInfo[category].index(item)
                gridLayout.addWidget(btn, i / 4, i % 4)

            categoryLayout.addWidget(label)
            categoryLayout.addWidget(separator)
            categoryLayout.addLayout(gridLayout)
            categoryWidget.setFixedHeight(categoryWidget.sizeHint().height())
            layout.addWidget(categoryWidget)

        self.riggingWidget.setLayout(layout)
        self.riggingWidget.setFixedHeight(self.riggingWidget.sizeHint().height())
        self.tabs.addTab(self.riggingWidget, 'Rigging')

    def setupSkinningTab(self):
        self.skinFunctionsInfo = self.getFunctions(skin_utils)
        print self.skinFunctionsInfo
        self.skinningWidget = QtWidgets.QWidget()
        layout = UI.VertBox()
        layout.setContentsMargins(5, 5, 5, 5)

        for category in self.skinFunctionsInfo.keys():
            categoryWidget = QtWidgets.QWidget()

            categoryLayout = UI.VertBox()
            categoryWidget.setLayout(categoryLayout)

            label = QtWidgets.QLabel(category)
            separator = UI.Separator()
            gridLayout = QtWidgets.QGridLayout()
            gridLayout.setAlignment(QtCore.Qt.AlignLeft)

            label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

            for item in self.skinFunctionsInfo[category]:
                btnName = self.niceName(item[0])
                btn = QtWidgets.QPushButton(btnName)
                btn.setFixedHeight(20)
                btn.clicked.connect(functools.partial(self.executeTool, item[1]))
                i = self.skinFunctionsInfo[category].index(item)
                gridLayout.addWidget(btn, i / 4, i % 4)

            categoryLayout.addWidget(label)
            categoryLayout.addWidget(separator)
            categoryLayout.addLayout(gridLayout)
            categoryWidget.setFixedHeight(categoryWidget.sizeHint().height())
            layout.addWidget(categoryWidget)

        self.skinningWidget.setLayout(layout)
        self.skinningWidget.setFixedHeight(self.skinningWidget.sizeHint().height())
        self.tabs.addTab(self.skinningWidget, 'Skinning')

    def setupControllersTab(self):
        self.ctrlsFunctionsInfo.clear()
        self.ctrlsFunctionsInfo = self.getFunctions(ctrls_utils)
        self.ctrlsWidget = QtWidgets.QWidget()

        layout = UI.VertBox()
        layout.setContentsMargins(5, 5, 5, 5)

        for category in self.ctrlsFunctionsInfo.keys():
            categoryWidget = QtWidgets.QWidget()

            categoryLayout = UI.VertBox()
            categoryWidget.setLayout(categoryLayout)

            label = QtWidgets.QLabel(category)
            separator = UI.Separator()
            gridLayout = QtWidgets.QGridLayout()
            gridLayout.setAlignment(QtCore.Qt.AlignLeft)

            label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

            for item in self.ctrlsFunctionsInfo[category]:
                btnName = self.niceName(item[0])
                btn = QtWidgets.QPushButton(btnName)
                btn.setFixedHeight(20)
                btn.clicked.connect(functools.partial(self.executeTool, item[1]))
                i = self.ctrlsFunctionsInfo[category].index(item)
                gridLayout.addWidget(btn, i / 4, i % 4)

            categoryLayout.addWidget(label)
            categoryLayout.addWidget(separator)
            categoryLayout.addLayout(gridLayout)
            categoryWidget.setFixedHeight(categoryWidget.sizeHint().height())
            layout.addWidget(categoryWidget)

        self.ctrlsWidget.setLayout(layout)
        self.ctrlsWidget.setFixedHeight(self.ctrlsWidget.sizeHint().height())
        self.tabs.addTab(self.ctrlsWidget, 'Controllers')

        # self.ctrlsFunctionsInfo = self.getFunctions(ctrls_utils)
        # self.ctrlsWidget = QtWidgets.QWidget()
        # layout = QtWidgets.QVBoxLayout()
        # layout.setSpacing(3)
        # layout.setAlignment(QtCore.Qt.AlignTop)
        # layout.setContentsMargins(5,5,5,5)

        # numCtrlsFnc = len(self.ctrlsFunctionsInfo)
        # gridLayout = QtWidgets.QGridLayout()


        # for i in range(numCtrlsFnc):

    #	btnName = self.niceName(self.ctrlsFunctionsInfo[i][0])
    #	btn = QtWidgets.QPushButton(btnName)
    #	btn.clicked.connect(functools.partial(self.executeTool,self.ctrlsFunctionsInfo[i][1]))
    #	gridLayout.addWidget(btn,i/6,i%6)


    # layout.addLayout(gridLayout)

    # self.ctrlsWidget.setLayout(layout)

    # self.tabs.addTab(self.ctrlsWidget,'Controllers')

    def executeTool(self, function):
        displayInfo = function()
        self.infoDisplay.append(displayInfo)
        self.infoDisplay.append('--------------------------------------------------------------------')

        # def getFunctions(self,module):

    #	functions_list = [o for o in getmembers(module) if isfunction(o[1])]
    #	i=0
    #	functionsDict = {}
    #	for function in functions_list:
    #		if function[1].__code__.co_argcount == 0:
    #			category = self.getCategory(function[1].__doc__)
    #			functionsDict[i] = [function[0],function[1],category]
    #			i+=1

    #	return functionsDict


    def getFunctions(self, module):
        functions_list = [o for o in getmembers(module) if isfunction(o[1])]

        i = 0
        functionsDict = {}
        functionItem = {}
        for function in functions_list:
            if function[1].__code__.co_argcount == 0:
                category = self.getCategory(function[1].__doc__)
                functionItem[i] = [function[0], function[1]]
                if category not in functionsDict:
                    functionsDict[category] = [functionItem[i]]
                else:
                    value = functionsDict[category]
                    value.append(functionItem[i])
                    functionsDict[category] = value
                i += 1

        return functionsDict

    def getCategory(self, doc):
        if doc:
            docLines = doc.split('\n')
            category = ''
            if docLines[1].split(':')[1].rstrip():
                category = docLines[1].split(':')[1].rstrip()
            else:
                category = 'General'

            return category

    def niceName(self, uglyName):
        uglyName = uglyName[0].capitalize() + uglyName[1:]
        tokens = re.findall('[A-Z][^A-Z]*', uglyName)
        if 'Bd' in tokens:
            tokens.remove('Bd')
        newName = ''
        for t in tokens:
            newName += (t + ' ')
        newName = newName.strip()
        return newName


def createUI():
    if pm.window(bdToolsWin, exists=True, q=True):
        pm.deleteUI(bdToolsWin)

    dsoToolsUI()
