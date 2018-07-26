import pymel.core as pm
import utils.libRig as libRig


def mirrorRig(side):
    selection = pm.ls(sl=1)
    if len(selection):
        anim_root = selection[0]
        parent_anim_root = anim_root.getParent()
        name = anim_root.name().replace(side + '_', 'r_')
        dup = None
        if side == 'l':
            dup = pm.duplicate()
            pm.parent(dup, 'anim_spine4')
            mirrored = pm.mirrorJoint(mirrorYZ=1, mirrorBehavior=1, searchReplace=("l_", "r_"))
            search = pm.ls(parent_anim_root.name().replace('l_', 'r_'))
            if len(search):
                pm.parent(mirrored[0], search[0])
                pm.delete(dup)
                pm.rename(mirrored[0], name)
                mirrorNodes(anim_root, side)
        elif side == 'r':
            # implement
            pass
        # mirrorJoint -mirrorYZ -mirrorBehavior -searchReplace "l_" "r_";


def mirrorNodes(anim_root, side):
    children = pm.listRelatives(anim_root, type='joint', ad=1)
    children.reverse()
    if len(children):
        chain = [anim_root] + children
        for jnt in chain:
            connections = pm.listConnections(jnt, c=1, scn=1, d=0, s=1)
            plugs = pm.listConnections(jnt, p=1, scn=1, d=0, s=1)
            i = 0
            for dest, src in connections:
                if side == 'l':
                    if src.type() == 'remapValue' or src.type() == 'multDoubleLinear':
                        mirrored_rig_node = pm.duplicate(src, name=src.name().replace('l_', 'r_'))[0]
                        src_attr = plugs[i].split('.')[1]
                        dest, dest_attr = dest.split('.')
                        mirrored_dest = pm.ls(dest.replace('l_', 'r_'))[0]
                        mirrored_rig_node.attr(src_attr) >> mirrored_dest.attr(dest_attr)
                        # print mirrored_rig_node
                        # print src.type() + '  -------  ' + dest
                        # print plugs[i]
                        # print src_attr
                        rig_node_connections = pm.listConnections(src, c=1, scn=1, d=0, s=1)
                        rig_node_plugs = pm.listConnections(src, p=1, scn=1, d=0, s=1)
                        j=0
                        for rig_node_dest, rig_node_src in rig_node_connections:
                            print rig_node_dest + ' ------------ '+ rig_node_src
                            print rig_node_plugs[j]
                            mirror_rig_node_src = pm.ls(rig_node_src.name().replace('l_', 'r_'))[0]
                            src_attr = rig_node_plugs[j].split('.')[1]
                            dest_attr = rig_node_dest.split('.')[1]
                            mirror_rig_node_src.attr(src_attr) >> mirrored_rig_node.attr(dest_attr)
                            j += 1
                    i += 1


def constraintAnimToBnd():
    selection = pm.ls(sl=1)
    for bnd in selection:
        find = pm.ls('anim_' + bnd.name())
        if find:
            anim = find[0]
            pm.parentConstraint(anim, bnd, mo=1)



