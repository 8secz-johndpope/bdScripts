import pymel.core as pm
import maya.OpenMaya as om
import pickle
import bdRig.utils.utils as utils

reload(utils)
import bdRig.utils.mayaDecorators as decorators

reload(decorators)


class Guide(object):
    def __init__(self, *args, **kargs):
        self.name = kargs.setdefault('name', 'guide')
        self.jointOrient = kargs.setdefault('jointOrient', 'xyz')
        self.moduleParent = kargs.setdefault('moduleParent', None)
        self.orient = kargs.setdefault('orient', 0)
        self.lineConnections = {}
        self.guideInfo = {}
        self.transform = None
        self.guideGrp = None
        self.orientGuide = None

    def saveGuideInfo(self):
        self.guideInfo['name'] = self.name
        self.guideInfo['moduleParent'] = self.moduleParent

        self.guideInfo['jointOrient'] = self.jointOrient
        self.guideInfo['transform'] = self.transform.name()
        self.guideInfo['position'] = self.getPos()
        self.guideInfo['orient'] = self.orient

        saveInfo = pickle.dumps(self.guideInfo)
        utils.addStringAttr(self.guideGrp, 'guideInfo', saveInfo)

    def restoreGuide(self):
        self.guideGrp = pm.ls(self.name + '_grp', type='transform')[0]
        self.guideInfo = self.guideGrp.attr('guideInfo').get()

    def drawGuide(self):
        print 'Creating guide %s' % self.name
        pm.select(cl=1)
        self.guideGrp = pm.group(n=self.name + '_grp')
        pm.select(cl=1)
        jntGuide = pm.joint(name=self.name)
        jntGuide.overrideEnabled.set(1)
        jntGuide.overrideColor.set(18)
        self.transform = pm.ls(jntGuide)[0]
        pm.parent(self.transform, self.guideGrp)
        pm.select(cl=1)

        self.saveGuideInfo()

    def setOrientGuide(self, orient):
        pm.select(cl=1)
        self.orient = orient
        self.orientGuide = pm.duplicate(self.transform)[0]
        self.orientGuide.rename(self.transform.name() + '_orient')
        self.orientGuide.radius.set(0.5)
        self.orientGuide.overrideColor.set(13)
        orientGuideGrp = pm.group(self.orientGuide, name=self.orientGuide.name() + '_grp')
        pm.parentConstraint(self.transform, orientGuideGrp, mo=1)

        if orient == 1:
            pm.move(self.orientGuide, 2, 0, 0, r=1)
        elif orient == 2:
            pm.move(self.orientGuide, 0, 2, 0, r=1)
        elif orient == 3:
            pm.move(self.orientGuide, 0, 0, 2, r=1)
        pm.select(cl=1)

    def setPos(self, pos):
        pm.move(self.guideGrp, pos[0], pos[1], pos[2])

    def getPos(self):
        pos = pm.xform(self.transform, q=1, a=1, ws=1, rp=1)
        return pos

    def drawConnectionTo(self, toGuide):
        pm.select(cl=1)
        conMainGrp = pm.group(n=self.name + '_line_grp')
        conMainGrp.overrideEnabled.set(1)
        conMainGrp.overrideColor.set(18)
        pos1 = self.getPos()
        pos2 = toGuide.getPos()
        connectionCrv = pm.curve(d=1, p=[pos1, pos2], k=[0, 1], name=self.name + '_line')
        pm.parent(connectionCrv, conMainGrp)
        pm.skinCluster(self.transform, toGuide.transform, connectionCrv)

        self.lineConnections[connectionCrv.name()] = [self.transform.name(), toGuide.transform.name()]
        return conMainGrp

    def getLineTo(self, toGuide):
        skinCls = pm.listConnections('%s.worldMatrix[0]' % self.name, type='skinCluster')
        if skinCls:
            for skin in skinCls:
                shape = pm.listConnections('%s.outputGeometry[0]' % skin.name())
                if shape:
                    jnts = pm.skinCluster(skin, q=True, influence=True)
                    if self.transform in jnts and toGuide.transform in jnts:
                        return shape[0]

    def setParent(self, parentsList):
        pass

    def setRollGuide(self, startGuide, endGuide):
        pass
