import pymel.core as pm
import bdScripts.utils.libRig as lr


def select_all():
    facial_ctrls = []
    facial_box_ctrls = []
    body_ctrls = []

    vis_curves_shapes = pm.ls(type='nurbsCurve')
    vis_curves = [shape.getParent() for shape in vis_curves_shapes]
    for ctrl in vis_curves:
        if ctrl.hasAttr('ctrl_type'):
            if ctrl.attr('ctrl_type').get() == 'facial_ctrl':
                facial_ctrls.append(ctrl.name())
            if ctrl.attr('ctrl_type').get() == 'body_ctrl':
                body_ctrls.append(ctrl.name())
            if ctrl.attr('ctrl_type').get() == 'facial_box_ui':
                facial_box_ctrls.append(ctrl.name())

    facial_box_ctrls.sort()
    facial_ctrls.sort()
    body_ctrls.sort()

    pm.select(facial_box_ctrls + facial_ctrls + body_ctrls)

def get_anim_layer():
    al_list = pm.ls(type='animLayer')
    anim_layers = []
    for layer in al_list:
        attr_list = layer.getAttributes()
        if len(attr_list):
            obj_list = []
            for attr in attr_list:
                obj = attr.info().split('.')[0]
                obj_list.append(obj)
            obj_list = list(set(obj_list))
            anim_layers.append([layer.name(), obj_list])

    return anim_layers


def restore_anim(from_file, to_file):
    fbx_rig = 'c:\\repo\\StarIsland_content\\06_TimoBoll\\07_Rig\\00_TimoBoll\\01_Release\\timoboll_fbxOn_rig.ma'
    pm.openFile(from_file, force=1)
    anim_layers_data = get_anim_layer()
    anim_layers = [item[0] for item in anim_layers_data]


    start_frame = pm.playbackOptions(q=1, min=1)
    end_frame = pm.playbackOptions(q=1, max=1)

    ###### Copy mocap
    pm.select('root_jnt')
    lr.bdSelectHierarchyJnt()
    pm.copyKey()

    pm.openFile(fbx_rig, force=1)
    start_frame = pm.playbackOptions(min=start_frame)
    end_frame = pm.playbackOptions(max=end_frame)
    pm.currentTime(0)

    pm.select('root_jnt')
    lr.bdSelectHierarchyJnt()
    pm.pasteKey()
    pm.saveAs(to_file)

    select_all()
    pm.copyKey()


    ##Copy Base Anim
    pm.openFile(from_file, force=1)
    set_active_layer('BaseAnimation')
    select_all()
    pm.copyKey()

    pm.openFile(to_file, force=1)
    start_frame = pm.playbackOptions(min=start_frame)
    end_frame = pm.playbackOptions(max=end_frame)
    pm.currentTime(start_frame)

    select_all()
    pm.setKeyframe()
    pm.pasteKey()

    pm.saveFile()
    # for data in anim_layers_data:
    #     pm.openFile(from_file, f=1)
    #     layer = data[0]
    #     obj_layer = data[1]
    #
    #     set_active_layer(layer)
    #     pm.select(obj_layer)
    #     pm.copyKey()
    #
    #     pm.openFile(to_file, force=1)
    #     pm.animLayer(layer)
    #     set_active_layer(layer)
    #     pm.select(obj_layer)
    #     pm.animLayer(layer, e=1, addSelectedObjects=1)
    #     try:
    #         pm.pasteKey()
    #     except:
    #         print('---------------------------------WTF--------------------------------------------')
    #     pm.saveFile()
    #
    # all = [obj.name() for obj in pm.ls(type='animLayer')]
    # for item in all:
    #     pm.animLayer(item, e=1, selected=0, lock=0)


def set_active_layer(layer):
    all = [obj.name() for obj in pm.ls(type='animLayer')]
    for item in all:
        if item == layer:
            pm.animLayer(item, e=1, selected=1, lock=0)
        else:
            pm.animLayer(item, e=1, selected=0, lock=1)




#from_file = 'c:\\repo\\StarIsland_content\\06_TimoBoll\\09_Animation\\00_Export\\test\\Starspace Emotions\\need_to_manual_fix\\A_TBO_EmotionAcheer1_Std_T_Idle_001.ma'
from_file = 'c:\\repo\\StarIsland_content\\06_TimoBoll\\09_Animation\\00_Export\\test\\Starspace Emotions\\need_to_manual_fix\\A_TBO_EmotionAcheer1_Std_T_Idle_001.ma'
to_file = 'c:\\repo\\StarIsland_content\\06_TimoBoll\\09_Animation\\00_Export\\test\\Starspace Emotions\\fixed\\A_TBO_EmotionAcheer1_Std_T_Idle_001.ma'

restore_anim(from_file, to_file)