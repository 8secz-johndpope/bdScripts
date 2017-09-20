import pymel.core as pm
import os, shutil, platform
import maya.OpenMaya as OpenMaya
import logging

hkIkDict = {"Reference": 0, "Hips": 1, "LeftUpLeg": 2, "LeftLeg": 3, "LeftFoot": 4, "RightUpLeg": 5, "RightLeg": 6,
            "RightFoot": 7, "Spine": 8, "LeftArm": 9, "LeftForeArm": 10, "LeftHand": 11, "RightArm": 12,
            "RightForeArm": 13, "RightHand": 14, "Head": 15, "LeftToeBase": 16, "RightToeBase": 17, "LeftShoulder": 18,
            "RightShoulder": 19, "Neck": 20, "LeftFingerBase": 21, "RightFingerBase": 22, "Spine1": 23, "Spine2": 24,
            "Spine3": 25, "Spine4": 26, "Spine5": 27, "Spine6": 28, "Spine7": 29, "Spine8": 30, "Spine9": 31,
            "Neck1": 32, "Neck2": 33, "Neck3": 34, "Neck4": 35, "Neck5": 36, "Neck6": 37, "Neck7": 38, "Neck8": 39,
            "Neck9": 40, "LeftUpLegRoll": 41, "LeftLegRoll": 42, "RightUpLegRoll": 43, "RightLegRoll": 44,
            "LeftArmRoll": 45, "LeftForeArmRoll": 46, "RightArmRoll": 47, "RightForeArmRoll": 48, "HipsTranslation": 49,
            "LeftHandThumb1": 50, "LeftHandThumb2": 51, "LeftHandThumb3": 52, "LeftHandThumb4": 53,
            "LeftHandIndex1": 54, "LeftHandIndex2": 55, "LeftHandIndex3": 56, "LeftHandIndex4": 57,
            "LeftHandMiddle1": 58, "LeftHandMiddle2": 59, "LeftHandMiddle3": 60, "LeftHandMiddle4": 61,
            "LeftHandRing1": 62, "LeftHandRing2": 63, "LeftHandRing3": 64, "LeftHandRing4": 65, "LeftHandPinky1": 66,
            "LeftHandPinky2": 67, "LeftHandPinky3": 68, "LeftHandPinky4": 69, "LeftHandExtraFinger1": 70,
            "LeftHandExtraFinger2": 71, "LeftHandExtraFinger3": 72, "LeftHandExtraFinger4": 73, "RightHandThumb1": 74,
            "RightHandThumb2": 75, "RightHandThumb3": 76, "RightHandThumb4": 77, "RightHandIndex1": 78,
            "RightHandIndex2": 79, "RightHandIndex3": 80, "RightHandIndex4": 81, "RightHandMiddle1": 82,
            "RightHandMiddle2": 83, "RightHandMiddle3": 84, "RightHandMiddle4": 85, "RightHandRing1": 86,
            "RightHandRing2": 87, "RightHandRing3": 88, "RightHandRing4": 89, "RightHandPinky1": 90,
            "RightHandPinky2": 91, "RightHandPinky3": 92, "RightHandPinky4": 93, "RightHandExtraFinger1": 94,
            "RightHandExtraFinger2": 95, "RightHandExtraFinger3": 96, "RightHandExtraFinger4": 97, "LeftFootThumb1": 98,
            "LeftFootThumb2": 99, "LeftFootThumb3": 100, "LeftFootThumb4": 101, "LeftFootIndex1": 102,
            "LeftFootIndex2": 103, "LeftFootIndex3": 104, "LeftFootIndex4": 105, "LeftFootMiddle1": 106,
            "LeftFootMiddle2": 107, "LeftFootMiddle3": 108, "LeftFootMiddle4": 109, "LeftFootRing1": 110,
            "LeftFootRing2": 111, "LeftFootRing3": 112, "LeftFootRing4": 113, "LeftFootPinky1": 114,
            "LeftFootPinky2": 115, "LeftFootPinky3": 116, "LeftFootPinky4": 117, "LeftFootExtraFinger1": 118,
            "LeftFootExtraFinger2": 119, "LeftFootExtraFinger3": 120, "LeftFootExtraFinger4": 121,
            "RightFootThumb1": 122, "RightFootThumb2": 123, "RightFootThumb3": 124, "RightFootThumb4": 125,
            "RightFootIndex1": 126, "RightFootIndex2": 127, "RightFootIndex3": 128, "RightFootIndex4": 129,
            "RightFootMiddle1": 130, "RightFootMiddle2": 131, "RightFootMiddle3": 132, "RightFootMiddle4": 133,
            "RightFootRing1": 134, "RightFootRing2": 135, "RightFootRing3": 136, "RightFootRing4": 137,
            "RightFootPinky1": 138, "RightFootPinky2": 139, "RightFootPinky3": 140, "RightFootPinky4": 141,
            "RightFootExtraFinger1": 142, "RightFootExtraFinger2": 143, "RightFootExtraFinger3": 144,
            "RightFootExtraFinger4": 145, "LeftInHandThumb": 146, "LeftInHandIndex": 147, "LeftInHandMiddle": 148,
            "LeftInHandRing": 149, "LeftInHandPinky": 150, "LeftInHandExtraFinger": 151, "RightInHandThumb": 152,
            "RightInHandIndex": 153, "RightInHandMiddle": 154, "RightInHandRing": 155, "RightInHandPinky": 156,
            "RightInHandExtraFinger": 157, "LeftInFootThumb": 158, "LeftInFootIndex": 159, "LeftInFootMiddle": 160,
            "LeftInFootRing": 161, "LeftInFootPinky": 162, "LeftInFootExtraFinger": 163, "RightInFootThumb": 164,
            "RightInFootIndex": 165, "RightInFootMiddle": 166, "RightInFootRing": 167, "RightInFootPinky": 168,
            "RightInFootExtraFinger": 169, "LeftShoulderExtra": 170, "RightShoulderExtra": 171}


def bdExportHIKAnim(fromFolder, toFolder, charName, charType):
    animFiles = [f for f in os.listdir(fromFolder) if (f.endswith('.ma') or f.endswith('.mb'))]
    for anim in animFiles:
        animFile = os.path.join(fromFolder, anim)
        pm.openFile(animFile, f=1)
        start = pm.playbackOptions(q=1, min=1)
        end = pm.playbackOptions(q=1, max=1)
