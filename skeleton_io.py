###############################################################################
#    Module:       common
#    Date:         14.06.2018
#    Author:       Bogdan Diaconu
#
#    Description:  Utility module to save skeleton information as a json file in order to be able to re-create it
#
#
#    Globals:
#
#    Classes:       SkeletonIO - used for immport/export joints data as json files and creating skeletons
#
#    Functions:
#    Usage:
#    Export example, replace name and path with the desired value
#
# import autorig.utils.skeleton as skl
# template = skl.SkeletonIO(name='generic_skeleton', path='d:\\')
# template.export_info()
#
#    Import example, replace name and path with the desired value
#
# import autorig.utils.skeleton as skl
# template = skl.SkeletonIO(name='generic_skeleton', path='d:\\')
# template.export_info()
# template.create_skeleton()
#
###############################################################################
import pymel.core as pm
import json
import os
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import maya.OpenMayaUI as mui
import shiboken2
import utils.libWidgets as UI
reload(UI)

sklio_win = 'sklio_win'


def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)


class SkeletonIO(object):
    def __init__(self, name='template', path='', root='root_jnt'):
        '''
        :param name:    template name, will be used as file name as well
        :param path:    the path for the export / import file
        :param root:    root of the skeleton, must be unique in scene
        '''
        self.name = name
        self.info = {}
        self.path = path
        self.root = root
        self.counter = 0

    def export_info(self):
        '''
        Exports the skeleton info as a dictionary using json
        :return:
        '''
        find = pm.ls(self.root)
        if find:
            root = find[0]
            children = pm.listRelatives(root, ad=1, type='joint')
            self.add_info(root)
            for c in children:
                self.add_info(c)
            if os.path.isdir(self.path):
                with open(os.path.join(self.path, self.name + '.json'), 'w') as outfile:
                    json.dump(self.info, outfile, sort_keys=True, indent=4)
            else:
                pm.warning('Path provided is not valid')
        else:
            pm.warning('No valid root provided')

    def import_info(self):
        '''
        Imports the skeleton info as a dictionary using json
        :return:
        '''
        file_path = os.path.join(self.path, self.name + '.json')
        if os.path.isfile(file_path):
            with open(file_path, 'r') as inDataFile:
                info = json.load(inDataFile)
                self.set_info(info)

    def create_skeleton(self):
        '''
        Creates a skeleton based in the information from the file
        :return:
        '''
        # first we create the joints
        for index in self.info:
            jnt_info = self.info[index]
            pm.select(cl=1)
            jnt = pm.joint(name=jnt_info['name'])
            jnt.setTranslation(jnt_info['position'], space='world')
            jnt.attr('rotate').set(jnt_info['rotation'])
            jnt.attr('jointOrient').set(jnt_info['joint_orient'])
        # we need a second for to parent the joints
        for index in self.info:
            jnt_info = self.info[index]
            pm.select(cl=1)
            if jnt_info['parent'] != 'none':
                pm.parent(jnt_info['name'], jnt_info['parent'])

    def add_info(self, node):
        '''
        Adds the name, position, rotation, jointOrientation and parent for the node joint to self.info
        :param node: name of the joint to extract the information
        :return:
        '''
        pm.select(cl=1)
        node_info = dict()
        node_info['name'] = node.name()
        temp_node = pm.duplicate(node,n=node.name() + '_temp',  po=1)[0]
        try:
            pm.parent(temp_node, w=1)
        except:
            print 'Joint already under world'
        position = [v for v in temp_node.getTranslation(space='world')]
        rotation = [v for v in temp_node.attr('rotate').get()]
        node_info['position'] = position
        node_info['rotation'] = rotation
        if node.getParent():
            parent = node.getParent()
            node_info['parent'] = parent.name()
        else:
            node_info['parent'] = 'none'

        joint_orient = [v for v in temp_node.attr('jointOrient').get()]
        node_info['joint_orient'] = joint_orient
        self.info[self.counter] = node_info
        self.counter += 1
        pm.delete(temp_node)

    def get_info(self):
        '''
        getter
        :return: a copy of the self.info dict
        '''
        return self.info.copy()

    def set_info(self, info):
        '''
        setter
        :param info: sets self.info to this
        :return:
        '''
        self.info = info


class SkeletonUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):

        super(SkeletonUI, self).__init__(parent)
        self.setWindowTitle('Skeletion IO')
        self.setObjectName(sklio_win)

        self.sklFolder = UI.LabelEditWidget(label='Skeleton files folder')
        self.setupUI()

    def setupUI(self):
        centralWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)

        pathLayout = UI.HorBox()
        browseBtn = UI.ButtonB('...')

        pathLayout.addWidget(self.sklFolder)
        pathLayout.addWidget(browseBtn)

        btnLayout = UI.HorBox()
        saveBtn = UI.ButtonB('Save skeleton')
        loadBtn = UI.ButtonB('Load skeleton')
        btnLayout.addWidget(saveBtn)
        btnLayout.addWidget(loadBtn)

        # mainLayout.addLayout(pathLayout)
        mainLayout.addLayout(btnLayout)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        # browseBtn.clicked.connect(self.browseSklFolder)
        saveBtn.clicked.connect(self.saveSkl)
        loadBtn.clicked.connect(self.loadSkl)

    def loadSkl(self):
        sceneName = pm.sceneName()
        if sceneName:
            path, file = os.path.split(sceneName)
            filePath = pm.fileDialog2(dir=path, ds=1, fm=1, fileFilter='Skin Files (*.json)')
            if not filePath:
                return

            path, fileName = os.path.split(filePath[0])
            import_skl = SkeletonIO(name=os.path.splitext(fileName)[0], path=path, root='root')
            import_skl.import_info()
            import_skl.create_skeleton()


    def saveSkl(self):
        sceneName = pm.sceneName()
        if sceneName:
            path, file = os.path.split(sceneName)
            filePath = pm.fileDialog2(dir=path, ds=1, fm=0, fileFilter='Skin Files (*.json)'
                                      , cap='Save skeleton file ')
            if not filePath:
                return

            path, fileName = os.path.split(filePath[0])
            export_skl = SkeletonIO(name=os.path.splitext(fileName)[0], path=path, root='root')
            export_skl.export_info()


def openTool():
    if pm.window(sklio_win, exists=True, q=True):
        pm.deleteUI(sklio_win)

    tool = SkeletonUI()
    tool.show()
    tool.resize(300, 80)