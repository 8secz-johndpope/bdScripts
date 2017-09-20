# Copyright (c) 2012-2013 Guillaume Barlier
# This file is part of "anim_picker" and covered by the LGPLv3 or later,
# read COPYING and COPYING.LESSER for details.

from maya import OpenMayaUI

SLOT = None
SIGNAL = None
PySide = False
PySide2 = False
PySides = False
PyQt4 = False

qMainWindow = object
qWidget = object
qSplitter = object
qGroupBox = object
qPushButton = object
qHBoxLayout = object
qVBoxLayout = object
qGridLayout = object
qFormLayout = object
qLayout = object
qLabel = object
qLineEdit = object
qCheckBox = object
qSpinBox = object
qDoubleSpinBox = object
qSlider = object
qFrame = object
qRadioButton = object
qButtonGroup = object
qScrollArea = object
qCursor = object
qProgressBar = object
qDialog = object
qMenu = object
qApplication = object
qDesktopWidget = object
qHBoxLayout = object
qToolTip = object
qFont = object
qListWidget = object
qListWidgetItem = object
qAbstractItemView = object
qPoint = object
qValidator = object
qComboBox = object
qDockWidget = object
qTabWidget = object
qTextEdit = object

try:
    # import shiboken
    from PySide2 import QtGui, QtCore, QtWidgets
    import shiboken2 as shiboken
    # import pysideuic
    from cStringIO import StringIO

    SLOT = QtCore.Slot()
    SIGNAL = QtCore.Signal()
    PySide2 = True
    print '\nusing PySide2'
except ImportError, e:
    # print( traceback.format_exc())
    try:
        import shiboken
        from PySide import QtGui, QtCore
        import pysideuic
        from cStringIO import StringIO

        SLOT = QtCore.Slot()
        SIGNAL = QtCore.Signal()
        PySide = True
        print '\nusing PySide'
    except ImportError, e:
        try:

            from PyQt4 import QtGui, QtCore, uic
            import sip

            SLOT = QtCore.pyqtSlot()
            SIGNAL = QtCore.pyqtSignal()
            PyQt4 = True
            print '\nusing PyQt4'
        except:
            print '\nNo pythonQT found'
            pass

if PySide or PyQt4:
    qMainWindow = QtGui.QMainWindow
    qWidget = QtGui.QWidget
    qSplitter = QtGui.QSplitter
    qGroupBox = QtGui.QGroupBox
    qPushButton = QtGui.QPushButton
    qHBoxLayout = QtGui.QHBoxLayout
    qVBoxLayout = QtGui.QVBoxLayout
    qGridLayout = QtGui.QGridLayout
    qFormLayout = QtGui.QFormLayout
    qLayout = QtGui.QLayout
    qLabel = QtGui.QLabel
    qLineEdit = QtGui.QLineEdit
    qCheckBox = QtGui.QCheckBox
    qSpinBox = QtGui.QSpinBox
    qDoubleSpinBox = QtGui.QDoubleSpinBox
    qSlider = QtGui.QSlider
    qFrame = QtGui.QFrame
    qRadioButton = QtGui.QRadioButton
    qScrollArea = QtGui.QScrollArea
    qButtonGroup = QtGui.QButtonGroup
    qCursor = QtGui.QCursor
    qProgressBar = QtGui.QProgressBar
    qDialog = QtGui.QDialog
    qSizePolicy = QtGui.QSizePolicy
    qMenu = QtGui.QMenu
    qApplication = QtGui.QApplication
    qDesktopWidget = QtGui.QDesktopWidget
    qToolTip = QtGui.QToolTip
    qListWidget = QtGui.QListWidget
    qListWidgetItem = QtGui.QListWidgetItem
    qAbstractItemView = QtGui.QAbstractItemView
    qPoint = QtCore.QPoint
    qValidator = QtGui.QValidator
    qComboBox = QtGui.QComboBox
    qDockWidget = QtGui.QDockWidget
    qTabWidget = QtGui.QTabWidget
    qTextEdit = QtGui.QTextEdit

if PySide2:
    qMainWindow = QtWidgets.QMainWindow
    qWidget = QtWidgets.QWidget
    qSplitter = QtWidgets.QSplitter
    qGroupBox = QtWidgets.QGroupBox
    qPushButton = QtWidgets.QPushButton
    qHBoxLayout = QtWidgets.QHBoxLayout
    qVBoxLayout = QtWidgets.QVBoxLayout
    qGridLayout = QtWidgets.QGridLayout
    qFormLayout = QtWidgets.QFormLayout
    qLayout = QtWidgets.QLayout
    qLabel = QtWidgets.QLabel
    qLineEdit = QtWidgets.QLineEdit
    qCheckBox = QtWidgets.QCheckBox
    qSpinBox = QtWidgets.QSpinBox
    qDoubleSpinBox = QtWidgets.QDoubleSpinBox
    qSlider = QtWidgets.QSlider
    qFrame = QtWidgets.QFrame
    qRadioButton = QtWidgets.QRadioButton
    qScrollArea = QtWidgets.QScrollArea
    qButtonGroup = QtWidgets.QButtonGroup
    qCursor = QtGui.QCursor
    qProgressBar = QtWidgets.QProgressBar
    qDialog = QtWidgets.QDialog
    qSizePolicy = QtWidgets.QSizePolicy
    qMenu = QtWidgets.QMenu
    qApplication = QtWidgets.QApplication
    qDesktopWidget = QtWidgets.QDesktopWidget
    qToolTip = QtWidgets.QToolTip
    qListWidget = QtWidgets.QListWidget
    qListWidgetItem = QtWidgets.QListWidgetItem
    qAbstractItemView = QtWidgets.QAbstractItemView
    qPoint = QtCore.QPoint
    qValidator = QtGui.QValidator
    qComboBox = QtWidgets.QComboBox
    qDockWidget = QtWidgets.QDockWidget
    qTabWidget = QtWidgets.QTabWidget
    qTextEdit = QtWidgets.QTextEdit

if PySide or PySide2:
    PySides = True


# Instance handling
def wrap_instance(ptr, base):
    '''Return QtGui object instance based on pointer address
    '''
    if globals().has_key('sip'):
        return sip.wrapinstance(long(ptr), QtCore.QObject)
    elif globals().has_key('shiboken'):
        return shiboken.wrapInstance(long(ptr), base)


def unwrap_instance(qt_object):
    '''Return pointer address for qt class instance
    '''
    if globals().has_key('sip'):
        return long(sip.unwrapinstance(qt_object))
    elif globals().has_key('shiboken'):
        return long(shiboken.getCppPointer(qt_object)[0])


def get_maya_window():
    '''Get the maya main window as a QMainWindow instance
    '''
    try:
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        return wrap_instance(long(ptr), QtGui.QMainWindow)
    except:
        #    fails at import on maya launch since ui isn't up yet
        return None
