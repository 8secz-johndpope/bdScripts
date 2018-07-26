import pymel.core as pm
import json, os, random, re

import mayaDecorators as decorators

import pymel.core.datatypes as dt
import maya.api.OpenMaya as om



def bdSelectSkinJnt():
    selection = pm.ls(sl=True)
    if selection:
        skinCls = pm.mel.eval('findRelatedSkinCluster ' + selection[0])
        if skinCls:
            jnts = pm.skinCluster(skinCls, q=True, influence=True)
            names = [str(jnt) for jnt in jnts]
            strList = ' '.join(names)
            pm.select(jnts)
            return 'Selected \' %s \' is influenced by: %s ' % (selection[0].name(), strList)
        else:
            return 'Selected has no skin cluster!'

    else:
        return 'No skinned mesh selected !'


def bdSetBindPose():
    selection = pm.ls(sl=True, type='joint')
    bindPose = ''
    skRoot = None
    if selection and len(selection) == 1:
        bindPose = pm.dagPose(save=True, bp=1)
        skRoot = selection[0]
    else:
        findRoot = pm.ls('Skeleton_Root', type='joint')
        if findRoot and len(findRoot) == 1:
            skRoot = findRoot[0]
            bndPoses = pm.listConnections('%s.bindPose' % skRoot.name())
            if bndPoses:
                strPoses = ''
                for p in bndPoses:
                    strPoses += (p.name() + ' ')
                return '%s has already the following bind pose(s): %s' % (skRoot.name(), strPoses)
            else:
                bindPose = pm.dagPose(skRoot, save=True, bp=1)
        else:
            return 'No selection and no Skeleton_Root found !!!'

    return 'Created %s for %s' % (bindPose, skRoot.name())


def bdDelBindPose():
    bindPoses = pm.ls(type='dagPose')
    if bindPoses:
        strList = ''
        for p in bindPoses:
            strList += (p.name() + ' ')
        pm.delete(bindPoses)
        return 'The following bind poses were deleted: %s ' % strList
    else:
        return 'Didn\'t find any  bind poses'


def bdAssumeBindPose():
    selection = pm.ls(sl=True, type='joint')
    bindPose = ''
    skRoot = None
    if selection and len(selection) == 1:
        skRoot = selection[0]
        poses = pm.listConnections('%s.bindPose' % skRoot.name())
        if len(poses) > 1:
            return 'Multiple poses found for selection, you have to create only one !!!'
        else:
            pm.dagPose(poses[0], restore=True)
            return 'Bind pose \' %s \' restored ' % poses[0].name()
    else:
        findRoot = pm.ls('Skeleton_Root', type='joint')
        if findRoot and len(findRoot) == 1:
            skRoot = findRoot[0]
            poses = pm.listConnections('%s.bindPose' % skRoot.name())
            if len(poses) > 1:
                return 'Multiple poses found for selection, you have to create only one !!!'
            else:
                pm.dagPose(poses[0], restore=True)
                return 'Bind pose \' %s \' restored ' % poses[0].name()
        else:
            return 'Did\'t find a Skeleton_Root'


### Vertex skinnining
def getSkinCluster(shape):
    history = pm.listHistory(shape, pruneDagObjects=True, il=2)
    if not history:
        return None
    skins = [s for s in history if pm.nodeType(s) == 'skinCluster']

    if skins:
        return skins[0].name()
    return None


def getVertexWeight():
    '''
    Category: Skinning
    Copy a vertex weight to another
    Select 2 vertices, will copy the weights from 1st selected to second
    '''
    vtx = pm.ls(fl=1, os=1)
    print vtx

    if len(vtx) == 2:
        if vtx[0].__class__.__name__ == 'MeshVertex' and vtx[1].__class__.__name__ == 'MeshVertex':

            shape = vtx[0].node()
            skinCls = getSkinCluster(shape)
            influences = pm.skinPercent(skinCls, vtx[0].name(), query=True, transform=None)
            weights = pm.skinPercent(skinCls, vtx[0].name(), query=True, v=True)
            normWeights = [float(i) / sum(weights) for i in weights]

            tvList = []
            for i in range(len(influences)):
                tvList.append((influences[i], normWeights[i]))

            pm.skinPercent(skinCls, vtx[1], transformValue=tvList)


def labelJoints():
    '''
    Category: Skinning
    Labels the joints based on their name
    '''
    for jnt in pm.ls(sl=1):
        jnt.attr("type").set(18)
        if 'l_' in jnt.name():
            jnt.attr("side").set(1)
            jnt.attr("otherType").set(jnt.name()[2:])
        elif 'r_' in jnt.name():
            jnt.attr("side").set(2)
            jnt.attr("otherType").set(jnt.name()[2:])
        else:
            jnt.attr("side").set(0)
            jnt.attr("otherType").set(jnt.name())