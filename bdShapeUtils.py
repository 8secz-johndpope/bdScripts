import pymel.core as pm
import json, os

defaultFolder = 'd:\\bogdan\\shapes'


class ShapeUtils(object):
    def __init__(self, *args, **kargs):
        self.shapesFolder = kargs.setdefault(defaultFolder)
        self.saveOnDisc = kargs.setdefault(0)

    def crvShapeSave(self):
        selection = pm.ls(sl=1)
        if selection:
            for obj in selection:
                shapes = obj.getShapes()
                objName = obj.name().replace('|', '_')
                for shape in shapes:
                    if shape.type() == 'nurbsCurve':
                        shapeInfoDict = getShapeInfo(shape)
                        shapeFile = os.path.join(shapesFolder, objName + '.json')
                        with open(shapeFile, 'w') as outfile:
                            json.dump(shapeInfoDict, outfile)

    def getShapeInfo(self, shape):
        name = shape.name()
        cvNum = shape.numCVs()
        cvPos = []

        for i in range(cvNum):
            pos = pm.xform(shape.name() + '.cv[' + str(i) + ']', q=1, a=1, t=1, ws=1)
            cvPos.append(pos)

        info = {'name': name, 'cvsPos': cvPos}
        return info

    def crvShapeLoad(self):
        selection = pm.ls(sl=1)
        if selection:
            for obj in selection:
                shapes = obj.getShapes()
                objName = obj.name().replace('|', '_')
                for shape in shapes:
                    if shape.type() == 'nurbsCurve':
                        shapeFile = os.path.join(shapesFolder, objName + '.json')
                        if os.path.isfile(shapeFile):
                            with open(shapeFile) as data_file:
                                shapeInfo = json.load(data_file)
                                setShape(shape, shapeInfo)

    def copyShape(self, src, dest):
        src = pm.ls(src)[0]
        srcShape = src.getShape()

        dest = pm.ls(dest)[0]
        destShape = dest.getShape()

        if srcShape:
            srcInfo = getShapeInfo(src)

        if destShape:
            setShape(destShape, srcInfo)

    def setShape(shape, shapeInfo):
        cvPos = shapeInfo['cvsPos']
        for i in range(len(cvPos)):
            pm.move(shape.name() + '.cv[' + str(i) + ']', cvPos[i][0], cvPos[i][1], cvPos[i][2], a=1, ws=1, )
