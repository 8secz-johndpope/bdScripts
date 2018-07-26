import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import pymel.core as pm
import pymel.core.datatypes as dt

source_vtx = []
dest_vtx = []

'''
def pickSource():
    # sel = om.MSelectionList()
    sel = om.MGlobal.getActiveSelectionList()
    sel_dag = sel.getDagPath(0)
    # print sel_dag
    vtx_iter = om.MItMeshVertex(sel_dag)
    while not vtx_iter.isDone():
        print vtx_iter.currentItem()
        vtx_iter.next()


def copyWeights():
    pass
'''

def pickVtx():
    edges = pm.ls(sl=1)
    vtx = pm.polyListComponentConversion(edges, fe=1, tv=1)
    vtx = pm.ls(vtx, fl=1)
    return vtx

def copyWeights(src_vtx, dest_vtx, dist=1):
    shape_mesh = pm.ls(src_vtx[0].name().split('.')[0])[0]
    vtx_all = shape_mesh.vtx
    skin_cluster = pm.listConnections(shape_mesh.name(), type = 'skinCluster')[0]

    # pairs = createPairs(src_vtx, dest_vtx, dist)
    #
    # for v in src_vtx:
    #     src_val =  pm.skinPercent(skin_cluster, v, q=1, v=1)
    #     src_inf =  pm.skinPercent(skin_cluster, v, q=1, t=None)
    #
    #     transform_value = zip(src_inf, src_val)
    #     pm.skinPercent(skin_cluster, pairs[v], tv=transform_value, )


def createPairs(src_vtx, dest_vtx, dist):
    pairs = {}
    for src in src_vtx:
        src_pos_v = dt.Vector(src.getPosition(space='world'))
        for dest in dest_vtx:
            dest_pos_v = dt.Vector(dest.getPosition(space='world'))
            if (dest_pos_v - src_pos_v).length() < dist:
                pairs[src] = dest
    return pairs




