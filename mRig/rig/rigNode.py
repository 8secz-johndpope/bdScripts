import pymel.core as pm

from ..utils import libCtrl as controller

reload(controller)

# ------- Global suffixes ------
BNDJNT = 'BND'
FKJNT = 'FK'
IKJNT = 'IK'
DRVJNT = 'DRV'
CTRL = 'ctrl'
CTRLGRP = 'ctrl_grp'


# ------------------------------

class RigNode(object):
    def __init__(self, *args, **kargs):
        self.rnSide = ''
        self.rnMirrored = 0
        self.rnStrLeft = 'L'
        self.rnStrRight = 'R'
        self.rnBndChain = []
        self.rnFkChain = []
        self.rnIkChain = []
        self.rnRbnChain = []
        # -----------------------------
        self.rnJntPos = kargs.setdefault('position', [])
        self.rnName = kargs.setdefault('name', 'rigNode')

    def buildBndJnt(self):
        pm.select(cl=1)
        jntList = []
        for i in range(1, len(rnJntPos)):
            jnt = pm.joint(n=self.side + self.name + '_' + str(i) + '_' + BNDJNT, p=pos)
            jntList.append(jnt)
        pm.joint(jntList[0], e=True, oj='xyz', secondaryAxisOrient='yup', zso=True)
        pm.select(cl=1)

    def setAttributes(self):
        pass

    def buildDrv(self, suffix):
        drvChain = []
        for jnt in self.bndChain:
            dup = pm.duplicate(jnt, po=1)[0]
            dup.rename(jnt.name().replace(BNDJNT, suffix))
            drvChain.append(dup)
        for i in range((len(drvChain) - 1), 0, -1):
            pm.parent(drvChain[i], drvChain[i - 1])
        '''
        drvRoot = pm.duplicate(self.bndChain[0])[0]
        drvRoot.rename(self.bndChain[0].name().replace(BNDJNT,suffix))
        drvRelatives = drvRoot.listRelatives(ad=True,type='joint',pa=True)
        drvRelatives.reverse()
        toDelete = drvRelatives[3:]
        drvRelatives = drvRelatives[:3]
        pm.delete(toDelete)

        for jnt in drvRelatives:
            jnt.rename(jnt.name().split('|')[-1].replace(BNDJNT,suffix))

        drvChain = [drvRoot] + drvRelatives
        for jnt in drvChain:
            if 'Roll' in jnt.name():
                print jnt
                #pm.removeJoint(jnt)
        '''
        return drvChain
