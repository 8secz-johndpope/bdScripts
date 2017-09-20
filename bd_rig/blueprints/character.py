import pymel.core as pm
import json
import single as single
from ..utils import libControllers as CTRL
from ..utils import libUtils as utils
from .. import mRigGlobals as MRIGLOBALS
reload(utils)
reload(MRIGLOBALS)
reload(CTRL)
reload(single)

# ------- Global suffixes ------
CHAR = MRIGLOBALS.CHAR
CHBPGRP = MRIGLOBALS.CHBPGRP
CHCTRL = MRIGLOBALS.CHCTRL
CHARROOT = MRIGLOBALS.CHARROOT
# ------------------------------


class Char(object):
    def __init__(self, name, leftString='', rightString=''):
        self.ch_name = name
        self.ch_main_ctrl = None
        self.ch_bp_list = []
        # self.ch_root_name = rootName
        self.ch_left_str = leftString
        self.ch_right_str = rightString
        self.ch_links_grp = None
        self.ch_info = {}
        # ----------Groups---------
        self.ch_top_grp = None
        self.ch_bp_grp = None
        self.ch_skeleton_grp = 'skeleton'

    def create(self):
        self.createGroups()
        self.createMainController()
        # self.createRootBlueprint()
        self.addAttributes()
        self.saveCharacterInfo()

    def createGroups(self):
        pm.select(cl=1)
        self.ch_top_grp = self.ch_name
        pm.group(name=self.ch_top_grp)
        pm.select(cl=1)

        self.ch_bp_grp = pm.group(name=CHBPGRP)
        pm.select(cl=1)
        pm.parent(self.ch_bp_grp, self.ch_top_grp)
        pm.select(cl=1)

        pm.group(name=self.ch_skeleton_grp)
        pm.select(cl=1)

        self.ch_links_grp = pm.group(name=self.ch_name + '_links_grp')
        pm.parent(self.ch_links_grp, self.ch_top_grp)
        pm.select(cl=1)

    def createMainController(self):
        self.ch_main_ctrl = self.ch_name + '_' + CHCTRL
        ctrl = CTRL.Controller(name=self.ch_main_ctrl, scale=80, ctrlType='circle')
        ctrl.buildController()
        ctrl_parent = pm.listRelatives(self.ch_main_ctrl, p=1, type='transform')[0]

        pm.parent(ctrl_parent, self.ch_top_grp)
        pm.parent(self.ch_bp_grp, self.ch_main_ctrl)
        pm.select(cl=1)

    def createRootBlueprint(self):
        if self.ch_root_name == '':
            self.ch_root_name = MRIGLOBALS.CHARROOT

        pm.select(cl=1)
        rootBp = single.SingleBlueprint(name=self.ch_root_name, ctrlShape='circle', parent=self.ch_main_ctrl,
                                        character=self, buildInfo={"guideSize": 3})
        rootBp.create()
        self.addBlueprint(rootBp)
        pm.select(cl=1)

    def addAttributes(self):
        utils.addStringAttr(self.ch_top_grp, 'name', self.ch_name)
        utils.addMessageAttr(self.ch_top_grp, self.ch_main_ctrl, 'mainController')
        utils.addMessageAttr(self.ch_top_grp, self.ch_bp_grp, MRIGLOBALS.CHBPGRP)
        # utils.addMessageAttr(self.ch_top_grp, self.ch_bp_list[0].bpTopGrp, 'rootName')

    def addBlueprint(self, blueprint):
        self.ch_bp_list.append(blueprint)
        pm.parent(blueprint.bpTopGrp, self.ch_bp_grp)

    def restore(self):
        self.ch_top_grp = pm.ls(self.ch_name)[0]
        self.ch_info = json.loads(self.ch_top_grp.attr('info').get())

        messageAttr = self.ch_top_grp + '.rootName'
        charRootGroup = pm.listConnections('%s' % messageAttr)[0]

        self.ch_root_name = charRootGroup.attr('name').get()
        self.ch_bp_grp = pm.ls(self.ch_info['blueprintsGrp'], type='transform')[0]
        self.ch_main_ctrl = pm.ls(self.ch_info['controller'], type='transform')[0]

    def hasBlueprint(self, blueprintName):
        for bp in self.ch_bp_list:
            if blueprintName == bp.bpName:
                return 1
        return 0

    def getSelectedBlueprint(self, bpName):
        for bp in self.ch_bp_list:
            if bp.bpName == bpName:
                return bp

        return None

    def saveCharacterInfo(self):
        self.ch_info['name'] = self.ch_name
        self.ch_info['blueprintsGrp'] = str(self.ch_bp_grp)
        self.ch_info['controller'] = str(self.ch_main_ctrl)
        self.ch_info['blueprintsList'] = [bp.bpTopGrp for bp in self.ch_bp_list]
        strInfo = json.dumps(self.ch_info)

        if pm.attributeQuery('info', node=self.ch_top_grp, ex=1):
            pm.setAttr(self.ch_top_grp + '.info', l=0)
            pm.setAttr(self.ch_top_grp + '.info', str(strInfo), type='string')
            pm.setAttr(self.ch_top_grp + '.info', l=1)
        else:
            utils.addStringAttr(self.ch_top_grp, 'info', strInfo)

    def restoreBlueprints(self, blueprintModules):
        blueprintsList = self.ch_info['blueprintsList']

        if len(blueprintsList):
            for bp in blueprintsList:
                bpTopGrp = pm.ls(bp)[0]
                bpName = bpTopGrp.attr('name').get()
                bpParent = bpTopGrp.attr('parent').get()
                bpType = bpTopGrp.attr('type').get()
                bpInfo = ast.literal_eval(bpTopGrp.attr('info').get())

                bpClass = self.restoreBpClass(blueprintModules, bpType)

                bpRestored = bpClass(name=bpName, parent=bpParent, buildInfo=bpInfo, character=self)
                bpRestored.restore()
                self.addBlueprint(bpRestored)

    @staticmethod
    def restoreBpClass(blueprintModules, bpType):
        mod = blueprintModules[bpType]
        blueprintClass = getattr(mod, mod.CLASS_NAME)

        if blueprintClass:
            return blueprintClass
        else:
            return "Failed getting the restored blueprint class!!!"

    '''
    def parentModule(self,newModule):
        pm.parent(newModule.moduleGrp,self.characterModulesGrp)
        if newModule == self.characterRootModule:
            pm.select(cl=1)
        else:
            pm.select(newModule.moduleCtrl)
        
    def restoreCharacter(self):
        self.ch_top_grp = pm.ls(self.ch_name + '_CHAR',type='transform')[0]
        self.ch_info = pickle.loads(self.ch_top_grp.attr('info').get())
        
        self.ch_name = self.ch_info['character_name']
        
        self.ch_top_grp = pm.ls(self.ch_info['character_root_group'],type='transform')[0]
        self.characterModulesGrp = pm.ls(self.ch_info['character_modules_group'],type='transform')[0]
        self.ch_main_ctrl = pm.ls(self.ch_info['character_controller'],type='transform')[0]
        
        self.restoreModulesList()
        

    

    

    def addModule(self,module):
        self.characterModules.append(module)
        self.blueprintsInfo.append({'name':module.name,'type':module.moduleType})
        self.saveCharacterInfo()
        self.parentModule(module)
    
    '''
