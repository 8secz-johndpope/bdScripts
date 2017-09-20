import pymel.core as pm
import maya.api.OpenMaya as om


class Ribbon():
    def __init__(self, *args, **kargs):
        self.rbnName = kargs.setdefault('name')
        self.rbnSegments = kargs.setdefault('segments')
        self.rbnDirection = kargs.setdefault('rbnDirection', 'u')
        self.rbnWidth = kargs.setdefault('rbnWidth', 6)
        self.rbnSrf = ''
        self.rbnGrp = ''
        self.rbnTransformGrp = ''
        self.rbnNoTransformGrp = ''
        self.rbnFlcGrp = ''
        self.rbnCtrl = ''
        self.rbnLocs = []
        self.rbnScaleRefCrv = ''
        self.rbnLength = 0
        #  Deformers
        self.rbnBsSrf = ''
        self.rbnVolSrf = ''
        self.rbnWireCrv = ''
        self.rbnTwist = ''
        self.rbnSquash = ''
        self.rbnCls = []
        # Extras
        self.startJnt = ''
        self.endJnt = ''
        self.buildCrv = None
        # start and end of ribbon , if a joint is selected ( that has a child joint), will be recalculated in self.setStartEnd() function
        self.setStartEnd()

    def buildRbnDT(self):
        self.buildGrps()
        self.buildSrf()
        self.rbnFlcGrp = self.createFlcs(self.rbnSrf)
        self.flcScaleCnstr()
        self.addFlcJnt()
        self.rigRbn()
        pm.select(self.rbnCtrl)

    def buildGrps(self):
        pm.select(cl=1)
        self.rbnGrp = pm.group(n=self.rbnName + "_grp", w=1)
        self.rbnCtrl = pm.circle(nr=[0, 1, 0], radius=self.rbnWidth * 2, ch=0, name=self.rbnName + '_trs')[0]
        pm.parent(self.rbnCtrl, self.rbnGrp)
        pm.select(cl=1)
        self.rbnTransformGrp = pm.group(n=self.rbnName + "_transform_grp", w=1)
        pm.parent(self.rbnTransformGrp, self.rbnCtrl)
        pm.select(cl=1)
        self.rbnNoTransformGrp = pm.group(n=self.rbnName + "_notransform_grp", w=1)
        pm.parent(self.rbnNoTransformGrp, self.rbnGrp)

    def rigRbn(self):
        # -------------- Create the wire curve that will drive the blendshape target srf---#
        self.rbnWireCrv = pm.curve(d=2, p=[[self.start[0], 0, self.rbnWidth * 5.0], [0, 0, self.rbnWidth * 5.0],
                                           [self.end[0], 0, self.rbnWidth * 5.0]], k=[0, 0, 1, 1],
                                   name=self.rbnName + '_wire_crv')
        self.rbnWireCrv.hide()
        pm.parent(self.rbnWireCrv, self.rbnNoTransformGrp)

        # -------------- Create the surface that will be the target blendshape ------------#
        self.rbnBsSrf = pm.duplicate(self.rbnSrf, name=self.rbnName + '_srf_bs')[0]
        self.rbnBsSrf.hide()
        pm.parent(self.rbnBsSrf, self.rbnNoTransformGrp)
        pm.xform(self.rbnBsSrf, r=1, t=[0, 0, self.rbnWidth * 5.0])

        blendshapeNode = pm.blendShape(self.rbnBsSrf, self.rbnSrf, name=self.rbnName + '_blendShape')[0]
        blendshapeNode.attr(self.rbnBsSrf.name()).set(1)

        # -------------- Create the locators that will drive the ribbon -------------------#
        topLocator = pm.spaceLocator(name=self.rbnName + '_loc_01', p=[self.start[0], 0, 0])
        pm.makeIdentity(topLocator, apply=True, t=True, r=True, s=True)
        topLocator.setPivots(topLocator.c.get())

        midLocator = pm.spaceLocator(name=self.rbnName + '_loc_02', p=[0, 0, 0])
        midLocatorGrp = pm.group(midLocator, name=midLocator.name() + '_grp')

        botLocator = pm.spaceLocator(name=self.rbnName + '_loc_03', p=[self.end[0], 0, 0])
        pm.makeIdentity(botLocator, apply=True, t=True, r=True, s=True)
        botLocator.setPivots(botLocator.c.get())

        self.rbnLocs.append(topLocator)
        self.rbnLocs.append(midLocator)
        self.rbnLocs.append(botLocator)

        pm.pointConstraint(topLocator, botLocator, midLocatorGrp)
        locGrp = pm.group([topLocator, midLocatorGrp, botLocator], n=self.rbnName + '_loc_grp')

        pm.parent(locGrp, self.rbnTransformGrp)
        # -------------------------- Create the wire deformer  -----------------------------#
        wireDef = pm.wire(self.rbnBsSrf, w=self.rbnWireCrv, en=1, gw=False, ce=0, li=0, dds=[0, 200],
                          n=self.rbnName + '_wire')

        self.clustersOnCurve()

        for i in range(3):
            self.rbnLocs[i].translate.connect(self.rbnCls[i].translate)

        # -------------------------- Create the twist deformer  -----------------------------#
        self.addTwist()

        botLocator.rotateX.connect(self.rbnTwist.startAngle)
        topLocator.rotateX.connect(self.rbnTwist.endAngle)

        pm.reorderDeformers(wireDef[0], self.rbnTwist, self.rbnBsSrf)
        pm.parent(self.rbnTwist, self.rbnNoTransformGrp)
        # -------------------------------- Add volume  --------------------------------------#
        self.addVolume()

    def buildSrf(self):
        startJntVec = om.MVector(self.start[0], self.start[1], self.start[2])
        endJntVec = om.MVector(self.end[0], self.end[1], self.end[2])
        diffVec = endJntVec - startJntVec
        self.rbnLength = diffVec.length()

        crvPoints = []
        for i in range(self.rbnSegments + 1):
            vec = startJntVec + diffVec * (i * 1.0 / self.rbnSegments)
            crvPoints.append([vec.x, vec.y, vec.z])
            # pm.spaceLocator(p=[vec.x,vec.y,vec.z])

        tmp = pm.curve(n=self.rbnName + '_crv1', d=1, p=crvPoints)
        crv1 = pm.ls(tmp)[0]
        crv1.setPivots(self.start)
        crv2 = pm.duplicate(crv1)[0]

        self.offsetCrv(crv1, -1.0 * self.rbnWidth / 2)
        self.offsetCrv(crv2, 1.0 * self.rbnWidth / 2)

        tmpLoftSrf = \
        pm.loft(crv1, crv2, ch=0, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=1, n=self.rbnName + "_lft_srf")[0]
        rebuiltLoftSrf = \
        pm.rebuildSurface(ch=0, rpo=0, rt=0, end=1, kr=1, kcp=0, kc=0, su=0, du=3, sv=0, dv=1, fr=0, dir=2,
                          n=self.rbnName + "_srf")[0]
        rebuiltLoftSrf.setPivots(rebuiltLoftSrf.c.get())
        self.rbnSrf = rebuiltLoftSrf
        pm.delete(self.rbnSrf, ch=1)

        pm.delete([crv1, crv2, tmpLoftSrf])

        pm.parent(self.rbnSrf, self.rbnTransformGrp)

    def setStartEnd(self):
        self.start = [-50.0, 0.0, 0.0]
        self.end = [50.0, 0.0, 0.0]

        selected = pm.ls(sl=1)
        if selected:
            if len(selected) == 1:
                if selected[0].type() == 'joint':
                    self.startJnt = selected[0]
                    children = self.startJnt.getChildren(type='joint')
                    self.endJnt = children[0]

                    start = self.startJnt.getTranslation(space='world')
                    end = self.endJnt.getTranslation(space='world')

                    startJntVec = om.MVector(start[0], start[1], start[2])
                    endJntVec = om.MVector(end[0], end[1], end[2])
                    diffVec = endJntVec - startJntVec
                    length = diffVec.length()

                    self.start = [length * - 0.5, 0, 0]
                    self.end = [length * 0.5, 0, 0]

    def offsetCrv(self, crv, offset):
        startPos = self.start
        tmpLoc = pm.spaceLocator(name='tmpLoc' + crv.name())

        tmpLoc.setTranslation([self.start[0], self.start[1], self.start[2] + offset])

        locPos = tmpLoc.getTranslation(space='world')
        locPosVec = om.MVector(locPos)
        crvPos = crv.getRotatePivot(space='world')
        crvPosVec = om.MVector(crvPos)
        newCrvVec = crvPosVec - locPosVec

        crv.setTranslation([newCrvVec.x, newCrvVec.y, newCrvVec.z], space='world')
        pm.delete(tmpLoc)

    def addFlcJnt(self):
        folicles = self.rbnFlcGrp.listRelatives(c=True, type='transform')
        for flc in folicles:
            flcJoint = pm.joint()
            flcJoint.rename(flc.name().replace('flc', 'jntdrv'))
            pm.parent(flcJoint, flc)
            flcJoint.setTranslation([0, 0, 0])
            self.createJntCtrl(flcJoint, 0.15)

    def createJntCtrl(self, jnt, scale):
        ctrl = pm.circle(n=jnt.name().replace('jntdrv', 'trs'), r=self.rbnWidth * 5, ch=0)[0]
        ctrl.ry.set(90)
        ctrl.setScale([scale, scale, scale])
        ctrl.overrideEnabled.set(1)
        ctrl.overrideColor.set(18)
        pm.makeIdentity(ctrl, a=1)
        ctrlGrp = pm.group(name=ctrl.name() + '_grp')
        if jnt.getParent():
            pm.parent(ctrlGrp, jnt.getParent())
            for axis in ['X', 'Y', 'Z']:
                ctrlGrp.attr('translate' + axis).set(0)
                ctrlGrp.attr('rotate' + axis).set(0)
            pm.parent(jnt, ctrl)
        else:
            pm.parent(ctrlGrp, jnt)
            for axis in ['X', 'Y', 'Z']:
                ctrlGrp.attr('translate' + axis).set(0)
                ctrlGrp.attr('rotate' + axis).set(0)
            pm.parent(ctrlGrp, w=1)
            pm.parent(jnt, ctrl)
        return ctrlGrp

    def createFlcs(self, srf):
        folicles = []

        for i in range(self.rbnSegments + 1):
            flcShape = pm.createNode('follicle', name=srf.name().replace('srf', str(i).zfill(2) + 'FlcShape'))
            flcTransform = flcShape.getParent()
            flcTransform.rename(srf.name().replace('srf', str(i).zfill(2) + '_flc'))
            folicles.append(flcTransform)

            srf.getShape().local.connect(flcShape.inputSurface)
            srf.getShape().worldMatrix[0].connect(flcShape.inputWorldMatrix)

            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)

            if (self.rbnDirection == 'v'):
                flcShape.parameterU.set(0.5)
                # flcShape.parameterV.set((i + 0.5)/self.rbnSegments)
                flcShape.parameterV.set((i * 1.0) / self.rbnSegments)
            else:
                flcShape.parameterV.set(0.5)
                # flcShape.parameterU.set((i + 0.5 )/self.rbnSegments)
                flcShape.parameterU.set((i * 1.0) / self.rbnSegments)

        rbnFlcGrp = pm.group(folicles, n=srf.name().replace('srf', 'flc_grp'))
        pm.parent(rbnFlcGrp, self.rbnGrp)
        pm.parent(rbnFlcGrp, self.rbnNoTransformGrp)

        return rbnFlcGrp

    def flcScaleCnstr(self):
        folicles = self.rbnFlcGrp.listRelatives(c=True, type='transform')
        for flc in folicles:
            pm.scaleConstraint(self.rbnCtrl, flc, mo=1)

    def addTwist(self):
        pm.select(self.rbnBsSrf)
        twistDef, twistDefTransform = pm.nonLinear(self.rbnBsSrf, type='twist')
        twistDefTransform.rename(self.rbnName + '_srf_bs_twistHandle')
        twistDefTransform.scale.set([self.rbnLength * 0.5, self.rbnLength * 0.5, self.rbnLength * 0.5])
        twistDefTransform.hide()
        pm.parent(twistDefTransform, self.rbnNoTransformGrp)

        twistDef.rename(self.rbnName + '_srf_bs_twist')
        twistDefTransform.rotateZ.set(90)
        self.rbnTwist = twistDef
        print twistDefTransform, twistDefTransform.scale
        pm.select(cl=1)

    def clustersOnCurve(self):
        curveCVs = self.rbnWireCrv.cv
        topClusterTransform = pm.cluster([curveCVs[0], curveCVs[1]], rel=True)[1]
        topClusterTransform.rename(self.rbnWireCrv.name() + '_cls_01')
        topClusterTransform.getShape().originX.set(self.start[0])
        pivot = curveCVs[0].getPosition(space='world')
        topClusterTransform.setPivots(pivot)
        self.rbnCls.append(topClusterTransform)

        midClusterTransform = pm.cluster(curveCVs[1], rel=True)[1]
        midClusterTransform.rename(self.rbnWireCrv.name() + '_cls_02')
        pivot = curveCVs[1].getPosition(space='world')
        midClusterTransform.setPivots(pivot)
        self.rbnCls.append(midClusterTransform)

        botClusterTransform = pm.cluster([curveCVs[1], curveCVs[2]], rel=True)[1]
        botClusterTransform.rename(self.rbnWireCrv.name() + '_cls_02')
        botClusterTransform.getShape().originX.set(self.end[0])
        pivot = curveCVs[2].getPosition(space='world')
        botClusterTransform.setPivots(pivot)
        self.rbnCls.append(botClusterTransform)

        topCluster = topClusterTransform.listConnections(type='cluster')[0]
        botCluster = botClusterTransform.listConnections(type='cluster')[0]
        pm.percent(topCluster, curveCVs[1], v=0.5)
        pm.percent(botCluster, curveCVs[1], v=0.5)

        clsGrp = pm.group(self.rbnCls, n=self.rbnWireCrv.name() + '_cls_grp')
        clsGrp.hide()
        pm.parent(clsGrp, self.rbnNoTransformGrp)

    def addVolume(self):
        self.rbnVolSrf = pm.duplicate(self.rbnSrf, name=self.rbnName + '_vol_srf')[0]
        pm.parent(self.rbnVolSrf, self.rbnNoTransformGrp)
        self.rbnSquash, rbnSquashTransform = pm.nonLinear(type='squash')
        rbnSquashTransform.rename(self.rbnName + '_vol_srf_squashHandle')

        pm.parent(rbnSquashTransform, self.rbnNoTransformGrp)

        self.rbnSquash.rename(self.rbnName + '_vol_srf_squash')
        rbnSquashTransform.rotateZ.set(90)

        self.rbnVolFlcGrp = self.createFlcs(self.rbnVolSrf)

        pm.xform(self.rbnVolSrf, t=[0, 0, -0.5 * self.rbnWidth])
        pm.xform(rbnSquashTransform, t=[0, 0, -0.5 * self.rbnWidth])

        # Add volume attributes on the rbn trs 
        pm.addAttr(self.rbnCtrl, ln='volumeAttr', nn='------', at='enum', en='Volume:', keyable=1)
        self.rbnCtrl.volumeAttr.lock()
        pm.addAttr(self.rbnCtrl, ln='enableVolume', nn='Enable', at='double', min=0, max=1, dv=0, keyable=1)
        pm.addAttr(self.rbnCtrl, ln='multiplyVolume', nn='Multiply', at='double', dv=0.7, keyable=1)
        pm.addAttr(self.rbnCtrl, ln='smoothVolume', nn='Smooth', at='double', min=0, max=1, dv=1, keyable=1)

        self.rbnCtrl.smoothVolume.connect(self.rbnSquash.startSmoothness)
        self.rbnCtrl.smoothVolume.connect(self.rbnSquash.endSmoothness)
        # drive the original surface follicles scale based on the translate Z of the vol follicles ( well, not the folicle , but the controler under it, the folicle has the global scale on it)
        folicles = self.rbnVolFlcGrp.listRelatives(c=True, type='transform')
        for flc in folicles:
            flcShape = flc.getShape()
            if (self.rbnDirection == 'v'):
                flcShape.parameterU.set(0.0)
            else:
                flcShape.parameterV.set(0.0)
            self.connectFlc(folicles.index(flc))

        rbnSquashTransform.hide()
        self.rbnVolFlcGrp.hide()
        self.rbnVolSrf.hide()

        # drive the suqash deformer factor with the scale of the ribbon 
        wireCrvInfo = pm.shadingNode('curveInfo', asUtility=1, name=self.rbnWireCrv.name() + '_ci')
        self.rbnWireCrv.getShape().worldSpace.connect(wireCrvInfo.inputCurve)

        self.rbnScaleRefCrv = pm.duplicate(self.rbnWireCrv, name=self.rbnName + '_scl_crv')[0]
        crvInfo = pm.shadingNode('curveInfo', asUtility=1, name=self.rbnScaleRefCrv.name() + '_ci')
        self.rbnScaleRefCrv.getShape().worldSpace.connect(crvInfo.inputCurve)

        scaleFactorMd = pm.shadingNode('multiplyDivide', au=1, name=self.rbnWireCrv.name() + '_scale_factor_md')
        scaleFactorMd.operation.set(2)
        wireCrvInfo.arcLength.connect(scaleFactorMd.input1X)
        crvInfo.arcLength.connect(scaleFactorMd.input2X)

        zeroFactorAdl = pm.shadingNode('addDoubleLinear', au=1, name=self.rbnWireCrv.name() + '_zerofactor_adl')
        zeroFactorAdl.input2.set(-1)
        scaleFactorMd.outputX.connect(zeroFactorAdl.input1)

        enableVolMdl = pm.shadingNode('multDoubleLinear', au=1, name=self.rbnName + '_enable_volume_mdl')
        self.rbnCtrl.enableVolume.connect(enableVolMdl.input1)
        zeroFactorAdl.output.connect(enableVolMdl.input2)

        enableVolMdl.output.connect(self.rbnSquash.factor)

    def connectFlc(self, index):
        folicles = self.rbnFlcGrp.listRelatives(c=True, type='transform')
        targetFlc = folicles[index]
        volFolicles = self.rbnVolFlcGrp.listRelatives(c=True, type='transform')
        driverFlc = volFolicles[index]
        temp = targetFlc.listRelatives(c=True, type='transform')
        ctrl = None
        for obj in temp:
            if '_trs_grp' in str(obj):
                ctrl = pm.ls(obj)[0]

        mdl = pm.shadingNode('multDoubleLinear', au=1, name=targetFlc.name() + '_tz_mdl')
        adl = pm.shadingNode('addDoubleLinear', au=1, name=targetFlc.name() + '_scaleone_adl')
        self.rbnCtrl.multiplyVolume.connect(mdl.input1)
        driverFlc.translateZ.connect(mdl.input2)
        mdl.output.connect(adl.input1)
        adl.input2.set(1)
        adl.output.connect(ctrl.scaleY)
        adl.output.connect(ctrl.scaleZ)
