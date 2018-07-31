import pymel.core as pm
import maya.OpenMaya as om
import os


class Controller(object):
    def __init__(self, *args, **kargs):
        self.name = kargs.setdefault('name', '')
        self.scale = kargs.setdefault('scale', 3)
        self.look = kargs.setdefault('look', 'circle')
        self.target = kargs.setdefault('target', None)

    def create(self):
        if self.name == '':
            pm.warning('No name or target specified for createing the controller')
            return

        if self.look == 'circle':
            return self.circle_ctrl()
        elif self.look == 'box':
            return self.box_ctrl()

    def box_ctrl(self):
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
        ctrl = pm.rename(ctrl, self.name)
        ctrl_grp = pm.group(ctrl, n=str(self.name + '_grp'))

        # pm.addAttr(ctrl,ln='parent',at='message')
        # pm.connectAttr(ctrlGrp.name() + '.message' , ctrl.name() + '.parent')

        if self.target:
            pos = self.target.getTranslation(space='world')
            ctrl_grp.setTranslation(pos, space='world')

        return ctrl, ctrl_grp

    def circle_ctrl(self):
        pm.select(cl=1)
        ctrl = pm.circle(name=self.name, c=[0, 0, 0], nr=[0, 1, 0], ch=0, radius=self.scale)[0]
        ctrl_grp = pm.group(ctrl, n=str(self.name + '_grp'))
        # pm.addAttr(ctrl,ln='parent',at='message')
        # pm.connectAttr(ctrlGrp.name() + '.message' , ctrl.name() + '.parent')
        pm.select(cl=1)
        if self.target:
            pos = self.target.getTranslation(space='world')
            ctrl_grp.setTranslation(pos, space='world')

        return ctrl, ctrl_grp


    def movePivot(self, target):
        pass

    def moveTo(self, pos):
        pass

    def alignTo(self, target):
        pass

    def resize(self, factor):
        pm.scale(self.name, factor)
        # pm.makeIdentity(self.name, scale=True)