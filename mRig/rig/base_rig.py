import pymel.core as pm

from ..utils import libCtrl as libCtrl
reload(libCtrl)

import bdScripts.mRig.utils.libUtils as utils
reload(utils)

from bdScripts.mRig.utils.libUtils import (join_name, create_blend)


BND = 'bnd'
FK = 'fk'
IK = 'ik'
DRV = 'drv'
RIG = 'rig'
CTRL = 'ctrl'
CTRLGRP = 'ctrl_all_grp'
MAINGRP = 'rig_grp'
GRP = 'grp'

class Rig(object):
    def __init__(self, name, side, bnd=[]):
        self.name = name

        self.rig_grp = None
        self.controllers_grp = None
        self.fk_ctrl_grp = None
        self.ik_ctrl_grp = None

        self.side = side[0]
        self.side_sign = side[1]
        self.mirrored = 0

        self.bnd_joints = self.set_bnd(bnd)
        self.rig_joints = []
        self.fk_joints = []
        self.ik_joints = []
        self.rbn_joints = []

        self.ctrl_obj = []
        self.ik_ctrls = []
        self.fk_ctrls = []
        self.ikfk_ctrl = None
        self.parent = None

        # -----------------------------

    def rig(self):
        self.rig_joints = self.create_chain(RIG)
        self.create_groups()
        pm.parent(self.rig_joints[0], self.rig_grp)

    def create_chain(self, prefix):
        chain = []
        dup_chain = self.rig_joints
        if prefix == RIG:
            dup_chain = self.bnd_joints

        for jnt in dup_chain:
            if prefix == RIG:
                new_jnt = pm.duplicate(jnt, name=RIG + '_' + jnt.name(), po=1)[0]
            else:
                new_jnt = pm.duplicate(jnt, name=jnt.name().replace(RIG, prefix), po=1)[0]
            chain.append(new_jnt)

        for i in range(len(chain)-1, 0, -1):
            pm.parent(chain[i], chain[i-1])

        return chain

    def create_groups(self):
        pm.select(cl=1)
        self.rig_grp = pm.group(name=join_name(self.side + self.name, MAINGRP))
        pm.select(cl=1)
        self.fk_ctrl_grp = pm.group(name=join_name(self.side + self.name, FK, GRP))
        pm.select(cl=1)
        self.ik_ctrl_grp = pm.group(name=join_name(self.side + self.name, IK, GRP))
        pm.select(cl=1)
        self.controllers_grp = pm.group(name=join_name(self.side + self.name, CTRLGRP))

        pm.parent([self.ik_ctrl_grp, self.fk_ctrl_grp], self.controllers_grp)

    @staticmethod
    def create_ctrl(name, scale, visual, target, pos, rot):
        ctrl_obj = libCtrl.Controller(name=name, scale=scale, visual=visual, target=target)
        ctrl_obj.create()
        if pos:
            ctrl_obj.match_position()
        if rot:
            ctrl_obj.match_rotation()
        if pos and rot:
            ctrl_obj.match_all()

        return ctrl_obj

    def connect_chains(self):
        for jnt in self.rig_joints:
            fk_jnt = pm.ls(jnt.name().replace(RIG, FK))[0]
            ik_jnt = pm.ls(jnt.name().replace(RIG, IK))[0]
            create_blend(jnt, fk_jnt, ik_jnt, self.ikfk_ctrl, 'ikfk')
            bnd_jnt = pm.ls(jnt.name().replace(RIG + '_', ''))[0]
            pm.parentConstraint(jnt, bnd_jnt)

    def set_bnd(self, bnd):
        temp = []
        for jnt in bnd:
            if self.side != '':
                find = pm.ls(jnt.replace('_SIDE_', self.side))
            else:
                find = pm.ls(jnt)
            if find:
                temp.append(find[0])
            else:
                pm.warning('Bind joint {} not found'.format(jnt))
                return None

        return temp[:]

    def create_ikfk_ctrl(self, attach_to, offset):
        # Create IKFK switch ctrl
        ctrl_name = join_name(attach_to.name(), 'ikfk', CTRL)
        fkik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', attach_to, 1, 1)
        pm.parent(fkik_ctrl_obj.ctrl_grp, self.ik_ctrl_grp)
        self.ikfk_ctrl = fkik_ctrl_obj.ctrl
        pm.parent(fkik_ctrl_obj.ctrl_grp, self.controllers_grp)
        fkik_ctrl_obj.add_float_attr('ikfk', 0, 1)
        fkik_ctrl_obj.offset_ctrl_grp(offset)
        fkik_ctrl_obj.lock_hide_attr(['translate_XYZ', 'rotate_XYZ', 'scale_XYZ', 'visibility'])

    def set_parent(self, parent, ctrl_parent):
        self.parent = parent
        pm.parent(self.controllers_grp, ctrl_parent)

