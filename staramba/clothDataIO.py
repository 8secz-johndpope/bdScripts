import pymel.core as pm
import os
import json
# import maya.api.OpenMaya as om

physicalLodClothAttr = ['GravityScale', 'Friction', 'Bendiness', 'StiffnessSheariness', 'StretchLimit',
                         'TetherStiffnessRelax', 'DampingCoefficient', 'Drag', 'InertiaBlend', 'FiberCompression' ,
                         'FiberExpansion' , 'FiberResistance']

lodClothAttr = ['lodThickness', 'lodSelfCollisionEnable', 'lodSelfCollisionThickness', 'lodSelfCollisionStiffness',
                'lodMassScale', 'lodVirtualParticleDensity', 'lodRestLengthScale', 'lodSolverFrequency']



def exportClothData():
    selection = pm.ls(sl=1)
    if len(selection) > 0:
        sl = selection[0]
        if sl.type() != 'apexClothing':
            pm.warning('Selected is not an APEX cloth node')
            return

        clothDataFile = setClothFile()

        if clothDataFile:
            print clothDataFile
            clothData = getClothData(sl)

            with open(clothDataFile, 'w') as outfile:
                json.dump(clothData, outfile)
        else:
            pm.warning('No file to save')
    else:
        pm.warning("Nothing selected")


def importClothData():
    selection = pm.ls(sl=1)
    if len(selection) > 0:
        sl = selection[0]
        if sl.type() != 'apexClothing':
            pm.warning('Selected is not an APEX cloth node')
            return

        clothDataFile = getClothFile()

        if clothDataFile:
            print clothDataFile
            clothData = getClothData(sl)

            with open(clothDataFile, 'r') as infile:
                clothData = json.load(infile)
                applyClothData(sl, clothData)


def getClothData(sl):
    clothData = {}
    for attr in physicalLodClothAttr:
        attrName = 'physicalMaterialSets[0].pm' + attr
        attrValue = sl.attr(attrName).get()
        clothData[attrName] = attrValue

    for attr in lodClothAttr:
        attrName = 'lodCompoundAttributes[0].' + attr
        attrValue = sl.attr(attrName).get()
        clothData[attrName] = attrValue

    return clothData

def setClothFile():
    sceneName = pm.sceneName()
    path, file = os.path.split(sceneName)
    clothFolder = os.path.join(path, '02_cloth_data')
    if not os.path.exists(clothFolder):
        os.makedirs(clothFolder)

    filePath = pm.fileDialog2(dir=clothFolder, ds=1, fm=0, fileFilter='Cloth data files (*.clothData)')
    if not filePath:
        return None

    return filePath[0]

def getClothFile():
    sceneName = pm.sceneName()
    path, file = os.path.split(sceneName)
    clothFolder = os.path.join(path, '02_cloth_data')
    if os.path.exists(clothFolder):
        filePath = pm.fileDialog2(dir=clothFolder, ds=1, fm=1, fileFilter='Cloth data files (*.clothData)')
        if not filePath:
            return None

        return filePath[0]

def applyClothData(clothNode, clothData):
    for attr, val in clothData.iteritems():
        print attr, val
        clothNode.attr(attr).set(val)

# def getClothDataApi():
#     # sel = om.MSelectionList()
#     sel = om.MGlobal.getActiveSelectionList()
#     if sel.length() > 0:
#         iterator = om.MItSelectionList(sel)
#         while not iterator.isDone():
#             depNode = om.MFnDependencyNode(iterator.getDependNode())
#             print depNode.name()
#             plugs = depNode.findPlug("lodGravityScale",0)
#             print plugs.asString()
#             # for i in range(plugs.numChildren()):
#             #     # attr = om.MFnAttribute(plugs.child(i).attribute())
#             #     print plugs.child(i).asDouble()
#             #
#             iterator.next()