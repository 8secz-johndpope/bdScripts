import pymel.core as pm
import json, os, random, re
import traceback
from functools import wraps


import pymel.core.datatypes as dt
import maya.OpenMaya as OpenMaya
from maya import OpenMaya

shapesFolder = 'd:\\bogdan\\shapes'

def undoable(function):
    '''A decorator that will make commands undoable in maya'''
    @wraps(function)
    def decoratorCode(*args, **kwargs):
        pm.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)
            pm.undoInfo(closeChunk=True)
        except:
            pm.undoInfo(closeChunk=True)
            print(traceback.format_exc())

            #	throw the actual error
            pm.error()

    return decoratorCode

def bdGetNumJnt():
    '''
    Category: Joint
    Returns the number of joints from selection
    '''
    numJnt = str(len(pm.ls(sl=1, type='joint')))
    return 'Number of selected joints: %s' % numJnt


def bdJointOnCurveFromEdge(baseName, center=0):
    '''
    Category: Joint
    Build joints based on the selected edge.
    Selected edge gets converted to a nurbs curve and the joints are built at the CVs position.
    '''
    if pm.ls(sl=1) > 0:
        if center:
            center = pm.ls('center')[0]
            centerPos = pm.xform(center, q=1, ws=1, t=1)
        edgeCurveAll = pm.polyToCurve(form=2, degree=1)
        pm.select(cl=1)
        # meshName = pm.listConnections('%s.inputPolymesh'%edgeCurveAll[1])[0]

        edgeCurve = pm.ls(edgeCurveAll[0])
        numCv = edgeCurve[0].getShape().numCVs()
        for i in range(numCv):
            pos = edgeCurve[0].getShape().getCV(i, space='world')
            if center:
                baseJnt = pm.joint(n=baseName + '_jntc_' + str(i), p=centerPos)
                endJnt = pm.joint(n=baseName + '_jnt_' + str(i), p=pos)
                pm.joint(baseJnt, e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
                endJnt.jointOrient.set([0, 0, 0])
                pm.select(cl=1)
            else:
                pm.joint(n=baseName + '_jnt_' + str(i), p=pos)
                pm.select(cl=1)


def bdJointToLocAim():
    '''
    Category: Joint
    :return:
    '''
    jntList = pm.ls(sl=1, type='joint')
    for jnt in jntList:
        loc = pm.spaceLocator(name=jnt.name().replace('jnt', 'loc'))
        jntPos = pm.xform(jnt, q=1, ws=1, t=1)
        pm.xform(loc, t=jntPos)
        jntParent = jnt.getParent()
        pm.aimConstraint(loc, jntParent, w=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="object",
                         worldUpObject='LeftEyeUpp_aim_loc')


def locatorsOnCurve(locList, curve):
    for loc in locList:
        pos = pm.xform(loc, q=1, ws=1, t=1)
        u = getUParam(pos, curve.name())
        pci = pm.createNode('pointOnCurveInfo', name=loc.name().replace('loc', 'pci'))
        curve.worldSpace >> pci.inputCurve
        pci.parameter.set(u)
        pci.position >> loc.translate


def getUParam(pnt=[], crv=None):
    point = OpenMaya.MPoint(pnt[0], pnt[1], pnt[2])
    curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
    paramUtill = OpenMaya.MScriptUtil()
    paramPtr = paramUtill.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve(point)
    if isOnCurve:

        curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
    else:
        point = curveFn.closestPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
        curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)

    param = paramUtill.getDouble(paramPtr)
    return param


def getDagPath(objectName):
    if isinstance(objectName, list):
        oNodeList = []
        for o in objectName:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(o)
            oNode = OpenMaya.MDagPath()
            selectionList.getDagPath(0, oNode)
            oNodeList.append(oNode)
        return oNodeList
    else:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(objectName)
        oNode = OpenMaya.MDagPath()
        selectionList.getDagPath(0, oNode)
        return oNode


