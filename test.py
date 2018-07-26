import re
import pymel.core as pm
import os
import json
from maya import cmds as mc, OpenMaya as om

def niceName(uglyName):
    splitted = ''
    start = 0
    for letter, index in enumerate(uglyName):
        if letter.isupper():
            token = uglyName[start:uglyName.index(letter)]
            splitted += ( token.capitalize() + ' ')
            start = uglyName.index(letter)
        if letter == uglyName[-1]:
            token = uglyName[start:]
            splitted += ( token.capitalize() + ' ')

    if splitted == '':
        return uglyName
    else:
        return splitted[:-1]


def niceName1(uglyName):
    print uglyName
    tokens = re.findall('[A-Z]+[a-z]*', uglyName)
    print tokens
    newName = ''
    for t in tokens:
        newName += (t + ' ')
    newName = newName.strip()
    return newName

def camel_case_split(identifier):
    #matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[0-9])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


def getShapeInfo(shape):
    name = shape.name()
    cvNum = shape.numCVs(editableOnly=False)
    knotNum = shape.numKnots()
    knots = shape.getKnots()

    points = []
    for i in range(pm.getAttr(name + ".controlPoints", s=1)):
        pointPos = pm.getAttr(name + ".controlPoints[%i]" % i)
        pointPos = [round(v,2) for v in pointPos]
        points.append(pointPos)

    print points
    cvPos = []
    for i in range(cvNum):
        pos = pm.xform(shape.name() + '.cv[' + str(i) + ']', q=1, t=1, ws=1)
        cvPos.append([round(val,2) for val in pos])
    return cvPos, knots
#############################

def getKnots(crvShape=None):
    mObj = om.MObject()
    sel = om.MSelectionList()
    sel.add(crvShape)
    sel.getDependNode(0, mObj)

    fnCurve = om.MFnNurbsCurve(mObj)
    tmpKnots = om.MDoubleArray()
    fnCurve.getKnots(tmpKnots)

    return [tmpKnots[i] for i in range(tmpKnots.length())]

def validateCurve(crv=None):
    '''Checks whether the transform we are working with is actually a curve and returns it's shapes'''
    if mc.nodeType(crv) == "transform" and mc.nodeType(mc.listRelatives(crv, c=1, s=1)[0]) == "nurbsCurve":
        crvShapes = mc.listRelatives(crv, c=1, s=1)
    elif mc.nodeType(crv) == "nurbsCurve":
        crvShapes = mc.listRelatives(mc.listRelatives(crv, p=1)[0], c=1, s=1)
    else:
        mc.error("The object " + crv + " passed to validateCurve() is not a curve")
    return crvShapes

def getShape(crv=None):
    '''Returns a dictionary containing all the necessery information for rebuilding the passed in crv.'''
    crvShapes = validateCurve(crv)

    crvShapeList = []

    for crvShape in crvShapes:
        crvShapeDict = {
            "points": [],
            "knots": [],
            "form": mc.getAttr(crvShape + ".form"),
            "degree": mc.getAttr(crvShape + ".degree"),
            "colour": mc.getAttr(crvShape + ".overrideColor")
        }
        points = []

        for i in range(mc.getAttr(crvShape + ".controlPoints", s=1)):
            points.append(mc.getAttr(crvShape + ".controlPoints[%i]" % i)[0])
            print mc.getAttr(crvShape + ".controlPoints[%i]" % i)[0]

        crvShapeDict["points"] = points
        print len(points)
        crvShapeDict["knots"] = getKnots(crvShape)
        print len(getKnots(crvShape))

        crvShapeList.append(crvShapeDict)

    return crvShapeList

def setShape(crv, crvShapeList):
    '''Creates a new shape on the crv transform, using the properties in the crvShapeDict.'''
    crvShapes = validateCurve(crv)

    oldColour = mc.getAttr(crvShapes[0] + ".overrideColor")
    mc.delete(crvShapes)

    for i, crvShapeDict in enumerate(crvShapeList):
        tmpCrv = mc.curve(p=crvShapeDict["points"], k=crvShapeDict["knots"], d=crvShapeDict["degree"], per=bool(crvShapeDict["form"]))
        newShape = mc.listRelatives(tmpCrv, s=1)[0]
        mc.parent(newShape, crv, r=1, s=1)

        mc.delete(tmpCrv)
        newShape = mc.rename(newShape, crv + "Shape" + str(i + 1).zfill(2))

        mc.setAttr(newShape + ".overrideEnabled", 1)

