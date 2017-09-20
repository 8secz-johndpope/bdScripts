import utils.libControllers as bdRigUtils
import pymel.core as pm

reload(bdRigUtils)

import utils.libControllers as libCtrl

reload(libCtrl)
from utils.libControllers import Controller

metaName = 'Finger0'
extraGrpSuffix = 'extra'


def bdRigFinger(fingerStart):
    fingerRoot = None
    if isinstance(fingerStart, str):
        found = pm.ls(fingerStart, type='joint')
        if len(found):
            fingerRoot = found[0]
        else:
            pm.warning('Finger joint not found')
            return
    else:
        fingerRoot = fingerStart

    children = pm.listRelatives(fingerRoot, ad=1, type='joint')
    allFingers = children[1:] + [fingerRoot]
    allFingers.reverse()

    ctrlList = bdAddCtrls(allFingers)
    ctrlList.reverse()

    bdAddSdk(ctrlList)


def bdAddCtrls(fingersJnt):
    ctrlList = []
    for jntFinger in fingersJnt:
        pm.undoInfo(openChunk=True)
        ctrl = Controller(name=jntFinger.name().replace('bnd', 'ctrl'), shape='circle', target=jntFinger, scale=10,
                          axis=[1, 0, 0])
        ctrl.buildController()
        ctrl.addExtraGroup(extraGrpSuffix)
        ctrlList.append(ctrl.ctrlName)
        if metaName not in jntFinger.name():
            bdAddAllFingerAttr(ctrl.ctrlName)

        pm.parentConstraint(ctrl.ctrlName, jntFinger)
        pm.undoInfo(closeChunk=True)

    ctrlList.reverse()
    for i in range(len(ctrlList) - 1):
        grp = pm.ls(ctrlList[i] + '_grp')[0]
        pm.parent(grp, ctrlList[i + 1])

    return ctrlList


def bdAddAllFingerAttr(ctrl):
    attrList = ['spread', 'curlVertical', 'curlHorizontal']

    bdRigUtils.bdAddSeparatorAttr(ctrl, 'Extras')
    for attr in attrList:
        pm.addAttr(ctrl, ln=attr, at='float', dv=0, min=-10, max=10)
        pm.setAttr((ctrl + "." + attr), e=True, keyable=True)


def bdAddSdk(ctrlList):
    # bdAddSpread(ctrlList)
    bdAddCurlVertical(ctrlList)
    bdAddCurlHorizontal(ctrlList)


    # bdAddCurl(ctrl)
    # bdAddScrunch(ctrl)
    # bdAddTwist(ctrl)
    # bdAddBendMeta(ctrl)
    # bdAddBend(ctrl)


def bdAddSpread(ctrlList):
    metaFound = [s for s in ctrlList if metaName in s]
    if metaFound:
        extraGrp = pm.ls(ctrlList[1] + '_' + extraGrpSuffix)[0]

        pm.setDrivenKeyframe(extraGrp, at='rotateY', cd=ctrlList[1] + '.Spread', dv=0, v=0)
        pm.setDrivenKeyframe(extraGrp, at='rotateY', cd=ctrlList[1] + '.Spread', dv=10, v=-90)
        pm.setDrivenKeyframe(extraGrp, at='rotateY', cd=ctrlList[1] + '.Spread', dv=-10, v=90)

    else:
        extraGrp = pm.ls(ctrlList[0] + '_' + extraGrpSuffix)[0]

        pm.setDrivenKeyframe(extraGrp, at='rotateY', cd=ctrlList[0] + '.Spread', dv=0, v=0)
        pm.setDrivenKeyframe(extraGrp, at='rotateY', cd=ctrlList[0] + '.Spread', dv=10, v=-90)
        pm.setDrivenKeyframe(extraGrp, at='rotateY', cd=ctrlList[0] + '.Spread', dv=-10, v=90)