def bdJointsOnEdge():
    '''
    Category: Joint
    Creates joints on the selected edges.
    The edges are converted to vertices, locators and joints are created at the position of those vertices and the joints are point constrained to the locators
    '''
    if pm.ls(sl=1) > 0:
        selection = pm.ls(sl=True, fl=1)
        edgeSelection = []
        if isinstance(selection[0], (pm.MeshEdge)):
            edgeSelection = selection
        else:
            pm.error('Selection is not an edge')
            return
        vertices = pm.polyListComponentConversion(edgeSelection, fromEdge=1, tv=1)
        pm.select(vertices)
        vertices = pm.ls(sl=1, fl=1)

        mesh = vertices[0].name().split('.')[0].replace('Shape', '')
        locators = []

        for vert in vertices:
            # vertUV = vert.getUV()
            uv = pm.polyListComponentConversion(vert, fromVertex=1, tuv=1)
            vertUV = pm.polyEditUV(uv[0], query=True)
            locator = pm.spaceLocator(n='loc_%s' % vert)
            locators.append(locator)
            cnstr = pm.animation.pointOnPolyConstraint(vert, locator)
            pm.setAttr('%s.%sU0' % (cnstr, mesh), vertUV[0])
            pm.setAttr('%s.%sV0' % (cnstr, mesh), vertUV[1])

        for loc in locators:
            pm.select(cl=1)
            jnt = pm.joint(p=(0, 0, 0), name=loc.name().replace('loc', 'jnt'))
            pm.pointConstraint(loc, jnt, mo=False)


# TO IMPLEMENT
'''
def bdCreateIkTwist(side):
    driver = side + 'hand_bnd_jnt_00'
    twistLocators = pm.ls(side + '_arm_ik_twist_loc_*')
    for l in twistLocators:
        print l
    #twistMd = pm.createNode('multiplyDivide',name= multDivName)

'''


def bdAddIk(start, end, ikType, ikName):
    pm.ikHandle(sol=ikType, sticky='sticky', startJoint=start, endEffector=end, name=ikName)


# @decorators.undoable
# def bdAddDamp(attribute):
#	selection = pm.ls(sl=True)
#	if len(selection) == 2:
#		source  = selection[0]
#		target = selection[1]

#		multDivNode = pm.createNode('multiplyDivide',name= source.name() + '_MD')
#		if attribute == 'r':
#			source.rotate >> multDivNode.input1
#			multDivNode.output >> target.rotate
#			return 'MD create'
#		elif attribute == 't':
#			source.translate >> multDivNode.input1
#			multDivNode.output >> target.translate
#			return 'MD create'
#	else:
#		return 'Select source and target !!!'


def bdAddScaleMulDiv():
    '''
    Category: Nodes
    '''
    pm.undoInfo(openChunk=True)
    selection = pm.ls(sl=True)
    if len(selection) == 2:
        source = selection[0]
        target = selection[1]

        multDivNode = pm.createNode('multiplyDivide', name=source.name() + '_scale_MD')

        source.scale >> multDivNode.input1
        multDivNode.output >> target.scale
        pm.undoInfo(closeChunk=True)
        return 'MD create'
    else:
        pm.undoInfo(closeChunk=True)
        return 'Select source and target !!!'


# def bdCreateDistanceCnd():
#	'''
#	Category: Nodes
#	'''
#	jnt = pm.ls(sl=1)[0]
#	#loc1,loc2,jnt = pm.ls(sl=1)
#	jntCnstr = jnt.listRelatives(type='pointConstraint')[0]
#	loc1,loc2 = pm.pointConstraint(jntCnstr,q=1,tl=1)

#	matrixLoc1 = pm.createNode('decomposeMatrix',name = loc1.name().replace('_loc','_dm'))
#	matrixLoc2 = pm.createNode('decomposeMatrix',name = loc2.name().replace('_loc','_dm'))
#	pma = pm.createNode('plusMinusAverage',name = loc1.name().replace('_loc','_pma'))
#	pma.operation.set(2)
#	rv = pm.createNode('remapValue',name = loc1.name().replace('_loc','_rv'))
#	rv.inputMin.set(0.1)

#	rev = pm.createNode('reverse',name = loc1.name().replace('_loc','_rev'))


#	loc1.worldMatrix[0].connect(matrixLoc1.inputMatrix)
#	loc2.worldMatrix[0].connect(matrixLoc2.inputMatrix)
#	matrixLoc1.outputTranslateY.connect(pma.input1D[0])
#	matrixLoc2.outputTranslateY.connect(pma.input1D[1])
#	pma.output1D.connect(rv.inputValue)

