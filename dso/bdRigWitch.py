import pymel.core as pm


def connectTail():
    tailBc = pm.ls('Spine_*_RIG_*_BC')
    tailConfig = pm.ls('Spine_Config_ctrl')[0]
    for bc in tailBc:
        tailConfig.IKFK >> bc.blender


def connectLeftArm():
    tailBc = pm.ls('LeftArm_*_RIG_*_BC')
    tailConfig = pm.ls('LeftArm_Config_ctrl')[0]
    for bc in tailBc:
        tailConfig.IKFK >> bc.blender


def connectRightArm():
    tailBc = pm.ls('RightArm_*_RIG_*_BC')
    tailConfig = pm.ls('RightArm_Config_ctrl')[0]
    for bc in tailBc:
        tailConfig.IKFK >> bc.blender


def rigLegs():
    legsRoot = pm.ls('*Leg*_1_RIG')

    for leg in legsRoot:
        pm.select(cl=1)
        ctrl = pm.circle(name=leg.name().replace('RIG', 'ctrl'), c=[0, 0, 0], nr=[1, 0, 0], ch=0, radius=20)[0]
        ctrlGrp = pm.group(name=ctrl.name() + '_grp')
        pm.select(cl=1)
        pm.parent(ctrlGrp, leg)
        ctrlGrp.translate.set([0, 0, 0])
        ctrlGrp.rotate.set([0, 0, 0])
        pm.parent(ctrlGrp, w=1)
        pm.parentConstraint(ctrl, leg, mo=1)
        leg2 = leg.listRelatives(type='joint')[0]
        pm.select(cl=1)
        ctrl1 = pm.circle(name=leg2.name().replace('RIG', 'ctrl'), c=[0, 0, 0], nr=[1, 0, 0], ch=0, radius=15)[0]
        ctrl1Grp = pm.group(name=ctrl1.name() + '_grp')
        pm.select(cl=1)
        pm.parent(ctrl1Grp, leg2)
        ctrl1Grp.translate.set([0, 0, 0])
        ctrl1Grp.rotate.set([0, 0, 0])
        pm.parent(ctrl1Grp, w=1)
        pm.parentConstraint(ctrl1, leg2, mo=1)
        pm.parent(ctrl1Grp, ctrl)


def addlegAimposGrp():
    legsRootCtrl = pm.ls('*Leg*_1_ctrl')
    for ctrl in legsRootCtrl:
        pm.select(cl=1)
        ctrlAimposGrp = pm.group(name=ctrl.name() + '_aimpos')
        tmp = pm.parentConstraint(ctrl, ctrlAimposGrp, mo=0)
        pm.delete(tmp)
        pm.parent(ctrlAimposGrp, ctrl.getParent())
        pm.parent(ctrl, ctrlAimposGrp)
        pm.select(cl=1)
        localPosLocator = pm.spaceLocator(name=ctrl.name() + '_local_pos_loc')
        tmp = pm.parentConstraint(ctrl, localPosLocator, mo=0)
        pm.delete(tmp)
        pm.select(cl=1)
        worldPosLocator = pm.spaceLocator(name=ctrl.name() + '_world_pos_loc')
        tmp = pm.parentConstraint(ctrl, worldPosLocator, mo=0)
        pm.delete(tmp)
        pm.select(cl=1)
        pm.group([localPosLocator, worldPosLocator], w=1, name=ctrl.name() + '_pos_grp')
        pm.select(cl=1)
        pm.pointConstraint([localPosLocator, worldPosLocator], ctrlAimposGrp, mo=1)
        jnt = pm.ls(ctrl.name().replace('ctrl', 'RIG'))[0]
        jntParent = jnt.getParent()
        pm.parentConstraint(jntParent, localPosLocator, mo=1)
        # addAimCtrl(ctrl)


def addAimCtrl(ctrl):
    pm.select(cl=1)
    aimCtrl = pm.circle(name=ctrl.name().replace('ctrl', 'aim_ctrl'), c=[0, 0, 0], nr=[1, 0, 0], ch=0, radius=20)[0]
    aimCtrlGrp = pm.group(name=aimCtrl.name() + '_grp')
    pm.select(cl=1)
    tmp = pm.parentConstraint(ctrl, aimCtrlGrp, mo=0)
    pm.delete(tmp)


