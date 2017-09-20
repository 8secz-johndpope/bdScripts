import pymel.core as pm

import pymel.core.datatypes as dt
import maya.OpenMaya as OpenMaya


class Controller(object):
    def __init__(self, *args, **kargs):
        self.ctrlName = kargs.setdefault('name', '')
        self.ctrlTarget = kargs.setdefault('target', '')
        self.ctrlScale = kargs.setdefault('scale', 3)
        self.ctrlShape = kargs.setdefault('shape', 'circle')
        self.ctrlAxis = kargs.setdefault('axis', [0, 1, 0])
        self.ctrlGrp = None
        self.ctrlPos = [0, 0, 0]
        self.ctrlRot = [0, 0, 0]
        self.ctrlPoints = []
        self.ctrlFolder = ''

    def addExtraGroup(self, name):
        pm.group(self.ctrlName, name=self.ctrlName + '_' + name)

    @classmethod
    def pole_vector_pos(cls, ik_1, ik_2, ik_3):
        ik_pos_1 = pm.xform(ik_1, q=1, t=1, ws=1)
        ik_pos_2 = pm.xform(ik_2, q=1, t=1, ws=1)
        ik_pos_3 = pm.xform(ik_3, q=1, t=1, ws=1)

        ik_vec_1 = OpenMaya.MVector(ik_pos_1[0], ik_pos_1[1], ik_pos_1[2])
        ik_vec_2 = OpenMaya.MVector(ik_pos_2[0], ik_pos_2[1], ik_pos_2[2])
        ik_vec_3 = OpenMaya.MVector(ik_pos_3[0], ik_pos_3[1], ik_pos_3[2])

        start_end_vec = ik_vec_3 - ik_vec_1
        start_end_vec_half = start_end_vec * 0.5
        start_end_mid_vec = ik_vec_1 + start_end_vec_half

        pole_vec = (ik_vec_2 - start_end_mid_vec) * 2 + ik_vec_2

        return [pole_vec.x, pole_vec.y, pole_vec.z]

    def buildController(self):
        if self.ctrlName == '':
            pm.warning('No name or target specified for building the controller')
            return
        if self.ctrlShape == 'circle':
            self.buildCircleController()
        elif self.ctrlShape == 'box':
            self.buildBoxController()
        elif self.ctrlShape == 'square':
            self.bdBuildSquareController()
        elif self.ctrlShape == 'joint':
            self.bdBuildSphereController()

        self.setPosition()

    def setPosition(self):
        if self.ctrlTarget != '':
            findNode = pm.ls(self.ctrlTarget)
            if findNode:
                node = findNode[0]
                self.ctrlPos = node.getTranslation(space='world')
                self.ctrlGrp.setTranslation(self.ctrlPos, space='world')

    def buildBoxController(self):
        defaultPointsList = [(1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1),
                             (-1, 1, 1)]
        pointsList = []
        for p in defaultPointsList:
            pointsList.append((p[0] * self.ctrlScale, p[1] * self.ctrlScale, p[2] * self.ctrlScale))

        knotsList = [i for i in range(16)]
        curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3],
                       pointsList[7], pointsList[4], pointsList[5], pointsList[6],
                       pointsList[7], pointsList[3], pointsList[0], pointsList[4],
                       pointsList[5], pointsList[1], pointsList[2], pointsList[6]]

        ctrl = pm.curve(d=1, p=curvePoints, k=knotsList)
        ctrl = pm.rename(ctrl, self.ctrlName)
        ctrlGrp = pm.group(ctrl, n=str(self.ctrlName + '_grp'))

        # pm.addAttr(ctrl,ln='parent',at='message')
        # pm.connectAttr(ctrlGrp.name() + '.message' , ctrl.name() + '.parent')

        pm.move(ctrlGrp, self.ctrlPos[0], self.ctrlPos[1], self.ctrlPos[2])
        pm.rotate(ctrlGrp, self.ctrlRot[0], self.ctrlRot[1], self.ctrlRot[2])
        self.ctrlGrp = ctrlGrp

    def buildCircleController(self):
        pm.select(cl=1)
        ctrl = pm.circle(name=self.ctrlName, c=[0, 0, 0], nr=self.ctrlAxis, ch=0, radius=self.ctrlScale)[0]
        ctrlGrp = pm.group(ctrl, n=str(self.ctrlName + '_grp'))
        pm.select(cl=1)
        pm.move(ctrlGrp, self.ctrlPos[0], self.ctrlPos[1], self.ctrlPos[2])
        pm.rotate(ctrlGrp, self.ctrlRot[0], self.ctrlRot[1], self.ctrlRot[2])

        self.ctrlGrp = ctrlGrp

    def bdBuildSquareController(self):
        defaultPointsList = [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0)]
        pointsList = []

        for p in defaultPointsList:
            pointsList.append((p[0] * self.ctrlScale, p[1] * self.ctrlScale, p[2] * self.ctrlScale))

        curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3], pointsList[0]]

        ctrl = pm.curve(d=1, p=curvePoints)
        ctrl.rename(self.ctrlName)
        ctrlGrp = pm.group(ctrl, n=self.ctrlName + '_grp')
        pm.move(ctrlGrp, self.ctrlPos[0], self.ctrlPos[1], self.ctrlPos[2], ws=True)
        pm.rotate(ctrlGrp, self.ctrlRot[0], self.ctrlRot[1], self.ctrlRot[2])

        self.ctrlGrp = ctrlGrp

    def bdBuildSphereController(self):
        circleA = pm.circle(n=self.ctrlName + 'A', nr=(0, 1, 0), c=(0, 0, 0), radius=self.ctrlScale)
        circleB = pm.circle(n=self.ctrlName + 'B', nr=(1, 0, 0), c=(0, 0, 0), radius=self.ctrlScale)
        circleC = pm.circle(n=self.ctrlName + 'C', nr=(0, 0, 1), c=(0, 0, 0), radius=self.ctrlScale)

        circleBShape = pm.listRelatives(circleB[0], c=True)
        circleCShape = pm.listRelatives(circleC[0], c=True)
        pm.parent(circleBShape[0], circleA[0], r=True, s=True)
        pm.parent(circleCShape[0], circleA[0], r=True, s=True)
        pm.delete(circleB, circleC)
        ctrl = pm.rename(circleA[0], self.ctrlName)
        ctrlGrp = pm.group(ctrl, n=self.ctrlName + '_grp')

        pm.move(ctrlGrp, self.ctrlPos[0], self.ctrlPos[1], self.ctrlPos[2])
        pm.rotate(ctrlGrp, self.ctrlRot[0], self.ctrlRot[1], self.ctrlRot[2])

        self.ctrlGrp = ctrlGrp


