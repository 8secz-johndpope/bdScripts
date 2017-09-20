import qt_handlers
from qt_handlers import QtCore, QtGui

import pymel.core as pm

MIN_LABEL_WIDTH = 40


class ButtonB(QtGui.QPushButton):
    def __init__(self, parent=None):
        super(ButtonB, self).__init__(parent)
        self.setFixedHeight(20)
        # self.setStyleSheet("border-top: 3px ;border-bottom: 3px ;border-right: 10px ;border-left:10px;")


class BlueprintButton(QtGui.QPushButton):
    def __init__(self, parent=None, index=0):
        super(BlueprintButton, self).__init__(parent)
        self.index = index

        color1 = QtGui.QColor(255, 255, 255)
        color2 = QtGui.QColor(255, 0, 0)

        self.backColorAnim = QtCore.QPropertyAnimation(self, "backColor")
        self.backColorAnim.setDuration(250)
        self.backColorAnim.setLoopCount(4)
        self.backColorAnim.setStartValue(color1)
        self.backColorAnim.setKeyValueAt(0.5, color2)
        self.backColorAnim.setEndValue(color1)

    def getBackColor(self):
        return self.palette().text()

    def setBackColor(self, color):
        pal = self.palette()
        pal.setColor(self.foregroundRole(), color)
        self.setPalette(pal)

    backColor = QtCore.Property(QtGui.QColor, getBackColor, setBackColor)


class TitledBox(QtGui.QGroupBox):
    def __init__(self, parent=None, title='Title', direction='v'):
        super(TitledBox, self).__init__(parent)
        self.title = title
        self.direction = direction
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = VertBox()
        if self.direction == 'h':
            self.layout.deleteLater()
            self.layout = HorBox()

        self.titleBar = TitleBar(title=self.title, height=20, color=(0, 80, 25))

        mainLayout.addWidget(self.titleBar)
        mainLayout.addLayout(self.layout)

        self.setLayout(mainLayout)


class LabelEditWidget(QtGui.QWidget):
    def __init__(self, parent=None, label=''):
        super(LabelEditWidget, self).__init__(parent)
        self.labelName = label
        self.label = None

        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        if self.labelName != '':
            self.label = QtGui.QLabel(self.labelName)
            self.layout.addWidget(self.label)

        self.edit = QtGui.QLineEdit()
        self.edit.setValidator(CharNameValidator())

        color1 = self.edit.palette().color(self.edit.backgroundRole())
        color2 = QtGui.QColor(255, 0, 0)

        self.backColorAnim = QtCore.QPropertyAnimation(self, "backColor")
        self.backColorAnim.setDuration(250)
        self.backColorAnim.setLoopCount(4)
        self.backColorAnim.setStartValue(color1)
        self.backColorAnim.setKeyValueAt(0.5, color2)
        self.backColorAnim.setEndValue(color1)

        self.layout.addWidget(self.edit)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)

    def getBackColor(self):
        return self.edit.palette().color(QtGui.QPalette.Background)

    def setBackColor(self, color):
        self.edit.setStyleSheet(
            "QLineEdit { background: rgb(" + str(color.red()) + "," + str(color.green()) + "," + str(
                color.blue()) + "); }")

    backColor = QtCore.Property(QtGui.QColor, getBackColor, setBackColor)


class ObjectPickerWidget(QtGui.QWidget):
    def __init__(self, parent=None, label=''):
        super(ObjectPickerWidget, self).__init__(parent)
        self.labelTitle = label
        self.label = None

        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        if self.labelTitle != '':
            self.label = QtGui.QLabel(self.labelTitle)
            self.layout.addWidget(self.label)

        self.edit = QtGui.QLineEdit()
        self.edit.setReadOnly(1)

        self.pickBtn = ButtonB('<<')

        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.pickBtn)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)


class SpinBox(QtGui.QWidget):
    def __init__(self, parent=None, label='Number'):
        super(SpinBox, self).__init__(parent)
        self.labelName = label
        self.label = None
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtGui.QGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.label = QtGui.QLabel(self.labelName)
        self.spin = QtGui.QSpinBox()

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spin, 0, 1)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)


class LabelComboWidget(QtGui.QWidget):
    def __init__(self, parent=None, label='Label', validator=None):
        super(LabelComboWidget, self).__init__(parent)
        self.labelName = label
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)

        self.label = QtGui.QLabel(self.labelName)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)
        self.combo = QtGui.QComboBox()

        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.combo, 0, 1)

        mainLayout.addLayout(layout)
        self.setLayout(mainLayout)


class VertBox(QtGui.QVBoxLayout):
    def __init__(self, *args, **kargs):
        super(VertBox, self).__init__(*args, **kargs)
        self.setSpacing(3)
        self.setAlignment(QtCore.Qt.AlignTop)
        self.setContentsMargins(0, 0, 0, 0)


class HorBox(QtGui.QHBoxLayout):
    def __init__(self, *args, **kargs):
        super(HorBox, self).__init__(*args, **kargs)
        self.setSpacing(3)
        self.setContentsMargins(0, 0, 0, 0)


class Separator(QtGui.QWidget):
    def __init__(self, parent=None, d=0):
        super(Separator, self).__init__(parent)
        self.direction = d
        self.setupUI()

    def setupUI(self):
        mainLayout = HorBox()

        separator = QtGui.QFrame()
        separator.setFrameShape(QtGui.QFrame.HLine)
        if self.direction:
            separator.setFrameShape(QtGui.QFrame.VLine)

        separator.setLineWidth(0.5)
        separator.setContentsMargins(0, 0, 0, 0)

        mainLayout.addWidget(separator)
        self.setLayout(mainLayout)


class TitleBar(QtGui.QWidget):
    def __init__(self, parent=None, title='', height=12, color=(0, 28, 36)):
        super(TitleBar, self).__init__(parent)
        self.title = title
        self.height = height
        self.color = str(color)
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        titleFrame = QtGui.QFrame()
        titleFrame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        titleFrame.setStyleSheet("QFrame { background-color : rgba" + self.color + "; color : white; }")

        titleLayout = QtGui.QHBoxLayout()
        titleLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QtGui.QLabel(self.title)
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.label.setFixedHeight(self.height)

        titleLayout.addWidget(self.label)

        titleFrame.setLayout(titleLayout)

        mainLayout.addWidget(titleFrame)

        self.setLayout(mainLayout)


class CharNameValidator(QtGui.QValidator):
    def __init__(self, parent=None):
        super(CharNameValidator, self).__init__(parent)

    def fixup(self, input):
        pass

    def validate(self, input, pos):
        import string
        allowed_chars = string.ascii_letters + string.digits + "_"
        if all([c in allowed_chars for c in input]):
            return QtGui.QValidator.Acceptable
        else:
            return QtGui.QValidator.Invalid


class InfoDock(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super(InfoDock, self).__init__(parent)
        self.setWindowTitle('Output Info')
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)

        self.setupUI()

    def setupUI(self):
        infoFrame = QtGui.QFrame()
        infoLayout = QtGui.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop)
        infoLayout.setContentsMargins(0, 0, 0, 0)

        self.infoDisplay = QtGui.QTextEdit()
        self.infoDisplay.setMinimumHeight(50)
        self.infoDisplay.setReadOnly(1)

        infoFrame.setLayout(infoLayout)
        infoLayout.addWidget(self.infoDisplay)

        self.setWidget(infoFrame)
