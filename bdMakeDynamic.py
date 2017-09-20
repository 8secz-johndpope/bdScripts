import pymel.core as pm
import pymel.core.datatypes as dt

import utils.qt_handlers as qt_handlers
from utils.qt_handlers import QtCore, QtGui

import utils.mayaDecorators as decorators

reload(decorators)

import logging, os
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import utils.ui_utils as utils

reload(utils)

mkDynamicWin = 'makeDynamicWin'


class bdMakeDynamic():
    def __init__(self, *args, **kargs):
        fkCtrlTop = ''
        self.fkRootObj = None
        self.dynRootObj = None
        self.crv = None
        self.dynCrv = None
        self.mainGrp = None
        self.hairSystemGrp = None
        self.drvJntGrp = None
        self.chainInfo = {}

        self.rootObj = kargs.setdefault('start')
        self.hairSystem = kargs.setdefault('hairSystem')
        self.hairSystemUserName = kargs.setdefault('hairSystemName')

    def createDynamicSystem(self):
        self.createGroups()
        self.bdCreateDynChain()
        self.bdCreateFKChain()
        self.bdConnectChains()
        self.bdAddFkCtrls()

    def createGroups(self):
        pm.select(cl=1)
        self.mainGrp = pm.group(name=self.rootObj + '_main_grp')
        pm.select(cl=1)
        self.hairSystemGrp = pm.group(name=self.rootObj + '_hair_grp')
        self.hairSystemGrp.hide()
        pm.select(cl=1)
        pm.parent(self.hairSystemGrp, self.mainGrp)
        pm.select(cl=1)
        self.drvJntGrp = pm.group(name=self.rootObj + '_drv_jnt_grp')
        self.drvJntGrp.hide()
        pm.select(cl=1)
        pm.parent(self.drvJntGrp, self.mainGrp)
        pm.select(cl=1)

    def bdCreateFKChain(self):
        print '----------------- Creating FK chain ---------------------------'
        fkRootObj = pm.duplicate(self.rootObj)[0]

        pm.parent(fkRootObj, self.mainGrp)

        fkRootObj.rename(self.rootObj.name() + '_fk')

        fkChain = fkRootObj.listRelatives(type='joint', ad=True, f=True)
        fkChain.reverse()

        for jnt in fkChain:
            jnt.rename(jnt.name() + '_fk')

        fkChain = [fkRootObj] + fkChain

        pm.skinCluster(fkChain, self.crv)
        self.fkRootObj = fkRootObj
        pm.parent(self.fkRootObj, self.drvJntGrp)

    def bdCreateDynChain(self):
        print '----------------- Creating dynamic chain -----------------------'
        pm.select(cl=1)
        jntPosArray = []

        dynRootObj = pm.duplicate(self.rootObj)[0]
        pm.select(cl=1)
        pm.parent(dynRootObj, self.mainGrp)

        dynRootObj.rename(self.rootObj.name() + '_dyn')
        jntPos = dynRootObj.getTranslation(space='world')
        jntPosArray.append(jntPos)

        dynChain = dynRootObj.listRelatives(type='joint', ad=True, f=True)
        # dynChain.append(dynRootObj)

        dynChain.reverse()

        for jnt in dynChain:
            jnt.rename(jnt.name() + '_dyn')
            jntPos = jnt.getTranslation(space='world')
            jntPosArray.append(jntPos)

        drvCrv = pm.curve(d=1, p=jntPosArray, k=[i for i in range(len(jntPosArray))])
        drvCrv.rename(self.rootObj.name() + '_flc_crv')
        drvCrvShape = drvCrv.getShape()

        self.crv = pm.duplicate(drvCrv)[0]
        pm.parent(self.crv, self.hairSystemGrp)
        self.crv.rename(self.rootObj.name() + '_crv')
        bs = pm.blendShape(self.crv, drvCrv)
        pm.blendShape(bs, edit=True, w=[(0, 1)])

        pm.select(drvCrv.fullPath())

        if self.hairSystem == '':
            if self.hairSystemUserName == '':
                self.hairSystemUserName = self.rootObj.name()

            mayaVersion = pm.about(v=True)
            if mayaVersion == '2011':
                pm.mel.eval('makeCurvesDynamicHairs 1 0 1;')
            elif mayaVersion == '2016':
                pm.mel.eval('makeCurvesDynamic 2 { "0", "0", "0", "1", "0"};')


                # get the follicle + dyn curve + hair system
            try:
                pm.select(cl=1)
                flcShape = pm.listConnections(drvCrvShape, type='follicle', s=False)[0]

                flcShape.pointLock.set(1)
                flcShape.restPose.set(1)
                flcShape.degree.set(1)
                flcShape.rename(self.rootObj.name() + '_flc')
                flcParent = flcShape.getParent()
                pm.parent(flcParent, self.hairSystemGrp)
            except:
                pm.warning('couldnt find follicle ')

            try:
                outCurveShape = pm.listConnections('%s.outCurve' % flcShape, s=False)[0]
                outCurveShape.rename(self.rootObj.name() + '_dyn_crv')
                outCurveParent = outCurveShape.getParent()

                pm.parent(outCurveParent, self.hairSystemGrp)
            except:
                pm.warning('couldnt find out curve ')

            try:
                hairSystem = pm.listConnections('%s.outHair' % flcShape, s=False)[0]
                hairSystem.rename(self.hairSystemUserName + '_hairSystem')
                pm.parent(hairSystem, self.hairSystemGrp)
                self.hairSystem = hairSystem
            except:
                pm.warning('couldnt find hairsystem ')

            flcParent = flcShape.getParent()
            print flcParent.name()
            flcParent.rename(hairSystem.name() + 'Follicles')

            outCurveParent = outCurveShape.getParent()
            outCurveParent.rename(hairSystem.name() + 'OutputCurves')
        else:
            assignHair = pm.ls(self.hairSystem)[0]

            pm.mel.eval('assignHairSystem %s' % assignHair)
            try:
                flcShape = pm.listConnections('%s.worldSpace' % drvCrvShape, s=False)[0]
                flcShape.pointLock.set(1)
                flcShape.restPose.set(1)
                flcShape.degree.set(1)
                flcShape.rename(self.rootObj.name() + '_flc')
                print flcShape.name()
            except:
                pm.warning('couldnt find follicle ')

            try:
                outCurveShape = pm.listConnections('%s.outCurve' % flcShape, s=False)[0]
                outCurveShape.rename(self.rootObj.name() + '_dyn_crv')
                print outCurveShape.name()
            except:
                pm.warning('couldnt find out curve ')

        dynChainIkHandle = \
        pm.ikHandle(sol='ikSplineSolver', sj=dynRootObj, ee=dynChain[-1], c=outCurveShape, ccv=False, roc=False,
                    pcv=False)[0]
        dynChainIkHandle.rename(self.rootObj.name() + '_ikHandle')
        pm.parent(dynChainIkHandle, self.hairSystemGrp)

        self.dynRootObj = dynRootObj
        pm.parent(self.dynRootObj, self.drvJntGrp)
        self.dynCrv = drvCrv

    def bdConnectChains(self):
        rootDesc = self.rootObj.listRelatives(type='joint', ad=True, f=True)
        rootDesc.append(self.rootObj)

        dynChainDesc = self.dynRootObj.listRelatives(type='joint', ad=True, f=True)
        dynChainDesc.append(self.dynRootObj)

        fkChainDesc = self.fkRootObj.listRelatives(type='joint', ad=True, f=True)
        fkChainDesc.append(self.fkRootObj)

        i = 0
        for jnt in dynChainDesc:
            pm.parentConstraint(jnt, rootDesc[i], w=1, mo=1)
            i += 1

        i = 0
        for jnt in fkChainDesc:
            pm.parentConstraint(jnt, rootDesc[i], w=0, mo=1)
            i += 1

    def bdAddFkCtrls(self):
        ctrlGrpAll = []

        ctrl = pm.circle(nr=[1, 0, 0], radius=10)[0]
        pm.delete(ctrl, ch=1)

        tempCtrl = ctrl.duplicate()[0]
        ctrlGrp = self.bdSetUpCtrl(ctrl, self.fkRootObj)
        ctrlGrpAll.append(ctrlGrp)
        pm.addAttr(ctrl, ln="dynamic", at='double', min=0, max=1, dv=0)
        ctrl.attr('dynamic').setKeyable(True)
        ctrl.overrideEnabled.set(1)
        ctrl.overrideColor.set(6)

        self.fkCtrlTop = ctrl

        fkChainDesc = self.fkRootObj.listRelatives(type='joint', ad=True, f=True)
        fkChainDesc.reverse()

        for jnt in fkChainDesc[:-1]:
            newCtrl = tempCtrl.duplicate()[0]
            newCtrl.overrideEnabled.set(1)
            newCtrl.overrideColor.set(6)
            ctrlGrp = self.bdSetUpCtrl(newCtrl, jnt)
            ctrlGrpAll.append(ctrlGrp)

        for i in range(len(ctrlGrpAll) - 1, 0, -1):
            pm.parent(ctrlGrpAll[i], ctrlGrpAll[i - 1].getChildren()[0])

        pm.parent(ctrlGrpAll[0], self.mainGrp)
        pm.delete([tempCtrl])

        pm.parentConstraint(self.fkCtrlTop, self.dynRootObj, mo=1)
        self.bdCreateFkDynSwitch()

    def bdCreateFkDynSwitch(self):
        parentCnstrAll = self.rootObj.listRelatives(type='parentConstraint', ad=True, f=True)
        reverseNode = pm.createNode('reverse', n=self.rootObj.name() + '_dyn_rev')
        self.fkCtrlTop.attr('dynamic').connect(reverseNode.inputX)

        for cnstr in parentCnstrAll:
            attrs = pm.listAttr(cnstr, ud=1)
            if attrs:
                dynAttrW = attrs[0]
                fkAttrW = attrs[1]

                self.fkCtrlTop.attr('dynamic').connect(cnstr.attr(dynAttrW))
                reverseNode.outputX.connect(cnstr.attr(fkAttrW))

    def bdSetUpCtrl(self, ctrl, jnt):
        ctrl.rename(jnt.name().replace('fk', 'ctrl'))
        ctrlGrp = pm.group([ctrl])
        ctrl.setTranslation([0, 0, 0], space='object')
        ctrl.setRotation([0, 0, 0], space='object')
        ctrlGrp.rename(ctrl.name() + '_grp')
        ctrlGrp.centerPivots()

        tempConstraint = pm.parentConstraint(jnt, ctrlGrp)
        pm.delete(tempConstraint)

        pm.parentConstraint(ctrl, jnt, mo=True)

        return ctrlGrp


