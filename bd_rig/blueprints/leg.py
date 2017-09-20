import pymel.core as pm

import blueprint as BPMAIN

reload(BPMAIN)

CLASS_NAME = 'LegBlueprint'
BLUEPRINT_TYPE = 'leg'
DESCRIPTION = 'Leg blueprint'
ICON = ''


class LegBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Leg Blueprint'
        super(LegBlueprint, self).__init__(*args, **kargs)
        self.bpType = BLUEPRINT_TYPE
        # self.bpGuidesPos = {0:{'pos':[0.0,120.0,0.0]},1:{'pos':[0.0,70.0,10.0]},2:{'pos':[0.0,20.0,0.0]},4:{'pos':[0.0,10.0,20.0]}}
        self.bpGuidesPos = {}

        self.upperRollNum = 0
        self.lowerRollNum = 0

        self.parseInfo()
        self.buildGuidesInfo()

    def parseInfo(self):
        super(LegBlueprint, self).parseInfo()
        for info, val in self.bpInfo.iteritems():
            if info == 'upRollNum':
                self.upperRollNum = val
            if info == 'lowRollNum':
                self.lowerRollNum = val

    def buildGuidesInfo(self):
        segmentLength = self.bpLength / 2.0

        for i in range(3):
            if i == 1:
                pos = [self.bpLength * 0.3, self.bpLength - i * segmentLength, self.bpLength * 0.02]
            else:
                pos = [self.bpLength * 0.3, self.bpLength - i * segmentLength, 0.0]
            self.bpGuidesPos[i] = {'pos': pos}

        pos = [self.bpLength * 0.3, 0.0, self.bpLength * 0.1]
        self.bpGuidesPos[3] = {'pos': pos}

        pos = [self.bpLength * 0.3, 0.0, self.bpLength * 0.2]
        self.bpGuidesPos[4] = {'pos': pos}

    def create(self):
        super(LegBlueprint, self).create()
        pm.select(cl=1)
