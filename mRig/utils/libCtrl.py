import pymel.core as pm
import pymel.core.datatypes as dt
import json
import os


class Controller(object):
    def __init__(self, *args, **kargs):
        self.name = kargs.setdefault('name', '')
        self.scale = kargs.setdefault('scale', 3)
        self.visual = kargs.setdefault('visual', 'circle')
        self.target = kargs.setdefault('target', None)
        self.ctrl = None
        self.ctrl_grp = None

    def create(self):
        if self.name == '':
            pm.displayError('No name specified for creating the controller')
            return

        if self.visual == 'circle':
            self.circle_ctrl()
        elif self.visual == 'box':
            self.box_ctrl()
        elif self.visual == 'square':
            self.square_ctrl()
        elif self.visual == 'joint':
            self.joint_ctrl()

        pm.addAttr(self.ctrl, ln="anim_ctrl", dt="string", k=0)
        self.ctrl.attr('anim_ctrl').set('body')

    def box_ctrl(self):
        points = [(1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1)]
        
        for i in range(len(points)):
            scaled_pos = (points[i][0] * self.scale,
                          points[i][1] * self.scale,
                          points[i][2] * self.scale)
            points[i] = scaled_pos

        crv_points = [points[0], points[1], points[2], points[3],
                       points[7], points[4], points[5], points[6],
                       points[7], points[3], points[0], points[4],
                       points[5], points[1], points[2], points[6]]

        ctrl = pm.curve(d=1, p=crv_points)
        ctrl = pm.rename(ctrl, self.name)
        ctrl_grp = pm.group(ctrl, n=str(self.name + '_grp'))
        pm.select(cl=1)
        self.ctrl = ctrl
        self.ctrl_grp = ctrl_grp

        pm.addAttr(ctrl, ln='parent', at='message')
        pm.connectAttr(ctrl_grp.name() + '.message', ctrl.name() + '.parent')

    def circle_ctrl(self):
        pm.select(cl=1)
        ctrl = pm.circle(name=self.name, c=[0, 0, 0], nr=[1, 0, 0], ch=0, radius=self.scale)[0]
        ctrl_grp = pm.group(ctrl, n=str(self.name + '_grp'))

        pm.addAttr(ctrl, ln='parent', at='message')
        pm.connectAttr(ctrl_grp.name() + '.message', ctrl.name() + '.parent')

        pm.select(cl=1)
        self.ctrl = ctrl
        self.ctrl_grp = ctrl_grp

    def square_ctrl(self):
        points = [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0)]

        for i in range(len(points)):
            scaled_pos = (points[i][0] * self.scale,
                          points[i][1] * self.scale,
                          points[i][2] * self.scale)
            points[i] = scaled_pos

        crv_points = [points[0], points[1], points[2], points[3], points[0]]

        ctrl = pm.curve(d=1, p=crv_points)
        ctrl.rename(self.name)
        ctrl_grp = pm.group(ctrl, n=self.name + '_grp')

        pm.addAttr(ctrl, ln='parent', at='message')
        pm.connectAttr(ctrl_grp.name() + '.message', ctrl.name() + '.parent')
        
        self.ctrl = ctrl
        self.ctrl_grp = ctrl_grp

    def joint_ctrl(self):
        circle1 = pm.circle(n=self.name + 'A', nr=(0, 1, 0), c=(0, 0, 0), radius=self.scale)[0]
        circle2 = pm.circle(n=self.name + 'B', nr=(1, 0, 0), c=(0, 0, 0), radius=self.scale)[0]
        circle3 = pm.circle(n=self.name + 'C', nr=(0, 0, 1), c=(0, 0, 0), radius=self.scale)[0]

        circle2_shape = circle2.getShape()
        circle3_shape = circle3.getShape()
        pm.parent(circle2_shape, circle1, r=True, s=True)
        pm.parent(circle3_shape, circle1, r=True, s=True)
        pm.delete(circle2, circle3)
        ctrl = pm.rename(circle1, self.name)
        ctrl_grp = pm.group(ctrl, n=self.name + '_grp')

        pm.addAttr(ctrl, ln='parent', at='message')
        pm.connectAttr(ctrl_grp.name() + '.message', ctrl.name() + '.parent')

        self.ctrl = ctrl
        self.ctrl_grp = ctrl_grp

    def offset_ctrl_grp(self, offset):
        pos = self.ctrl_grp.getTranslation(space='world')
        pos += dt.Vector(offset)
        self.ctrl_grp.setTranslation(pos, space='world')

    def match_rotation(self):
        if self.target:
            temp_pc = pm.orientConstraint(self.target, self.ctrl_grp, mo=0)
            pm.delete(temp_pc)

    def match_position(self):
        if self.target:
            temp_pc = pm.pointConstraint(self.target, self.ctrl_grp, mo=0)
            pm.delete(temp_pc)

    def match_all(self):
        self.match_position()
        self.match_rotation()

    def resize(self, factor):
        pm.scale(self.name, factor)
        # pm.makeIdentity(self.name, scale=True)

    def add_float_attr(self, attr_name, min, max):
        pm.addAttr(self.ctrl, ln=attr_name, at='double', min=min, max=max, dv=0, k=1)

    def lock_hide_attr(self, attr_name_list):
        for attr_name in attr_name_list:
            tokens = attr_name.split('_')
            if len(tokens) > 1:
                attr, axis = tokens[0], tokens[1]

                for a in axis:
                    self.ctrl.attr(attr + a).setKeyable(0)
                    self.ctrl.attr(attr + a).setLocked(1)
            else:
                self.ctrl.attr(attr_name).setKeyable(0)
                self.ctrl.attr(attr_name).setLocked(1)