def bdAddExtraGrp():
    returnMessage = ''
    selection = pm.ls(sl=1)
    message = ''
    if selection:
        controllers = selection

        for ctrl in controllers:
            pm.select(cl=True)
            extraGrp = pm.group(name=ctrl.name() + '_grp')
            ctrlParent = ctrl.getParent()
            tmp = pm.parentConstraint(ctrl, extraGrp, mo=0)
            pm.delete(tmp)
            pm.parent(extraGrp, ctrlParent)
            pm.parent(ctrl, extraGrp)
            returnMessage += 'Added grp for ctrl %s \n ' % ctrl

    return message


def bdAddAttribute(obj, a, attrType):
    pm.addAttr(obj, ln=a, at=attrType)
    pm.setAttr((obj + "." + a), e=True, keyable=True)


def bdAddAttributeMinMax(obj, attrList, attrType, minVal, maxVal, defVal):
    for a in attrList:
        pm.addAttr(obj, ln=a, at=attrType, min=minVal, max=maxVal, dv=defVal)
        pm.setAttr((obj + "." + a), e=True, keyable=True)


def bdAddSeparatorAttr(obj, attr):
    pm.addAttr(obj, ln=attr, nn='------', at='enum', en=[attr])
    # pm.addAttr(obj ,ln=attr,nn=attr,at='bool'  )
    pm.setAttr((obj + "." + attr), keyable=True)
    pm.setAttr((obj + "." + attr), lock=True)


def bdCreateGroup(objects, grpName, pivot, rot=False):
    grp = pm.group(objects, n=grpName)
    footJntPos = pm.xform(pivot, q=True, ws=True, t=True)
    pm.move(footJntPos[0], footJntPos[1], footJntPos[2], grp + '.rp', grp + '.sp')
    return grp


def bdCleanUpController(object, attrList, lockFlag=True):
    for attr in attrList:
        pm.setAttr(object + '.' + attr, lock=lockFlag, keyable=False, channelBox=False)


def bdCreateOffsetLoc(destination, name):
    loc = pm.spaceLocator(n=name)
    destPos = destination.getScalePivot()
    loc.setTranslation(destPos)
    locGrp = pm.duplicate(loc, name=str(loc[0] + "_GRP"))
    pm.parent(loc, locGrp)


def bdAddFkCtrls(scale=1, color=1):
    selection = pm.ls(sl=1, type='joint')
    pm.select(cl=1)
    if selection:
        for rootJnt in selection:
            chainJnt = rootJnt.listRelatives(type='joint', ad=True, f=True)
            # chainJnt.reverse()
            chainJnt.append(rootJnt)

            for jnt in chainJnt:
                pos = jnt.getTranslation(space='world')
                rot = jnt.getRotation(space='world')
                pm.select(cl=1)
                ctrl = pm.circle(name=jnt.name() + '_ctrl', c=[0, 0, 0], nr=[1, 0, 0], ch=0, radius=scale)[0]
                ctrlGrp = pm.group(ctrl, n=ctrl.name() + '_grp')
                pm.select(cl=1)
                ctrlGrp.setTranslation(pos, space='world')
                ctrlGrp.setRotation(rot, space='world')

                ctrl.getShape().overrideEnabled.set(1)
                ctrl.getShape().overrideColor.set(color)


def bdReplaceShape():
    selection = pm.ls(sl=1)
    if selection:
        source = selection[0]
        dest = selection[1:]

        for target in dest:
            sourceDup = pm.duplicate(selection[0])[0]
            sourceShapes = sourceDup.getShapes()

            tempConstraint = pm.parentConstraint(target, sourceDup, mo=0)
            pm.delete(tempConstraint)
            pm.makeIdentity(sourceDup, r=1, t=1, s=1)
            targetShapes = target.getShapes()
            oc = 0
            for shape in targetShapes:
                oc = shape.overrideColor.get()
                pm.delete(shape)
            for shape in sourceShapes:
                pm.parent(shape, target, r=1, s=1)
                shape.rename(target.name() + 'Shape')
                shape.overrideColor.set(oc)

            pm.delete(sourceDup)


# pymel
def bdMirrorCtrlPymel():
    selection = pm.ls(sl=True)
    if selection:
        try:
            source, target = pm.ls(sl=True)
        except:
            pm.warning('Select source and target controller')
            return

        sourceShape = source.getShape()
        if sourceShape.type() != 'nurbsCurve':
            pm.error('Selected source is not nurbs curve')
            return

        targetCvsPos = [(dt.Point(-x.x, x.y, x.z)) for x in sourceShape.getCVs(space='world')]

        targetShape = target.getShape()

        if targetShape.type() != 'nurbsCurve':
            pm.error('Selected target is not nurbs curve')
            return
        targetShape.setCVs(targetCvsPos, space='world')
        targetShape.updateCurve()


    else:
        print 'Select source and target controller'


def bdMirrorCtrlApi():
    mDagPath = OpenMaya.MDagPath()
    mSelList = OpenMaya.MSelectionList()

    OpenMaya.MGlobal.getActiveSelectionList(mSelList)
    srcCurvePointAray = OpenMaya.MPointArray()
    destCurvePointAray = OpenMaya.MPointArray()

    numSel = mSelList.length()

    if numSel == 2:

        mSelList.getDagPath(0, mDagPath)

        if mDagPath.hasFn(OpenMaya.MFn.kNurbsCurve):
            srcCurveFn = OpenMaya.MFnNurbsCurve(mDagPath)
            srcCurveFn.getCVs(srcCurvePointAray, OpenMaya.MSpace.kWorld)

            mSelList.getDagPath(1, mDagPath)
            if mDagPath.hasFn(OpenMaya.MFn.kNurbsCurve):
                destCurveFn = OpenMaya.MFnNurbsCurve(mDagPath)
                for i in range(srcCurvePointAray.length()):
                    destCurvePointAray.append(
                        OpenMaya.MPoint(-srcCurvePointAray[i].x, srcCurvePointAray[i].y, srcCurvePointAray[i].z))
                destCurveFn.setCVs(destCurvePointAray, OpenMaya.MSpace.kWorld)
                destCurveFn.updateCurve()


