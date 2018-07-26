import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
# from maya.OpenMayaUI import MProgressWindow
import maya.OpenMayaMPx as OpenMayaMpx
import sys
import math

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class zooSurgeonCommand(om.MPxCommand):
    cmdName = "zooSurgeonCommand"

    def __init__(self):
        om.MPxCommand.__init__(self)
        self.proxyGroups = ''
        self.averageWeights = []
        self.facesWeights = {}
        self.proxyInfluencePairs = {}
        self.animCurvesTranslate = {}
        self.animCurvesRotate = {}
        self.animCurvesScale = {}
        self.inPlug = om.MPlug()

    @staticmethod
    def creator():
        return zooSurgeonCommand()

    def doIt(self,argList):
        mSelList = om.MGlobal.getActiveSelectionList()

        if mSelList.length() > 0:
            for i in range(mSelList.length()):
                mDagPath = mSelList.getDagPath(i)

                if mDagPath.hasFn(om.MFn.kMesh):
                    fnMesh = om.MFnMesh(mDagPath)
                    skinNode = self.getSkincluster(fnMesh)
                    if skinNode:
                        self.createProxies(mDagPath, fnMesh, skinNode)
                #         self.resetAttr()
            # self.groupAllProxies()
        else:
            sys.stdout.write('Nothing selected')
    
    def resetAttr(self):
        self.averageWeights = []
        self.facesWeights = {}
        self.proxyInfluencePairs = {}
        self.animCurvesTranslate = {}
        self.animCurvesRotate = {}
        self.animCurvesScale = {}        
        
    def createProxies(self, node, meshFn, skinNode):
        mSkinInf = om.MDagPathArray()
        skinInfNames = []
        components = om.MFnSingleIndexedComponent()
        mFaceVerts = om.MIntArray()
        weights = om.MDoubleArray()
        
        weightsDict = {}
        try:
            mSkinInf = skinNode.influenceObjects()
            print mSkinInf
        except:
            sys.stderr.write('Object has no influences')
            return
        numFaces = meshFn.numPolygons

        polyIter = om.MItMeshPolygon(node)
        while not polyIter.isDone():
            self.averageWeights = [0] * len(mSkinInf)
            mFaceVerts = polyIter.getVertices()
            vertComp = components.create(om.MFn.kMeshVertComponent)
            components.addElements(mFaceVerts)
            vertIter = om.MItMeshVertex(node,vertComp)
            while not vertIter.isDone():
                weights, infIndex = skinNode.getWeights(node, vertIter.currentItem())
                # print weights, infIndex
                self.averageFaceWeights(weights, mSkinInf)
                vertIter.next()
            self.setFaceWeights(polyIter.index(), self.averageWeights, mSkinInf)
            polyIter.next(None)

        print self.facesWeights
        print self.averageWeights


        allFaces = []
        for i in range(numFaces):
            allFaces.append(i)
        translation = om.MFloatVector(0,0,0)
        for inf, faces in self.facesWeights.iteritems():
            dgMod = om.MDagModifier()
            meshName = node.partialPathName()
            proxyName = meshName.split('|')[-1] + '_' + inf + '_proxy'
            dgMod.commandToExecute('duplicate -n ' + proxyName + ' ' + meshName)
            #dgMod.commandToExecute('group -w -n ' + proxyName + '_grp ' + proxyName)
            dgMod.commandToExecute('parent -w ' + proxyName)
            dgMod.doIt()

            duplicatedMeshDag = self.getDagPath(proxyName)
            self.unlockDupChannels(duplicatedMeshDag)
            duplicatedFn = om.MFnMesh(duplicatedMeshDag)
            facesTodelete = list(set(allFaces) - set(faces))
            facesArray = om.MIntArray()

            if len(facesTodelete) > 0:
                for f in facesTodelete:
                    facesArray.append(f)

                duplicatedFn.extractFaces(facesArray,translation)
                duplicatedFn.collapseFaces(facesArray)
                duplicatedFn.updateSurface()

            # self.setProxyPivot(duplicatedMeshDag,inf)
            # self.proxyInfluencePairs[duplicatedMeshDag] = self.getDagPath(inf)
        #
        # self.animateProxy()
        # self.groupProxies(node)

    def averageFaceWeights(self, weights, skinInf):
        # non_zero_weights = {}
        # for index, value in enumerate(weights):
        #     if value > 0:
        #         non_zero_weights[skinInf[index].partialPathName()] = value
        # print non_zero_weights
        for i in range(len(self.averageWeights)):
            self.averageWeights[i] += weights[i]

    def setFaceWeights(self, polyIndex, weights, mSkinInf):
        maxValue = sorted(weights)[-1]
        index = list(weights).index(maxValue)
        self.appendFaceWeights(polyIndex, mSkinInf[index].partialPathName())

    def appendFaceWeights(self, polyIndex, infName):
        index = int(polyIndex)
        if self.facesWeights.has_key(infName):
            val = self.facesWeights[infName]
            val.append(index)
            self.facesWeights[infName] = val
        else:
            self.facesWeights[infName] = [index]

    def groupProxies(self,node):
        dgMod = om.MDagModifier()
        proxiesString = ''
        for proxy in self.proxyInfluencePairs.keys():
            proxiesString = proxiesString + proxy.partialPathName() + ' '
        dgMod.commandToExecute('group -w -n ' + node.partialPathName() + '_proxies_grp ' + proxiesString) 
        dgMod.doIt()
        self.proxyGroups = self.proxyGroups + node.partialPathName() + '_proxies_grp '
    
    def groupAllProxies(self):
        rigNode = self.getDagPath('*RIG')
        proxyGroupName = ''

        if rigNode:
            proxyGroupName = rigNode.partialPathName()
        if proxyGroupName != '':
            proxyGroupName += '_proxies_grp'
        else:
            proxyGroupName = 'proxies_grp'
            
        dgMod = om.MDagModifier()
        dgMod.commandToExecute('group -w -n ' + proxyGroupName +' ' + self.proxyGroups) 
        dgMod.doIt()
    
    def animateProxy(self):
        startTime = oma.MAnimControl.minTime()
        endTime = oma.MAnimControl.maxTime()
        startVal = int(startTime.asUnits(om.MTime.kPALFrame))
        endVal = int(endTime.asUnits(om.MTime.kPALFrame))
        
        #self.constraintProxies()
        startTranslation = {}
        startRotation = {}
        self.createProxyAnimCurves()
        for i in range(startVal,endVal+1):
            currentTime = om.MTime(i,om.MTime.kPALFrame)
            oma.MAnimControl.setCurrentTime(currentTime)
            for proxyDag,jntDag in self.proxyInfluencePairs.iteritems():
                if i == startVal:
                    startTranslation[jntDag] = self.getJointValue(jntDag,'t')
                    jntRotation = self.getJointValue(jntDag,'r')
                    jntScale = self.getJointValue(jntDag,'s')
                    self.addProxyKey(currentTime,proxyDag,om.MVector(0,0,0),jntRotation,jntScale)
                else:
                    jntTranslation = self.getJointValue(jntDag,'t')
                    deltaTranslation = startTranslation[jntDag] - jntTranslation
                    deltaTranslation = om.MVector(-1*deltaTranslation.x,-1*deltaTranslation.y,-1*deltaTranslation.z)
                    
                    jntRotation = self.getJointValue(jntDag,'r')
                    jntScale = self.getJointValue(jntDag,'s')
                    
                    
                    self.addProxyKey(currentTime,proxyDag,deltaTranslation,jntRotation,jntScale)

        oma.MAnimControl.setCurrentTime(startTime)        
                
    def constraintProxies(self):
        dgMod = om.MDagModifier()
        for proxyDag,jntDag in self.proxyInfluencePairs.iteritems():
            proxyTransformFn = om.MFnTransform(proxyDag)
            jntTransformFn = om.MFnTransform(jntDag)
            
            dgMod.commandToExecute('parentConstraint -mo ' + jntTransformFn.name() + ' ' + proxyTransformFn.name() )
            dgMod.doIt()
    
    def addProxyKey(self,time,proxyDag,translate,rotate,scale):
        self.animCurvesTranslate[proxyDag][0].addKeyframe(time,translate.x)
        self.animCurvesTranslate[proxyDag][1].addKeyframe(time,translate.y)
        self.animCurvesTranslate[proxyDag][2].addKeyframe(time,translate.z)

        self.animCurvesRotate[proxyDag][0].addKeyframe(time,math.radians(rotate[0]))
        self.animCurvesRotate[proxyDag][1].addKeyframe(time,math.radians(rotate[1]))
        self.animCurvesRotate[proxyDag][2].addKeyframe(time,math.radians(rotate[2]))

        self.animCurvesScale[proxyDag][0].addKeyframe(time,scale[0])
        self.animCurvesScale[proxyDag][1].addKeyframe(time,scale[1])
        self.animCurvesScale[proxyDag][2].addKeyframe(time,scale[2])
        
    def createProxyAnimCurves(self):
        for proxyDag in self.proxyInfluencePairs.keys():
            proxyDagNodeFn = om.MFnDagNode(proxyDag)
            
            attrXCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'translateX')
            attrYCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'translateY')
            attrZCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'translateZ')

            self.animCurvesTranslate[proxyDag] = [attrXCurve,attrYCurve,attrZCurve]
            
            attrXCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'rotateX')
            attrYCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'rotateY')
            attrZCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'rotateZ')
        
            self.animCurvesRotate[proxyDag] = [attrXCurve,attrYCurve,attrZCurve]
            
            attrXCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'scaleX')
            attrYCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'scaleY')
            attrZCurve = self.createAnimCurve(proxyDagNodeFn,proxyDag,'scaleZ')
        
            self.animCurvesScale[proxyDag] = [attrXCurve,attrYCurve,attrZCurve]
            
            
    def createAnimCurve(self,dagNodeFn,dag,attribute):
        attr = dagNodeFn.attribute(attribute)
        attrCurve = oma.MFnAnimCurve()
        attrCurve.create(dag.transform(),attr, None )
        
        return attrCurve
        
    def unlockDupChannels(self, dagMesh):
        depNode = om.MFnDependencyNode(dagMesh.node())
        depNode.findPlug("translateX", False).isLocked = False
        depNode.findPlug("translateY", False).isLocked = False
        depNode.findPlug("translateZ", False).isLocked = False

        depNode.findPlug("rotateX", False).isLocked = False
        depNode.findPlug("rotateY", False).isLocked = False
        depNode.findPlug("rotateZ", False).isLocked = False

        depNode.findPlug("scaleX", False).isLocked = False
        depNode.findPlug("scaleY", False).isLocked = False
        depNode.findPlug("scaleZ", False).isLocked = False


    def setProxyPivot(self,proxy,jnt):
        proxyTransformFn = om.MFnTransform(proxy)
        jntDagPath = self.getDagPath(jnt)
        jntPivot = self.getJointValue(jntDagPath,'t')
        proxyTransformFn.setRotatePivot(om.MPoint(jntPivot.x,jntPivot.y,jntPivot.z),om.MSpace.kWorld,1)
        proxyTransformFn.setScalePivot(om.MPoint(jntPivot.x,jntPivot.y,jntPivot.z),om.MSpace.kWorld,1)
        
        proxyPoints = self.getProxyPoints(proxy)
        proxyUvs = self.getProxyUVs(proxy)
        
        jntScale = self.getJointValue(jntDagPath,'s')
        
        scaleDoubleArray = om.MScriptUtil()
        scaleDoubleArray.createFromList( [jntScale[0], jntScale[1], jntScale[2]], 3 )
        scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
        proxyTransformFn.setScale(scaleDoubleArrayPtr)
        
        jntRotate = self.getJointValue(jntDagPath,'r')
        eulerRotation = om.MEulerRotation(math.radians(jntRotate[0]),math.radians(jntRotate[1]),math.radians(jntRotate[2]))
        proxyTransformFn.setRotation(eulerRotation)
        self.setProxyPoints(proxy,proxyPoints)
        self.setProxyUVs(proxy,proxyUvs)
        
        
        #proxyTransformFn.setTranslation(om.MVector(-1*jntPivot.x,-1*jntPivot.y,-1*jntPivot.z),om.MSpace.kWorld)
        #dgMod = om.MDagModifier()
        #dgMod.commandToExecute('makeIdentity -apply true -t 1 -r 1 -s 1 ' + proxyTransformFn.name())
        #dgMod.doIt()
        #proxyTransformFn.setTranslation(om.MVector(jntPivot.x,jntPivot.y,jntPivot.z),om.MSpace.kWorld)
        
        #m_list = [[0.0 for x in range(4)] for x in range(4)]
        #m_list[0][0] = m_list[1][1] = m_list[2][2] = 1.0
        #m_list[3][3] = 1.0
        #zeroMatrix = om.MMatrix()
        #om.MScriptUtil.createMatrixFromList( m_list, zeroMatrix )
        #transformMatrix = om.MTransformationMatrix(zeroMatrix)
        #proxyTransformFn.setRestPosition(transformMatrix)

    def getProxyUVs(self,proxy):
        proxyMeshFn = om.MFnMesh(proxy)
        u = om.MFloatArray()
        v= om.MFloatArray()
        proxyMeshFn.getUVs(u,v)
        return [u,v]

    def setProxyUVs(self,proxy,uvs):
        proxyMeshFn = om.MFnMesh(proxy)
        proxyMeshFn.setUVs(uvs[0],uvs[1])

    
    def getProxyPoints(self,proxy):
        proxyMeshFn = om.MFnMesh(proxy)
        allPoints = om.MPointArray()
        proxyMeshFn.getPoints(allPoints ,om.MSpace.kWorld)
        return allPoints
    
    def setProxyPoints(self,proxy,points):
        proxyMeshFn = om.MFnMesh(proxy)
        proxyMeshFn.setPoints(points,om.MSpace.kWorld)
        
    def getJointValue(self,jntDag,val):
        jntDagPath = self.getDagPath(jntDag)
        jntMatrix = jntDagPath.inclusiveMatrix()
        jntTransformMatrix = om.MTransformationMatrix(jntMatrix)
        if val == 't':
            jntTranslation = jntTransformMatrix.getTranslation(om.MSpace.kWorld)
            return jntTranslation
        elif val == 'r':
            eulerRot = jntTransformMatrix.eulerRotation()
            jntRotation  = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]
            return jntRotation 
        elif val == 's':
            scaleDoubleArray = om.MScriptUtil()
            scaleDoubleArray.createFromList( [1.0, 1.0, 1.0], 3 )
            scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
            jntTransformMatrix.getScale(scaleDoubleArrayPtr,om.MSpace.kWorld)
            jntscale = [om.MScriptUtil().getDoubleArrayItem( scaleDoubleArrayPtr, 0 ),om.MScriptUtil().getDoubleArrayItem( scaleDoubleArrayPtr, 1 ),om.MScriptUtil().getDoubleArrayItem( scaleDoubleArrayPtr, 2 )]
            return jntscale

    def getDagPath(self,proxyName):
        mSelList =  om.MSelectionList()
        try:
            mSelList.add(proxyName)
        except:
            return None
        
        mDagPath = mSelList.getDagPath(0)
        
        if mDagPath:
            return mDagPath
        else:
            return None
    
    def getSkincluster(self, fnMesh):
        '''
        get a list of all the skin clusters in the file, iterate and see if the shapes connected match our selection
        '''
        self.inPlug = fnMesh.findPlug('inMesh', False)
        connections = self.inPlug.connectedTo(True, False)
        for c in connections:
            mObj = c.node()
            try:
                skinClusterFn = oma.MFnSkinCluster(mObj)
                return skinClusterFn
            except:
                sys.stderr.write("No skin cluster found! ")
                return None

    
    
def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.registerCommand(zooSurgeonCommand.cmdName,zooSurgeonCommand.creator)
    except:
        sys.stderr.write("Failed to register command: " + zooSurgeonCommand.cmdName)

def uninitializePlugin(mobject):
    plugin_fn = om.MFnPlugin(mobject)
    try:
        plugin_fn.deregisterCommand(zooSurgeonCommand.cmdName)
    except:
        sys.stderr.write("Failed to unregister command: " + zooSurgeonCommand.cmdName)