import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
from maya.OpenMayaUI import MProgressWindow
import maya.OpenMayaMPx as OpenMayaMpx
import sys, math, array
import pymel.core as pm

import utils.mayaDecorators as decorators


@decorators.undoable
def mirrorVertexWeight():
    vertPosDict = {}

    mDagPath = OpenMaya.MDagPath()
    fnMesh = None
    skinNode = None
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)

    if selection.length() > 0:
        selection.getDagPath(0, mDagPath)
        if mDagPath.hasFn(OpenMaya.MFn.kMesh):
            fnMesh = OpenMaya.MFnMesh(mDagPath)

    componentIter = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMeshVertComponent)

    selection_DagPath = OpenMaya.MDagPath()

    componentVert = OpenMaya.MObject()
    selectedMObject = OpenMaya.MObject()

    try:
        componentIter.getDagPath(selection_DagPath, componentVert)
    except:
        pm.warning('select vertices')
        return

    vert_iter = OpenMaya.MItMeshVertex(selection_DagPath, componentVert)
    while not vert_iter.isDone():
        vertPos = vert_iter.position(OpenMaya.MSpace.kWorld)
        vertIndex = vert_iter.index()
        vertPosDict[vertIndex] = vertPos
        vert_iter.next()

    mirrorVertsDict = buildMirrorVert(vertPosDict)

    if fnMesh:
        skinNode = getSkincluster(fnMesh)

    targetWeightsDict = {}

    if skinNode:
        vert_iter.reset()

        skinInf = OpenMaya.MDagPathArray()
        skinNode.influenceObjects(skinInf)

        influenceIndices = OpenMaya.MIntArray()
        for i in range(skinInf.length()):
            influenceIndices.append(i)

        while not vert_iter.isDone():
            vertIndex = vert_iter.index()
            if vertIndex in mirrorVertsDict.keys():
                infCount = OpenMaya.MScriptUtil()
                infCountPtr = infCount.asUintPtr()
                OpenMaya.MScriptUtil.setUint(infCountPtr, 0)
                weights = OpenMaya.MDoubleArray()
                skinNode.getWeights(mDagPath, vert_iter.currentItem(), weights, infCountPtr)
                targetWeightsDict[vertIndex] = weights

            vert_iter.next()

        vert_iter.reset()

        while not vert_iter.isDone():
            vertIndex = vert_iter.index()
            for key, val in mirrorVertsDict.iteritems():
                if vertIndex == val:
                    skinNode.setWeights(mDagPath, vert_iter.currentItem(), influenceIndices, targetWeightsDict[key])
            vert_iter.next()


def buildMirrorVert(vertPosDict):
    mirrorVertsDict = {}
    for index in vertPosDict.keys():
        mirrorIndex = findZMirror(index, vertPosDict)
        if mirrorIndex >= 0:
            mirrorVertsDict[index] = mirrorIndex
            mirrorVertsDict = removeDuplicate(mirrorVertsDict, index)

    return mirrorVertsDict


def removeDuplicate(mirrorVertsDict, mirrorIndex):
    tempDict = {}
    for index, mirror in mirrorVertsDict.iteritems():
        if mirror != mirrorIndex:
            tempDict[index] = mirror

    return tempDict


def findZMirror(index, vertPosDict):
    indexPos = vertPosDict[index]
    for vertIndex in vertPosDict.keys():
        if index != vertIndex:
            if ((indexPos[0] < vertPosDict[vertIndex][0] + 2) and (indexPos[0] > vertPosDict[vertIndex][0] - 2)) and (
                (indexPos[1] < vertPosDict[vertIndex][1] + 2) and (indexPos[1] > vertPosDict[vertIndex][1] - 2)) and (
                indexPos[2] > vertPosDict[vertIndex][2]):
                return vertIndex

    return -1


def getSkincluster(fnMesh):
    '''
    get a list of all the skin clusters in the file, iterate and see if the shapes connected match our selection
    '''
    skinClustersIt = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kSkinClusterFilter)
    while not skinClustersIt.isDone():
        oItem = skinClustersIt.item()
        fnSkinCluster = OpenMayaAnim.MFnSkinCluster(oItem)
        numGeom = fnSkinCluster.numOutputConnections()
        for i in range(numGeom):
            index = fnSkinCluster.indexForOutputConnection(i)
            outputObject = fnSkinCluster.outputShapeAtIndex(index)
            if outputObject == fnMesh.object():
                return fnSkinCluster
        skinClustersIt.next()
