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
        pm.parent(self.fk_joints[0], self.rig_grp)
        self.create_chain_ctrls(rn.FK)

        for i in range(len(self.fk_ctrls)):
            pm.parentConstraint(self.fk_ctrls[i], self.fk_joints[i], mo=0)

    def rig_ik(self):
        self.ik_joints = self.create_chain(rn.IK)
        pm.parent(self.ik_joints[0], self.rig_grp)
        self.create_chain_ctrls(rn.IK)

        foot_ik = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=self.ik_joints[0],
                              endEffector=self.ik_joints[2], name=self.side + '_foot_ikHandle')[0]
        foot_ik.visibility.set(0)

        ball_ik = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=self.ik_joints[2],
                              endEffector=self.ik_joints[3], name=self.side + '_ball_ikHandle')[0]
        ball_ik.visibility.set(0)

        toe_ik = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=self.ik_joints[3],
                             endEffector=self.ik_joints[4], name=self.side + '_toe_ikHandle')[0]
        toe_ik.visibility.set(0)



        ankle_loc = self.create_locator(self.ik_joints[2], self.side + '_ankle_loc')
        foot_loc = self.create_locator(self.ik_joints[2], self.side + '_foot_loc')
        ball_loc = self.create_locator(self.ik_joints[3], self.side + '_ball_loc')
        ball_twist_loc = self.create_locator(self.ik_joints[3], self.side + '_ball_twist_loc')
        toe_loc = self.create_locator(self.ik_joints[4], self.side + '_toe_loc')
        toe_bend_loc = self.create_locator(self.ik_joints[3], self.side + '_toe_bend_loc')

        foot_helpers = pm.ls(self.side + '*_helper', type='transform')
        inner_loc = outer_loc = heel_loc = ''
        for helper in foot_helpers:
            if 'inner' in helper.name():
                inner_loc = self.create_locator(helper, self.side + '_inner_bank_loc')
            elif 'outer' in helper.name():
                outer_loc = self.create_locator(helper, self.side + '_outer_bank_loc')
            elif 'heel' in helper.name():
                heel_loc = self.create_locator(helper, self.side + '_heel_loc')

        pm.parent(foot_ik, foot_loc)
        pm.parent(ball_ik, ball_loc)
        pm.parent(toe_ik, toe_bend_loc)
        pm.parent(toe_bend_loc, toe_loc)

        pm.parent(foot_loc, ball_loc)
        pm.parent(ball_loc, toe_loc)
        pm.parent(toe_loc, ball_twist_loc)
        pm.parent(ball_twist_loc, inner_loc)
        pm.parent(inner_loc, outer_loc)
        pm.parent(outer_loc, heel_loc)
        pm.parent(heel_loc, ankle_loc)

    def create_chain_ctrls(self, chain):
        if chain == rn.FK:
            prev_ctrl = None
            i = 0
            for jnt in self.bnd_joints[:-1]:
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
            # Create IK foot ctrl
            ik_jnt = self.bnd_joints[-3]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 0)
            pm.parent(ik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            ik_ctrl_obj.lock_hide_attr(['scale_XYZ', 'visibility'])

            # Create IKFK switch foot ctrl
            fkik_ctrl_obj= self.create_ctrl(self.side + '_ikfk_' + rn.CTRL, 1, 'box', ik_jnt, 1, 0)
            pm.parent(fkik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ikfk_ctrl = fkik_ctrl_obj.ctrl
            pm.parent(fkik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            fkik_ctrl_obj.add_float_attr('ikfk', 0, 1)
            fkik_ctrl_obj.offset_ctrl_grp([10, 0, 0])
            fkik_ctrl_obj.lock_hide_attr(['translate_XYZ', 'rotate_XYZ', 'scale_XYZ', 'visibility'])

            # Create ik pole vector ctrl
            ik_jnt = self.bnd_joints[1]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 0)
            pm.parent(ik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            ik_ctrl_obj.offset_ctrl_grp([0, 0, 10])
            ik_ctrl_obj.lock_hide_attr(['rotate_XYZ', 'scale_XYZ', 'visibility'])

    @staticmethod
    def create_locator(destination, name):
        loc = pm.spaceLocator(n=name)
        pos = destination.getTranslation(space='world')
        loc.setTranslation(pos, space='world')
        return loc
