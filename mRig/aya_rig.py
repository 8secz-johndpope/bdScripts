import bdScripts.mRig.rig.mchar as char
reload(char)
import bdScripts.mRig.rig.leg_rig as lr
reload(lr)
import bdScripts.mRig.rig.arm_rig as ar
reload(ar)


def rig():
    aya_char = char.Character(name='Aya', root='Root')
    aya_char.create()

    # Create arms rig
    bind_jnt = ['Arm', 'ForeArm', 'Hand']
    clavicle = 'Shoulder'

    left_arm_rig = ar.ArmRig(side=['Left', 1], bnd=bind_jnt, clav=clavicle)
    left_arm_rig.rig()

    right_arm_rig = ar.ArmRig(side=['Right', 1], bnd=bind_jnt, clav=clavicle)
    right_arm_rig.rig()

    aya_char.add_rig(left_arm_rig)
    aya_char.add_rig(right_arm_rig)
    # Create legs rig
    bind_jnt = ['UpLeg', 'Leg', 'Foot', 'ToeBase', 'ToeBaseEnd']
    hips = 'Hips'

    left_leg_rig = lr.LegRig(side=['Left', 1], bnd=bind_jnt, hips=hips)
    left_leg_rig.rig()

    right_leg_rig = lr.LegRig(side=['Right', -1], bnd=bind_jnt, hips=hips)
    right_leg_rig.rig()

    aya_char.add_rig(left_leg_rig)
    aya_char.add_rig(right_leg_rig)
