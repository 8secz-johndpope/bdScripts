import pymel.core as pm

import blueprint as BPMAIN

reload(BPMAIN)

CLASS_NAME = 'NeckBlueprint'
BLUEPRINT_TYPE = 'neck'
DESCRIPTION = 'Neck Blueprint'
ICON = ''


class NeckBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Neck Blueprint'
        super(NeckBlueprint, self).__init__(*args, **kargs)
        self.bpType = BLUEPRINT_TYPE
        # self.bpGuidesPos = {0:{'pos':[0.0,0.0,0.0]},1:{'pos':[0.0,20.0,0.0]}}
        self.bpInfo = kargs.setdefault('buildInfo', {})

        self.neckNumJnt = 2

        self.bpGuidesPos = {}

        self.parseInfo()
        self.buildGuidesInfo()

    def parseInfo(self):
        super(NeckBlueprint, self).parseInfo()
        for info, val in self.bpInfo.iteritems():
            if info == 'spineNumJnt':
                self.neckNumJnt = val

    def buildGuidesInfo(self):
        parent = pm.ls(self.bpParent)[0]
        parentPos = parent.getTranslation(space='world')

        segmentLength = 0

        if self.neckNumJnt > 1:
            segmentLength = 1.0 * self.bpLength / (self.neckNumJnt - 1.0)

        for i in range(self.neckNumJnt):
            pos = [parentPos[0], parentPos[1] + (segmentLength * i), parentPos[2]]
            self.bpGuidesPos[i] = {'pos': pos}

    def create(self):
        super(NeckBlueprint, self).create()