def bdAddCurlVertical(ctrlList):
    metaFound = [s for s in ctrlList if metaName in s]
    targetValuesDown = [-100, -90, -125]
    if metaFound:
        ctrlRoot = ctrlList[1]
        for ctrl in ctrlList[1:]:
            extraGrp = pm.ls(ctrl + '_' + extraGrpSuffix)[0]
            print extraGrp, ctrlRoot
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateZ', cd=ctrlRoot + '.curlVertical', dv=0, v=0)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateZ', cd=ctrlRoot + '.curlVertical', dv=10, v=-90)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateZ', cd=ctrlRoot + '.curlVertical', dv=-10, v=90)
    else:
        ctrlRoot = ctrlList[0]
        for ctrl in ctrlList:
            extraGrp = pm.ls(ctrl + '_' + extraGrpSuffix)[0]
            print extraGrp, ctrlRoot
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateZ', cd=ctrlRoot + '.curlVertical', dv=0, v=0)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateZ', cd=ctrlRoot + '.curlVertical', dv=10, v=-90)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateZ', cd=ctrlRoot + '.curlVertical', dv=-10, v=90)


def bdAddCurlHorizontal(ctrlList):
    metaFound = [s for s in ctrlList if metaName in s]
    targetValuesDown = [-100, -90, -125]
    if metaFound:
        ctrlRoot = ctrlList[1]
        for ctrl in ctrlList[1:]:
            extraGrp = pm.ls(ctrl + '_' + extraGrpSuffix)[0]
            print extraGrp, ctrlRoot
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateY', cd=ctrlRoot + '.curlHorizontal', dv=0, v=0)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateY', cd=ctrlRoot + '.curlHorizontal', dv=10, v=-90)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateY', cd=ctrlRoot + '.curlHorizontal', dv=-10, v=90)
    else:
        ctrlRoot = ctrlList[0]
        for ctrl in ctrlList:
            extraGrp = pm.ls(ctrl + '_' + extraGrpSuffix)[0]
            print extraGrp, ctrlRoot
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateY', cd=ctrlRoot + '.curlHorizontal', dv=0, v=0)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateY', cd=ctrlRoot + '.curlHorizontal', dv=10, v=-90)
            pm.setDrivenKeyframe(extraGrp.name(), at='rotateY', cd=ctrlRoot + '.curlHorizontal', dv=-10, v=90)


def bdAddBend(ctrlList):
    metaFound = [s for s in ctrlList if metaName in s]

    #
    # if metaFound:
    #     startFingerSdk = pm.ls(side + finger + '_01_SDK')[0]
    #
    #     pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    #     pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10, v=90)
    #     pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=-90)
    #
    # elif 'Thumb' in ctrlList[0]:
    #     startFingerJnt = pm.ls(side + finger + '_01_SDK')[0]
    #     pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=0, v=0)
    #     pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=10, v=-90)
    #     pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd=fingerAnim.name() + '.' + attr, dv=-10, v=90)
    #
    # def bdAddScrunch(side,finger,attr):
    #     fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
    #     targetValuesUp = [70,-85,-60]
    #     targetValuesDown = [-45,45,45]
    #     sdkFingers = pm.ls(side + finger + '_*_SDK')
    #     for finger in sdkFingers:
    #         print finger.name(), targetValuesUp[sdkFingers.index(finger)], targetValuesDown[sdkFingers.index(finger)]
    #         pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
    #         pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = targetValuesUp[sdkFingers.index(finger)])
    #         pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = targetValuesDown[sdkFingers.index(finger)])
    #
    # def bdAddTwist(side,finger,attr):
    #     fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
    #     startFingerSdk = pm.ls(side + finger + '_01_SDK')[0]
    #     pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
    #     pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -90)
    #     pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 90)
    #
    #
    #
    # def bdAddBendMeta(side,finger,attr):
    #     fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
    #     if finger != 'Thumb':
    #         startFingerJnt = pm.ls(side + finger + '_00_JNT')[0]
    #         startFingerSdk = pm.ls(side + finger + '_01_SDK')[0]
    #         pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
    #         pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -45)
    #         pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 45)
    #
    #         pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
    #         pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = 45)
    #         pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = -45)
    #
    #
    #



    # bdAddAllFingerAttr("L")
    # bdAddSDK("L_")
    # bdAddAllFingerAttr("R")
    # bdAddSDK("R_")
