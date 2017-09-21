import pymel.core as pm
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *

from ..utils import libWidgets as UI
reload(UI)

dlg_name = 'BlueprintDlg'


class BlueprintDialog(QDialog):
    TYPE = 'blueprint'
    
    def __init__(self, parent=None, category='', signal=None):
        super(BlueprintDialog, self).__init__(parent)
        self.setParent(parent)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowTitle('Blueprint Settings')
        self.setObjectName(dlg_name)

        self.signal = signal.bp_signal
        self.bp_type = category
        self.bp_info = {}

        # -------------------- UI elements --------------------------
        self.bp_ui_layout = None
        self.bp_name = None
        self.bp_parent = None
        self.bp_length = None
        self.bp_guide_size = None
        self.bp_mirror = None
        self.create_bp_btn = None
        # -----------------------------------------------------------
        self.setup_ui()

    def setup_ui(self):
        main_layout = UI.VertBox()
        self.bp_ui_layout = UI.VertBox()

        separator = UI.Separator()
        title_bar = UI.TitleBar(title=self.bp_type.title() + ' Settings', height=14)

        self.bp_name = UI.LabelEditWidget(label='Enter name:')
        self.bp_name.edit.setText(self.bp_type.capitalize())
        self.bp_name.layout.setContentsMargins(5, 0, 5, 0)
        self.bp_name.label.setFixedWidth(60)

        self.bp_parent = UI.ObjectPickerWidget(label='Parent')
        self.bp_parent.label.setFixedWidth(60)
        self.bp_parent.layout.setContentsMargins(5, 0, 5, 0)
        self.bp_parent.pickBtn.clicked.connect(self.set_bp_parent_text)

        self.bp_length = UI.SpinWidget(label='Length')
        self.bp_length.label.setFixedWidth(60)
        self.bp_length.layout.setContentsMargins(5, 0, 5, 0)

        self.bp_length.spin.setMaximum(1000)
        self.bp_length.spin.setMinimum(1)
        self.bp_length.spin.setValue(100)

        self.bp_guide_size = UI.SpinWidget(label='Guide Size')
        self.bp_guide_size.label.setFixedWidth(60)
        self.bp_guide_size.layout.setContentsMargins(5, 0, 5, 0)

        self.bp_guide_size.spin.setMaximum(1000)
        self.bp_guide_size.spin.setMinimum(1)
        self.bp_guide_size.spin.setValue(3)

        self.create_bp_btn = UI.ButtonB('Create Blueprint')
        self.create_bp_btn.setStyleSheet("background-color: rgb(0,100,200); font-weight: bold")
        self.create_bp_btn.clicked.connect(self.send_data)

        self.bp_ui_layout.addWidget(self.bp_name)
        self.bp_ui_layout.addWidget(self.bp_parent)
        self.bp_ui_layout.addWidget(self.bp_length)
        self.bp_ui_layout.addWidget(self.bp_guide_size)

        main_layout.addWidget(separator)
        main_layout.addWidget(title_bar)
        main_layout.addLayout(self.bp_ui_layout)
        main_layout.addWidget(self.create_bp_btn)

        self.setLayout(main_layout)

    def get_type(self):
        return self.bp_type

    def get_info(self):
        # self.bp_mirror = None
        self.bp_info['name'] = self.bp_name.edit.text()
        self.bp_info['parent'] = self.bp_parent.edit.text()
        self.bp_info['length'] = self.bp_length.spin.value()
        self.bp_info['guideSize'] = self.bp_guide_size.spin.value()
        self.bp_info['type'] = self.bp_type
        return self.bp_info

    def send_data(self):
        self.signal.emit(self.get_info())
        super(BlueprintDialog, self).accept()

    def set_bp_parent_text(self):
        selection = pm.ls(sl=1)
        try:
            self.bp_parent.edit.setText(selection[0].name())
        except:
            pm.warning('Nothing or more than one object was selected')


class BlueprintSpineDialog(BlueprintDialog):
    TYPE = 'spine'

    def __init__(self, parent=None, category='', signal=None):
        super(BlueprintSpineDialog, self).__init__(parent, category=category, signal=signal)
        # --------------------- UI elements -------------------
        self.spineNumJnt = None

        self.append_ui()

    def append_ui(self):
        separator = UI.Separator()

        row1layout = UI.HorBox()

        self.spineNumJnt = UI.SpinWidget(label='Joint Number')
        self.spineNumJnt.label.setFixedWidth(60)
        self.spineNumJnt.layout.setContentsMargins(5, 0, 5, 0)

        self.spineNumJnt.spin.setValue(3)

        row1layout.addWidget(self.spineNumJnt)

        self.bp_ui_layout.addWidget(separator)
        self.bp_ui_layout.addLayout(row1layout)

    def get_info(self):
        super(BlueprintSpineDialog, self).get_info()
        self.bp_info['num_jnt'] = self.spineNumJnt.spin.value()
        return self.bp_info
