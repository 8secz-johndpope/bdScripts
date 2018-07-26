import pymel.core as pm
import utils.libControllers as ctrl

reload(ctrl)
import utils.bdScaleSpline as scaleUtil

reload(scaleUtil)


def build_drv_chain(start, drvSuffix):
    if len(start):
        startLegJnt = pm.ls(start, type='joint')[0]
        newChainStart = pm.duplicate(startLegJnt, name=startLegJnt.name() + drvSuffix)[0]
        pm.parent(newChainStart, w=1)
        newRelatives = newChainStart.listRelatives(ad=True, type='joint', pa=True)
        newRelatives.reverse()

        for jnt in newRelatives:
            jnt.rename(jnt.name() + drvSuffix)

        newChain = [newChainStart] + newRelatives
        return newChain
    else:
        print 'No start joint selected'
        return 0


def rig_quad_leg(ikChain, ikSpringChain, helper_loc):
    # create foot controller
    ctrl_name = ikChain[3].split('_')[0] + '_foot_ctrl'
    foot_ctrl = ctrl.Controller(name=ctrl_name, target=ikChain[3], scale=20)
    foot_ctrl.buildCircleController()
    foot_ctrl.setPosition()

    # create pole vector controller
    pv_ctrl_name = ctrl_name.replace('foot', 'pv')
    pv_ctrl = ctrl.Controller(name=pv_ctrl_name, scale=20)
    pv_ctrl.buildCircleController()
    pv_ctrl_pos = ctrl.Controller.pole_vector_pos(ikChain[0], ikChain[1], ikChain[2])
    pm.xform(pv_ctrl.ctrlGrp, t=pv_ctrl_pos)

    # create ik handles
    footIk = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=ikChain[0], endEffector=ikChain[2],
                         name=ikChain[2].name().replace('ik', 'foot_ikHandle'))[0]
    footIk.visibility.set(0)
    ballIk = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=ikChain[2], endEffector=ikChain[3],
                         name=ikChain[3].name().replace('ik', 'ball_ikHandle'))[0]
    ballIk.visibility.set(0)
    toeIk = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=ikChain[3], endEffector=ikChain[4],
                        name=ikChain[3].name().replace('ik', 'toe_ikHandle'))[0]
    toeIk.visibility.set(0)
    # pm.mel.eval('ikSpringSolver')
    springIk = \
    pm.ikHandle(sol='ikSpringSolver', sticky='sticky', startJoint=ikSpringChain[0], endEffector=ikSpringChain[-1],
                name=ikSpringChain[-1].name().replace('ikSpring', 'ikSpringHandle'))[0]
    springIk.visibility.set(0)

    # pole vector constraints
    pm.poleVectorConstraint(pv_ctrl.ctrlName, footIk)
    pm.poleVectorConstraint(pv_ctrl.ctrlName, springIk)

    # create the locators for the custom attributes
    rollFrontLoc = pm.spaceLocator(name=ikChain[3].name().replace('ik', 'rollFront_loc'))
    rollBackLoc = pm.spaceLocator(name=ikChain[3].name().replace('ik', 'rollBack_loc'))
    compressLoc = pm.spaceLocator(name=ikChain[3].name().replace('ik', 'compress_loc'))
    hoofLoc = pm.spaceLocator(name=ikChain[4].name().replace('ik', 'hoof_loc'))
    ankleLoc = pm.spaceLocator(name=ikChain[3].name().replace('ik', 'ankle_loc'))
    ankleLocGrp = pm.group(name=ankleLoc.name() + '_grp')

    pos = pm.xform(ikChain[3], q=1, t=1, ws=1)
    pm.xform(ankleLoc, t=pos)

    for loc in helper_loc:
        pos = pm.xform(loc, q=1, t=1, ws=1)
        if 'rollFront' in loc.name():
            pm.xform(rollFrontLoc, t=pos)
        elif 'rollBack' in loc.name():
            pm.xform(rollBackLoc, t=pos)

    pos = pm.xform(ikChain[4], q=1, t=1, ws=1)
    pm.xform(compressLoc, t=pos)
    pm.xform(hoofLoc, t=pos)

    pm.parent(compressLoc, rollBackLoc)
    pm.parent(rollBackLoc, rollFrontLoc)
    pm.parent(rollFrontLoc, foot_ctrl.ctrlName)
    pm.parent(hoofLoc, rollBackLoc)
    pm.parent(ankleLocGrp, ikSpringChain[-1])

    pm.parent(springIk, compressLoc)
    pm.parent(toeIk, rollBackLoc)
    pm.parent(footIk, ankleLoc)
    pm.parent(ballIk, ikSpringChain[-1])

    # add custom attributes
    ctrl.bdAddSeparatorAttr(foot_ctrl.ctrlName, 'Extra')
    ctrl.bdAddAttribute(foot_ctrl.ctrlName, 'footRoll', 'double')
    ctrl.bdAddAttribute(foot_ctrl.ctrlName, 'ankleRoll', 'double')
    ctrl.bdAddAttribute(foot_ctrl.ctrlName, 'compress', 'double')
    ctrl.bdAddAttribute(foot_ctrl.ctrlName, 'hoofBend', 'double')

    # connect the attributes
    # ------------------------------------------------------
    foot_ctrl_node = pm.ls(foot_ctrl.ctrlName)[0]
    # roll back
    rollBackRv = pm.shadingNode('remapValue', asUtility=1, name=rollBackLoc.name().replace('loc', 'rv'))
    rollBackRv.inputMax.set(100)
    rollBackRv.outputMax.set(-100)
    foot_ctrl_node.attr('footRoll') >> rollBackRv.inputValue
    rollBackRv.outValue >> rollBackLoc.rx
    # roll forward
    rollFrontRv = pm.shadingNode('remapValue', asUtility=1, name=rollFrontLoc.name().replace('loc', 'rv'))
    rollFrontRv.inputMax.set(-100)
    rollFrontRv.outputMax.set(100)
    foot_ctrl_node.attr('footRoll') >> rollFrontRv.inputValue
    rollFrontRv.outValue >> rollFrontLoc.rx
    # ankle roll
    foot_ctrl_node.attr('ankleRoll') >> ankleLoc.rx
    # compress
    foot_ctrl_node.attr('compress') >> compressLoc.rx
    # hoof bend
    pm.orientConstraint(hoofLoc, ikChain[-1], mo=1)
    foot_ctrl_node.attr('hoofBend') >> hoofLoc.rx


def rig(start):
    name_template = start.split('_')[0]
    helper_loc = pm.ls(name_template + '*helper')
    if len(helper_loc):
        ikChain = build_drv_chain(start, '_ik')
        ikSpringChain = build_drv_chain(start, '_ikSpring')
        pm.delete(ikSpringChain[-1])
        ikSpringChain.pop()

        rig_quad_leg(ikChain, ikSpringChain, helper_loc)
    else:
        pm.warning('Create the foot helper locators')
