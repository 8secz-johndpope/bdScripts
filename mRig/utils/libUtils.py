import pymel.core as pm
import maya.OpenMaya as om
import os
import inspect


def toVector(posList):
    vector = om.MVector(posList[0], posList[1], posList[2])
    return vector


def addStringAttr(transform, attrName, attrVal):
    pm.addAttr(transform, ln=attrName, dt="string")
    pm.setAttr((transform + '.' + attrName), str(attrVal), type='string')
    pm.setAttr((transform + '.' + attrName), l=1)


def addMessageAttr(obj, target, attrName):
    pm.addAttr(obj, ln=attrName, at='message')
    pm.connectAttr(target + '.message', obj + '.' + attrName)


def getBlueprintsList():
    # script directory    
    utilsFolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    blueprintsFolder = utilsFolder.replace('system\utils', 'blueprints')

    if os.path.isdir(blueprintsFolder):
        blueprintFiles = [os.path.splitext(py)[0] for py in os.listdir(blueprintsFolder) if
                          py.endswith('.py') and '__init__' not in py]

        if len(blueprintFiles):
            return blueprintFiles
        else:
            return None


def undoable(function):
    '''A decorator that will make commands undoable in maya'''

    def decoratorCode(*args, **kwargs):
        pm.undoInfo(openChunk=True)
        functionReturn = None
        print 'adad'
        try:
            functionReturn = function(*args, **kwargs)
            pm.undoInfo(closeChunk=True)

        except:
            pm.undoInfo(closeChunk=True)
            print(traceback.format_exc())

            #	throw the actual error
            pm.error()

    return decoratorCode
