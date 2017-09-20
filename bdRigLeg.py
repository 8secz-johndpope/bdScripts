import pymel.core as pm

import utils.bdScaleSpline as scaleUtil

reload(scaleUtil)

legBonesNames = ['Leg_1', 'Leg_2', 'Leg_3', 'Leg_4', 'Leg_end']
bndString = 'rig'
foot_bend_axis = 'Z'
foot_bend_direction = -1

def bdBuildDrvChain(side, drvType):
    startLegJnt = pm.ls(side + legBonesNames[0] + '_' + bndString, type='joint')[0]
    newChainStart = pm.duplicate(startLegJnt, name=startLegJnt.name().replace(bndString, drvType))[0]
    newRelatives = newChainStart.listRelatives(ad=True, type='joint', pa=True)
    newRelatives.reverse()

    for jnt in newRelatives:
        if bndString in jnt.name():
            jnt.rename(jnt.name().split('|')[-1].replace(bndString, drvType))
        elif 'end' in jnt.name():
            jnt.rename(jnt.name().split('|')[-1] + '_' + drvType)

    newChain = [newChainStart] + newRelatives
    return newChain


# create a group based rig for a leg
def bdRigIkLeg(side):
    ikAnimCon = pm.ls(side + 'Leg_ik_ctrl', type='transform')[0]

    legBones = []
    for bone in legBonesNames:
        legBone = pm.ls(side + bone + '_ik')[0]
        legBones.append(legBone)
        print legBone.name()

    # START setup foot roll
    footIk = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=legBones[0], endEffector=legBones[2],
                         name=side + '_foot_ikHandle')[0]
    footIk.visibility.set(0)
    ballIk = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=legBones[2], endEffector=legBones[3],
                         name=side + '_ball_ikHandle')[0]
    ballIk.visibility.set(0)
    toeIk = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=legBones[3], endEffector=legBones[4],
                        name=side + '_toe_ikHandle')[0]
    toeIk.visibility.set(0)
    # create the groups that will controll the foot animations ( roll, bend, etc etc)
    footHelpers = pm.ls(side + '*_helper', type='transform')

    ankleLoc = bdCreateOffsetLoc(legBones[2], side + '_ankle_loc')
    footLoc = bdCreateOffsetLoc(legBones[2], side + '_foot_loc')
    ballLoc = bdCreateOffsetLoc(legBones[3], side + '_ball_loc')
    ballTwistLoc = bdCreateOffsetLoc(legBones[3], side + '_ball_twist_loc')
    toeLoc = bdCreateOffsetLoc(legBones[4], side + '_toe_loc')
    toeBendLoc = bdCreateOffsetLoc(legBones[3], side + '_toe_bend_loc')

    innerLoc = outerLoc = heelLoc = ''
    for helper in footHelpers:
        if 'inner' in helper.name():
            innerLoc = bdCreateOffsetLoc(helper, side + '_inner_bank_loc')
        elif 'outer' in helper.name():
            outerLoc = bdCreateOffsetLoc(helper, side + '_outer_bank_loc')
        elif 'heel' in helper.name():
            heelLoc = bdCreateOffsetLoc(helper, side + '_heel_loc')

    # pm.delete(footHelpers)


    pm.parent(footIk, footLoc)
    pm.parent(ballIk, ballLoc)
    pm.parent(toeIk, toeBendLoc)
    pm.parent(toeBendLoc, toeLoc)

    pm.parent(footLoc, ballLoc)
    pm.parent(ballLoc, toeLoc)
    pm.parent(toeLoc, ballTwistLoc)
    pm.parent(ballTwistLoc, innerLoc)
    pm.parent(innerLoc, outerLoc)
    pm.parent(outerLoc, heelLoc)
    pm.parent(heelLoc, ankleLoc)

    print "start adding attributes"
    # add atributes on the footGrp - will be conected later to an anim controler
    autoRollAttrList = ['Roll', 'ToeStart', 'BallStraight']
    footAttrList = ['HeelTwist', 'BallTwist', 'TipTwist', 'Bank', 'ToeBend', 'KneeTwist']

    pm.addAttr(ikAnimCon, ln='separator1', nn='------', at='enum', en=['Roll'])
    ikAnimCon.attr('separator1').setKeyable(True)
    ikAnimCon.attr('separator1').setLocked(True)

    for attr in autoRollAttrList:
        pm.addAttr(ikAnimCon, ln=attr, nn=attr, at='float')
        ikAnimCon.attr(attr).setKeyable(True)

    pm.addAttr(ikAnimCon, ln='separator2', nn='------', at='enum', en=['Extras'])
    ikAnimCon.attr('separator2').setKeyable(True)
    ikAnimCon.attr('separator2').setLocked(True)

    for attr in footAttrList:
        pm.addAttr(ikAnimCon, ln=attr, nn=attr, at='float')
        ikAnimCon.attr(attr).setKeyable(True)

    ikAnimCon.attr('ToeStart').set(40)
    ikAnimCon.attr('BallStraight').set(80)
    bdCreateReverseFootRoll(ikAnimCon, heelLoc, ballLoc, toeLoc)

    # connect the attributes
    ikAnimCon.attr('HeelTwist').connect(heelLoc.rotateY)
    ikAnimCon.attr('BallTwist').connect(ballTwistLoc.rotateY)
    ikAnimCon.attr('TipTwist').connect(toeLoc.rotateY)
    ikAnimCon.attr('ToeBend').connect(toeBendLoc.rotateX)

    bdConnectBank(ikAnimCon, innerLoc, outerLoc)

    # # START no flip knee knee
    # mirror = 1
    # if side == 'R':
    #     mirror = -1
    #
    # poleVectorLoc = pm.spaceLocator(name=side + '_knee_loc_PV')
    # poleVectorLocGrp = pm.group(poleVectorLoc, n=poleVectorLoc + '_GRP')
    #
    # thighPos = legBones[0].getTranslation(space='world')
    # poleVectorLocGrp.setTranslation([thighPos[0] + mirror * 5, thighPos[1], thighPos[2]])
    #
    # pm.poleVectorConstraint(poleVectorLoc, footIk)
    #
    # adlNode = pm.createNode('addDoubleLinear', name=side + '_adl_twist')
    #
    # adlNode.input2.set(mirror * 90)
    #
    # ikAnimCon.attr('KneeTwist').connect(adlNode.input1)
    # adlNode.output.connect(footIk.twist)
    #
    # startTwist = mirror * 90
    # limit = 0.001
    # increment = mirror * 0.01
    #
    # while True:
    #     pm.select(cl=True)
    #     thighRot = pm.xform(legBones[0], q=True, ro=True, os=True)
    #     if ((thighRot[0] > limit)):
    #         startTwist = startTwist - increment
    #         adlNode.input2.set(startTwist)
    #
    #     else:
    #         break
    #
    # # END knee

    pm.parent(ankleLoc, ikAnimCon)


