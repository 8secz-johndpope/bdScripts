import pymel.core as pm
import json
import os
import utils.utils as utils


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

skeletonPoseWin = 'skeletonPoseWin'

class SkeletonPose(object):
    def __init__(self,*args,**kargs):
        self.poseName = kargs.setdefault('name','bindPose')
        self.workFolder = kargs.setdefault('filePath','')
        self.translate = kargs.setdefault('translate',0)
        self.rotate = kargs.setdefault('rotate',0)
        self.scale = kargs.setdefault('scale',0)

        self.poseData = {}
        self.skeletonGroup = None
        self.poseFile = ''

    def savePose(self):
        jntList = self.getSelection()
        if jntList:
            self.getPoseData(jntList)
            self.poseFile = os.path.join(self.workFolder, self.poseName + '.txt')
            print self.poseFile
            with open (self.poseFile,'w') as outPoseFile:
                json.dump(self.poseData,outPoseFile)
            #if not pm.hasAttr(self.skeletonGroup, self.poseName):
                #utils.addStringAttr(self.skeletonGroup, self.poseName, poseInfo)
                #pm.setAttr(self.skeletonGroup.name() + '.' + self.poseName,e=1,lock=1)
            #else:
                #pm.warning('Pose %s saved already'%self.poseName)
        else:
            pm.warning('Select joints to save the pose')
                
    def loadPose(self):
        self.poseFile = os.path.join(self.workFolder, self.poseName + '.txt')
        poseData = None
        with open(self.poseFile,'r') as inPoseFile:
            self.poseData= json.load(inPoseFile)
        
        self.setPose()
    
    def setPose(self):
        for jnt,jntData in self.poseData.iteritems():
            jntNode = None
            search = pm.ls(jnt)
            if search:
                jntNode = search[0]
                for op,opData in jntData.iteritems():
                    if op == 'scl':
                        jntNode.setScale(opData)
                    elif op == 'rot':
                        jntNode.setRotation(opData)
                    elif op == 'pos':
                        jntNode.setTranslation(opData)
            
                  
    def getSelection(self):
        selection = pm.ls(sl=1,type='joint')
        if selection:
            return selection
        
        return None
                
    def getPoseData(self,jntList):
        for jnt in jntList:
            jntData = {}
            pos = jnt.getTranslation(space='object')
            rot = jnt.getRotation(space='object')
            scale = jnt.getScale()
            
            if self.translate:
                jntData['pos'] = [pos[0],pos[1],pos[2]]
            if self.rotate:
                jntData['rot'] = [rot[0],rot[1],rot[2]]
            if self.scale:
                jntData['scl'] = scale
            
            self.poseData[jnt.name()] = jntData



class SkeletonPoseUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(SkeletonPoseUI, self).__init__(parent)
        self.setObjectName(skeletonPoseWin)
        self.setWindowTitle('Skeleton Pose')
        
        self.skeletonPose = None
        self.workFolder = ''
        self.getWorkFolder()
        
        self.setupUI()
        self.show()
        self.resize(300,100)        
    
    def setupUI(self):
        centralWidget = QtWidgets.QWidget()
        centralWidget.setMinimumWidth(350)
        mainLayout = QtWidgets.QVBoxLayout()
    
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.optionsBox = UI.TitledBox(title='Options')
        rowLayout = QtWidgets.QHBoxLayout()
        self.checkTranslate = QtWidgets.QCheckBox('Translate')
        self.checkTranslate.toggle()
        self.checkRotate = QtWidgets.QCheckBox('Rotate')
        self.checkRotate.toggle()
        self.checkScale = QtWidgets.QCheckBox('Scale')
        self.checkScale.toggle()
        rowLayout.addWidget(self.checkTranslate)
        rowLayout.addWidget(self.checkRotate)
        # rowLayout.addWidget(self.checkScale)
        
        self.optionsBox.layout.addLayout(rowLayout)

        self.btnBox = UI.TitledBox(title='Pose')
        
        self.btnSave = QtWidgets.QPushButton('Save')
        self.btnLoad = QtWidgets.QPushButton('Load')
        rowLayout = QtWidgets.QHBoxLayout()
        rowLayout.addWidget(self.btnSave)
        rowLayout.addWidget(self.btnLoad)
        self.btnBox.layout.addLayout(rowLayout)
        
        mainLayout.addWidget(self.optionsBox)
        mainLayout.addWidget(self.btnBox)
        
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        
        self.btnSave.clicked.connect(self.save)
        self.btnLoad.clicked.connect(self.load)
        
    
    def getWorkFolder(self):
        currentFile = pm.sceneName()
        print currentFile
        folderPath, currFile = os.path.split(currentFile)
        self.workFolder = folderPath
        
    def save(self):
        returnString = pm.fileDialog2(dir=self.workFolder,ds=2,fm=0,ff="Filtered Files (*.txt)")
        if returnString:
            
            self.fileName = os.path.splitext(os.path.basename(returnString[0]))[0]
            t = self.checkTranslate.isChecked()
            r = self.checkRotate.isChecked()
            s = self.checkScale.isChecked()
            
            self.skeletonPose = SkeletonPose(name = self.fileName,filePath=self.workFolder,translate = t,rotate = r, scale = s)
            self.skeletonPose.savePose()
        else:
            pm.warning('No file name entered')
        
    def load(self):
        returnString = pm.fileDialog2(dir=self.workFolder,ds=2,fm=1,ff="Filtered Files (*.txt)")
        if returnString:
            self.fileName = os.path.splitext(os.path.basename(returnString[0]))[0]
            self.skeletonPose = SkeletonPose(name = self.fileName,filePath=self.workFolder)
            self.skeletonPose.loadPose()
            
def createUI():
    if pm.window(skeletonPoseWin, exists = True, q = True ):
        pm.deleteUI(skeletonPoseWin)

    SkeletonPoseUI()
