import pymel.core as pm

from ..utils import libCtrl as libCtrl
reload(libCtrl)

import bdScripts.mRig.utils.libUtils as utils
reload(utils)

from bdScripts.mRig.utils.libUtils import (set_bnd, join_name, create_blend)


BND = 'bnd'
FK = 'fk'
IK = 'ik'
DRV = 'drv'
RIG = 'rig'
CTRL = 'ctrl'
CTRLGRP = 'ctrl_grp'
MAINGRP = 'rig_grp'
GRP = 'grp'

class Rig(object):
    def __init__(self, name, side, bnd=None):
        self.name = name

        self.rig_grp = None
        self.controllers_grp = None
        self.fk_ctrl_grp = None
        self.ik_ctrl_grp = None

        self.side = side
        self.mirrored = 0

        self.bnd_joints = set_bnd(bnd)
        self.rig_joints = []
        self.fk_joints = []
        self.ik_joints = []
        self.rbn_joints = []

        self.ik_ctrls = []
        self.fk_ctrls = []
        self.ikfk_ctrl = None

        # -----------------------------

    def rig(self):
        self.rig_joints = self.create_chain(RIG, bnd=1)
        self.create_groups()
        pm.parent(self.rig_joints[0], self.rig_grp)



    def create_chain(self, prefix, bnd=0):
        chain = []
        dup_chain = self.rig_joints
        if bnd:
            dup_chain = self.bnd_joints

        for jnt in dup_chain:
            if bnd:
                new_jnt = pm.duplicate(jnt, name=RIG + '_' + jnt.name(), po=1)[0]
            else:
                new_jnt = pm.duplicate(jnt, name=jnt.name().replace(RIG, prefix), po=1)[0]
            chain.append(new_jnt)

        for i in range(len(chain)-1, 0, -1):
            pm.parent(chain[i], chain[i-1])

        return chain

    def create_groups(self):
        pm.select(cl=1)
        self.rig_grp = pm.group(name=join_name(self.name, MAINGRP))
        pm.select(cl=1)
        self.fk_ctrl_grp = pm.group(name=join_name(self.name, FK, GRP))
        pm.select(cl=1)
        self.ik_ctrl_grp = pm.group(name=join_name(self.name, IK, GRP))
        pm.select(cl=1)
        self.controllers_grp = pm.group(name=join_name(self.name, CTRL, GRP))

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



