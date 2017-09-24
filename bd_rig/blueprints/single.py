import pymel.core as pm

import blueprint as BPMAIN

reload(BPMAIN)

CLASS_NAME = 'SingleBlueprint'
BLUEPRINT_TYPE = 'single'
DESCRIPTION = 'Single Blueprint'
ICON = ''


class SingleBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Single Blueprint'
        super(SingleBlueprint, self).__init__(*args, **kargs)
        self.type_bp = BLUEPRINT_TYPE

        self.parse_info()
        self.buildGuidesInfo()

    def parse_info(self):
        super(SingleBlueprint, self).parse_info()

    def buildGuidesInfo(self):
        parent = pm.ls(self.parent)[0]
        parentPos = parent.getTranslation(space='world')

        pos = [parentPos[0], parentPos[1], parentPos[2]]
        self.guide_pos[0] = {'pos': pos}

    def create(self):
        super(SingleBlueprint, self).create()
