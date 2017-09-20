import pymel.core as pm
import maya.OpenMaya as om


def buildBoxController(target, ctrlName, scale=1):
    defaultPointsList = [(1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1),
                         (-1, 1, 1)]
    pointsList = []
    for p in defaultPointsList:
        pointsList.append((p[0] * scale, p[1] * scale, p[2] * scale))

    knotsList = [i for i in range(16)]
    curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3],
                   pointsList[7], pointsList[4], pointsList[5], pointsList[6],
                   pointsList[7], pointsList[3], pointsList[0], pointsList[4],
                   pointsList[5], pointsList[1], pointsList[2], pointsList[6]]

    ctrl = pm.curve(d=1, p=curvePoints, k=knotsList)
    ctrl = pm.rename(ctrl, ctrlName)
    ctrlGrp = pm.group(ctrl, n=str(ctrlName + '_grp'))
    targetPos = pm.xform(target, q=True, ws=True, t=True)
    pm.move(ctrlGrp, targetPos[0], targetPos[1], targetPos[2])
    return [ctrl, ctrlGrp]


def buildCircleController(target='', ctrlName='', scale=1):
    pm.select(cl=1)
    ctrl = pm.circle(name=ctrlName, c=[0, 0, 0], nr=[0, 1, 0], ch=0, radius=scale)[0]
    ctrlGrp = pm.group(ctrl, n=str(ctrlName + '_grp'))
    pm.select(cl=1)

    targetPos = [0, 0, 0]

    if target != '':
        targetPos = pm.xform(target, q=True, ws=True, t=True)

    pm.move(ctrlGrp, targetPos[0], targetPos[1], targetPos[2])

    return ctrl, ctrlGrp


def toVector(posList):
    vector = om.MVector(posList[0], posList[1], posList[2])
    return vector


def addStringAttr(transform, attrName, attrVal):
    pm.addAttr(transform, ln=attrName, dt="string")
    pm.setAttr((transform.name() + '.' + attrName), str(attrVal), type='string')
