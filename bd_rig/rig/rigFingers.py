import pymel.core as pm


def bdAddAllFingerAttr(side):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    fingerList = ['Index', 'Middle', 'Ring', 'Pinky', 'Thumb']
    attrList = ['Bend', 'Curl', 'Spread', 'Scrunch', 'Twist', 'BendMeta', 'SpreadMeta']

    print 'bla'
    for attr in attrList:
        pm.addAttr(fingerAnim, ln=attr, nn='--------', at='enum', en=attr + ':')
        fingerAnim.attr(attr).setKeyable(True)
        fingerAnim.attr(attr).setLocked(True)
        for finger in fingerList:
            if 'Meta' not in attr or 'Thumb' not in finger:
                pm.addAttr(fingerAnim, ln=finger + '_' + attr, at='float', dv=0, min=-10, max=10)
                pm.setAttr((fingerAnim + "." + finger + '_' + attr), e=True, keyable=True)


def bdAddSdkCtrl(side, fingerList, toe=0):
    if not fingerList:
        fingerList = ['Index', 'Middle', 'Ring', 'Pinky', 'Thumb']

    for finger in fingerList:
        fingerJoints = pm.ls(side + '*' + finger + '*' + 'RIG')
        if fingerJoints:
            if finger == 'Thumb':
                toCreate = fingerJoints
            else:
                toCreate = fingerJoints[1:]
            if toe:
                toCreate = fingerJoints
            for jnt in toCreate:
                bdCreateCircleCtrl(jnt.name())

            bdGroupCtrls(side + '*' + finger)


def bdCreateCircleCtrl(jnt):
    ctrl = pm.circle(nr=[1, 0, 0], r=10)[0]
    jntNum = jnt.split('_')[-2]
    ctrlNum = '0' + str(int(jntNum))

    ctrlName = jnt.replace('RIG', 'ctrl').replace(jntNum, ctrlNum)
    ctrl.rename(ctrlName)
    sdkGrp = pm.group(name=ctrl.name() + '_sdk')
    ctrlGrp = pm.group(name=sdkGrp.name() + '_grp')
    pm.parent(ctrl, sdkGrp)
    pm.parent(sdkGrp, ctrlGrp)

    temp = pm.parentConstraint(jnt, ctrlGrp)
    pm.delete(temp)
    pm.parentConstraint(ctrl, jnt)


def bdGroupCtrls(finger):
    fingerCtrls = pm.ls(finger + '*ctrl_sdk_grp')
    fingerCtrls.reverse()
    print fingerCtrls
    for i in range(len(fingerCtrls) - 1):
        ctrlUp = pm.ls(fingerCtrls[i + 1].replace('ctrl_sdk_grp', 'ctrl'))
        pm.parent(fingerCtrls[i], ctrlUp)
    if 'Thumb' not in finger:
        fingerMeta = pm.ls(finger + '*00_RIG')
        pm.parentConstraint(fingerMeta, fingerCtrls[-1], mo=1)


def bdAddSDK(side):
    fingerList = ['Index', 'Middle', 'Ring', 'Pinky', 'Thumb']
    attrList = ['SpreadMeta', 'Spread', 'Curl', 'Scrunch', 'Twist', 'BendMeta', 'Bend']
    for finger in fingerList:
        print ' ---------- START  ' + finger + ' ------------------------'
        for attr in attrList:
            if attr == 'Spread':
                print 'Spread'
                bdAddSpread(side, finger, finger + '_' + attr)
            elif attr == 'SpreadMeta':
                print 'Spread Meta'
                bdAddSpreadMeta(side, finger, finger + '_' + attr)
            elif attr == 'Curl':
                print 'Curl ' + side + '  ' + finger
                bdAddCurl(side, finger, finger + '_' + attr)
            elif attr == 'Scrunch':
                print 'Scrunch'
                bdAddScrunch(side, finger, finger + '_' + attr)
            elif attr == 'Twist':
                print 'Twist'
                bdAddTwist(side, finger, finger + '_' + attr)
            elif attr == 'BendMeta':
                print 'BendMeta'
                bdAddBendMeta(side, finger, finger + '_' + attr)
            elif attr == 'Bend':
                print 'Bend'
                bdAddBend(side, finger, finger + '_' + attr)
        print ' ---------- END  ' + finger + ' ------------------------'


def bdAddSpreadMeta(side, finger, attr):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    if finger != 'Thumb':
        startFingerJnt = pm.ls(side + finger + '*_00_RIG')[0]
        print startFingerJnt
        pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=10, v=-10)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=-10, v=10)


