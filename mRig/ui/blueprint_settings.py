from ..utils.qt_handlers import QtCore, QtGui

from ..utils import libWidgets as UI

reload(UI)


# import pymel.core as pm


class BlueprintSettingsWidget(QtGui.QWidget):
    TYPE = 'blueprint'

    def __init__(self, parent=None, blueprintType=''):
        super(BlueprintSettingsWidget, self).__init__(parent)
        self.blueprintType = blueprintType
        self.blueprintInfo = {}

        # -------------------- UI elements --------------------------
        self.inputSettingsLayout = None
        self.blueprintName = None
        self.blueprintParent = None
        self.blueprintLength = None
        self.blueprintGuideSize = None
        self.blueprintMirror = None
        self.createBlueprintBtn = None
        # -----------------------------------------------------------
        self.setupUI()

    def setupUI(self):
        mainLayout = UI.VertBox()
        self.inputSettingsLayout = UI.VertBox()

        separator = UI.Separator()
        titleBar = UI.TitleBar(title=self.blueprintType.title() + ' Settings', height=14)

        self.blueprintName = UI.LabelEditWidget(label='Enter name:')
        self.blueprintName.layout.setContentsMargins(5, 0, 5, 0)
        self.blueprintName.label.setFixedWidth(60)

        self.blueprintParent = UI.ObjectPickerWidget(label='Parent')
        self.blueprintParent.label.setFixedWidth(60)
        self.blueprintParent.layout.setContentsMargins(5, 0, 5, 0)

        self.blueprintLength = UI.SpinBox(label='Length')
        self.blueprintLength.label.setFixedWidth(60)
        self.blueprintLength.layout.setContentsMargins(5, 0, 5, 0)

        self.blueprintLength.spin.setMaximum(1000)
        self.blueprintLength.spin.setMinimum(1)
        self.blueprintLength.spin.setValue(100)

        self.blueprintGuideSize = UI.SpinBox(label='Guide Size')
        self.blueprintGuideSize.label.setFixedWidth(60)
        self.blueprintGuideSize.layout.setContentsMargins(5, 0, 5, 0)

        self.blueprintGuideSize.spin.setMaximum(1000)
        self.blueprintGuideSize.spin.setMinimum(1)
        self.blueprintGuideSize.spin.setValue(3)

        self.createBlueprintBtn = UI.ButtonB('Create Blueprint')
        self.createBlueprintBtn.setStyleSheet("background-color: rgb(0,100,200); font-weight: bold")

        self.inputSettingsLayout.addWidget(self.blueprintName)
        self.inputSettingsLayout.addWidget(self.blueprintParent)
        self.inputSettingsLayout.addWidget(self.blueprintLength)
        self.inputSettingsLayout.addWidget(self.blueprintGuideSize)

        mainLayout.addWidget(separator)
        mainLayout.addWidget(titleBar)
        mainLayout.addLayout(self.inputSettingsLayout)
        mainLayout.addWidget(self.createBlueprintBtn)

        self.setLayout(mainLayout)

    def getType(self):
        return self.blueprintType

    def getInfo(self):
        self.blueprintInfo['length'] = self.blueprintLength.spin.value()
        self.blueprintInfo['guideSize'] = self.blueprintGuideSize.spin.value()
        return self.blueprintInfo


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

        self.spineNumJnt = UI.SpinBox(label='Joint Number')
        self.spineNumJnt.label.setFixedWidth(60)
        self.spineNumJnt.layout.setContentsMargins(5, 0, 5, 0)

        self.spineNumJnt.spin.setValue(3)

        row1layout.addWidget(self.spineNumJnt)

        self.inputSettingsLayout.addWidget(separator)
        self.inputSettingsLayout.addLayout(row1layout)

    def getInfo(self):
        super(SpineSettingsWidget, self).getInfo()
        self.blueprintInfo['spineNumJnt'] = self.spineNumJnt.spin.value()
        return self.blueprintInfo
