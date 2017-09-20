import pymel.core as pm


def bdCleanKeyframes():
    start = pm.playbackOptions(q=1, ast=1)
    end = pm.playbackOptions(q=1, aet=1)

    sel = pm.ls(sl=1, type='transform')

    for i in range(8, end - 10, 1):
        if not (i % 4):
            print i
            pm.currentTime(i)
            pm.setKeyframe(sel, t=i)
        else:
            pm.cutKey(sel, clear=1, an='objects', iub=0, t=(i, i + 1))


def bdBuildBoxController(target, ctrlName, scale):
    defaultPointsList = [(1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1),
                         (-1, 1, 1)]
    pointsList = []
    for p in defaultPointsList:
        pointsList.append((p[0] * scale, p[1] * scale, p[2] * scale))

    knotsList = [i for i in range(16)]
    curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3],
                   pointsList[7], pointsList[4], pointsList[5], pointsList[6],
                   pointsList[7], pointsList[3], pointsList[0], pointsList[4],
                   pointsList[5], pointsList[1], pointsList[2], pointsList[6]]

    ctrl = pm.curve(d=1, p=curvePoints, k=knotsList)
    ctrl = pm.rename(ctrl, ctrlName)
    ctrlGrp = pm.group(ctrl, n=ctrlName.replace("anim", "anim_CON"))
    targetPos = pm.xform(target, q=True, ws=True, t=True)
    pm.move(targetPos[0], targetPos[1], targetPos[2], ctrlGrp)
    return [ctrl, ctrlGrp]


def bdBuildSquareController(target, ctrlName, scale, pivotOfset=0.5):
    defaultPointsList = [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0)]
    pointsList = []
    targetPos = pm.xform(target, q=True, ws=True, t=True)
    for p in defaultPointsList:
        pointsList.append((p[0] * scale, p[1] * scale, p[2] * scale))

    curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3], pointsList[0]]

    ctrl = pm.curve(d=1, p=curvePoints)
    ctrl.rename(ctrlName)
    ctrlGrp = pm.group(ctrl, n=ctrlName.replace("anim", "anim_CON"))
    pm.move(targetPos[0], targetPos[1], targetPos[2], ctrlGrp, ws=True)
    ctrl.translateZ.set(pivotOfset)
    pm.makeIdentity(ctrl, apply=True, translate=True, rotate=True, scale=True)
    ctrl.setPivots([0, 0, 0])
    return [ctrl, ctrlGrp]


def bdBuildSphereController(target, ctrlName, scale):
    circleA = pm.circle(n=ctrlName + 'A', nr=(0, 1, 0), c=(0, 0, 0), radius=scale)
    circleB = pm.circle(n=ctrlName + 'B', nr=(1, 0, 0), c=(0, 0, 0), radius=scale)
    circleBShape = pm.listRelatives(circleB[0], c=True)
    circleC = pm.circle(n=ctrlName + 'C', nr=(0, 0, 1), c=(0, 0, 0), radius=scale)
    circleCShape = pm.listRelatives(circleC[0], c=True)
    pm.parent(circleBShape[0], circleA[0], r=True, s=True)
    pm.parent(circleCShape[0], circleA[0], r=True, s=True)
    pm.delete(circleB, circleC)
    ctrl = pm.rename(circleA[0], ctrlName)
    ctrlGrp = pm.group(ctrl, n=ctrlName.replace("anim", "anim_CON"))
    targetPos = pm.xform(target, q=True, ws=True, t=True)
    targetRot = pm.xform(target, q=True, ws=True, ro=True)
    pm.move(targetPos[0], targetPos[1], targetPos[2], ctrlGrp)
    pm.rotate(targetRot[0], targetRot[1], targetRot[2], ctrlGrp)


def bdLocOnJnt():
    selection = pm.ls(sl=1)
    if len(selection) != 2:
        return

    rootJnt = pm.ls(sl=True)[0]
    crvPath = pm.ls(sl=True)[1]

    allJnt = rootJnt.listRelatives(f=True, ad=True, type='joint')
    allJnt = allJnt + [rootJnt]
    allJnt.reverse()

    locators = []
    for jnt in allJnt:
        loc = pm.spaceLocator(name=jnt.name().replace('_jnt', '_loc'))
        locGrp = pm.group(n=loc.name() + '_grp')

        tempCnstr = pm.pointConstraint(jnt, locGrp, mo=0);
        pm.delete(tempCnstr)
        locators.append(locGrp)

    bdMultiMotionPath(crvPath, locators)
    bdParentJntToLocs(allJnt)


def bdParentJntToLocs(allJnt):
    for jnt in allJnt:
        loc = pm.ls(jnt.name().replace('_jnt', '_loc'))[0]
        pm.parentConstraint(jnt.name().replace('_jnt', '_loc'), jnt, mo=0)
        # pm.scaleConstraint(jnt.name().replace('_jnt','_loc'),jnt,mo=0)
        loc.scaleX.connect(jnt.scaleX)
        loc.scaleY.connect(jnt.scaleY)
        loc.scaleZ.connect(jnt.scaleZ)
        jntMp = pm.ls(jnt.name().replace('_jnt', '_loc_grp_mp'))


