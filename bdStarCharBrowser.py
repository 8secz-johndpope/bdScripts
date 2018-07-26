import pymel.core as pm
import maya.cmds as cmds
import os
import re
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from functools import partial
import maya.OpenMayaUI as mui
import shiboken2

import utils.libWidgets as UI
reload(UI)


def getMayaWindow():
    pointer = mui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)

CharBrowserUIWin = 'CharBrowserUIWin'

class CharBrowserUI(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaWindow()):
        super(CharBrowserUI, self).__init__(parent)

        #
        self.repo_path = 'c:\\repo\\StarIsland_content\\'
        self.char_list = self.get_dirs(self.repo_path)
        self.back_folders_btn = []
        self.favorite_folders = []
        # UI members
        self.char_layout = UI.VertBox()
        self.back_folders_layout = UI.HorBox()
        self.back_folders_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.char_combo = QtWidgets.QComboBox()
        self.char_combo.setMinimumHeight(30)
        self.char_combo.setEditable(1)
        self.char_combo.lineEdit().setReadOnly(1)
        self.char_combo.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.action_btn_layout = QtWidgets.QHBoxLayout()
        self.set_project_btn = UI.ActionButton('Set Project')
        self.open_file_btn = UI.ActionButton('Open File')
        self.save_file_btn = UI.ActionButton('Save File')


        self.char_browser = QtWidgets.QListWidget()
        #
        self.setWindowTitle('Staramba Char Browser')
        self.setObjectName(CharBrowserUIWin)

        self.setupUI()
        self.resize(400, 500)

    def setupUI(self):
        central_widget = QtWidgets.QWidget()

        main_layout = UI.VertBox()
        main_box = UI.TitledBox(title='Browse')

        if len(self.char_list) > 0:
            self.char_combo.addItems(self.char_list)

        self.char_combo.activated[str].connect(self.char_combo_changed)

        separator = UI.Separator()

        char_browser_layout = UI.HorBox()
        self.char_browser.hide()
        self.char_browser.itemDoubleClicked.connect(self.char_browser_double_clicked)
        char_browser_layout.addWidget(self.char_browser)

        self.char_layout.addWidget(self.char_combo)
        # self.char_layout.addWidget(self.main_dir)
        self.char_layout.addWidget(separator)
        self.char_layout.addLayout(self.back_folders_layout)
        self.char_layout.addLayout(char_browser_layout)

        self.set_project_btn.clicked.connect(self.set_project_clicked)
        self.open_file_btn.clicked.connect(self.open_file_clicked)
        self.save_file_btn.clicked.connect(self.save_file_clicked)

        self.action_btn_layout.addWidget(self.set_project_btn)
        self.action_btn_layout.addWidget(self.open_file_btn)
        self.action_btn_layout.addWidget(self.save_file_btn)

        main_box.layout.addLayout(self.char_layout)
        main_box.layout.addLayout(self.action_btn_layout)
        main_layout.addWidget(main_box)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.char_combo_changed(self.char_combo.currentText())

    @staticmethod
    def get_dirs(path):
        dir_all = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        # filter based on name
        char_list = []
        for name in dir_all:
            match = re.search(r'^\d{2}', name)
            if match:
                char_list.append(name)

        return char_list


    @staticmethod
    def get_files(path):
        dirs = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
        return dirs + files

    def char_combo_changed(self, text):
        for b in self.back_folders_btn:
            b.deleteLater()
        self.back_folders_btn = []

        current_char = text
        current_path = os.path.join(self.repo_path, current_char)
        main_dirs = self.get_dirs(current_path)

        self.char_browser.show()
        self.char_browser.clear()

        for d in main_dirs:
            listItem = QtWidgets.QListWidgetItem()
            listItem.setForeground(QtGui.QColor('#4498bf'))
            listItem.setText(d)
            self.char_browser.addItem(listItem)

        # self.go_main_dir()

    def update_char_browser(self, path):
        all_files = self.get_files(path)
        self.char_browser.clear()

        for d in all_files:
            listItem = QtWidgets.QListWidgetItem()
            if os.path.isdir(os.path.join(path, d)):
                listItem.setForeground(QtGui.QColor('#4498bf'))
            listItem.setText(d)
            self.char_browser.addItem(listItem)


    def char_browser_double_clicked(self, item):
        path = self.build_clicked_item_path(item.text())
        if os.path.isdir(path):
            index = len(self.back_folders_btn)
            back_folder_btn = UI.ButtonBack(str(item.text()), index)
            self.back_folders_layout.addWidget(back_folder_btn)
            back_folder_btn.clicked.connect(self.back_btn_clicked)
            self.back_folders_btn.append(back_folder_btn)
            self.update_char_browser(path)
        else:
            self.open_maya_file(path)

    def back_btn_clicked(self):
        btn_index = self.sender().index

        if btn_index == 0:
            for b in self.back_folders_btn:
                b.deleteLater()
                self.char_combo_changed(self.char_combo.currentText())
            self.back_folders_btn = []
        else:
            for b in self.back_folders_btn[btn_index+1:]:
                b.deleteLater()
                self.back_folders_btn.remove(b)

            path = self.build_clicked_item_path('')
            self.update_char_browser(path)

    def build_clicked_item_path(self, text):
        char_name = self.char_combo.currentText()
        char_subpath = ''
        path = ''
        for b in self.back_folders_btn:
            char_subpath = os.path.join(char_subpath, b.text())
        if text == '':
            path = os.path.join(self.repo_path, char_name, char_subpath)
        else:
            path = os.path.join(self.repo_path, char_name, char_subpath, text)
        return path

    def go_main_dir(self):
        char_dir = os.path.join(self.repo_path, self.char_combo.currentText())
        rig_dir = ''

        files_all  = self.get_files(char_dir)
        for d in files_all:
            if self.favorite_folders in d:
                rig_dir = d
                break

        item = QtWidgets.QListWidgetItem(rig_dir)
        self.char_browser_double_clicked(item)

        path = os.path.join(self.repo_path, self.char_combo.currentText(), rig_dir, '02_Wip')
        item = QtWidgets.QListWidgetItem('02_Wip')
        self.char_browser_double_clicked(item)

    def set_project_clicked(self):
        char_name = self.char_combo.currentText()
        currentPath = self.repo_path
        subPath = ''
        for b in self.back_folders_btn:
            print b
            subPath = os.path.join(subPath,b.text())
        print subPath
        currentPath = os.path.join(currentPath, char_name, subPath)

        pm.workspace(currentPath, openWorkspace = 1)

    def open_maya_file(self, path):
        path = path.replace('\\','/')

        saveDlg = SaveChangesDlg()
        # saveDlg.setFixedSize(800,  300)
        result = saveDlg.exec_()
        if result == 1:
            pm.saveFile()
            pm.openFile(path)
        elif result == 2:
            pm.openFile(path, f=1)

    def open_file_clicked(self):
        fileName = self.char_browser.currentItem().text()
        path = self.build_clicked_item_path(fileName)
        if os.path.isfile(path):
            extension = os.path.splitext(path)[1]
            print extension
            if  extension in ['.ma', '.mb']:
                self.open_maya_file(path)

    def save_file_clicked(self):
        pass

class SaveChangesDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SaveChangesDlg, self).__init__(parent)
        main_layout = QtWidgets.QVBoxLayout()

        self.save = 0

        labelLayout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel('Save changes to current file ?')
        labelLayout.addWidget(label)

        btnLayout = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No,
                                           QtCore.Qt.Horizontal, self)
        btnLayout.accepted.connect(self.accept)
        btnLayout.button(QtWidgets.QDialogButtonBox.No).clicked.connect(self.discarded)
        main_layout.addLayout(labelLayout)
        main_layout.addWidget(btnLayout)

        self.setLayout(main_layout)
        self.setWindowTitle('Save changes')

    def discarded(self):
        self.done(2)


def openTool():
    if pm.window(CharBrowserUIWin, exists=1):
        pm.deleteUI(CharBrowserUIWin)

    tool = CharBrowserUI()
    tool.show()
