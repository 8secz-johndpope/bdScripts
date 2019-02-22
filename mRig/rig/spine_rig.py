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
    def __init__(self, name='', bnd=[], fk=False, ik=False, ribbon=False):
        super(SpineRig, self).__init__(name=name, side='', bnd=bnd)
        self.hip = None
        self.has_fk = fk
        self.has_ik = ik
        self.has_rbn = ribbon

    def rig(self):
        super(SpineRig, self).rig()
        # if self.has_fk:
        #     self.add_fk_rig()
        # if self.has_ik:
        #     self.add_ik_rig()
        # if self.has_rbn:
        #     self.add_rbn_rig()
        #
        # self.create_switch()

    def set_hip(self, hip):
        find = pm.ls(hip)
        if find:
            self.hip = find[0]

    def add_fk_rig(self):
        pass

    def add_ik_rig(self):
        pass

    def add_rbn_rig(self):
        pass

    def create_switch(self):
        pass

