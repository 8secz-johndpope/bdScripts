import pymel.core as pm

from ..utils import libCtrl as ctrl
reload(ctrl)

import bdScripts.mRig.utils.libUtils as utils
reload(utils)

from bdScripts.mRig.utils.libUtils import (set_bnd, join_name)


BND = 'bnd'
FK = 'fk'
IK = 'ik'
DRV = 'drv'
RIG = 'anim'
CTRL = 'ctrl'
CTRLGRP = 'ctrl_grp'
MAINGRP = 'rig_grp'
GRP = 'grp'

class Rig(object):
    def __init__(self, name='', side='', bnd=None):
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

        # -----------------------------

    def rig(self):
        self.rig_joints = self.create_chain(RIG, bnd=1)
        self.create_groups()

    def create_chain(self, prefix, bnd=0):
        chain = []
        dup_chain = self.rig_joints
        if bnd:
            dup_chain = self.bnd_joints
        print dup_chain
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
        self.rig_grp = pm.group(name=join_name([self.name, MAINGRP]))
        pm.select(cl=1)
        self.fk_ctrl_grp = pm.group(name=join_name([self.name, FK, GRP]))
        pm.select(cl=1)
        self.ik_ctrl_grp = pm.group(name=join_name([self.name, IK, GRP]))
        pm.select(cl=1)
        self.controllers_grp = pm.group(name=join_name([self.name, CTRL, GRP]))

        pm.parent([self.ik_ctrl_grp, self.fk_ctrl_grp], self.controllers_grp)


