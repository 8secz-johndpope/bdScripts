import pymel.core as pm

import blueprint as BPMAIN

reload(BPMAIN)

CLASS_NAME = 'ArmBlueprint'
BLUEPRINT_TYPE = 'arm'
DESCRIPTION = 'Arm Blueprint'
ICON = ''


class ArmBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Arm Blueprint'
        super(ArmBlueprint, self).__init__(*args, **kargs)
        # self.bpGuidesPos = {0:{'pos':[0.0,0.0,0.0]},1:{'pos':[20.0,0.0,0.0]},2:{'pos':[40.0,0.0,0.0]}}
        self.bpType = BLUEPRINT_TYPE

        self.upperRollNum = 0
        self.lowerRollNum = 0

        self.parseInfo()
        self.buildGuidesInfo()

    def parseInfo(self):
        super(ArmBlueprint, self).parseInfo()
        for info, val in self.bpInfo.iteritems():
            if info == 'upRollNum':
                self.upperRollNum = val
            if info == 'lowRollNum':
                self.lowerRollNum = val

    def buildGuidesInfo(self):
        parent = pm.ls(self.bpParent)[0]
        parentPos = parent.getTranslation(space='world')

        segmentLength = self.bpLength / 2.0

        for i in range(3):
            pos = [parentPos[0] + self.bpLength * 0.1 + segmentLength * i, parentPos[1], parentPos[2]]
            self.bpGuidesPos[i] = {'pos': pos}

    def create(self):
        print 'Creating arm module'
        super(ArmBlueprint, self).create()
