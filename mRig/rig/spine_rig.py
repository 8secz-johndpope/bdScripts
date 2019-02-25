import pymel.core as pm

from ..utils import libCtrl as libCtrl
reload(libCtrl)

import base_rig as base
reload(base)

import bdScripts.mRig.utils.libUtils as utils
reload(utils)
from bdScripts.mRig.utils.libUtils import (join_name)

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

class SpineIkFkRig(base.Rig):
    def __init__(self, name='', bnd=[]):
        super(SpineIkFkRig, self).__init__(name=name, side=['', 0], bnd=bnd)
        self.hip = None
        self.ik_spline = None
        self.ik_crv = None
        self.clusters = []
        self.spine_twist_pma = None
        self.spine_roll_pma = None

    def rig(self):
        super(SpineIkFkRig, self).rig()

        self.hip = self.bnd_joints[0]

        self.rig_fk()
        self.rig_ik()

        self.create_ikfk_ctrl(self.bnd_joints[0], [0, 0, -10])
        self.connect_chains()

    def rig_fk(self):
        self.fk_joints = self.create_chain(FK)
        pm.parent(self.fk_joints[0], self.rig_grp)
        self.create_chain_ctrls(FK)

        for i in range(1, len(self.fk_ctrls)):
            pm.parentConstraint(self.fk_ctrls[i], self.fk_joints[i], mo=0)

    def rig_ik(self):
        self.ik_joints = self.create_chain(IK)
        self.create_chain_ctrls(IK)
        self.create_ik_spline()
        self.create_clusters()
        self.create_twist()

    def create_chain_ctrls(self, chain):
        if chain == FK:
            prev_ctrl = None
            i = 0
            for jnt in self.bnd_joints:
                ctrl_name = join_name(jnt.name(), FK, CTRL)
                fk_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'circle', jnt, 1, 1)
                fk_ctrl = fk_ctrl_obj.ctrl
                fk_ctrl_grp = fk_ctrl_obj.ctrl_grp
                fk_ctrl_obj.lock_hide_attr(['translate_XYZ', 'scale_XYZ', 'visibility'])
                self.fk_ctrls.append(fk_ctrl)
                if i == 0:
                    pm.parent(fk_ctrl_grp, self.fk_ctrl_grp)
                elif i > 0:
                    pm.parent(fk_ctrl_grp, prev_ctrl)
                prev_ctrl = fk_ctrl
                i += 1
        if chain == IK:
            for jnt in self.bnd_joints:
                ctrl_name = join_name(jnt.name(), IK, CTRL)
                ik_ctrl_obj = self.create_ctrl(ctrl_name, 1, 'box', jnt, 1, 1)
                ik_ctrl = ik_ctrl_obj.ctrl
                ik_ctrl_grp = ik_ctrl_obj.ctrl_grp
                ik_ctrl_obj.lock_hide_attr(['scale_XYZ', 'visibility'])
                self.ik_ctrls.append(ik_ctrl)
                pm.parent(ik_ctrl_grp, self.ik_ctrl_grp)

    def create_ik_spline(self):
        points = []
        for jnt in self.ik_joints:
            pos = jnt.getTranslation(space='world')
            points.append(pos)

        self.ik_crv = pm.curve(n='spine_ikSpline_crv', d=1, p=points)
        self.ik_crv.attr('v').set(0)
        self.ik_spline = pm.ikHandle(sj=self.ik_joints[0], ee=self.ik_joints[-1], c=self.ik_crv, ccv=False,
                                    sol='ikSplineSolver', name='spine_ikSpline')[0]
        self.ik_spline.attr('v').set(0)

        pm.parent(self.ik_crv, self.rig_grp)
        pm.parent(self.ik_spline, self.rig_grp)

    def create_clusters(self):
        self.ik_drv_crv = pm.rebuildCurve(self.ik_crv, ch=1, rpo=0, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=2, d=3,
                                          tol=0.01, name = self.ik_crv.name().replace('crv', 'drv_crv'))[0]
        self.ik_drv_crv.attr('v').set(0)
        pm.delete(self.ik_drv_crv, ch=1)
        wire_def = pm.wire(self.ik_crv, w=self.ik_drv_crv, en=1, gw=False, ce=0, li=0, dds=[(0, 20)],
                           n=self.ik_crv.name() + '_wire')
        wire_transform = pm.listConnections((wire_def[0].name() + '.baseWire[0]'))[0]

        pm.parent(self.ik_drv_crv, self.rig_grp)
        pm.parent(wire_transform, self.rig_grp)

        for i, cv in enumerate(['.cv[0:1]', '.cv[2]', '.cv[3:4]']):
            cluster = pm.cluster(self.ik_drv_crv.name() + cv)
            name = join_name(self.ik_crv.name(), 'cls', str(i))
            cluster[1].rename(name)
            cluster[1].attr('v').set(0)
            self.clusters.append(cluster[1])
            pm.parent(cluster[1], self.ik_ctrls[i])

    def create_twist(self):
        pma = pm.shadingNode('plusMinusAverage', asUtility=1, name='spine_twist_pma')
        self.spine_twist_pma = pma
        pm.connectAttr(pma.name() + '.output1D', self.ik_spline.name() + '.twist')
        pm.connectAttr(self.ik_ctrls[-1] + '.rx', pma.name() + '.input1D[0]')

        mdl = pm.shadingNode('multDoubleLinear', asUtility=1, name='spine_roll_rev_mdl')
        mdl.attr('input2').set(-1)
        pm.connectAttr(self.ik_ctrls[0] + '.rx', mdl.name() + '.input1')
        pm.connectAttr(mdl.name() + '.output',  pma.name() + '.input1D[1]')

        pma = pm.shadingNode('plusMinusAverage', asUtility=1, name='spine_roll_pma')
        pm.connectAttr(self.ik_ctrls[0] + '.rx', pma.name() + '.input1D[0]')
        pm.connectAttr(pma.name() + '.output1D', self.ik_spline.name() + '.roll')

        self.spine_roll_pma = pma

