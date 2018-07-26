import cPickle as pickle
import os
import pymel.core as pm
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from functools import partial
import maya.OpenMayaUI as mui
import shiboken2

import utils.libWidgets as UI
reload(UI)


def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)

skinIOWin = 'skinIOWin'


class SkinCluster(object):
    def __init__(self, *args, **kargs):
        self.skinsFolder = kargs.setdefault('skinsFolder', '')
        self.shape = None
        self.initShape()
        self.skinNode = None
        self.mObject = None
        self.fnSkin = None
        self.data = {}

    def exportSkin(self):
        filePath = ''
        if self.shape is None:
            pm.warning('Nothing selected')
            return
        # if self.skinsFolder == '':
        # currentFile = pm.sceneName()
        # currentFilePath = os.path.split(currentFile)[0]
        # filePath = pm.fileDialog2(dir=self.skinsFolder,ds=2,fm=2,fileFilter = 'Skin Files (*.skin)')
        # if not filePath:
        # 	return
        # filePath = filePath [0]
        # if not filePath.endswith('.skin'):
        #	filePath += '.skin'\
        shapeParent = pm.ls(self.shape)[0].getParent().name()
        filePath = os.path.join(self.skinsFolder, shapeParent + '.skin')

        self.getSkinData()

        with open(filePath, 'wb') as fp:
            pickle.dump(self.data, fp, pickle.HIGHEST_PROTOCOL)

        print 'Exported skinCluster (%d influences, %d vertices ) %s' % (
        len(self.data['weights'].keys()), len(self.data['blendWeights']), filePath)

        # print self.data

    def importSkin(self, filePath=None):
        data = {}
        shapeParent = pm.ls(self.shape)[0].getParent().name()
        filePath = os.path.join(self.skinsFolder, shapeParent + '.skin')

        # if filePath is None:
        # 	currentFile = pm.sceneName()
        # 	currentFilePath = os.path.split(currentFile)[0]
        # 	filePath = pm.fileDialog2(dir=currentFilePath,ds=2,fm=1,fileFilter = 'Skin Files (*.skin)')[0]

        if not filePath:
            return

        with open(filePath, 'rb') as fp:
            data = pickle.load(fp)

            # check for same vertex count
        meshVertices = pm.polyEvaluate(self.shape, vertex=True)

        importedVertices = len(data['blendWeights'])

        self.skinNode = self.getSkinCluster()

        if not self.skinNode:
            joints = data['weights'].keys()

            unusedImports = []
            noMatch = set([x.name() for x in pm.ls(type='joint')])

            for jnt in joints:
                if jnt in noMatch:
                    noMatch.remove(jnt)
                else:
                    unusedImports.append(jnt)

            if unusedImports and noMatch:
                global mappingDialogWin
                if 'mappingDialogWin' in globals():
                    mappingDialogWin.close()

                mappingDialog = MappingDialog()
                mappingDialog.populateLists(unusedImports, noMatch)
                mappingDialog.exec_()

                for src, dst in mappingDialog.mapping.items():
                    data['weights'][dst] = data['weights'][src]
                    del data['weights'][src]

            joints = data['weights'].keys()
            try:
                pm.skinCluster(joints, self.shape, tsb=True, nw=2, n=data['name'])
            except:
                pm.error('Failed recreating the skin cluster ')

        if len(data):
            self.setSkinData(data)
            print 'Imported skin'

    def initShape(self):
        if not self.shape:
            selection = pm.ls(sl=1)
            if selection:
                transform = selection[0]
                self.shape = transform.getShape().name()
            else:
                pm.warning('No shape passed or selected')

    def getSkinCluster(self):
        history = pm.listHistory(self.shape, pruneDagObjects=True, il=2)
        if not history:
            return None
        skins = [s for s in history if pm.nodeType(s) == 'skinCluster']

        if skins:
            return skins[0].name()
        return None

    def getSkinData(self):
        self.skinNode = self.getSkinCluster()
        self.data = {
            'weights': {},
            'blendWeights': [],
            'name': self.skinNode
        }

        selectionList = OpenMaya.MSelectionList()
        selectionList.add(self.skinNode)

        self.mObject = OpenMaya.MObject()
        selectionList.getDependNode(0, self.mObject)
        self.fnSkin = OpenMayaAnim.MFnSkinCluster(self.mObject)

        dagPath, components = self.getGeometryComponents()
        self.getInfluenceWeights(dagPath, components)
        self.getBlendWeights(dagPath, components)

        for attr in ['skinningMethod', 'normalizeWeights']:
            self.data[attr] = pm.ls(self.skinNode)[0].attr(attr).get()

    def getGeometryComponents(self):
        fnSet = OpenMaya.MFnSet(self.fnSkin.deformerSet())
        members = OpenMaya.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OpenMaya.MDagPath()
        components = OpenMaya.MObject()
        members.getDagPath(0, dagPath, components)
        return dagPath, components

    def getInfluenceWeights(self, dagPath, components):
        weights = self.getCurrentWeigths(dagPath, components)

        influencePaths = OpenMaya.MDagPathArray()
        numInfluences = self.fnSkin.influenceObjects(influencePaths)
        numComponentsPerInfluence = weights.length() / numInfluences

        for i in range(influencePaths.length()):
            influenceName = influencePaths[i].partialPathName()
            self.data['weights'][influenceName] = [weights[j * numInfluences + i] for j in
                                                   range(numComponentsPerInfluence)]

    def getCurrentWeigths(self, dagpath, components):
        weights = OpenMaya.MDoubleArray()
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        pUInt = util.asUintPtr()
        self.fnSkin.getWeights(dagpath, components, weights, pUInt)
        return weights

    def getBlendWeights(self, dagPath, components):
        weights = OpenMaya.MDoubleArray()
        self.fnSkin.getBlendWeights(dagPath, components, weights)
        self.data['blendWeights'] = [weights[i] for i in range(weights.length())]

    def setSkinData(self, data):
        self.data = data

        self.skinNode = self.getSkinCluster()
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(self.skinNode)

        self.mObject = OpenMaya.MObject()
        selectionList.getDependNode(0, self.mObject)
        self.fnSkin = OpenMayaAnim.MFnSkinCluster(self.mObject)

        dagPath, components = self.getGeometryComponents()
        self.setInfluenceWeights(dagPath, components)
        self.setBlendWeights(dagPath, components)

        for attr in ['skinningMethod', 'normalizeWeights']:
            pm.setAttr('%s.%s' % (self.skinNode, attr), self.data[attr])

    def setInfluenceWeights(self, dagPath, components):
        weights = self.getCurrentWeigths(dagPath, components)
        influencePaths = OpenMaya.MDagPathArray()
        numInfluences = self.fnSkin.influenceObjects(influencePaths)
        numComponentsPerInfluence = weights.length() / numInfluences

        unusedImports = []

        noMatch = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]
        print noMatch

        for importedInfluence, importedWeights in self.data['weights'].items():
            for i in range(influencePaths.length()):
                influenceName = influencePaths[i].partialPathName()
                if influenceName == importedInfluence:
                    for j in range(numComponentsPerInfluence):
                        weights.set(importedWeights[j], j * numInfluences + i)
                    noMatch.remove(influenceName)
                    break
            else:
                print importedInfluence
                unusedImports.append(importedInfluence)

        print noMatch
        print unusedImports

        if unusedImports and noMatch:
            mappingDialog = MappingDialog()
            mappingDialog.populateLists(unusedImports, noMatch)
            mappingDialog.exec_()

            for src, dst in mappingDialog.mapping.items():
                for i in range(influencePaths.length()):
                    if influencePaths[i].partialPathName() == dst:
                        for j in range(numComponentsPerInfluence):
                            weights.set(self.data['weights'][src][j], j * numInfluences + i)
                        break

        influenceIndices = OpenMaya.MIntArray(numInfluences)
        for i in range(numInfluences):
            influenceIndices.set(i, i)
        self.fnSkin.setWeights(dagPath, components, influenceIndices, weights, False)

    def setBlendWeights(self, dagPath, components):
        blendWeights = OpenMaya.MDoubleArray(len(self.data['blendWeights']))
        for i, w in enumerate(self.data['blendWeights']):
            blendWeights.set(w, i)
        self.fnSkin.setBlendWeights(dagPath, components, blendWeights)

