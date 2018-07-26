import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya

class DoublerNode(OpenMayaMPx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0x00047251)

    aInputA = OpenMaya.MObject()
    aInputB = OpenMaya.MObject()
    aOutput = OpenMaya.MObject()
    aPercent = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def compute(self, plug, data):
        if plug != DoublerNode.aOutput:
            return OpenMaya.MStatus.kUnknownParameter

        worldMatrixA = data.inputValue(DoublerNode.aInputA).asMatrix()
        worldMatrixB = data.inputValue(DoublerNode.aInputB).asMatrix()
        multi = data.inputValue(DoublerNode.aPercent).asFloat()

        # MTransformationMatrix
        mTMA = OpenMaya.MTransformationMatrix(worldMatrixA)
        mTMB = OpenMaya.MTransformationMatrix(worldMatrixB)

        # Get the translation from world matrix
        transA = mTMA.getRotation( OpenMaya.MSpace.kTransform )
        transB = mTMB.getRotation( OpenMaya.MSpace.kTransform )

        #setting the output
        hOutput = data.outputValue(DoublerNode.aOutput)
        resultTrans = OpenMaya.MFloatVector((transA.x + transB.x)*multi, (transA.y + transB.y)*multi, (transA.z + transB.z)*multi)
        hOutput.setMFloatVector(resultTrans)

        data.setClean(plug)


def creator():
    return OpenMayaMPx.asMPxPtr(DoublerNode())

#define new attributes here
def initialize():

    nAttr = OpenMaya.MFnNumericAttribute()
    nMAttr = OpenMaya.MFnMatrixAttribute()

    DoublerNode.aPercent = nAttr.create('percent', 'per',OpenMaya.MFnNumericData.kFloat, 0.5)
    nAttr.setWritable(True)
    nAttr.setStorable(True)
    nAttr.setReadable(True)

    nAttr.setKeyable(True)

    DoublerNode.aInputA = nMAttr.create('inMatrixA', 'inA',OpenMaya.MFnMatrixAttribute.kDouble)
    nMAttr.setWritable(True)
    nMAttr.setStorable(True)
    nMAttr.setReadable(True)
    nMAttr.setKeyable(True)

    DoublerNode.aInputB = nMAttr.create('inMatrixB', 'inB',OpenMaya.MFnMatrixAttribute.kDouble)
    nMAttr.setWritable(True)
    nMAttr.setStorable(True)
    nMAttr.setReadable(True)
    nMAttr.setKeyable(True)

    DoublerNode.aOutput = nAttr.createPoint("outputTranslate", "ot" )
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    nAttr.setReadable(True)

    DoublerNode.addAttribute(DoublerNode.aPercent)
    DoublerNode.addAttribute(DoublerNode.aOutput)
    DoublerNode.addAttribute(DoublerNode.aInputA)
    DoublerNode.addAttribute(DoublerNode.aInputB)

    DoublerNode.attributeAffects(DoublerNode.aPercent, DoublerNode.aOutput)
    DoublerNode.attributeAffects(DoublerNode.aInputA, DoublerNode.aOutput)
    DoublerNode.attributeAffects(DoublerNode.aInputB, DoublerNode.aOutput)

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'Asim', '1.0', 'Any')
    try:
        plugin.registerNode('doublerNode', DoublerNode.kPluginNodeId, creator, initialize)
    except:
        raise RuntimeError, 'Failed to register node'

def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(DoublerNode.kPluginNodeId)
    except:
        raise RuntimeError, 'Failed to register node'