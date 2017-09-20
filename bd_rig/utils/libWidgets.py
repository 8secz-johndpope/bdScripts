import pymel.core as pm
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *


MIN_LABEL_WIDTH = 40


class ButtonB(QPushButton):
    def __init__(self, parent=None, index=0):
        super(ButtonB, self).__init__(parent)
        self.setFixedHeight(20)

        # self.setStyleSheet("border-top: 3px ;border-bottom: 3px ;border-right: 10px ;border-left:10px;")


class BlueprintButton(QPushButton):
    def __init__(self, parent=None, index=0):
        super(BlueprintButton, self).__init__(parent)
        self.setFixedHeight(17)
        self.index = index

        color1 = QColor(255, 255, 255)
        color2 = QColor(255, 0, 0)

        self.backColorAnim = QPropertyAnimation(self, "backColor")
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

    backColor = Property(QColor, getBackColor, setBackColor)


class TitledBox(QGroupBox):
    def __init__(self, parent=None, title='Title', direction='v'):
        super(TitledBox, self).__init__(parent)
        self.title = title
        self.direction = direction

        self.layout = None
        self.title_bar = None
        self.central_widget = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()
        self.central_widget = QWidget()

        self.layout = VertBox()
        if self.direction == 'h':
            self.layout.deleteLater()
            self.layout = HorBox()

        self.title_bar = TitleBar(title=self.title, height=20, color=(0, 161, 114))

        self.central_widget.setLayout(self.layout)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.central_widget)

        self.setLayout(main_layout)


class LabelEditWidget(QWidget):
    def __init__(self, parent=None, label='', label_size=MIN_LABEL_WIDTH, edit_size=MIN_LABEL_WIDTH):
        super(LabelEditWidget, self).__init__(parent)
        self.label_name = label
        self.label_size = label_size
        self.edit_size = edit_size
        self.label = None
        self.layout = None
        self.edit = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        if self.label_name != '':
            self.label = QLabel(self.label_name)
            self.layout.addWidget(self.label)
            self.label.setFixedWidth(self.label_size)

        self.edit = QLineEdit()
        self.edit.setFixedWidth(self.edit_size)
        self.layout.addWidget(self.edit, Qt.AlignLeft)

        main_layout.addLayout(self.layout)
        self.setLayout(main_layout)


class ObjectPickerWidget(QWidget):
    def __init__(self, parent=None, label=''):
        super(ObjectPickerWidget, self).__init__(parent)
        self.labelTitle = label
        self.label = None

        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        if self.labelTitle != '':
            self.label = QLabel(self.labelTitle)
            self.layout.addWidget(self.label)
            self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        self.edit = QLineEdit()
        self.edit.setReadOnly(1)

        self.pickBtn = ButtonB('<<')
        self.pickBtn.released.connect(self.setObject)

        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.pickBtn)

        main_layout.addLayout(self.layout)
        self.setLayout(main_layout)

    def setObject(self):
        selection = pm.ls(sl=1, type='transform')
        if selection:
            self.edit.setText(selection[0].name())
        else:
            pm.warning('No transform selected!')


class SpinWidget(QWidget):
    def __init__(self, parent=None, label='Number'):
        super(SpinWidget, self).__init__(parent)
        self.label_name = label
        self.label = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()

        self.layout = QGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.label = QLabel(self.label_name)
        self.spin = QSpinBox()

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spin, 0, 1)

        main_layout.addLayout(self.layout)
        self.setLayout(main_layout)


class FloatSpinWidget(QWidget):
    def __init__(self, parent=None, label='Number'):
        super(FloatSpinWidget, self).__init__(parent)
        self.label_name = label
        self.label = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()

        self.layout = QGridLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.label = QLabel(self.label_name)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        self.spin = QDoubleSpinBox()
        self.spin.setMinimumWidth(100)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spin, 0, 1)

        main_layout.addLayout(self.layout)
        self.setLayout(main_layout)


class LabelComboWidget(QWidget):
    def __init__(self, parent=None, label='Label', validator=None):
        super(LabelComboWidget, self).__init__(parent)
        self.label_name = label
        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)

        self.label = QLabel(self.label_name)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)
        self.combo = QComboBox()

        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.combo, 0, 1)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)


class VertBox(QVBoxLayout):
    def __init__(self, *args, **kargs):
        super(VertBox, self).__init__(*args, **kargs)
        self.setSpacing(3)
        self.setAlignment(Qt.AlignTop)
        self.setContentsMargins(0, 0, 0, 0)


class HorBox(QHBoxLayout):
    def __init__(self, *args, **kargs):
        super(HorBox, self).__init__(*args, **kargs)
        self.setSpacing(3)
        self.setContentsMargins(0, 0, 0, 0)


class Separator(QWidget):
    def __init__(self, parent=None, d=0):
        super(Separator, self).__init__(parent)
        self.direction = d
        self.setup_ui()

    def setup_ui(self):
        main_layout = HorBox()

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        if self.direction:
            separator.setFrameShape(QFrame.VLine)

        separator.setLineWidth(0.5)
        separator.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(separator)
        self.setLayout(main_layout)


class TitleBar(QWidget):
    def __init__(self, parent=None, title='', height=12, color=(0, 28, 36)):
        super(TitleBar, self).__init__(parent)
        self.title = title
        self.height = height
        self.color = str(color)
        self.setup_ui()

    def setup_ui(self):
        main_layout = VertBox()

        titleFrame = QFrame()
        titleFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        titleFrame.setStyleSheet("QFrame { background-color : rgba" + self.color + "; color : white; }")

        titleLayout = QHBoxLayout()
        titleLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.title)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label.setFixedHeight(self.height)

        titleLayout.addWidget(self.label)

        titleFrame.setLayout(titleLayout)

        main_layout.addWidget(titleFrame)

        self.setLayout(main_layout)


class CharNameValidator(QValidator):
    def __init__(self, parent=None):
        super(CharNameValidator, self).__init__(parent)

    def fixup(self, input):
        pass

    def validate(self, input, pos):
        import string
        allowed_chars = string.ascii_letters + string.digits + "_"
        if all([c in allowed_chars for c in input]):
            return QValidator.Acceptable
        else:
            return QValidator.Invalid


class InfoDock(QDockWidget):
    def __init__(self, parent=None):
        super(InfoDock, self).__init__(parent)
        self.setWindowTitle('Output Info')
        self.setAllowedAreas(Qt.BottomDockWidgetArea)

        self.setup_ui()

    def setup_ui(self):
        infoFrame = QFrame()
        infoLayout = QVBoxLayout()
        infoLayout.setAlignment(Qt.AlignTop)
        infoLayout.setContentsMargins(0, 0, 0, 0)

        self.infoDisplay = QTextEdit()
        self.infoDisplay.setMinimumHeight(50)
        self.infoDisplay.setReadOnly(1)

        infoFrame.setLayout(infoLayout)
        infoLayout.addWidget(self.infoDisplay)

        self.setWidget(infoFrame)
