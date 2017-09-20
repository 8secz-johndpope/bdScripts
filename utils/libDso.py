import pymel.core as pm
import json, os, random, re

import mayaDecorators as decorators

import pymel.core.datatypes as dt

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim


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
            tempNull.translateX.set(500)
            pm.aimConstraint(tempNull, jnt, aimVector=[1, 0, 0], upVector=[0, 1, 0])
            pm.delete(tempNull)
            mirrorJntRot(jnt)


def mirrorJntRot(leftSide):
    findRightSide = pm.ls(leftSide.name().replace('Left', 'Right'))
    if findRightSide:
        rightSide = findRightSide[0]
        leftSideRot = leftSide.getRotation(space='object')
        rightSide.setRotation(leftSideRot, space='object')


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


def createFxJoints():
    root = None
    chest = None
    search = pm.ls('Skeleton_Root')
    if search:
        root = search[0]
    search = pm.ls('Chest')
    if search:
        chest = search[0]

    if not root or not chest:
        return "No Skeleton_Root or Chest joint in scene"

    pm.select(cl=1)
    fxroot = pm.joint(name='fx_root')
    rootPos = root.getTranslation(space='world')
    fxroot.setTranslation([rootPos[0], rootPos[1], rootPos[2] + 4])
    pm.parent(fxroot, root)

    pm.select(cl=1)
    fxchest = pm.joint(name='fx_chest')
    chestPos = chest.getTranslation(space='world')
    fxchest.setTranslation([chestPos[0], chestPos[1], chestPos[2] + 4])
    pm.parent(fxchest, chest)
    return 'Fx Joints Created'


def setClipOffsets(jnt, t, r, s):
    charNodes = []
    it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kCharacter)
    while not it.isDone():
        obj = it.item()
        if obj.hasFn(OpenMaya.MFn.kCharacter):
            fnCharNode = OpenMayaAnim.MFnCharacter(obj)
            charNodes.append(fnCharNode)
        it.next()

    for char in charNodes:
        if 'characterset_skeleton' == char.name():
            fnCharNode = OpenMayaAnim.MFnCharacter()
            fnCharNode = char

            plugs = OpenMaya.MPlugArray()
            fnCharNode.getMemberPlugs(plugs)
            numSheduledClips = fnCharNode.getScheduledClipCount()

            for i in range(numSheduledClips):
                animClip = fnCharNode.getScheduledClip(i)
                if animClip.hasFn(OpenMaya.MFn.kClip):
                    fnClip = OpenMayaAnim.MFnClip(animClip)
                    if 'spawn' == fnClip.name():
                        curves = OpenMaya.MObjectArray()
                        plugArray = OpenMaya.MPlugArray()
                        fnClip.getMemberAnimCurves(curves, plugArray)

                        absoluteChannels = OpenMaya.MIntArray()
                        fnClip.getAbsoluteChannelSettings(absoluteChannels)
                        for i in range(plugArray.length()):
                            if jnt.name() in plugArray[i].name():
                                if t:
                                    if 'translate' in plugArray[i].name():
                                        absoluteChannels[i] = 1
                                if r:
                                    if 'rotate' in plugArray[i].name():
                                        absoluteChannels[i] = 1
                                if s:
                                    if 'scale' in plugArray[i].name():
                                        absoluteChannels[i] = 1

                        fnClip.setAbsoluteChannelSettings(absoluteChannels)


def cleanSkins():
    meshes = []

    selection = pm.ls(sl=1)
    if selection:
        shapes = [s for s in selection if s.getShape()]
        meshes = [m for m in shapes if m.getShape().nodeType() == 'mesh']
        if len(meshes) > 0:
            print meshes


def locOnVertex():
    selection = pm.ls(sl=1, fl=1)
    if selection:
        if isinstance(selection[0], pm.MeshVertex):
            locators = []
            for i in range(len(selection)):
                vtx = selection[i]
                loc = pm.spaceLocator()
                pointCnstr = pm.pointOnPolyConstraint(vtx, loc)
                uv = vtx.getUV()
                attrs = pm.listAttr(pointCnstr, ud=1)
                pointCnstr.attr(attrs[1]).set(uv[0])
                pointCnstr.attr(attrs[2]).set(uv[1])
                locators.append(loc)
            if len(selection) > 1:
                drvLoc = pm.spaceLocator(name='drvLoc')
                pm.parentConstraint(locators, drvLoc, mo=0)


def animateSpikes():
    spikes = pm.ls('ice_spike_*', type='transform')
    bursts = pm.ls('burst_out_*', type='transform')

    print bursts
    indexes = [i for i in range(len(spikes))]
    print indexes
    random.shuffle(indexes)

    timeOffset = 0
    for i in indexes:
        pm.currentTime(timeOffset)
        pm.setKeyframe(spikes[i].name() + '.ty', v=0)
        print bursts[i]
        setParticlesAttr(bursts[i], timeOffset + 4)
        pm.currentTime(timeOffset + 4)
        pm.setKeyframe(spikes[i].name() + '.ty', v=random.uniform(1.3, 1.7))
        pm.currentTime(timeOffset + 5)
        y = spikes[i].ty.get()
        pm.setKeyframe(spikes[i].ty, v=y - 0.1)
        timeOffset += 2
        if timeOffset == 12:
            timeOffset = 2


