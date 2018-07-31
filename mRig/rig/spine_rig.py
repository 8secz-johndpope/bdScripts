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
        self.ik_drv_crv = None
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
        mid = int(len(self.rig_joints)/2)
        end = len(self.rig_joints) - 1
        for i in [0, mid, end]:
            ctrl_node = libCtrl.Controller(name='spine_' + str(i+1) + '_ik_ctrl', target=self.rig_joints[i], look='box')
            ctrl, ctrl_grp = ctrl_node.create()
            if i == mid:
                ctrl_node.resize([5, 0.5, 5])
            else:
                ctrl_node.resize([6, 1, 6])
            self.ik_ctrls.append(ctrl)
            pm.parent(ctrl_grp, self.ik_ctrl_grp)

    def create_clusters(self):

        self.ik_drv_crv = pm.rebuildCurve(self.ik_crv, ch=1, rpo=0, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=2, d=3,
                                          tol=0.01, name = self.ik_crv.name().replace('crv', 'drv_crv'))[0]
        pm.delete(self.ik_drv_crv, ch=1)
        wire_def = pm.wire(self.ik_crv, w=self.ik_drv_crv, en=1, gw=False, ce=0, li=0, dds=[(0, 20)],
                n=self.ik_crv.name() + '_wire')
        wire_transform = pm.listConnections((wire_def[0].name() + '.baseWire[0]'))[0]
        pm.parent(self.ik_drv_crv, self.rig_grp)
        pm.parent(wire_transform , self.rig_grp)
        for i, cv in enumerate(['.cv[0:1]', '.cv[2]', '.cv[3:4]']):
            cluster = pm.cluster(self.ik_drv_crv.name() + cv)
            name = join_name([self.ik_crv.name(), 'cls', str(i)])
            cluster[1].rename(name)
            cluster[1].attr('v').set(0)
            self.clusters.append(cluster[1])
            pm.parent(cluster[1], self.ik_ctrls[i])

