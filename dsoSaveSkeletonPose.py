import pymel.core as pm
import json
import os
import utils.utils as utils


import utils.qt_handlers as qt_handlers
from utils.qt_handlers import QtCore, QtGui


import utils.ui_utils as ui_utils
reload(ui_utils)

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
        self.getSkeletonGroup()

        
    def getSkeletonGroup(self):
        search = pm.ls('skeleton')
        if search:
            self.skeletonGroup = search[0]
            
    def savePose(self):
        jntList = self.getSelection()
        if jntList:
            self.getPoseData(jntList)
            if self.skeletonGroup:
                self.poseFile = self.workFolder + self.poseName + '.txt'
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
        self.poseFile = self.workFolder + self.poseName + '.txt'
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



class SkeletonPoseUI(QtGui.QMainWindow):
    def __init__(self,parent=qt_handlers.get_maya_window()):
        super(SkeletonPoseUI,self).__init__(parent)
        self.setObjectName(skeletonPoseWin)
        self.setWindowTitle('Skeleton Pose')
        
        self.skeletonPose = None
        self.workFolder = ''
        self.getWorkFolder()
        
        self.setupUI()
        self.show()
        self.resize(300,100)        
    
    def setupUI(self):
        centralWidget = QtGui.QWidget()
        centralWidget.setMinimumWidth(350)
        mainLayout = QtGui.QVBoxLayout()
    
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        
        self.optionsBox = ui_utils.TitledBox(title='Options',settings=0)
        rowLayout = QtGui.QHBoxLayout()
        self.checkTranslate = QtGui.QCheckBox('Translate')
        self.checkTranslate.toggle()
        self.checkRotate = QtGui.QCheckBox('Rotate')
        self.checkRotate.toggle()
        self.checkScale = QtGui.QCheckBox('Scale')
        self.checkScale.toggle()
        rowLayout.addWidget(self.checkTranslate)
        rowLayout.addWidget(self.checkRotate)
        rowLayout.addWidget(self.checkScale)
        
        self.optionsBox.groupBoxLayout.addLayout(rowLayout)
        
        self.btnBox = ui_utils.TitledBox(title='Pose',settings=0)
        
        self.btnSave = QtGui.QPushButton('Save')
        self.btnLoad = QtGui.QPushButton('Load')
        rowLayout = QtGui.QHBoxLayout()
        rowLayout.addWidget(self.btnSave)
        rowLayout.addWidget(self.btnLoad)
        self.btnBox.groupBoxLayout.addLayout(rowLayout)
        
        mainLayout.addWidget(self.optionsBox)
        mainLayout.addWidget(self.btnBox)
        
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        
        self.btnSave.clicked.connect(self.save)
        self.btnLoad.clicked.connect(self.load)
        
    
    def getWorkFolder(self):
        currentFile = pm.sceneName()
        workFolder = ''
        if currentFile:
            splitPath = currentFile.split('/')
            i=0
            for token in splitPath[4:]:
                if token == 'work':
                    break
                i += 1
            for t in range(i+5):
                workFolder += (splitPath[t] + '/')
            
            self.workFolder = workFolder
        
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
    if pm.window( skeletonPoseWin, exists = True, q = True ):
        pm.deleteUI( skeletonPoseWin)

    SkeletonPoseUI()
