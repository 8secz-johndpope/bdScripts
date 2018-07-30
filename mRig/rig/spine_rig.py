import pymel.core as pm

from ..utils import libCtrl as libCtrl
reload(libCtrl)

import base_rig as base
reload(base)

import bdScripts.mRig.utils.libUtils as utils
reload(utils)
from bdScripts.mRig.utils.libUtils import (set_bnd, join_name)

# ------- Global suffixes ------
BND = base.BND
FK = base.FK
IK = base.IK
DRV = base.DRV
RIG = base.RIG
CTRL = base.CTRL
CTRLGRP = base.CTRLGRP
MAINGRP = base.MAINGRP
# ------------------------------

class SpineRig(base.Rig):
    def __init__(self, name = '', side='', bnd=None):
        super(SpineRig, self).__init__(name=name, side=side, bnd=bnd)
        self.hip = None
        self.ik_handle = None
        self.ik_crv = None
        self.clusters = []
        self.ikFkSwitchCtrl = None
    # -----------------------------

    def rig(self):
        super(SpineRig, self).rig()
        # self.rig_fk()
        self.rig_ik()
        # self.connect()

    def set_hip(self, hip):
        find = pm.ls(hip)
        if find:
            self.hip = find[0]

    def rig_ik(self):
        self.ik_joints = self.create_chain(IK)
        last_jnt_name = self.ik_joints[-1].name()
        new_name = last_jnt_name + '_end'
        self.ik_joints[-1].rename(new_name)

        self.create_ik_spline()
        self.create_ik_ctrl()
        self.create_clusters()

    def create_ik_spline(self):
        points = []
        for jnt in self.rig_joints:
            pos = jnt.getTranslation(space='world')
            points.append(pos)

        self.ik_crv = pm.curve(n='spine_ikSpline_crv', d=1, p=points)

        self.ik_handle= pm.ikHandle(sj=self.ik_joints[0], ee=self.ik_joints[-1], c=self.ik_crv, ccv=False,
                                         sol='ikSplineSolver', name='spine_ikSpline')[0]

        pm.parent(self.ik_crv, self.rig_grp)
        pm.parent(self.ik_handle, self.rig_grp)

    def create_ik_ctrl(self):
        for i, jnt in enumerate(self.rig_joints):
            ctrl_node = libCtrl.Controller(name='spine_' + str(i+1) + '_ik_ctrl', target=jnt, scale = 20)
            ctrl, ctrl_grp = ctrl_node.create()
            self.ik_ctrls.append(ctrl)
            pm.parent(ctrl_grp, self.ik_ctrl_grp)

    def create_clusters(self):
        crv_shape = self.ik_crv.getShape()
        for i in range(crv_shape.numCVs()):
            cluster = pm.cluster(crv_shape.cv[i])
            name = join_name([self.ik_crv.name(), 'cls', str(i)])
            cluster[1].rename(name)
            cluster[1].attr('v').set(0)
            self.clusters.append(cluster[1])
            pm.parent(cluster[1], self.ik_ctrls[i])

