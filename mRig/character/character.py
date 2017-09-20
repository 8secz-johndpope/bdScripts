import pymel.core as pm
import json, inspect, pickle

from ..utils import libUtils as utils
import ast

reload(utils)

from .. import mRigGlobals as MRIGLOBALS

reload(MRIGLOBALS)

from ..utils import libCtrl as CTRL

reload(CTRL)

from ..blueprints import single as single

reload(single)

# ------- Global suffixes ------
CHAR = MRIGLOBALS.CHAR
CHBPGRP = MRIGLOBALS.CHBPGRP
CHCTRL = MRIGLOBALS.CHCTRL
CHARROOT = MRIGLOBALS.CHARROOT


# ------------------------------

class Char(object):
    def __init__(self, name, rootName='', leftString='', rightString=''):
        self.chName = name
        self.chMainController = None
        self.chBlueprintsList = []
        self.chRootName = rootName
        self.chLeftString = leftString
        self.chRightString = rightString
        self.chLinksGrp = None
        self.chInfo = {}
        # ----------Groups---------
        self.chTopGrp = None
        self.chBlueprintsGrp = None
        self.chSkeletonGrp = 'skeleton'

    def create(self):
        self.createGroups()
        self.createMainController()
        self.createRootBlueprint()
        self.addAttributes()
        self.saveCharacterInfo()

    def createGroups(self):
        pm.select(cl=1)
        self.chTopGrp = self.chName
        pm.group(name=self.chTopGrp)
        pm.select(cl=1)

        self.chBlueprintsGrp = pm.group(name=CHBPGRP)
        pm.select(cl=1)
        pm.parent(self.chBlueprintsGrp, self.chTopGrp)
        pm.select(cl=1)

        pm.group(name=self.chSkeletonGrp)
        pm.select(cl=1)

        self.chLinksGrp = pm.group(name=self.chName + '_links_grp')
        pm.parent(self.chLinksGrp, self.chTopGrp)
        pm.select(cl=1)

    def createMainController(self):
        newCtrl = CTRL.Controller(ctrlName=self.chName + '_' + CHCTRL, scale=80, ctrlType='circle')
        self.chMainController = newCtrl.buildController()
        mainControllerParent = pm.listRelatives(self.chMainController, p=1, type='transform')[
            0]  # pm.listConnections('%s.parent'%self.chMainController)[0]

        pm.parent(mainControllerParent, self.chTopGrp)
        pm.parent(self.chBlueprintsGrp, self.chMainController)
        pm.select(cl=1)

    def createRootBlueprint(self):
        if self.chRootName == '':
            self.chRootName = MRIGLOBALS.CHARROOT

        pm.select(cl=1)
        rootBp = single.SingleBlueprint(name=self.chRootName, ctrlShape='circle', parent=self.chMainController,
                                        character=self, buildInfo={"guideSize": 3})
        rootBp.create()
        self.addBlueprint(rootBp)
        pm.select(cl=1)

    def addAttributes(self):
        utils.addStringAttr(self.chTopGrp, 'name', self.chName)
        utils.addMessageAttr(self.chTopGrp, self.chMainController, 'mainController')
        utils.addMessageAttr(self.chTopGrp, self.chBlueprintsGrp, MRIGLOBALS.CHBPGRP)
        utils.addMessageAttr(self.chTopGrp, self.chBlueprintsList[0].bpTopGrp, 'rootName')

    def addBlueprint(self, blueprint):
        self.chBlueprintsList.append(blueprint)
        pm.parent(blueprint.bpTopGrp, self.chBlueprintsGrp)

    def restore(self):
        self.chTopGrp = pm.ls(self.chName)[0]
        self.chInfo = json.loads(self.chTopGrp.attr('info').get())

        messageAttr = self.chTopGrp + '.rootName'
        charRootGroup = pm.listConnections('%s' % messageAttr)[0]

        self.chRootName = charRootGroup.attr('name').get()
        self.chBlueprintsGrp = pm.ls(self.chInfo['blueprintsGrp'], type='transform')[0]
        self.chMainController = pm.ls(self.chInfo['controller'], type='transform')[0]

    def hasBlueprint(self, blueprintName):
        for bp in self.chBlueprintsList:
            if blueprintName == bp.bpName:
                return 1
        return 0

    def getSelectedBlueprint(self, bpName):
        for bp in self.chBlueprintsList:
            if bp.bpName == bpName:
                return bp

        return None

    def saveCharacterInfo(self):
        self.chInfo['name'] = self.chName
        self.chInfo['blueprintsGrp'] = str(self.chBlueprintsGrp)
        self.chInfo['controller'] = str(self.chMainController)
        self.chInfo['blueprintsList'] = [bp.bpTopGrp for bp in self.chBlueprintsList]
        strInfo = json.dumps(self.chInfo)

        if pm.attributeQuery('info', node=self.chTopGrp, ex=1):
            pm.setAttr(self.chTopGrp + '.info', l=0)
            pm.setAttr(self.chTopGrp + '.info', str(strInfo), type='string')
            pm.setAttr(self.chTopGrp + '.info', l=1)
        else:
            utils.addStringAttr(self.chTopGrp, 'info', strInfo)

    def restoreBlueprints(self, blueprintModules):
        blueprintsList = self.chInfo['blueprintsList']

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
        self.chTopGrp = pm.ls(self.chName + '_CHAR',type='transform')[0]
        self.chInfo = pickle.loads(self.chTopGrp.attr('info').get())
        
        self.chName = self.chInfo['character_name']
        
        self.chTopGrp = pm.ls(self.chInfo['character_root_group'],type='transform')[0]
        self.characterModulesGrp = pm.ls(self.chInfo['character_modules_group'],type='transform')[0]
        self.chMainController = pm.ls(self.chInfo['character_controller'],type='transform')[0]
        
        self.restoreModulesList()
        

    

    

    def addModule(self,module):
        self.characterModules.append(module)
        self.blueprintsInfo.append({'name':module.name,'type':module.moduleType})
        self.saveCharacterInfo()
        self.parentModule(module)
    
    '''
