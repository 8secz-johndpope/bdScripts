import pymel.core as pm

import json
import os

import utils.libControllers as libCtrl

reload(libCtrl)
from utils.libControllers import Controller

import utils.libWidgets as UI

reload(UI)

import utils.qt_handlers as qt_handlers

reload(qt_handlers)

from utils.qt_handlers import QtCore


class ControllerUI(qt_handlers.qMainWindow):
    CTRL = '_ctrl'

    def __init__(self, parent=qt_handlers.get_maya_window()):
        global controllerWin
        if 'controllerWin' in globals():
            controllerWin.close()

        super(ControllerUI, self).__init__(parent)
        self.setWindowTitle('Create controller')

        self.ctrlNameEdit = None
        self.ctrlTargetPicker = None
        self.ctrlScaleSlider = None
        self.ctrlShape = None
        self.ctrlShapeFile = None
        self.ctrlLibFolder = ''
        self.shapeInfoDict = {}

        self.setupUI()
        controllerWin = self
        self.show()
        self.resize(300, 300)

        self.setCtrlLibFolder()

    def setupUI(self):
        centralWidget = qt_handlers.qWidget()

        mainLayout = UI.VertBox()
        mainBox = UI.TitledBox(title='Controllers Util')

        nameLayout = UI.HorBox()
        self.ctrlNameEdit = UI.LabelEditWidget(label='Name')
        pickNameBtn = UI.ButtonB('<<')
        self.ctrlTargetPicker = UI.ObjectPickerWidget(label='Target')

        ctrlLayout = UI.HorBox()
        ctrlLayout.setAlignment(QtCore.Qt.AlignLeft)
        shapes = ['circle', 'box', 'square', 'joint']
        self.ctrlShape = UI.LabelComboWidget(label='Shape')
        # self.ctrlShape.setMaximumWidth(140)
        self.ctrlShape.combo.addItems(shapes)
        attrSeparator = UI.Separator(d=1)
        self.ctrlScaleSlider = UI.FloatSpinWidget(label='Scale')
        self.ctrlScaleSlider.spin.setValue(1.0)
        ctrlLayout.addWidget(self.ctrlShape)
        ctrlLayout.addWidget(attrSeparator)
        ctrlLayout.addWidget(self.ctrlScaleSlider)

        separator = UI.Separator()
        btnLayout = UI.HorBox()
        newBtn = UI.ButtonB('create')
        exportBtn = UI.ButtonB('export')
        importBtn = UI.ButtonB('import')

        btnLayout.addWidget(exportBtn)
        btnLayout.addWidget(importBtn)

        separator1 = UI.Separator()
        titleBar = UI.TitleBar(title='Library')
        separator2 = UI.Separator()

        nameLayout.addWidget(self.ctrlNameEdit)
        nameLayout.addWidget(pickNameBtn)
        mainBox.layout.addLayout(nameLayout)
        mainBox.layout.addWidget(self.ctrlTargetPicker)
        mainBox.layout.addLayout(ctrlLayout)
        mainBox.layout.addWidget(separator)
        mainBox.layout.addWidget(newBtn)
        mainBox.layout.addWidget(separator1)
        mainBox.layout.addWidget(titleBar)
        mainBox.layout.addWidget(separator2)
        mainBox.layout.addLayout(btnLayout)

        newBtn.released.connect(self.createCtrl)
        pickNameBtn.released.connect(self.setCtrlName)
        exportBtn.released.connect(self.exportShape)
        importBtn.released.connect(self.importShape)

        mainLayout.addWidget(mainBox)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def createCtrl(self):
        ctrlName = self.ctrlNameEdit.edit.text()
        ctrlTarget = self.ctrlTargetPicker.edit.text()
        ctrlShape = self.ctrlShape.combo.currentText()
        ctrlScale = self.ctrlScaleSlider.spin.value()
        if ctrlName != '':
            pm.undoInfo(openChunk=True)
            ctrl = Controller(name=ctrlName, shape=ctrlShape, target=ctrlTarget, scale=ctrlScale)
            ctrl.buildController()
            pm.undoInfo(closeChunk=True)

    def setCtrlName(self):
        selection = pm.ls(sl=1, type='transform')
        if selection:
            ctrlName = selection[0].name()
            self.ctrlNameEdit.edit.setText(ctrlName + self.CTRL)
            self.ctrlTargetPicker.edit.setText(ctrlName)

    def setCtrlLibFolder(self):
        sceneName = pm.sceneName()
        path, file = os.path.split(sceneName)
        ctrlFolder = os.path.join(path, 'ctrl')
        if not os.path.exists(ctrlFolder):
            os.makedirs(ctrlFolder)

        self.ctrlLibFolder = ctrlFolder

    def exportShape(self):
        selection = pm.ls(sl=1)
        # currentFile = inspect.getfile(inspect.currentframe())
        # path = os.path.split(currentFile)[0]

        if os.path.isdir(self.ctrlLibFolder):
            filePath = pm.fileDialog2(dir=self.ctrlLibFolder, ds=1, fm=2, fileFilter='Ctrl Files (*.ctrl)')
            if not filePath:
                return
            # filePath = filePath [0]
            for transform in selection:
                if transform.getShape().type() == 'nurbsCurve':
                    self.saveShape(transform)
        else:
            pm.displayWarning('No path selected')

    def saveShape(self, transform):
        self.shapeInfoDict.clear()
        ctrlExport = transform
        shapes = ctrlExport.getShapes()
        if len(shapes):
            shape = shapes[0]
            self.shapeInfoDict['transform'] = ctrlExport.name()
            self.getShapeInfo(shape)

            shapeFile = os.path.join(self.ctrlLibFolder, ctrlExport + '.ctrl')
            with open(shapeFile, 'w') as outfile:
                json.dump(self.shapeInfoDict, outfile)

    def getShapeInfo(self, shape):
        name = shape.name()
        # cvNum = shape.numCVs()
        # cvPos = []

        # numCtrlPoints = pm.getAttr(name + '.contrlPoints')
        # USE CONTROL POINTS IN CASE ITS NEEDED FOR PERIODIC CURVES
        points = []
        for i in range(pm.getAttr(name + ".controlPoints", s=1)):
            pointPos = pm.getAttr(name + ".controlPoints[%i]" % i)
            pointPos = [round(v, 2) for v in pointPos]
            points.append(pointPos)

        # for i in range(cvNum):
        #     pos = pm.xform(shape.name() + '.cv[' + str(i) + ']', q=1, t=1, ws=1)
        #     cvPos.append(pos)

        self.shapeInfoDict['shapes'] = [{'shapeName': name, 'cvsPos': points}]

    def importShape(self):
        print self.ctrlLibFolder
        selectedCtrls = pm.ls(sl=1)
        for ctrlFile in os.listdir(self.ctrlLibFolder):
            if os.path.isfile(os.path.join(self.ctrlLibFolder, ctrlFile)):
                ctrlFileName, ext = os.path.splitext(ctrlFile)
                if ctrlFileName in selectedCtrls:
                    ctrlData = None
                    with open(os.path.join(self.ctrlLibFolder, ctrlFile), 'r') as inDataFile:
                        ctrlData = json.load(inDataFile)
                        self.restoreShape(ctrlData)

    def restoreShape(self, ctrlData):
        ctrlName = ctrlData['transform']
        if len(pm.ls(ctrlName)):
            print 'Found controller %s, restoring shape' % ctrlName
            shapesList = ctrlData['shapes']
            for shapeDict in shapesList:
                shapeFound = pm.ls(shapeDict['shapeName'])
                if shapeFound:
                    pm.undoInfo(openChunk=True)
                    shape = shapeFound[0]

                    cvNum = shape.numCVs()
                    cvPos = shapeDict['cvsPos']

                    for i in range(cvNum):
                        pm.move(shape.name() + '.cv[' + str(i) + ']', cvPos[i][0], cvPos[i][1], cvPos[i][2], ws=1)

                    pm.undoInfo(closeChunk=True)