mappingDialogWin = 'mapDlgWin'

class MappingDialog(QtWidgets.QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(MappingDialog, self).__init__(parent)

        self.setWindowTitle('Mapping Dialog')
        self.setModal(True)

        self.setupUI()
        # self.show()
        self.resize(400, 200)

        self.mapping = {}

    def setupUI(self):
        mainLayout = UI.VertBox()
        mainBox = UI.TitledBox(title='Mappings')
        mainBoxLayout = UI.HorBox()

        unmappedLayout = UI.VertBox()
        separator = UI.Separator(d=1)
        mapBtnLayout = UI.VertBox()
        mapBtnLayout.setAlignment(QtCore.Qt.AlignVCenter)
        separator1 = UI.Separator(d=1)
        importedLayout = UI.VertBox()

        mainBoxLayout.addLayout(unmappedLayout)
        mainBoxLayout.addWidget(separator)
        mainBoxLayout.addLayout(mapBtnLayout)
        mainBoxLayout.addWidget(separator1)
        mainBoxLayout.addLayout(importedLayout)

        #########
        label =QtWidgets.QLabel('Unmapped influences')
        label.setAlignment(QtCore.Qt.AlignHCenter)

        self.existingInfluences = QtWidgets.QListWidget()
        unmappedLayout.addWidget(label)
        unmappedLayout.addWidget(self.existingInfluences)
        ###############
        mapBtn = QtWidgets.QPushButton('>>>')
        mapBtn.setFixedWidth(30)
        mapBtn.released.connect(self.setInfluenceMapping)
        mapBtnLayout.addWidget(mapBtn)

        unmapBtn = QtWidgets.QPushButton('<<<')
        unmapBtn.setFixedWidth(30)
        unmapBtn.released.connect(self.resetInfluenceMapping)
        mapBtnLayout.addWidget(unmapBtn)

        #############
        label =QtWidgets.QLabel('Available imported influences')
        label.setAlignment(QtCore.Qt.AlignHCenter)
        self.importedInfluences = QtWidgets.QListWidget()
        importedLayout.addWidget(label)
        importedLayout.addWidget(self.importedInfluences)
        ################
        okBtn = QtWidgets.QPushButton('Ok')
        okBtn.clicked.connect(self.accept)

        mainBox.layout.addLayout(mainBoxLayout)
        mainLayout.addWidget(mainBox)
        mainLayout.addWidget(okBtn)
        self.setLayout(mainLayout)

    def populateLists(self, importedInfluences, existingInfluences):
        tmp = list(existingInfluences)
        tmp.sort()
        self.existingInfluences.addItems(tmp)

        tmp = list(importedInfluences)
        tmp.sort()
        self.importedInfluences.addItems(tmp)

    def setInfluenceMapping(self):
        unmappedSelected = self.existingInfluences.currentItem().text()
        importedSelected = self.importedInfluences.currentItem().text()
        if unmappedSelected and importedSelected:
            self.mapping[importedSelected] = unmappedSelected
            self.existingInfluences.takeItem(self.existingInfluences.row(self.existingInfluences.currentItem()))
            self.importedInfluences.currentItem().setText(importedSelected + ' -> ' + unmappedSelected)

    def resetInfluenceMapping(self):
        importedSelected = self.importedInfluences.currentItem().text()
        if importedSelected:
            importedInfluence, tmp, existingInfluence = importedSelected.split(' ')
            del self.mapping[importedInfluence]
            self.existingInfluences.addItem(existingInfluence)
            self.importedInfluences.takeItem(self.importedInfluences.row(self.importedInfluences.currentItem()))
            self.importedInfluences.addItem(importedInfluence)


class SkinIOUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(SkinIOUI, self).__init__(parent)

        self.setObjectName(skinIOWin)
        self.setWindowTitle('Skin IO')
        self.skinsFolder = ''
        self.skinFolderEdit = None

        self.setupUI()
        self.setSkinsFolder()

    def setupUI(self):
        centralWidget = QtWidgets.QWidget()

        mainLayout = UI.VertBox()
        mainBox = UI.TitledBox(title='Skin IO')

        skinFolderLayout = UI.HorBox()
        self.skinFolderEdit = UI.LabelEditWidget(label='Skin Folder')
        skinFolderBtn = UI.ButtonB('<<')

        skinFolderLayout.addWidget(self.skinFolderEdit)
        skinFolderLayout.addWidget(skinFolderBtn)

        exportBtn = UI.ButtonB('Export')
        importBtn = UI.ButtonB('Import')

        exportBtn.clicked.connect(self.exportSkin)
        importBtn.clicked.connect(self.importSkin)
        skinFolderBtn.clicked.connect(self.setSkinsFolder)

        mainBox.layout.addLayout(skinFolderLayout)
        mainBox.layout.addWidget(exportBtn)
        mainBox.layout.addWidget(importBtn)

        mainLayout.addWidget(mainBox)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def exportSkin(self):
        selection = pm.ls(sl=1)
        if len(selection):
            for s in selection:
                pm.select(s)
                skinIo = SkinCluster(skinsFolder=self.skinsFolder)
                skinIo.exportSkin()

    def importSkin(self):
        selection = pm.ls(sl=1)
        if len(selection):
            for s in selection:
                pm.select(s)
                skinIo = SkinCluster(skinsFolder=self.skinsFolder)
                skinIo.importSkin()

    def setSkinsFolder(self):
        sceneName = pm.sceneName()
        path, file = os.path.split(sceneName)
        skinsFolder = os.path.join(path, 'skins')
        if not os.path.exists(skinsFolder):
            os.makedirs(skinsFolder)

        self.skinsFolder = skinsFolder
        self.skinFolderEdit.edit.setText(self.skinsFolder)


def openTool():
    if pm.window(skinIOWin, exists=True, q=True):
        pm.deleteUI(skinIOWin)

    tool = SkinIOUI()
    tool.show()
    tool.resize(500, 100)


