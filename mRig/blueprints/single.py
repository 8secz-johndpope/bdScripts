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
        self.bpType = BLUEPRINT_TYPE

        self.parseInfo()
        self.buildGuidesInfo()

    def parseInfo(self):
        super(SingleBlueprint, self).parseInfo()

    def buildGuidesInfo(self):
        parent = pm.ls(self.bpParent)[0]
        parentPos = parent.getTranslation(space='world')

        pos = [parentPos[0], parentPos[1], parentPos[2]]
        self.bpGuidesPos[0] = {'pos': pos}

    def create(self):
        super(SingleBlueprint, self).create()