#	rv.outValue.connect(jntCnstr.attr(loc1.name() + 'W0'))
#	rv.outValue.connect(rev.inputX)
#	rev.outputX.connect(jntCnstr.attr(loc2.name() + 'W1'))

def bdPoinOnPoly():
    '''
    Category: General
    '''
    verts = pm.ls(sl=1, fl=1)
    vertsUV = {}
    locs = []

    for i in range(len(verts)):
        loc = pm.spaceLocator(n='eyelid_' + str(i) + '_drv_loc')
        locs.append(loc)
        melCmd = 'doCreatePointOnPolyConstraintArgList 2 {   "0" ,"0" ,"0" ,"1" ,"" ,"1" ,"0" ,"0" ,"0" ,"0" };'
        pm.select(verts[i])
        pm.select(loc, add=1)
        pm.mel.eval(melCmd)


def bdBuildSplineSolverScale():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1, type='transform')
    startJoint = ''
    if selection:
        startJoint = selection[0]
    else:
        return

    print startJoint

    ikSpline = pm.listConnections(startJoint, type='ikHandle')[0]
    print ikSpline
    solver = ikSpline.ikSolver.inputs()[0]

    if 'ikSplineSolver' in solver.name():
        sclChain = pm.duplicate(startJoint, name=startJoint.name() + '_SCL')[0]
        sclChainAll = sclChain.listRelatives(f=True, ad=True, type='joint')

        print sclChainAll

        for sclJnt in sclChainAll:
            pm.rename(sclJnt, sclJnt + '_SCL')

        splineCurve = pm.listConnections(ikSpline, type='nurbsCurve')[0]

        effector = pm.listConnections(ikSpline, source=True, type='ikEffector')[0]
        endJoint = pm.listConnections(effector, source=True, type='joint')[0]
        jointChain = startJoint.listRelatives(f=True, ad=True, type='joint')
        jointChain = jointChain + [startJoint]
        jointChain.reverse()
        print jointChain

        splineCurveScl = pm.duplicate(splineCurve, name=splineCurve.name().replace('crv', 'crv_scl'))
        strArclenSCL = pm.arclen(splineCurveScl, ch=True)
        strArclenCRV = pm.arclen(splineCurve, ch=True)
        arclenSCL = pm.ls(strArclenSCL)[0]
        arclenCRV = pm.ls(strArclenCRV)[0]
        arclenSCL.rename(splineCurveScl[0].name() + '_length')
        arclenCRV.rename(splineCurve.name() + '_length')

        mdScaleFactor = pm.createNode('multiplyDivide', name=splineCurve.name().replace('crv', 'crv_scaleFactor_md'))
        arclenCRV.arcLength.connect(mdScaleFactor.input1X)
        arclenSCL.arcLength.connect(mdScaleFactor.input2X)
        mdScaleFactor.operation.set(2)

        for jnt in jointChain[1:]:
            mdJntTr = pm.createNode('multiplyDivide', name=jnt + '_trX_MD')
            # mdJntTr.operation.set(2)

            sclJnt = pm.ls(jnt + '_SCL')[0]
            mdScaleFactor.outputX.connect(mdJntTr.input2X)
            sclJnt.translateX.connect(mdJntTr.input1X)
            mdJntTr.outputX.connect(jnt.translateX)


# def bdCreateRemapValue():
#     '''
#     Category: Nodes
#     '''
#     selection = pm.ls(sl=1)
#     if selection:
#         for obj in selection:
#             rvNode = pm.shadingNode('remapValue', name=obj.name() + '_rv', asUtility=1)
#             rvNode.inputMax.set(10)
#             obj.attr('Dynamics') >> rvNode.inputValue

@undoable
def bdCreateFolSnp():
    '''
    Category: Snappers
    '''
    selection = pm.ls(sl=1)
    last_flc = max(
        [int(token.getParent().name().split('_')[-1]) for token in pm.ls('head_snappers_flc_*', type='follicle')])
    if selection:
        for vtx in selection:
            last_flc += 1
            shapeStr = vtx.name().split('.')[0]
            shape = pm.ls(shapeStr)[0]

            flcShape = pm.createNode('follicle', name='head_snappers_flc_'+ str(last_flc) +'Shape')
            flcTransform = flcShape.getParent()
            # flcTransform.rename('head_snappers_flc_')

            shape.outMesh.connect(flcShape.inputMesh)
            shape.worldMatrix[0].connect(flcShape.inputWorldMatrix)

            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)

            uvPos = vtx.getUV(uvSet=shape.getCurrentUVSetName())
            uv = pm.polyListComponentConversion(vtx, tuv=True)[0]
            u, v = pm.polyEditUV(uv, q=1)

            flcShape.parameterU.set(u)
            flcShape.parameterV.set(v)


