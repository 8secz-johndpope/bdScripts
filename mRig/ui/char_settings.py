from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from ..utils import libWidgets as UI
reload(UI)

from .. import mRigGlobals as MRIGLOBALS
reload(MRIGLOBALS)


class CharSettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CharSettingsWidget, self).__init__(parent)
        self.titleBar = None
        self.leftString = None
        self.rightString = None
        self.rootName = None

        self.setupUI()

    def setupUI(self):
        mainLayout = UI.VertBox()

        self.titleBar = UI.TitleBar(title='Character Settings', height=14)

        row1Layout = UI.HorBox()
        row2Layout = UI.HorBox()

        self.leftString = UI.LabelEditWidget(label='Left String')
        self.leftString.edit.setText('Left')
        self.rightString = UI.LabelEditWidget(label='Right String')
        self.rightString.edit.setText('Right')
        self.rootName = UI.LabelEditWidget(label='Root Name')
        self.rootName.edit.setText('Skeleton_Root')
        splitSeparator = UI.Separator(d=1)

        row1Layout.addWidget(self.leftString)
        row1Layout.addWidget(splitSeparator)
        row1Layout.addWidget(self.rightString)
        row2Layout.addWidget(self.rootName)
        separator2 = UI.Separator()

        mainLayout.addWidget(self.titleBar)
        mainLayout.addLayout(row1Layout)
        mainLayout.addWidget(separator2)
        mainLayout.addLayout(row2Layout)

        self.setLayout(mainLayout)
