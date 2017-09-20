import pymel.core as pm
import maya.OpenMaya as om


# Creates a ribbon setup as following ( based on a Rigging Dojo technique):
# - creates two 1 degree curves
# - creates driver joints for the curves to be skinned 
# - lofts the curves as 1 degree surface, history on
# - rebuilds the lofted surface as a 3 degree surface, history on


class bdRibbon(object):
    def __init__(self, *args, **kargs):
        self.rigJntList = []
        self.cposList = []
        self.flcTransformList = []
        self.flcGrp = None
        self.rbnSrf = None
        self.mainGrp = None
        self.wireCrv = None
        self.stretchRev = None
        self.width = 0
        self.widthMult = 0.1
        self.rbnLocs = []
        self.rbnLocGrp = None

        self.name = kargs.setdefault('name', 'testRbn')
        self.numCtrl = kargs.setdefault('numCtrl', 3)
        self.numJnt = kargs.setdefault('numJnt', 6)

        # Extras
        self.startJnt = ''
        self.endJnt = ''
        # start and end of ribbon , if a joint is selected ( that has only one child joint), will be recalculated in self.setStartEnd() function
        self.setStartEnd()

    def create(self):
        self.createGroups()
        self.createRbnSrf()
        self.createFlcs('u', 1)

        self.createDrivers()

    def setStartEnd(self):
        self.start = [-10.0, 0.0, 0.0]
        self.end = [10.0, 0.0, 0.0]

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
                elif selected[0].getShape().type() == 'nurbsCurve':
                    self.start = selected[0].getShape().getCV(0, space='world')
                    self.end = selected[0].getShape().getCV(selected[0].getShape().numCVs() - 1, space='world')
                    self.ikCrv = selected[0]

    def createRbnSrf(self):
        startJntVec = om.MVector(self.start[0], self.start[1], self.start[2])
        endJntVec = om.MVector(self.end[0], self.end[1], self.end[2])
        diffVec = endJntVec - startJntVec

        # calculate the witdth of the surface as a fraction of the total joint chain length
        jntChainLength = diffVec.length()
        self.width = jntChainLength * self.widthMult

        crvPoints = []

        for i in range(self.numCtrl):
            vec = startJntVec + diffVec * (i * 1.0 / (self.numCtrl - 1))
            crvPoints.append([vec.x, vec.y, vec.z])

        tmp = pm.curve(n=self.name + '_crv1', d=1, p=crvPoints)
        crv1 = pm.ls(tmp)[0]
        crv1.setPivots(self.start)
        crv2 = pm.duplicate(crv1)[0]

        self.offsetCrv(crv1, -1.0 * self.width / 2)
        self.offsetCrv(crv2, 1.0 * self.width / 2)

        tmpLoftSrf = pm.loft(crv1, crv2, ch=0, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=1, n=self.name + "_tmp")[0]
        rebuiltLoftSrf = \
            pm.rebuildSurface(ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kc=0, su=10, du=3, sv=0, dv=3, tol=0, fr=0, dir=2,
                              n=self.name + "_srf")[0]
        rebuiltLoftSrf.setPivots(rebuiltLoftSrf.c.get())
        self.rbnSrf = rebuiltLoftSrf
        pm.delete(self.rbnSrf, ch=1)

        pm.delete([crv1, crv2, tmpLoftSrf])
        pm.parent(self.rbnSrf, self.mainGrp)

    def createGroups(self):
        pm.select(cl=1)
        self.mainGrp = pm.group(n=self.name + '_grp')
        pm.select(cl=1)

    def offsetCrv(self, crv, offset):
        tmpLoc = pm.spaceLocator(name='tmpLoc' + crv.name())

        tmpLoc.setTranslation([self.start[0], self.start[1], self.start[2] + offset])

        locPos = tmpLoc.getTranslation(space='world')
        locPosVec = om.MVector(locPos)
        crvPos = crv.getRotatePivot(space='world')
        crvPosVec = om.MVector(crvPos)
        newCrvVec = crvPosVec - locPosVec

        crv.setTranslation([newCrvVec.x, newCrvVec.y, newCrvVec.z], space='world')
        pm.delete(tmpLoc)

    def createFlcs(self, direction, ends):
        folicles = []

        pm.select(cl=1)

        for i in range(self.numJnt + 1):
            pm.select(cl=1)
            flcShape = pm.createNode('follicle', name=self.rbnSrf.name() + '_' + str(i).zfill(2) + '_flcShape')
            flcTransform = flcShape.getParent()
            flcTransform.rename(flcShape.name().replace('flcShape', 'flc'))
            folicles.append(flcTransform)

            srfShape = pm.listRelatives(self.rbnSrf)[0]
            srfShape.local.connect(flcShape.inputSurface)
            srfShape.worldMatrix[0].connect(flcShape.inputWorldMatrix)

            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)
            # flcShape.flipDirection.set(1)

            flcShape.parameterU.set((i * 1.0) / self.numJnt)
            flcShape.parameterV.set(0.5)

        pm.select(cl=1)
        self.flcGrp = pm.group(folicles, n=self.rbnSrf.name() + '_flc_grp')
        pm.select(cl=1)
        pm.parent(self.flcGrp, self.mainGrp)
        self.flcTransformList = folicles

    # def bdFlcScaleCnstr(self,scaleGrp,flcGrp):
    #     folicles = flcGrp.listRelatives(c=True,type='transform')
    #     for flc in folicles:
    #         pm.scaleConstraint(scaleGrp,flc)
    #
    #
    def createDrivers(self):
        # surfaceRbn_BS = surfaceRbn.duplicate()[0]
        # surfaceRbn_BS.rename(name + '_BS')
        # surfaceRbn_BS.translateX.set(segments * 0.5 )
        # blendshapeNode = pm.blendShape(surfaceRbn_BS,surfaceRbn,name=surfaceRbn.name() + '_blendShape')[0]
        # blendshapeNode.attr(surfaceRbn_BS.name()).set(1)

        startLocator = pm.spaceLocator(name=self.name + '_start_loc')
        startLocatorGrp = pm.group(startLocator, name=startLocator.name() + '_grp')
        startLocatorGrp.translate.set(self.start)

        midLocator = pm.spaceLocator(name=self.name + '_mid_loc')
        midLocatorGrp = pm.group(midLocator, name=midLocator.name() + '_grp')

        endLocator = pm.spaceLocator(name=self.name + '_end_loc')
        endLocatorGrp = pm.group(endLocator, name=endLocator.name() + '_grp')
        endLocatorGrp.translate.set(self.end)

        self.rbnLocs.append(startLocator)
        self.rbnLocs.append(midLocator)
        self.rbnLocs.append(endLocator)
        #
        pm.pointConstraint(startLocator, endLocator, midLocatorGrp)

        self.rbnLocGrp = pm.group([startLocatorGrp, midLocatorGrp, endLocatorGrp], n=self.name + '_drv_loc_grp')
        #
        #
        curveDrv = pm.curve(d=2, p=[self.start, (0, 0, 0), self.end], k=[0, 0, 1, 1])
        curveDrv.rename(self.name + '_wire_crv')
        self.wireCrv = curveDrv
        wireSrf = pm.duplicate(self.rbnSrf, name=self.name + '_wire_srf')[0]

        wireDef = pm.wire(wireSrf, w=curveDrv, en=1, gw=False, ce=0, li=0, dds=[(0, 20)], n=self.name + '_wire')

        # #kind of a hack
        # wireDefBase = wireDef[0].baseWire[0].listConnections(d=False,s=True)
        # curveCLS,clsGrp = self.bdClustersOnCurve(curveDrv,segments)
        #
        # for i in range(3):
        #     self.rbnLocs[i].translate.connect(curveCLS[i].translate)
        #
        # #organize a bit
        # moveGrp = pm.group([conGrp,surfaceRbn],name=name.replace('srf','move_GRP'))
        # extraGrp = pm.group([flcGrp,surfaceRbn_BS,clsGrp,curveDrv,wireDefBase],name = name.replace('srf','extra_GRP'))
        # allGrp = pm.group([moveGrp,extraGrp],name = name.replace('srf','RBN'))
        #
        # self.bdFlcScaleCnstr(moveGrp,flcGrp)
        #
        # globalCon = pm.spaceLocator()
        # globalCon.rename(name.replace("srf",'world_CON'))
        #
        # pm.parent(globalCon,allGrp)
        # pm.parent(moveGrp,globalCon)
        #
        #
        # twistDef, twistDefTransform = self.bdAddTwist(surfaceRbn_BS)
        # pm.parent(twistDefTransform, extraGrp)
        # topLocator.rotateY.connect(twistDef.startAngle)
        # botLocator.rotateY.connect(twistDef.endAngle)
        #
        # pm.reorderDeformers(wireDef[0],twistDef,surfaceRbn_BS)
        #
        # def bdAddTwist(self,surfaceRbn_BS):
        #     pm.select(surfaceRbn_BS)
        #     twistDef, twistDefTransform = pm.nonLinear(type='twist')
        #     twistDefTransform.rename(surfaceRbn_BS.name().replace('SRF_BS','twistHandle'))
        #     twistDef.rename(surfaceRbn_BS.name().replace('SRF_BS','twist'))
        #     twistDefTransform.rotateX.set(180)
        #     return twistDef, twistDefTransform
        #
        #
        # def bdClustersOnCurve(self,curveDrv,segments):
        #     clusters = []
        #     curveCVs = curveDrv.cv
        #     topClusterTransform= pm.cluster([curveCVs[0],curveCVs[1]],rel=True)[1]
        #     topClusterTransform.rename(curveDrv.name() + '_top_CLS')
        #     topClusterTransform.getShape().originY.set(segments * 0.5)
        #     pivot = curveCVs[0].getPosition(space='world')
        #     topClusterTransform.setPivots(pivot)
        #     clusters.append(topClusterTransform)
        #
        #     midClusterTransform = pm.cluster(curveCVs[1],rel=True)[1]
        #     midClusterTransform.rename(curveDrv.name() + '_mid_CLS')
        #     pivot = curveCVs[1].getPosition(space='world')
        #     midClusterTransform.setPivots(pivot)
        #     clusters.append(midClusterTransform)
        #
        #     botClusterTransform = pm.cluster([curveCVs[1],curveCVs[2]],rel=True)[1]
        #     botClusterTransform.rename(curveDrv.name() + '_bot_CLS')
        #     botClusterTransform.getShape().originY.set(segments * - 0.5 )
        #     pivot = curveCVs[2].getPosition(space='world')
        #     botClusterTransform.setPivots(pivot)
        #     clusters.append(botClusterTransform)
        #
        #     topCluster = topClusterTransform.listConnections(type='cluster')[0]
        #     botCluster = botClusterTransform.listConnections(type='cluster')[0]
        #     pm.percent(topCluster,curveCVs[1],v=0.5)
        #     pm.percent(botCluster,curveCVs[1],v=0.5)
        #
        #     clsGrp = pm.group(clusters,n=curveDrv.name() + '_CLS_GRP')
        #     return clusters,clsGrp
