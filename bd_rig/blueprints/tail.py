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
        self.type_bp = BLUEPRINT_TYPE

        self.info = kargs.setdefault('buildInfo', {})

        self.tailNumJnt = 5

        self.guide_pos = {}

        self.parse_info()
        self.buildGuidesInfo()
        # self.guide_pos = {0:{'pos':[0.0,0.0,0.0]},1:{'pos':[-20.0,0.0,0]},2:{'pos':[-40.0,0.0,0]}}

    def parse_info(self):
        super(TailBlueprint, self).parse_info()
        for info, val in self.info.iteritems():
            if info == 'spineNumJnt':
                self.tailNumJnt = val

    def buildGuidesInfo(self):
        parent = pm.ls(self.parent)[0]
        parentPos = parent.getTranslation(space='world')

        segmentLength = 1.0 * self.length / (self.tailNumJnt - 1)

        for i in range(self.tailNumJnt):
            pos = [parentPos[0], parentPos[1], parentPos[2] + -1 * (self.length + segmentLength * i)]
            self.guide_pos[i] = {'pos': pos}

    def create(self):
        super(TailBlueprint, self).create()
