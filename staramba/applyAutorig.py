import autorig.tsgs.legSetup as legs
import autorig.biped_rig as bp
import autorig.tsgs.tongueSetup as t
import autorig.tsgs.jawSetup as j
import autorig.utils.rename_head_bs_attr as rbs

reload(bp)
reload(rbs)
reload(legs)

name='popefrancis'
root_joint = 'root_jnt'
bsDir = 'c:\\repo\\StarIsland_content\\07_Pope\\02_Model\\01_Release\\facial_bs.ma'
bsNameList = rbs.getCassandraAttrNameList()
bp.createBipedRig(name, root_joint, bsDir, bsNameList, fingerRotationAxis='z')