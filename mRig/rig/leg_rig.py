import pymel.core as pm
import base_rig as rn
reload(rn)

import bdScripts.mRig.utils.libUtils as lu
reload(lu)
from bdScripts.mRig.utils.libUtils import (get_pv_pos)


class LegRig(rn.Rig):
    def __init__(self, side, bnd, hips):
        super(LegRig, self).__init__('Leg', side, bnd)
        self.parent = None
        self.hips = pm.ls(hips)[0]

    def rig(self):
        super(LegRig, self).rig()
        self.rig_fk()
        self.rig_ik()
        self.connect_chains()
        self.connect_to_hips()

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

        # Create Iks
        foot_ik = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=self.ik_joints[0],
                              endEffector=self.ik_joints[2], name=self.side + '_foot_ikHandle')[0]
        foot_ik.visibility.set(0)

        ball_ik = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=self.ik_joints[2],
                              endEffector=self.ik_joints[3], name=self.side + '_ball_ikHandle')[0]
        ball_ik.visibility.set(0)

        toe_ik = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=self.ik_joints[3],
                             endEffector=self.ik_joints[4], name=self.side + '_toe_ikHandle')[0]
        toe_ik.visibility.set(0)

        # Create the poll vector
        pm.poleVectorConstraint(self.ik_ctrls[1], foot_ik)
        # Create the pivot locators
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

        # Create the hierarchy
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
        #
        auto_roll_attr = ['roll', 'toe_start', 'ball_straight']
        foot_attr = ['heel_twist', 'ball_twist', 'tip_twist', 'bank', 'toe_bend']
        roll_attr = ['heel_roll', 'ball_roll', 'tip_roll']

        pm.addAttr(self.ik_ctrls[0], ln='auto_foot_roll', nn='--------', at='enum', en="Auto Foot Roll")
        self.ik_ctrls[0].attr('auto_foot_roll').setKeyable(True)
        self.ik_ctrls[0].attr('auto_foot_roll').setLocked(True)

        pm.addAttr(self.ik_ctrls[0], ln='Enabled', nn='Enabled', at='long')
        self.ik_ctrls[0].attr('Enabled').setKeyable(True)
        self.ik_ctrls[0].attr('Enabled').setMin(0)
        self.ik_ctrls[0].attr('Enabled').setMax(1)
        self.ik_ctrls[0].attr('Enabled').set(1)

        for attr in auto_roll_attr:
            pm.addAttr(self.ik_ctrls[0], ln=attr, nn=attr, at='float')
            self.ik_ctrls[0].attr(attr).setKeyable(True)

        pm.addAttr(self.ik_ctrls[0], ln='foot_roll', nn='--------', at='enum', en="Foot Roll")
        self.ik_ctrls[0].attr('foot_roll').setKeyable(True)
        self.ik_ctrls[0].attr('foot_roll').setLocked(True)

        for attr in roll_attr:
            pm.addAttr(self.ik_ctrls[0], ln=attr, nn=attr, at='float')
            self.ik_ctrls[0].attr(attr).setKeyable(True)

        pm.addAttr(self.ik_ctrls[0], ln='foot_attr', nn='--------', at='enum', en="Foot Attr")
        self.ik_ctrls[0].attr('foot_attr').setKeyable(True)
        self.ik_ctrls[0].attr('foot_attr').setLocked(True)

        for attr in foot_attr:
            pm.addAttr(self.ik_ctrls[0], ln=attr, nn=attr, at='float')
            self.ik_ctrls[0].attr(attr).setKeyable(True)

        self.ik_ctrls[0].attr('toe_start').set(40)
        self.ik_ctrls[0].attr('ball_straight').set(80)
        self.rig_reverse_foot(self.ik_ctrls[0], heel_loc, ball_loc, toe_loc)
        #
        # # connect the attributes
        self.ik_ctrls[0].attr('heel_twist').connect(heel_loc.rotateY)
        self.ik_ctrls[0].attr('ball_twist').connect(ball_twist_loc.rotateY)
        self.ik_ctrls[0].attr('tip_twist').connect(toe_loc.rotateY)
        self.ik_ctrls[0].attr('toe_bend').connect(toe_bend_loc.rotateX)
        #
        self.rig_bank(self.ik_ctrls[0], inner_loc, outer_loc)
        #
        pm.parent(ankle_loc, self.ik_ctrls[0])

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
            fkik_ctrl_obj.offset_ctrl_grp([10 * self.side_sign, 0, 0])
            fkik_ctrl_obj.lock_hide_attr(['translate_XYZ', 'rotate_XYZ', 'scale_XYZ', 'visibility'])

            # Create ik pole vector ctrl
            ik_jnt = self.bnd_joints[1]
            ctrl_name = rn.join_name(ik_jnt.name(), rn.IK, rn.CTRL)
            ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', ik_jnt, 1, 0)
            pm.parent(ik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
            self.ik_ctrls.append(ik_ctrl_obj.ctrl)
            pv_pos = get_pv_pos(self.ik_joints[0], self.ik_joints[1], self.ik_joints[2], 15)
            ik_ctrl_obj.ctrl_grp.setTranslation(pv_pos, space='world')
            # ik_ctrl_obj.offset_ctrl_grp([0, 0, 10])
            ik_ctrl_obj.lock_hide_attr(['rotate_XYZ', 'scale_XYZ', 'visibility'])

    @staticmethod
    def create_locator(destination, name):
        loc = pm.spaceLocator(n=name)
        pos = destination.getTranslation(space='world')
        loc.setTranslation(pos, space='world')
        return loc

    @staticmethod
    def rig_reverse_foot(ik_ctrl, heel_loc, ball_loc, toe_loc):
        '''
        Reverse foot setup
        :param self:
        :param ik_ctrl:
        :param heel_loc:
        :param ball_loc:
        :param toe_loc:
        :return:
        '''
        heel_bc = pm.createNode('blendColors', name=heel_loc.name().replace('loc', 'auto_bc'))
        ball_bc = pm.createNode('blendColors', name=ball_loc.name().replace('loc', 'auto_bc'))
        toe_bc = pm.createNode('blendColors', name=toe_loc.name().replace('loc', 'auto_bc'))

        ik_ctrl.attr('Enabled').connect(heel_bc.blender)
        ik_ctrl.attr('Enabled').connect(ball_bc.blender)
        ik_ctrl.attr('Enabled').connect(toe_bc.blender)

        ik_ctrl.attr('heel_roll').connect(heel_bc.color2R)
        ik_ctrl.attr('ball_roll').connect(ball_bc.color2R)
        ik_ctrl.attr('tip_roll').connect(toe_bc.color2R)

        # setup auto part
        heel_clamp = pm.createNode('clamp', n=heel_loc.name().replace('loc', 'roll_cl'))
        heel_clamp.minR.set(-90)

        toe_sr = pm.createNode('setRange', n=toe_loc.name().replace('loc', 'linestep_sr'))
        toe_sr.minX.set(0)
        toe_sr.maxX.set(1)

        ball_sr = pm.createNode('setRange', n=ball_loc.name().replace('loc', 'linestep_sr'))
        ball_sr.minX.set(0)
        ball_sr.maxX.set(1)
        ball_sr.oldMinX.set(0)

        toe_roll_md = pm.createNode('multiplyDivide', n=toe_loc.name().replace('loc', 'roll_md'))
        ball_roll_md = pm.createNode('multiplyDivide', n=ball_loc.name().replace('loc', 'roll_md'))

        ball_range_md = pm.createNode('multiplyDivide', n=ball_loc.name().replace('loc', 'roll_range_md'))

        ball_range_pma = pm.createNode('plusMinusAverage', n=ball_loc.name().replace('loc', 'range_pma'))
        ball_range_pma.input1D[0].set(1)
        ball_range_pma.operation.set(2)

        # connect the heel for negative rolls
        ik_ctrl.attr('roll').connect(heel_clamp.inputR)
        heel_clamp.outputR.connect(heel_bc.color1R)
        heel_bc.outputR.connect(heel_loc.rotateX)

        # connect the toe
        ik_ctrl.attr('roll').connect(toe_sr.valueX)
        ik_ctrl.attr('ball_straight').connect(toe_sr.oldMaxX)
        ik_ctrl.attr('toe_start').connect(toe_sr.oldMinX)

        ik_ctrl.attr('roll').connect(toe_roll_md.input2X)
        toe_sr.outValueX.connect(toe_roll_md.input1X)

        toe_roll_md.outputX.connect(toe_bc.color1R)
        toe_bc.outputR.connect(toe_loc.rotateX)

        # connect the ball
        ik_ctrl.attr('roll').connect(ball_sr.valueX)
        ik_ctrl.attr('toe_start').connect(ball_sr.oldMaxX)

        toe_sr.outValueX.connect(ball_range_pma.input1D[1])

        ball_sr.outValueX.connect(ball_range_md.input1X)
        ball_range_pma.output1D.connect(ball_range_md.input2X)

        ik_ctrl.attr('roll').connect(ball_roll_md.input2X)
        ball_range_md.outputX.connect(ball_roll_md.input1X)

        ball_roll_md.outputX.connect(ball_bc.color1R)
        ball_bc.outputR.connect(ball_loc.rotateX)

    def rig_bank(self, ik_ctrl, inner_loc, outer_loc):
        inner_cl = pm.createNode('clamp', n=inner_loc.name().replace('loc', 'cl'))
        inner_reverse_mdl = pm.createNode('multDoubleLinear', n=inner_loc.name().replace('loc', 'mdl'))
        inner_reverse_mdl.input2.set(self.side_sign)
        if self.side_sign:
            inner_cl.maxR.set(90)
        else:
            inner_cl.minR.set(-90)

        outer_cl = pm.createNode('clamp', n=outer_loc.name().replace('loc', 'cl'))
        outer_reverse_mdl = pm.createNode('multDoubleLinear', n=outer_loc.name().replace('loc', 'mdl'))
        outer_reverse_mdl.input2.set(self.side_sign)
        if self.side_sign:
            outer_cl.minR.set(-90)
        else:
            outer_cl.maxR.set(90)

        ik_ctrl.attr('bank').connect(inner_cl.inputR)
        inner_cl.outputR.connect(inner_reverse_mdl.input1)
        inner_reverse_mdl.output.connect(inner_loc.rotateZ)
        # inner_cl.outputR.connect(inner_loc.rotateZ)

        ik_ctrl.attr('bank').connect(outer_cl.inputR)
        outer_cl.outputR.connect(outer_reverse_mdl.input1)
        outer_reverse_mdl.output.connect(outer_loc.rotateZ)
        # outer_cl.outputR.connect(outer_loc.rotateZ)

    def connect_to_hips(self):
        pm.parentConstraint(self.hips, self.ik_joints[0], mo=1)
        pm.parentConstraint(self.hips, self.fk_ctrl_grp, mo=1)

