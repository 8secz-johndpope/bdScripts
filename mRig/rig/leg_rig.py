import pymel.core as pm


class LegRig():
    def __init__(self, side, suffix=[], bnd = []):
        self.side = side
        self.parent = None

        self.bnd_joints = LegRig.set_bnd(bnd)
        self.anim_joints = []
        self.fk_joints = []
        self.ik_joints = []

        self.ik_ctrls = []
        self.fk_ctrls = []

        self.anim_prefix = suffix[0]
        self.fk_prefix = suffix[0]
        self.ik_prefix = suffix[0]

    def rig(self):
        self.create_chain(self.anim_prefix, bnd=1)
        self.rig_fk()
        self.rig_ik()
        self.connect()

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

        return temp[:]

    def rig_fk(self):
        self.fk_joints = self.create_chain(self.fk_prefix)

    def rig_ik(self):
        self.ik_joints = self.create_chain(self.ik_prefix)

    def create_chain(self, prefix, bnd=0):
        chain = []
        for jnt in self.bnd_joints:
            if bnd:
                new_jnt = pm.duplicate(jnt, name=self.anim_prefix + '_' + jnt.name(), po=1)[0]
            else:
                new_jnt = pm.duplicate(jnt, name=jnt.name().replace(self.anim_prefix, prefix), po=1)[0]
            chain.append(new_jnt)

        for i in range(len(chain)-1, 0, -1):
            pm.parent(chain[i], chain[i-1])

    def connect(self):
        pass

