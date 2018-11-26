import pymel.core as pm

tongue_hor = {1: 2.2, 2: 2, 3: 1.5, 4: 1, 5: 0.5}

def add_rig(jnt, axis, ctrlName, side, attrName):
    ctrl = pm.ls(ctrlName)[0]
    # mdl = pm.shadingNode('multDoubleLinear', asUtility=1, name=jnt.name() + '_mdl')
    num_jnt = int(jnt.name().split('_')[1])

    pma = pm.shadingNode('plusMinusAverage', asUtility=1, name=jnt.name() + '_tz_pma')
    rv = pm.shadingNode('remapValue', asUtility=1, name=jnt.name() + '_tz_rv')
    rv.attr('inputMin').set(-10)
    rv.attr('inputMax').set(10)
    if side == 'left':
        rv.attr('outputMin').set(-1 * tongue_hor[num_jnt])
        rv.attr('outputMax').set(tongue_hor[num_jnt])
    elif side == 'right':
        rv.attr('outputMin').set(tongue_hor[num_jnt])
        rv.attr('outputMax').set(-1 * tongue_hor[num_jnt])
    else:
        rv.attr('outputMin').set(-1 * tongue_hor[num_jnt])
        rv.attr('outputMax').set(tongue_hor[num_jnt])

    #
    default_val = jnt.attr(axis).get()
    pma.attr('input1D[0]').set(default_val)
    rv.attr('outValue') >> pma.attr('input1D[1]')
    pma.attr('output1D') >> jnt.attr(axis)
    ctrl.attr(attrName) >> rv.attr('inputValue')

def add_roll(jnt, ctrlName, attrName ):
    ctrl = pm.ls(ctrlName)[0]
    # translate
    rv = pm.shadingNode('remapValue', asUtility=1, name=jnt.name() + '_ty_rv')
    rv.attr('inputMin').set(-10)
    rv.attr('inputMax').set(10)
    rv.attr('outputMin').set(-1)
    rv.attr('outputMax').set(1)
    ctrl.attr(attrName) >> rv.attr('inputValue')
    rv.attr('outValue') >> jnt.attr('ty')
    # rotate
    rv = pm.shadingNode('remapValue', asUtility=1, name=jnt.name() + '_rx_rv')
    rv.attr('inputMin').set(-10)
    rv.attr('inputMax').set(10)
    rv.attr('outputMin').set(-45)
    rv.attr('outputMax').set(45)
    ctrl.attr(attrName) >> rv.attr('inputValue')
    rv.attr('outValue') >> jnt.attr('rx')

def rig_tongue():
    jnt_list = pm.ls('tongue_*_left')
    for jnt in jnt_list:
        add_rig(jnt, 'tz', 'tongue_end_ctrl', 'left', 'wide_narrow')

    jnt_list = pm.ls('tongue_*_right')
    for jnt in jnt_list:
        add_rig(jnt, 'tz', 'tongue_end_ctrl', 'right', 'wide_narrow')

    jnt_list = pm.ls('tongue_*_up')
    for jnt in jnt_list:
        add_rig(jnt, 'ty', 'tongue_end_ctrl', 'left', 'thin_thick')

    jnt_list = pm.ls('tongue_*_down')
    for jnt in jnt_list:
        add_rig(jnt, 'ty', 'tongue_end_ctrl', 'right', 'thin_thick')

    side_jnt = pm.ls('tongue_*_left') + pm.ls('tongue_*_right')
    for jnt in side_jnt:
        add_roll(jnt, 'tongue_end_ctrl', 'roll')