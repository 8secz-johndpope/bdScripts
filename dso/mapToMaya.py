import os
import xml.etree.ElementTree
import pymel.core as pm

mapPath = "d:\\drasa_online\\work\\maps\\g0008_altar_01_boss.lef"
gfxLib = "d:\\drasa_online\\work\\gfxlib\\"


def createMap():
    root = xml.etree.ElementTree.parse(mapPath).getroot()
    i = 0

    data = []
    for levelNode in root.iter('LevelNode'):
        info = []
        for levelNodeAttr in levelNode:
            if levelNodeAttr.get('name') == 'resource':
                info.append(levelNodeAttr.get('value'))
            if levelNodeAttr.get('name') == 'position':
                info.append(levelNodeAttr.get('value'))
            if levelNodeAttr.get('name') == 'scale':
                info.append(levelNodeAttr.get('value'))
            if levelNodeAttr.get('name') == 'rotation':
                info.append(levelNodeAttr.get('value'))
            if levelNodeAttr.get('name') == 'name':
                info.append(levelNodeAttr.get('value'))
            if levelNodeAttr.get('name') == 'class':
                info.append(levelNodeAttr.get('value'))

        data.append(info)

    i = 0
    for d in data:
        if len(d) == 6:
            if d[0] == 'EnvNode':
                mayaFile = os.path.abspath(os.path.join(gfxLib + d[1] + '.mb'))

                if os.path.isfile(mayaFile):
                    ns = d[2].replace('.', '_') + '_' + str(i)
                    pos = [float(n) * 100 for n in d[3].split(' ')[:-1]]
                    scale = [float(n) for n in d[4].split(' ')[:-1]]
                    rotation = [float(n) for n in d[5].split(' ')[:-1]]

                    i += 1
                    try:
                        pm.importFile(mayaFile, namespace=ns)
                        pm.move(ns + ':model', pos)
                        pm.rotate(ns + ':model', rotation)
                        pm.scale(ns + ':model', scale)
                        i += 1
                    except:
                        pm.error('Importing file %s' % mayaFile)
