def bdPlayblastFolder(folder, outFolder, characterRig, codec, camera, referenceCam='', cleanName=0):
    CHARACTER_RIG = characterRig
    print CHARACTER_RIG
    animDir = folder
    animFiles = [os.path.splitext(f)[0] for f in sorted(os.listdir(animDir)) if f.endswith('.ma')]
    if not cleanName:
        lastVersions = []
        temp = []
        for f in animFiles:
            if '_v' in f:
                fileName = f[:-4]
                temp.append(fileName)

        temp1 = list(set(temp[:]))

        for t in temp1:
            lastVersions.append(t + '_v0' + str(temp.count(t)))

        animFiles = lastVersions
    for f in sorted(animFiles):
        pathFile = animDir + f + '.ma'
        if outFolder == '':
            pathMovie = 'movies/' + f
        else:
            pathMovie = outFolder + f

        if os.path.isfile(pathFile):
            print pathFile
        else:
            print 'no file'
        checkFileCallbackId = OM.MSceneMessage.addCheckFileCallback(OM.MSceneMessage.kBeforeReferenceCheck,
                                                                    bdReplaceRig)
        pm.openFile(pathFile, f=1)
        pm.setAttr("defaultResolution.width", 1280)
        pm.setAttr("defaultResolution.height", 720)
        bdSetCamera(camera, referenceCam)
        pm.playblast(format='avi', filename=pathMovie, forceOverwrite=1, sequenceTime=0, clearCache=0, viewer=0,
                     showOrnaments=1, fp=4, percent=100, compression=codec, quality=100, widthHeight=[1280, 720])
        OM.MMessage.removeCallback(checkFileCallbackId)


def bdSetCamera(camera, referenceCam):
    if referenceCam:
        pm.createReference(referenceCam, namespace="CAM")
        camera = pm.ls('CAM:*', type='camera')[0]

    perspModel = "".join(pm.getPanel(withLabel='Persp View'))
    pm.setFocus(perspModel)
    perspView = pm.getPanel(wf=1)
    pm.lookThru(perspView, camera)
    # pm.modelPanel (perspView, query=1,label=1)
    pm.modelEditor(perspView, e=1, alo=0)
    pm.modelEditor(perspView, e=1, polymeshes=1, grid=0)
    pm.modelEditor(perspView, e=1, displayAppearance='smoothShaded', displayTextures=1)
    perspCam = pm.ls('persp', type='transform')[0]
    # perspCam.setTranslation([0,10,60])
    # perspCam.setRotation([0,0,0])


def bdPlayblastFolderVP2(folder, outFolder, codec, cleanName=0):
    animDir = folder
    animFiles = [os.path.splitext(f)[0] for f in sorted(os.listdir(animDir)) if f.endswith('.mb')]
    if not cleanName:
        lastVersions = []
        temp = []
        for f in animFiles:
            if '_v' in f:
                fileName = f[:-4]
                temp.append(fileName)

        temp1 = list(set(temp[:]))

        for t in temp1:
            lastVersions.append(t + '_v0' + str(temp.count(t)))

        animFiles = lastVersions
    for f in sorted(animFiles):
        pathFile = animDir + f + '.mb'
        if outFolder == '':
            pathMovie = 'movies/' + f
        else:
            pathMovie = outFolder + f

        if os.path.isfile(pathFile):
            print pathFile
        else:
            print 'no file'
        # checkFileCallbackId = OM.MSceneMessage.addCheckFileCallback(OM.MSceneMessage.kBeforeReferenceCheck, bdReplaceRig)
        pm.mel.eval('ActivateViewport20')
        pm.openFile(pathFile, f=1)
        pm.mel.eval('setCameraNamesVisibility 0')
        pm.select('zoo:body')
        pm.hyperShade(assign='zoo:cat_body_linkSHD')
        pm.select(cl=1)

        pm.setAttr("defaultResolution.width", 1280)
        pm.setAttr("defaultResolution.height", 720)

        bdSetCameraVP2('cam:cameraShape1')

        pm.playblast(format='avi', filename=pathMovie, forceOverwrite=1, sequenceTime=0, clearCache=0, viewer=0,
                     showOrnaments=1, fp=4, percent=100, compression=codec, quality=100, widthHeight=[1280, 720])
        # OM.MMessage.removeCallback(checkFileCallbackId)


def bdSetCameraVP2(cam):
    pm.createReference("P:/smurfs/working_project/cameras/worldcup_cam.ma", ns='cam')

    pm.mel.eval('setNamedPanelLayout \"Single Perspective View\"');
    perspModel = "".join(pm.getPanel(withLabel='Persp View'))
    pm.setFocus(perspModel)
    perspView = pm.getPanel(wf=1)
    pm.lookThru(perspView, cam)
    # pm.modelPanel (perspView, query=1,label=1)
    pm.modelEditor(perspView, e=1, alo=0)
    pm.modelEditor(perspView, e=1, polymeshes=1, imagePlane=1, grid=0)
    pm.modelEditor(perspView, e=1, displayAppearance='smoothShaded', displayTextures=1, wireframeOnShaded=0)
    consolidate = pm.mel.eval('checkMemoryForConsolidatedWorld()')
    if consolidate:
        pm.modelEditor(perspView, e=1, rnm="vp2Renderer", rom='')

# recursiveCurveOnGuidesBuilder.py
