import qt_handlers
from qt_handlers import QtCore, QtGui

import pymel.core as pm

MIN_LABEL_WIDTH = 80


class TitledBox(QtGui.QWidget):
    def __init__(self, parent=None, title='Title', settings=0):
        super(TitledBox, self).__init__(parent)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(3)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.groupBox = QtGui.QGroupBox()
        self.groupBoxLayout = QtGui.QVBoxLayout()
        self.groupBoxLayout.setSpacing(3)
        self.groupBoxLayout.setAlignment(QtCore.Qt.AlignTop)
        self.groupBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.titleFrame = QtGui.QFrame()
        self.titleFrame.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        self.titleFrame.setStyleSheet("QFrame { background-color : green; color : white; }")

        self.titleLayout = QtGui.QHBoxLayout()
        self.titleLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QtGui.QLabel(title)
        self.label.setFixedHeight(20)

        self.titleLayout.addWidget(self.label)

        self.settingsBtn = QtGui.QPushButton('+')
        self.settingsBtn.setFixedWidth(20)
        self.settingsBtn.setStyleSheet("QPushButton { background-color : green; color : white; border: none }")

        if settings:
            self.titleLayout.addWidget(self.settingsBtn)

        self.titleFrame.setLayout(self.titleLayout)

        self.groupBoxLayout.addWidget(self.titleFrame)
        self.groupBox.setLayout(self.groupBoxLayout)

        mainLayout.addWidget(self.groupBox)

        self.setLayout(mainLayout)


class LabelEdit(QtGui.QWidget):
    def __init__(self, parent=None, label='Label', validator=None):
        super(LabelEdit, self).__init__(parent)
        self.labelName = label
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)

        self.label = QtGui.QLabel(self.labelName)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)
        self.edit = QtGui.QLineEdit()

        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.edit, 0, 1)

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
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setContentsMargins(0, 0, 0, 0)


class SpinBox(QtGui.QWidget):
    def __init__(self, parent=None, label='------'):
        super(SpinBox, self).__init__(parent)
        self.labelName = label
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)

        self.label = QtGui.QLabel(self.labelName)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        # self.label.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")
        self.spin = QtGui.QSpinBox()
        self.spin.setMinimum(1)

        layout.addWidget(self.label, 0, 0, 1, 1)
        layout.addWidget(self.spin, 0, 1, 1, 1)
        mainLayout.addLayout(layout)

        self.setLayout(mainLayout)


class Picker(QtGui.QWidget):
    def __init__(self, parent=None, label='------'):
        super(SpinBox, self).__init__(parent)
        self.lableName = label
        self.setupUI()

    def setupUI(self):
        mainLayout = VertBox()

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)

        self.label = QtGui.QLabel(self.labelName)
        self.label.setMinimumWidth(MIN_LABEL_WIDTH)

        self.parentNameEdit = QtGui.QLineEdit('Skeleton_Root')

        self.pickBtn = QtGui.QPushButton('<<')

        layout.addWidget(self.label, 0, 0, 1, 1)
        layout.addWidget(self.parentNameEdit, 0, 1, 1, 1)
        layout.addWidget(self.pickBtn, 0, 2, 1, 1)

        mainLayout.addLayout(layout)

        self.setLayout(mainLayout)

        self.pickBtn.clicked.connect(self.pickParent)

    def pickParent(self):
        selection = pm.ls(sl=1, type='transform')
        if selection and len(selection) == 1:
            self.parentNameEdit.setText(selection[0])
