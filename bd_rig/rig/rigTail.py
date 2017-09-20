import pymel.core as pm
import pymel.core.datatypes as dt
import maya.api.OpenMaya as om
import math


# hybrid IK spline / ribbon, allowing individual twist for the ik spline
class TailIkRbn():
    def __init__(self, *args, **kargs):
        self.ikJntList = []
        self.rigJntList = []
        self.ctrlList = []
        self.drvJntList = []
        self.cposList = []
        self.flcTransformList = []
        self.flcGrp = None
        self.rbnSrf = None
        self.jntGrp = None
        self.allCtrlGrp = None
        self.mainGrp = None
        self.mainCtrl = None
        self.ikCrv = None
        self.stretchRev = None
        self.ikHandle = None
        self.width = 0
        self.widthMult = 0.1

        self.name = kargs.setdefault('name', 'test')
        self.numCtrl = kargs.setdefault('numCtrl', 5)
        self.numJnt = kargs.setdefault('numJnt', 10)

        # Extras
        self.startJnt = ''
        self.endJnt = ''
        # start and end of ribbon , if a joint is selected ( that has only one child joint), will be recalculated in self.setStartEnd() function
        self.setStartEnd()

    def create(self):
        self.createGroups()
        self.createRbnSrf()

        self.createFlcs('u', 1)
        self.createIkChain()
        self.createIk()

        self.createCtrls()
        self.createMainCtrl()

        self.createSplineDrv()
        self.rigFlcs()

        # create the follicles on the surface and also the controllers
        '''
        #get the joint position on the surface and store it as an attribute
        #self.addJntPosAttr()
        self.constraintRigJnt()

        
    
        self.skinSrf()
        #self.addScale()
        '''

    def createGroups(self):
        pm.select(cl=1)
        self.mainGrp = pm.group(n=self.name + '_grp')
        pm.select(cl=1)
        self.jntGrp = pm.group(name=self.name + '_jnt_grp')
        pm.rotate(self.jntGrp, 0, -90, 0, r=1)
        pm.parent(self.jntGrp, self.mainGrp)
        pm.select(cl=1)
        self.allCtrlGrp = pm.group(n=self.name + '_ctrl_grp')
        pm.select(cl=1)

    def createSplineDrv(self):
        self.createDrvJnt()

        skinCls = pm.skinCluster(self.rbnSrf, self.drvJntList, tsb=1, ih=1, bindMethod=0, maximumInfluences=1,
                                 dropoffRate=10.0)

        for i in range(len(self.drvJntList)):
            if i == 0:
                pm.skinPercent(skinCls.name(), self.rbnSrf.name() + '.cv[0:1][0:3]', tv=[(self.drvJntList[i], 1)])
            elif i > 0 and i < self.numJnt - 1:
                pm.skinPercent(skinCls.name(), self.rbnSrf.name() + '.cv[' + str(i + 1) + '][0:3]',
                               tv=[(self.drvJntList[i], 1)])
            elif i == self.numJnt - 1:
                pm.skinPercent(skinCls.name(), self.rbnSrf.name() + '.cv[' + str(i + 1) + ':' + str(i + 2) + '][0:3]',
                               tv=[(self.drvJntList[i], 1)])

    def createDrvJnt(self):
        drvJntGrpList = []
        i = 0
        for ctrl in self.ctrlList:
            pos = ctrl.getTranslation(space='world')
            pm.select(cl=1)
            drvJnt = pm.joint(name=self.name + '_' + (str(i)).zfill(2) + '_DRV')
            drvJntGrp = pm.group(drvJnt, name=drvJnt.name() + '_grp')
            drvJntGrpList.append(drvJntGrp)
            drvJntGrp.setTranslation(pos, space='world')
            self.drvJntList.append(drvJnt)
            pm.parentConstraint(ctrl, drvJntGrp)
            i += 1

        pm.select(cl=1)

        allDrvJntGrp = pm.group(drvJntGrpList, n=self.name + '_drv_jnt_grp')
        pm.parent(allDrvJntGrp, self.mainGrp)

    def createIkChain(self):
        print 'creating joint chains'
        ikJntList = []

        startJntVec = om.MVector(self.start[0], self.start[1], self.start[2])
        endJntVec = om.MVector(self.end[0], self.end[1], self.end[2])
        diffVec = endJntVec - startJntVec

        # calculate the witdth of the surface as a fraction of the total joint chain length
        jntChainLength = diffVec.length()
        self.width = jntChainLength * self.widthMult

        crvPoints = []

        for i in range(self.numJnt + 1):
            vec = startJntVec + diffVec * (i * 1.0 / self.numJnt)
            jntPos = [vec.x, vec.y, vec.z]

            ikJnt = pm.joint(p=jntPos, name=self.name + '_' + (str(i)).zfill(2) + '_IK')
            ikJntList.append(ikJnt)

        pm.joint(ikJntList[0], e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        ikJntList[-1].jointOrient.set([0, 0, 0])

        self.ikJntList = ikJntList
        pm.parent(self.ikJntList[0], self.jntGrp)
        pm.select(cl=1)

    def createMainCtrl(self):
        pos = self.ikJntList[0].getTranslation(space='world')

        ctrl = pm.circle(name=self.name + '_main_ctrl', nr=[1, 0, 0], radius=self.width * 2)[0]
        pm.delete(ctrl, ch=1)

        ctrlGrp = pm.group(ctrl, name=ctrl.name() + '_grp')
        pm.parent(ctrlGrp, self.mainGrp)

        ctrlGrp.setTranslation(pos, space='world')
        pm.parentConstraint(ctrl, self.jntGrp, mo=1)

        self.mainCtrl = ctrl
        pm.addAttr(self.mainCtrl, shortName='stretch', minValue=0.0, maxValue=1.0, defaultValue=0.0, keyable=1)
        self.stretchRev = pm.shadingNode('reverse', name=self.name + '_stretch_rev', asUtility=1)
        self.mainCtrl.stretch >> self.stretchRev.inputX

        pm.parentConstraint(self.mainCtrl, self.allCtrlGrp, mo=1)

    def createRbnSrf(self):
        startJntVec = om.MVector(self.start[0], self.start[1], self.start[2])
        endJntVec = om.MVector(self.end[0], self.end[1], self.end[2])
        diffVec = endJntVec - startJntVec

        # calculate the witdth of the surface as a fraction of the total joint chain length
        jntChainLength = diffVec.length()
        self.width = jntChainLength * self.widthMult

        crvPoints = []

        for i in range(self.numCtrl):
            vec = startJntVec + diffVec * (i * 1.0 / (self.numCtrl - 1))
            crvPoints.append([vec.x, vec.y, vec.z])

        tmp = pm.curve(n=self.name + '_crv1', d=1, p=crvPoints)
        crv1 = pm.ls(tmp)[0]
        crv1.setPivots(self.start)
        crv2 = pm.duplicate(crv1)[0]

        self.offsetCrv(crv1, -1.0 * self.width / 2)
        self.offsetCrv(crv2, 1.0 * self.width / 2)

        tmpLoftSrf = pm.loft(crv1, crv2, ch=0, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=1, n=self.name + "_tmp")[0]
        rebuiltLoftSrf = \
        pm.rebuildSurface(ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kc=0, su=0, du=3, sv=0, dv=1, fr=0, dir=2,
                          n=self.name + "_srf")[0]
        rebuiltLoftSrf.setPivots(rebuiltLoftSrf.c.get())
        self.rbnSrf = rebuiltLoftSrf
        pm.delete(self.rbnSrf, ch=1)

        pm.delete([crv1, crv2, tmpLoftSrf])
        pm.parent(self.rbnSrf, self.mainGrp)

    def createIk(self):
        # create the curve for the ik
        self.ikCrv = pm.duplicateCurve(self.rbnSrf + ".v[0.5]", ch=1, rn=0, local=0, name=self.name + '_ik_crv')[0]
        print self.ikCrv

        # create the ik
        self.ikHandle = \
        pm.ikHandle(sj=self.ikJntList[0], ee=self.ikJntList[-1], c=self.ikCrv, ccv=False, sol='ikSplineSolver',
                    name=self.name + '_ikspline')[0]
        pm.select(cl=1)
        pm.parent(self.ikHandle, self.mainGrp)
        pm.parent(self.ikCrv, self.mainGrp)
        pm.select(cl=1)

    def createCtrls(self):
        ctrlList = []

        startJntVec = om.MVector(self.start[0], self.start[1], self.start[2])
        endJntVec = om.MVector(self.end[0], self.end[1], self.end[2])
        diffVec = endJntVec - startJntVec
        pm.select(cl=1)

        for i in range(self.numCtrl):
            vec = startJntVec + diffVec * (i * 1.0 / (self.numCtrl - 1))
            pos = [vec.x, vec.y, vec.z]

            ctrl = self.addCtrl(i)
            self.ctrlList.append(ctrl)
            ctrlMainGrp = self.getCtrlMainGrp(ctrl)
            ctrlMainGrp.setTranslation(pos)
            pm.parent(ctrlMainGrp, self.allCtrlGrp)

        pm.parent(self.allCtrlGrp, self.mainGrp)

    def createFlcs(self, direction, ends):
        folicles = []

        pm.select(cl=1)

        for i in range(self.numJnt + 1):
            pm.select(cl=1)
            flcShape = pm.createNode('follicle', name=self.rbnSrf.name() + '_' + str(i).zfill(2) + '_flcShape')
            flcTransform = flcShape.getParent()
            flcTransform.rename(flcShape.name().replace('flcShape', 'flc'))
            folicles.append(flcTransform)

            srfShape = pm.listRelatives(self.rbnSrf)[0]
            srfShape.local.connect(flcShape.inputSurface)
            srfShape.worldMatrix[0].connect(flcShape.inputWorldMatrix)

            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)
            # flcShape.flipDirection.set(1)

            flcShape.parameterU.set((i * 1.0) / self.numJnt)
            flcShape.parameterV.set(0.5)

        pm.select(cl=1)
        self.flcGrp = pm.group(folicles, n=self.rbnSrf.name() + '_flc_grp')
        pm.select(cl=1)
        pm.parent(self.flcGrp, self.mainGrp)
        self.flcTransformList = folicles

    def getCtrlMainGrp(self, ctrl):
        chainParents = []
        parent = pm.listRelatives(ctrl, p=1)
        chainParents.append(parent)
        while parent:
            parent = pm.listRelatives(parent, p=1)
            chainParents.append(parent)

        chainParents.pop()

        return chainParents[-1][0]

    def addCtrl(self, num):
        ctrl = pm.circle(name=self.name + '_ik_' + str(num).zfill(2) + '_ctrl', nr=[1, 0, 0], radius=self.width * 0.8)[
            0]
        pm.delete(ctrl, ch=1)

        ctrlGrp = pm.group(ctrl, name=ctrl.name() + '_grp')

        return ctrl

    def addJntPosAttr(self):
        for jnt in self.ikJntList:
            cposNode = pm.shadingNode('closestPointOnSurface', asUtility=True)
            decMtx = pm.shadingNode('decomposeMatrix', asUtility=True)

            self.rbnSrf.getShape().worldSpace[0].connect(cposNode.inputSurface)
            decMtx.outputTranslate.connect(cposNode.inPosition)

            jnt.worldMatrix[0].connect(decMtx.inputMatrix)
            pm.addAttr(jnt, shortName='jointPosition', longName='jointPosition', defaultValue=0, minValue=0, maxValue=1)
            jntPos = cposNode.parameterU.get()
            jnt.jointPosition.set(jntPos)

            pm.delete([cposNode, decMtx])

    def setStartEnd(self):
        self.start = [-50.0, 0.0, 0.0]
        self.end = [50.0, 0.0, 0.0]

        selected = pm.ls(sl=1)
        if selected:
            if len(selected) == 1:
                if selected[0].type() == 'joint':
                    self.startJnt = selected[0]
                    children = self.startJnt.getChildren(type='joint')
                    self.endJnt = children[0]

                    start = self.startJnt.getTranslation(space='world')
                    end = self.endJnt.getTranslation(space='world')

                    startJntVec = om.MVector(start[0], start[1], start[2])
                    endJntVec = om.MVector(end[0], end[1], end[2])
                    diffVec = endJntVec - startJntVec
                    length = diffVec.length()

                    self.start = [length * - 0.5, 0, 0]
                    self.end = [length * 0.5, 0, 0]

    def offsetCrv(self, crv, offset):
        startPos = self.start
        tmpLoc = pm.spaceLocator(name='tmpLoc' + crv.name())

        tmpLoc.setTranslation([self.start[0], self.start[1], self.start[2] + offset])

        locPos = tmpLoc.getTranslation(space='world')
        locPosVec = om.MVector(locPos)
        crvPos = crv.getRotatePivot(space='world')
        crvPosVec = om.MVector(crvPos)
        newCrvVec = crvPosVec - locPosVec

        crv.setTranslation([newCrvVec.x, newCrvVec.y, newCrvVec.z], space='world')
        pm.delete(tmpLoc)

    def addRigJnt(self, flc):
        flcJoint = pm.joint()
        flcJoint.rename(flc.name().replace('flc', 'RIG'))
        pm.parent(flcJoint, flc)
        flcJoint.setTranslation([0, 0, 0])
        self.rigJntList.append(flcJoint)

    def rigFlcs(self):
        for flc in self.flcTransformList:
            self.addRigJnt(flc)

            index = self.flcTransformList.index(flc)
            ikJoint = self.ikJntList[index]
            # get the world position of the ik joint using a vectorProduct node
            vp = pm.shadingNode('vectorProduct', asUtility=1, name=ikJoint + '_ws_pmm')
            # use a closestPointOnSurface to get the coordinates on the surface of the closesest point from the ik joint
            cps = pm.shadingNode('closestPointOnSurface', asUtility=1, name=ikJoint + '_cps')
            # the blendTwoAttr is used to blend the flc position between its default position and the ik joints the 
            bta = pm.shadingNode('blendTwoAttr', asUtility=1, name=flc + '_drv_bta')

            vp.operation.set(4)
            ikJoint.worldMatrix >> vp.matrix
            ikJoint.rotatePivot >> vp.input1

            vp.output >> cps.inPosition
            self.rbnSrf.worldSpace[0] >> cps.inputSurface

            # get the default U parameter of the follicle to store it in the blendAttr input
            flcU = flc.getShape().parameterU.get()

            bta.input[0].set(flcU)

            cps.parameterU >> bta.input[1]
            self.mainCtrl.stretch >> bta.attributesBlender

            bta.output >> flc.getShape().parameterU
