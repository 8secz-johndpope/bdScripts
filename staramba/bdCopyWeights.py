import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.OpenMayaUI as mui
import shiboken2

import pymel.core as pm
import pymel.core.datatypes as dt
import math


from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from ..utils import libWidgets as UI
reload(UI)

def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)

copyWeightsWin = 'copyWeightsWin'

source_vtx = []
dest_vtx = []


class CopyWeightsUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(CopyWeightsUI, self).__init__(parent)

        self.setObjectName(copyWeightsWin)
        self.setWindowTitle('Copy Weights')

        self.srcFaces = []
        self.dstFaces = []
        self.pairs = {}
        self.meshFn = None
        self.meshDag = None
        self.skinFn = None

        self.srcFacesWgt = QtWidgets.QLineEdit()
        self.dstFacesWgt = QtWidgets.QLineEdit()
        self.srcPickBtn = QtWidgets.QPushButton('Set Source Faces')
        self.dstPickBtn = QtWidgets.QPushButton('Set Destination Faces')
        self.copyWeightsBtn = QtWidgets.QPushButton('Copy Weights')

        self.setupUI()
        self.setupSignals()


    def setupUI(self):
        centralWidget = QtWidgets.QWidget()

        mainLayout = UI.VertBox()
        srcBox = UI.TitledBox(title='Source Faces')
        dstBox = UI.TitledBox(title='Destination Faces')

        srcBox.layout.addWidget(self.srcFacesWgt)
        srcBox.layout.addWidget(self.srcPickBtn)

        dstBox.layout.addWidget(self.dstFacesWgt)
        dstBox.layout.addWidget(self.dstPickBtn)

        mainLayout.addWidget(srcBox)
        mainLayout.addWidget(dstBox)

        separator = UI.Separator()
        mainLayout.addWidget(separator)
        mainLayout.addWidget(self.copyWeightsBtn)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def setupSignals(self):
        self.srcPickBtn.clicked.connect(self.setFaces)
        self.dstPickBtn.clicked.connect(self.setFaces)
        self.copyWeightsBtn.clicked.connect(self.copyWeights)

    def setFaces(self):
        if 'Source' in self.sender().text():
            self.srcFaces = self.getSelectedFaces()
            self.srcFacesWgt.setText(' '.join(map(str, self.srcFaces)))
        elif 'Destination' in self.sender().text():
            self.dstFaces = self.getSelectedFaces()
            self.dstFacesWgt.setText(' '.join(map(str, self.dstFaces)))

    @staticmethod
    def getSelectedFaces():
        sel = om.MGlobal.getActiveSelectionList()
        faces = []
        if sel.length() == 1:
            mesh_dag, face_component = sel.getComponent(0)
            if face_component is not None:
                faceVertexIter = om.MItMeshPolygon(mesh_dag, face_component)
                while not faceVertexIter.isDone():
                    faces.append(int(faceVertexIter.index()))
                    faceVertexIter.next(None)

        return faces

    def copyWeights(self):
        srcVtx = []
        dstVtx = []
        self.pairs = {}

        sel = om.MGlobal.getActiveSelectionList()
        if sel.length() == 1:
            meshDag = sel.getDagPath(0)
            if meshDag.hasFn(om.MFn.kMesh):
                self.meshFn = om.MFnMesh(meshDag)
                self.meshDag = meshDag

                for id in self.srcFaces:
                    faceVtx = self.meshFn.getPolygonVertices(id)
                    for v in faceVtx:
                        srcVtx.append(v)
                for id in self.dstFaces:
                    faceVtx = self.meshFn.getPolygonVertices(id)
                    for v in faceVtx:
                        dstVtx.append(v)

        srcVtx = list(set(srcVtx))
        dstVtx = list(set(dstVtx))

        self.pairs = self.createPairs(srcVtx, dstVtx)
        self.getSkinFn()
        vtxIter = om.MItMeshVertex(self.meshDag)
        influences = self.skinFn.influenceObjects()
        influenceArray = om.MIntArray()
        influenceArray.setLength(len(influences))
        for count in xrange(len(influences)):
            influenceArray[count] = count

        for srcId, dstId in self.pairs.iteritems():
            vtxIter.setIndex(srcId)
            weights = self.skinFn.getWeights(self.meshDag, vtxIter.currentItem(),influenceArray)
            vtxIter.setIndex(dstId)
            self.skinFn.setWeights(self.meshDag, vtxIter.currentItem(),influenceArray, weights, False)


    def createPairs(self,srcVtx, dstVtx):
        vtxIter = om.MItMeshVertex(self.meshDag)
        pairs = {}
        for srcId in srcVtx:
            vtxIter.setIndex(srcId)
            srcPos = om.MVector(vtxIter.position(om.MFn.kWorld))
            for dstId in dstVtx:
                vtxIter.setIndex(dstId)
                dstPos = om.MVector(vtxIter.position(om.MFn.kWorld))
                if (dstPos - srcPos).length() < 0.5:
                    pairs[srcId] = dstId

        return pairs


    def getSkinFn(self):
        sel = om.MGlobal.getActiveSelectionList()
        meshDag = sel.getDagPath(0)
        meshDag.extendToShape()
        selList = om.MSelectionList()
        selList.add(meshDag)
        shapeObj = selList.getDependNode(0)
        dagIter = om.MItDependencyGraph(shapeObj, om.MItDependencyGraph.kDownstream, om.MItDependencyGraph.kPlugLevel)
        while not dagIter.isDone():
            currentItem = dagIter.currentNode()
            if currentItem.hasFn(om.MFn.kSkinClusterFilter):
                self.skinFn = oma.MFnSkinCluster(currentItem)
            dagIter.next()