def bdAddSpread(side, finger, attr):
    print 'adding spread for %s %s' % (side, finger)
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    startFingerSdk = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]

    pm.setDrivenKeyframe(startFingerSdk, at='rotatey', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=10, v=30)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=-10, v=-30)

    if finger == 'thumb':
        pm.setDrivenKeyframe(startFingerSdk, at='rotatey', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(startFingerSdk, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=10, v=90)
        pm.setDrivenKeyframe(startFingerSdk, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=-10, v=-90)
    '''
    spreadRv = pm.createNode('remapValue',name = startFinger.name() + '_ry_rv')
    spreadRv.inputMin.set(-10)
    spreadRv.inputMax.set(10)

    spreadRv.outputMin.set(-30)
    spreadRv.outputMax.set(30)
    if finger == 'Thumb':
        spreadRv.outputMin.set(-90)
        spreadRv.outputMax.set(90)


    fingerAnim.attr(attr).connect(spreadRv.inputValue)
    spreadRv.outValue.connect(startFinger.rotateY)
    '''


def bdAddCurl(side, finger, attr):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    targetValuesDown = [-100, -90, -125]
    targetValuesDownThumb = [100, 90, 125]
    sdkFingers = pm.ls(side + '*' + finger + '*_sdk')
    print sdkFingers
    rev = 1
    if side == 'Right':
        rev = -1
    for sdk in sdkFingers[:-1]:
        if finger != 'Thumb':
            print 'Add curl for %s %s' % (side, finger)
            pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
            pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10,
                                 v=targetValuesDown[sdkFingers.index(sdk)])
            pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=25)
        else:
            pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
            pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10,
                                 v=targetValuesDown[sdkFingers.index(sdk)])
            pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=-25)


def bdAddScrunch(side, finger, attr):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    targetValuesUp = [70, -85, -60]
    targetValuesDown = [-45, 45, 45]
    sdkFingers = pm.ls(side + '*' + finger + '_sdk')
    for finger in sdkFingers[:-1]:
        pm.setDrivenKeyframe(finger, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(finger, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10,
                             v=targetValuesUp[sdkFingers.index(finger)])
        pm.setDrivenKeyframe(finger, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10,
                             v=targetValuesDown[sdkFingers.index(finger)])


def bdAddTwist(side, finger, attr):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    startFingerSdk = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]
    pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd=fingerAnim.name() + '.' + attr, dv=10, v=-90)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd=fingerAnim.name() + '.' + attr, dv=-10, v=90)


def bdAddBendMeta(side, finger, attr):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    if finger != 'Thumb':
        startFingerJnt = pm.ls(side + '*' + finger + '*_00_RIG')[0]
        startFingerSdk = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10, v=-45)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=45)

        # pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
        # pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = 45)
        # pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = -45)


def bdAddBend(side, finger, attr):
    fingerAnim = pm.ls(side + '*Fingers_ctrl', type='transform')[0]
    startFingerSdk = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]
    startFingerJnt = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]

    rev = 1;
    if side == 'Right':
        rev = -1
    if finger != 'Thumb':
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10, v=-90)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=90)
    else:
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10, v=rev * -90)
        pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=rev * 90)


def bdScaleHand(side):
    handJnt = ['hand', 'palm']
    ikfk = pm.ls(side + '_arm_ikfk_ctrl')[0]
    allFingers = pm.ls(side + '*finger*BND')
    for finger in allFingers:
        ikfk.attr('handScale').connect(finger.scaleX)
        ikfk.attr('handScale').connect(finger.scaleY)
        ikfk.attr('handScale').connect(finger.scaleZ)
    for jnt in handJnt:
        for type in ['fk', 'ik']:
            j = pm.ls(side + '*' + jnt + '*' + type)[0]
            print jnt
            ikfk.attr('handScale').connect(j.scaleX)
            ikfk.attr('handScale').connect(j.scaleY)
            ikfk.attr('handScale').connect(j.scaleZ)
    fingersCtrlGrp = pm.ls(side + '*fingers_grp')[0]
    ikfk.attr('handScale').connect(fingersCtrlGrp.scaleX)
    ikfk.attr('handScale').connect(fingersCtrlGrp.scaleY)
    ikfk.attr('handScale').connect(fingersCtrlGrp.scaleZ)

# bdAddAllFingerAttr("L")
# bdAddSDK("L_")
# bdAddAllFingerAttr("R")
# bdAddSDK("R_")
