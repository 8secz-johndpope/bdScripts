###############################################################################
#    Module:       Bogdan Diaconu
#    Date:         20.06.2017
#    Author:       Bogdan Diaconu
#
#    Description:  Utility script to allow relativly quick selection of the vertices that have identical position in world
#                    on two meshes
#
#    Globals:
#
#    Classes:
#
#    Functions:
#    Usage:         Select the source mesh, the one you want the follicles to be on. Select the destination mesh,
#                   this should be the mask. Run the code under
#
#                   import src.tools.intersect_meshes
#                   import pymel.core as pm
#                   vtx = intersect_meshes.get_vertices()
#                   pm.select(vtx)
#
#                   After you will have a selection of vertices selected on the first mesh. Create follicles or locators
#
#
#
###############################################################################
import maya.api.OpenMaya as om
import pymel.core as pm

# def get_vertices(mask):
#     '''
#     :return: a list of vertices
#     '''
#     mSelList = om.MGlobal.getActiveSelectionList()
#     mesh1_dist = {}
#     mesh2_dist = {}
#     meshes = []
#     result_vtx = []
#     if mSelList.length() > 0:
#         first = 0
#         for i in range(mSelList.length()):
#             mDagPath = mSelList.getDagPath(i)
#             if mDagPath.hasFn(om.MFn.kMesh):
#                 fnMesh = om.MFnMesh(mDagPath)
#                 meshes.append(fnMesh)
#                 # print str(fnMesh.name())
#                 points = fnMesh.getPoints()
#                 index = 0
#                 # print fnMesh.getPoints()
#                 for p in points:
#                     vect = om.MVector(p)
#                     if i == 0:
#                         mesh1_dist[index] = p
#                     else:
#                         mesh2_dist[index] = p
#                     index += 1
#
#     loc = []
#     for i2, p2 in mesh2_dist.iteritems():
#         for i1, p1 in  mesh1_dist.iteritems():
#             if (om.MVector(p2) - om.MVector(p1)).length() <= 0.001:
#                 loc.append(i1)
#
#     pm.select(cl=1)
#     if meshes[0].numVertices > meshes[1].numVertices:
#         print meshes[0].name() + ' has more than ' +  meshes[1].name()
#         mesh = pm.ls(meshes[0].name())[0]
#         parent = mesh.getParent()
#         for i in loc:
#             pm.select(parent.name() + '.vtx[' + str(i) + ']', tgl=True)
#     else:
#         print meshes[1].name() + ' has more than ' + meshes[0].name()
#         mesh = pm.ls(meshes[1].name())[0]
#         parent = mesh.getParent()
#         for i in loc:
#             # pm.select(parent.name() + '.vtx[' + str(i) + ']', tgl=True)
#             result_vtx.append(parent.name() + '.vtx[' + str(i) + ']')
#
#     return result_vtx

# def get_vertices(mask):
#     '''
#     :return: a list of vertices
#     '''
#     # get the mask's MFnMesh , based on the string name provided
#     result_vtx = []
#     sel_list = om.MSelectionList()
#     sel_list.add(mask)
#     dag_path = sel_list.getDagPath(0)
#     if dag_path.hasFn(om.MFn.kMesh):
#         mask_mesh_fn = om.MFnMesh(dag_path)
#         # get the selected vertices indices and the fn mesh of the source
#         sel_list = om.MGlobal.getActiveSelectionList()
#
#         if sel_list.length() > 0:
#             (dag_path, comp) = sel_list.getComponent(0)
#             if dag_path.hasFn(om.MFn.kMesh):
#                 src_mesh_fn= om.MFnMesh(dag_path)
#                 if comp.apiType() == om.MFn.kMeshVertComponent:
#                     comp_fn = om.MFnSingleIndexedComponent(comp)
#                     indices = comp_fn.getElements()
#
#                     mask_points = mask_mesh_fn.getPoints()
#                     for i in indices:
#                         src_point = src_mesh_fn.getPoint(i)
#                         for p in mask_points:
#                             if (om.MVector(src_point) - om.MVector(p)).length() <= 0.001:
#                                 result_vtx.append(src_mesh_fn.name() + '.vtx[' + str(i) + ']')
#
#         return result_vtx


def get_vertices(src_mesh_fn, mask_mesh_fn):
    pairs_vtx = {}

    for i in range(mask_mesh_fn.numVertices):#mask_mesh_fn.getPoints():
        p = mask_mesh_fn.getPoint(i)
        (src_p, face_index) = src_mesh_fn.getClosestPoint(p)
        face_vtx_array = src_mesh_fn.getPolygonVertices(face_index)
        for j in face_vtx_array:
            src_point = src_mesh_fn.getPoint(j)
            if (om.MVector(src_point) - om.MVector(p)).length() <= 0.001:
                pairs_vtx[i] = j

    return pairs_vtx


def select_head_vtx():
    sel_list= om.MGlobal.getActiveSelectionList()
    if sel_list.length() > 0:
        src_dag_path = sel_list.getDagPath(0)
        mask_dag_path = sel_list.getDagPath(1)

        src_mesh_fn = om.MFnMesh(src_dag_path)
        mask_mesh_fn = om.MFnMesh(mask_dag_path)
        pairs_vtx = get_vertices(src_mesh_fn, mask_mesh_fn)

        if pairs_vtx:
            selection_list = []
            for head_vtx in pairs_vtx.itervalues():
                selection_list.append(src_mesh_fn.name() + '.vtx[' + str(head_vtx) + ']')

            pm.select(selection_list)

def adjust_mask(new_head_name):
    find = pm.ls(new_head_name)
    if find:
        new_head_shape = find[0].getShape()
        print new_head_shape

        sel_list = om.MGlobal.getActiveSelectionList()
        if sel_list.length() > 0:
            src_dag_path = sel_list.getDagPath(0)
            mask_dag_path = sel_list.getDagPath(1)

            src_mesh_fn = om.MFnMesh(src_dag_path)
            mask_mesh_fn = om.MFnMesh(mask_dag_path)
            pairs_vtx = get_vertices(src_mesh_fn, mask_mesh_fn)

            for mask_vtx, head_vtx in pairs_vtx.iteritems():
                pos = om.MPoint(new_head_shape.getPoint(head_vtx, space='world'))
                mask_mesh_fn.setPoint(int(mask_vtx), pos)

            print pairs_vtx