def bdJointOnSelCenter():
    '''
    Category: Joint
    '''
    selection = pm.ls(sl=True, fl=True)
    if selection:
        vertices = pm.polyListComponentConversion(selection, toVertex=True)

        if len(vertices) > 0:
            pm.select(vertices)
            selection = pm.ls(sl=True, fl=True)
            averagePos = dt.Vector(0, 0, 0)
            if type(selection[0]).__name__ == 'MeshVertex':
                numSel = len(selection)
                for sel in selection:
                    vtxPos = sel.getPosition(space='world')
                    averagePos = averagePos + vtxPos

                averagePos = averagePos / numSel
                pm.select(cl=True)
                joint = pm.joint(p=[averagePos.x, averagePos.y, averagePos.z], radius=0.2)
                return 'Joint \'%s \' created' % joint.name()
        else:
            return 'Selection is not a mesh '
    else:
        return 'Nothing selected '


def bdSelectHierarchyJnt():
    '''
    Category: Joint
    '''
    selection = pm.ls(sl=True, type='joint')
    if selection:
        start = selection[0]
        desc = start.listRelatives(ad=1, type='joint')
        allJnt = desc + [start]
        pm.select(allJnt)
        return 'Joint \' %s \' and children selected' % start.name()
    else:
        return 'Nothing selected !!!'


def bdCreateClustersOnCurve(curveName):
    '''
    Category: Rig
    '''
    pm.select((curveName + '.cv[0]'))
    pm.cluster(name=(curveName + '_startCluster'), relative=True)
    pm.select((curveName + '.cv[1]'))
    pm.cluster(name=(curveName + '_endCluster'), relative=True)


def bdSetNormals():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1, fl=1)
    if selection:
        for obj in selection:
            if obj.__class__.__name__ == 'MeshVertex':
                index = re.search("(?<=\[)(\d+)(?=\])", str(obj.name())).group(0)
                shape = obj.name().split('.')[0]
                bdGetVertexInfo(index)


def bdGetVertexInfo(index):
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)
    selection_iter = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMeshVertComponent)

    selection_DagPath = OpenMaya.MDagPath()

    component_vert = OpenMaya.MObject()
    selectedMObject = OpenMaya.MObject()

    try:
        selection_iter.getDagPath(selection_DagPath, component_vert)
    except:
        pm.warning('select vetrices')
        return
    vert_iter = OpenMaya.MItMeshVertex(selection_DagPath, component_vert)
    print vert_iter.count()
    while not vert_iter.isDone():
        intArray = OpenMaya.MIntArray()
        print vert_iter.index(), vert_iter.getConnectedVertices(intArray)
        vert_iter.next()


def bdAddLocGrp(replace):
    selection = pm.ls(sl=1, type='joint')
    if selection:
        for jnt in selection:
            pm.select(cl=1)
            grp = pm.group(name=jnt.name() + '_grp')
            loc = pm.spaceLocator(name=jnt.name().replace(replace, replace + '_loc'))
            pm.parent(loc, grp)
            cnstr = pm.parentConstraint(jnt, grp)
            pm.delete(cnstr)
            pm.parent(jnt, loc)


##'nu e terminata'
# def bdAddGrp():
#	selection  = pm.ls(sl=1)
#	if selection and len(selection) == 2:
#		ikCtrl = selection[0]
#		target = selection[1]
#		pm.select(cl=1)
#		emptyGrp = pm.group(empty=1)
#		emptyGrp.rename(ikCtrl.name().replace('ikCtrl','ikCtrl_Shield'))
#		find = pm.ls(ikCtrl.name() + 'Null')
#		if find:
#			ctrlNull = find[0]
#			temp = pm.parentConstraint(ctrlNull,emptyGrp,mo=0)
#			pm.delete(temp)
#			pm.select(cl=1)
#			pm.parent(emptyGrp,ctrlNull)
#			spaceNullFind = pm.ls(ikCtrl.name() + '_spaceNull')
#			if spaceNullFind:
#				spaceNull = spaceNullFind[0]
#				pm.parent(spaceNull,emptyGrp)
#				pm.parentConstraint(ctrlNull,emptyGrp,mo=0)
#				pm.parentConstraint(target,emptyGrp,mo=0)



