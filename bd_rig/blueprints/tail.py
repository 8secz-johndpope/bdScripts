import pymel.core as pm

import blueprint as BPMAIN

reload(BPMAIN)

CLASS_NAME = 'TailBlueprint'
BLUEPRINT_TYPE = 'tail'
DESCRIPTION = 'Tail Blueprint'
ICON = ''


class TailBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Tail Blueprint'
        super(TailBlueprint, self).__init__(*args, **kargs)
        self.bpType = BLUEPRINT_TYPE

        self.bpInfo = kargs.setdefault('buildInfo', {})

        self.tailNumJnt = 5

        self.bpGuidesPos = {}

        self.parseInfo()
        self.buildGuidesInfo()
        # self.bpGuidesPos = {0:{'pos':[0.0,0.0,0.0]},1:{'pos':[-20.0,0.0,0]},2:{'pos':[-40.0,0.0,0]}}

    def parseInfo(self):
        super(TailBlueprint, self).parseInfo()
        for info, val in self.bpInfo.iteritems():
            if info == 'spineNumJnt':
                self.tailNumJnt = val

    def buildGuidesInfo(self):
        parent = pm.ls(self.bpParent)[0]
        parentPos = parent.getTranslation(space='world')

        segmentLength = 1.0 * self.bpLength / (self.tailNumJnt - 1)

        for i in range(self.tailNumJnt):
            pos = [parentPos[0], parentPos[1], parentPos[2] + -1 * (self.bpLength + segmentLength * i)]
            self.bpGuidesPos[i] = {'pos': pos}

    def create(self):
        super(TailBlueprint, self).create()
