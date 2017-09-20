import pymel.core as pm

armBones = ['Arm1', 'Arm2', 'Arm3']


def bdConnectChains(side):
    bindChain = pm.ls(side + armBones[0] + '_bnd')[0]
    ikfkCon = pm.ls(side + 'Arm_ik_ctrl', type='transform')[0]

    if ikfkCon.hasAttr('fkIk'):
        print 'has attr already'
    else:
        pm.addAttr(ikfkCon, ln='fkIk', nn='fkIk', at='float')
        ikfkCon.attr('fkIk').setMin(0)
        ikfkCon.attr('fkIk').setMax(1)
        ikfkCon.attr('fkIk').setKeyable(True)

    fkJnt = pm.ls(bindChain.name().replace('bnd', 'fk'))[0]
    ikJnt = pm.ls(bindChain.name().replace('bnd', 'ik'))[0]

    bdCreateBlend(bindChain, fkJnt, ikJnt, ikfkCon)

    bindChainChildren = bindChain.listRelatives(c=True, type='joint', ad=True)
    bindChainChildren.reverse()
    bindChainChildren = bindChainChildren[:3]
    for child in bindChainChildren:
        fkJnt = pm.ls(child.name().replace('bnd', 'fk'))[0]
        ikJnt = pm.ls(child.name().replace('bnd', 'ik'))[0]
        print child
        bdCreateBlend(child, fkJnt, ikJnt, ikfkCon)


def bdCreateBlend(bindJnt, fkJnt, ikJnt, ikfkCon):
    blendColorPos = pm.createNode('blendColors', name=bindJnt.name().replace('bnd', 'pos_bc'))
    blendColorRot = pm.createNode('blendColors', name=bindJnt.name().replace('bnd', 'rot_bc'))
    blendColorScl = pm.createNode('blendColors', name=bindJnt.name().replace('bnd', 'scl_bc'))

    ikfkCon.attr('fkIk').connect(blendColorPos.blender)
    ikfkCon.attr('fkIk').connect(blendColorRot.blender)
    ikfkCon.attr('fkIk').connect(blendColorScl.blender)

    fkJnt.translate.connect(blendColorPos.color1)
    ikJnt.translate.connect(blendColorPos.color2)
    blendColorPos.output.connect(bindJnt.translate)

    fkJnt.rotate.connect(blendColorRot.color1)
    ikJnt.rotate.connect(blendColorRot.color2)
    blendColorRot.output.connect(bindJnt.rotate)

    fkJnt.scale.connect(blendColorScl.color1)
    ikJnt.scale.connect(blendColorScl.color2)
    blendColorScl.output.connect(bindJnt.scale)


def bdBuildDrvChain(side, drvType):
    newChain = []
    for bone in armBones:
        jntNonRoll = pm.ls(side + bone + '_bnd', type='joint')[0]
        newJnt = pm.duplicate(jntNonRoll, po=1, name=jntNonRoll.name().replace('bnd', drvType))[0]
        newChain.append(newJnt)

    newChain.reverse()
    for i in range(len(newChain) - 1):
        print newChain[i], newChain[i + 1]
        pm.parent(newChain[i], newChain[i + 1])
    # shoulderJnt = pm.ls(side + armBones[0] + '_bnd', type='joint')[0]
    # ikChainStart = pm.duplicate(shoulderJnt)[0]
    # ikChainStart.rename(shoulderJnt.name().replace('bnd',drvType))
    # ikRelatives = ikChainStart.listRelatives(ad=True,type='joint',pa=True)
    # ikRelatives.reverse()
    # toDelete = ikRelatives[3:]
    # ikRelatives = ikRelatives[:3]
    # pm.delete(toDelete)
    #
    # for jnt in ikRelatives:
    #     jnt.rename(jnt.name().split('|')[-1].replace('bnd',drvType))
    #
    # ikChain = [ikChainStart] + ikRelatives
    return newChain


