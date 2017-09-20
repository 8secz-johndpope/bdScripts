import pymel.core as pm

from ..utils import libCtrl as controller

reload(controller)

import rigNode as RN

reload(RN)

# ------- Global suffixes ------
BNDJNT = RN.BNDJNT
FKJNT = RN.FKJNT
IKJNT = RN.IKJNT
DRVJNT = RN.DRVJNT
CTRL = RN.CTRL
CTRLGRP = RN.CTRLGRP


# ------------------------------

class RigArm(RN.RigNode):
    def __init__(self, *args, **kargs):
        super(RigArm, self).__init__(*args, **kargs)
        # use 4 joint for the arm
        self.armNumMain = 4
        self.armUpperRoll = 0
        self.armlowerRoll = 0
        # self.side = kargs.setdefault('side','L')
        # ----------------------------
        self.armCtrls = {}
        self.armIkfkSwitchCtrl = ''
        # -----------------------------

    def rigIt(self):
        self.buildBndChain()
        # self.fkChain = self.buildDrv('FK')
        # self.ikChain = self.buildDrv('IK')
        # self.bdRigIkArm(self.side)
        # self.bndChainConnect()

    def bndChainConnect(self):
        ctrl = controller.Controller(ctrlName=self.side + 'Arm_ikfk_' + CTRL, target=self.rnBndChain[2], ctrlType='box')
        self.ikfkSwitchCtrl = ctrl.buildController()

        ikfkSwitchCtrlParent = pm.listConnections('%s.parent' % self.ikfkSwitchCtrl)[0]
        pm.parentConstraint(self.rnBndChain[2], ikfkSwitchCtrlParent)

        pm.addAttr(self.ikfkSwitchCtrl, ln='IKFK', nn='IKFK', at='double', min=0, max=1, dv=1, k=1)

        for i in range(len(self.rnBndChain)):
            self.createBlend(self.rnBndChain[i], self.fkChain[i], self.ikChain[i])

    def createBlend(self, bindJnt, fkJnt, ikJnt):
        blendColorPos = pm.createNode('blendColors', name=bindJnt.name().replace(BNDJNT, 'POS_BC'))
        blendColorRot = pm.createNode('blendColors', name=bindJnt.name().replace(BNDJNT, 'ROT_BC'))
        blendColorScl = pm.createNode('blendColors', name=bindJnt.name().replace(BNDJNT, 'SCL_BC'))

        pm.connectAttr(self.ikfkSwitchCtrl + '.IKFK', blendColorPos.name() + '.blender')
        pm.connectAttr(self.ikfkSwitchCtrl + '.IKFK', blendColorRot.name() + '.blender')
        pm.connectAttr(self.ikfkSwitchCtrl + '.IKFK', blendColorScl.name() + '.blender')

        pm.connectAttr(fkJnt + '.translate', blendColorPos.name() + '.color1')
        pm.connectAttr(ikJnt + '.translate', blendColorPos.name() + '.color2')
        pm.connectAttr(blendColorPos.name() + '.output', bindJnt + '.translate')

        pm.connectAttr(fkJnt + '.rotate', blendColorRot.name() + '.color1')
        pm.connectAttr(ikJnt + '.rotate', blendColorRot.name() + '.color2')
        pm.connectAttr(blendColorRot.name() + '.output', bindJnt + '.rotate')

        pm.connectAttr(fkJnt + '.scale', blendColorScl.name() + '.color1')
        pm.connectAttr(ikJnt + '.scale', blendColorScl.name() + '.color2')
        pm.connectAttr(blendColorScl.name() + '.output', bindJnt + '.scale')

    def bdRigIkArm(self, side):
        ikChain = self.ikChain

        armIk = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=ikChain[0], endEffector=ikChain[2],
                            name=side + 'Arm_ikHandle')[0]
        handIk = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=ikChain[2], endEffector=ikChain[3],
                             name=side + 'Palm_ikHandle')[0]

        ikHandlesGrp = pm.group([armIk, handIk], n=side + 'Arm_ikHandles_GRP')
        wristPos = ikChain[2].getTranslation(space='world')
        ikHandlesGrp.setPivots(wristPos)
        '''
        pvAnim = pm.ls(side + '_elbow_ik_anim', type='transform')[0]
        if pvAnim:
            pm.poleVectorConstraint(pvAnim,armIk[0])

        '''
        ikAnimCtrl = pm.ls(side + 'Arm_ik_ctrl', type='transform')[0]
        pm.parentConstraint(ikAnimCtrl, ikHandlesGrp, mo=True)

    def bdScaleChain(side):
        pm.select(cl=True)
        ikAnimCon = pm.ls(side + '_Hand_IK_CON', type='transform')[0]
        armBonesNames = ['Shoulder', 'Elbow', 'Hand']

        scaleBones = []
        for bone in armBonesNames:
            scaleBone = pm.ls(side + '_' + bone + '_SCL')[0]
            scaleBones.append(scaleBone)

        armBones = []
        for bone in armBonesNames:
            armBone = pm.ls(side + '_' + bone + '_IK')[0]
            armBones.append(armBone)

        print scaleBones
        print armBones

        distance1 = pm.createNode('distanceBetween', name=side + '_uppArm_length')
        distance2 = pm.createNode('distanceBetween', name=side + '_lowArm_length')
        distanceStraight = pm.createNode('distanceBetween', name=side + '_straightArm_length')
        adlDistance = pm.createNode('addDoubleLinear', name=side + '_armLength_ADL')
        condDistance = pm.createNode('condition', name=side + '_armLength_CND')
        condDistance.colorIfTrueR.set(1)
        condDistance.secondTerm.set(1)
        condDistance.operation.set(5)

        mdScaleFactor = pm.createNode('multiplyDivide', name=side + '_arm_scaleFactor_MD')
        mdScaleFactor.operation.set(2)

        scaleBones[0].rotatePivotTranslate.connect(distance1.point1)
        scaleBones[1].rotatePivotTranslate.connect(distance1.point2)
        scaleBones[0].worldMatrix.connect(distance1.inMatrix1)
        scaleBones[1].worldMatrix.connect(distance1.inMatrix2)

        scaleBones[1].rotatePivotTranslate.connect(distance2.point1)
        scaleBones[2].rotatePivotTranslate.connect(distance2.point2)
        scaleBones[1].worldMatrix.connect(distance2.inMatrix1)
        scaleBones[2].worldMatrix.connect(distance2.inMatrix2)

        scaleBones[0].rotatePivotTranslate.connect(distanceStraight.point1)
        ikAnimCon.rotatePivotTranslate.connect(distanceStraight.point2)
        scaleBones[0].worldMatrix.connect(distanceStraight.inMatrix1)
        ikAnimCon.worldMatrix.connect(distanceStraight.inMatrix2)

        distance1.distance.connect(adlDistance.input1)
        distance2.distance.connect(adlDistance.input2)

        adlDistance.output.connect(mdScaleFactor.input2X)
        distanceStraight.distance.connect(mdScaleFactor.input1X)

        mdScaleFactor.outputX.connect(condDistance.firstTerm)
        mdScaleFactor.outputX.connect(condDistance.colorIfFalseR)

        condDistance.outColorR.connect(armBones[0].scaleX)
        condDistance.outColorR.connect(armBones[1].scaleX)

        # def bdRigArm(side):
        # bdBuildDrvChain(side,'FK')
        # bdRigIkArm(side)
        # bdConnectChains()
