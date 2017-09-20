import os, re
import pymel.core as pm
import maya.OpenMaya as OpenMaya
import pymel.core.datatypes as dt

import maya.cmds as mc


def createClustersOnCurve(curveName):
    mc.select((curveName + '.cv[0]'))
    mc.cluster(name=(curveName + '_startCluster'), relative=True)
    mc.select((curveName + '.cv[1]'))
    mc.cluster(name=(curveName + '_endCluster'), relative=True)


def recurseBuildCurves(startObject):
    startObjectPos = mc.xform(startObject, q=True, ws=True, rp=True)

    children = mc.listRelatives(startObject, children=True, type='transform', fullPath=True)
    if children:
        for child in children:
            endObjectPos = mc.xform(child, q=True, ws=True, rp=True)
            curveName = mc.curve(d=1, p=[startObjectPos, endObjectPos])
            createClustersOnCurve(curveName)
            recurseBuildCurves(child)


def buildCurvesOnTemplate():
    selection = mc.ls(sl=True, type='transform')
    startObject = selection[0]
    # endObject = selection[1]
    recurseBuildCurves(startObject)


# --------------------------


def copyFilesDso():
    import os, shutil, stat

    charsPath = 'd:/drasa_online/work/gfxlib/characters/'

    charDirs = [dir for dir in os.listdir(charsPath) if os.path.isdir(os.path.join(charsPath, dir)) and 'new' in dir]
    print len(charDirs)
    for char in charDirs:
        path = os.path.join(charsPath, char)
        skeletonFile = [f for f in os.listdir(path) if 'skeleton' in f][0]
        src = os.path.join(path, skeletonFile)
        dest = os.path.join(path, skeletonFile).replace('_new', '')
        try:
            fileAtt = os.stat(dest)[0]
            if (not fileAtt & stat.S_IWRITE):
                # File is read-only, so make it writeable
                os.chmod(dest, stat.S_IWRITE)
            shutil.copy2(src, dest)
        except:
            print 'failed at ', src, dest


def setNormals():
    selection = pm.ls(sl=1, fl=1)
    if selection:
        for obj in selection:
            if obj.__class__.__name__ == 'MeshVertex':
                index = re.search("(?<=\[)(\d+)(?=\])", str(obj.name())).group(0)
                shape = obj.name().split('.')[0]
                getVertexInfo(index)


def getVertexInfo(index):
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


def replaceShape():
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


# 'nu e terminata'
def addGrp():
    selection = pm.ls(sl=1)
    if selection and len(selection) == 2:
        ikCtrl = selection[0]
        target = selection[1]
        pm.select(cl=1)
        emptyGrp = pm.group(empty=1)
        emptyGrp.rename(ikCtrl.name().replace('ikCtrl', 'ikCtrl_Shield'))
        find = pm.ls(ikCtrl.name() + 'Null')
        if find:
            ctrlNull = find[0]
            temp = pm.parentConstraint(ctrlNull, emptyGrp, mo=0)
            pm.delete(temp)
            pm.select(cl=1)
            pm.parent(emptyGrp, ctrlNull)
            spaceNullFind = pm.ls(ikCtrl.name() + '_spaceNull')
            if spaceNullFind:
                spaceNull = spaceNullFind[0]
                pm.parent(spaceNull, emptyGrp)
                pm.parentConstraint(ctrlNull, emptyGrp, mo=0)
                pm.parentConstraint(target, emptyGrp, mo=0)


def constraintSkeleton():
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


def cleanNamespaces():
    sceneNS = pm.namespaceInfo(lon=True, r=True)
    print sceneNS
    importNS = []
    for ns in sceneNS:
        importNS.append(ns)
    importNS.reverse()

    for ns in importNS:
        try:
            pm.namespace(rm=ns)
        except:
            pm.namespace(moveNamespace=[ns, ':'], force=1)


# Creates a variation animation clip
def createVarClip(scale, name):
    charSkeleton = None
    charSkeletonSheduler = None
    findCharSkeleton = pm.ls('characterset_skeleton', type='character')

    if findCharSkeleton:
        charSkeleton = findCharSkeleton[0]
        charSkeletonSheduler = charSkeleton.getClipScheduler()

    else:
        pm.warning('Couldn\'t find character_skeleton')
        return

    excludeJoints = ['mount', 'fx_root', 'fx_chest']
    findRoot = pm.ls('Skeleton_Root', type='joint')
    if len(findRoot) == 1:
        skRoot = findRoot[0]
        children = skRoot.listRelatives(ad=1, type='joint')
        skeleton = [skRoot] + children
    findClips = pm.ls(type='animClip')

    if findClips:
        for clip in findClips:
            clip.enable.set(0)

    pm.select(skeleton)
    for jnt in skeleton:
        jnt.scaleX.set(scale)
        jnt.scaleY.set(scale)
        jnt.scaleZ.set(scale)
    for jnt in excludeJoints:
        findJnt = pm.ls(jnt)
        if findJnt:
            findJnt[0].scaleX.set(1)
            findJnt[0].scaleY.set(1)
            findJnt[0].scaleZ.set(1)
    pm.setKeyframe(time=-1)

    for jnt in skeleton:
        jnt.scaleX.set(1)
        jnt.scaleY.set(1)
        jnt.scaleZ.set(1)
    pm.setKeyframe(time=-5)

    varClip = pm.clip(charSkeleton, name=name, sc=1, ignoreSubcharacters=1, startTime=-5, endTime=-1)
    clipsInfo = pm.clipSchedule(charSkeletonSheduler, q=True)
    print clipsInfo
    for info in clipsInfo:
        infoSplit = info.split(',')
        if name == infoSplit[0]:
            print infoSplit[1]
            pm.clipSchedule(charSkeletonSheduler, ci=int(infoSplit[1]), allRelative=1)


def setTpose():
    selection = pm.ls(sl=1, type='joint')
    if selection:
        for jnt in selection:
            tempNull = pm.spaceLocator(name=jnt.name() + '_temp_loc')
            pm.delete(pm.pointConstraint(jnt, tempNull))
            tempNull.translateX.set(100)
            pm.aimConstraint(tempNull, jnt, aimVector=[1, 0, 0], upVector=[0, 1, 0])
            pm.delete(tempNull)
            mirrorJntRot(jnt)


def mirrorJntRot(leftSide):
    findRightSide = pm.ls(leftSide.name().replace('Left', 'Right'))
    if findRightSide:
        rightSide = findRightSide[0]
        leftSideRot = leftSide.getRotation(space='local')
        rightSide.setRotation(leftSideRot, space='local')
