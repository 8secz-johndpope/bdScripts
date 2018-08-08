###############################################################################
#    Module:       spine_ik_rig
#    Date:         27.07.2017
#    Author:       Oleg Solovjov
#
#    Description:    Spine ik rig. Based on ribbon joint rig.
#
#    Globals:
#
#    Classes:
#
#    Functions:
#
###############################################################################
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

class SpineIkSplineRig(base.RIG):
    def __init__(self, name, bnd):
        super(SpineIkSplineRig, self).__init__(name='', side='', bnd=None)

        self.hip = None
        self.ik_handle = None
        self.ik_crv = None
        self.ik_drv_crv = None
        self.clusters = []

        self.spine_roll_pma = None
        self.spine_twist_pma = None

    def create(self):
        '''
        Creates ik ribbon spine rig.
        :return: Returns nothing.
        '''
        super(SpineIkSplineRig, self).createHierarchy()
        self.create_ik_chain()
        self.bind_anim()
        self.create_ik_spline()
        self.create_ik_ctrl()
        self.create_clusters()
        self.create_connections()
        self.cleanUp()

    def create_ik_chain(self):
        for jnt in self.rig_joints:
            new_jnt = pm.duplicate(jnt, name='ik_' + jnt , po=1)[0]
            self.ik_joints.append(new_jnt)

        for i in range(len(self.ik_joints) - 1, 0, -1):
            pm.parent(self.ik_joints[i], self.ik_joints[i - 1])

        pm.parent(self.ik_joints[0], self.jointGrp)

    def create_ik_spline(self):
        points = []
        for jnt in self.ik_joints:
            pos = jnt.getTranslation(space='world')
            points.append(pos)

        self.ik_crv = pm.curve(n='spine_ikSpline_crv', d=1, p=points)
        self.ik_crv.attr('v').set(0)
        self.ik_handle = pm.ikHandle(sj=self.ik_joints[0], ee=self.ik_joints[-1], c=self.ik_crv, ccv=False,
                                    sol='ikSplineSolver', name='spine_ikSpline')[0]
        self.ik_handle.attr('v').set(0)

        pm.parent(self.ik_crv, self.rigGrp)
        pm.parent(self.ik_handle, self.rigGrp)

    def create_ik_ctrl(self):
        '''
        Creates main controls for ribbon twist rig.
        Start, end and middle controls.
        They are circles for a first time.
        Could be replaced with another shape with replaceCtrlShape()
        from ctrl_curve_lib later.
        :return: Returns nothing.
        '''
        pass
        # start_ctrl, start_ctrl_grp = boxCtrl('spine1_ik_ctrl')
        # nonProportionalScaleCtrl(start_ctrl, (1, 12, 12))
        # setSideColorCoding(start_ctrl, 'center_ik')
        # self.ik_ctrl.append(start_ctrl)
        # self.ik_ctrl_grp.append(start_ctrl_grp)
        #
        # mid_ctrl, mid_ctrl_grp = boxCtrl('spine2_ik_ctrl')
        # nonProportionalScaleCtrl(mid_ctrl, (0.5, 10.0, 10.0))
        # setSideColorCoding(mid_ctrl, 'center_ik')
        # self.ik_ctrl.append(mid_ctrl)
        # self.ik_ctrl_grp.append(mid_ctrl_grp)
        #
        # end_ctrl, end_ctrl_grp = boxCtrl('spine3_ik_ctrl')
        # nonProportionalScaleCtrl(end_ctrl, (1, 12.0, 12.0))
        # setSideColorCoding(end_ctrl, 'center_ik')
        # self.ik_ctrl.append(end_ctrl)
        # self.ik_ctrl_grp.append(end_ctrl_grp)
        #
        # # place main controls
        # pm.parent(start_ctrl_grp, self.rig_joints[0])
        # zeroOutTrans(start_ctrl_grp)
        # pm.parent(start_ctrl_grp, w=True)
        #
        # pm.parent(end_ctrl_grp, self.rig_joints[-1])
        # zeroOutTrans(end_ctrl_grp)
        # pm.parent(end_ctrl_grp, w=True)
        #
        # pcName = self.composeNodeName('midCtrl', 'pc')
        # pc = pm.pointConstraint([start_ctrl, end_ctrl], mid_ctrl_grp, mo=False, w=1, n=pcName)[0]
        # self.appendToNodeList(pc)
        #
        # acName = self.composeNodeName('midCtrl', 'ac')
        # ac = pm.aimConstraint(start_ctrl, mid_ctrl_grp, aimVector=(1, 0, 0), upVector=(0, 1, 0)
        #                       , worldUpVector=(0, 0, 1), worldUpType="vector", n=acName)[0]
        # self.appendToNodeList(ac)
        #
        # self.rigConnectAttr('%s.%s' % (start_ctrl, 'v'), '%s.%s' % (mid_ctrl,'v'))
        # self.rigConnectAttr('%s.%s' % (start_ctrl, 'v'), '%s.%s' % (end_ctrl, 'v'))
        #
        # pm.parent(self.ik_ctrl_grp, self.ctrlGrp)
        #
        # pm.orientConstraint(end_ctrl, self.ik_joints[-1])

    def create_clusters(self):
        self.ik_drv_crv = pm.rebuildCurve(self.ik_crv, ch=1, rpo=0, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=2, d=3,
                                          tol=0.01, name = self.ik_crv.name().replace('crv', 'drv_crv'))[0]
        self.ik_drv_crv.attr('v').set(0)
        pm.delete(self.ik_drv_crv, ch=1)
        wire_def = pm.wire(self.ik_crv, w=self.ik_drv_crv, en=1, gw=False, ce=0, li=0, dds=[(0, 20)],
                n=self.ik_crv.name() + '_wire')
        wire_transform = pm.listConnections((wire_def[0].name() + '.baseWire[0]'))[0]

        pm.parent(self.ik_drv_crv, self.rigGrp)
        pm.parent(wire_transform , self.rigGrp)

        for i, cv in enumerate(['.cv[0:1]', '.cv[2]', '.cv[3:4]']):
            cluster = pm.cluster(self.ik_drv_crv.name() + cv)
            name = join_name(self.ik_crv.name(), 'cls', str(i))
            cluster[1].rename(name)
            cluster[1].attr('v').set(0)
            self.clusters.append(cluster[1])
            pm.parent(cluster[1], self.ik_ctrl[i])

    def create_connections(self):
        pma = pm.shadingNode('plusMinusAverage', asUtility=1, name='spine_twist_pma')
        self.spine_twist_pma = pma
        pm.connectAttr(pma.name() + '.output1D', self.ik_handle.name() + '.twist')
        pm.connectAttr(self.ik_ctrl[-1] + '.rx', pma.name() + '.input1D[0]')

        mdl = pm.shadingNode('multDoubleLinear', asUtility=1, name='spine_roll_rev_mdl')
        mdl.attr('input2').set(-1)
        pm.connectAttr(self.ik_ctrl[0] + '.rx', mdl.name() + '.input1')
        pm.connectAttr(mdl.name() + '.output',  pma.name() + '.input1D[1]')

        pma = pm.shadingNode('plusMinusAverage', asUtility=1, name='spine_roll_pma')
        pm.connectAttr(self.ik_ctrl[0] + '.rx', pma.name() + '.input1D[0]')
        pm.connectAttr(pma.name() + '.output1D', self.ik_handle.name() + '.roll')

        self.spine_roll_pma = pma

    def cleanUp(self):
        for ctrl in self.ik_ctrl:
            for attr in ['sx', 'sy', 'sz', 'v']:
                lockHideAttr(ctrl, attr)

    def unCleanUp(self):
        super(SpineIkSplineRig, self).unCleanUp()


    def bind_anim(self):
        '''
        Binds ribbon stripe rig joints to result joints.
        Binds with parentConstraints.
        :return: Returns nothing.
        '''
        if not len(self.rig_joints):
            msg = "Please set result joints with setResJoints() method before."
            self.logger.error(msg)
            raise ValueError, msg

        for i in range(len(self.rig_joints)):
            pc = pm.parentConstraint(self.ik_joints[i]
                                     , self.rig_joints[i]
                                     , mo=True, w=1.0)[0]
            self.appendToNodeList(pc)


