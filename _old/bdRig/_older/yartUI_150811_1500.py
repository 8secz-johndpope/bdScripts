# Yet Another Rigging Tool or shortly yart
import bdRig.system.guide as guide

import pymel.core as pm
import pymel.core.datatypes as dt
import re, os, shutil, glob, sys, inspect

import logging

import shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import maya.OpenMayaUI
import utils as utils

reload(utils)

import widgets.characterWidget as characterWidget

reload(characterWidget)


def get_maya_window():
    maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
    maya_window = shiboken.wrapInstance(long(maya_window_util), QtGui.QWidget)
    return maya_window


yartWin = 'yartWindow'


class YartUI(QtGui.QMainWindow):
    def __init__(self, parent=get_maya_window()):
        self.charSettingsWidget = None
        self.characterGroup = None
        self.charSettingsVisible = 0
        self.size_anim = None

        super(YartUI, self).__init__(parent)

        self.setObjectName(yartWin)
        self.setWindowTitle('Rigging Kit 0.1')

        centralWidget = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()

        # top layout will hold the character name
        # characterLayout = QtGui.QHBoxLayout()
        # self.createCharacterUi(characterLayout)
        # middle left side layout will hold the modules list
        leftSideLayout = QtGui.QVBoxLayout()
        # middle right side layout will hold the functionality
        rightSideLayout = QtGui.QVBoxLayout()

        # middle layout
        middleLayout = QtGui.QHBoxLayout()
        # middleLayout.setFrameStyle(QtGui.QFrame.StyledPanel)
        middleLayout.addLayout(leftSideLayout)
        middleLayout.addLayout(rightSideLayout)

        self.createLeftSideUi(leftSideLayout)
        self.createRightSideUi(rightSideLayout)

        charWidget = characterWidget.CharacterWidget()

        # mainLayout.addLayout(characterLayout)
        mainLayout.addWidget(charWidget)
        mainLayout.addLayout(middleLayout)

        # mainLayout.addLayout(splitterLayout)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        # menu bar
        # self.addMenu()

        self.show()
        self.resize(300, 600)

    def addMenu(self):
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.fileMenu.addAction('Load skeleton')
        self.fileMenu.addAction('Save skeleton')
        self.toolsMenu = self.menuBar.addMenu('Tools')
        self.toolsMenu.addAction('Create Picking Geometry')

    def createCharacterUi(self, parentLayout):
        self.characterGroup = utils.uiCreateLabeledBox('Character', settings=1)
        self.characterGroup.setFixedHeight(60)

        characterGroupLayout = utils.uiGetMainLayout(self.characterGroup, 'Character')
        characterGroupLayout.setAlignment(QtCore.Qt.AlignTop)
        characterGroupLayout.setContentsMargins(0, 0, 0, 0)

        nameLayout = QtGui.QHBoxLayout()
        nameLabel = QtGui.QLabel('Character name')
        nameEdit = QtGui.QLineEdit()
        nameBtn = QtGui.QPushButton('Create character')

        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(nameEdit)
        nameLayout.addWidget(nameBtn)

        self.characterSettingWidget = QtGui.QWidget()
        self.characterSettingWidget.setContentsMargins(0, 0, 0, 0)
        self.characterSettingWidget.setFixedHeight(0)

        characterGroupLayout.addWidget(self.characterSettingWidget)
        characterGroupLayout.addLayout(nameLayout)
        self.characterGroup.setLayout(characterGroupLayout)
        parentLayout.addWidget(self.characterGroup)

        settingsBtn = utils.uiGetButton(self.characterGroup, 'settingsButton')
        settingsBtn.clicked.connect(self.toggleCharSettingsUi)

    def toggleCharSettingsUi(self):
        if not self.charSettingsVisible:
            self.charSettingsVisible = 1
            self.addCharSettingsUi()
            self.addWidgetSizeAnim(self.characterSettingWidget, 1)
            self.characterGroup.setFixedHeight(90)
        else:
            self.charSettingsVisible = 0
            self.addWidgetSizeAnim(self.characterSettingWidget, 0)
            # self.charSettingsWidget.deleteLater()
            self.characterGroup.setFixedHeight(60)

    def addCharSettingsUi(self):
        charSettingsLayout = QtGui.QVBoxLayout()
        charSettingsLayout.setContentsMargins(0, 0, 0, 0)
        charSidesStrings = QtGui.QLineEdit('Left,Right')
        charSettingsLayout.addWidget(charSidesStrings)
        self.characterSettingWidget.setLayout(charSettingsLayout)

    def addWidgetSizeAnim(self, widget, onoff):
        self.size_anim = QtCore.QPropertyAnimation(widget, 'geometry')
        geometry = widget.geometry()
        width = geometry.width()
        x, y, _, _ = geometry.getCoords()
        print x, y
        size_start = QtCore.QRect(x, y, width, int(not (onoff)) * 20)
        size_end = QtCore.QRect(x, y, width, onoff * 20)

        self.size_anim.setStartValue(size_start)
        self.size_anim.setEndValue(size_end)
        self.size_anim.setDuration(200)

        size_anim_curve = QtCore.QEasingCurve()
        if onoff:
            size_anim_curve.setType(QtCore.QEasingCurve.InQuad)
        else:
            size_anim_curve.setType(QtCore.QEasingCurve.OutQuad)

        self.size_anim.setEasingCurve(size_anim_curve)

        self.size_anim.valueChanged.connect(self.forceResize)
        self.size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def forceResize(self, new_height):
        self.characterSettingWidget.setFixedHeight(new_height.height())

    def createLeftSideUi(self, parentLayout):
        label = QtGui.QLabel('Create modules')
        label.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        label.setStyleSheet("QLabel { background-color : green; color : white; }")
        label.setFixedHeight(20)
        labelLayout = QtGui.QVBoxLayout()
        labelLayout.addWidget(label)

        modulesGroup = QtGui.QGroupBox()
        modulesGroupLayout = QtGui.QVBoxLayout()
        modulesGroupLayout.setAlignment(QtCore.Qt.AlignTop)
        modulesGroupLayout.setContentsMargins(0, 0, 0, 0)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.HLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)

        modulesGroupLayout.addLayout(labelLayout)
        self.addmodulesBtns(modulesGroupLayout)
        modulesGroupLayout.addWidget(separator)

        modulesGroup.setLayout(modulesGroupLayout)

        parentLayout.addWidget(modulesGroup)

    def addmodulesBtns(self, modulesGroupLayout):
        uiScriptFile = os.path.realpath(__file__)
        uiScriptPath, _ = os.path.split(uiScriptFile)
        modulesPath = uiScriptPath.replace('ui', 'modules')

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
                btn.clicked.connect(self.createModule)

    def createRightSideUi(self, parentLayout):
        label = QtGui.QLabel('modules List ')
        label.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        label.setStyleSheet("QLabel { background-color : green; color : white; }")
        label.setFixedHeight(20)
        labelLayout = QtGui.QVBoxLayout()
        labelLayout.addWidget(label)

        modulesGroup = QtGui.QGroupBox()
        self.modulesGroupLayout = QtGui.QVBoxLayout()
        self.modulesGroupLayout.setAlignment(QtCore.Qt.AlignTop)
        self.modulesGroupLayout.setContentsMargins(0, 0, 0, 0)
        self.modulesGroupLayout.addLayout(labelLayout)

        modulesGroup.setLayout(self.modulesGroupLayout)

        parentLayout.addWidget(modulesGroup)

    def createModule(self):
        moduleName = self.sender().text()
        toImport = 'bdRig.modules.' + moduleName

        try:
            mod = __import__(toImport, {}, {}, [moduleName])
            reload(mod)
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    baseclass = obj.__bases__[0].__name__
                    if 'UI' in baseclass:
                        print baseclass
                        mod.createUI()
        except:
            pm.error("Did not find any modules")

    def createNewGuide(self):
        print 'Creating New Guide Template'
        import bdRig.ui.templateUI as templateUI
        reload(templateUI)
        templateUI.create()


def create():
    if pm.window(yartWin, exists=True, q=True):
        pm.deleteUI(yartWin)

    YartUI()