class bdMakeDynamicUI(QtGui.QMainWindow):
    def __init__(self, parent=qt_handlers.get_maya_window()):
        super(bdMakeDynamicUI, self).__init__(parent)
        self.dynFk = ''

        self.setObjectName(mkDynamicWin)
        self.setWindowTitle('Create Dynamic FX Chain')

        self.setupUI()
        self.show()
        self.resize(300, 300)

    def setupUI(self):
        centralWidget = QtGui.QWidget()
        # centralWidget.setMinimumWidth(350)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.mainGroup = utils.TitledBox(self, title='Dynamic driven FK chain')

        self.hairSystemNameWidget = utils.LabelEdit(label='System name', labelWidth=120)
        self.hairSystemName = self.hairSystemNameWidget.edit
        self.hairSystemListWidget = utils.LabelComboBox(label='Hair Systems in scene', labelWidth=120)
        self.hairSystemsList = self.hairSystemListWidget.comboBOx

        self.createBtn = QtGui.QPushButton('Create system')
        self.bakeOnCtrl = QtGui.QPushButton('bake on controllers')

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.HLine)
        separator.setFrameShadow(QtGui.QFrame.Sunken)

        self.mainGroup.groupBoxLayout.addWidget(self.hairSystemNameWidget)
        self.mainGroup.groupBoxLayout.addWidget(self.hairSystemListWidget)
        self.mainGroup.groupBoxLayout.addWidget(self.createBtn)
        self.mainGroup.groupBoxLayout.addWidget(separator)
        self.mainGroup.groupBoxLayout.addWidget(self.bakeOnCtrl)

        mainLayout.addWidget(self.mainGroup)
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.bdPopulate_hairSystemsList()

        self.createBtn.clicked.connect(self.bdAddDynamicChain)
        # self.bakeOnCtrl.clicked.connect(self.bakeOnCtrls)

    @decorators.undoable
    def bdAddDynamicChain(self, *args):
        hairSystem = str(self.hairSystemsList.currentText())
        hairSystemName = str(self.hairSystemName.text())
        if hairSystem == "New":
            hairSystem = ''
        else:
            hairSystem = hairSystem.replace('Shape', '')
            hairSystemName = hairSystem.replace('_hairSystem', '')

        selection = pm.ls(sl=True)
        if len(selection) <> 1:
            pm.warning('Select the root joint')
        else:
            self.dynFk = bdMakeDynamic(start=selection[0], hairSystem=hairSystem, hairSystemName=hairSystemName)
            self.dynFk.createDynamicSystem()

        self.bdPopulate_hairSystemsList()

    def bdPopulate_hairSystemsList(self):
        self.hairSystemsList.clear()
        hairSystems = pm.ls(type='hairSystem')
        self.hairSystemsList.addItem('New')
        for hs in hairSystems:
            self.hairSystemsList.addItem(hs.name())

    def bdPickFkCtrl(self):
        selection = pm.ls(sl=True, type='transform')

        if selection:
            fkCtrl = selection[0]

        self.fkCtrlName.setText(fkCtrl.name())

    def bdAddFkCtrl(self):
        fkCtrl = str(self.fkCtrlName.text())
        fkCtrlObj = pm.ls(fkCtrl)[0]
        self.dynFk.bdAddFkCtrls(fkCtrlObj)


def createUI():
    if pm.window(mkDynamicWin, exists=True, q=True):
        pm.deleteUI(mkDynamicWin)

    bdMakeDynamicUI()
