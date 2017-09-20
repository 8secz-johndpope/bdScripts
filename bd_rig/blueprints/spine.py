import pymel.core as pm

import blueprint as BPMAIN

reload(BPMAIN)

CLASS_NAME = 'SpineBlueprint'
BLUEPRINT_TYPE = 'spine'
DESCRIPTION = 'Spine Blueprint'
ICON = ''


class SpineBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Spine Blueprint'
        super(SpineBlueprint, self).__init__(*args, **kargs)
        self.bpType = BLUEPRINT_TYPE

        self.bpInfo = kargs.setdefault('buildInfo', {})

        self.spineNumJnt = 0

        self.bpGuidesPos = {}

        self.parseInfo()
        self.buildGuidesInfo()

    def parseInfo(self):
        super(SpineBlueprint, self).parseInfo()
        for info, val in self.bpInfo.iteritems():
            if info == 'spineNumJnt':
                self.spineNumJnt = val

    def buildGuidesInfo(self):
        segmentLength = 1.0 * self.bpLength / (self.spineNumJnt - 1)
        print segmentLength

        for i in range(self.spineNumJnt):
            pos = [0.0, self.bpLength + segmentLength * i, 0.0]
            self.bpGuidesPos[i] = {'pos': pos}

    def create(self):
        super(SpineBlueprint, self).create()
