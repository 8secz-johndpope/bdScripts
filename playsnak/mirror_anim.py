import pymel.core as pm
import math

class MirrorAnim:
    def __init__(self, name='', side=[]):
        self.name = name
        self.ctrl = None
        self.anim_crv = []
        self.mirror_anim_crv = []
        self.mirrored_ctrl = None
        self.side = side
        self.set_ctrl()


    def set_ctrl(self):
        find = pm.ls(self.name)
        if find:
            self.ctrl = find[0]
        else:
            pm.error('Could not set the controller')

        if self.side[0] in self.name:
            find = pm.ls(self.name.replace(self.side[0], self.side[1]))
            if find:
                self.mirrored_ctrl = find[0]
                print('Found mirrored controller for {} -> {}'.format(self.ctrl, self.mirrored_ctrl))

    def get_anim_crv(self):
        if not self.mirrored_ctrl:
            anim_crv = pm.listConnections(self.ctrl.name() + '.rotateY', t='animCurve')
            if len(anim_crv):
                self.anim_crv.append(anim_crv[0])

            anim_crv = pm.listConnections(self.ctrl.name() + '.rotateZ', t='animCurve')
            if len(anim_crv):
                self.anim_crv.append(anim_crv[0])

            anim_crv = pm.listConnections(self.ctrl.name() + '.translateX', t='animCurve')
            if len(anim_crv):
                self.anim_crv.append(anim_crv[0])
        else:
            self.anim_crv = pm.listConnections(self.ctrl, t='animCurve')
            self.mirror_anim_crv = pm.listConnections(self.mirrored_ctrl, t='animCurve')
            # for channel in ['translate', 'rotate']:
            #     for axis in ['X', 'Y', 'Z']:
            #         anim_crv = pm.listConnections(self.ctrl.name() + '.' + channel + axis, t='animCurve')
            #         if len(anim_crv):
            #             self.anim_crv.append(anim_crv[0])
            #
            #         anim_crv = pm.listConnections(self.mirrored_ctrl.name() + '.' + channel + axis, t='animCurve')
            #         if len(anim_crv):
            #             self.mirror_anim_crv.append(anim_crv[0])

    def print_anim_crv(self):
        for crv in self.anim_crv:
            print crv

    def mirror_anim(self, swap=0):
        self.get_anim_crv()
        if len(self.anim_crv):
            if not self.mirrored_ctrl:
                for crv in self.anim_crv:
                    self.mirror_crv(crv)
            else:
                if swap:
                    self.swap_anim()
                else:
                    self.mirror_ctrl_anim()

    def mirror_crv(self, crv):
        num_keys = crv.numKeys()
        start_key_val = crv.getValue(0)
        for i in range(1, num_keys):
            key_val = crv.getValue(i)
            delta = key_val - start_key_val
            new_val = start_key_val - delta

            crv.setValue(i, new_val)

    def mirror_ctrl_anim(self):
        first_key_val = {}
        # First we disconnect the controllers from the anim curves
        for ctrl in [self.ctrl, self.mirrored_ctrl]:
            attributes = pm.listConnections(ctrl, c=True, type='animCurve') or []
            for pair in attributes:
                # if 'translate' in pair[0].name() or 'rotate' in pair[0].name():
                first_key_val[pair[1].name()] = pair[1].getValue(0)
                pm.disconnectAttr(pair[1].name() + '.output', pair[0].name())

        # We connect the source ctrl to the mirrored animcurves and offset them so there is the same start value as
        # the original
        for crv in self.mirror_anim_crv:
            val1 = first_key_val[crv.name()]
            val2 = first_key_val[crv.name().replace(self.side[1], self.side[0])]
            offset = val1 - val2

            if 'translateX' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.translateX')
            if 'translateY' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.translateY')
            if 'translateZ' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.translateZ')
            if 'rotateX' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.rotateX')
            if 'rotateY' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.rotateY')
            if 'rotateZ' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.rotateZ')
            MirrorAnim.offset_crv(crv, -1 * offset)

        # We connect the mirror ctrl to the source animcurves and offset them so there is the same start value as
        # the original
        for crv in self.anim_crv:
            val1 = first_key_val[crv.name()]
            val2 = first_key_val[crv.name().replace(self.side[0], self.side[1])]
            offset = val1 - val2

            if 'translateX' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.translateX')
            if 'translateY' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.translateY')
            if 'translateZ' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.translateZ')
            if 'rotateX' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.rotateX')
            if 'rotateY' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.rotateY')
            if 'rotateZ' in crv.name():
                pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.rotateZ')

            MirrorAnim.offset_crv(crv, -1 * offset)

        for crv in self.mirror_anim_crv:
            if 'translateZ' in crv.name():
                self.mirror_crv(crv)
            elif 'rotateX' in crv.name():
                self.mirror_crv(crv)
            elif 'rotateY' in crv.name():
                self.mirror_crv(crv)

        for crv in self.anim_crv:
            if 'translateZ' in crv.name():
                self.mirror_crv(crv)
            elif 'rotateX' in crv.name():
                self.mirror_crv(crv)
            elif 'rotateY' in crv.name():
                self.mirror_crv(crv)


    def swap_anim(self):
        # First we disconnect the controllers from the anim curves
        for ctrl in [self.ctrl, self.mirrored_ctrl]:
            attributes = pm.listConnections(ctrl, c=True, type='animCurve') or []
            for pair in attributes:
                # if 'translate' in pair[0].name() or 'rotate' in pair[0].name():
                pm.disconnectAttr(pair[1].name() + '.output', pair[0].name())

        # We connect the source ctrl to the mirrored animcurves and offset them so there is the same start value as
        # the original
        for crv in self.mirror_anim_crv:
            attr_con = '.' + crv.name().split('_')[-1]
            pm.connectAttr(crv.name() + '.output', self.ctrl.name() + attr_con)
            # if 'translateX' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.translateX')
            # if 'translateY' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.translateY')
            # if 'translateZ' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.translateZ')
            # if 'rotateX' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.rotateX')
            # if 'rotateY' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.rotateY')
            # if 'rotateZ' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.ctrl.name() + '.rotateZ')

        # We connect the mirror ctrl to the source animcurves and offset them so there is the same start value as
        # the original
        for crv in self.anim_crv:
            attr_con = '.' + crv.name().split('_')[-1]
            pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + attr_con)

            # if 'translateX' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.translateX')
            # if 'translateY' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.translateY')
            # if 'translateZ' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.translateZ')
            # if 'rotateX' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.rotateX')
            # if 'rotateY' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.rotateY')
            # if 'rotateZ' in crv.name():
            #     pm.connectAttr(crv.name() + '.output', self.mirrored_ctrl.name() + '.rotateZ')


    @staticmethod
    def offset_crv(crv, offset):
        num_keys = crv.numKeys()
        for i in range(num_keys):
            val = crv.getValue(i)
            crv.setValue(i, val + offset)
