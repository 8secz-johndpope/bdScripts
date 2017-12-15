import maya.api.OpenMaya as OpenMaya
import pymel.core as pm
import mayaDecorators as decorators

def run_tool():
    selection = OpenMaya.MGlobal.getActiveSelectionList()
    meshes = []
    if selection.length() == 2:
        iterator = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kDagNode)
        while not iterator.isDone():
            meshes.append(iterator.getDagPath())
            iterator.next()
    else:
        pm.warning("select a source and a destionation")
        return

    match_objects(meshes)


def match_objects(meshes):
    pm.undoInfo(openChunk=True)
    fn_src = None
    fn_dest = None

    if meshes[0].hasFn(OpenMaya.MFn.kMesh):
        fn_src = OpenMaya.MFnMesh(meshes[0])

    if meshes[1].hasFn(OpenMaya.MFn.kMesh):
        fn_dest = OpenMaya.MFnMesh(meshes[1])

    if fn_src.numVertices == fn_dest.numVertices:
        points_src = fn_src.getPoints()
        fn_dest.setPoints(points_src)
        fn_dest.updateSurface()
    else:
        pm.warning("Source and destination have different number of verts, aborting")
        return

    pm.undoInfo(closeChunk=True)