def bdMatchCtrlsApi():
    mDagPath = OpenMaya.MDagPath()
    mSelList = OpenMaya.MSelectionList()

    OpenMaya.MGlobal.getActiveSelectionList(mSelList)
    srcCurvePointAray = OpenMaya.MPointArray()
    destCurvePointAray = OpenMaya.MPointArray()

    numSel = mSelList.length()

    if numSel == 2:

        mSelList.getDagPath(0, mDagPath)

        if mDagPath.hasFn(OpenMaya.MFn.kNurbsCurve):
            srcCurveFn = OpenMaya.MFnNurbsCurve(mDagPath)
            srcCurveFn.getCVs(srcCurvePointAray, OpenMaya.MSpace.kWorld)

            mSelList.getDagPath(1, mDagPath)
            if mDagPath.hasFn(OpenMaya.MFn.kNurbsCurve):
                destCurveFn = OpenMaya.MFnNurbsCurve(mDagPath)
                for i in range(srcCurvePointAray.length()):
                    destCurvePointAray.append(
                        OpenMaya.MPoint(srcCurvePointAray[i].x, srcCurvePointAray[i].y, srcCurvePointAray[i].z))
                destCurveFn.setCVs(destCurvePointAray, OpenMaya.MSpace.kWorld)
                destCurveFn.updateCurve()


# def bdReplaceShape():
#	selection = pm.ls(sl=1)
#	if len(selection) != 2:
#		return 'Select two curves'
#	else:
#		if selection[0].getShape().type() =='nurbsCurve' and selection[1].getShape().type() =='nurbsCurve':
#			srcTransform = selection[0]
#			destTransform = selection[1]
#			pm.ls(sl=1)
#			srcTransformPos = srcTransform.getTranslation(space='world') 
#			srcTransformRot = srcTransform.getRotation(space='world') 

#			destTransform.setTranslation(srcTransformPos,space='world') 
#			destTransform.setRotation(srcTransformRot,space='world') 

#			srcShapeName = srcTransform.getShape().name()
#			srcShapeCol = srcTransform.getShape().overrideColor.get()

#			destShape = destTransform.getShape()
#			pm.parent(destShape,srcTransform,r=1,s=1)
#			pm.delete(srcTransform.getShape())
#			destShape.rename(srcShapeName)
#			destShape.overrideEnabled.set(1)
#			destShape.overrideColor.set(srcShapeCol)
#		else:
#			return 'Select two curves'
def bdCreatNullParentGrp():
    selection = pm.ls(sl=1)
    if selection:
        ctrl = selection[0]
        pm.select(cl=1)
        nullGrp = pm.group(n=ctrl.name() + '_ZERO')
        temp = pm.parentConstraint(ctrl, nullGrp)
        pm.delete(temp)
        ctrlParent = ctrl.getParent()
        pm.parent(nullGrp, ctrlParent)
        pm.parent(ctrl, nullGrp)


def bdTrsUnlock():
    selection = pm.ls(sl=1)
    for s in selection:
        if s.type() == 'transform':
            pm.setAttr(s.name() + '.translateX', k=True, lock=False)
            pm.setAttr(s.name() + '.translateY', k=True, lock=False)
            pm.setAttr(s.name() + '.translateZ', k=True, lock=False)

            pm.setAttr(s.name() + '.rotateX', k=True, lock=False)
            pm.setAttr(s.name() + '.rotateY', k=True, lock=False)
            pm.setAttr(s.name() + '.rotateZ', k=True, lock=False)

            pm.setAttr(s.name() + '.scaleX', k=True, lock=False)
            pm.setAttr(s.name() + '.scaleY', k=True, lock=False)
            pm.setAttr(s.name() + '.scaleZ', k=True, lock=False)


def bdTrsLock():
    selection = pm.ls(sl=1)
    for s in selection:
        if s.type() == 'transform':
            pm.setAttr(s.name() + '.translateX', k=0, lock=1)
            pm.setAttr(s.name() + '.translateY', k=0, lock=1)
            pm.setAttr(s.name() + '.translateZ', k=0, lock=1)

            pm.setAttr(s.name() + '.rotateX', k=0, lock=1)
            pm.setAttr(s.name() + '.rotateY', k=0, lock=1)
            pm.setAttr(s.name() + '.rotateZ', k=0, lock=1)

            pm.setAttr(s.name() + '.scaleX', k=0, lock=1)
            pm.setAttr(s.name() + '.scaleY', k=0, lock=1)
            pm.setAttr(s.name() + '.scaleZ', k=0, lock=1)
