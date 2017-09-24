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
        self.type_bp = BLUEPRINT_TYPE
        # self.guide_pos = {0:{'pos':[0.0,0.0,0.0]},1:{'pos':[0.0,20.0,0.0]}}
        self.info = kargs.setdefault('buildInfo', {})

        self.neckNumJnt = 2

        self.guide_pos = {}

        self.parse_info()
        self.buildGuidesInfo()

    def parse_info(self):
        super(NeckBlueprint, self).parse_info()
        for info, val in self.info.iteritems():
            if info == 'spineNumJnt':
                self.neckNumJnt = val

    def buildGuidesInfo(self):
        parent = pm.ls(self.parent)[0]
        parentPos = parent.getTranslation(space='world')

        segmentLength = 0

        if self.neckNumJnt > 1:
            segmentLength = 1.0 * self.length / (self.neckNumJnt - 1.0)

        for i in range(self.neckNumJnt):
            pos = [parentPos[0], parentPos[1] + (segmentLength * i), parentPos[2]]
            self.guide_pos[i] = {'pos': pos}

    def create(self):
        super(NeckBlueprint, self).create()
