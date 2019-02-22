import pymel.core as pm
import base_rig as rn
reload(rn)

import bdScripts.mRig.utils.libUtils as lu
reload(lu)

from bdScripts.mRig.utils.libUtils import (get_pv_pos)


class ArmRig(rn.Rig):
    def __init__(self, side, bnd, clav):
        super(ArmRig, self).__init__('Arm', side, bnd)
        self.parent = None
        self.clav = pm.ls(self.side + clav)[0]

    def rig(self):
        super(ArmRig, self).rig()
        self.rig_fk()
        self.rig_ik()
        self.connect_chains()
        self.connect_to_clav()

    def rig_fk(self):
        self.fk_joints = self.create_chain(rn.FK)
        pm.parent(self.fk_joints[0], self.rig_grp)
        self.create_chain_ctrls(rn.FK)

        for i in range(len(self.fk_ctrls)):
            pm.parentConstraint(self.fk_ctrls[i], self.fk_joints[i], mo=0)

    def rig_ik(self):
        self.ik_joints = self.create_chain(rn.IK)
        self.create_chain_ctrls(rn.IK)

        extra_jnt = pm.duplicate(self.ik_joints[-1])[0]
        extra_jnt.rename(self.ik_joints[-1].name() + '_palm')
        pm.parent(extra_jnt, self.ik_joints[-1])
        extra_jnt.translateX.set(4)
        self.ik_joints.append(extra_jnt)

        pm.parent(self.ik_joints[0], self.rig_grp)

        # Create Iks
        arm_ik = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=self.ik_joints[0],
                             endEffector=self.ik_joints[2], name=self.side + '_arm_ikHandle')[0]
        hand_ik = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=self.ik_joints[2],
                              endEffector=self.ik_joints[3], name=self.side + '_palm_ikHandle')[0]

        pm.select(cl=1)
        iks_grp = pm.group(n=self.side + '_arm_ikHandles_grp')
        print iks_grp
        iks_grp.visibility.set(0)
        wrist_pos = self.ik_joints[2].getTranslation(space='world')
        iks_grp.setPivots(wrist_pos)
        pm.parent([arm_ik, hand_ik], iks_grp)

        pm.poleVectorConstraint(self.ik_ctrls[1], arm_ik)
        pm.parent(iks_grp, self.ik_ctrls[0])


    def create_chain_ctrls(self, chain):
        if chain == rn.FK:
            prev_ctrl = None
            i = 0
            for jnt in self.bnd_joints:
                ctrl_name = rn.join_name(jnt.name(), rn.FK, rn.CTRL)
                fk_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'circle', jnt, 1, 1)
                fk_ctrl = fk_ctrl_obj.ctrl
                fk_ctrl_grp = fk_ctrl_obj.ctrl_grp
                fk_ctrl_obj.lock_hide_attr(['translate_XYZ', 'scale_XYZ', 'visibility'])
                self.fk_ctrls.append(fk_ctrl)
                if i == 0:
                    pm.parent(fk_ctrl_grp, self.fk_ctrl_grp)
                elif i >= 1:
                    pm.parent(fk_ctrl_grp, prev_ctrl)
                prev_ctrl = fk_ctrl
                i += 1

        if chain == rn.IK:
            # Create IK ctrl
            ik_jnt = self.bnd_joints[-1]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 1)
            pm.parent(ik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            ik_ctrl_obj.lock_hide_attr(['scale_XYZ', 'visibility'])

            # Create IKFK switch ctrl
            ctrl_name = rn.join_name((self.side + 'Arm'), 'ikfk', rn.CTRL)
            fkik_ctrl_obj= self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 1)
            pm.parent(fkik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ikfk_ctrl = fkik_ctrl_obj.ctrl
            pm.parent(fkik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            fkik_ctrl_obj.add_float_attr('ikfk', 0, 1)
            fkik_ctrl_obj.offset_ctrl_grp([10 * self.side_sign, 0, 0])
            fkik_ctrl_obj.lock_hide_attr(['translate_XYZ', 'rotate_XYZ', 'scale_XYZ', 'visibility'])

            # Create ik pole vector ctrl
            ik_jnt = self.bnd_joints[1]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 0)
            pm.parent(ik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            pv_pos = get_pv_pos(self.ik_joints[0], self.ik_joints[1], self.ik_joints[2], 10)
            ik_ctrl_obj.ctrl_grp.setTranslation(pv_pos, space='world')
            ik_ctrl_obj.lock_hide_attr(['rotate_XYZ', 'scale_XYZ', 'visibility'])

    @staticmethod
    def create_locator(destination, name):
        loc = pm.spaceLocator(n=name)
        pos = destination.getTranslation(space='world')
        loc.setTranslation(pos, space='world')
        return loc

    def connect_to_clav(self):
        pm.parentConstraint(self.clav, self.ik_joints[0], mo=1)
        pm.parentConstraint(self.clav, self.fk_ctrl_grp, mo=1)

