import os, sip, sys, inspect, re, shutil, glob
import pymel.core as pm
import maya.OpenMayaUI

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore


def get_maya_window():
    ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)


scriptsWin = 'scriptsWindow'


class ScriptsListUi(QtGui.QMainWindow):
    def __init__(self, parent=get_maya_window()):
        super(ScriptsListUi, self).__init__(parent)
        self.setObjectName(scriptsWin)
        self.setWindowTitle('Scripts List')

        self.defaultScriptsPath = self.getDefaultPath()

        self.setupUi()
        self.show()
        self.resize(300, 300)

    def setupUi(self):
        centralWidget = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()

        mainGroup = QtGui.QGroupBox()
        mainGroupLayout = QtGui.QVBoxLayout()

        # --------------- widgets -----------------#
        self.scriptsPathCombo = QtGui.QComboBox()
        self.scriptsList = QtGui.QListWidget()
        self.scriptClassesList = QtGui.QListWidget()
        self.scriptMethodsList = QtGui.QListWidget()
        self.executeLine = QtGui.QLineEdit()
        # ------------------------------------------#

        scriptInfoLayout = QtGui.QHBoxLayout()
        scriptInfoLayout.addWidget(self.scriptClassesList)
        scriptInfoLayout.addWidget(self.scriptMethodsList)

        mainGroupLayout.addWidget(self.scriptsPathCombo)
        mainGroupLayout.addWidget(self.scriptsList)
        mainGroupLayout.addLayout(scriptInfoLayout)
        mainGroupLayout.addWidget(self.executeLine)

        mainGroup.setLayout(mainGroupLayout)

        mainLayout.addWidget(mainGroup)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        # ---------------- signals ------------------
        self.scriptsPathCombo.currentIndexChanged.connect(self.updateList)
        self.scriptsList.itemDoubleClicked.connect(self.loadScript)
        self.populatePaths()

    def getDefaultPath(self):
        path = 'C:/Users/local_user/Documents/maya/scripts'
        user = os.environ.get("USERNAME")
        path = path.replace('local_user', user)

        return path

    def populatePaths(self):
        dirs = self.listDirs(self.defaultScriptsPath)

        if dirs:
            self.scriptsPathCombo.addItems(dirs)
            self.updateList()

    def listDirs(self, path):
        dirs = [os.path.realpath(os.path.join(path, d)) for d in os.listdir(path) if
                os.path.isdir(os.path.join(path, d))]
        if dirs:
            return dirs
        return None

    def updateList(self):
        self.scriptsList.clear()
        currentDir = self.scriptsPathCombo.currentText()
        scripts = [py for py in os.listdir(currentDir) if py.endswith('.py') and '__init__' not in py]
        self.scriptsList.addItems(scripts)

    def loadScript(self, item):
        path = self.scriptsPathCombo.currentText()
        module = os.path.split(str(path))[1]
        script = str(item.text().replace('.py', ''))
        toImport = str(module + '.' + script)

        try:
            print toImport
            mod = __import__(toImport, {}, {}, [script])
            reload(mod)

            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    if obj.__module__ == toImport:
                        print 'class ', name, obj
                elif inspect.isfunction(obj):
                    if obj.__module__ == toImport:
                        print 'function ', name, obj

            print 'Mod %s loaded' % toImport
        except:
            pm.warning('failed to load %s' % toImport)


def createUI():
    if pm.window(scriptsWin, exists=True, q=True):
        pm.deleteUI(scriptsWin)

    ScriptsListUi()
