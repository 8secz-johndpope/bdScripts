try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *


from ..utils import libWidgets as UI
reload(UI)

from .. import mRigGlobals as MRIGLOBALS
reload(MRIGLOBALS)


class CharSettingsDialog(QDialog):
    def __init__(self, parent=None, signal=None):
        super(CharSettingsDialog, self).__init__()
        self.setParent(parent)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowTitle('Character Settings')

        self.title_bar = None
        self.left_str = None
        self.right_str = None
        self.name_edit = None
        self.suffix_edit = None
        self.signal = signal.char_signal
        print self.signal
        # self.root_name = None

        self.setup_ui()
        self.setFixedSize(250, 150)

    def setup_ui(self):
        main_layout = UI.VertBox()

        self.title_bar = UI.TitleBar(title='Settings', height=14)

        row1_layout = UI.HorBox()
        row1_layout.setContentsMargins(3, 0, 0, 0)
        row2_layout = UI.HorBox()
        row2_layout.setContentsMargins(3, 0, 0, 0)
        row3_layout = UI.HorBox()
        row3_layout.setContentsMargins(3, 0, 3, 3)

        self.name_edit = UI.LabelEditWidget(label='Character name', label_size=100, edit_size=80)
        self.suffix_edit = UI.LabelEditWidget(label='+', label_size=10, edit_size=40)
        self.suffix_edit.edit.setText('_' + MRIGLOBALS.CHAR)
        self.left_str = UI.LabelEditWidget(label='Left String:', label_size=60, edit_size=40)
        self.left_str.edit.setText('Left')
        self.right_str = UI.LabelEditWidget(label='Right String:', label_size=65, edit_size=40)
        self.right_str.edit.setText('Right')

        separator1 = UI.Separator(d=1)
        separator2 = UI.Separator()
        separator3 = UI.Separator()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,Qt.Horizontal, self)
        buttons.accepted.connect(self.send_data)
        buttons.rejected.connect(self.reject)

        # self.root_name = UI.LabelEditWidget(label='Root Name')
        # self.root_name.edit.setText('Skeleton_Root')
        row1_layout.addWidget(self.name_edit)
        row1_layout.addWidget(self.suffix_edit)
        # row1_layout.addWidget(separator1)

        row2_layout.addWidget(self.left_str)
        row2_layout.addWidget(separator1)
        row2_layout.addWidget(self.right_str)

        row3_layout.addWidget(buttons)

        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(row1_layout)
        main_layout.addWidget(separator2)
        main_layout.addLayout(row2_layout)
        main_layout.addWidget(separator3)
        main_layout.addLayout(row3_layout)

        self.setLayout(main_layout)

    def get_info(self):
        info = dict()
        info['name'] = self.name_edit.edit.text()
        info['suffix'] = self.suffix_edit.edit.text()
        info['left'] = self.left_str.edit.text()
        info['right'] = self.right_str.edit.text()

        return info

    def send_data(self):
        self.signal.emit(self.get_info())
        super(CharSettingsDialog, self).accept()



