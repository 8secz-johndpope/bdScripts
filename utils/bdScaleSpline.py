import pymel.core as pm


class bdScaleIkChain():
    def __init__(self, *argv, **kargv):
        self.splineCurve = ''
        self.startJoint = kargv.setdefault('startJoint')
        self.condition = kargv.setdefault('condition')
        self.bdBuildScaleSystem(self.startJoint, self.condition)
        self.jointChain = []
        self.ikSpline = ''
        self.splineCurveScl = ''

    def bdBuildScaleSystem(self, startJoint, condition):
        print startJoint.name()
        self.ikSpline = pm.listConnections(startJoint, type='ikHandle')[0]
        print self.ikSpline
        solver = self.ikSpline.ikSolver.inputs()[0]
        print solver
        if 'ikSplineSolver' in solver.name():
            self.bdBuildSplineSolverScale(condition)
        elif ('ikRPsolver' in solver.name()) or ('ikSCsolver' in solver.name()):
            self.bdBuildRPSolverScale(condition)

    def bdBuildSplineSolverScale(self, condition):
        self.splineCurve = pm.listConnections(self.ikSpline, type='nurbsCurve')[0]

        effector = pm.listConnections(self.ikSpline, source=True, type='ikEffector')[0]
        endJoint = pm.listConnections(effector, source=True, type='joint')[0]
        startJointChild = pm.listRelatives(self.startJoint, c=True, type='joint')[0]
        self.jointChain = []
        self.jointChain.append(self.startJoint)
        self.jointChain.append(startJointChild)
        while startJointChild.name() != endJoint.name():
            startJointChild = pm.listRelatives(startJointChild, c=True, type='joint')[0]
            self.jointChain.append(startJointChild)

        self.splineCurveScl = pm.duplicate(self.splineCurve, name=self.splineCurve.name().replace('crv', 'crv_scl'))
        strArclenSCL = pm.arclen(self.splineCurveScl, ch=True)
        strArclenCRV = pm.arclen(self.splineCurve, ch=True)
        arclenSCL = pm.ls(strArclenSCL)[0]
        arclenCRV = pm.ls(strArclenCRV)[0]
        arclenSCL.rename(self.splineCurveScl[0].name() + '_length')
        arclenCRV.rename(self.splineCurve.name() + '_length')

        mdScaleFactor = pm.createNode('multiplyDivide',
                                      name=self.splineCurve.name().replace('crv', 'crv_scaleFactor_md'))
        arclenCRV.arcLength.connect(mdScaleFactor.input1X)
        arclenSCL.arcLength.connect(mdScaleFactor.input2X)
        mdScaleFactor.operation.set(2)

        for jnt in self.jointChain:
            mdScaleFactor.outputX.connect(jnt.scaleX)

    def bdBuildRPSolverScale(self, condition):
        print 'RP Solver'

        # self.splineCurve = pm.listConnections(self.ikSpline, type = 'nurbsCurve')[0]
        pm.select(cl=True)
        ikGrp = pm.group(n=self.ikSpline.name() + '_grp')
        ikParent = self.ikSpline.getParent()
        ikPos = self.ikSpline.getTranslation(space='world')
        ikGrp.setTranslation(ikPos)
        pm.parent(ikGrp, ikParent)
        pm.parent(self.ikSpline, ikGrp)

        sclJnt = pm.duplicate(self.startJoint, parentOnly=True, name=self.startJoint.name().replace('ik', 'scl'))[0]
        effector = pm.listConnections(self.ikSpline, source=True, type='ikEffector')[0]
        endJoint = pm.listConnections(effector, source=True, type='joint')[0]
        startJointChild = pm.listRelatives(self.startJoint, c=True, type='joint')[0]
        self.jointChain = []
        self.jointChain.append(self.startJoint)
        self.jointChain.append(startJointChild)
        while startJointChild.name() != endJoint.name():
            startJointChild = pm.listRelatives(startJointChild, c=True, type='joint')[0]
            self.jointChain.append(startJointChild)

        jntPos = []
        for jnt in self.jointChain:
            pos = jnt.getTranslation(space='world')
            jntPos.append(pos)

        self.splineCurveScl = pm.curve(p=jntPos, degree=1, n=self.startJoint.name().replace('ik', 'crv_scl'))
        self.splineCurveScl.setPivots(jntPos[0])
        pm.parent(self.splineCurveScl, sclJnt)

        strArclenSCL = pm.arclen(self.splineCurveScl, ch=True)
        arclenSCL = pm.ls(strArclenSCL)[0]
        arclenSCL.rename(self.splineCurveScl.name() + '_length')
        distanceNode = pm.createNode('distanceBetween', name=self.startJoint.name().replace('ik', 'db'))

        sclJnt.rotatePivotTranslate.connect(distanceNode.point1)
        ikGrp.rotatePivotTranslate.connect(distanceNode.point2)
        sclJnt.worldMatrix.connect(distanceNode.inMatrix1)
        ikGrp.worldMatrix.connect(distanceNode.inMatrix2)

        mdScaleFactor = pm.createNode('multiplyDivide',
                                      name=self.splineCurveScl.name().replace('crv_scl', 'crv_scaleFactor_md'))
        distanceNode.distance.connect(mdScaleFactor.input1X)
        arclenSCL.arcLength.connect(mdScaleFactor.input2X)
        mdScaleFactor.operation.set(2)

        cndScaleFactor = pm.createNode('condition',
                                       name=self.splineCurveScl.name().replace('crv_scl', 'crv_scaleFactor_cnd'))
        distanceNode.distance.connect(cndScaleFactor.firstTerm)
        arclenSCL.arcLength.connect(cndScaleFactor.secondTerm)
        mdScaleFactor.outputX.connect(cndScaleFactor.colorIfTrueR)

        cndScaleFactor.operation.set(2)

        for jnt in self.jointChain[:2]:
            cndScaleFactor.outColorR.connect(jnt.scaleX)