def openTool():
    if pm.window(copyWeightsWin, exists=True, q=True):
        pm.deleteUI(copyWeightsWin)

    tool = CopyWeightsUI()
    tool.show()
    tool.resize(500, 100)

def pickSource():
    # sel = om.MSelectionList()
    sel = om.MGlobal.getActiveSelectionList()
    sel_iter = om.MItSelectionList(sel, om.MFn.kMeshVertComponent)
    l1 = pm.spaceLocator()
    l2 = pm.spaceLocator()
    while not sel_iter.isDone():
        meshDagPath, multiVertexComponent = sel_iter.getComponent()
        if multiVertexComponent is not None:
            itMeshVertex = om.MItMeshVertex(meshDagPath, multiVertexComponent)
            while not itMeshVertex.isDone():
                pos = om.MVector(itMeshVertex.position())
                normal = itMeshVertex.getNormal()
                print pos, normal
                pm.move(l1, pos)
                pm.move(l2, pos+normal)
                itMeshVertex.next()
        # vert_it = om.MItMeshVertex(sel_iter.getDagPath(), )
        # print vert_it.count()
        sel_iter.next()

    # sel_dag = sel.getDagPath(0)
    # # print sel_dag
    # vtx_iter = om.MItMeshVertex(sel_dag)
    # while not vtx_iter.isDone():
    #     print vtx_iter.currentItem()
    #     vtx_iter.next()




def pickVtx():
    edges = pm.ls(sl=1)
    vtx = pm.polyListComponentConversion(edges, fe=1, tv=1)
    vtx = pm.ls(vtx, fl=1)
    return vtx

def copyWeights(src_vtx, dest_vtx, dist=1):
    shape_mesh = pm.ls(src_vtx[0].name().split('.')[0])[0]
    skin_cluster = pm.listConnections(shape_mesh.name(), type = 'skinCluster')[0]

    pairs = createPairs(src_vtx, dest_vtx, dist)

    for v in src_vtx:
        src_val =  pm.skinPercent(skin_cluster, v, q=1, v=1)
        src_inf =  pm.skinPercent(skin_cluster, v, q=1, t=None)

        transform_value = zip(src_inf, src_val)
        pm.skinPercent(skin_cluster, pairs[v], tv=transform_value, )


def createPairs(src_vtx, dest_vtx, dist):
    pairs = {}
    for src in src_vtx:
        src_pos_v = dt.Vector(src.getPosition(space='world'))
        for dest in dest_vtx:
            dest_pos_v = dt.Vector(dest.getPosition(space='world'))
            if (dest_pos_v - src_pos_v).length() < dist:
                pairs[src] = dest
    return pairs