def ctrlAimConstraint():
    legsRootCtrl = pm.ls('*Leg*_1_ctrl')
    for ctrl in legsRootCtrl:
        pm.select(cl=1)
        aimposGrp = ctrl.getParent()
        aimCtrl = pm.ls(ctrl.name().replace('ctrl', 'aim_ctrl'))[0]
        pm.aimConstraint(aimCtrl, aimposGrp,
                         mo=1)  # aimConstraint -mo -weight 1 -aimVector 1 0 0 -upVector 0 1 1 -worldUpType "vector" -worldUpVector 0 1 0;


def connectFollow():
    legsRootCtrl = pm.ls('*Leg*_1_ctrl')
    for ctrl in legsRootCtrl:
        pm.select(cl=1)
        aimposGrp = ctrl.getParent()
        aimCnstr = aimposGrp.listRelatives(type='aimConstraint')[0]
        pointCnstr = aimposGrp.listRelatives(type='pointConstraint')[0]

        aimAttr = pm.listAttr(aimCnstr, ud=1)
        ctrl.follow >> aimCnstr.attr(aimAttr[0])
        pointAttr = pm.listAttr(pointCnstr, ud=1)

        reverse = pm.shadingNode('reverse', asUtility=1, name=ctrl.name() + '_follow_rev')
        ctrl.follow >> pointCnstr.attr(pointAttr[0])
        ctrl.follow >> reverse.input.inputX
        reverse.outputX >> pointCnstr.attr(pointAttr[1])


def bdconnectTailScale():
    selection = pm.ls(sl=True)
    if len(selection) == 2:
        source = selection[0]
        target = selection[1]

        source.scaleX >> target.scaleZ
        source.scaleY >> target.scaleY

        return 'MD create'
    else:
        return 'Select source and target !!!'


def bdconnectTailRigScale():
    tailBnd = pm.ls('Tail_?')
    for tail in tailBnd:
        rig = pm.ls(tail.name() + '_RIG')[0]
        rig.scale >> tail.scale


def rigLegLocalLocs():
    localLocs = pm.ls('*Leg*_1_ctrl_local_pos_loc')
    for loc in localLocs:
        ctrl = pm.ls(loc.name().replace('_local_pos_loc', ''))[0]
        jnt = pm.ls(ctrl.name().replace('ctrl', 'RIG'))[0]
        pm.select(cl=1)
        locParent = loc.getParent()
        zeroGrp = pm.group(name=loc.name() + '_ZERO')
        scaleGrp = pm.group(name=loc.name() + '_SCL')

        pm.parent(scaleGrp, locParent)
        tmp = pm.parentConstraint(jnt.getParent(), scaleGrp, mo=0)
        pm.delete(tmp)
        tmp = pm.parentConstraint(ctrl, zeroGrp, mo=0)
        pm.delete(tmp)
        pm.parent(loc, zeroGrp)
        pm.pointConstraint(jnt.getParent(), zeroGrp, mo=1)
        pm.scaleConstraint(jnt.getParent(), scaleGrp, mo=1)


def rigLegWorldLocs():
    localLocs = pm.ls('*Leg*_1_ctrl_world_pos_loc')
    for loc in localLocs:
        aimCtrlGrp = pm.ls(loc.name().replace('_ctrl_world_pos_loc', '_aim_ctrl_grp'))[0]
        jnt = pm.ls(loc.name().replace('ctrl_world_pos_loc', 'RIG'))[0]
        pm.select(cl=1)
        locParent = loc.getParent()
        scaleGrp = pm.group(name=loc.name() + '_SCL')

        pm.parent(scaleGrp, locParent)
        tmp = pm.parentConstraint(jnt.getParent(), scaleGrp, mo=0)
        pm.delete(tmp)

        pm.parent(loc, scaleGrp)
        pm.pointConstraint(loc, aimCtrlGrp, mo=1)
        pm.scaleConstraint(jnt.getParent(), scaleGrp, mo=1)
