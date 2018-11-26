import pymel.core as pm

left_thigh = pm.ls('anim_l_thigh')[0]
right_thigh = pm.ls('anim_r_thigh')[0]

def rig_mid_front():
    mid_0 = pm.ls('anim_mid_front_tshirt_0')[0]
    val = mid_0.attr('tx').get()
    rv_1 = create_rv_node(left_thigh,'ry', mid_0, 'tx')
    rv_1.inputMax.set(-90)
    rv_1.outputMin.set(val)
    rv_1.outputMax.set(val + 4)

    mid_1 = pm.ls('anim_mid_front_tshirt_1')[0]
    md_1 = create_md_node(left_thigh, mid_1, 'rotate')
    md_1.input2Y.set(0.2)

    mid_2 = pm.ls('anim_mid_front_tshirt_2')[0]
    md_2 = create_md_node(left_thigh, mid_2, 'rotate')
    md_2.input2Y.set(0.2)

def rig_left_front():
    mid_0 = pm.ls('anim_front_l_tshirt_0')[0]
    val = mid_0.attr('tx').get()
    rv_1 = create_rv_node(left_thigh,'ry', mid_0, 'tx')
    rv_1.inputMax.set(-90)
    rv_1.outputMin.set(val)
    rv_1.outputMax.set(val + 10)
    md_0 =  create_md_node(left_thigh, mid_1, 'rotate')


    mid_1 = pm.ls('anim_front_l_tshirt_1')[0]
    md_1 = create_md_node(left_thigh, mid_1, 'rotate')
    md_1.input2Y.set(0.6)

    mid_2 = pm.ls('anim_front_l_tshirt_2')[0]
    md_2 = create_md_node(left_thigh, mid_2, 'rotate')
    md_2.input2Y.set(0.5)


def rig_left():
    # mid_0 = pm.ls('anim_l_tshirt_1')[0]
    # val = mid_0.attr('tx').get()
    # rv_1 = create_rv_node(left_thigh,'ry', mid_0, 'tx')
    # rv_1.inputMax.set(-90)
    # rv_1.outputMin.set(val)
    # rv_1.outputMax.set(val + 7)

    mid_1 = pm.ls('anim_l_tshirt_1')[0]
    md_1 = create_md_node(left_thigh, mid_1, 'rotate')
    md_1.input2Y.set(0.8)

    mid_2 = pm.ls('anim_l_tshirt_2')[0]
    md_2 = create_md_node(left_thigh, mid_2, 'rotate')
    md_2.input2Y.set(-0.5)


def rig_tshirt():
    rig_mid_front()
    rig_left_front()
    rig_left()


def create_md_node(src, dest, attr):
    md_node = pm.shadingNode('multiplyDivide', asUtility=1, name=dest.name() + '_rot_md')
    src.attr(attr) >> md_node.input1
    md_node.output >> dest.attr(attr)

    return md_node


def create_rv_node(src, src_attr, dest, dest_attr):
    rv_node = pm.shadingNode('remapValue', asUtility=1, name=dest.name() + '_' + dest_attr + '_rv')
    src.attr(src_attr) >> rv_node.inputValue
    rv_node.outValue >> dest.attr(dest_attr)

    return rv_node