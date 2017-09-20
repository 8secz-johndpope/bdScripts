import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import sys, math
import pymel.core as pm
import pymel.core.datatypes as dt
import mayaDecorators as dec

reload(dec)


# pymel
def bdMirrorCtrl():
    selection = pm.ls(sl=True)
    if selection:
        try:
            source, target = pm.ls(sl=True)
        except:
            pm.warning('Select source and target controller')
            return

        sourceShape = source.getShape()
        if sourceShape.type() != 'nurbsCurve':
            pm.error('Selected source is not nurbs curve')
            return

        targetCvsPos = [(dt.Point(-x.x, x.y, x.z)) for x in sourceShape.getCVs(space='world')]

        targetShape = target.getShape()

        if targetShape.type() != 'nurbsCurve':
            pm.error('Selected target is not nurbs curve')
            return
        targetShape.setCVs(targetCvsPos, space='world')
        targetShape.updateCurve()


    else:
        print 'Select source and target controller'


@dec.undoable
def mirrorCtrlAPI():
    mDagPath = om.MDagPath()
    mSelList = om.MSelectionList()

    om.MGlobal.getActiveSelectionList(mSelList)
    srcCurvePointAray = om.MPointArray()
    destCurvePointAray = om.MPointArray()

    numSel = mSelList.length()

    if numSel == 2:

        mSelList.getDagPath(0, mDagPath)

        if mDagPath.hasFn(om.MFn.kNurbsCurve):
            srcCurveFn = om.MFnNurbsCurve(mDagPath)
            srcCurveFn.getCVs(srcCurvePointAray, om.MSpace.kWorld)

            mSelList.getDagPath(1, mDagPath)
            if mDagPath.hasFn(om.MFn.kNurbsCurve):
                destCurveFn = om.MFnNurbsCurve(mDagPath)
                for i in range(srcCurvePointAray.length()):
                    destCurvePointAray.append(
                        om.MPoint(-srcCurvePointAray[i].x, srcCurvePointAray[i].y, srcCurvePointAray[i].z))
                destCurveFn.setCVs(destCurvePointAray, om.MSpace.kWorld)
                destCurveFn.updateCurve()


def matchCtrlAPI():
    mDagPath = om.MDagPath()
    mSelList = om.MSelectionList()

    om.MGlobal.getActiveSelectionList(mSelList)
    srcCurvePointAray = om.MPointArray()
    destCurvePointAray = om.MPointArray()

    numSel = mSelList.length()

    if numSel == 2:

        mSelList.getDagPath(0, mDagPath)

        if mDagPath.hasFn(om.MFn.kNurbsCurve):
            srcCurveFn = om.MFnNurbsCurve(mDagPath)
            srcCurveFn.getCVs(srcCurvePointAray, om.MSpace.kWorld)

            mSelList.getDagPath(1, mDagPath)
            if mDagPath.hasFn(om.MFn.kNurbsCurve):
                destCurveFn = om.MFnNurbsCurve(mDagPath)
                for i in range(srcCurvePointAray.length()):
                    destCurvePointAray.append(
                        om.MPoint(srcCurvePointAray[i].x, srcCurvePointAray[i].y, srcCurvePointAray[i].z))
                destCurveFn.setCVs(destCurvePointAray, om.MSpace.kWorld)
                destCurveFn.updateCurve()
