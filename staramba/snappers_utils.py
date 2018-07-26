import pymel.core as pm
import bdScripts.utils.mayaDecorators as deco

@deco.undoable
def create_skeleton():
    root_ori = pm.ls('Adjustment_layer')[0]
    pm.select(cl=1)
    root_jnt = pm.joint(name = 'root')
    children = pm.listRelatives(root_ori)
    for child in children:
        pm.select(cl=1)
        if child.getChildren():
            jnt = pm.joint(name=child.getChildren()[0].name())
            pm.parent(jnt, root_jnt)
            pm.parentConstraint(child.getChildren()[0], jnt, mo=0)
            # pm.parentConstraint(child.getChildren()[0], jnt, rm=1)


