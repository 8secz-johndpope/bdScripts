from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

# import qt_handlers as qtHandlers
# reload(qtHandlers)
#
# from qt_handlers import *

MIN_LABEL_WIDTH = 40


class ButtonB(QtWidgets.QPushButton):
    def __init__(self, parent=None, index=0):
        super(ButtonB, self).__init__(parent)
        self.setFixedHeight(20)

        # self.setStyleSheet("border-top: 3px ;border-bottom: 3px ;border-right: 10px ;border-left:10px;")

class ButtonBack(QtWidgets.QPushButton):
    def __init__(self, parent, index ):
        super(ButtonBack, self).__init__(parent)
        self.setFixedHeight(20)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.index = index
        self.setStyleSheet("background-color: #4498bf; ")

class ActionButton(QtWidgets.QPushButton):
    def __init__(self, parent):
        super(ActionButton, self).__init__(parent)
        self.setFixedHeight(20)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet("background-color: #3ba04d; ")

class BlueprintButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, index=0):
        super(BlueprintButton, self).__init__(parent)
        self.setFixedHeight(17)
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


class TitledBox(QtWidgets.QGroupBox):
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

        self.titleBar = TitleBar(title=self.title, height=20, color=(0, 161, 114))

        mainLayout.addWidget(self.titleBar)
        mainLayout.addLayout(self.layout)

        self.setLayout(mainLayout)


class LabelEditWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label=''):
        super(LabelEditWidget, self).__init__(parent)
        self.labelName = label
        self.label = None
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        if self.labelName != '':
            self.label = QtWidgets.QLabel(self.labelName)
            self.layout.addWidget(self.label)
            self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        self.edit = QtWidgets.QLineEdit()

        self.layout.addWidget(self.edit)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)


class ObjectPickerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label=''):
        super(ObjectPickerWidget, self).__init__(parent)
        self.labelTitle = label
        self.label = None

        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        if self.labelTitle != '':
            self.label = QtWidgets.QLabel(self.labelTitle)
            self.layout.addWidget(self.label)
            self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        self.edit = QtWidgets.QLineEdit()
        self.edit.setReadOnly(1)

        self.pickBtn = ButtonB('<<')
        self.pickBtn.released.connect(self.setObject)

        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.pickBtn)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)

    def setObject(self):
        selection = pm.ls(sl=1, type='transform')
        if selection:
            self.edit.setText(selection[0].name())
        else:
            pm.warning('No transform selected!')


class SpinWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label='Number'):
        super(SpinWidget, self).__init__(parent)
        self.labelName = label
        self.label = None
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.label = QtWidgets.QLabel(self.labelName)
        self.spin = QtWidgets.QSpinBox()

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spin, 0, 1)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)


class FloatSpinWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label='Number'):
        super(FloatSpinWidget, self).__init__(parent)
        self.labelName = label
        self.label = None
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.label = QtWidgets.QLabel(self.labelName)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setMinimumWidth(100)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spin, 0, 1)

        mainLayout.addLayout(self.layout)
        self.setLayout(mainLayout)


class LabelComboWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, label='Label', validator=None):
        super(LabelComboWidget, self).__init__(parent)
        self.labelName = label
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(1, 1)

        self.label = QtWidgets.QLabel(self.labelName)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)
        self.combo = QtWidgets.QComboBox()

        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.combo, 0, 1)

        mainLayout.addLayout(layout)
        self.setLayout(mainLayout)


class VertBox(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kargs):
        super(VertBox, self).__init__(*args, **kargs)
        self.setSpacing(3)
        self.setAlignment(QtCore.Qt.AlignTop)
        self.setContentsMargins(0, 0, 0, 0)


class HorBox(QtWidgets.QHBoxLayout):
    def __init__(self, *args, **kargs):
        super(HorBox, self).__init__(*args, **kargs)
        self.setSpacing(3)
        self.setContentsMargins(0, 0, 0, 0)


class Separator(QtWidgets.QWidget):
    def __init__(self, parent=None, d=0):
        super(Separator, self).__init__(parent)
        self.direction = d
        self.setupUI()

    def setupUI(self):
        mainLayout = HorBox()

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        if self.direction:
            separator.setFrameShape(QtWidgets.QFrame.VLine)

        separator.setLineWidth(0.5)
        separator.setContentsMargins(0, 0, 0, 0)

        mainLayout.addWidget(separator)
        self.setLayout(mainLayout)


class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None, title='', height=12, color=(120, 28, 36)):
        super(TitleBar, self).__init__(parent)
        self.title = title
        self.height = height
        self.color = str(color)
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        titleFrame = QtWidgets.QFrame()
        titleFrame.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        titleFrame.setStyleSheet("QFrame { background-color : rgba" + self.color + "; color : white; }")

        titleLayout = QtWidgets.QHBoxLayout()
        titleLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QtWidgets.QLabel(self.title)
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


class InfoDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(InfoDock, self).__init__(parent)
        self.setWindowTitle('Output Info')
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)

        self.setupUI()

    def setupUI(self):
        infoFrame = QtWidgets.QFrame()
        infoLayout = QtWidgets.QVBoxLayout()
        infoLayout.setAlignment(QtCore.Qt.AlignTop)
        infoLayout.setContentsMargins(0, 0, 0, 0)

        self.infoDisplay = QtWidgets.QTextEdit()
        self.infoDisplay.setMinimumHeight(50)
        self.infoDisplay.setReadOnly(1)

        infoFrame.setLayout(infoLayout)
        infoLayout.addWidget(self.infoDisplay)

        self.setWidget(infoFrame)
