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

import utils.libWidgets as UI
reload(UI)



def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)


mrWin = 'multiRenameWin'

class MultiRenameUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):

        super(MultiRenameUI, self).__init__(parent)
        self.setWindowTitle('Bd Tools 0.1')
        self.setObjectName(mrWin)
        self.setupUI()


    def setupUI(self):
        centralWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        #
        self.renameWidget = QtWidgets.QWidget()
        self.addRenameUI()

        #
        self.searchReplaceWidget = QtWidgets.QWidget()
        self.addSearchReplaceUI()

        #
        self.prefixSufixWidget = QtWidgets.QWidget()
        self.addPrefixSufixUI()

        #
        # self.infoWidget = UI.InfoWidget()
        self.infoDock = UI.InfoDock()

        # -----------------------------------------------------#
        mainLayout.addWidget(self.renameWidget)
        mainLayout.addWidget(self.searchReplaceWidget)
        mainLayout.addWidget(self.prefixSufixWidget)

        # -----------------------------------------------------#

        #
        # dockWidget = QtGui.QDockWidget("Output Info ")
        # dockWidget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        # dockWidget.setWidget(self.infoWidget)

        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.infoDock)  # dockWidget
        #
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def addRenameUI(self):
        renameLayout = UI.VertBox()
        self.renameBox = UI.TitledBox(title='    Rename')

        self.renameMask = UI.LabelEditWidget(label='Rename Mask')
        self.startCount = UI.SpinWidget(label='Start Count')
        self.startCount.spin.setMinimum(0)
        self.startCount.spin.setValue(1)

        self.renameBtn = QtWidgets.QPushButton('Rename')
        self.renameBtn.clicked.connect(self.rename)

        self.renameBox.layout.addWidget(self.renameMask)
        self.renameBox.layout.addWidget(self.startCount)
        self.renameBox.layout.addWidget(self.renameBtn)

        renameLayout.addWidget(self.renameBox)

        self.renameWidget.setLayout(renameLayout)

    def addSearchReplaceUI(self):
        searchReplaceLayout = UI.VertBox()
        self.searchReplaceBox = UI.TitledBox(title='    Search and Replace')

        self.search = UI.LabelEditWidget(label='Search')
        self.replace = UI.LabelEditWidget(label='Replace')

        self.searchReplaceBtn = QtWidgets.QPushButton('Search and Replace')
        self.searchReplaceBtn.clicked.connect(self.searchReplace)

        self.searchReplaceBox.layout.addWidget(self.search)
        self.searchReplaceBox.layout.addWidget(self.replace)
        self.searchReplaceBox.layout.addWidget(self.searchReplaceBtn)

        searchReplaceLayout.addWidget(self.searchReplaceBox)

        self.searchReplaceWidget.setLayout(searchReplaceLayout)

    def addPrefixSufixUI(self):
        prefixSufixLayout = UI.VertBox()
        self.prefixSufixBox = UI.TitledBox(title='    Prefix  / Sufix ')

        self.prefix = UI.LabelEditWidget(label='Prefix')
        self.sufix = UI.LabelEditWidget(label='Sufix')

        self.prefixSufixBtn = QtWidgets.QPushButton('Add Prefix / Sufix')
        self.prefixSufixBtn.clicked.connect(self.addPrefixSufix)

        self.prefixSufixBox.layout.addWidget(self.prefix)
        self.prefixSufixBox.layout.addWidget(self.sufix)
        self.prefixSufixBox.layout.addWidget(self.prefixSufixBtn)

        prefixSufixLayout.addWidget(self.prefixSufixBox)

        self.prefixSufixWidget.setLayout(prefixSufixLayout)

    def searchReplace(self):
        selectedObj = pm.ls(selection=True, ap=True)
        pm.undoInfo(openChunk=True)
        if selectedObj:
            strSearch = str(self.search.edit.text())
            strReplace = str(self.replace.edit.text())

            strNewNames = []

            if strSearch != '':
                for obj in selectedObj:
                    newName = obj.name().replace(strSearch, strReplace)
                    strNewNames.append(newName)
            else:
                self.infoDock.infoDisplay.append('Enter a search string')
                pm.warning('Enter a search string')

            strNewNames = list(reversed(strNewNames))
            strSelected = list(reversed(selectedObj))
            self.infoDock.infoDisplay.append('-------------- Search and Replace -------------------')
            for i in range(len(strNewNames)):
                self.infoDock.infoDisplay.append('%s renamed to %s' % (strSelected[i], strNewNames[i]))
                pm.rename(strSelected[i], strNewNames[i])
        else:
            self.infoDock.infoDisplay.append('Nothing Selected')
            pm.warning('Nothing selected!')
        pm.undoInfo(closeChunk=True)

    def rename(self):
        selectedObj = pm.ls(selection=True, ap=True)
        pm.undoInfo(openChunk=True)
        if selectedObj:
            strRenameMask = str(self.renameMask.edit.text())
            countStart = self.startCount.spin.value()

            padding = ''
            regex = re.compile(r"#+")
            result = regex.search(strRenameMask)
            if result:
                padding = result.group()

            if padding == '':
                self.infoDock.infoDisplay.append(
                    'Use a group of # sign for the position of the counter and the padding length !')
                pm.warning('Use a group of # sign for the position of the counter and the padding length !')
                return

            strNewNames = []
            if (strRenameMask != ''):
                strSelected = selectedObj

                strIndex = ''
                for i in range(countStart, countStart + len(selectedObj)):
                    paddingReplace = str(i).zfill(len(padding))
                    newName = strRenameMask.replace(padding, paddingReplace)
                    strNewNames.append(newName)

                strNewNames = list(reversed(strNewNames))
                strSelected = list(reversed(selectedObj))
                self.infoDock.infoDisplay.append('-------------- Rename -------------------')
                for i in range(len(strNewNames)):
                    self.infoDock.infoDisplay.append('%s renamed to %s' % (strSelected[i], strNewNames[i]))
                    pm.rename(strSelected[i], strNewNames[i])

            else:
                self.infoDock.infoDisplay.append('Need a Mask')
                pm.warning('Need a mask')
        else:
            self.infoDock.infoDisplay.append('Nothing Selected')
            pm.warning('Nothing selected!')

        pm.undoInfo(closeChunk=True)

    def addPrefixSufix(self):
        selectedObj = pm.ls(selection=True, ap=True)
        pm.select(cl=1)
        pm.undoInfo(openChunk=True)
        if selectedObj:
            strPrefix = str(self.prefix.edit.text())
            strSufix = str(self.sufix.edit.text())

            nameDict = {}
            newNames = []

            if strPrefix != '':
                for obj in selectedObj:
                    print obj.name()
                    newName = strPrefix + '_' + obj.nodeName()
                    obj.rename(newName)
                    print newName
                    nameDict[obj.name()] = newName

            self.infoDock.infoDisplay.append('-------------- Add Prefix / Sufix ------------------- \n')
            if strSufix != '':
                for obj in selectedObj:
                    newName = obj.name() + '_' + strSufix
                    nameDict[obj.name()] = newName
                    newNames.append(newName)
                    obj.rename(newName)
                    self.infoDock.infoDisplay.append('%s renamed to %s \n' % (obj.name(), newName))




                    # for oldName,newName in nameDict.iteritems():
                    # self.infoDock.infoDisplay.append('%s renamed to %s'%(oldName,newName))
                    # obj = pm.ls(oldName)[0]
                    # obj.rename(newName)

        else:
            self.infoDock.infoDisplay.append('Nothing Selected')
            pm.warning('Nothing selected!')
        pm.undoInfo(closeChunk=True)


def openTool():
    if pm.window(mrWin, exists=True, q=True):
        pm.deleteUI(mrWin)

    tool = MultiRenameUI()
    tool.show()
    tool.resize(300, 300)


