# Yet Another Rigging Tool or shortly yart
import bdRig.utils.qt_handlers as qt_handlers
from bdRig.utils.qt_handlers import QtCore, QtGui

import bdRig.system.guide as guide

import pymel.core as pm
import pymel.core.datatypes as dt
import re, os, shutil, glob, sys, inspect

import bdRig.utils.ui_utils as utils

reload(utils)

import bdRig.utils.mayaDecorators as decorators

reload(decorators)

from ..system import characterX as character

reload(character)

import bdRig.ui.widgets.armWidget as armWidget

reload(armWidget)

yartWin = 'yartWindow'


class YartUI(QtGui.QMainWindow):
    def __init__(self, parent=qt_handlers.get_maya_window()):
        super(YartUI, self).__init__(parent)
        self.setObjectName(yartWin)
        self.setWindowTitle('Rigging Kit 0.1')

        # --------------------------------- Character ---------------------------------------#
        self.currentCharacterName = ''
        self.charactersList = []
        self.currentCharacter = None
        self.characterGroup = None
        self.rootItem = None

        self.charSettingsVisible = 0
        self.charSettingsWidget = None

        self.settings_size_anim = None
        self.charGroup_size_anim = None
        # -------------------------------------------------------------------------------------#
        self.setupUI()
        self.show()
        self.resize(300, 300)

    def setupUI(self):
        centralWidget = QtGui.QWidget()
        centralWidget.setMinimumWidth(350)
        mainLayout = QtGui.QVBoxLayout()

        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        #
        # ----------------------------------Character Widget ----------------------------------#
        #
        self.charWidget = QtGui.QWidget()
        self.ch_setupUI()
        self.initializeChars()
        #
        # ----------------------------------Modules Widget ------------------------------------#
        #
        self.modulesBtnWidget = QtGui.QWidget()
        self.mb_setupUI()
        self.updateModulesTreeWidget()
        #
        # ----------------------------------Skeleton Widget -----------------------------------#
        #
        self.skeletonWidget = QtGui.QWidget()
        self.skeleton_setupUI()
        #
        # ----------------------------------Rigging Widget ------------------------------------#
        #
        self.rigWidget = QtGui.QWidget()
        self.rig_setupUI()
        # -------------------------------------------------------------------------------------#

        mainLayout.addWidget(self.charWidget)
        mainLayout.addWidget(self.modulesBtnWidget)
        mainLayout.addWidget(self.skeletonWidget)
        mainLayout.addWidget(self.rigWidget)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        # menu bar
        # self.addMenu()

    # --------------------------------------------Char Widget Functions ------------------------------------------#
    def ch_setupUI(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.ch_box = utils.TitledBox(title='Character', settings=1)

        nameLayout = QtGui.QHBoxLayout()
        nameLabel = QtGui.QLabel('Character name')
        nameLabel.setMaximumWidth(80)
        self.charNameCombo = QtGui.QComboBox()
        self.charNameCombo.setEditable(1)
        self.ch_nameBtn = QtGui.QPushButton('Create character')

        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.charNameCombo)

        self.characterSettingWidget = QtGui.QWidget()
        self.characterSettingWidget.setContentsMargins(0, 0, 0, 0)
        self.characterSettingWidget.setFixedHeight(0)

        self.ch_box.groupBoxLayout.addWidget(self.characterSettingWidget)
        self.ch_box.groupBoxLayout.addLayout(nameLayout)
        self.ch_box.groupBoxLayout.addWidget(self.ch_nameBtn)

        layout.addWidget(self.ch_box)
        self.ch_settingsBtn = self.ch_box.settingsBtn

        self.charWidget.setLayout(layout)

        self.ch_nameBtn.clicked.connect(self.ch_create)
        self.ch_settingsBtn.clicked.connect(self.ch_toggleSettingsUi)
        self.charNameCombo.activated.connect(self.refreshCharacter)

    @decorators.undoable
    def ch_create(self, *args):
        self.currentCharacterName = self.charNameCombo.currentText()
        if self.currentCharacterName:
            if not self.ch_exists(self.currentCharacterName):
                self.modulesTree.clear()
                self.currentCharacter = character.CharacterX(name=self.currentCharacterName)
                self.currentCharacter.createCharacterX()
                self.mt_setRoot(self.currentCharacter.characterRootModule.name)
                self.charNameCombo.addItem(self.currentCharacterName)
                self.charactersList.append(self.currentCharacter)
            else:
                pm.warning('A character with %s name exists already' % self.currentCharacterName)
        else:
            pm.warning('You need a name, don\'t you ?')

    def ch_exists(self, charName):
        for char in self.charactersList:
            if charName == char.characterName:
                return 1
        return 0

    def ch_toggleSettingsUi(self):
        if not self.charSettingsVisible:
            self.charSettingsVisible = 1
            self.ch_settingsBtn.setText('-')
            self.ch_addSettingsUi()
            '''
            self.settings_size_anim= utils.uiAddWidgetSizeAnim(self.characterSettingWidget,1,20)
            self.settings_size_anim.valueChanged.connect(self.forceResize)
            self.settings_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
            
            
            self.charGroup_size_anim= utils.uiAddWidgetSizeAnim(self.characterGroup,1,20,60)
            self.charGroup_size_anim.valueChanged.connect(self.charGroupForceResize)
            self.charGroup_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
            #self.characterGroup.setFixedHeight(80)
            '''
        else:
            self.charSettingsVisible = 0
            self.ch_settingsBtn.setText('+')
            # ----------------- PyQt4
            self.characterSettingWidget.setFixedHeight(0)
            self.ch_box.groupBox.setFixedHeight(80)
            ''' PySide
            self.settings_size_anim = utils.uiAddWidgetSizeAnim(self.characterSettingWidget,0,20)
            self.settings_size_anim.valueChanged.connect(self.forceResize)
            self.settings_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
            
            self.charGroup_size_anim= utils.uiAddWidgetSizeAnim(self.characterGroup,0,20,60)
            self.charGroup_size_anim.valueChanged.connect(self.charGroupForceResize)
            self.charGroup_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)            
            '''

    def ch_addSettingsUi(self):
        charSettingsLayout = QtGui.QVBoxLayout()
        charSettingsLayout.setContentsMargins(0, 0, 0, 0)
        charSidesStrings = QtGui.QLineEdit('Left,Right')
        charSettingsLayout.addWidget(charSidesStrings)
        self.characterSettingWidget.setLayout(charSettingsLayout)
        # PyQt4
        self.characterSettingWidget.setFixedHeight(30)
        self.ch_box.groupBox.setFixedHeight(105)

    def forceResize(self, new_height):
        self.characterSettingWidget.setFixedHeight(new_height.height())

    def charGroupForceResize(self, new_height):
        self.characterGroup.setFixedHeight(new_height.height())

    def refreshCharacter(self, item):
        self.currentCharacter = self.charactersList[item]
        self.updateModulesTreeWidget()

    # ----------------------------------Modules Buttons Functions------------------------------------------------------#

    def mb_setupUI(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.mb_splitLayout = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.mb_box = utils.TitledBox(title='Modules')
        self.mb_box.groupBoxLayout.addWidget(self.mb_splitLayout)
        self.addmodulesBtns()

        self.modulesTree = QtGui.QTreeWidget()
        self.modulesTree.setColumnCount(1)
        self.modulesTree.setHeaderHidden(1)
        self.modulesTree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        # self.moduleAttributes = moduleWidget.ModuleAttrWidget(self)
        self.moduleAttributes = None
        self.mb_splitLayout.addWidget(self.modulesTree)
        # self.mb_splitLayout.addWidget(self.moduleAttributes)
        # self.moduleAttributes.hide()


        layout.addWidget(self.mb_box)
        self.modulesBtnWidget.setLayout(layout)

    def addmodulesBtns(self):
        uiScriptFile = os.path.realpath(__file__)
        uiScriptPath, _ = os.path.split(uiScriptFile)
        modulesPath = uiScriptPath.replace('ui', 'modules')

        moduleFiles = [py for py in os.listdir(modulesPath) if py.endswith('.py') and '__init__' not in py]

        if moduleFiles:
            btnWidget = QtGui.QWidget()
            btnModulesLayout = QtGui.QVBoxLayout()
            btnModulesLayout.setAlignment(QtCore.Qt.AlignTop)
            btnModulesLayout.setContentsMargins(5, 3, 5, 0)

            btnLayout = QtGui.QVBoxLayout()
            btnLayout.setSpacing(3)

            btnModulesLayout.addLayout(btnLayout)
            btnWidget.setLayout(btnModulesLayout)
            self.mb_splitLayout.addWidget(btnWidget)

            numBtn = len(moduleFiles)

            for i in range(numBtn):
                name = moduleFiles[i][:-3]
                btn = QtGui.QPushButton(name)
                btn.setMinimumWidth(100)
                btnLayout.addWidget(btn)
                btn.clicked.connect(self.displayModuleWidget)

    def displayModuleWidget(self):
        moduleType = str(self.sender().text())

        toImport = 'bdRig.ui.widgets.' + moduleType + 'Widget'
        mod = None
        if self.currentCharacter:
            try:
                mod = __import__(toImport, {}, {}, [moduleType + 'Widget'])
                reload(mod)
            except:
                pm.warning("Did not find module %s" % toImport)
                return

            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    baseclass = obj.__bases__[0].__name__
                    if 'Widget' in baseclass:
                        if not self.moduleAttributes:
                            self.moduleAttributes = obj(self)
                            self.moduleAttributes.moduleType = moduleType
                            self.moduleAttributes.setDefaultName(moduleType)

                            self.mb_splitLayout.addWidget(self.moduleAttributes)
                            self.modulesTree.hide()

        else:
            pm.warning('No character to add modules too !!!')

            # --------------------------------------------Modules Tree Widget Functions ---------------------------------------#

    def mt_setRoot(self, rootName):
        self.rootItem = QtGui.QTreeWidgetItem(self.modulesTree)
        self.rootItem.setText(0, rootName)

    def mt_appendModulesList(self, moduleName):
        item = QtGui.QTreeWidgetItem(self.rootItem)
        item.setText(0, moduleName)
        self.modulesTree.expandItem(self.rootItem)

    def mt_populateTree(self, currentCharacter):
        self.modulesTree.clear()
        rootModuleInfo = currentCharacter.characterInfo['character_root_module_info']
        self.mt_setRoot(rootModuleInfo['name'])
        modulesList = currentCharacter.characterInfo['character_modules_info']
        for module in modulesList:
            self.mt_appendModulesList(module['name'])

        self.modulesTree.expandItem(self.rootItem)

        # --------------------------------------------SkeletonWidget Functions ---------------------------------------#

    def skeleton_setupUI(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.skeleton_box = utils.TitledBox(title='Skeleton', settings=0)

        self.buildSkeletonBtn = QtGui.QPushButton('Build Skeleton')

        self.skeleton_box.groupBoxLayout.addWidget(self.buildSkeletonBtn)
        layout.addWidget(self.skeleton_box)
        self.skeletonWidget.setLayout(layout)

        self.buildSkeletonBtn.clicked.connect(self.buildModuleSkeleton)

    def buildModuleSkeleton(self):
        print self.currentCharacter.characterRootModule
        print self.currentCharacter.characterModules
        for module in self.currentCharacter.characterModules:
            module.buildSkeleton()

    # --------------------------------------------Rigging Widget Functions ---------------------------------------#
    def rig_setupUI(self):
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.rig_box = utils.TitledBox(title='Rig', settings=0)

        layout.addWidget(self.rig_box)
        self.rigWidget.setLayout(layout)

    # ------------------------------------------------------------------------------------------------------------#

    def addMenu(self):
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.fileMenu.addAction('Load skeleton')
        self.fileMenu.addAction('Save skeleton')
        self.toolsMenu = self.menuBar.addMenu('Tools')
        self.toolsMenu.addAction('Create Picking Geometry')

    def initializeChars(self):
        characters = pm.ls('*CHAR')
        if characters:
            for char in characters:
                characterName = char.name().replace('_CHAR', '')
                self.currentCharacter = character.CharacterX(name=characterName)
                self.currentCharacter.restoreCharacter()
                self.charNameCombo.addItem(characterName)
                self.charactersList.append(self.currentCharacter)
                self.charNameCombo.setCurrentIndex(self.charNameCombo.count() - 1)

    def updateModulesTreeWidget(self):
        if self.currentCharacter:
            self.mt_populateTree(self.currentCharacter)

    def closeEvent(self, e):
        pass


def createUI():
    if pm.window(yartWin, exists=True, q=True):
        pm.deleteUI(yartWin)

    YartUI()
