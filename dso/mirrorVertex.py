import pymel.core as pm
import maya.OpenMaya as om


def mirrorVtx():
    selection = pm.ls(sl=1, fl=1)
    if selection and len(selection) == 2:
        srcVert = selection[0]
        destVert = selection[1]
        srcPos = srcVert.getPosition(space='world')
        destPos = [srcPos[0] * -1, srcPos[1], srcPos[2]]
        destVert.setPosition(destPos, space='world')


class MeshMirror():
    def __init__(self):
        self.mesh = None
        self.vertsPos = []
        self.vertices = []
        self.mirrorVertices = []
        self.initMesh()

    def initMesh(self):
        selection = pm.ls(sl=1)
        if selection:
            shape = selection[0].getShape()
            if shape and shape.type() == 'mesh':
                self.mesh = shape
                self.vertsPos = self.mesh.getPoints(space='world')
                # self.vertices = self.mesh.getVertices()
                # print self.vertices

    def mirrorSelection(self, threshhold):
        selection = pm.ls(sl=1, fl=1)
        self.mirrorVertices = []
        if selection:
            for vtx in selection:
                mirrorVtx = self.findMirror(vtx, threshhold)
                if mirrorVtx:
                    self.mirrorVertices.append(mirrorVtx)
                    self.setMirrorPos(vtx, mirrorVtx)

        pm.select(self.mirrorVertices, tgl=1)

    def findMirror(self, vtx, threshhold):
        vtxPos = vtx.getPosition(space='world')
        for pos in self.vertsPos:
            if pos.x < 0:
                deltaX = vtxPos.x + pos.x
                deltaY = vtxPos.y - pos.y
                deltaZ = vtxPos.z - pos.z
                if (deltaX > (-1) * threshhold and deltaX < threshhold) and (
                        deltaY > (-1) * threshhold and deltaY < threshhold) and (
                        deltaZ > (-1) * threshhold and deltaZ < threshhold):
                    index = self.vertsPos.index(pos)
                    transform = self.mesh.getParent()
                    mirrorVtx = transform.name() + '.vtx[' + str(index) + ']'
                    return pm.ls(mirrorVtx)[0]

    def setMirrorPos(self, srcVert, destVert):
        srcPos = srcVert.getPosition(space='world')
        destPos = [srcPos[0] * -1, srcPos[1], srcPos[2]]
        destVert.setPosition(destPos, space='world')


class MeshMirrorApi():
    def __init__(self):
        self.mesh = None
        self.vertsPos = []
        self.vertices = []
        self.mirrorVertices = []
        self.initMesh()

    def initMesh(self):
        selection = pm.ls(sl=1)
        if selection:
            shape = selection[0].getShape()
            if shape and shape.type() == 'mesh':
                self.mesh = shape
                self.vertsPos = self.getVertPos()
                print self.vertsPos

    def getVertPos():
        selection = om.MSelectionList()

        # 2 # get the selected object in the viewport and put it in the selection list
        om.MGlobal.getActiveSelectionList(selection)

        # 3 # initialize a dagpath object
        dagPath = om.MDagPath()

        # 4 # populate the dag path object with the first object in the selection list
        selection.getDagPath(0, dagPath)

        # ___________Query vertex position ___________

        # initialize a Point array holder
        vertPoints = om.MPointArray()

        # create a Mesh functionset from our dag object
        mfnObject = om.MFnMesh(dagPath)

        # call the function "getPoints" and feed the data into our pointArray
        mfnObject.getPoints(vertPoints)

        return vertPoints

    def mirrorSelection(self, threshhold):
        selection = pm.ls(sl=1, fl=1)
        self.mirrorVertices = []
        if selection:
            for vtx in selection:
                mirrorVtx = self.findMirror(vtx, threshhold)
                if mirrorVtx:
                    self.mirrorVertices.append(mirrorVtx)
                    self.setMirrorPos(vtx, mirrorVtx)

        pm.select(self.mirrorVertices, tgl=1)

    def findMirror(self, vtx, threshhold):
        vtxPos = vtx.getPosition(space='world')
        for pos in self.vertsPos:
            if pos.x < 0:
                deltaX = vtxPos.x + pos.x
                deltaY = vtxPos.y - pos.y
                deltaZ = vtxPos.z - pos.z
                if (deltaX > (-1) * threshhold and deltaX < threshhold) and (
                        deltaY > (-1) * threshhold and deltaY < threshhold) and (
                        deltaZ > (-1) * threshhold and deltaZ < threshhold):
                    index = self.vertsPos.index(pos)
                    transform = self.mesh.getParent()
                    mirrorVtx = transform.name() + '.vtx[' + str(index) + ']'
                    return pm.ls(mirrorVtx)[0]

    def setMirrorPos(self, srcVert, destVert):
        srcPos = srcVert.getPosition(space='world')
        destPos = [srcPos[0] * -1, srcPos[1], srcPos[2]]
        destVert.setPosition(destPos, space='world')
