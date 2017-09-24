import pymel.core as pm
import json
from ..utils import libWidgets as UI
from ..utils import libUtils as utils
from ..utils import libControllers as CTRL
from .. import mRigGlobals as MRIGLOBALS
reload(UI)
reload(utils)
reload(CTRL)
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
        self.top_grp = ''
        self.guides_grp = ''
        self.guides_list = []
        self.controller = ''
        # -----------------------------
        self.name = kargs.setdefault('name', '')
        self.character = kargs.setdefault('character', None)
        self.parent = kargs.setdefault('parent', '')
        self.ctrl_shape = kargs.setdefault('ctrlShape', 'box')
        self.side = kargs.setdefault('side', '')
        self.mirror = kargs.setdefault('mirror', 1)
        self.type_bp = ''
        # -------------------------------------------
        self.guide_size = kargs.setdefault('guideSize', 1)
        self.guide_pos = {}
        # -------------------------------------------
        self.info = kargs.setdefault('buildInfo', {})
        self.length = 100

    def create(self):
        self.create_groups()
        self.create_guides()
        self.create_ctrl()
        self.add_attributes()
        self.save_bp_info()
        pm.select(cl=1)

    def create_groups(self):
        pm.select(cl=1)
        self.top_grp = self.name + '_' + BPGRP
        pm.group(name=self.top_grp)
        pm.select(cl=1)

        self.guides_grp = self.name + '_' + BPGUIDESGRP
        pm.group(name=self.guides_grp)
        pm.select(cl=1)

        pm.parent(self.guides_grp, self.top_grp)

    def create_ctrl(self):
        ctrl_pos = self.guide_pos[0]['pos']
        self.controller = self.name + '_' + BPCTRL
        self.controller = self.name + '_' + BPCTRL
        new_ctrl = CTRL.Controller(name=self.controller, scale=4, shape=self.ctrl_shape, pos=ctrl_pos)
        new_ctrl.buildController()
        print "--------------------------------------", self.ctrl_shape, "--------------------------------------"
        ctrl_parent = pm.listRelatives(self.controller, p=1, type='transform')[0]

        pm.parent(ctrl_parent, self.top_grp)
        pm.parent(self.guides_grp, self.controller)

    def create_guides(self):
        # At the moment just plain joints
        i = 1
        prevGuide = ''
        for index, data in self.guide_pos.iteritems():
            childClass = self.__class__.__name__

            if childClass == 'SingleBlueprint':
                # if its the SingleBlueprint, the only guide needs no number count in its name
                guideName = self.name + '_' + BPGUIDE
            else:
                # for more guides, we name them based on the name of the blueprint and we number them
                guideName = self.name + '_' + str(i).zfill(2) + '_' + BPGUIDE
            guidePos = data['pos']

            # if index == 0:
            # ctrl_parent = pm.listConnections('%s.parent'%self.controller)[0]
            # pm.xform(ctrl_parent,t=guidePos,ws=1)
            pm.select(cl=1)

            guide = pm.joint(name=guideName, p=guidePos)
            guide.radius.set(self.guide_size)

            # guideAxis = Axis(name=guideName + 'Axis', guide=guide)
            # guideAxis.createAxis()
            # pm.parent(guideAxis.axName, guide)
            pm.select(cl=1)
            pm.parent(guide, self.guides_grp)
            self.guides_list.append(guide)
            if i > 1:
                self.create_link(guide, prevGuide)
            prevGuide = guide
            i += 1

    def add_attributes(self):
        utils.addStringAttr(self.top_grp, 'name', self.name)
        utils.addStringAttr(self.top_grp, 'type', self.type_bp)
        utils.addMessageAttr(self.top_grp, self.parent, 'parent')
        utils.addMessageAttr(self.top_grp, self.controller, BPCTRL)
        utils.addMessageAttr(self.top_grp, self.guides_grp, BPGUIDESGRP)

    def create_link(self, guide1, guide2):
        clusters = []
        guide1Pos = guide1.getTranslation(space='world')
        guide2Pos = guide2.getTranslation(space='world')
        linkCrv = pm.curve(n=guide2 + '_crvlink', d=1, p=[guide1Pos, guide2Pos])
        numCvs = linkCrv.numCVs()

        for i in range(numCvs):
            linkCls = pm.cluster(linkCrv.name() + '.cv[' + str(i) + ']', name=linkCrv.name() + '_cls_' + str(i))[1]
            linkCls.visibility.set(0)
            pm.parent(linkCls, self.top_grp)
            clusters.append(linkCls)

        pm.pointConstraint(guide1, clusters[0], mo=1)
        pm.pointConstraint(guide2, clusters[1], mo=1)
        linkCrv.inheritsTransform.set(0)
        linkCrv.overrideEnabled.set(1)
        linkCrv.overrideDisplayType.set(1)
        pm.parent(linkCrv, self.top_grp)

    def create_link_parent(self):
        clusters = []
        parent = pm.ls(self.parent)[0]  # get the object
        guide0 = self.guides_list[0]

        guide1Pos = guide0.getTranslation(space='world')
        guide2Pos = parent.getTranslation(space='world')

        linkCrv = pm.curve(n=guide0 + '_bp_parent_link', d=1, p=[guide1Pos, guide2Pos])
        linkCrv.inheritsTransform.set(0)
        linkCrv.overrideEnabled.set(1)
        linkCrv.overrideDisplayType.set(1)

        numCvs = linkCrv.numCVs()

        for i in range(numCvs):
            linkCls = pm.cluster(linkCrv.name() + '.cv[' + str(i) + ']', name=linkCrv.name() + '_cls_' + str(i))[1]
            linkCls.visibility.set(0)
            pm.parent(linkCls, self.character.ch_links_grp)
            clusters.append(linkCls)

        pm.pointConstraint(guide0, clusters[0], mo=1)
        pm.pointConstraint(parent, clusters[1], mo=1)

        # skinCls = pm.skinCluster( tmp,[parent,guide0], tsb=1, ih=1, bindMethod = 0, maximumInfluences = 1, dropoffRate = 10.0 )

        # pm.skinPercent(skinCls.name(),linkCrv+ '.cv[1]',tv=[(parent,1)])
        # pm.skinPercent(skinCls.name(),linkCrv+ '.cv[0]',tv=[(guide0,1)])

        pm.parent(linkCrv, self.character.ch_links_grp)

    def setParent(self, newParent):
        self.parent = newParent

    def parse_info(self):
        for info, val in self.info.iteritems():
            if info == 'length':
                self.length = val
            elif info == 'guideSize':
                self.guide_size = val

    def save_bp_info(self):
        self.info['topGrp'] = self.top_grp
        strInfo = json.dumps(self.info)

        if pm.attributeQuery('info', node=self.top_grp, ex=1):
            pm.setAttr(self.top_grp + '.info', l=0)
            pm.setAttr(self.top_grp + '.info', str(strInfo), type='string')
            pm.setAttr(self.top_grp + '.info', l=1)
        else:
            utils.addStringAttr(self.top_grp, 'info', strInfo)

    def restore(self):
        self.top_grp = self.info['topGrp']

        messageAttr = self.top_grp + '.' + BPCTRL
        self.controller = pm.listConnections('%s' % messageAttr)[0].name()

        messageAttr = self.top_grp + '.' + BPGUIDESGRP
        self.guides_grp = pm.listConnections('%s' % messageAttr)[0].name()

        guides = pm.listRelatives(self.guides_grp)
        self.guides_list = [g for g in guides]

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
