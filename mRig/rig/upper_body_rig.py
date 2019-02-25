import pymel.core as pm
import base_rig as rn
reload(rn)

import bdScripts.mRig.utils.libUtils as lu
reload(lu)


class UpperBodyRig(rn.Rig):
    def __init__(self, name, side, bnd):
        super(UpperBodyRig, self).__init__(name, side, bnd)
        self.parent = None
        self.hips_ctrl = None
        self.upper_body_ctrl = None

    def rig(self):
        super(UpperBodyRig, self).rig()
        self.create_controllers()

    def create_controllers(self):
        # create the hips ctrl
        ctrl_name = rn.join_name(self.bnd_joints[0].name(), rn.CTRL)
        ctrl_obj = self.create_ctrl(ctrl_name, 1, 'circle', self.bnd_joints[0], 1, 1)
        self.hips_ctrl = ctrl_obj.ctrl
        hips_ctrl_grp = ctrl_obj.ctrl_grp
        ctrl_obj.lock_hide_attr(['translate_XYZ', 'scale_XYZ', 'visibility'])

        pm.parentConstraint(self.hips_ctrl, self.rig_joints[0])
        pm.parentConstraint(self.rig_joints[0], self.bnd_joints[0])

        # create the upper body ctrl
        ctrl_name = rn.join_name('UpperBody', rn.CTRL)
        ctrl_obj = self.create_ctrl(ctrl_name, 15, 'box', self.bnd_joints[0], 1, 0)
        self.upper_body_ctrl = ctrl_obj.ctrl
        ctrl_grp = ctrl_obj.ctrl_grp
        ctrl_obj.lock_hide_attr(['scale_XYZ', 'visibility'])
        pm.parent(ctrl_grp, self.controllers_grp)
        pm.parent(hips_ctrl_grp, self.upper_body_ctrl)
