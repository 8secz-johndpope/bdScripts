import pymel.core as pm
import base_rig as rn
reload(rn)


class LegRig(rn.Rig):
    def __init__(self, side, bnd):
        super(LegRig, self).__init__('Leg', side, bnd)
        self.parent = None

    def rig(self):
        super(LegRig, self).rig()
        self.rig_fk()
        self.rig_ik()
        self.connect_chains()

    def rig_fk(self):
        self.fk_joints = self.create_chain(rn.FK)
        self.create_chain_ctrls(rn.FK)
        print self.fk_joints, self.fk_ctrls
        for i in range(len(self.fk_ctrls)):
            pm.parentConstraint(self.fk_ctrls[i], self.fk_joints[i], mo=0)

    def rig_ik(self):
        self.ik_joints = self.create_chain(rn.IK)
        self.create_chain_ctrls(rn.IK)

    def create_chain_ctrls(self, chain):
        if chain == rn.FK:
            prev_ctrl = None
            i = 0
            for jnt in self.bnd_joints[:-1]:
                ctrl_name = rn.join_name(jnt.name(), rn.FK, rn.CTRL)
                fk_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'circle', jnt, 1, 1)
                fk_ctrl = fk_ctrl_obj.ctrl
                fk_ctrl_grp = fk_ctrl_obj.ctrl_grp
                fk_ctrl_obj.lock_hide_attr(['rotate_XYZ', 'scale_XYZ', 'visibility'])
                self.fk_ctrls.append(fk_ctrl)
                if i >= 1:
                    pm.parent(fk_ctrl_grp, prev_ctrl)
                prev_ctrl = fk_ctrl
                i += 1

        if chain == rn.IK:
            ik_jnt = self.bnd_joints[-3]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 0)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            ik_ctrl_obj.lock_hide_attr(['scale_XYZ', 'visibility'])

            fkik_ctrl_obj= self.create_ctrl(self.side + '_ikfk_' + rn.CTRL, 1, 'box', ik_jnt, 1, 0)
            self.ikfk_ctrl = fkik_ctrl_obj.ctrl
            fkik_ctrl_obj.add_float_attr('ikfk', 0, 1)
            fkik_ctrl_obj.offset_ctrl_grp([10, 0, 0])
            fkik_ctrl_obj.lock_hide_attr(['translate_XYZ', 'rotate_XYZ', 'scale_XYZ', 'visibility'])

            ik_jnt = self.bnd_joints[1]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 0)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            ik_ctrl_obj.offset_ctrl_grp([0, 0, 10])
            ik_ctrl_obj.lock_hide_attr(['rotate_XYZ', 'scale_XYZ', 'visibility'])