def bdRigIkArm(side):
    # ikChain = bdBuildDrvChain(side,'ik')

    armIk = pm.ikHandle(sol='ikRPsolver', sticky='sticky', startJoint=ikChain[0], endEffector=ikChain[2],
                        name=side + '_hand_ikHandle')[0]
    handIk = pm.ikHandle(sol='ikSCsolver', sticky='sticky', startJoint=ikChain[2], endEffector=ikChain[3],
                         name=side + '_palm_ikHandle')[0]

    ikHandlesGrp = pm.group([armIk, handIk], n=side + '_hand_ikHandles_GRP')
    wristPos = ikChain[2].getTranslation(space='world')
    ikHandlesGrp.setPivots(wristPos)
    '''
    pvAnim = pm.ls(side + '_elbow_ik_anim', type='transform')[0]
    if pvAnim:
        pm.poleVectorConstraint(pvAnim,armIk[0])

    '''
    ikAnimCtrl = pm.ls(side + 'Arm_ik_ctrl', type='transform')[0]
    pm.parentConstraint(ikAnimCtrl, ikHandlesGrp, mo=True)


def bdScaleChain(side):
    pm.select(cl=True)
    ikAnimCon = pm.ls(side + 'Arm_ik_ctrl', type='transform')[0]
    armBonesNames = ['Arm1', 'Arm2', 'Arm3']

    scaleBones = []
    for bone in armBonesNames:
        scaleBone = pm.ls(side + '_' + bone + '_SCL')[0]
        scaleBones.append(scaleBone)

    ikBones = []
    for bone in armBonesNames:
        armBone = pm.ls(side + '_' + bone + '_ik')[0]
        ikBones.append(armBone)

    print scaleBones
    print armBones

    distance1 = pm.createNode('distanceBetween', name=side + '_uppArm_length')
    distance2 = pm.createNode('distanceBetween', name=side + '_lowArm_length')
    distanceStraight = pm.createNode('distanceBetween', name=side + '_straightArm_length')
    adlDistance = pm.createNode('addDoubleLinear', name=side + '_armLength_ADL')
    condDistance = pm.createNode('condition', name=side + '_armLength_CND')
    condDistance.colorIfTrueR.set(1)
    condDistance.secondTerm.set(1)
    condDistance.operation.set(5)

    mdScaleFactor = pm.createNode('multiplyDivide', name=side + '_arm_scaleFactor_MD')
    mdScaleFactor.operation.set(2)

    scaleBones[0].rotatePivotTranslate.connect(distance1.point1)
    scaleBones[1].rotatePivotTranslate.connect(distance1.point2)
    scaleBones[0].worldMatrix.connect(distance1.inMatrix1)
    scaleBones[1].worldMatrix.connect(distance1.inMatrix2)

    scaleBones[1].rotatePivotTranslate.connect(distance2.point1)
    scaleBones[2].rotatePivotTranslate.connect(distance2.point2)
    scaleBones[1].worldMatrix.connect(distance2.inMatrix1)
    scaleBones[2].worldMatrix.connect(distance2.inMatrix2)

    scaleBones[0].rotatePivotTranslate.connect(distanceStraight.point1)
    ikAnimCon.rotatePivotTranslate.connect(distanceStraight.point2)
    scaleBones[0].worldMatrix.connect(distanceStraight.inMatrix1)
    ikAnimCon.worldMatrix.connect(distanceStraight.inMatrix2)

    distance1.distance.connect(adlDistance.input1)
    distance2.distance.connect(adlDistance.input2)

    adlDistance.output.connect(mdScaleFactor.input2X)
    distanceStraight.distance.connect(mdScaleFactor.input1X)

    mdScaleFactor.outputX.connect(condDistance.firstTerm)
    mdScaleFactor.outputX.connect(condDistance.colorIfFalseR)

    condDistance.outColorR.connect(ikBones[0].scaleX)
    condDistance.outColorR.connect(ikBones[1].scaleX)


def bdRigArm(side):
    bdBuildDrvChain(side, 'fk')
    # bdRigIkArm(side)
    # bdConnectChains(side)
