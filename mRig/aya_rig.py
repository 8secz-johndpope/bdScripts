import pymel.core as pm
import bdScripts.mRig.rig.mchar as char
reload(char)
import bdScripts.mRig.rig.leg_rig as lr
reload(lr)
import bdScripts.mRig.rig.arm_rig as ar
reload(ar)
import bdScripts.mRig.utils.shape_io as sio
reload(sio)

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


def save_shapes():
    ctrls = [attr.node() for attr in pm.ls("*.anim_ctrl")]
    for ctrl in ctrls:
        ctrl_out = sio.ShapeIO(ctrl)
        ctrl_out.save_shape()

def load_shapes():
    ctrls = [attr.node() for attr in pm.ls("*.anim_ctrl")]
    for ctrl in ctrls:
        ctrl_in = sio.ShapeIO(ctrl)
        ctrl_in.import_shape()