def bdConstraintSkeleton():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1)
    tolerance = dt.Vector(0.1, 0.1, 0.1)
    print tolerance
    if selection and len(selection) == 2:
        srcRoot = selection[0]
        srcSkeleton = srcRoot.listRelatives(ad=1, type='joint')
        srcSkeleton.append(srcRoot)
        srcDict = {}

        for jnt in srcSkeleton:
            pos = jnt.getTranslation(space='world')
            srcDict[jnt] = pos
        print srcDict

        destRoot = selection[1]
        destSkeleton = destRoot.listRelatives(ad=1, type='joint')
        destSkeleton.append(destRoot)
        destDict = {}

        for jnt in destSkeleton:
            pos = jnt.getTranslation(space='world')
            destDict[jnt] = pos
        print destDict

        for srcJnt, srcPos in srcDict.iteritems():
            for destJnt, destPos in destDict.iteritems():
                if srcPos.isEquivalent(destPos, tol=0.1):
                    print srcJnt, ' ------ ', destJnt
                    pm.parentConstraint(srcJnt, destJnt, mo=1)


def bdCleanNamespaces():
    '''
    Category: General
    '''
    sceneNS = pm.namespaceInfo(lon=True, r=True)
    sceneNS.remove('UI')
    sceneNS.remove('shared')

    importNS = []
    for ns in sceneNS:
        importNS.append(ns)
    importNS.reverse()

    for ns in importNS:
        try:
            pm.namespace(rm=ns)
        except:
            pm.namespace(moveNamespace=[ns, ':'], force=1)


def bdConstraintChains():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=True)
    returnMessage = 'No message'
    if len(selection) == 2:
        if selection[0].type() == 'joint' and selection[1].type() == 'joint':
            source = selection[0]
            target = selection[1]

            sourceChildren = source.listRelatives(f=True, ad=True, type='joint')
            sourceAll = sourceChildren + [source]

            targetChildren = target.listRelatives(f=True, ad=True, type='joint')
            targetAll = targetChildren + [target]

            i = 0
            for target in targetAll:
                pm.parentConstraint(sourceAll[i], target, mo=1)
                # pm.scaleConstraint(sourceAll[i],target,mo=1)
                i += 1
            returnMessage = 'Chain starting  with %s constrained to chain starting with %s' % (
            selection[1], selection[0])
        else:
            # pm.warning('Selected must be joints!')
            returnMessage = 'Selected must be joints!'
    else:
        # pm.warning('Select two root joints!')
        returnMessage = 'Select two root joints!'

    return returnMessage



def bdConstraintChainsName():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=True)
    returnMessage = 'No message'
    if len(selection) == 1:
        if selection[0].type() == 'joint':
            source = selection[0]


            sourceChildren = source.listRelatives(f=True, ad=True, type='joint')
            sourceAll = sourceChildren + [source]

            for jnt in sourceAll:
                target = pm.ls(jnt.name().replace('_rig', ''))[0]
                pm.parentConstraint(jnt, target, mo=1)
                jnt.scaleX >> target.scaleX
                jnt.scaleY >> target.scaleY
                jnt.scaleZ >> target.scaleZ
                # pm.scaleConstraint(sourceAll[i],target,mo=1)

            returnMessage = 'Chain starting  with %s constrained to chain starting with %s' % (
            selection[1], selection[0])
        else:
            # pm.warning('Selected must be joints!')
            returnMessage = 'Selected must be joints!'
    else:
        # pm.warning('Select two root joints!')
        returnMessage = 'Select the source target'

    return returnMessage

@undoable
def bdConstraintToAnim():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1)
    if selection:
        for obj in selection:
            if obj.type() == 'joint':
                target = obj
                find = pm.ls('anim_' + target.name())
                if find:
                    src = find[0]
                    pm.parentConstraint(src, target, mo=1)


