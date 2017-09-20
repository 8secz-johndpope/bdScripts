# import shiboken
import sip
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

import pymel.core as pm
import maya.OpenMayaUI

import utils as utils

reload(utils)

import bdRig.system.module as module

reload(module)

import json

'''
def get_maya_window():
    maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
    maya_window = shiboken.wrapInstance( long( maya_window_util ), QtGui.QWidget )
    return maya_window
'''


def get_maya_window():
    ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)


templateWin = 'templateWindow'


class TemplateUI(QtGui.QMainWindow):
    def __init__(self, parent=get_maya_window()):
        super(TemplateUI, self).__init__(parent)

        self.modulesList = {}

        self.setObjectName(templateWin)
        self.setWindowTitle('Create New Guide Template')
        self.setWindowFlags(QtCore.Qt.Tool)

        centralWidget = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()

        # top layout will hold the character name
        toplayout = QtGui.QVBoxLayout()
        self.createTopUi(toplayout)

        guideUtilsLayout = QtGui.QVBoxLayout()
        self.createGuideUtilsUi(guideUtilsLayout)

        # modulesListLayout = QtGui.QVBoxLayout()
        # self.createModulesListUi(modulesListLayout)

        mainLayout.addLayout(toplayout)
        mainLayout.addLayout(guideUtilsLayout)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.show()
        self.resize(300, 300)

        '''
        dockWidget = QtGui.QDockWidget("Dock Widget")
        dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        dockWidget.setWidget(centralWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)
        '''

    def createTopUi(self, parentLayout):
        self.attrGroup = utils.uiCreateLabeledBox('Attributes')
        attrGroupLayout = utils.uiGetMainLayout(self.attrGroup, 'Attributes')

        templateNameLayout = QtGui.QHBoxLayout()
        templateNameLayout.setContentsMargins(10, 5, 10, 0)
        templateNameLabel = QtGui.QLabel('Template Name: ')
        templateNameEdit = QtGui.QLineEdit()
        templateNameEdit.setObjectName('moduleNameEdit')
        templateNameLayout.addWidget(templateNameLabel)
        templateNameLayout.addWidget(templateNameEdit)

        jointNumberLayout = QtGui.QHBoxLayout()
        jointNumberLayout.setContentsMargins(10, 0, 10, 0)
        jointNumberLabel = QtGui.QLabel('Joint Number: ')
        jointNumberSpin = QtGui.QSpinBox()
        jointNumberSpin.setMinimum(1)
        jointNumberSpin.setObjectName('numJntSpin')
        jointNumberLayout.addWidget(jointNumberLabel)
        jointNumberLayout.addWidget(jointNumberSpin)

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.HLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)

        newAttrBtn = QtGui.QPushButton('+')
        createModuleBtn = QtGui.QPushButton('Create')

        attrGroupLayout.addLayout(templateNameLayout)
        attrGroupLayout.addLayout(jointNumberLayout)
        attrGroupLayout.addWidget(separator)
        attrGroupLayout.addWidget(newAttrBtn)
        attrGroupLayout.addWidget(createModuleBtn)

        self.attrGroup.setLayout(attrGroupLayout)

        parentLayout.addWidget(self.attrGroup)

        createModuleBtn.clicked.connect(self.createModule)

    def createGuideUtilsUi(self, parentLayout):
        guidesUtilsBoxGroup = utils.uiCreateLabeledBox('Utils')
        guidesUtilsBoxGroupLayout = utils.uiGetMainLayout(guidesUtilsBoxGroup, 'Utils')

        btnLayout = QtGui.QGridLayout()

        guideParentBtn = QtGui.QPushButton('Parent')
        guideUnparentBtn = QtGui.QPushButton('Unparent')
        orientBtn = QtGui.QPushButton('Orient Guides')
        alignBtn = QtGui.QPushButton('Align Guide(s)')

        btnLayout.addWidget(guideParentBtn, 0, 0)
        btnLayout.addWidget(guideUnparentBtn, 0, 1)
        btnLayout.addWidget(orientBtn, 0, 2)
        btnLayout.addWidget(alignBtn, 1, 0)

        guidesUtilsBoxGroupLayout.addLayout(btnLayout)
        parentLayout.addWidget(guidesUtilsBoxGroup)

        orientBtn.clicked.connect(self.orientGuides)

    def createModulesListUi(self, modulesListLayout):
        modulesListBoxGroup = utils.uiCreateLabeledBox('Modules List')
        modulesListBoxGroupLayout = utils.uiGetMainLayout(guidesUtilsBoxGroup, 'Modules List')

    def createModule(self):
        moduleNameEdit = self.attrGroup.findChild(QtGui.QLineEdit, 'moduleNameEdit')
        moduleName = moduleNameEdit.text()
        moduleNumJntSpin = self.attrGroup.findChild(QtGui.QSpinBox, 'numJntSpin')
        moduleNumJnt = moduleNumJntSpin.value()

        if moduleName:
            moduleExists = pm.ls(moduleName)
            if not moduleExists:
                newModule = module.Module(name=moduleName, nJnt=moduleNumJnt)
                newModule.createModule()
                self.modulesList[newModule.name] = {'Joint Number': moduleNumJnt,
                                                    'Module Controller': newModule.moduleCtrl}
            else:
                pm.warning('Module "%s" exists already' % moduleName)

    def orientGuides(self):
        selection = pm.ls(sl=1)
        if selection:
            guide = selection[0]
            for module, attrs in self.modulesList.iteritems():
                for k, v in attrs.iteritems():
                    if k == 'Module Controller':
                        guideMessage = pm.listConnections(guide.message)
                        if guideMessage:
                            if guideMessage[0] == v:
                                module.reorientGuides()

    def closeEvent(self, event):
        print 'closing'
        event.accept()  # let the window close


def create():
    if pm.window(templateWin, exists=True, q=True):
        pm.deleteUI(templateWin)

    TemplateUI()
