import pymel.core as pm

import blueprint as BPMAIN
reload(BPMAIN)

CLASS_NAME = 'RootBlueprint'
BLUEPRINT_TYPE = 'root'
DESCRIPTION = 'Root Blueprint'
ICON = ''


class RootBlueprint(BPMAIN.Blueprint):
    def __init__(self, *args, **kargs):
        print 'Root Blueprint'
        super(RootBlueprint, self).__init__(*args, **kargs)
        self.type_bp = BLUEPRINT_TYPE

        self.parse_info()
        self.buildGuidesInfo()

    def parse_info(self):
        super(RootBlueprint, self).parse_info()

    def buildGuidesInfo(self):
        parent = pm.ls(self.parent)[0]
        parentPos = parent.getTranslation(space='world')

        pos = [parentPos[0], parentPos[1], parentPos[2]]
        self.guide_pos[0] = {'pos': pos}

    def create(self):
        super(RootBlueprint, self).create()