# @decorators.undoable
def bdConstraintBndToRig():
    '''
    Category: Rig
    '''
    pm.undoInfo(openChunk=True)
    selection = pm.ls(sl=True)
    returnMessage = 'No message'

    if len(selection) == 1:
        if selection[0].type() == 'joint':
            source = selection[0]

            sourceChildren = source.listRelatives(f=True, ad=True, type='joint')
            sourceAll = sourceChildren + [source]

            target = None
            i = 0
            for jnt in sourceAll:
                search = pm.ls(jnt.name() + '_ik')
                if search:
                    target = search[0]
                    pm.parentConstraint(target, jnt, mo=1)
                    pm.scaleConstraint(target, jnt, mo=1)
                    i += 1
                else:
                    print "Didn't find RIG for it"

            returnMessage = 'Chain starting  with %s constrained ' % (source)
        else:
            # pm.warning('Selected must be joints!')
            returnMessage = 'Selected must be joints!'
    else:
        # pm.warning('Select two root joints!')
        returnMessage = 'Select two root joints!'

    pm.undoInfo(closeChunk=True)
    return returnMessage


def bdUnlockNodes():
    '''
    Category: General
    '''
    unlockError = False
    selection = pm.ls(sl=1)
    returnMessage = 'No return message'

    if selection:
        for node in selection:
            lockStatus = pm.lockNode(node, q=True)
            for response in lockStatus:
                if response != False:
                    try:
                        pm.lockNode(node, lock=False)
                        returnMessage += ('Unlocked: ' + node + '\n')
                    except:
                        returMessage += ('Error: Could not unlock ' + node + '\n')
    else:
        returnMessage = 'Nothing selected'

    return returnMessage


# def bdRebuildWithNames():
#	selection = pm.ls(sl=1,type='joint')
#	if selection:
#		root = selection[0]
#		chain = root.listRelatives(ad=1,type='joint')
#		chain.reverse()
#		allJnt = [root] + chain
#		newChain = []
#		pm.select(cl=1)
#		for jnt in allJnt:
#			print jnt.name()
#			pos = jnt.getTranslation(space='world')
#			newChain.append(pm.joint(name=jnt.name(),p=pos))
#		pm.joint(newChain[0],e=1,oj='xyz',secondaryAxisOrient='yup',ch= True,zso=True)


def bdLocOnVertex():
    '''
    Category: General
    '''
    selection = pm.ls(sl=1, fl=1)
    if selection:
        if isinstance(selection[0], pm.MeshVertex):
            locators = []
            for i in range(len(selection)):
                vtx = selection[i]
                loc = pm.spaceLocator()
                pointCnstr = pm.pointOnPolyConstraint(vtx, loc)
                # uv = vtx.getUV()
                # attrs = pm.listAttr(pointCnstr, ud=1)
                # pointCnstr.attr(attrs[1]).set(uv[0])
                # pointCnstr.attr(attrs[2]).set(uv[1])
                # locators.append(loc)
            # if len(selection) > 1:
            #     drvLoc = pm.spaceLocator(name='drvLoc')
            #     pm.parentConstraint(locators, drvLoc, mo=0)


def bdParentSelected():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1)
    if selection and len(selection) > 1:
        pm.select(cl=1)
        for i in range(len(selection) - 1):
            pm.parent(selection[i], selection[i + 1])


def bdAddBlendSwitch(rigString, ikString, fkString):
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1)
    if selection:
        rigJnts = selection
        print rigJnts
        for jnt in rigJnts:
            if rigString in jnt.name():
                fkJnt = None
                ikJnt = None
                searchFkJnt = pm.ls(jnt.name().replace(rigString, fkString))
                if searchFkJnt:
                    fkJnt = searchFkJnt[0]

                searchIkJnt = pm.ls(jnt.name().replace(rigString, ikString))
                if searchIkJnt:
                    ikJnt = searchIkJnt[0]

                if fkJnt and ikJnt:
                    bdCreateBlend(jnt, fkJnt, ikJnt)


