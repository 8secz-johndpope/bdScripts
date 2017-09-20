import pymel.core as pm
import pymel.core.datatypes as dt
import re, os, shutil, glob, sys, inspect

import logging

# import shiboken
import sip
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

import maya.OpenMayaUI

from .. import ui_utils as utils

reload(utils)

from ...system import characterX as character

reload(character)


class CharacterWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CharacterWidget, self).__init__(parent)
        # -------------------- CharX related ------------------#
        self.currentCharacterName = ''
        self.charactersList = []
        self.currentCharacter = None
        # ---------------------- UI related --------------------#
        self.charSettingsVisible = 0
        self.charSettingsWidget = None
        self.characterGroup = None
        self.settings_size_anim = None
        self.charGroup_size_anim = None

        self.setupUi()

    def setupUi(self):
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.box = utils.TitledBox(title='Character', settings=1)

        nameLayout = QtGui.QHBoxLayout()
        nameLabel = QtGui.QLabel('Character name')
        nameLabel.setMaximumWidth(80)
        self.charNameCombo = QtGui.QComboBox()
        self.charNameCombo.setEditable(1)
        nameBtn = QtGui.QPushButton('Create character')

        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.charNameCombo)

        self.characterSettingWidget = QtGui.QWidget()
        self.characterSettingWidget.setContentsMargins(0, 0, 0, 0)
        self.characterSettingWidget.setFixedHeight(0)

        self.box.groupBoxLayout.addWidget(self.characterSettingWidget)
        self.box.groupBoxLayout.addLayout(nameLayout)
        self.box.groupBoxLayout.addWidget(nameBtn)

        mainLayout.addWidget(self.box)
        self.settingsBtn = self.box.settingsBtn
        self.settingsBtn.clicked.connect(self.toggleCharSettingsUi)

        self.setLayout(mainLayout)

        nameBtn.clicked.connect(self.createCharacter)

    def toggleCharSettingsUi(self):
        if not self.charSettingsVisible:
            self.charSettingsVisible = 1
            self.settingsBtn.setText('-')
            self.addCharSettingsUi()
            '''
            self.settings_size_anim= utils.uiAddWidgetSizeAnim(self.characterSettingWidget,1,20)
            self.settings_size_anim.valueChanged.connect(self.forceResize)
            self.settings_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
            
            
            self.charGroup_size_anim= utils.uiAddWidgetSizeAnim(self.characterGroup,1,20,60)
            self.charGroup_size_anim.valueChanged.connect(self.charGroupForceResize)
            self.charGroup_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
            #self.characterGroup.setFixedHeight(80)
            '''
        else:
            self.charSettingsVisible = 0
            self.settingsBtn.setText('+')
            # ----------------- PyQt4
            self.characterSettingWidget.setFixedHeight(0)
            self.box.groupBox.setFixedHeight(80)
            ''' PySide
            self.settings_size_anim = utils.uiAddWidgetSizeAnim(self.characterSettingWidget,0,20)
            self.settings_size_anim.valueChanged.connect(self.forceResize)
            self.settings_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
            
            self.charGroup_size_anim= utils.uiAddWidgetSizeAnim(self.characterGroup,0,20,60)
            self.charGroup_size_anim.valueChanged.connect(self.charGroupForceResize)
            self.charGroup_size_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)            
            '''

    def addCharSettingsUi(self):
        charSettingsLayout = QtGui.QVBoxLayout()
        charSettingsLayout.setContentsMargins(0, 0, 0, 0)
        charSidesStrings = QtGui.QLineEdit('Left,Right')
        charSettingsLayout.addWidget(charSidesStrings)
        self.characterSettingWidget.setLayout(charSettingsLayout)
        # PyQt4
        self.characterSettingWidget.setFixedHeight(30)
        self.box.groupBox.setFixedHeight(105)

    def forceResize(self, new_height):
        self.characterSettingWidget.setFixedHeight(new_height.height())

    def charGroupForceResize(self, new_height):
        self.characterGroup.setFixedHeight(new_height.height())

    def createCharacter(self):
        yartWindow = self.parent().parent()
        self.currentCharacterName = self.charNameCombo.currentText()
        if self.currentCharacterName:
            if self.currentCharacterName not in self.charactersList:
                self.charNameCombo.addItem(self.currentCharacterName)
                self.charactersList.append(self.currentCharacterName)
                self.currentCharacter = character.CharacterX(name=self.currentCharacterName)
                self.currentCharacter.createCharacterX()
                yartWindow.modulesTreeWidget.setRoot(self.currentCharacter.characterRootModule.name)
            else:
                pm.warning('A character with %s name exists already' % self.currentCharacterName)
        else:
            pm.warning('You need a name, don\'t you ?')
