import pymel.core as pm

def bdMirrorCapsule():
    sl = pm.ls(sl=1)
    capsule_shape = None
    for s in sl:
        if s.type() == 'physicsShape':
            capsule_shape = s

    if capsule_shape:
        capsule_transform = capsule_shape.getTransform()
        mirrored_name = getMirrorName(capsule_shape)

        find = pm.ls(mirrored_name)
        if find:
            mirrored_capsule_shape = find[0]
            mirrored_capsule_transform = mirrored_capsule_shape.getTransform()

            pos = mirrored_capsule_transform.getTranslation()
            rot = mirrored_capsule_transform.getRotation()
            height = mirrored_capsule_shape.attr('height').get()
            radius = mirrored_capsule_shape.attr('radius').get()

            capsule_transform.setTranslation(-1 * pos)#([pos[0] * -1, pos[1], pos[2] * -1])
            capsule_transform.setRotation(rot)
            capsule_shape.attr('height').set(height)
            capsule_shape.attr('radius').set(radius)


# splitting the name using _ in order t properly get the name of the mirrored shape
def getMirrorName(shape_name):
    short_name_mirror = ''

    tokens = [x for x in shape_name.split('_')]
    short_name = '_'.join(tokens[:2])

    if 'l_' in short_name:
        short_name_mirror = short_name.replace('l_', 'r_')
    elif 'r_' in short_name:
        short_name_mirror = short_name.replace('r_', 'l_')

    if len(tokens) == 2:
        return short_name_mirror
    else:
        return short_name_mirror  + '_' + '_'.join(tokens[2:])

