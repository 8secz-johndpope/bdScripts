import pymel.core as pm

from ..utils import libCtrl as controller

reload(controller)

import rigNode as RN

reload(RN)

# ------- Global suffixes ------
BNDJNT = RN.BNDJNT
FKJNT = RN.FKJNT
IKJNT = RN.IKJNT
DRVJNT = RN.DRVJNT
CTRL = RN.CTRL
CTRLGRP = RN.CTRLGRP


# ------------------------------

class SpineNode(RN.RigNode):
    def __init__(self, *args, **kargs):
        super(SpineNode, self).__init__(*args, **kargs)
        self.spineNumJnt = 5
        self.spineBndJnt = []
        self.spineRigJnt = []
        self.spineIkJnt = []
        self.spineFkJnt = []
        self.spineHip = 1
        self.spineIkHandle = None

        # self.side = kargs.setdefault('side','L')
        # ----------------------------
        self.spineCtrls = {}
        self.spineIkfkSwitchCtrl = ''

    # -----------------------------


    def rigIt(self):
        self.getSpineJnt()
        self.buildRigChains()
        self.rigIk()

    # self.bdRigIkArm(self.side)
    # self.bndChainConnect()

    def getSpineJnt(self):
        searchFor = pm.ls('Spine*BND')
        if searchFor:
            self.spineBndJnt = searchFor

    def buildRigChains(self):
        if len(self.spineBndJnt):
            self.spineRigJnt = self.duplicateRenameChain(self.spineBndJnt, 'BND', 'RIG')
            self.spineIkJnt = self.duplicateRenameChain(self.spineBndJnt, 'BND', 'IK')
            self.spineFkJnt = self.duplicateRenameChain(self.spineBndJnt, 'BND', 'FK')

    def duplicateRenameChain(self, chain, search, replace):
        newChain = pm.duplicate(chain)
        for jnt in newChain:
            jnt.rename(jnt.name().replace(search, replace))
        newChain[0].rename(newChain[0].name()[:-1])

        return newChain

    def rigIk(self):
        crvPoints = []
        for jnt in self.spineIkJnt:
            pos = jnt.getTranslation(space='world')
            crvPoints.append(pos)

        ikCrv = pm.curve(n='spine_ikSpline_Crv', d=1, p=crvPoints)
        ikCrv = pm.rebuildCurve(ikCrv, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, d=3, tol=0)[0]

        self.spineIkHandle = pm.ikHandle(sj=self.spineIkJnt[0], ee=self.spineIkJnt[-1], c=ikCrv, ccv=False,
                                         sol='ikSplineSolver', name='spine_ikSpline')[0]
