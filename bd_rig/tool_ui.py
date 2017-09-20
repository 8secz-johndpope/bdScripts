from maya import OpenMayaUI
import pymel.core as pm
import os
import inspect
import traceback
import ui.char_settings as char_settings
import ui.blueprint_settings as blueprint_settings
import blueprints.character as char
import mRigGlobals as MRIGLOBALS
from utils import libWidgets as UI

reload(MRIGLOBALS)
reload(char)
reload(blueprint_settings)
reload(char_settings)
reload(UI)

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from shiboken import wrapInstance


mayaMainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)


rigWin = 'mRigWindow'


class ToolWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ToolWindow, self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setObjectName(rigWin)
        self.setWindowTitle('Modular Rigging Tool')
        """Class members:
        self.bp_modules - dict holding the python modules where the blueprints are implemented. The key is the blueprint name, the value is the python module pointer
        self.character - active character
        """
        self.bp_modules = {}
        self.bp_modules_ui = []
        self.character = None
        self.bp_parent = ''
        self.bp_settings_ui = None
        self.char_name = None
        self.char_name_suffix = None
        self.char_settings = None
        # # ------------------------- UI elements -------------------------

        self.char_widget = QWidget()
        self.bp_widget = QWidget()
        self.skeleton_widget = QWidget()
        self.rig_widget = QWidget()

        self.bp_box = None
        self.bp_settings_ui_layout = None
        self.bp_list = QListWidget()
        self.list_rigs = None
        #
        # self.skeleton_widget = qt_handlers.qWidget()
        # self.rig_widget = qt_handlers.qWidget()
        # self.rig_box = None
        #
        self.info_dock = None
        # ---------------------------------------------------------------
        self.setup_ui()

        # self.restore_character()

    def setup_ui(self):
        """
        Sets up the UI for the tool
        """
        central_widget = QWidget()
        central_widget.setFixedWidth(300)
        main_layout = UI.VertBox()
        # The four main widgets: Character , Blueprints, Skeleton, Rigging
        main_layout.addWidget(self.char_widget)
        main_layout.addWidget(self.bp_widget)
        main_layout.addWidget(self.skeleton_widget)
        main_layout.addWidget(self.rig_widget)

        # create the char layout ui
        self.add_char_ui()
        # create the blueprints layout ui
        self.add_blueprints_ui()
        # skeleton ui
        self.add_skeleton_ui()
        # rigging ui
        self.add_rigging_ui()

        self.info_dock = UI.InfoDock()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.info_dock)  # dockWidget

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # --------------------------------------------Character Widget UI ------------------------------------------#
    def add_char_ui(self):
        """
        Sets up the UI for the character.

        Important:
        char_box.layout  - the layout where all the widgets should be added
        """
        char_layout = UI.VertBox()

        char_box = UI.TitledBox(title='Character')

        self.char_settings = char_settings.CharSettingsWidget()
        name_layout = UI.HorBox()
        self.char_name = UI.LabelEditWidget(label='Character name:', label_size=85, edit_size=80)
        self.char_name_suffix = UI.LabelEditWidget(label='+', label_size=10, edit_size=40)
        self.char_name_suffix.edit.setText('_' + MRIGLOBALS.CHAR)

        name_layout.addWidget(self.char_name)
        name_layout.addWidget(self.char_name_suffix)

        title = UI.TitleBar(title='Name')
        btn_layout = UI.HorBox()
        new_char_btn = UI.ButtonB('NEW')
        new_char_btn.setStyleSheet("background-color: rgb(0,100,200); font-weight: bold")
        delete_char_btn = UI.ButtonB('Rename')
        btn_layout.addWidget(new_char_btn)
        btn_layout.addWidget(delete_char_btn)

        separator = UI.Separator()

        char_box.layout.addWidget(self.char_settings)
        char_box.layout.addWidget(title)
        char_box.layout.addLayout(name_layout)
        char_box.layout.addWidget(separator)
        char_box.layout.addLayout(btn_layout)

        char_layout.addWidget(char_box)

        new_char_btn.clicked.connect(self.create_character)

        self.char_widget.setLayout(char_layout)

    # --------------------------------------------Blueprints Widget UI -----------------------------------------------#
    def add_blueprints_ui(self):
        """
        Sets up the Blueprint tab UI
        Dynamically creates the UI for the creation of the blueprints by getting a list of python files holding the
         blueprints from modules/blueprint
        Currently each blueprint module gets a button
        """
        blueprints_layout = UI.VertBox()
        self.bp_box = UI.TitledBox(title='Blueprints')

        bp_ui_layout = QGridLayout()
        blueprints_list = self.get_bp_files_list()

        if blueprints_list:
            num_bp = len(blueprints_list)
            for i in range(num_bp):
                if blueprints_list[i] != 'blueprint':  # we dont need to create an UI for the blueprint base class
                    python_module = self.import_python_module(blueprints_list[i])
                    if python_module:
                        module_ui = self.create_bp_ui(modName=python_module.BLUEPRINT_TYPE, index=i)
                        self.bp_modules_ui.append(module_ui)

        for i, m in enumerate(self.bp_modules_ui):
            bp_ui_layout.addWidget(m, i / 3, i % 3)

        btn_layout = UI.HorBox()
        btn_layout.setAlignment(Qt.AlignRight)

        edit_bp_btn = UI.ButtonB('Edit')
        delete_bp_btn = UI.ButtonB('Delete')
        delete_bp_btn.setStyleSheet("background-color: rgb(250,10,20); font-weight: bold")
        btn_layout.addWidget(edit_bp_btn)
        btn_layout.addWidget(delete_bp_btn)

        self.bp_settings_ui_layout = UI.HorBox()

        self.bp_box.layout.addLayout(bp_ui_layout)
        self.bp_box.layout.addLayout(self.bp_settings_ui_layout)
        separator = UI.Separator()
        self.bp_box.layout.addWidget(separator)
        self.bp_box.layout.addWidget(self.bp_list)
        self.bp_box.layout.addLayout(btn_layout)

        blueprints_layout.addWidget(self.bp_box)
        self.bp_widget.setLayout(blueprints_layout)

        edit_bp_btn.released.connect(self.editSelectedBlueprint)
        self.bp_list.doubleClicked.connect(self.deselectBlueprint)

    def add_skeleton_ui(self):
        layout = UI.VertBox()

        skeleton_box = UI.TitledBox(title='    Skeleton')
        create_skeleton_btn = UI.ButtonB('Create')
        skeleton_box.layout.addWidget(create_skeleton_btn)

        layout.addWidget(skeleton_box)
        create_skeleton_btn.clicked.connect(self.buildSkeleton)
        self.skeleton_widget.setLayout(layout)

    def add_rigging_ui(self):
        layout = UI.VertBox()

        rig_box = UI.TitledBox(title='    Rig')
        create_rig_btn = UI.ButtonB('RIG IT')
        rig_box.layout.addWidget(create_rig_btn)

        layout.addWidget(rig_box)
        self.rig_widget.setLayout(layout)

        # --------------------------------------------------------------------------------------------------------------

    def create_character(self):
        """
        Clicked event for self.char_settings.createCharBtn
        Creates a new character
        """
        pm.undoInfo(openChunk=True)
        char_name = self.char_name.edit.text()
        char_suffix = self.char_name_suffix.edit.text()
        # char_root_name = self.char_settings.root_name.edit.text()
        left_str = self.char_settings.left_str.edit.text()
        right_str = self.char_settings.right_str.edit.text()

        if len(char_name) and len(char_suffix):
            char_name = char_name + char_suffix
            self.character = char.Char(name=char_name, leftString=left_str, rightString=right_str)
            self.character.create()
            self.info_dock.infoDisplay.append('Created %s character' % char_name)
            # list_item = QListWidgetItem()
            # list_item.setText(self.character.chRootName)
            # list_item.setTextAlignment(Qt.AlignHCenter)
            # self.bp_list.addItem(list_item)

        pm.undoInfo(closeChunk=True)

    def restore_character(self):
        find = pm.ls('*_' + char.CHAR, type='transform')
        if find:
            char_name = find[0].name()
            self.character = char.Char(char_name)
            self.character.restore()
            self.character.restoreBlueprints(self.bp_modules)
            self.char_name.edit.setText(char_name.replace(('_' + char.CHAR), ''))

            print [bp.bpName for bp in self.character.chBlueprintsList]

            for i in range(len(self.character.chBlueprintsList)):
                list_item = QListWidgetItem()
                list_item.setText(self.character.chBlueprintsList[i].bpName)
                self.bp_list.addItem(list_item)

    def import_python_module(self, blueprintName):
        """
        Returns a Python Module

        Arguments:
        blueprintName - a string containing the name of the blueprint file without the extension
        """
        top_package = __name__.split('.')[0]
        module_to_import = top_package + '.bd_rig.blueprints.' + blueprintName
        # print('------------------>' + module_to_import)
        mod = None

        try:
            mod = __import__(module_to_import, {}, {}, [blueprintName])
            reload(mod)
            self.bp_modules[mod.BLUEPRINT_TYPE] = mod
            print ('Imported blueprint module %s' % module_to_import)
        except:
            pm.warning("Error importing python module %s" % module_to_import)
            pm.warning(traceback.format_exc())
        return mod

    def create_bp_ui(self, modName, index):
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
        btn.clicked.connect(self.show_bp_settings_ui)
        return btn

    # --------------------------------------------Buttons callbacks ------------------------------------------#
    def show_bp_settings_ui(self):
        """
        Creates or toggles the clicked blueprint creation UI. This will happen ONLY if a character was created

        When a blueprint creation button is clicked, the blueprint settings UI is created. If the same button is pressed, the UI visibility will be toggled.
        When another  blueprint creation button is clicked, the current settings UI is deleted and a new one is created for the new blueprint. The toggle system applies here as well.
        """
        if self.character:
            blueprint = str(self.sender().text())

            # if you press the same button, ui visibility is toggled
            if self.bp_settings_ui:
                bp_type = self.bp_settings_ui.getType()
                if bp_type == blueprint:
                    if self.bp_settings_ui.isVisible():
                        self.bp_settings_ui.hide()
                    else:
                        self.bp_settings_ui.show()
                        self.bp_settings_ui.bp_name.edit.setText(blueprint.capitalize())
                        self.bp_settings_ui.bp_name.edit.setFocus()
                    return

            # delete the settings when a a new blueprint btn is pressed
            if self.bp_settings_ui is not None:
                self.bp_settings_ui.deleteLater()
            # create the blueprints creation/edit settings UI
            settingsClass = self.getSettingsClass(blueprint)
            self.bp_settings_ui = settingsClass(blueprintType=blueprint)  # blueprint_settings.BlueprintSettingsWidget(bp_type=blueprint)
            self.bp_settings_ui.bp_name.edit.setText(blueprint.capitalize())
            self.bp_settings_ui.bp_name.edit.setFocus()
            selection = pm.ls(sl=1)
            if selection and '_guide' in selection[0].name():
                self.bp_settings_ui.bp_parent.edit.setText(selection[0].name())
            # else:
            #     self.bp_settings_ui.bp_parent.edit.setText(
            #         self.character.chBlueprintsList[0].bpGuidesList[0].name())

            self.bp_settings_ui_layout.addWidget(self.bp_settings_ui)

            self.bp_settings_ui.create_bp_btn.clicked.connect(self.createBlueprint)
            self.bp_settings_ui.bp_parent.pickBtn.clicked.connect(self.setBlueprintParent)

        else:
            pm.warning('No character created !!!')
            self.info_dock.infoDisplay.append('No character created !!!')
            self.sender().backColorAnim.start()
            self.char_name.backColorAnim.start()
            self.tabs.setCurrentIndex(0)
            self.char_name.edit.setFocus()

    def createBlueprint(self):
        """
        Clicked slot from self.bp_settings_ui.create_bp_btn

        It will create the blueprint in Maya
        """
        pm.undoInfo(openChunk=True)
        blueprintName = self.bp_settings_ui.bp_name.edit.text()
        bp_parent = self.bp_settings_ui.bp_parent.edit.text()
        blueprintInfo = self.bp_settings_ui.getInfo()

        if blueprintName != '':
            mod = self.bp_modules[self.bp_settings_ui.bp_type]
            # reload(mod)

            blueprintClass = getattr(mod, mod.CLASS_NAME)
            if blueprintClass:
                if not self.character.hasBlueprint(blueprintName):
                    blueprintInstance = blueprintClass(name=blueprintName, parent=bp_parent,
                                                       buildInfo=blueprintInfo, character=self.character)
                    blueprintInstance.create()
                    blueprintInstance.createParentLink()
                    self.character.addBlueprint(blueprintInstance)
                    self.character.saveCharacterInfo()
                    self.bp_list.addItem(blueprintInstance.bpName)
                    self.info_dock.infoDisplay.append(
                        'Blueprint \'%s\' of type %s created !' % (blueprintName, self.bp_settings_ui.bp_type))
                    pm.select(blueprintInstance.bpController)
                    for i in range(len(self.bp_modules_ui)):
                        self.bp_modules_ui[i].show()
                        self.bp_settings_ui.hide()
                else:
                    self.info_dock.infoDisplay.append(
                        'Blueprint with the name \'%s\' already exists, choose a new name !!!' % blueprintName)
                    pm.warning('Blueprint with the name \'%s\' already exists, choose a new name !!!' % blueprintName)
            else:
                self.info_dock.infoDisplay.append('Found no blueprint class in module %s!!!' % mod)
                pm.warning('Found no blueprint class in module %s!!!' % mod)


                # self.bp_settings_ui.bp_name.edit.setText("")

        else:
            self.info_dock.infoDisplay.append('Enter a name for the blueprint !')
            print('Enter a name for the blueprint !')
        pm.undoInfo(closeChunk=True)

    def deselectBlueprint(self):
        self.bp_list.clearSelection()

    def buildSkeleton(self):
        pm.undoInfo(openChunk=True)
        parentChildPairs = {}
        for blueprint in self.character.chBlueprintsList:
            pm.select(cl=1)
            jntList = []
            i = 1
            prevJnt = None
            for guide in blueprint.bpGuidesList:
                guidePos = guide.getTranslation(space='world')
                jnt = pm.joint(n=blueprint.bpSide + guide.name().replace(MRIGLOBALS.BPGUIDE, MRIGLOBALS.BNDJNT),
                               p=guidePos)
                if i > 1:
                    pm.joint(prevJnt, e=True, oj='xyz', secondaryAxisOrient='yup', zso=True)
                prevJnt = jnt
                jntList.append(jnt)
                i += 1

            jntList[-1].jointOrientX.set(0)
            jntList[-1].jointOrientY.set(0)
            jntList[-1].jointOrientZ.set(0)
            parentName = blueprint.bpParent.replace(MRIGLOBALS.BPGUIDE, MRIGLOBALS.BNDJNT)
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
                self.info_dock.infoDisplay.append('Please select a guide to be used as a parent')
            else:
                self.bp_settings_ui.bp_parent.edit.setText(selection[0].name())

    def editBlueprintSettingsUI(self, blueprint):
        """
        Shows the settings UI for the selected bp for editing.

        """
        if self.character:
            bpType = blueprint.bpType
            # if you press the same button, ui visibility is toggled
            if self.bp_settings_ui:
                bp_type = self.bp_settings_ui.getType()
                if bp_type == type:
                    if self.bp_settings_ui.isVisible():
                        self.bp_settings_ui.hide()
                    else:
                        self.bp_settings_ui.show()
                        self.bp_settings_ui.bp_name.edit.setText(blueprint.bpName)
                        self.bp_settings_ui.bp_name.edit.setFocus()
                    return

            # delete the settings when a a new blueprint btn is pressed
            if self.bp_settings_ui is not None:
                self.bp_settings_ui.deleteLater()

            # create the blueprints creation/edit settings UI
            settingsClass = self.getSettingsClass(bpType)
            self.bp_settings_ui = settingsClass(bpType)
            self.bp_settings_ui.bp_name.edit.setText(blueprint.bpName)
            self.bp_settings_ui.bp_name.edit.setFocus()

            self.bp_settings_ui.bp_parent.edit.setText(str(blueprint.bpParent))
            self.bp_settings_ui_layout.addWidget(self.bp_settings_ui)
            self.bp_settings_ui.create_bp_btn.clicked.connect(self.createBlueprint)
            self.bp_settings_ui.bp_parent.pickBtn.clicked.connect(self.setBlueprintParent)
        else:
            pm.warning('No character created !!!')
            self.info_dock.infoDisplay.append('No character created !!!')
            self.sender().backColorAnim.start()
            self.char_name.backColorAnim.start()
            self.tabs.setCurrentIndex(0)
            self.char_name.edit.setFocus()

    def editSelectedBlueprint(self):
        selectedBlueprintIndex = self.bp_list.currentRow()
        if selectedBlueprintIndex > 0:
            blueprint = self.character.chBlueprintsList[selectedBlueprintIndex]
            self.editBlueprintSettingsUI(blueprint)
        else:
            self.info_dock.infoDisplay.append('Skeleton Root is not editable, select another blueprint!')

    # ---------------------------------------Static methods---------------------------------------------------------#
    @staticmethod
    def get_bp_files_list():
        # script directory
        utils_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        print '-----------------------------------'
        print utils_folder
        print '-----------------------------------'
        blueprints_folder = os.path.join(utils_folder, 'blueprints') #utils_folder.replace('ui', 'blueprints')

        if os.path.isdir(blueprints_folder):
            blueprint_files = [os.path.splitext(bp_file)[0] for bp_file in os.listdir(blueprints_folder) if
                               bp_file.endswith('.py') and '__init__' not in bp_file and 'character' not in bp_file]
            if len(blueprint_files):
                # blueprint_files.remove('blueprint')
                return blueprint_files
            else:
                return None

    @staticmethod
    def getSettingsClass(bp_type):
        blueprintClass = None
        print inspect.getmembers(blueprint_settings, inspect.isclass)
        classes = [m[1] for m in inspect.getmembers(blueprint_settings, inspect.isclass)
                   if m[1].__module__ == blueprint_settings.__name__]

        for cl in classes:
            print cl
            if cl.TYPE == bp_type:
                return cl
            elif cl.TYPE == 'blueprint':
                blueprintClass = cl

        return blueprintClass


def create():
    """
    Creates the tool window
    """
    if pm.window(rigWin, exists=True, q=True):
        pm.deleteUI(rigWin)

    ui = ToolWindow()
    ui.show()
    # ui.resize(350, 400)
    # ui.char_name.edit.setFocus()
