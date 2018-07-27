import pymel.core as pm

from ..utils import libCtrl as ctrl
reload(ctrl)

# ------- Global suffixes ------
BNDJNT = 'BND'
FKJNT = 'FK'
IKJNT = 'IK'
DRVJNT = 'DRV'
CTRL = 'ctrl'
CTRLGRP = 'ctrl_grp'


# ------------------------------

class Rig(object):
    def __init__(self, side='', prefix=[], bnd=[]):
        self.side = side
        self.mirrored = 0
        self.bnd_joints= Rig.set_bnd(bnd)
        self.rig_joints = []
        self.fk_joints = []
        self.ik_joints = []
        self.rbn_joints = []

        self.ik_ctrls = []
        self.fk_ctrls = []

        self.rig_prefix = prefix[0]
        self.fk_prefix = prefix[1]
        self.ik_prefix = prefix[2]
        # -----------------------------

    def create_chain(self, prefix, bnd=0):
        chain = []
        dup_chain = self.rig_joints
        if bnd:
            dup_chain = self.bnd_joints

        for jnt in dup_chain:
            if bnd:
                new_jnt = pm.duplicate(jnt, name=self.rig_prefix + '_' + jnt.name(), po=1)[0]
            else:
                new_jnt = pm.duplicate(jnt, name=jnt.name().replace(self.rig_prefix, prefix), po=1)[0]
            chain.append(new_jnt)

        for i in range(len(chain)-1, 0, -1):
            pm.parent(chain[i], chain[i-1])

        return chain

    @staticmethod
    def set_bnd(bnd):
        temp = []
        for jnt in bnd:
            find = pm.ls(jnt)
            if find:
                temp.append(find[0])
            else:
                pm.warning('Bind joint {} not found'.format(jnt))
                return None
        print temp
        return temp[:]