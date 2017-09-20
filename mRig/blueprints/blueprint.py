import pymel.core as pm
import json

from ..utils import libWidgets as UI

reload(UI)

from ..utils import libUtils as utils

reload(utils)

from ..utils import libCtrl as CTRL

reload(CTRL)

from .. import mRigGlobals as MRIGLOBALS

reload(MRIGLOBALS)

# ------- Global suffixes ------
BPGRP = MRIGLOBALS.BPGRP
BPGUIDESGRP = MRIGLOBALS.BPGUIDESGRP
BPCTRL = MRIGLOBALS.BPCTRL
BPGUIDE = MRIGLOBALS.BPGUIDE
BLUEPRINT_TYPE = 'blueprint'


# ------------------------------

class Blueprint(object):
    def __init__(self, *args, **kargs):
        # ----------------------------
        self.bpTopGrp = ''
        self.bpGuidesGrp = ''
        self.bpGuidesList = []
        self.bpController = ''
        # -----------------------------
        self.bpName = kargs.setdefault('name', '')
        self.bpCharacter = kargs.setdefault('character', None)
        self.bpParent = kargs.setdefault('parent', '')
        self.bpCtrlShape = kargs.setdefault('ctrlShape', 'box')
        self.bpSide = kargs.setdefault('side', '')
        self.bpMirror = kargs.setdefault('mirror', 1)
        self.bpType = ''
        # -------------------------------------------
        self.bpGuideSize = kargs.setdefault('guideSize', 1)
        self.bpGuidesPos = {}
        # -------------------------------------------
        self.bpInfo = kargs.setdefault('buildInfo', {})
        self.bpLength = 100

    def create(self):
        self.createGroups()
        self.createController()
        self.createGuides()
        self.addAttributes()
        self.saveBlueprintInfo()
        pm.select(cl=1)

    def createGroups(self):
        pm.select(cl=1)
        self.bpTopGrp = self.bpName + '_' + BPGRP
        pm.group(name=self.bpTopGrp)
        pm.select(cl=1)

        self.bpGuidesGrp = self.bpName + '_' + BPGUIDESGRP
        pm.group(name=self.bpGuidesGrp)
        pm.select(cl=1)

        pm.parent(self.bpGuidesGrp, self.bpTopGrp)

    def createController(self):
        ctrlPos = self.bpGuidesPos[0]['pos']
        newCtrl = CTRL.Controller(ctrlName=self.bpName + '_' + BPCTRL, scale=4, ctrlType=self.bpCtrlShape,
                                  ctrlPos=ctrlPos)
        self.bpController = newCtrl.buildController()

        controllerParent = pm.listRelatives(self.bpController, p=1, type='transform')[
            0]  # pm.listConnections('%s.parent'%self.bpController)[0]

        pm.parent(controllerParent, self.bpTopGrp)
        pm.parent(self.bpGuidesGrp, self.bpController)

    def createGuides(self):
        # At the moment just plain joints
        i = 1
        prevGuide = ''
        for index, data in self.bpGuidesPos.iteritems():
            childClass = self.__class__.__name__

            if childClass == 'SingleBlueprint':
                # if its the SingleBlueprint, the only guide needs no number count in its name
                guideName = self.bpName + '_' + BPGUIDE
            else:
                # for more guides, we name them based on the name of the blueprint and we number them
                guideName = self.bpName + '_' + str(i).zfill(2) + '_' + BPGUIDE
            guidePos = data['pos']

            # if index == 0:
            # controllerParent = pm.listConnections('%s.parent'%self.bpController)[0]
            # pm.xform(controllerParent,t=guidePos,ws=1)
            pm.select(cl=1)

            guide = pm.joint(name=guideName, p=guidePos)
            guide.radius.set(self.bpGuideSize)

            guideAxis = Axis(name=guideName + 'Axis', guide=guide)
            guideAxis.createAxis()
            pm.parent(guideAxis.axName, guide)
            pm.select(cl=1)
            pm.parent(guide, self.bpGuidesGrp)
            self.bpGuidesList.append(guide)
            if i > 1:
                self.createLink(guide, prevGuide)
            prevGuide = guide
            i += 1

    def addAttributes(self):
        utils.addStringAttr(self.bpTopGrp, 'name', self.bpName)
        utils.addStringAttr(self.bpTopGrp, 'type', self.bpType)
        utils.addMessageAttr(self.bpTopGrp, self.bpParent, 'parent')
        utils.addMessageAttr(self.bpTopGrp, self.bpController, BPCTRL)
        utils.addMessageAttr(self.bpTopGrp, self.bpGuidesGrp, BPGUIDESGRP)

    def createLink(self, guide1, guide2):
        clusters = []
        guide1Pos = guide1.getTranslation(space='world')
        guide2Pos = guide2.getTranslation(space='world')
        linkCrv = pm.curve(n=guide2 + '_crvlink', d=1, p=[guide1Pos, guide2Pos])
        numCvs = linkCrv.numCVs()

        for i in range(numCvs):
            linkCls = pm.cluster(linkCrv.name() + '.cv[' + str(i) + ']', name=linkCrv.name() + '_cls_' + str(i))[1]
            linkCls.visibility.set(0)
            pm.parent(linkCls, self.bpTopGrp)
            clusters.append(linkCls)

        pm.pointConstraint(guide1, clusters[0], mo=1)
        pm.pointConstraint(guide2, clusters[1], mo=1)
        linkCrv.inheritsTransform.set(0)
        linkCrv.overrideEnabled.set(1)
        linkCrv.overrideDisplayType.set(1)
        pm.parent(linkCrv, self.bpTopGrp)

    def createParentLink(self):
        clusters = []
        bpParent = pm.ls(self.bpParent)[0]  # get the object
        guide0 = self.bpGuidesList[0]

        guide1Pos = guide0.getTranslation(space='world')
        guide2Pos = bpParent.getTranslation(space='world')

        linkCrv = pm.curve(n=guide0 + '_bp_parent_link', d=1, p=[guide1Pos, guide2Pos])
        linkCrv.inheritsTransform.set(0)
        linkCrv.overrideEnabled.set(1)
        linkCrv.overrideDisplayType.set(1)

        numCvs = linkCrv.numCVs()

        for i in range(numCvs):
            linkCls = pm.cluster(linkCrv.name() + '.cv[' + str(i) + ']', name=linkCrv.name() + '_cls_' + str(i))[1]
            linkCls.visibility.set(0)
            pm.parent(linkCls, self.bpCharacter.chLinksGrp)
            clusters.append(linkCls)

        pm.pointConstraint(guide0, clusters[0], mo=1)
        pm.pointConstraint(bpParent, clusters[1], mo=1)

        # skinCls = pm.skinCluster( tmp,[bpParent,guide0], tsb=1, ih=1, bindMethod = 0, maximumInfluences = 1, dropoffRate = 10.0 )

        # pm.skinPercent(skinCls.name(),linkCrv+ '.cv[1]',tv=[(bpParent,1)])
        # pm.skinPercent(skinCls.name(),linkCrv+ '.cv[0]',tv=[(guide0,1)])


        pm.parent(linkCrv, self.bpCharacter.chLinksGrp)

    def setParent(self, newParent):
        self.bpParent = newParent

    def parseInfo(self):
        for info, val in self.bpInfo.iteritems():
            if info == 'length':
                self.bpLength = val
            elif info == 'guideSize':
                self.bpGuideSize = val

    def saveBlueprintInfo(self):
        self.bpInfo['topGrp'] = self.bpTopGrp
        strInfo = json.dumps(self.bpInfo)

        if pm.attributeQuery('info', node=self.bpTopGrp, ex=1):
            pm.setAttr(self.bpTopGrp + '.info', l=0)
            pm.setAttr(self.bpTopGrp + '.info', str(strInfo), type='string')
            pm.setAttr(self.bpTopGrp + '.info', l=1)
        else:
            utils.addStringAttr(self.bpTopGrp, 'info', strInfo)

    def restore(self):
        self.bpTopGrp = self.bpInfo['topGrp']

        messageAttr = self.bpTopGrp + '.' + BPCTRL
        self.bpController = pm.listConnections('%s' % messageAttr)[0].name()

        messageAttr = self.bpTopGrp + '.' + BPGUIDESGRP
        self.bpGuidesGrp = pm.listConnections('%s' % messageAttr)[0].name()

        guides = pm.listRelatives(self.bpGuidesGrp)
        self.bpGuidesList = [g for g in guides]

        # self.chRootName = charRootGroup.attr('name').get()


