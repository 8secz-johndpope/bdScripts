import pymel.core as pm


def cleanRootJoint():
    pm.select('root_jnt', hi=1)
    all_under = pm.ls(sl=1)
    jnt = pm.ls(sl=1, type='joint')

    extras = list(set(all_under) - set(jnt))
    pm.delete(extras)


def connectNewBs():
    selection = pm.ls(sl=1)
    targets_old = []
    targets_new = []
    for s in selection:
        shape = s.getShape()
        shape_new = pm.ls('new_' + shape.name())[0]
        con = pm.listConnections(shape.name(), plugs=1, type='blendShape')[0]

        shape.attr('worldMesh[0]') // con
        shape_new.attr('worldMesh[0]') >> con


def createMulDiv(src, src_attr, dest, dest_attr):
    md_node = pm.shadingNode('multDoubleLinear', asUtility=1, name = dest.name() + '_' + dest_attr + '_mdl')
    src.attr(src_attr) >> md_node.input1
    md_node.output >> dest.attr(dest_attr)

def createRemapValue(src, src_attr, dest, dest_attr):
    rv_node = pm.shadingNode('remapValue', asUtility=1, name = dest.name() + '_' + dest_attr + '_rv')
    src.attr(src_attr) >> rv_node.inputValue
    rv_node.outValue >> dest.attr(dest_attr)



