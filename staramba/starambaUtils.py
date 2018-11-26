import pymel.core as pm
import maya.api.OpenMaya as om

def cleanRootJoint():
    pm.select('root_jnt', hi=1)
    all_under = pm.ls(sl=1)
    jnt = pm.ls(sl=1, type='joint')

    extras = list(set(all_under) - set(jnt))
    pm.delete(extras)



def connectNewBs():
    selection = pm.ls(sl=1)
    for s in selection:
        shape = s.getShape()
        shape_new = pm.ls('new_' + shape.name())[0]
        con = pm.listConnections(shape.name(), plugs=1, type='blendShape')[0]

        shape.attr('worldMesh[0]') // con
        shape_new.attr('worldMesh[0]') >> con

def connectNewBs1():
    selection = pm.ls(sl=1)
    old_bs = []
    if selection:
        for s in selection:
            shape_new = s.getShape()
            try:
                shape_old = pm.ls(shape_new.name().replace('new_', ''))[0]
            except:
                pm.warning('No old BS found for %s'%shape_new.name())
                pm.select(old_bs)
                return

            con = pm.listConnections(shape_old.name(), plugs=1, type='blendShape')[0]

            shape_old.attr('worldMesh[0]') // con
            shape_new.attr('worldMesh[0]') >> con

            # pm.delete(shape_old.getParent())
            old_bs.append(shape_old.getParent())

        pm.select(old_bs)


def createMulDiv(src, src_attr, dest, dest_attr):
    md_node = pm.shadingNode('multDoubleLinear', asUtility=1, name = dest.name() + '_' + dest_attr + '_mdl')
    src.attr(src_attr) >> md_node.input1
    md_node.output >> dest.attr(dest_attr)

def createRemapValue(src, src_attr, dest, dest_attr):
    rv_node = pm.shadingNode('remapValue', asUtility=1, name = dest.name() + '_' + dest_attr + '_rv')
    src.attr(src_attr) >> rv_node.inputValue
    rv_node.outValue >> dest.attr(dest_attr)


def connectLipJnt(pairs):
    sel = pm.ls(sl=1)
    loc = sel[0]
    jnt = sel[1]
    flc = sel[2]

    pma_translate = pm.shadingNode('plusMinusAverage', au=True)
    for p in pairs:
        loc_axis = p[0]
        jnt_axis = p[1]

def edge_to_jnt():
    selection = pm.ls(sl=1)
    vtx = pm.polyListComponentConversion(selection, fe=True, tv=1)
    pm.select(vtx)
    vtx = pm.ls(sl=1, fl=1)

def build_mask_vtx_jnt_dict(maskName):
    mask = pm.ls(maskName)[0]
    maskShape = mask.getShape()
    flc_jnt = [attr.node() for attr in pm.ls('*.face_joint')]

    pairs = {}
    if pm.nodeType(maskShape) == 'mesh':
        for i in range(maskShape.numVertices()):
            vtx_pos = om.MVector(maskShape.getPoint(i))
            for jnt in flc_jnt:
                jnt_pos = om.MVector(pm.joint(jnt, q=1, p=1, a=1 ))
                if (jnt_pos - vtx_pos).length() <= 0.001:
                    pairs[i] = jnt
                    break

def create_bnd_flc():
    flc_jnt = [attr.node() for attr in pm.ls('*.face_joint')]
    face_jnt = pm.ls('face', type='joint')[0]
    for jnt in flc_jnt:
        pm.parent(jnt, face_jnt)
        loc = jnt.getParent()
        pm.parentConstraint(loc, jnt, mo=1)

def build_mirror_dict():
    face_jnt = [attr.node() for attr in pm.ls('*.face_joint')]
    no_mid_face_jnt = []
    for jnt in face_jnt:
        pos = om.MVector(pm.joint(jnt, q=1, p=1, a=1))
        if pos.x > 0.2 or pos.x < -0.2:
            no_mid_face_jnt.append(jnt)

    face_jnt = no_mid_face_jnt

    mirror_dict = {}
    pairs = 0
    for i in range(len(face_jnt)):
        start_jnt = face_jnt[i]
        start_pos = om.MVector(pm.joint(start_jnt, q=1, p=1, a=1 ))
        for j in range(i+1, len(face_jnt)):
            jnt = face_jnt[j]
            jnt_pos = om.MVector(pm.joint(jnt, q=1, p=1, a=1 ))
            mid = (start_pos + jnt_pos) * 0.5
            if -0.001 <= mid.x <= 0.001:
                if jnt_pos.x > 0:
                    mirror_dict[pairs] = [jnt, start_jnt]
                elif jnt_pos.x < 0:
                    mirror_dict[pairs] = [start_jnt, jnt]
                pairs += 1
                # face_jnt.remove(jnt)
                # face_jnt.remove(start_jnt)
                break

    return mirror_dict

