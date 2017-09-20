import pymel.core as pm


def bdAddAllFingerAttr(side, fingerList):
    fingerAnim = pm.ls(side + '*_toes_ctrl', type='transform')[0]
    # fingerList = ['Index','Middle','Pinky','Thumb']
    attrList = ['Bend', 'Curl', 'Spread', 'Scrunch', 'Twist']

    for attr in attrList:
        pm.addAttr(fingerAnim, ln=attr, nn='--------', at='enum', en=attr + ':')
        fingerAnim.attr(attr).setKeyable(True)
        fingerAnim.attr(attr).setLocked(True)
        for finger in fingerList:
            pm.addAttr(fingerAnim, ln=finger + '_' + attr, at='float', dv=0, min=-10, max=10)
            pm.setAttr((fingerAnim + "." + finger + '_' + attr), e=True, keyable=True)


def bdAddSdkCtrl(side, fingerList):
    if not fingerList:
        fingerList = ['index', 'middle', 'pinky', 'thumb']

    for finger in fingerList:
        fingerJoints = pm.ls(side + '*' + finger + '*' + 'bnd')
        if fingerJoints:
            for jnt in fingerJoints:
                bdCreateCircleCtrl(jnt.name())

            bdGroupCtrls(fingerJoints[0])


def bdCreateCircleCtrl(jnt):
    ctrl = pm.circle(nr=[1, 0, 0])[0]

    ctrlName = jnt.replace('bnd', 'ctrl')
    ctrl.rename(ctrlName)
    sdkGrp = pm.group(name=ctrl.name() + '_sdk')
    ctrlGrp = pm.group(name=ctrl.name() + '_grp')
    pm.parent(ctrl, sdkGrp)
    pm.parent(sdkGrp, ctrlGrp)

    temp = pm.parentConstraint(jnt, ctrlGrp)
    pm.delete(temp)
    pm.parentConstraint(ctrl, jnt)


def bdGroupCtrls(finger):
    fingerCtrls = pm.ls(finger.replace('_01_bnd', '*ctrl_grp'))
    fingerCtrls.reverse()
    for i in range(len(fingerCtrls) - 1):
        ctrlUp = pm.ls(fingerCtrls[i + 1].replace('ctrl_grp', 'ctrl'))
        pm.parent(fingerCtrls[i], ctrlUp)


def bdAddSDK(side, fingerList):
    # fingerList =  ['Index','Middle','Pinky','Thumb']
    attrList = ['Spread', 'Curl', 'Scrunch', 'Twist', 'Bend']
    for finger in fingerList:
        for attr in attrList:
            if attr == 'Spread':
                print 'Spread'
                bdAddSpread(side, finger.lower(), finger + '_' + attr)
            elif attr == 'Curl':
                print 'Curl'
                bdAddCurl(side, finger.lower(), finger + '_' + attr)
            elif attr == 'Scrunch':
                print 'Scrunch'
                bdAddScrunch(side, finger.lower(), finger + '_' + attr)
            elif attr == 'Twist':
                print 'Twist'
                bdAddTwist(side, finger.lower(), finger + '_' + attr)
            elif attr == 'Bend':
                print 'Bend'
                bdAddBend(side, finger.lower(), finger + '_' + attr)


def bdAddSpread(side, finger, attr):
    print 'adding spread for %s %s' % (side, finger)
    fingerAnim = pm.ls(side + '*toes_ctrl', type='transform')[0]
    startFingerSdk = pm.ls(side + '*' + finger.lower() + '*_01_ctrl_sdk')[0]

    pm.setDrivenKeyframe(startFingerSdk, at='rotatey', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=10, v=30)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateY', cd=fingerAnim.name() + '.' + attr, dv=-10, v=-30)

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
    fingerAnim = pm.ls(side + '*toes_ctrl', type='transform')[0]
    targetValuesDown = [-100, -90, -125]
    targetValuesDownThumb = [100, 90, 125]
    sdkFingers = pm.ls(side + '*' + finger + '_*_sdk')
    rev = 1;
    if side == 'right':
        rev = -1
    for sdk in sdkFingers:
        print 'Add curl for %s %s' % (side, finger)
        pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10,
                             v=targetValuesDown[sdkFingers.index(sdk)])
        pm.setDrivenKeyframe(sdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=25)


def bdAddScrunch(side, finger, attr):
    fingerAnim = pm.ls(side + '*toes_ctrl', type='transform')[0]
    targetValuesUp = [70, -85, -60]
    targetValuesDown = [-45, 45, 45]
    sdkFingers = pm.ls(side + '*' + finger + '_*_sdk')
    for finger in sdkFingers:
        pm.setDrivenKeyframe(finger, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
        pm.setDrivenKeyframe(finger, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10,
                             v=targetValuesUp[sdkFingers.index(finger)])
        pm.setDrivenKeyframe(finger, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10,
                             v=targetValuesDown[sdkFingers.index(finger)])


def bdAddTwist(side, finger, attr):
    fingerAnim = pm.ls(side + '*toes_ctrl', type='transform')[0]
    startFingerSdk = pm.ls(side + '*' + finger.lower() + '*_01_ctrl_sdk')[0]
    pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd=fingerAnim.name() + '.' + attr, dv=10, v=-90)
    pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd=fingerAnim.name() + '.' + attr, dv=-10, v=90)


def bdAddBend(side, finger, attr):
    fingerAnim = pm.ls(side + '*toes_ctrl', type='transform')[0]
    startFingerSdk = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]
    startFingerJnt = pm.ls(side + '*' + finger + '*_01_ctrl_sdk')[0]

    pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10, v=-90)
    pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=90)


def bdScaleHand(side):
    handJnt = ['hand', 'palm']
    ikfk = pm.ls(side + '_arm_ikfk_ctrl')[0]
    allFingers = pm.ls(side + '*finger*bnd')
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