def setParticlesAttr(emitterGroup, val):
    emitters = pm.listRelatives(emitterGroup, c=1, type='transform')
    for e in emitters:
        particleMaterial = None
        shape = e.getShape()
        shapeShadeGrp = pm.listConnections(shape, type='shadingEngine')[0]
        shapeShader = pm.listConnections('%s.surfaceShader' % shapeShadeGrp)[0]

        attrs = pm.listAttr(e, ud=1)
        pm.select(e)
        if 'ParticleStartDelay' not in attrs:
            melCmd = 'rlScriptEdit_animShaderParam ParticleStartDelay ' + shapeShader + '.rlParticleStartDelay ' + shapeShader + ' 0'
            pm.mel.eval(melCmd)

        if 'ParticleStartVelocityRandomize' not in attrs:
            melCmd = 'rlScriptEdit_animShaderParam ParticleStartVelocityRandomize ' + shapeShader + '.rlParticleStartVelocityRandomize ' + shapeShader + ' 0'
            pm.mel.eval(melCmd)
            print e, 'ParticleStartVelocityRandomize'

        if 'ParticleSizeRandomize' not in attrs:
            melCmd = 'rlScriptEdit_animShaderParam ParticleSizeRandomize ' + shapeShader + '.rlParticleSizeRandomize ' + shapeShader + ' 0'
            pm.mel.eval(melCmd)
            print e, 'ParticleSizeRandomize'

        pm.setAttr(e + '.ParticleStartDelay', val / 25.0)
        pm.setAttr(e + '.ParticleStartVelocityRandomize', random.uniform(0, 1))
        pm.setAttr(e + '.ParticleSizeRandomize', random.uniform(0, 1))


def randomizeVerts(offset=0.3):
    vertPosArray = OpenMaya.MPointArray()
    newVertPosArray = OpenMaya.MPointArray()
    fnMesh = OpenMaya.MObject()

    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)
    dagPath = OpenMaya.MDagPath()
    if selection.length() > 0:
        selection.getDagPath(0, dagPath)
    else:
        pm.warning('Nothing selected')
        return

    try:
        fnMesh = OpenMaya.MFnMesh(dagPath)
    except:
        pm.warning('Selection is not polygon')
        return

    fnMesh.getPoints(vertPosArray)

    for i in range(vertPosArray.length()):
        x = random.uniform(vertPosArray[i].x - offset, vertPosArray[i].x + offset)
        y = random.uniform(vertPosArray[i].y - offset, vertPosArray[i].y + offset)
        z = random.uniform(vertPosArray[i].z - offset, vertPosArray[i].z + offset)
        newVertPosArray.append(OpenMaya.MPoint(x, y, z))

    fnMesh.setPoints(newVertPosArray)
    fnMesh.updateSurface()


def copyMinionSkin(skin1, skin2):
    srcSkin = pm.ls(skin1)[0]
    destSkin = pm.ls(skin2)[0]

    srcSkinTransform = pm.listConnections('%s.outputGeometry[0]' % srcSkin)[0]
    srcSkinInfluence = pm.skinCluster(srcSkin, q=True, influence=True)
    srcSkinShape = srcSkinTransform.getShape()
    srcVtx = pm.polyEvaluate(srcSkinTransform, v=1)
    print srcSkinInfluence

    destSkinTransform = pm.listConnections('%s.outputGeometry[0]' % destSkin)[0]
    destSkinInfluence = pm.skinCluster(srcSkin, q=True, influence=True)
    destSkinShape = destSkinTransform.getShape()
    destVtx = pm.polyEvaluate(destSkinTransform, v=1)
    print destSkinInfluence
    pairs = {}
    for jnt in srcSkinInfluence:
        val = jnt.find('Meanie01')
        if val > 0:
            tmp = jnt.replace('Meanie01', 'Meanie02')
            if tmp:
                pairs[jnt] = tmp

    pairs['Pelvis'] = 'Spine_Meanie02Pelvis'
    pairs['Chest'] = 'Spine_Meanie02Chest'
    pairs['Head'] = 'Neck_Meanie02Head'

    for jnt in srcSkinInfluence:
        for i in range(srcVtx):
            val = pm.skinPercent(srcSkin, srcSkinTransform.name() + '.vtx[' + str(i) + ']', transform=jnt, query=True)
            if val > 0:
                pm.skinPercent(destSkin, destSkinTransform.name() + '.vtx[' + str(i) + ']',
                               transformValue=[(pairs[jnt], val)])


def bdScaleAlong():
    travelLoc = pm.ls('Mag01TailFront_scaleFollicle')[0]
    rigJnt = pm.ls(sl=1, type='joint')

    if rigJnt:
        for jnt in rigJnt:
            distance = pm.shadingNode('distanceBetween', asUtility=1, n=jnt.name() + '_DB')
            print distance
            pm.connectAttr(travelLoc + '.worldMatrix[0]', distance + '.inMatrix1')
            pm.connectAttr(travelLoc + '.rotatePivotTranslate', distance + '.point1')
            flc = jnt.getParent()
            print flc
            pm.connectAttr(flc + '.worldMatrix[0]', distance + '.inMatrix2')
            pm.connectAttr(flc + '.rotatePivotTranslate', distance + '.point2')

            rv = pm.shadingNode('remapValue', asUtility=1, n=jnt.name() + '_RV')
            rv.inputMin.set(3)
            rv.inputMax.set(0)
            rv.outputMin.set(1)
            rv.outputMax.set(2)
            pm.connectAttr(distance + '.distance', rv.name() + '.inputValue')
            pm.connectAttr(rv.name() + '.outValue', jnt.name() + '.scaleX')
            pm.connectAttr(rv.name() + '.outValue', jnt.name() + '.scaleY')
            pm.connectAttr(rv.name() + '.outValue', jnt.name() + '.scaleZ')
