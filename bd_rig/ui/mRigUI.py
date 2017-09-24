import pymel.core as pm
import traceback
import os
import inspect

from ..utils.qt_handlers import QtCore, QtGui
from ..utils import qt_handlers as qt_handlers

from ..utils import libWidgets as UI

reload(UI)

from ..utils import libUtils as utils

reload(utils)

import char_settings as char_settings

reload(char_settings)

import blueprint_settings as blueprint_settings

reload(blueprint_settings)

from ..character import character as char

reload(char)

from .. import mRigGlobals as MRIGLOBALS

reload(MRIGLOBALS)

mRigWin = 'mRigWindow'


class mRigUI(QtGui.QMainWindow):
    def __init__(self, parent=qt_handlers.get_maya_window()):
        super(mRigUI, self).__init__(parent)
        """
        Class members:
        self.blueprintModules - dict holding the python modules where the blueprints are implemented. The key is the blueprint name, the value is the python module pointer
        self.character - active character
        """
        self.blueprintModules = {}
        self.blueprintModulesUIs = []
        self.character = None
        self.blueprintParent = ''
        # -------------------------------

        self.setObjectName(mRigWin)
        self.setWindowTitle('Modular Rigging Tool')
        # ------------------------- UI elements -------------------------
        self.tabs = QtGui.QTabWidget()
        self.blueprintSettings = None
        self.charWidget = QtGui.QWidget()
        self.charName = None
        self.charBox = None
        self.charNameSuffix = None
        self.charSettings = None

        self.blueprintsWidget = QtGui.QWidget()
        self.blueprintsBox = None
        self.blueprintsSettingsLayout = None

        self.listsWidget = QtGui.QWidget()
        self.bpCharList = QtGui.QListWidget()
        self.listRigs = None

        self.skeletonWidget = QtGui.QWidget()
        self.skeletonBox = None
        self.riggingWidget = QtGui.QWidget()
        self.riggingBox = None

        self.infoDock = None
        # ---------------------------------------------------------------
        self.setupUI()
        self.show()
        self.resize(300, 400)

        self.restoreCharacter()

    def setupUI(self):
        """
        Sets up the UI for the tool
        """
        centralWidget = QtGui.QWidget()

        mainLayout = UI.VertBox()
        mainLayout.addWidget(self.tabs)

        # self.charWidget - widget holding the UI for the character creation
        self.charWidget = QtGui.QWidget()
        self.addCharUI()
        self.tabs.addTab(self.charWidget, 'Character')

        # self.blueprintsWidget - widget holding the UI for the character creation
        self.blueprintsWidget = QtGui.QWidget()
        self.addBlueprintsUI()
        self.tabs.addTab(self.blueprintsWidget, 'Blueprints')

        # self.createSkeletonWidget - widget holding the UI for the skeleton building, based on the layed out blueprints
        self.skeletonWidget = QtGui.QWidget()
        self.addSkeletonUI()
        self.tabs.addTab(self.skeletonWidget, 'Skeleton')

        # self.createSkeletonWidget - widget holding the UI for the skeleton building, based on the layed out blueprints
        self.riggingWidget = QtGui.QWidget()
        self.addRiggingUI()
        self.tabs.addTab(self.riggingWidget, 'Rigging')
        #
        self.infoDock = UI.InfoDock()
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.infoDock)  # dockWidget

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    # --------------------------------------------Character Widget UI ------------------------------------------#
    def addCharUI(self):
        """
        Sets up the UI for the character.

        Important:
        self.charBox.layout  - the layout where all the widgets should be added
        """
        charLayout = UI.VertBox()

        self.charBox = UI.TitledBox(title='Character')

        self.charSettings = char_settings.CharSettingsWidget()
        nameLayout = UI.HorBox()
        self.charName = UI.LabelEditWidget(label='Enter character name:')
        self.charNameSuffix = UI.LabelEditWidget(label='Suffix')
        self.charNameSuffix.edit.setText('_' + MRIGLOBALS.CHAR)

        nameLayout.addWidget(self.charName)
        nameLayout.addWidget(self.charNameSuffix)

        title = UI.TitleBar(title='Name')
        btnLayout = UI.HorBox()
        newCharBtn = UI.ButtonB('NEW')
        newCharBtn.setStyleSheet("background-color: rgb(0,100,200); font-weight: bold")
        deleteCharBtn = UI.ButtonB('Rename')
        btnLayout.addWidget(newCharBtn)
        btnLayout.addWidget(deleteCharBtn)

        separator = UI.Separator()

        self.charBox.layout.addWidget(self.charSettings)
        self.charBox.layout.addWidget(title)
        self.charBox.layout.addLayout(nameLayout)
        self.charBox.layout.addWidget(separator)
        self.charBox.layout.addLayout(btnLayout)

        charLayout.addWidget(self.charBox)

        newCharBtn.clicked.connect(self.createCharacter)

        self.charWidget.setLayout(charLayout)

    # --------------------------------------------Blueprints Widget UI -------------------------------------------------#
    def addBlueprintsUI(self):
        """
        Sets up the Blueprint tab UI
        Dynamically creates the UI for the creation of the blueprints by getting a list of python files holding the blueprints from modules/blueprint
        Currently each blueprint module gets a button
        """
        blueprintsLayout = UI.VertBox()

        self.blueprintsBox = UI.TitledBox(title='Blueprints')

        gridLayout = QtGui.QGridLayout()

        moduleUILayout = UI.VertBox()
        moduleUILayout.setSpacing(2)

        blueprintsList = self.getBlueprintsList()

        if blueprintsList:
            numBlueprints = len(blueprintsList)

            for i in range(numBlueprints):
                if blueprintsList[i] != 'blueprint':  # we dont need to create an UI for the blueprint base class
                    pyModule = self.importPythonModule(blueprintsList[i])

                    if pyModule:
                        moduleUI = self.createPyModuleUI(modName=pyModule.BLUEPRINT_TYPE, index=i)
                        moduleUILayout.addWidget(moduleUI)
                        self.blueprintModulesUIs.append(moduleUI)

        spacerItem = QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        moduleUILayout.addItem(spacerItem)

        createdBlueprintsLayout = UI.VertBox()

        btnLayout = UI.HorBox()
        btnLayout.setAlignment(QtCore.Qt.AlignRight)

        editBlueprintBtn = UI.ButtonB('Edit')
        deleteBlueprintBtn = UI.ButtonB('Delete')
        deleteBlueprintBtn.setStyleSheet("background-color: rgb(250,10,20); font-weight: bold")
        btnLayout.addWidget(editBlueprintBtn)
        btnLayout.addWidget(deleteBlueprintBtn)

        createdBlueprintsLayout.addWidget(self.bpCharList)
        createdBlueprintsLayout.addLayout(btnLayout)

        gridLayout.addLayout(moduleUILayout, 0, 0)
        gridLayout.setColumnMinimumWidth(0, 150)
        separator = UI.Separator(d=1)
        gridLayout.addWidget(separator, 0, 1)
        gridLayout.addLayout(createdBlueprintsLayout, 0, 2)

        self.blueprintsSettingsLayout = UI.HorBox()

        self.blueprintsBox.layout.addLayout(gridLayout)
        self.blueprintsBox.layout.addLayout(self.blueprintsSettingsLayout)

        blueprintsLayout.addWidget(self.blueprintsBox)
        self.blueprintsWidget.setLayout(blueprintsLayout)

        editBlueprintBtn.released.connect(self.editSelectedBlueprint)
        self.bpCharList.doubleClicked.connect(self.deselectBlueprint)

    def addSkeletonUI(self):
        skeletonLayout = UI.VertBox()

        self.skeletonBox = UI.TitledBox(title='    Skeleton')
        createSkeletonBtn = UI.ButtonB('Create')
        self.skeletonBox.layout.addWidget(createSkeletonBtn)

        skeletonLayout.addWidget(self.skeletonBox)
        createSkeletonBtn.clicked.connect(self.buildSkeleton)
        self.skeletonWidget.setLayout(skeletonLayout)

    def addRiggingUI(self):
        riggingLayout = UI.VertBox()

        self.riggingBox = UI.TitledBox(title='    Rig')
        createRigBtn = UI.ButtonB('RIG IT')
        self.riggingBox.layout.addWidget(createRigBtn)

        riggingLayout.addWidget(self.riggingBox)
        self.riggingWidget.setLayout(riggingLayout)

        # --------------------------------------------------------------------------------------------------------------

    def createCharacter(self):
        """
        Clicked event for self.charSettings.createCharBtn
        Creates a new character
        """
        pm.undoInfo(openChunk=True)
        inputName = self.charName.edit.text()
        charSuffix = self.charNameSuffix.edit.text()
        rootName = self.charSettings.rootName.edit.text()
        leftString = self.charSettings.leftString.edit.text()
        rightString = self.charSettings.rightString.edit.text()

        if len(inputName) and len(charSuffix):
            charName = inputName + charSuffix
            self.character = char.Char(charName, rootName=rootName, leftString=leftString, rightString=rightString)
            self.character.create()
            self.infoDock.infoDisplay.append('Created %s character' % charName)
            listItem = QtGui.QListWidgetItem()
            listItem.setText(self.character.chRootName)
            listItem.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.bpCharList.addItem(listItem)

        pm.undoInfo(closeChunk=True)

    def restoreCharacter(self):
        find = pm.ls('*_' + char.CHAR, type='transform')
        if find:
            charName = find[0].name()
            self.character = char.Char(charName)
            self.character.restore()
            self.character.restoreBlueprints(self.blueprintModules)
            self.charName.edit.setText(charName.replace(('_' + char.CHAR), ''))

            print [bp.name for bp in self.character.chBlueprintsList]

            for i in range(len(self.character.chBlueprintsList)):
                listItem = QtGui.QListWidgetItem()
                listItem.setText(self.character.chBlueprintsList[i].name)
                if i == 0:
                    listItem.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.bpCharList.addItem(listItem)

    def importPythonModule(self, blueprintName):
        """
        Returns a Python Module

        Arguments:
        blueprintName - a string containing the name of the blueprint file without the extension
        """
        top_package = __name__.split('.')[0]
        toImport = top_package + '.mRig.blueprints.' + blueprintName
        mod = None

        try:
            mod = __import__(toImport, {}, {}, [blueprintName])
            reload(mod)
            self.blueprintModules[mod.BLUEPRINT_TYPE] = mod
            print ('Imported blueprint module %s' % toImport)
        except:
            pm.warning("Error importing python module %s" % toImport)
            pm.warning(traceback.format_exc())
        return mod

    def createPyModuleUI(self, modName, index):
        """
        Implement a desired UI for the blueprint , currently it's just a button

        Arguments:
        modName - string , to be used for the creation button

        Return:
        the ui/widget for the blueprint module
        """
        # self.getSettingsClass(modName)
        btn = UI.BlueprintButton(modName, index)
        # color = btn.palette().color(QtGui.QPalette.Background)
        btn.clicked.connect(self.showBlueprintSettingsUI)
        return btn

    # --------------------------------------------Buttons callbacks ------------------------------------------#
    def showBlueprintSettingsUI(self):
        """
        Creates or toggles the clicked blueprint creation UI. This will happen ONLY if a character was created

        When a blueprint creation button is clicked, the blueprint settings UI is created. If the same button is pressed, the UI visibility will be toggled.
        When another  blueprint creation button is clicked, the current settings UI is deleted and a new one is created for the new blueprint. The toggle system applies here as well.
        """
        if self.character:
            blueprint = str(self.sender().text())

            # if you press the same button, ui visibility is toggled
            if self.blueprintSettings:
                blueprintType = self.blueprintSettings.getType()
                if blueprintType == blueprint:
                    if self.blueprintSettings.isVisible():
                        self.blueprintSettings.hide()
                    else:
                        self.blueprintSettings.show()
                        self.blueprintSettings.blueprintName.edit.setText(blueprint.capitalize())
                        self.blueprintSettings.blueprintName.edit.setFocus()
                    return

            # delete the settings when a a new blueprint btn is pressed
            if self.blueprintSettings is not None:
                self.blueprintSettings.deleteLater()

            # create the blueprints creation/edit settings UI
            settingsClass = self.getSettingsClass(blueprint)
            self.blueprintSettings = settingsClass(
                blueprintType=blueprint)  # blueprint_settings.BlueprintSettingsWidget(blueprintType=blueprint)
            self.blueprintSettings.blueprintName.edit.setText(blueprint.capitalize())
            self.blueprintSettings.blueprintName.edit.setFocus()
            selection = pm.ls(sl=1)
            if selection and '_guide' in selection[0].name():
                self.blueprintSettings.blueprintParent.edit.setText(selection[0].name())
            else:
                self.blueprintSettings.blueprintParent.edit.setText(
                    self.character.chBlueprintsList[0].guides_list[0].name())

            self.blueprintsSettingsLayout.addWidget(self.blueprintSettings)

            self.blueprintSettings.createBlueprintBtn.clicked.connect(self.createBlueprint)
            self.blueprintSettings.blueprintParent.pickBtn.clicked.connect(self.setBlueprintParent)

        else:
            pm.warning('No character created !!!')
            self.infoDock.infoDisplay.append('No character created !!!')
            self.sender().backColorAnim.start()
            self.charName.backColorAnim.start()
            self.tabs.setCurrentIndex(0)
            self.charName.edit.setFocus()

    def createBlueprint(self):
        """
        Clicked slot from self.blueprintSettings.createBlueprintBtn

        It will create the blueprint in Maya
        """
        pm.undoInfo(openChunk=True)
        blueprintName = self.blueprintSettings.blueprintName.edit.text()
        blueprintParent = self.blueprintSettings.blueprintParent.edit.text()
        blueprintInfo = self.blueprintSettings.getInfo()

        if blueprintName != '':
            mod = self.blueprintModules[self.blueprintSettings.blueprintType]
            # reload(mod)

            blueprintClass = getattr(mod, mod.CLASS_NAME)
            if blueprintClass:
                if not self.character.hasBlueprint(blueprintName):
                    blueprintInstance = blueprintClass(name=blueprintName, parent=blueprintParent,
                                                       buildInfo=blueprintInfo, character=self.character)
                    blueprintInstance.create()
                    blueprintInstance.createParentLink()
                    self.character.addBlueprint(blueprintInstance)
                    self.character.saveCharacterInfo()
                    self.bpCharList.addItem(blueprintInstance.name)
                    self.infoDock.infoDisplay.append(
                        'Blueprint \'%s\' of type %s created !' % (blueprintName, self.blueprintSettings.blueprintType))
                    pm.select(blueprintInstance.controller)
                    for i in range(len(self.blueprintModulesUIs)):
                        self.blueprintModulesUIs[i].show()
                        self.blueprintSettings.hide()
                else:
                    self.infoDock.infoDisplay.append(
                        'Blueprint with the name \'%s\' already exists, choose a new name !!!' % blueprintName)
                    pm.warning('Blueprint with the name \'%s\' already exists, choose a new name !!!' % blueprintName)
            else:
                self.infoDock.infoDisplay.append('Found no blueprint class in module %s!!!' % mod)
                pm.warning('Found no blueprint class in module %s!!!' % mod)


                # self.blueprintSettings.blueprintName.edit.setText("")

        else:
            self.infoDock.infoDisplay.append('Enter a name for the blueprint !')
            print('Enter a name for the blueprint !')
        pm.undoInfo(closeChunk=True)

    # def blueprintTreeAdd(self,itemName):
    # 	treeItem = QtGui.QTreeWidgetItem(self.rootItem)
    # 	treeItem.setText(0,itemName)
    # 	self.blueprintsTree.expandItem(self.rootItem)

    def deselectBlueprint(self):
        self.bpCharList.clearSelection()

    def buildSkeleton(self):
        pm.undoInfo(openChunk=True)
        parentChildPairs = {}
        for blueprint in self.character.chBlueprintsList:
            pm.select(cl=1)
            jntList = []
            i = 1
            prevJnt = None
            for guide in blueprint.guides_list:
                guidePos = guide.getTranslation(space='world')
                jnt = pm.joint(n=blueprint.side + guide.name().replace(MRIGLOBALS.BPGUIDE, MRIGLOBALS.BNDJNT),
                               p=guidePos)
                if i > 1:
                    pm.joint(prevJnt, e=True, oj='xyz', secondaryAxisOrient='yup', zso=True)
                prevJnt = jnt
                jntList.append(jnt)
                i += 1

            jntList[-1].jointOrientX.set(0)
            jntList[-1].jointOrientY.set(0)
            jntList[-1].jointOrientZ.set(0)
            parentName = blueprint.parent.replace(MRIGLOBALS.BPGUIDE, MRIGLOBALS.BNDJNT)
            parentChildPairs[parentName] = jntList[0]

        for parent, child in parentChildPairs.iteritems():
            if 'trs' in parent:
                pm.parent(child, self.character.chSkeletonGrp)
            else:
                pm.parent(child, parent)
        pm.undoInfo(closeChunk=True)

    def setBlueprintParent(self):
        selection = pm.ls(sl=1)
        if selection:
            if 'guide' not in selection[0].name():
                pm.warning('Please select a guide to be used as a parent')
                self.infoDock.infoDisplay.append('Please select a guide to be used as a parent')
            else:
                self.blueprintSettings.blueprintParent.edit.setText(selection[0].name())

    def editBlueprintSettingsUI(self, blueprint):
        """
        Shows the settings UI for the selected bp for editing.

        """
        if self.character:
            type_bp = blueprint.type_bp
            # if you press the same button, ui visibility is toggled
            if self.blueprintSettings:
                blueprintType = self.blueprintSettings.getType()
                if blueprintType == type:
                    if self.blueprintSettings.isVisible():
                        self.blueprintSettings.hide()
                    else:
                        self.blueprintSettings.show()
                        self.blueprintSettings.blueprintName.edit.setText(blueprint.name)
                        self.blueprintSettings.blueprintName.edit.setFocus()
                    return

            # delete the settings when a a new blueprint btn is pressed
            if self.blueprintSettings is not None:
                self.blueprintSettings.deleteLater()

            # create the blueprints creation/edit settings UI
            settingsClass = self.getSettingsClass(type_bp)
            self.blueprintSettings = settingsClass(
                blueprintType=type_bp)  # blueprint_settings.BlueprintSettingsWidget(blueprintType=blueprint)
            self.blueprintSettings.blueprintName.edit.setText(blueprint.name)
            self.blueprintSettings.blueprintName.edit.setFocus()

            self.blueprintSettings.blueprintParent.edit.setText(str(blueprint.parent))
            self.blueprintsSettingsLayout.addWidget(self.blueprintSettings)
            self.blueprintSettings.createBlueprintBtn.clicked.connect(self.createBlueprint)
            self.blueprintSettings.blueprintParent.pickBtn.clicked.connect(self.setBlueprintParent)
        else:
            pm.warning('No character created !!!')
            self.infoDock.infoDisplay.append('No character created !!!')
            self.sender().backColorAnim.start()
            self.charName.backColorAnim.start()
            self.tabs.setCurrentIndex(0)
            self.charName.edit.setFocus()

    def editSelectedBlueprint(self):
        selectedBlueprintIndex = self.bpCharList.currentRow()
        if selectedBlueprintIndex > 0:
            blueprint = self.character.chBlueprintsList[selectedBlueprintIndex]
            self.editBlueprintSettingsUI(blueprint)
        else:
            self.infoDock.infoDisplay.append('Skeleton Root is not editable, select another blueprint!')

    # ---------------------------------------Static methods---------------------------------------------------------#
    @staticmethod
    def getBlueprintsList():
        # script directory
        utilsFolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        print '-----------------------------------'
        print utilsFolder
        print '-----------------------------------'
        blueprintsFolder = utilsFolder.replace('ui', 'blueprints')

        if os.path.isdir(blueprintsFolder):
            blueprintFiles = [os.path.splitext(py)[0] for py in os.listdir(blueprintsFolder) if
                              py.endswith('.py') and '__init__' not in py]
            if len(blueprintFiles):
                # blueprintFiles.remove('blueprint')
                return blueprintFiles
            else:
                return None

    @staticmethod
    def getSettingsClass(blueprintType):
        blueprintClass = None
        classes = [m[1] for m in inspect.getmembers(blueprint_settings, inspect.isclass)]
        for cl in classes:
            if cl.TYPE == blueprintType:
                return cl
            elif cl.TYPE == 'blueprint':
                blueprintClass = cl

        return blueprintClass


def create():
    """
    Creates the tool window
    """
    if pm.window(mRigWin, exists=True, q=True):
        pm.deleteUI(mRigWin)

    ui = mRigUI()
    ui.charName.edit.setFocus()
