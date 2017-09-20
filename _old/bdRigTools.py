import pymel.core as pm
import pymel.core.datatypes as dt
import re, os, shutil, glob, sys, functools

from inspect import getmembers, isfunction

import utils.libRig as rig_utils

reload(rig_utils)

import utils.libDso as dso_utils

reload(dso_utils)

import logging

import utils.qt_handlers as qt_handlers
from utils.qt_handlers import QtCore, QtGui
import maya.OpenMayaUI

dsoToolsWin = 'dsoTools'


class dsoToolsUI(QtGui.QMainWindow):
    def __init__(self, parent=qt_handlers.get_maya_window()):
        super(dsoToolsUI, self).__init__(parent)
        self.setObjectName(dsoToolsWin)
        self.setWindowTitle('Dso Tools 0.1')

        self.setupUI()
        self.show()
        self.resize(600, 500)

    def setupUI(self):
        centralWidget = QtGui.QWidget()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        tabsFrame = QtGui.QFrame()
        tabsLayout = QtGui.QVBoxLayout()
        tabsLayout.setAlignment(QtCore.Qt.AlignTop)
        tabsLayout.setContentsMargins(0, 0, 0, 0)
        tabsFrame.setLayout(tabsLayout)
        tabsFrame.setMinimumHeight(200)

        infoFrame = QtGui.QFrame()
        infoLayout = QtGui.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop)
        infoLayout.setContentsMargins(0, 0, 0, 0)
        infoFrame.setLayout(infoLayout)

        self.tabs = QtGui.QTabWidget()
        self.setupRiggingTab()
        self.setupSkinningTab()

        self.infoDisplay = QtGui.QTextEdit()
        self.infoDisplay.setMinimumHeight(50)
        self.infoDisplay.setReadOnly(1)

        tabsLayout.addWidget(self.tabs)
        infoLayout.addWidget(self.infoDisplay)

        mainLayout.addWidget(tabsFrame)

        dockWidget = QtGui.QDockWidget("Output Info ")
        dockWidget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        dockWidget.setWidget(infoFrame)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dockWidget)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def setupRiggingTab(self):
        self.riggingWidget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(3)
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.setContentsMargins(5, 5, 5, 5)

        self.riggingWidget.setLayout(layout)

        rowLayout1 = QtGui.QHBoxLayout()
        rowLayout1.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        rowLayout2 = QtGui.QHBoxLayout()
        rowLayout2.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        layout.addLayout(rowLayout1)
        layout.addLayout(rowLayout2)

        self.rigBtn1 = QtGui.QPushButton('Num Joints')
        self.rigBtn1.setMinimumWidth(100)
        self.rigBtn2 = QtGui.QPushButton('Create Center Joint')
        self.rigBtn2.setMinimumWidth(100)
        self.rigBtn3 = QtGui.QPushButton('Select Hierarchy')
        self.rigBtn3.setMinimumWidth(100)
        self.rigBtn4 = QtGui.QPushButton('Add Fx Bones')
        self.rigBtn4.setMinimumWidth(100)
        self.rigBtn5 = QtGui.QPushButton('Constraint chains')
        self.rigBtn5.setMinimumWidth(100)
        self.rigBtn6 = QtGui.QPushButton('Unlock Nodes')
        self.rigBtn6.setMinimumWidth(100)
        self.rigBtn7 = QtGui.QPushButton('Replace crvShape')
        self.rigBtn7.setMinimumWidth(100)
        self.rigBtn8 = QtGui.QPushButton('Scale Ik Spline')
        self.rigBtn8.setMinimumWidth(100)
        self.rigBtn9 = QtGui.QPushButton('Add ROT MD node')
        self.rigBtn9.setMinimumWidth(100)
        self.rigBtn10 = QtGui.QPushButton('ConnectScale')
        self.rigBtn10.setMinimumWidth(100)

        self.rigBtn1.clicked.connect(functools.partial(self.executeTool, 'numJnt'))
        self.rigBtn2.clicked.connect(functools.partial(self.executeTool, 'centerJnt'))
        self.rigBtn3.clicked.connect(functools.partial(self.executeTool, 'selAll'))
        self.rigBtn4.clicked.connect(functools.partial(self.executeTool, 'addFx'))
        self.rigBtn5.clicked.connect(functools.partial(self.executeTool, 'cnstrChains'))
        self.rigBtn6.clicked.connect(functools.partial(self.executeTool, 'unlockNodes'))
        self.rigBtn7.clicked.connect(functools.partial(self.executeTool, 'replaceCrvShape'))
        self.rigBtn8.clicked.connect(functools.partial(self.executeTool, 'sclSpline'))
        self.rigBtn9.clicked.connect(functools.partial(self.executeTool, 'addMD'))
        self.rigBtn10.clicked.connect(functools.partial(self.executeTool, 'connectScl'))

        rowLayout1.addWidget(self.rigBtn1)
        rowLayout1.addWidget(self.rigBtn2)
        rowLayout1.addWidget(self.rigBtn3)
        rowLayout1.addWidget(self.rigBtn4)
        rowLayout1.addWidget(self.rigBtn5)
        rowLayout1.addWidget(self.rigBtn6)

        rowLayout2.addWidget(self.rigBtn7)
        rowLayout2.addWidget(self.rigBtn8)
        rowLayout2.addWidget(self.rigBtn9)
        rowLayout2.addWidget(self.rigBtn10)

        self.tabs.addTab(self.riggingWidget, 'Rigging')

    def setupSkinningTab(self):
        self.skinningWidget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(3)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setContentsMargins(5, 5, 5, 5)

        self.skinningWidget.setLayout(layout)

        rowLayout1 = QtGui.QHBoxLayout()
        layout.addLayout(rowLayout1)

        self.skinBtn1 = QtGui.QPushButton('Set Bind Pose')
        self.skinBtn1.clicked.connect(functools.partial(self.executeTool, 'setBnd'))
        self.skinBtn1.setMinimumWidth(100)
        self.skinBtn2 = QtGui.QPushButton('Delete Bind Pose(s)')
        self.skinBtn2.clicked.connect(functools.partial(self.executeTool, 'delBnd'))
        self.skinBtn2.setMinimumWidth(100)
        self.skinBtn3 = QtGui.QPushButton('Assume Bind Pose')
        self.skinBtn3.clicked.connect(functools.partial(self.executeTool, 'toBnd'))
        self.skinBtn3.setMinimumWidth(100)
        self.skinBtn4 = QtGui.QPushButton('Select Skin Joints')
        self.skinBtn4.clicked.connect(functools.partial(self.executeTool, 'selSkinJnt'))
        self.skinBtn4.setMinimumWidth(100)

        rowLayout1.addWidget(self.skinBtn1)
        rowLayout1.addWidget(self.skinBtn2)
        rowLayout1.addWidget(self.skinBtn3)
        rowLayout1.addWidget(self.skinBtn4)

        self.tabs.addTab(self.skinningWidget, 'Skinning')

    def executeTool(self, tool):
        if tool == 'numJnt':
            displayInfo = rig_utils.getNumJnt()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'centerJnt':
            displayInfo = rig_utils.bdJointOnSelCenter()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'setBnd':
            displayInfo = dso_utils.setBindPose()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'delBnd':
            displayInfo = dso_utils.delBindPose()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'toBnd':
            displayInfo = dso_utils.assumeBindPose()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'selSkinJnt':
            displayInfo = rig_utils.selectSkinJnt()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'addFx':
            displayInfo = dso_utils.createFxJoints()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'cnstrChains':
            displayInfo = rig_utils.constraintBndToRig()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'unlockNodes':
            displayInfo = rig_utils.unlockNodes()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'replaceCrvShape':
            displayInfo = rig_utils.bdReplaceShape()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'selAll':
            displayInfo = rig_utils.selectHierarchyJnt()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'sclSpline':
            displayInfo = rig_utils.bdBuildSplineSolverScale()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'addMD':
            displayInfo = rig_utils.bdAddDamp('r')
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')
        elif tool == 'connectScl':
            displayInfo = rig_utils.connectScale()
            self.infoDisplay.append(displayInfo)
            self.infoDisplay.append('--------------------------------------------------------------------')


def createUI():
    if pm.window(dsoToolsWin, exists=True, q=True):
        pm.deleteUI(dsoToolsWin)

    dsoToolsUI()
