from maya import OpenMayaUI
import pymel.core as pm
import os
import inspect
import traceback
import ui.blueprint_settings as blueprint_settings
import blueprints.character as char
import mRigGlobals as MRIGLOBALS
from utils import libWidgets as UI
import ui.character_dialog as char_dlg
import ui.blueprint_dialog as bp_dlg

reload(MRIGLOBALS)
reload(char)
reload(blueprint_settings)
reload(char_dlg)
reload(bp_dlg)
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
dlg_name = 'BlueprintDlg'


class Communicate(QObject):
    char_signal = Signal(dict)
    bp_signal = Signal(object)


class ToolWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ToolWindow, self).__init__(*args, **kwargs)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setObjectName(rigWin)
        self.setWindowTitle('Modular Rigging Tool')

        self.signals = Communicate()
        self.signals.char_signal.connect(self.create_character)
        self.signals.bp_signal.connect(self.create_blueprint)
        self.character = None
        self.bp_modules = {}
        self.bp_modules_ui = []
        self.bp_parent = ''
        self.bp_settings_ui = None
        # # ------------------------- UI elements -------------------------
        self.char_widget = QWidget()
        self.char_name = None
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

        # self.char_settings = char_settings.CharSettingsWidget()
        # name_layout = UI.HorBox()
        self.char_name = UI.LabelEditWidget(label='Character name:', label_size=85)
        self.char_name.edit.setReadOnly(1)
        self.char_name.hide()
        #
        # name_layout.addWidget(self.char_name)
        # name_layout.addWidget(self.char_name_suffix)
        #
        # title = UI.TitleBar(title='Name')
        btn_layout = UI.HorBox()
        new_char_btn = UI.ButtonB('NEW')
        new_char_btn.setStyleSheet("background-color: rgb(0,100,200); font-weight: bold")
        delete_char_btn = UI.ButtonB('Rename')
        btn_layout.addWidget(new_char_btn)
        btn_layout.addWidget(delete_char_btn)

        separator = UI.Separator()

        # char_box.layout.addWidget(self.char_settings)
        # char_box.layout.addWidget(title)
        # char_box.layout.addLayout(name_layout)
        char_box.layout.addWidget(self.char_name)
        char_box.layout.addWidget(separator)
        char_box.layout.addLayout(btn_layout)

        char_layout.addWidget(char_box)

        new_char_btn.clicked.connect(self.open_char_dialog)

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
                        module_ui = self.create_bp_ui(mod_name=python_module.BLUEPRINT_TYPE, index=i)
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
        self.bp_list.doubleClicked.connect(self.deselect_bp)

    def add_skeleton_ui(self):
        layout = UI.VertBox()

        skeleton_box = UI.TitledBox(title='    Skeleton')
        create_skeleton_btn = UI.ButtonB('Create')
        skeleton_box.layout.addWidget(create_skeleton_btn)

        layout.addWidget(skeleton_box)
        create_skeleton_btn.clicked.connect(self.build_skeleton)
        self.skeleton_widget.setLayout(layout)

    def add_rigging_ui(self):
        layout = UI.VertBox()

        rig_box = UI.TitledBox(title='    Rig')
        create_rig_btn = UI.ButtonB('RIG IT')
        rig_box.layout.addWidget(create_rig_btn)

        layout.addWidget(rig_box)
        self.rig_widget.setLayout(layout)

        # --------------------------------------------------------------------------------------------------------------

    def open_char_dialog(self):
        """
        Clicked event for self.char_settings.createCharBtn
        Creates a new character
        """
        char_dialog = char_dlg.CharSettingsDialog(parent=self, signal=self.signals)
        char_dialog.show()

    @Slot(dict)
    def create_character(self, info):
        pm.undoInfo(openChunk=True)
        char_name = info['name']
        char_suffix = info['suffix']
        left_str = info['left']
        right_str = info['right']

        if len(char_name) and len(char_suffix):
            char_name = char_name + char_suffix
            self.character = char.Char(name=char_name, leftString=left_str, rightString=right_str)
            self.character.create()
            self.char_name.edit.setText(char_name)
            self.char_name.show()
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

            print [bp.name for bp in self.character.chBlueprintsList]

            for i in range(len(self.character.chBlueprintsList)):
                list_item = QListWidgetItem()
                list_item.setText(self.character.chBlueprintsList[i].name)
                self.bp_list.addItem(list_item)

    def import_python_module(self, bp_name):
        """
        Returns a Python Module

        Arguments:
        bp_name - a string containing the name of the blueprint file without the extension
        """
        top_package = __name__.split('.')[0]
        module_to_import = top_package + '.bd_rig.blueprints.' + bp_name
        # print('------------------>' + module_to_import)
        mod = None

        try:
            mod = __import__(module_to_import, {}, {}, [bp_name])
            reload(mod)
            self.bp_modules[mod.BLUEPRINT_TYPE] = mod
            print ('Imported blueprint module %s' % module_to_import)
        except:
            pm.warning("Error importing python module %s" % module_to_import)
            pm.warning(traceback.format_exc())
        return mod

    def create_bp_ui(self, mod_name, index):
        """
        Implement a desired UI for the blueprint , currently it's just a button

        Arguments:
        modName - string , to be used for the creation button

        Return:
        the ui/widget for the blueprint module
        """
        btn = UI.BlueprintButton(mod_name, index)
        btn.clicked.connect(self.open_blueprint_dialog)
        return btn

    # --------------------------------------------Buttons callbacks ------------------------------------------#
    def open_blueprint_dialog(self):
        """
        Creates or toggles the clicked blueprint creation UI. This will happen ONLY if a character was created

        When a blueprint creation button is clicked, the blueprint settings UI is created. If the same button is pressed, the UI visibility will be toggled.
        When another  blueprint creation button is clicked, the current settings UI is deleted and a new one is created for the new blueprint. The toggle system applies here as well.
        """
        if self.character:
            blueprint = str(self.sender().text())

            # create the blueprints creation/edit settings UI
            if pm.window(dlg_name, exists=True, q=True):
                pm.deleteUI(dlg_name)

            dialog_class = self.get_bp_dialog_class(blueprint)
            bp_dialog = dialog_class(parent=self, category=blueprint, signal=self.signals)
            bp_dialog.show()

        #     self.bp_settings_ui = dialog_class(blueprintType=blueprint)  # blueprint_settings.BlueprintSettingsWidget(type_bp=blueprint)
        #     self.bp_settings_ui.bp_name.edit.setText(blueprint.capitalize())
        #     self.bp_settings_ui.bp_name.edit.setFocus()
        #     selection = pm.ls(sl=1)
        #     if selection and '_guide' in selection[0].name():
        #         self.bp_settings_ui.bp_parent.edit.setText(selection[0].name())
        #     # else:
        #     #     self.bp_settings_ui.bp_parent.edit.setText(
        #     #         self.character.chBlueprintsList[0].guides_list[0].name())
        #
        #     self.bp_settings_ui_layout.addWidget(self.bp_settings_ui)
        #
        #     self.bp_settings_ui.create_bp_btn.clicked.connect(self.create_blueprint)
        #     self.bp_settings_ui.bp_parent.pickBtn.clicked.connect(self.setBlueprintParent)
        #
        else:
            pm.warning('No character created !!!')
            self.info_dock.infoDisplay.append('No character created !!!')
        #     self.sender().backColorAnim.start()
        #     self.char_name.backColorAnim.start()
        #     self.tabs.setCurrentIndex(0)
        #     self.char_name.edit.setFocus()

    @Slot(dict)
    def create_blueprint(self, info):
        """
        Clicked slot from self.bp_settings_ui.create_bp_btn
        It will create the blueprint in Maya
        """
        pm.undoInfo(openChunk=True)
        bp_name = info['name']
        bp_parent = info['parent']
        type_bp = info['type']
        bp_info = info

        if bp_name != '':
            mod = self.bp_modules[type_bp]

            bp_class = getattr(mod, mod.CLASS_NAME)
            if bp_class:
                if not self.character.hasBlueprint(bp_name):
                    bp_new = bp_class(name=bp_name, parent=bp_parent, buildInfo=bp_info, character=self.character)
                    bp_new.create()
                    bp_new.create_link_parent()
                    self.character.addBlueprint(bp_new)
                    self.character.saveCharacterInfo()
                    self.bp_list.addItem(bp_new.name)
                    self.info_dock.infoDisplay.append(
                        'Blueprint \'%s\' of type %s created !' % (bp_name, type_bp))
                    pm.select(bp_new.controller)
                else:
                    self.info_dock.infoDisplay.append(
                        'Blueprint with the name \'%s\' already exists, choose a new name !!!' % bp_name)
                    pm.warning('Blueprint with the name \'%s\' already exists, choose a new name !!!' % bp_name)
            else:
                self.info_dock.infoDisplay.append('Found no blueprint class in module %s!!!' % mod)
                pm.warning('Found no blueprint class in module %s!!!' % mod)
                # self.bp_settings_ui.bp_name.edit.setText("")
        else:
            self.info_dock.infoDisplay.append('Enter a name for the blueprint !')
            print('Enter a name for the blueprint !')
        pm.undoInfo(closeChunk=True)

    def deselect_bp(self):
        self.bp_list.clearSelection()

    def build_skeleton(self):
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
                return blueprint_files
            else:
                return None

    @staticmethod
    def get_settings_class(type_bp):
        bp_class = None
        print inspect.getmembers(blueprint_settings, inspect.isclass)
        classes = [m[1] for m in inspect.getmembers(blueprint_settings, inspect.isclass)
                   if m[1].__module__ == blueprint_settings.__name__]

        for cl in classes:
            print cl
            if cl.TYPE == type_bp:
                return cl
            elif cl.TYPE == 'blueprint':
                bp_class = cl

        return bp_class

    @staticmethod
    def get_bp_dialog_class(type_bp):
        bp_class = None
        print inspect.getmembers(bp_dlg, inspect.isclass)
        classes = [m[1] for m in inspect.getmembers(bp_dlg, inspect.isclass)
                   if m[1].__module__ == bp_dlg.__name__]

        for cl in classes:
            print cl
            if cl.TYPE == type_bp:
                return cl
            elif cl.TYPE == 'blueprint':
                bp_class = cl

        return bp_class


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