def bdMultiMotionPath(crvPath, objects, interval=2, speed=20):
    numObjects = len(objects)
    startTime = pm.playbackOptions(q=1, minTime=1)
    endTime = pm.playbackOptions(q=1, maxTime=1)
    allMotionPath = []
    for i in range(numObjects):
        # motionPath = pm.pathAnimation(objects[i],c=crvPath,n=objects[i].name() + '_mp',stu = i*interval , etu = i*interval + speed,follow = 1, followAxis = 'x', upAxis = 'y',fractionMode =1)
        pm.currentTime(0)
        motionPath = pm.pathAnimation(objects[i], c=crvPath, n=objects[i].name() + '_mp', follow=1, followAxis='x',
                                      upAxis='y', fractionMode=1)
        allMotionPath.append(motionPath)
        pm.setAttr(motionPath + '.worldUpType', 1)

    bdSetStartMp(allMotionPath)
    startCycleFrame = i * interval + speed + 2

    # bdCyclePath(allMotionPath,startCycleFrame,interval,speed,repeat = 4)


def bdCyclePath(allMotionPath, startCycleFrame, interval, speed, repeat):
    scaleOffset = 1
    for i in range(1, len(allMotionPath) + 1):
        print 'locator ', i
        for r in range(repeat):
            loc = allMotionPath[i - 1].replace('_grp_mp', '')
            if i == 0:
                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=r * (startCycleFrame + 1) + i * interval, value=0)
                bdScaleLocAnim(loc, r * (startCycleFrame + 1) + i * interval - 1, 0.001)
                bdScaleLocAnim(loc, r * (startCycleFrame + 1) + i * interval + scaleOffset - 1, 1)
                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=r * (startCycleFrame + 1) + i * interval + speed,
                               value=1)
                bdScaleLocAnim(loc, r * (startCycleFrame + 1) + i * interval + speed - scaleOffset - 1, 1)
                bdScaleLocAnim(loc, r * (startCycleFrame + 1) + i * interval + speed - 1, 0.001)
                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=(r + 1) * startCycleFrame, value=1)
                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=(r + 1) * startCycleFrame + 1, value=0)
                bdScaleLocAnim(loc, (r + 1) * startCycleFrame - 1, 0.001)
            else:
                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=r * startCycleFrame + i * interval, value=0)
                bdScaleLocAnim(loc, r * (startCycleFrame) + i * interval - 1, 0.001)
                bdScaleLocAnim(loc, r * (startCycleFrame) + i * interval + scaleOffset - 1, 1)

                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=r * startCycleFrame + i * interval + speed,
                               value=1)
                bdScaleLocAnim(loc, r * (startCycleFrame) + i * interval + speed - scaleOffset - 1, 1)
                bdScaleLocAnim(loc, r * (startCycleFrame) + i * interval + speed - 1, 0.001)

                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=(r + 1) * startCycleFrame, value=1)
                pm.setKeyframe(allMotionPath[i - 1] + '.uValue', time=(r + 1) * startCycleFrame + 1, value=0)
                bdScaleLocAnim(loc, (r + 1) * startCycleFrame - 1, 0.001)


def bdScaleLocAnim(loc, time, val):
    pm.setKeyframe(loc + '.scaleX', time=time, value=val)
    pm.setKeyframe(loc + '.scaleY', time=time, value=val)
    pm.setKeyframe(loc + '.scaleZ', time=time, value=val)


def bdSetStartMp(allMotionPath):
    animCtrl = pm.ls('L_crying_CTL')[0]
    interval = 1.0 / (len(allMotionPath) - 1)
    for i in range(len(allMotionPath)):
        uAnim = pm.listConnections('%s.uValue' % allMotionPath[i])
        if uAnim:
            pm.delete(uAnim)
        motionPath = pm.ls(allMotionPath[i])[0]
        remapNode = pm.createNode('remapValue', n=motionPath.name().replace('_grp_mp', '_rv'))
        pm.setAttr(remapNode + ".color[0].color_Color", 0, 0, 0, type='double3')
        pm.setAttr(remapNode + ".color[2].color_Position", 0.5)
        pm.setAttr(remapNode + ".color[2].color_Color", 1 - i * interval, 0, 0, type='double3')
        pm.setAttr(remapNode + ".color[0].color_Interp", 1)
        pm.setAttr(remapNode + ".color[1].color_Interp", 1)
        pm.setAttr(remapNode + ".color[2].color_Interp", 1)

        remapNode.inputMax.set(10)
        # remapNode.outputMax.set(1 - i*interval)

        animCtrl.attr('crying_tears').connect(remapNode.inputValue)
        # remapNode.outValue.connect(motionPath.uValue)
        remapNode.outColorR.connect(motionPath.uValue)

        def bdSetStartMp(allMotionPath):
            animCtrl = pm.ls('L_crying_CTL')[0]
            interval = 1.0 / (len(allMotionPath) - 1)
            for i in range(len(allMotionPath)):
                uAnim = pm.listConnections('%s.uValue' % allMotionPath[i])
                if uAnim:
                    pm.delete(uAnim)
                motionPath = pm.ls(allMotionPath[i])[0]
                remapNode = pm.createNode('remapValue', n=motionPath.name().replace('_grp_mp', '_rv'))
                pm.setAttr(remapNode + ".color[0].color_Color", 0, 0, 0, type='double3')
                pm.setAttr(remapNode + ".color[2].color_Position", 0.5)
                pm.setAttr(remapNode + ".color[2].color_Color", 1 - i * interval, 0, 0, type='double3')
                pm.setAttr(remapNode + ".color[0].color_Interp", 1)
                pm.setAttr(remapNode + ".color[1].color_Interp", 1)
                pm.setAttr(remapNode + ".color[2].color_Interp", 1)

                remapNode.inputMax.set(10)
                # remapNode.outputMax.set(1 - i*interval)

                animCtrl.attr('crying_tears').connect(remapNode.inputValue)
                # remapNode.outValue.connect(motionPath.uValue)
                remapNode.outColorR.connect(motionPath.uValue)
