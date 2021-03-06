import pymel.core as pm

'''     UTILS     '''


def bdGetTRS(widg):
    pos = widg.getTranslation(space='world')
    rot = widg.getRotation(space='world')
    scl = widg.getScale()
    return pos, rot, scl


def bdSetTRS(widg, pos, rot, scl):
    widg.setTranslation([pos[0] * -1, pos[1], pos[2]], space='world')
    widg.setRotation([rot[0], rot[1] * -1, rot[2] * -1], space='world')
    widg.setScale(scl)


'''     END UTILS     '''

'''     LEFT -> RIGHT EYELIDS     '''


def bdMirrorEyes():
    leftSideMainWidgets = ['leftEye1_Widget', 'leftLid*1_Widget', 'leftBrow*1_Widget', 'leftLipUpper1_Widget',
                           'leftLipCorner1_Widget', 'leftLipLower1_Widget']

    for mainWidget in leftSideMainWidgets:
        leftSideMain = pm.ls(mainWidget, type='transform')
        rightSideMain = pm.ls(mainWidget.replace('left', 'right'), type='transform')
        leftSideWidg = pm.ls(mainWidget + '?', type='transform')
        rightSideWidg = pm.ls(mainWidget.replace('left', 'right') + '?', type='transform')

        for widget in leftSideMain:
            pos, rot, scl = bdGetTRS(widget)
            bdSetTRS(rightSideMain[leftSideMain.index(widget)], pos, rot, scl)
            leftChildrenWidgets = widget.getChildren(c=1, type='transform')[0:-1]
            rightChildrenWidgets = rightSideMain[leftSideMain.index(widget)].getChildren(c=1, type='transform')[0:-1]

            for child in leftChildrenWidgets:
                pos, rot, scl = bdGetTRS(child)
                bdSetTRS(rightChildrenWidgets[leftChildrenWidgets.index(child)], pos, rot, scl)


bdMirrorEyes()
