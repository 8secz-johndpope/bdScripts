import pymel.core as pm

import guide

reload(guide)
from guide import Guide

import skeleton

reload(skeleton)
from skeleton import Skeleton

import bdRig.utils.utils as utils

reload(utils)

import pickle


class Module(object):
    def __init__(self, *args, **kargs):
        # moduleRebuildInfo - dictionary holding all the data for a module, needed for re-building. 
        self.moduleRebuildInfo = {}
        # moduleGrp - top group for the module
        self.moduleGrp = None
        # moduleCtrl - the transform of the module controller
        self.moduleCtrl = None
        self.moduleCtrlGrp = None
        # moduleGuidesGrp - transform group for all the guides
        self.moduleGuidesGrp = None
        # moduleConnectionsGrp - transform group for all the curves connecting the guides
        self.moduleConnectionsGrp = None
        # moduleGuides - list of objects holding the Guides 
        self.moduleGuides = []
        # moduleGuidesNames - list of strings holding the Guides objects names
        self.moduleGuidesNames = {}
        # moduleGuidesData - dict holding information per module for building the guides , initialized in the child classes
        self.moduleGuidesData = {}
        # moduleType - string holding the name of the module to be built, has to be identical to the python file name containing the class for it
        self.moduleType = ''
        # moduleSkeleton - object holding the Skeleton
        self.moduleSkeleton = None
        # moduleJntCrv - the joints will be created along this curve at its points
        self.moduleJntCrv = ''

        self.name = kargs.setdefault('name', '')
        self.mirror = kargs.setdefault('mirror', 0)
        self.moduleParent = kargs.setdefault('module_parent', None)
        self.nCtrl = kargs.setdefault('nCtrl', 1)
        self.spaceSwitch = kargs.setdefault('spaceSwitch', 0)
        self.jointOrient = kargs.setdefault('jointOrient', 'xyz')
        self.color = kargs.setdefault('color', [1, 1, 0])
        self.position = kargs.setdefault('position', [0, 0, 0])

    #  ---------------------------------------------------------------------CREATION-------------------------------------------------------------------------------#
    '''
    @decorators.undoable
    def createModule(self):
        #print 'Building module %s'%self.name
        self.createGroups()
        #print 'Groups created'
        self.createGuides()
        #print 'Guides created'
        #self.saveModuleInfo()
        #pm.select(self.moduleCtrl)
    '''

    def createGroups(self):
        pm.select(cl=1)
        self.moduleGrp = pm.group(name=self.name + '_module')
        pm.select(cl=1)
        self.moduleGuidesGrp = pm.group(name=self.name + '_guides_grp')
        pm.parent(self.moduleGuidesGrp, self.moduleGrp)
        pm.select(cl=1)
        self.moduleConnectionsGrp = pm.group(name=self.name + '_connections_grp')
        pm.parent(self.moduleConnectionsGrp, self.moduleGrp)
        pm.select(cl=1)

    def createGuides(self):
        prevGuide = None
        jntCrvPoints = []
        if self.moduleGuidesData:
            for i in range(len(self.moduleGuidesData)):
                guide = Guide(name=self.name + '_' + self.moduleGuidesData[i]['name'], moduleParent=self.name)
                guide.drawGuide()
                if self.moduleGuidesData[i]['orient']:
                    guide.setOrientGuide(self.moduleGuidesData[i]['orient'])

                pos = self.moduleGuidesData[i]['pos']
                jntCrvPoints.append(pos)
                if i == 0:
                    self.moduleCtrl, self.moduleCtrlGrp = utils.buildBoxController(guide.name, self.name + '_ctrl', 2)
                    pm.parent(self.moduleCtrlGrp, self.moduleGrp)
                    pm.parent(self.moduleGuidesGrp, self.moduleCtrl)
                guide.setPos(pos)
                self.addGuide(guide)

                if i > 0:
                    connectionGrp = prevGuide.drawConnectionTo(guide)
                    pm.parent(connectionGrp, self.moduleConnectionsGrp)

                prevGuide = guide
                self.moduleGuidesNames[i] = guide.name

            self.moduleCtrlGrp.setTranslation(self.position, space='world')

    # -------------------------------------------------------------------SAVE MODULE INFO ---------------------------------------------------------------------------#
    def saveModuleInfo(self):
        self.moduleRebuildInfo['module_group'] = self.moduleGrp.name()
        self.moduleRebuildInfo['module_guides_group'] = self.moduleGuidesGrp.name()
        self.moduleRebuildInfo['module_connections_group'] = self.moduleConnectionsGrp.name()
        self.moduleRebuildInfo['module_guides_names'] = self.moduleGuidesNames
        self.moduleRebuildInfo['module_parent'] = 'Skeleton_Root'
        # Be aware that pickle converts everything to strings
        saveInfo = pickle.dumps(self.moduleRebuildInfo)

        if pm.attributeQuery('moduleInfo', node=self.moduleGrp.name(), ex=True):
            pm.setAttr(self.moduleGrp.name() + '.moduleInfo', str(strInfo), type='string')
        else:
            utils.addStringAttr(self.moduleGrp, 'moduleInfo', saveInfo)

    # -------------------------------------------------------------------RESTORE MODULE ---------------------------------------------------------------------------#
    def restoreModule(self):
        self.moduleGrp = pm.ls(self.name + '_module')[0]
        self.moduleRebuildInfo = pickle.loads(self.moduleGrp.attr('moduleInfo').get())
        self.moduleGuidesNames = self.moduleRebuildInfo['module_guides_names']
        self.moduleParent = self.moduleRebuildInfo['module_parent']

        for k, guideName in self.moduleGuidesNames.iteritems():
            restoreGuide = guide.Guide(name=guideName)
            restoreGuide.restoreGuide()
            self.moduleGuides.append(restoreGuide)

    def getGuideByName(self, name):
        for guide in self.moduleGuides:
            if name == guide.name:
                return guide
        return None

    def parentGuide(self, guide):
        pm.select(cl=1)
        pm.parent(guide.guideGrp, self.moduleGuidesGrp)
        pm.select(cl=1)

    def addGuide(self, guide):
        pm.select(cl=1)
        self.parentGuide(guide)
        self.moduleGuides.append(guide)

        # add message attributes
        '''
        attrName = 'guide_' + (str(i)).zfill(2) 
        pm.addAttr(self.moduleCtrl,ln=attrName,at='message')
        guide.transform.message.connect( self.moduleCtrl.attr(attrName))
        '''

    def insertGuidePos(self, guide, atPos):
        leftSide = {}
        insert = {atPos: guide.name}
        rightSide = {}
        for i in range(len(self.moduleGuidesNames)):
            if i < atPos:
                leftSide[i] = self.moduleGuidesNames[i]
            else:
                rightSide[i + 1] = self.moduleGuidesNames[i]

        temp = dict(leftSide, **insert)
        temp.update(rightSide)

        self.moduleGuidesNames = temp

    def setModuleParent(self, parent):
        pass

    def buildSkeleton(self):
        self.moduleSkeleton = Skeleton(module=self)
        self.moduleSkeleton.build()
