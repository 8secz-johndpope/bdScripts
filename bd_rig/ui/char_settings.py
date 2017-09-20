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


class CharSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(CharSettingsWidget, self).__init__(parent)
        self.title_bar = None
        self.left_str = None
        self.right_str = None
        # self.root_name = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = UI.VertBox()

        self.title_bar = UI.TitleBar(title='Settings', height=14)

        row1_layout = UI.HorBox()
        row1_layout.setAlignment(Qt.AlignLeft)
        # row2_layout = UI.HorBox()

        self.left_str = UI.LabelEditWidget(label='Left String:', label_size=60, edit_size=40)
        self.left_str.edit.setText('Left')
        self.right_str = UI.LabelEditWidget(label='Right String:', label_size=65, edit_size=40)
        self.right_str.edit.setText('Right')
        # self.root_name = UI.LabelEditWidget(label='Root Name')
        # self.root_name.edit.setText('Skeleton_Root')
        split_separator = UI.Separator(d=1)

        row1_layout.addWidget(self.left_str)
        row1_layout.addWidget(split_separator)
        row1_layout.addWidget(self.right_str)
        # row2_layout.addWidget(self.root_name)
        separator2 = UI.Separator()

        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(row1_layout)
        main_layout.addWidget(separator2)
        # main_layout.addLayout(row2_layout)

        self.setLayout(main_layout)
