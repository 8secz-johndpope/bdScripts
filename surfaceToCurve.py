import maya.OpenMaya as OpenMaya

edgeRing = []


def getInfo():
    mDagPath = OpenMaya.MDagPath()
    mSelList = OpenMaya.MSelectionList()

    OpenMaya.MGlobal.getActiveSelectionList(mSelList)

    if mSelList.length() == 2:
        mSelList.getDagPath(0, mDagPath)

        if mDagPath.hasFn(OpenMaya.MFn.kNurbsCurve):
            getCurveInfo(mDagPath)

        mSelList.getDagPath(1, mDagPath)
        if mDagPath.hasFn(OpenMaya.MFn.kMesh):
            getMeshInfo(mDagPath)


def getCurveInfo(dagPath):
    curveFn = OpenMaya.MFnNurbsCurve(dagPath)
    print curveFn.name()


def getMeshInfo(dagPath):
    meshFn = OpenMaya.MFnMesh(dagPath)
    edgeIter = OpenMaya.MItMeshEdge(dagPath)
    faceIter = OpenMaya.MItMeshPolygon(dagPath)
    mutil = OpenMaya.MScriptUtil()
    intPtr = mutil.asIntPtr()
    while not edgeIter.isDone():
        edgeIter.numConnectedEdges(intPtr)
        numConEdges = mutil.getInt(intPtr)
        if numConEdges == 2:
            facesArray = OpenMaya.MIntArray()
            edgeIter.getConnectedFaces(facesArray)
            for f in facesArray:
                recurseFace(edgeIter, edgeIter.index(), faceIter, f, -1)
            break
        edgeIter.next()


def recurseFace(edgeIter, startEdge, faceIter, startFace, prevFace):
    mutil = OpenMaya.MScriptUtil()
    faceIter.setIndex(startFace, mutil.asIntPtr())
    nextEdge = processFace(edgeIter, startEdge, faceIter)
    facesArray = OpenMaya.MIntArray()
    faceIter.getConnectedFaces(facesArray)
    for f in facesArray:
        if f != prevFace:
            recurseFace(edgeIter, nextEdge, faceIter, f, startFace)


def processFace(edgeIter, startEdge, faceIter):
    edgeRing.append(startEdge)
    edgesArray = OpenMaya.MIntArray()
    mutil = OpenMaya.MScriptUtil()
    faceIter.getEdges(edgesArray)
    for edge in edgesArray:
