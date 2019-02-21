import pymel.core as pm
import traceback
import os
import inspect
import re
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import maya.OpenMayaUI as mui
import shiboken2

from ..utils import libWidgets as UI
reload(UI)


def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)


cmWin = 'cmWin'


class ShamanContentManagerUI(QtWidgets.QMainWindow):
    contentPath = 'd:/Projects/Shaman/Content_Sources'
    categories = ['Characters', 'Weapons']
    characterCategories = ['Animals', 'Humans']

    def __init__(self, parent=getMayaWindow()):
        super(ShamanContentManagerUI, self).__init__(parent)
        self.setWindowTitle('Shaman Assets')
        self.setObjectName(cmWin)

        self.categoriesCombo = QtWidgets.QComboBox()
        self.assetsLayout = UI.TitledBox(title='', barHeight=15)
        self.charactersCategoryCombo = QtWidgets.QComboBox()
        self.charactersCombo = QtWidgets.QComboBox()
        self.weaponsCombo = QtWidgets.QComboBox()
        self.setProjectButton = UI.ActionButton('Set project')
        self.sectionTab = QtWidgets.QTabWidget()
        self.rigFilesTab = QtWidgets.QWidget()

        self.setupUI()
        self.categoriesChanged(self.categoriesCombo.currentIndex())

    def setupUI(self):
        centralWidget = QtWidgets.QWidget()
        mainLayout = UI.VertBox()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        categoriesBox = UI.TitledBox(title='Categories', barHeight=15)
        categoriesBox.layout.addWidget(self.categoriesCombo)
        for cat in ShamanContentManagerUI.categories:
            self.categoriesCombo.addItem(cat)

        mainLayout.addWidget(categoriesBox)

        separator = UI.Separator()
        mainLayout.addWidget(separator)

        self.assetsLayout.layout.addWidget(self.charactersCategoryCombo)
        self.charactersCategoryCombo.hide()
        for category in ShamanContentManagerUI.characterCategories:
            self.charactersCategoryCombo.addItem(category)
        self.assetsLayout.layout.addWidget(self.charactersCombo)
        self.charactersCombo.hide()
        self.assetsLayout.layout.addWidget(self.weaponsCombo)
        self.weaponsCombo.hide()
        self.assetsLayout.layout.addWidget(self.setProjectButton)
        mainLayout.addWidget(self.assetsLayout)

        separator = UI.Separator()
        mainLayout.addWidget(separator)

        self.sectionTab.addTab(self.rigFilesTab, "Rig")
        mainLayout.addWidget(self.sectionTab)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.categoriesCombo.currentIndexChanged.connect(self.categoriesChanged)
        self.charactersCategoryCombo.currentIndexChanged.connect(self.updateCharacters)

    def categoriesChanged(self, index):
        if index == 0:
            self.assetsLayout.setTitle('Characters')
            self.charactersCategoryCombo.show()
            self.charactersCombo.show()
            self.weaponsCombo.hide()
        elif index == 1:
            self.assetsLayout.setTitle('Weapons')
            self.charactersCategoryCombo.hide()
            self.charactersCombo.hide()
            self.weaponsCombo.show()
        self.updateCategories(index)

    def updateCategories(self, index):
        # Characters
        if index == 0:
            self.updateCharacters(self.charactersCategoryCombo.currentIndex())
        #Weapons
        elif index == 1:
            path = os.path.join(ShamanContentManagerUI.contentPath,  ShamanContentManagerUI.categories[index])
            fileList = self.listFolders(path)
            self.weaponsCombo.clear()
            for f in fileList:
                self.weaponsCombo.addItem(f)

    def updateCharacters(self, index):
        path = os.path.join(ShamanContentManagerUI.contentPath,  self.categoriesCombo.currentText(),
                                self.charactersCategoryCombo.currentText())
        fileList = self.listFolders(path)
        self.charactersCombo.clear()
        for f in fileList:
            self.charactersCombo.addItem(f)

    def listFolders(self, path):
        folders = os.listdir(path)
        return folders


def openTool():
    if pm.window(cmWin, exists=True, q=True):
        pm.deleteUI(cmWin)

    tool = ShamanContentManagerUI()
    tool.show()
    tool.resize(300, 300)


