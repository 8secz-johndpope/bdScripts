﻿import cPickle as pickle
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
        self.skinFileName = kargs.setdefault('skinFile', '')
        self.mesh = kargs.setdefault('mesh', '')
        self.shape = None
        self.skinNode = None
        self.mObject = None
        self.fnSkin = None
        self.data = {}


    def exportSkin(self):
        filePath = ''
        self.initShape()
        if self.shape is None:
            pm.warning('Nothing selected')
            return

        shapeParent = pm.ls(self.shape)[0].getParent().name()
        if self.skinFileName == '':
            filePath = os.path.join(self.skinsFolder, shapeParent + '.skin')
        else:
            filePath = os.path.join(self.skinsFolder, self.skinFileName)

        self.getSkinData()

        with open(filePath, 'wb') as fp:
            pickle.dump(self.data, fp, pickle.HIGHEST_PROTOCOL)

        print 'Exported skinCluster (%d influences, %d vertices ) %s' % (
        len(self.data['weights'].keys()), len(self.data['blendWeights']), filePath)

        # print self.data

    def importSkin(self, filePath=None):
        data = {}
        filePath = os.path.join(self.skinsFolder, self.skinFileName)
        # shapeParent = pm.ls(self.shape)[0].getParent().name()
        # if self.skinFileName == '':
        #     filePath = os.path.join(self.skinsFolder, shapeParent + '.skin')
        # else:
        #     filePath = os.path.join(self.skinsFolder, self.skinFileName)
        # if filePath is None:
        # 	currentFile = pm.sceneName()
        # 	currentFilePath = os.path.split(currentFile)[0]
        # 	filePath = pm.fileDialog2(dir=currentFilePath,ds=2,fm=1,fileFilter = 'Skin Files (*.skin)')[0]

        if not filePath:
            return

        with open(filePath, 'rb') as fp:
            data = pickle.load(fp)

            # check for same vertex count

        shapeParent = data['mesh']
        self.shape = pm.ls(shapeParent)[0].getShape()
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
                if pm.window(mappingDialogWin, exists=True, q=True):
                    pm.deleteUI(mappingDialogWin)

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
            'mesh':self.mesh,
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
            if pm.window(mappingDialogWin, exists=True, q=True):
                pm.deleteUI(mappingDialogWin)

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
        self.setObjectName(mappingDialogWin)

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

        self.skinFolderEdit = UI.LabelEditWidget(label='Skin Folder')
        # self.meshesListWidget = QtWidgets.QListWidget()
        self.useMeshName = QtWidgets.QCheckBox('Use file name for export')
        self.skinsListWidget = QtWidgets.QListWidget()


        self.setupUI()
        self.setSkinsFolder()
        # self.populateMeshes()

    def setupUI(self):
        centralWidget = QtWidgets.QWidget()

        mainLayout = UI.VertBox()
        mainBox = UI.TitledBox(title='Skin IO')

        skinFolderLayout = UI.HorBox()
        skinFolderBtn = UI.ButtonB('...')

        skinFolderLayout.addWidget(self.skinFolderEdit)
        skinFolderLayout.addWidget(skinFolderBtn)

        gridLayout = QtWidgets.QGridLayout()
        # titleMesh = QtWidgets.QLabel('Meshes')
        titleSkins = QtWidgets.QLabel('Skin Files')
        # gridLayout.addWidget(titleMesh, 0, 0)
        gridLayout.addWidget(titleSkins, 0, 0)
        # gridLayout.addWidget(self.meshesListWidget, 1, 0)
        gridLayout.addWidget(self.skinsListWidget, 1, 0)
        # self.meshesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.skinsListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)


        exportBtn = UI.ButtonB('Export')
        importBtn = UI.ButtonB('Import')

        exportBtn.clicked.connect(self.exportSkin)
        importBtn.clicked.connect(self.importSkin)
        skinFolderBtn.clicked.connect(self.browseSkinsFolder)

        mainBox.layout.addLayout(skinFolderLayout)
        mainBox.layout.addLayout(gridLayout)
        # mainBox.layout.addWidget(self.skinsListWidget)

        mainBox.layout.addWidget(self.useMeshName)
        mainBox.layout.addWidget(exportBtn)
        mainBox.layout.addWidget(importBtn)

        mainLayout.addWidget(mainBox)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def exportSkin(self):
        selectedMeshes  = pm.ls(sl=1)
        if len(selectedMeshes) > 0:
            for item in selectedMeshes:
                pm.select(item)
                skinFile = self.setSkinFileName(item.name())
                if skinFile is not None:
                    skinIo = SkinCluster(skinsFolder=self.skinsFolder, mesh = item.name(), skinFile = skinFile)
                    skinIo.exportSkin()
                    self.addList(skinFile)
                # else:
                #     skinIo = SkinCluster(skinsFolder=self.skinsFolder, mesh = item.name())
                #     skinIo.exportSkin()
                #     self.addList(item.name())
        else:
            pm.warning('Please select one or more meshes!!!')

    def importSkin(self):
        selectedSkins = self.skinsListWidget.selectedItems()

        if len(selectedSkins) > 0:
            for item in selectedSkins:
                skinFile = item.text()
                skinIo = SkinCluster(skinsFolder=self.skinsFolder, skinFile = skinFile)
                skinIo.importSkin()

    def setSkinsFolder(self):
        sceneName = pm.sceneName()
        if sceneName:
            path, file = os.path.split(sceneName)
            pathSplit = path.split('/')
            i=0
            for t in pathSplit:
                if '_Rig' not in t:
                    i += 1
                else:
                    break

            skinsDataPath = '\\'.join(pathSplit[:i+1])
            skinDataFolder = ''
            for root, dirs, files in os.walk(skinsDataPath):
                for d in dirs:
                    if '03_skin_data' in d:
                        skinDataFolder = os.path.join(root, d)
                        break

            # print skinDataFolder
            # skinsFolder = os.path.join(path, '00_skins_data')
            # if not os.path.exists(skinsFolder):
            #     os.makedirs(skinsFolder)

            self.skinsFolder = skinDataFolder
            self.skinFolderEdit.edit.setText(self.skinsFolder)

            self.populateSkins()

    def setSkinFileName(self,mesh):
        f = ''
        if os.path.isdir(self.skinsFolder):
            if not self.useMeshName.isChecked():
                filePath = pm.fileDialog2(dir=self.skinsFolder, ds=1, fm=0, fileFilter='Skin Files (*.skin)',
                                          cap = 'Save skin for '+ mesh)

                if filePath is None:
                    return
                p, f = os.path.split(filePath[0])
            else:
                f = mesh + '.skin'
            return f
        else:
            pm.displayWarning('No path selected')

    def getSkinFileName(self):
        if self.skinsListWidget.currentItem() is not None:
            return self.skinsListWidget.currentItem().text()
        else:
            if os.path.isdir(self.skinsFolder):
                filePath = pm.fileDialog2(dir=self.skinsFolder, ds=1, fm=1, fileFilter='Skin Files (*.skin)')
                if not filePath:
                    return
                p, f = os.path.split(filePath[0])
                return f

        pm.displayWarning('No path selected')
        return None

    def populateSkins(self):
        self.skinsListWidget.clear()
        if os.path.isdir(self.skinsFolder):
            files = [name for name in os.listdir(self.skinsFolder) if os.path.isfile(os.path.join(self.skinsFolder, name)) and 'skin' in os.path.splitext(name)[1]]
            for f in files:
                listItem = QtWidgets.QListWidgetItem()
                listItem.setForeground(QtGui.QColor('#4498bf'))
                listItem.setText(f)
                self.skinsListWidget.addItem(listItem)

    def addList(self,skinFile):
        checkExist = 0
        for i in range(self.skinsListWidget.count()):
            if skinFile == self.skinsListWidget.item(i).text():
                checkExist = 1
                break

        if not checkExist:
            listItem = QtWidgets.QListWidgetItem()
            listItem.setForeground(QtGui.QColor('#4498bf'))
            listItem.setText(skinFile)
            self.skinsListWidget.addItem(listItem)

    def populateMeshes(self):
        geoMeshes = pm.ls('*geo', type='transform')
        if len(geoMeshes)>0:
            for mesh in geoMeshes:
                self.meshesListWidget.addItem(mesh.name())

    def browseSkinsFolder(self):
        sceneName = pm.sceneName()
        if sceneName:
            path, file = os.path.split(sceneName)
            pathSplit = path.split('/')
            i=0
            for t in pathSplit:
                if '_Rig' not in t:
                    i += 1
                else:
                    break

            rigFolderPath = '\\'.join(pathSplit[:i+1])

            filePath = pm.fileDialog2(dir= rigFolderPath, ds=1, fm=2)

            if not filePath:
                return

            self.skinFolderEdit.edit.setText(filePath[0])
            self.skinsFolder = filePath[0]
            self.populateSkins()


def openTool():
    if pm.window(skinIOWin, exists=True, q=True):
        pm.deleteUI(skinIOWin)

    tool = SkinIOUI()
    tool.show()
    tool.resize(500, 100)


