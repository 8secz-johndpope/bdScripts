import pymel.core as pm
import base_rig as rn
reload(rn)


class LegRig(rn.Rig):
    def __init__(self, side, prefix, bnd):
        super(LegRig, self).__init__(side, prefix=prefix, bnd=bnd)
        self.parent = None

    def rig(self):
        self.rig_joints = self.create_chain(self.rig_prefix, bnd=1)
        self.rig_fk()
        self.rig_ik()
        self.connect()

    def rig_fk(self):
        self.fk_joints = self.create_chain(self.fk_prefix)

    def rig_ik(self):
        self.ik_joints = self.create_chain(self.ik_prefix)

    def connect(self):
        pass

