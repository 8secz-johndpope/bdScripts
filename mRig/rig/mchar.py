import pymel.core as pm

from ..utils import libCtrl as libCtrl
reload(libCtrl)

import base_rig as base
reload(base)

import bdScripts.mRig.utils.libUtils as utils
reload(utils)
from bdScripts.mRig.utils.libUtils import (join_name, obj_from_name)

# ------- Global suffixes ------
BND = base.BND
FK = base.FK
IK = base.IK
DRV = base.DRV
RIG = base.RIG
CTRL = base.CTRL
CTRLGRP = base.CTRLGRP
MAINGRP = base.MAINGRP
GRP = base.GRP
# ------------------------------

class Character():
    def __init__(self, name='', root=''):
        self.name = name
        self.top_grp = None
        self.root_jnt = obj_from_name(root)
        self.controllers_grp = None
        self.joints_grp = None
        self.geometry_grp = None
        self.subrigs_grp = None
        self.rigs = []

    def create(self):
        self.create_groups()

    def create_groups(self):
        pm.select(cl=1)
        self.top_grp = pm.group(name = join_name(self.name, 'rig', GRP))
        pm.select(cl=1)
        self.controllers_grp = pm.group(name = join_name(self.name, CTRL, GRP))
        pm.select(cl=1)
        self.joints_grp = pm.group(name = join_name(self.name, 'joints', GRP))
        pm.select(cl=1)
        self.geometry_grp = pm.group(name = join_name(self.name, 'geo', GRP))
        pm.select(cl=1)
        self.subrig_grp = pm.group(name = join_name(self.name, 'subrigs', GRP))
        pm.select(cl=1)
        pm.parent([self.controllers_grp, self.joints_grp, self.geometry_grp, self.subrig_grp], self.top_grp)

    def add_rig(self, rig):
        self.rigs.append(rig)
        pm.parent(rig.controllers_grp, self.controllers_grp)
        pm.parent(rig.rig_grp, self.subrig_grp)