def bdCreateOffsetLoc(destination, name):
    loc = pm.spaceLocator(n=name)
    destPos = destination.getTranslation(space='world')
    loc.setTranslation(destPos, space='world')
    return loc


def bdCreateReverseFootRoll(ankleLoc, heelLoc, ballLoc, toeLoc):
    # setup auto part
    clampHeel = pm.createNode('clamp', n=heelLoc.name().replace('loc', 'roll_CL'))
    clampHeel.minR.set(-90)

    setRangeToe = pm.createNode('setRange', n=toeLoc.name().replace('loc', 'linestep_SR'))
    setRangeToe.minX.set(0)
    setRangeToe.maxX.set(1)

    setRangeBall1 = pm.createNode('setRange', n=ballLoc.name().replace('loc', 'linestep_SR'))
    setRangeBall1.minX.set(0)
    setRangeBall1.maxX.set(1)
    setRangeBall1.oldMinX.set(0)

    mdToeRoll = pm.createNode('multiplyDivide', n=toeLoc.name().replace('loc', 'roll_MD'))
    mdBallRoll = pm.createNode('multiplyDivide', n=ballLoc.name().replace('loc', 'roll_MD'))

    mdBallRange2 = pm.createNode('multiplyDivide', n=ballLoc.name().replace('loc', 'roll_range_MD'))

    pmaBallRange = pm.createNode('plusMinusAverage', n=ballLoc.name().replace('loc', 'range_PMA'))
    pmaBallRange.input1D[0].set(1)
    pmaBallRange.operation.set(2)

    # connect the heel for negative rolls
    ankleLoc.attr('Roll').connect(clampHeel.inputR)

    if foot_bend_direction == -1:
        rev_node = pm.shadingNode('multDoubleLinear',asUtility=1,name=heelLoc.name() + '_r' + foot_bend_axis + '_mdl')
        clampHeel.outputR.connect(rev_node.input1)
        rev_node.input2.set(-1)
        rev_node.output.connect(heelLoc.attr('rotate' + foot_bend_axis))
    else:
        clampHeel.outputR.connect(heelLoc.attr('rotate' + foot_bend_axis))
    # clampHeel.outputR.connect(blendColorHeelAuto.color1R)
    # blendColorHeelAuto.outputR.connect(heelLoc.rotateX)

    # connect the toe
    ankleLoc.attr('Roll').connect(setRangeToe.valueX)
    ankleLoc.attr('BallStraight').connect(setRangeToe.oldMaxX)
    ankleLoc.attr('ToeStart').connect(setRangeToe.oldMinX)

    ankleLoc.attr('Roll').connect(mdToeRoll.input2X)
    setRangeToe.outValueX.connect(mdToeRoll.input1X)

    if foot_bend_direction == -1:
        rev_node = pm.shadingNode('multDoubleLinear',asUtility=1,name=toeLoc.name() + '_r' + foot_bend_axis + '_mdl')
        rev_node.input2.set(-1)
        mdToeRoll.outputX.connect(rev_node.input1)
        rev_node.output.connect(toeLoc.attr('rotate' + foot_bend_axis))
    else:
        mdToeRoll.outputX.connect(toeLoc.attr('rotate' + foot_bend_axis))
    # mdToeRoll.outputX.connect(blendColorToeAuto.color1R)
    # blendColorToeAuto.outputR.connect(toeLoc.rotateX)

    # connect the ball
    ankleLoc.attr('Roll').connect(setRangeBall1.valueX)
    ankleLoc.attr('ToeStart').connect(setRangeBall1.oldMaxX)

    setRangeToe.outValueX.connect(pmaBallRange.input1D[1])

    setRangeBall1.outValueX.connect(mdBallRange2.input1X)
    pmaBallRange.output1D.connect(mdBallRange2.input2X)

    ankleLoc.attr('Roll').connect(mdBallRoll.input2X)
    mdBallRange2.outputX.connect(mdBallRoll.input1X)

    if foot_bend_direction == -1:
        rev_node = pm.shadingNode('multDoubleLinear',asUtility=1,name=ballLoc.name() + '_r' + foot_bend_axis + '_mdl')
        rev_node.input2.set(-1)
        mdBallRoll.outputX.connect(rev_node.input1)
        rev_node.output.connect(ballLoc.attr('rotate' + foot_bend_axis))
    else:
        mdBallRoll.outputX.connect(ballLoc.attr('rotate' + foot_bend_axis))
    # mdBallRoll.outputX.connect(blendColorBallAuto.color1R)
    # blendColorBallAuto.outputR.connect(ballLoc.rotateX)
    # setup manual