def mirror_names():
    mirror_dict = build_mirror_dict()
    for pairs in mirror_dict.itervalues():
        left_jnt = pairs[0]
        left_jnt.rename('left_' + left_jnt.name())
        right_jnt = pairs[1]
        right_jnt.rename(left_jnt.name().replace('left', 'right'))
        print pairs
        # pm.rename(right_jnt, left_jnt.name().replace('left', 'right'))


def create_sticky_locs():
    '''
    Select the follicle locators for the lips
    :return:
    '''
    lips_jnt = [attr.node() for attr in pm.ls('*.face_joint') if attr.get() == 'stickylip']

    sticky_locs_list = []
    for jnt in lips_jnt:
        cnstr = pm.listRelatives(jnt, type='parentConstraint')[0]
        flc_loc = pm.parentConstraint(cnstr, q=1, tl=1)[0]
        sticky_loc = pm.duplicate(flc_loc, name='sticky_' + flc_loc.name())
        sticky_locs_list.append(sticky_loc)
        pm.parent(sticky_loc, world=True)

    return sticky_locs_list

def constraint_to_sticky():
    lips_jnt = [attr.node() for attr in pm.ls('*.face_joint') if attr.get() == 'stickylip']

    for jnt in lips_jnt:
        cnstr = pm.listRelatives(jnt, type='parentConstraint')[0]
        flc_loc = pm.parentConstraint(cnstr, q=1, tl=1)[0]
        sticky_loc = pm.ls('sticky_' + flc_loc.name())[0]
        pm.parentConstraint(sticky_loc, jnt, mo=1, w=0)


def toggle_sticky():
    lips_jnt = [attr.node() for attr in pm.ls('*.face_joint') if attr.get() == 'stickylip']
    for jnt in lips_jnt:
        cnstr = pm.listRelatives(jnt, type='parentConstraint')[0]
        params = pm.parentConstraint(cnstr, q=1, wal=1)
        if params[0].get() == 1:
            params[0].set(0)
            params[1].set(1)
        else:
            params[0].set(1)
            params[1].set(0)

def set_attr(attr, val):
    selection = pm.ls(sl=1)

    for jnt in selection:
        pm.setAttr(jnt.name() + attr, val)



def create_face_jnt_drv():
    '''
    duplicates the face joints
    :return:
    '''
    face_jnt = [attr.node() for attr in pm.ls('*.face_joint')]
    for jnt in face_jnt:
        jnt_drv = pm.duplicate(jnt,name=jnt.name() + '_face_drv', po=1)
        pm.parent(jnt_drv, w=1)


def connect_face_jnt_drv():
    '''
    Parent constraint the face driver face joints to the zero locators under the follicles
    :return:
    '''
    face_jnt = [attr.node() for attr in pm.ls('*.face_joint')]
    for jnt in face_jnt:
        cnstr = pm.listRelatives(jnt, type='parentConstraint')[0]
        flc_loc = pm.parentConstraint(cnstr, q=1, tl=1)[0]

        jnt_drv = pm.ls(jnt.name() + '_face_drv')[0]
        pm.parentConstraint(flc_loc, jnt_drv, mo=1)


def drive_face_jnt():
    '''
    direct connections between the driver joints and the face joints
    :return:
    '''
    face_jnt = [attr.node() for attr in pm.ls('*.face_joint')]
    for jnt in face_jnt:
        face_loc = pm.ls(jnt.name() + '_face_drv')[0]

        face_loc.tx >> jnt.tx
        face_loc.ty >> jnt.ty
        face_loc.tz >> jnt.tz

        face_loc.rx >> jnt.rx
        face_loc.ry >> jnt.ry
        face_loc.rz >> jnt.rz



def tongue_globals():
    tongue_end_ctrl = pm.ls('tongue_end_ctrl', type='transform')[0]
    tongue_config_ctrl = pm.ls('tongue_config', type='transform')[0]

    wide_narrow_nodes = pm.listConnections(tongue_end_ctrl.name() + '.wide_narrow')
    pma = pm.shadingNode('plusMinusAverage', name='wide_narrow_config_pma', asUtility=True)
    tongue_end_ctrl.attr('wide_narrow') >> pma.attr('input1D[0]')
    tongue_config_ctrl.attr('wide_narrow') >> pma.attr('input1D[1]')
    for node in wide_narrow_nodes:
        tongue_end_ctrl.attr('wide_narrow') // node.attr('inputValue')
        pma.attr('output1D') >> node.attr('inputValue')

    thin_thick_nodes = pm.listConnections(tongue_end_ctrl.name() + '.thin_thick')
    pma = pm.shadingNode('plusMinusAverage', name='thin_thick_config_pma', asUtility=True)
    tongue_end_ctrl.attr('thin_thick') >> pma.attr('input1D[0]')
    tongue_config_ctrl.attr('thin_thick') >> pma.attr('input1D[1]')
    for node in thin_thick_nodes:
        tongue_end_ctrl.attr('thin_thick') // node.attr('inputValue')
        pma.attr('output1D') >> node.attr('inputValue')