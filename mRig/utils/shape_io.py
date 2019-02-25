import pymel.core as pm
import json
import os


class ShapeIO:
    def __init__(self, name):
        self.ctrl = name
        self.ctrl_folder = ''
        self.shape_info = {}
        self.set_ctrl_folder()

    def save_shape(self):
        self.shape_info.clear()
        shapes = self.ctrl.getShapes()
        if len(shapes):
            shape = shapes[0]
            self.shape_info['transform'] = self.ctrl.name()
            self.get_shape_info(shape)

            shape_file = os.path.join(self.ctrl_folder, self.ctrl + '.ctrl')
            with open(shape_file, 'w') as outfile:
                json.dump(self.shape_info, outfile)

    def get_shape_info(self, shape):
        name = shape.name()
        points = []
        cvs = shape.getCVs(space='world')
        for cv in cvs:
            pos = [round(v, 2) for v in cv]
            points.append(pos)
        #
        # for i in range(pm.getAttr(name + ".controlPoints", s=1)):
        #     pos = pm.getAttr(name + ".controlPoints[%i]" % i)
        #     pos = [round(v, 2) for v in pos]
        #     points.append(pos)

        self.shape_info['shapes'] = [{'shapeName': name, 'cvsPos': points}]

    def import_shape(self):
        ctrl_file = os.path.join(self.ctrl_folder, self.ctrl.name() + '.ctrl')
        if os.path.isfile(ctrl_file):
            with open(os.path.join(self.ctrl_folder, ctrl_file), 'r') as infile:
                ctrl_info = json.load(infile)
                self.restore_shape(ctrl_info)

    def restore_shape(self, ctrl_info):
        ctrl_name = ctrl_info['transform']
        if len(pm.ls(ctrl_name)):
            print 'Found controller %s, restoring shape' % ctrl_name
            shapes = ctrl_info['shapes']
            for shape_info in shapes:
                shapeFound = pm.ls(shape_info['shapeName'])
                if shapeFound:
                    shape = shapeFound[0]

                    cvNum = shape.numCVs()
                    cvPos = shape_info['cvsPos']
                    shape.setCVs(cvPos, space='world')
                    shape.updateCurve()
                    # for i in range(cvNum):
                    #     pm.move(shape.name() + '.cv[' + str(i) + ']', cvPos[i][0], cvPos[i][1], cvPos[i][2], a=1, ws=1)

    def set_ctrl_folder(self):
        scene = pm.sceneName()
        path, _ = os.path.split(scene)
        ctrl_folder = os.path.join(path, 'ctrl')
        if not os.path.exists(ctrl_folder):
            os.makedirs(ctrl_folder)

        self.ctrl_folder = ctrl_folder