def bdCreateBlend(bindJnt, fkJnt, ikJnt):
    blendColorPos = pm.createNode('blendColors', name=bindJnt.name() + '_pos_bc')
    blendColorRot = pm.createNode('blendColors', name=bindJnt.name() + '_rot_bc')
    #blendColorScl = pm.createNode('blendColors', name=bindJnt.name() + '_scl_bc')

    blendColorPos.blender.set(1)
    blendColorRot.blender.set(1)
    #blendColorScl.blender.set(1)
    # pm.connectAttr(self.ikfkSwitchCtrl + '.IKFK', blendColorPos.name() + '.blender')
    # pm.connectAttr(self.ikfkSwitchCtrl + '.IKFK', blendColorRot.name() + '.blender')
    # pm.connectAttr(self.ikfkSwitchCtrl + '.IKFK', blendColorScl.name() + '.blender')


    pm.connectAttr(fkJnt + '.translate', blendColorPos.name() + '.color1')
    pm.connectAttr(ikJnt + '.translate', blendColorPos.name() + '.color2')
    pm.connectAttr(blendColorPos.name() + '.output', bindJnt + '.translate')

    pm.connectAttr(fkJnt + '.rotate', blendColorRot.name() + '.color1')
    pm.connectAttr(ikJnt + '.rotate', blendColorRot.name() + '.color2')
    pm.connectAttr(blendColorRot.name() + '.output', bindJnt + '.rotate')

    # pm.connectAttr(fkJnt + '.scale', blendColorScl.name() + '.color1')
    # pm.connectAttr(ikJnt + '.scale', blendColorScl.name() + '.color2')
    # pm.connectAttr(blendColorScl.name() + '.output', bindJnt + '.scale')


# connects the blend nodes to the config switcher
def connectConfigBlend(ctrl):
    selection = pm.ls(sl=1)
    if selection:
        ctrlFound = pm.ls(ctrl)
        if ctrlFound:
            ctrlObj = ctrlFound[0]
            reverse = pm.createNode('reverse', name=ctrlObj.name() + '_IKFK_REV')
            ctrlObj.attr('IKFK') >> reverse.input.inputX
            for s in selection:
                inputs = pm.listConnections(s, source=1, destination=0)
                for i in inputs:
                    if i.type() == 'blendColors':
                        reverse.output.outputX >> i.blender
                    elif i.type() == 'unitConversion':
                        nextLevel = pm.listConnections(i, source=1, destination=0)
                        if nextLevel:
                            reverse.output.outputX >> nextLevel[0].blender

                print inputs


def bdConnectScale():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1)
    if selection and len(selection) == 2:
        selection[0].scale >> selection[1].scale


def bdAddDistanceBetween():
    '''
    Category: Nodes
    '''
    selection = pm.ls(sl=1)
    if selection and len(selection) == 2:
        source1 = selection[0]
        source2 = selection[1]

        dbNode = pm.shadingNode('distanceBetween', asUtility=1, name=source1.name() + '_' + source2.name() + '_db')
        source1.worldMatrix[0] >> dbNode.inMatrix1
        source1.rotatePivotTranslate >> dbNode.point1

        source2.worldMatrix[0] >> dbNode.inMatrix2
        source2.rotatePivotTranslate >> dbNode.point2



def bdCreateMulDivRot():
    '''
    Category: Nodes
    '''
    selection = pm.ls(sl=1)
    if selection and len(selection) == 2:
        src = selection[0]
        dest = selection[1]

        md_node = pm.shadingNode('multiplyDivide', asUtility=1, name=dest.name() + '_rot_md')
        src.attr('rotate') >> md_node.input1
        md_node.output >> dest.attr('rotate')


def bdCreateRemapValue(src, src_attr, dest, dest_attr):
    rv_node = pm.shadingNode('remapValue', asUtility=1, name = dest.name() + '_' + dest_attr + '_rv')
    src.attr(src_attr) >> rv_node.inputValue
    rv_node.outValue >> dest.attr(dest_attr)


def bdJntGrp():
    '''
    Category: Snappers
    '''
    selection = pm.ls(sl=1)

    i=0
    if selection:
        for flc in selection:
            pm.select(cl=1)
            loc = pm.spaceLocator(name=flc.name() +  '_loc')
            grp = pm.group(name=flc.name() + '_grp')
            pm.parent(grp,flc)
            grp.setTranslation([0,0,0])
            grp.setRotation([0, 0, 0])
            jnt = pm.joint(name= flc.name().replace('flc', 'jnt'))
            jnt.radius.set(0.2)
            pm.parent(jnt,loc)
            jnt.t.set([0,0,0])
            jnt.r.set([0, 0, 0])
            i+=1