def bdConnectBank(ikAnimCon, innerLoc, outerLoc):
    side = 'L'
    if 'R_' in ikAnimCon.name():
        side = 'R'
    clampInner = pm.createNode('clamp', n=innerLoc.name().replace('loc', 'CL'))
    if side == 'L':
        clampInner.maxR.set(90)
    else:
        clampInner.minR.set(-90)

    clampOuter = pm.createNode('clamp', n=outerLoc.name().replace('loc', 'CL'))
    if side == 'L':
        clampOuter.minR.set(-90)
    else:
        clampOuter.maxR.set(90)

    ikAnimCon.attr('Bank').connect(clampInner.inputR)
    clampInner.outputR.connect(innerLoc.rotateZ)

    ikAnimCon.attr('Bank').connect(clampOuter.inputR)
    clampOuter.outputR.connect(outerLoc.rotateZ)


def bdConnectChains(side, rigString, ikString, fkString):
    rigBones = []
    for bone in legBonesNames[:-1]:
        legBone = pm.ls(side + bone + '_' + rigString)[0]
        rigBones.append(legBone)
        print legBone.name()

    for jnt in rigBones:
        if rigString in jnt.name():
            fkJnt = None
            ikJnt = None
            searchFkJnt = pm.ls(jnt.name().replace(rigString, fkString))
            if searchFkJnt:
                fkJnt = searchFkJnt[0]

            searchIkJnt = pm.ls(jnt.name().replace(rigString, ikString))
            if searchIkJnt:
                ikJnt = searchIkJnt[0]

            print fkJnt, ikJnt
            if fkJnt and ikJnt:
                # baseName = ''.join([i for i in jnt.name().split("_")[0] if not i.isdigit()])
                cfgCtrl = pm.ls(side + '*cfg_ctrl')[0]
                if cfgCtrl.hasAttr('fkIk'):
                    print 'has attr already'
                else:
                    pm.addAttr(cfgCtrl, ln='fkIk', nn='fkIk', at='float')
                    cfgCtrl.attr('fkIk').setMin(0)
                    cfgCtrl.attr('fkIk').setMax(1)
                    cfgCtrl.attr('fkIk').setKeyable(True)
                bdCreateBlend(jnt, fkJnt, ikJnt, cfgCtrl)