class Axis(object):
    def __init__(self, *args, **kargs):
        self.axName = kargs.setdefault('name', '')
        self.axPos = [0, 0, 0]
        self.axGuide = kargs.setdefault('guide')
        self.axScale = 1
        self.axShaders = self.createRGBShaders()

    def createAxis(self):
        pm.select(cl=1)
        xyzTopGrp = pm.group(name=self.axName)

        rgbShaders = self.createRGBShaders()

        xCylinder = pm.cylinder(hr=12, r=0.1, p=[0, 0, 0], ax=[1, 0, 0], name=self.axName + 'X')[0]
        xCylinder.translateX.set(0.6)
        xCylinder.setPivots([0, 0, 0], worldSpace=1)
        pm.makeIdentity(t=1, a=1)
        pm.delete(ch=1)
        pm.hyperShade(a=rgbShaders[0])

        yCylinder = pm.cylinder(hr=12, r=0.1, p=[0, 0, 0], ax=[0, 1, 0], name=self.axName + 'Y')[0]
        yCylinder.translateY.set(0.6)
        yCylinder.setPivots([0, 0, 0], worldSpace=1)
        pm.makeIdentity(t=1, a=1)
        pm.delete(ch=1)
        pm.hyperShade(a=rgbShaders[1])

        zCylinder = pm.cylinder(hr=12, r=0.1, p=[0, 0, 0], ax=[0, 0, 1], name=self.axName + 'Z')[0]
        zCylinder.translateZ.set(0.6)
        zCylinder.setPivots([0, 0, 0], worldSpace=1)
        pm.makeIdentity(t=1, a=1)
        pm.delete(ch=1)
        pm.hyperShade(a=rgbShaders[2])

        xArrow = pm.cone(hr=2, r=0.2, p=[0, 0, 0], ax=[1, 0, 0], name=self.axName + 'arrX')[0]
        xArrow.translateX.set(1.4)
        xArrow.setPivots([0, 0, 0], worldSpace=1)
        pm.makeIdentity(t=1, a=1)
        pm.delete(ch=1)
        pm.hyperShade(a=rgbShaders[0])

        yArrow = pm.cone(hr=2, r=0.2, p=[0, 0, 0], ax=[0, 1, 0], name=self.axName + 'arrY')[0]
        yArrow.translateY.set(1.4)
        yArrow.setPivots([0, 0, 0], worldSpace=1)
        pm.makeIdentity(t=1, a=1)
        pm.delete(ch=1)
        pm.hyperShade(a=rgbShaders[1])

        zArrow = pm.cone(hr=2, r=0.2, p=[0, 0, 0], ax=[0, 0, 1], name=self.axName + 'arrZ')[0]
        zArrow.translateZ.set(1.4)
        zArrow.setPivots([0, 0, 0], worldSpace=1)
        pm.makeIdentity(t=1, a=1)
        pm.delete(ch=1)
        pm.hyperShade(a=rgbShaders[2])

        pm.parent(
            [xCylinder.getShape(), yCylinder.getShape(), zCylinder.getShape(), xArrow.getShape(), yArrow.getShape(),
             zArrow.getShape()], xyzTopGrp, r=1, s=1)

        guidePos = self.axGuide.getTranslation(worldSpace=1)

        jntRadius = self.axGuide.radius.get()
        scaleFactor = [jntRadius * 1.2, jntRadius * 1.2, jntRadius * 1.2]

        xyzTopGrp.translate.set(guidePos)
        xyzTopGrp.scale.set(scaleFactor)
        pm.makeIdentity(xyzTopGrp, t=1, s=1, r=1, a=1)
        pm.delete([xCylinder, yCylinder, zCylinder, xArrow, yArrow, zArrow])

        plug = pm.listConnections(xyzTopGrp.getShapes()[0].name() + '.instObjGroups[0]', plugs=1)
        if plug:
            xyzTopGrp.getShapes()[0].instObjGroups[0] // plug[0]
            xyzTopGrp.getShapes()[0].instObjGroups[0] >> plug[0]
        plug = pm.listConnections(xyzTopGrp.getShapes()[3].name() + '.instObjGroups[0]', plugs=1)
        if plug:
            xyzTopGrp.getShapes()[3].instObjGroups[0] // plug[0]
            xyzTopGrp.getShapes()[3].instObjGroups[0] >> plug[0]

        plug = pm.listConnections(xyzTopGrp.getShapes()[1].name() + '.instObjGroups[0]', plugs=1)
        if plug:
            xyzTopGrp.getShapes()[1].instObjGroups[0] // plug[0]
            xyzTopGrp.getShapes()[1].instObjGroups[0] >> plug[0]
        plug = pm.listConnections(xyzTopGrp.getShapes()[4].name() + '.instObjGroups[0]', plugs=1)
        if plug:
            xyzTopGrp.getShapes()[4].instObjGroups[0] // plug[0]
            xyzTopGrp.getShapes()[4].instObjGroups[0] >> plug[0]

        plug = pm.listConnections(xyzTopGrp.getShapes()[2].name() + '.instObjGroups[0]', plugs=1)
        if plug:
            xyzTopGrp.getShapes()[2].instObjGroups[0] // plug[0]
            xyzTopGrp.getShapes()[2].instObjGroups[0] >> plug[0]
        plug = pm.listConnections(xyzTopGrp.getShapes()[5].name() + '.instObjGroups[0]', plugs=1)
        if plug:
            xyzTopGrp.getShapes()[5].instObjGroups[0] // plug[0]
            xyzTopGrp.getShapes()[5].instObjGroups[0] >> plug[0]

    @staticmethod
    def createRGBShaders():
        search = pm.ls('redAxisSG', type='shadingEngine')
        if search:
            xShadingGrp = search[0]
        else:
            xShader = pm.shadingNode("blinn", asShader=True, name='redAxis')
            xShadingGrp = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='redAxisSG')
            xShader.outColor >> xShadingGrp.surfaceShader
            xShader.color.set([1, 0, 0])

        search = pm.ls('greenAxisSG', type='shadingEngine')
        if search:
            yShadingGrp = search[0]
        else:
            yShader = pm.shadingNode("blinn", asShader=True, name='greenAxis')
            yShader.color.set([0, 1, 0])
            yShadingGrp = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='greenAxisSG')
            yShader.outColor >> yShadingGrp.surfaceShader

        search = pm.ls('blueAxisSG', type='shadingEngine')
        if search:
            zShadingGrp = search[0]
        else:
            zShader = pm.shadingNode("blinn", asShader=True, name='blueAxis')
            zShader.color.set([0, 0, 1])
            zShadingGrp = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='blueAxisSG')
            zShader.outColor >> zShadingGrp.surfaceShader

        return [xShadingGrp, yShadingGrp, zShadingGrp]