# @undoable
# def bdJntLocGrp():
#     '''
#     Category: Snappers
#     '''
#     selection = pm.ls(sl=1)
#     if selection:
#         for jnt in selection:
#             pm.select(cl=1)
#             loc = pm.spaceLocator(name=jnt.name() + '_loc')
#             grp = pm.group(name=jnt.name() + '_grp')
#             pm.parentConstraint(jnt, grp, mo=0)
#             pm.parentConstraint(jnt, grp, remove=1)
#             pm.parent(jnt,loc)



@undoable
def bdMirrorJntLocGrp():
    '''
    Category: Snappers
    '''
    selection = pm.ls(sl=1)
    if selection:
        for grp in selection:
            pm.select(cl=1)
            if '_c_' not in grp.name():
                mirrored = pm.duplicate(grp, name=grp.replace('_l_', '_r_'))[0]
                pos = grp.getTranslation()
                mirrored.setTranslation([pos.x * -1.0, pos.y, pos.z])
                children = pm.listRelatives(mirrored, type='transform', ad=1)
                for child in children:
                    pm.rename(child, child.name().replace('_l_', '_r_'))
                    if '_loc' in child.name():
                        ry = child.rotateY.get()
                        child.rotateY.set(-1.0 * ry)


@undoable
def bdCreateBnd():
    '''
    Category: Snappers
    '''
    selection = pm.ls(sl=1)
    if selection:
        for grp in selection:
            pm.select(cl=1)
            children = pm.listRelatives(grp, type='joint', ad=1)
            if children:
                anim_jnt = children[0]
                dup = pm.duplicate(anim_jnt, name = anim_jnt.name().replace('anim_', ''))
                pm.parent(dup[0], w=1)
                pm.parentConstraint(anim_jnt, dup[0])

@undoable
def bdCreateFol():
    '''
    Category: Rig
    '''
    selection = pm.ls(sl=1, fl=1)
    if selection:
        for vtx in selection:
            shapeStr = vtx.name().split('.')[0]
            shape = pm.ls(shapeStr)[0]

            flcShape = pm.createNode('follicle')
            flcTransform = flcShape.getParent()
            # flcTransform.rename('head_snappers_flc_')

            shape.outMesh.connect(flcShape.inputMesh)
            shape.worldMatrix[0].connect(flcShape.inputWorldMatrix)

            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)

            uv_m = pm.polyListComponentConversion(vtx, tuv=True)[0]
            uv = pm.ls(uv_m, fl=1)[0]
            try:
                u, v = pm.polyEditUV(uv, q=1)
            except:
                pm.warning('Total fail')

            flcShape.parameterU.set(u)
            flcShape.parameterV.set(v)


@undoable
def bdZeroEndJoint():
    '''
    Category: Joint
    '''
    selection = pm.ls(sl=1)
    if selection:
        for jnt in selection:
            try:
                jnt.jointOrient.set([0, 0, 0])
            except:
                pm.warning("%s is not a joint"%jnt.name())



@undoable
def bdToggleAxis():
    '''
    Category: Joint
    '''
    selection = pm.ls(sl=1)
    if selection:
        for jnt in selection:
            pm.select(cl=1)
            try:
                pm.select(jnt)
                state = pm.toggle(q=True, localAxis=True)
                if state == 1:
                    pm.toggle(state=False, localAxis=True)
                elif state == 0:
                    pm.toggle(state=True, localAxis=True)
            except:
                pm.warning("%s is not a joint"%jnt.name())
        pm.select(selection)


@undoable
def bdCopyChainName():
    '''
    Category: Joint
    '''
    selection = pm.ls(sl=1)
    print len(selection)
    if selection:
        if len(selection) == 2:
            src_chain = selection[0]
            tgt_chain = selection[1]
            src_children = pm.listRelatives(src_chain, ad=1, type='joint')
            tgt_children = pm.listRelatives(tgt_chain, ad=1, type='joint')
            if len(src_children) == len(tgt_children):
                src_names = []
                src_chain = src_children + [src_chain]
                for jnt in src_chain:
                    src_names.append(jnt.name())
                print src_names

                tgt_chain = tgt_children + [tgt_chain]
                for i in range(len(tgt_chain)):
                    tgt_chain[i].rename(src_names[i])
            else:
                pm.warning('The two chains have to be identical ')
        else:
            pm.warning('Select 2 joint chains !!!')
    else:
        pm.warning('Nothing selected')