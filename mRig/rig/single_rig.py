import pymel.core as pm
import base_rig as rn
reload(rn)

import bdScripts.mRig.utils.libUtils as lu
reload(lu)


class SingleRig(rn.Rig):
    def __init__(self, name, side, bnd, channels):
        super(SingleRig, self).__init__(name, side, bnd)
        self.parent = None
        self.channels = channels

    def rig(self):
        super(SingleRig, self).rig()
        ctrl_name = rn.join_name(self.bnd_joints[0].name(), rn.CTRL)
        ctrl_obj = self.create_ctrl(ctrl_name, 1, 'circle', self.bnd_joints[0], 1, 1)
        ctrl = ctrl_obj.ctrl
        ctrl_grp = ctrl_obj.ctrl_grp
        print ctrl_grp
        hide = set('trs') - set(self.channels)
        for ch in hide:
            if ch == 't':
                ctrl_obj.lock_hide_attr(['translate_XYZ'])
            if ch == 'r':
                ctrl_obj.lock_hide_attr(['rotate_XYZ'])
            if ch == 's':
                ctrl_obj.lock_hide_attr(['scale_XYZ'])
        ctrl_obj.lock_hide_attr(['visibility'])
        self.fk_ctrls.append(ctrl)
        print ctrl_grp, self.fk_ctrls
        pm.parent(ctrl_grp, self.controllers_grp)
        pm.parentConstraint(ctrl, self.rig_joints[0])
        pm.parentConstraint(self.rig_joints[0], self.bnd_joints[0])

