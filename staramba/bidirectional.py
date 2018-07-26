import pymel.core as pm


def add_attr(obj):
    pm.addAttr(obj,ln="space", at="enum", en=["global", "rig"])


def add_global(obj):
    decompose_mat = pm.createNode('decomposeMatrix', name = obj.name() + '_to_global')


def connect():
    selection = pm.ls(sl=1)
    if selection:
        for obj in selection:
            add_attr(obj)
            add_global(obj)

