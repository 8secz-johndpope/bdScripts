import pymel.core as pm
import os


def createLocPoseReader(name):
    baseLoc = pm.spaceLocator(name=name + '_loc_base')
    poseLoc = pm.spaceLocator(name=name + '_loc_pose')
