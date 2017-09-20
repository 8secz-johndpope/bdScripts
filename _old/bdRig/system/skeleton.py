import pymel.core as pm
import pickle
import bdRig.utils.utils as utils

reload(utils)

import bdRig.utils.mayaDecorators as decorators

reload(decorators)


class Skeleton(object):
    def __init__(self, *args, **kargs):
        self.jointList = {}
        self.skeletonInfo = {}
        self.module = kargs.setdefault('module', None)
        self.guidesList = {}

    def build(self):
        if len(self.module.moduleRebuildInfo) > 0:
            self.guidesList = self.module.moduleRebuildInfo['module_guides_names']
            startJnt = ''
            pm.select(cl=1)
            for index, name in self.guidesList.iteritems():
                findGuide = pm.ls(name, type='transform')
                pos = [0, 0, 0]
                if findGuide:
                    guideTransform = findGuide[0]
                    pos = guideTransform.getTranslation(space='world')

                jntGuide = pm.joint(n=name.replace('Guide', 'Bnd') + '_jnt', p=pos)
                self.jointList[index] = {'joint': jntGuide, 'guide': name}
                if index == 0:
                    startJnt = jntGuide
            pm.joint(startJnt, e=True, oj='xyz', secondaryAxisOrient='yup', zso=True)
            pm.select(cl=1)
            print self.jointList

    def saveSkeletonInfo(self):
        findSkeletonGrp = pm.ls('skeleton', type='transform')
        skeletonGrp = None
        if findSkeletonGrp:
            skeletonGrp = findSkeletonGrp[0]

        self.skeletonInfo['skeleton_joints'] = self.jointList
        saveInfo = pickle.dumps(self.skeletonInfo)

        if pm.attributeQuery('skeletonInfo', node=skeletonGrp.name(), ex=True):
            pm.setAttr(skeletonGrp.name() + '.skeletonInfo', str(strInfo), type='string')
        else:
            utils.addStringAttr(skeletonGrp, 'skeletonInfo', saveInfo)