def createPairs1(dist):
    pairs = {}
    vtx = pm.ls(sl=1, fl=1)
    i = 0
    while i < len(vtx):
        src_pos_v = dt.Vector(vtx[i].getPosition(space='world'))
        for j in range(i+1, len(vtx)):
            dest_pos_v = dt.Vector(vtx[j].getPosition(space='world'))
            if (dest_pos_v - src_pos_v).length() < dist:
                pairs[vtx[i]] = vtx[j]
                break
        i += 1


    pm.select(cl=1)
    for v1, v2 in pairs.iteritems():
        pm.select([v1,v2], tgl=1)


def measureDistance():
    verts = pm.ls(sl=1, fl=1)
    v1 = dt.Vector(verts[0].getPosition(space='world'))
    v2 = dt.Vector(verts[1].getPosition(space='world'))
    
    # n1 = verts[0].getNormal()
    # n2 = verts[1].getNormal()
    #
    l1 = pm.spaceLocator()
    l2 = pm.spaceLocator()
    l3 =  pm.spaceLocator()
    l4 = pm.spaceLocator()
    #
    pm.move(l1, v1)
    pm.move(l2, v2)
    # pm.move(l3, v1+n1)
    # pm.move(l4, v2+n2)
    #
    #
    # a1 = math.degrees(v1.angle(n1))
    # a2 = math.degrees(v2.angle(n2))
    #
    # print verts
    # print v1, a1, n1
    # print v2, a2, n2

    length1 = v1.length()
    length2 = v2.length()
    d = v1-v2
    pm.move(l3, d)
    d_length = d.length()

    e = v2 + d
    pm.move(l4, e)

    print verts[0], length1
    print verts[1], length2
    print d, d_length

    angle = v1.axis(v2)
    v3 = v1.rotateBy(angle, 0.1)
    l5 = pm.spaceLocator()
    pm.move(l5, v3)
    #

    # v3 = v1 - v2
    # loc = pm.spaceLocator()
    # pm.move(loc, v3)
    # z_vector = dt.Vector([0,0,1])
    #
    # print math.degrees(z_vector.angle(v3))


    # print v1_pos.axis(v2_pos)
    # print v2_pos.axis(v1_pos)


def checkHit():
    sel = om.MGlobal.getActiveSelectionList()
    mesh_fn = loc_fn = None
    if sel.length():
        mesh_dag = sel.getDagPath(0)
        if mesh_dag.hasFn(om.MFn.kMesh):
            mesh_fn = om.MFnMesh(mesh_dag)

    loc_dag = sel.getDagPath(1)
    if loc_dag.hasFn(om.MFn.kTransform):
        loc_fn = om.MFnTransform(loc_dag)

    print mesh_fn, loc_fn
    ray_src = om.MFloatPoint(loc_fn.translation(om.MSpace.kWorld))
    ray_dir = om.MFloatVector(0,0,1)
    hit_points = mesh_fn.allIntersections(ray_src, ray_dir, om.MSpace.kObject, 9999, False )
    for p in hit_points[0]:
        loc = pm.spaceLocator()
        pm.move(loc, [p[0], p[1], p[2]])



def getSkinFn():
    sel = om.MGlobal.getActiveSelectionList()
    meshDag = sel.getDagPath(0)

    meshDag.extendToShape()
    selList = om.MSelectionList()
    selList.add(meshDag)
    shapeObj = selList.getDependNode(0)
    dagIter =  om.MItDependencyGraph(shapeObj, om.MItDependencyGraph.kDownstream, om.MItDependencyGraph.kPlugLevel)
    skinFn = None
    while not dagIter.isDone():
        currentItem = dagIter.currentNode()
        if currentItem.hasFn(om.MFn.kSkinClusterFilter):
            skinFn = oma.MFnSkinCluster(currentItem)
        dagIter.next()

    vertIter = om.MItMeshVertex(shapeObj)
    influences = skinFn.influenceObjects()
    print len(influences)
    while not vertIter.isDone():
        weights =  skinFn.getWeights(meshDag, vertIter.currentItem())
        vertIter.next()
    # weights = skinFn.getWeights(meshDag, vertIter)

