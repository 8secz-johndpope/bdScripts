import random
import pymel.core as pm


def animateSpikes():
    spikes = pm.ls('ice_spike_*', type='transform')
    bursts = pm.ls('burst_out_*', type='transform')

    print bursts
    indexes = [i for i in range(len(spikes))]
    print indexes
    random.shuffle(indexes)

    timeOffset = 0
    for i in indexes:
        pm.currentTime(timeOffset)
        pm.setKeyframe(spikes[i].name() + '.ty', v=0)
        print bursts[i]
        setParticlesAttr(bursts[i], timeOffset + 4)
        pm.currentTime(timeOffset + 2)
        pm.setKeyframe(spikes[i].name() + '.ty', v=random.uniform(1.3, 1.7))
        pm.currentTime(timeOffset + 3)
        y = spikes[i].ty.get()
        pm.setKeyframe(spikes[i].ty, v=y - 0.1)
        timeOffset += 2
        if timeOffset == 12:
            timeOffset = 2


def setParticlesAttr(emitterGroup, val):
    emitters = pm.listRelatives(emitterGroup, c=1, type='transform')
    for e in emitters:
        particleMaterial = None
        shape = e.getShape()
        shapeShadeGrp = pm.listConnections(shape, type='shadingEngine')[0]
        shapeShader = pm.listConnections('%s.surfaceShader' % shapeShadeGrp)[0]

        attrs = pm.listAttr(e, ud=1)
        pm.select(e)
        if 'ParticleStartDelay' not in attrs:
            melCmd = 'rlScriptEdit_animShaderParam ParticleStartDelay ' + shapeShader + '.rlParticleStartDelay ' + shapeShader + ' 0'
            pm.mel.eval(melCmd)

        if 'ParticleStartVelocityRandomize' not in attrs:
            melCmd = 'rlScriptEdit_animShaderParam ParticleStartVelocityRandomize ' + shapeShader + '.rlParticleStartVelocityRandomize ' + shapeShader + ' 0'
            pm.mel.eval(melCmd)
            print e, 'ParticleStartVelocityRandomize'

        if 'ParticleSizeRandomize' not in attrs:
            melCmd = 'rlScriptEdit_animShaderParam ParticleSizeRandomize ' + shapeShader + '.rlParticleSizeRandomize ' + shapeShader + ' 0'
            pm.mel.eval(melCmd)
            print e, 'ParticleSizeRandomize'

        pm.setAttr(e + '.ParticleStartDelay', val / 25.0)
        pm.setAttr(e + '.ParticleStartVelocityRandomize', random.uniform(0, 1))
        pm.setAttr(e + '.ParticleSizeRandomize', random.uniform(0, 1))
