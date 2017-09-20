import pymel.core as pm

import bdRig.system.module as module

reload(module)

import bdRig.system.guide as guide

reload(guide)

import bdRig.utils.mayaDecorators as decorators

reload(decorators)


class ArmModule(module.Module):
    def __init__(self, *args, **kargs):
        super(ArmModule, self).__init__(*args, **kargs)
        self.upperRollJnt = kargs.setdefault('upperRollJnt', 0)
        self.lowerRollJnt = kargs.setdefault('lowerRollJnt', 0)
        self.moduleType = 'arm'
        self.moduleGuidesData = {0: {'name': 'ShoulderGuide', 'pos': [0, 0, 0], 'orient': 0},
                                 1: {'name': 'ElbowGuide', 'pos': [10, 0, -3], 'orient': 0},
                                 2: {'name': 'WristGuide', 'pos': [20, 0, 0], 'orient': 1}}
        self.upperRollGuides = []
        self.lowerRollGuides = []

    def createModule(self):
        # print 'Building module %s'%self.name
        self.createGroups()
        # print 'Groups created'
        self.createGuides()
        # print 'Guides created'
        # self.saveModuleInfo()
        # pm.select(self.moduleCtrl)
        self.addRollGuides()
        self.saveModuleInfo()

    def addRollGuides(self):
        if self.upperRollJnt > 0:
            total = self.upperRollJnt
            for i in range(self.upperRollJnt):
                self.createRollGuide('upper', i, total)

        if self.lowerRollJnt > 0:
            total = self.lowerRollJnt
            for i in range(self.lowerRollJnt):
                self.createRollGuide('lower', i, total)

    def createRollGuide(self, limb, index, total):
        shoulderGuide = self.getGuideByName(self.name + '_' + self.moduleGuidesData[0]['name'])
        elbowGuide = self.getGuideByName(self.name + '_' + self.moduleGuidesData[1]['name'])
        handGuide = self.getGuideByName(self.name + '_' + self.moduleGuidesData[2]['name'])

        if limb == 'upper':
            shoulderElbowCrv = shoulderGuide.getLineTo(elbowGuide)
            rollGuide = guide.Guide(name=shoulderGuide.name + '_Roll_0' + str(index), moduleParent=self.name)
            rollGuide.drawGuide()
            self.addGuide(rollGuide)
            rollGuide.guideGrp.inheritsTransform.set(0)
            self.lockRollGuideAttrs(rollGuide)

            pociNode = pm.shadingNode('pointOnCurveInfo', asUtility=1)
            shoulderElbowCrv.getShape().worldSpace[0] >> pociNode.inputCurve
            pociNode.position >> rollGuide.guideGrp.translate
            pociNode.parameter.set(1.0 * (1.0 + index) / (total + 1.0))
            pm.aimConstraint(elbowGuide.transform, rollGuide.guideGrp)

        elif limb == 'lower':
            elbowWristCrv = elbowGuide.getLineTo(handGuide)
            rollGuide = guide.Guide(name=elbowGuide.name + '_Roll_0' + str(index), moduleParent=self.name)
            rollGuide.drawGuide()
            self.addGuide(rollGuide)
            rollGuide.guideGrp.inheritsTransform.set(0)
            self.lockRollGuideAttrs(rollGuide)
            self.limitRollGuideTx(rollGuide)

            pociNode = pm.shadingNode('pointOnCurveInfo', asUtility=1)
            elbowWristCrv.getShape().worldSpace[0] >> pociNode.inputCurve
            pociNode.position >> rollGuide.guideGrp.translate
            pociNode.parameter.set(1.0 * (1.0 + index) / (total + 1.0))
            pm.aimConstraint(handGuide.transform, rollGuide.guideGrp)

    def lockRollGuideAttrs(self, guide):
        guide.transform.tz.lock()
        guide.transform.ty.lock()

        guide.transform.rx.lock()
        guide.transform.ry.lock()
        guide.transform.rz.lock()

    def setGuidesOrder(self):

        pass

    def limitRollGuideTx(self, guide):
        pass
