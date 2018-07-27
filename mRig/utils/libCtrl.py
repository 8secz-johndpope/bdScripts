import pymel.core as pm
import maya.OpenMaya as om
import os


class Controller(object):
    def __init__(self, *args, **kargs):
        self.ctrlName = kargs.setdefault('ctrlName', '')
        self.scale = kargs.setdefault('scale', 3)
        self.ctrlType = kargs.setdefault('ctrlType', 'circle')
        self.ctrlPos = None

    def buildController(self):
        if self.ctrlName == '':
            pm.warning('No name or target specified for building the controller')
            return

        if self.ctrlType == 'circle':
            return self.buildCircleController()
        elif self.ctrlType == 'box':
            return self.buildBoxController()

    def buildBoxController(self):
        defaultPointsList = [(1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1),
                             (-1, 1, 1)]
        pointsList = []
        for p in defaultPointsList:
            pointsList.append((p[0] * self.scale, p[1] * self.scale, p[2] * self.scale))

        curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3],
                       pointsList[7], pointsList[4], pointsList[5], pointsList[6],
                       pointsList[7], pointsList[3], pointsList[0], pointsList[4],
                       pointsList[5], pointsList[1], pointsList[2], pointsList[6]]

        ctrl = pm.curve(d=1, p=curvePoints)
        ctrl = pm.rename(ctrl, self.ctrlName)
        ctrlGrp = pm.group(ctrl, n=str(self.ctrlName + '_grp'))

        # pm.addAttr(ctrl,ln='parent',at='message')
        # pm.connectAttr(ctrlGrp.name() + '.message' , ctrl.name() + '.parent')

        pm.move(ctrlGrp, self.ctrlPos[0], self.ctrlPos[1], self.ctrlPos[2])

        return ctrl.name()

    def buildCircleController(self):
        pm.select(cl=1)
        ctrl = pm.circle(name=self.ctrlName, c=[0, 0, 0], nr=[0, 1, 0], ch=0, radius=self.scale)[0]
        ctrlGrp = pm.group(ctrl, n=str(self.ctrlName + '_grp'))

        # pm.addAttr(ctrl,ln='parent',at='message')
        # pm.connectAttr(ctrlGrp.name() + '.message' , ctrl.name() + '.parent')

        pm.select(cl=1)

        pm.move(ctrlGrp, self.ctrlPos[0], self.ctrlPos[1], self.ctrlPos[2])

        return ctrl.name()

    def movePivot(self, target):
        pass

    def moveCtrl(self, pos):
        pass

    def alignCtrl(self, target):
        pass
