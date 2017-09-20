import pymel.core as pm
import json, inspect, pickle

from ..modules import single as single

reload(single)

import bdRig.utils.utils as utils

reload(utils)

import module as module

reload(module)

import guide as guide

reload(guide)


class CharacterX(object):
    def __init__(self, name):
        self.characterName = str(name)
        self.characterCtrl = ''
        self.characterModulesInfo = []
        self.characterInfo = {}
        self.characterRootGrp = None
        self.characterModulesGrp = None
        self.characterRootModule = None
        self.characterModules = []
        self.characterSkeletonGrp = None
        # self.bpModelGrp = None
        # self.bdSkeletonGrp = None

    def createCharacterX(self):
        self.createGroups()
        self.createMainController()
        self.createRootModule()
        self.saveCharacterInfo()

    def createGroups(self):
        pm.select(cl=1)
        self.characterRootGrp = pm.group(name=self.characterName + '_CHAR')
        pm.select(cl=1)
        self.characterModulesGrp = pm.group(name=self.characterName + '_modules_grp')
        pm.select(cl=1)
        pm.parent(self.characterModulesGrp, self.characterRootGrp)
        pm.select(cl=1)
        self.characterSkeletonGrp = pm.group(name='skeleton')
        pm.select(cl=1)

    def createMainController(self):
        self.characterCtrl, grp = utils.buildCircleController(ctrlName=self.characterName + '_character_ctrl', scale=10)
        pm.parent(grp, self.characterRootGrp)
        pm.parent(self.characterModulesGrp, self.characterCtrl)

    def createRootModule(self):
        pm.select(cl=1)
        rootModule = single.SingleModule(name=self.characterName + '_Skeleton_Root')
        rootModule.moduleGuidesData = {0: {'name': 'Guide', 'pos': [0, 0, 0], 'orient': 0}}
        rootModule.createModule()
        rootModule.saveModuleInfo()
        ctrlShape = rootModule.moduleCtrl.getShape()
        ctrlShape.visibility.set(0)
        skRootGuide = rootModule.moduleGuides[0]
        skRootGuide.transform.overrideColor.set(17)

        self.characterRootModule = rootModule
        self.parentModule(rootModule)
        pm.select(cl=1)

    def parentModule(self, newModule):
        pm.parent(newModule.moduleGrp, self.characterModulesGrp)
        if newModule == self.characterRootModule:
            pm.select(cl=1)
        else:
            pm.select(newModule.moduleCtrl)

    def restoreCharacter(self):
        self.characterRootGrp = pm.ls(self.characterName + '_CHAR', type='transform')[0]
        self.characterInfo = pickle.loads(self.characterRootGrp.attr('characterInfo').get())

        self.characterName = self.characterInfo['character_name']

        self.characterRootGrp = pm.ls(self.characterInfo['character_root_group'], type='transform')[0]
        self.characterModulesGrp = pm.ls(self.characterInfo['character_modules_group'], type='transform')[0]
        self.characterCtrl = pm.ls(self.characterInfo['character_controller'], type='transform')[0]

        self.restoreModulesList()

    def restoreModulesList(self):
        rootModuleInfo = self.characterInfo['character_root_module_info']
        rootModuleName = rootModuleInfo['name']
        rootModuleType = rootModuleInfo['type']
        moduleClass = self.restoreModuleClass(rootModuleType)
        self.characterRootModule = moduleClass(name=rootModuleName)
        self.characterRootModule.restoreModule()

        self.characterModulesInfo = self.characterInfo['character_modules_info']
        for mod in self.characterModulesInfo:
            moduleName = mod['name']
            moduleType = mod['type']
            moduleClass = self.restoreModuleClass(moduleType)
            restoredModule = moduleClass(name=moduleName)
            restoredModule.restoreModule()
            self.characterModules.append(restoredModule)

    def restoreModuleClass(self, moduleType):
        moduleName = moduleType
        toImport = 'bdRig.modules.' + moduleName

        try:
            mod = __import__(toImport, {}, {}, [moduleName])
            reload(mod)
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    if 'UI' not in obj.__name__:
                        return obj
        except:
            pm.error("Did not find any modules")

    def saveCharacterInfo(self):

        self.characterInfo['character_name'] = self.characterName
        self.characterInfo['character_root_module_info'] = {'name': self.characterRootModule.name,
                                                            'type': self.characterRootModule.moduleType}
        self.characterInfo['character_root_group'] = self.characterRootGrp.name()
        self.characterInfo['character_modules_group'] = self.characterModulesGrp.name()
        self.characterInfo['character_controller'] = self.characterCtrl.name()
        self.characterInfo['character_modules_info'] = self.characterModulesInfo
        strInfo = pickle.dumps(self.characterInfo)

        if pm.attributeQuery('characterInfo', node=self.characterRootGrp.name(), ex=1):
            pm.setAttr(self.characterRootGrp.name() + '.characterInfo', str(strInfo), type='string')
        else:
            utils.addStringAttr(self.characterRootGrp, 'characterInfo', strInfo)

    def listCharacterInfo(self):
        pass

    def addModule(self, module):
        self.characterModules.append(module)
        self.characterModulesInfo.append({'name': module.name, 'type': module.moduleType})
        self.saveCharacterInfo()
        self.parentModule(module)
