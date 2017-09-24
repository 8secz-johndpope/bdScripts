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
        self.type_bp = BLUEPRINT_TYPE
        # self.guide_pos = {0:{'pos':[0.0,120.0,0.0]},1:{'pos':[0.0,70.0,10.0]},2:{'pos':[0.0,20.0,0.0]},4:{'pos':[0.0,10.0,20.0]}}
        self.guide_pos = {}

        self.upperRollNum = 0
        self.lowerRollNum = 0

        self.parse_info()
        self.buildGuidesInfo()

    def parse_info(self):
        super(LegBlueprint, self).parse_info()
        for info, val in self.info.iteritems():
            if info == 'upRollNum':
                self.upperRollNum = val
            if info == 'lowRollNum':
                self.lowerRollNum = val

    def buildGuidesInfo(self):
        segmentLength = self.length / 2.0

        for i in range(3):
            if i == 1:
                pos = [self.length * 0.3, self.length - i * segmentLength, self.length * 0.02]
            else:
                pos = [self.length * 0.3, self.length - i * segmentLength, 0.0]
            self.guide_pos[i] = {'pos': pos}

        pos = [self.length * 0.3, 0.0, self.length * 0.1]
        self.guide_pos[3] = {'pos': pos}

        pos = [self.length * 0.3, 0.0, self.length * 0.2]
        self.guide_pos[4] = {'pos': pos}

    def create(self):
        super(LegBlueprint, self).create()
        pm.select(cl=1)
