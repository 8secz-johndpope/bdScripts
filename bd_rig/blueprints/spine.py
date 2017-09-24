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
        self.type_bp = BLUEPRINT_TYPE

        self.info = kargs.setdefault('buildInfo', {})

        self.spineNumJnt = 0

        # self.guide_pos = {}

        self.parse_info()
        self.buildGuidesInfo()
        print self.guide_pos


    def parse_info(self):
        super(SpineBlueprint, self).parse_info()
        for info, val in self.info.iteritems():
            if info == 'num_jnt':
                self.spineNumJnt = val

    def buildGuidesInfo(self):
        segmentLength = 1.0 * self.length / (self.spineNumJnt - 1)
        print segmentLength

        for i in range(self.spineNumJnt):
            pos = [0.0, self.length + segmentLength * i, 0.0]
            self.guide_pos[i] = {'pos': pos}


    def create(self):
        super(SpineBlueprint, self).create()