def bdCreateBlend(bindJnt, fkJnt, ikJnt, ikCtrl):
    blendColorPos = pm.createNode('blendColors', name=bindJnt.name().replace(bndString, 'pos_bc'))
    blendColorRot = pm.createNode('blendColors', name=bindJnt.name().replace(bndString, 'rot_bc'))
    blendColorScl = pm.createNode('blendColors', name=bindJnt.name().replace(bndString, 'scl_bc'))


    ikCtrl.attr('fkIk').connect(blendColorPos.blender)
    ikCtrl.attr('fkIk').connect(blendColorRot.blender)
    ikCtrl.attr('fkIk').connect(blendColorScl.blender)

    fkJnt.translate.connect(blendColorPos.color2)
    ikJnt.translate.connect(blendColorPos.color1)
    blendColorPos.output.connect(bindJnt.translate)

    fkJnt.rotate.connect(blendColorRot.color2)
    ikJnt.rotate.connect(blendColorRot.color1)
    blendColorRot.output.connect(bindJnt.rotate)

    fkJnt.scale.connect(blendColorScl.color2)
    ikJnt.scale.connect(blendColorScl.color1)
    blendColorScl.output.connect(bindJnt.scale)


def rig(side):
    bdBuildDrvChain(side, 'fk')
    ikChain = bdBuildDrvChain(side, 'ik')
    bdRigIkLeg(side)
    #scaleUtil.bdScaleIkChain(startJoint=ikChain[0], condition=False)
    bdConnectChains(side, bndString, 'ik', 'fk')

# bdRigLegBones('L')
# bdRigLegBones('R')
# bdConnectChains()

# bdScaleChain('R')
# bdScaleChain('L')
