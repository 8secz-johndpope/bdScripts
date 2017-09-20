try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *

from ..utils import libWidgets as UI
reload(UI)


class BlueprintSettingsWidget(QWidget):
    TYPE = 'blueprint'

    def __init__(self, parent=None, blueprintType=''):
        super(BlueprintSettingsWidget, self).__init__(parent)
        self.bp_type = blueprintType
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
        mainLayout = UI.VertBox()
        self.bp_ui_layout = UI.VertBox()

        separator = UI.Separator()
        titleBar = UI.TitleBar(title=self.bp_type.title() + ' Settings', height=14)

        self.bp_name = UI.LabelEditWidget(label='Enter name:')
        self.bp_name.layout.setContentsMargins(5, 0, 5, 0)
        self.bp_name.label.setFixedWidth(60)

        self.bp_parent = UI.ObjectPickerWidget(label='Parent')
        self.bp_parent.label.setFixedWidth(60)
        self.bp_parent.layout.setContentsMargins(5, 0, 5, 0)

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

        self.bp_ui_layout.addWidget(self.bp_name)
        self.bp_ui_layout.addWidget(self.bp_parent)
        self.bp_ui_layout.addWidget(self.bp_length)
        self.bp_ui_layout.addWidget(self.bp_guide_size)

        mainLayout.addWidget(separator)
        mainLayout.addWidget(titleBar)
        mainLayout.addLayout(self.bp_ui_layout)
        mainLayout.addWidget(self.create_bp_btn)

        self.setLayout(mainLayout)

    def getType(self):
        return self.bp_type

    def getInfo(self):
        self.bp_info['length'] = self.bp_length.spin.value()
        self.bp_info['guideSize'] = self.bp_guide_size.spin.value()
        return self.bp_info


class SpineSettingsWidget(BlueprintSettingsWidget):
    TYPE = 'spine'

    def __init__(self, parent=None, blueprintType=''):
        super(SpineSettingsWidget, self).__init__(parent, blueprintType=blueprintType)
        # --------------------- UI elements -------------------
        self.spineNumJnt = None

        self.appendUI()

    def appendUI(self):
        separator = UI.Separator()

        row1layout = UI.HorBox()

        self.spineNumJnt = UI.SpinWidget(label='Joint Number')
        self.spineNumJnt.label.setFixedWidth(60)
        self.spineNumJnt.layout.setContentsMargins(5, 0, 5, 0)

        self.spineNumJnt.spin.setValue(3)

        row1layout.addWidget(self.spineNumJnt)

        self.bp_ui_layout.addWidget(separator)
        self.bp_ui_layout.addLayout(row1layout)

    def getInfo(self):
        super(SpineSettingsWidget, self).getInfo()
        self.bp_info['spineNumJnt'] = self.spineNumJnt.spin.value()
        return self.bp_info
