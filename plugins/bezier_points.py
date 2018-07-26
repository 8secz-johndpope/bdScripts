import maya.api.OpenMaya as om


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

class BezierPoints(om.MPxNode):
    kPluginNodeId = om.MTypeId(0x00047251)

    aInput1 = om.MObject()
    aInput2 = om.MObject()
    aInput3 = om.MObject()
    aPercent = om.MObject()

    aOutput = om.MObject()


    def __init__(self):
        om.MPxNode.__init__(self)

    def compute(self, plug, data):
        p0 = data.inputValue(BezierPoints.aInput1).asVector()
        p1 = data.inputValue(BezierPoints.aInput2).asVector()
        p2 = data.inputValue(BezierPoints.aInput3).asVector()
        t = data.inputValue(BezierPoints.aPercent).asFloat()

        #bezier quadratic
        sum = pow(1 - t,2)*p0 + 2*(1 - t)*t*p1 + pow(t,2) * p2

        # setting the output
        hOutput = data.outputValue(BezierPoints.aOutput)
        hOutput.set3Double(sum[0], sum[1], sum[2])

        data.setClean(plug)

    @staticmethod
    def creator():
        return BezierPoints()

    @staticmethod
    def initialize():
        nAttr = om.MFnNumericAttribute()

        BezierPoints.aInput1 = nAttr.create('BPoint1', 'bp1', om.MFnNumericData.k3Double)
        BezierPoints.aInput2 = nAttr.create('BPoint2', 'bp2', om.MFnNumericData.k3Double)
        BezierPoints.aInput3 = nAttr.create('BPoint3', 'bp3', om.MFnNumericData.k3Double)

        BezierPoints.aPercent = nAttr.create('percent', 'per', om.MFnNumericData.kFloat, 0.0)
        nAttr.writable = True
        nAttr.keyable = True
        nAttr.setSoftMin(0.0)
        nAttr.setSoftMax(1.0)

        BezierPoints.aOutput = nAttr.create("outResult", "out", om.MFnNumericData.k3Double)
        nAttr.writable = True

        BezierPoints.addAttribute(BezierPoints.aInput1)
        BezierPoints.addAttribute(BezierPoints.aInput2)
        BezierPoints.addAttribute(BezierPoints.aInput3)

        BezierPoints.addAttribute(BezierPoints.aPercent)
        BezierPoints.addAttribute(BezierPoints.aOutput)


        BezierPoints.attributeAffects(BezierPoints.aPercent, BezierPoints.aOutput)
        BezierPoints.attributeAffects(BezierPoints.aInput1, BezierPoints.aOutput)
        BezierPoints.attributeAffects(BezierPoints.aInput2, BezierPoints.aOutput)
        BezierPoints.attributeAffects(BezierPoints.aInput3, BezierPoints.aOutput)


#define new attributes here

def initializePlugin(obj):
    plugin = om.MFnPlugin(obj, 'bd', '1.0', 'Any')
    try:
        plugin.registerNode('bezierPoints', BezierPoints.kPluginNodeId, BezierPoints.creator, BezierPoints.initialize)
    except:
        raise RuntimeError, 'Failed to register node'

def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(BezierPoints.kPluginNodeId)
    except:
        raise RuntimeError, 'Failed to deregister node'