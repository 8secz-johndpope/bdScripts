import maya.cmds as cmds
#import pymel.core as pm


#TO IMPLEMENT
'''
def bdCreateIkTwist(side):
	driver = side + 'hand_bnd_jnt_00'
	twistLocators = cmds.ls(side + '_arm_ik_twist_loc_*')
	for l in twistLocators:
		print l
	#twistMd = cmds.createNode('multiplyDivide',name= multDivName)
	
'''

#order - fk chain root, ik chain root, bind chain
def bdConstrainChain(ik,fk,bind):
	ikChild = cmds.listRelatives(ik, c=True, typ = 'joint')
	fkChild = cmds.listRelatives(fk, c=True, typ = 'joint')
	bindChild = cmds.listRelatives(bind, c=True, typ = 'joint')

	cmds.parentConstraint(ik ,bind ,mo=True,weight=1)
	cmds.parentConstraint(fk ,bind ,mo=True,weight=1)

	if (ikChild != None) and (bindChild != None) and (fkChild != None):
		bdConstrainChain(ikChild,fkChild,bindChild)	

# Create an IKFK switch
def bdConnectSwitch(root,mdNode,revNode):
	parentCnstr = cmds.listRelatives(root,c=True, typ = 'parentConstraint')
	cRoot = cmds.listRelatives(root, c=True, typ = 'joint')
	
	#check for a parent constraint
	if parentCnstr != None:
		attr = cmds.listAttr(parentCnstr, v=True,ud=True)
		cmds.connectAttr(mdNode + '.outputX',(str(parentCnstr[0]) + "." + str(attr[0])),force=True)
		cmds.connectAttr(revNode + '.outputX',(str(parentCnstr[0]) + "." + str(attr[1])),force=True)
		#check for a child
		if cRoot != None:
			bdConnectSwitch(cRoot,mdNode,revNode)
		

def bdRecursiveIKFKSwitch(side,limb,controller):
	ctrlAnim = [controller]
	
	bdAddSeparatorAttr(ctrlAnim[0],'_Switch_')
	cmds.addAttr( ctrlAnim[0] ,ln="IKFK" ,at='long'  ,min=0 ,max=1 ,dv=0)
	cmds.setAttr((ctrlAnim[0] + "." + 'IKFK'),keyable=True)
	
	multDivName = side  + limb + 'ikfkSwitchMD'
	revName = side  + limb + 'switchRev'
	multDivNode = cmds.createNode('multiplyDivide',name= multDivName)
	revNode = cmds.createNode('reverse',name= revName )
	
	cmds.connectAttr((ctrlAnim[0] + '.IKFK'),multDivName + '.input1X',force=True)
	cmds.connectAttr( multDivName+ '.outputX',revName + '.inputX',force=True)
	
	startJoint = cmds.ls(side + limb + 'bnd_jnt_00')
	bdConnectSwitch(startJoint[0],multDivName,revName)



def bdAddAttribute(object, attrList,attrType ):
	for a in attrList:
		cmds.addAttr(object,ln=a,at = attrType)
		cmds.setAttr((object + "." + a),e=True, keyable=True)

def bdAddAttributeMinMax(object, attrList,attrType,minVal,maxVal,defVal ):
	for a in attrList:
		cmds.addAttr(object,ln=a,at = attrType,min = minVal,max=maxVal,dv=defVal)
		cmds.setAttr((object + "." + a),e=True, keyable=True)
		
def bdAddSeparatorAttr(object, attr):
	cmds.addAttr(object ,ln=attr,nn=attr,at='bool'  )
	cmds.setAttr((object + "." + attr),keyable = True)
	cmds.setAttr((object + "." + attr),lock = True)
	

def bdCreateGroup(objects,grpName,pivot,rot=False):
	grp = cmds.group(objects,n=grpName)
	footJntPos = cmds.xform(pivot,q=True,ws=True,t=True)
	cmds.move(footJntPos[0],footJntPos[1],footJntPos[2],grp + '.rp',grp + '.sp')
	return grp
	

def bdCleanUpController(object,attrList,lockFlag=True):
	for attr in attrList:
		cmds.setAttr(object + '.' + attr,lock=lockFlag,keyable=False,channelBox=False)

def bdCreateOffsetLoc(destination,name):
	loc = cmds.spaceLocator(n=name)
	cmds.parent(loc,destination)
	for axis in ['X','Y','Z']:
		cmds.setAttr(str(loc[0]) + '.translate' + axis,0)
		cmds.setAttr(str(loc[0]) + '.rotate' + axis,0)
	cmds.parent(loc,world=True)
	locGrp = cmds.duplicate(loc,name=str(loc[0] + "_grp"))
	cmds.parent(loc,locGrp)
	
def bdAddIk(start,end,ikType,ikName):
	cmds.ikHandle(sol= ikType,sticky='sticky', startJoint=start,endEffector = end,name = ikName)


def bdBuildBoxController(target,ctrlName,scale):
	defaultPointsList = [(1,-1,1),(1,-1,-1),(-1,-1,-1),(-1,-1,1),(1,1,1),(1,1,-1),(-1,1,-1),(-1,1,1)]
	pointsList = []
	for p in defaultPointsList:
		pointsList.append(( p[0] * scale, p[1] * scale , p[2] * scale ))
		
	knotsList = [i for i in range(16)]
	curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3], 
	                pointsList[7], pointsList[4], pointsList[5], pointsList[6],
	                pointsList[7], pointsList[3], pointsList[0], pointsList[4],
	                pointsList[5], pointsList[1], pointsList[2], pointsList[6] ]
	
	ctrl = cmds.curve(d=1, p = curvePoints , k = knotsList )
	ctrl = cmds.rename(ctrl,ctrlName)
	ctrlGrp = cmds.group(ctrl,n=ctrlName.replace("anim","anim_CON"))
        targetPos = cmds.xform(target,q=True,ws=True,t=True)
	cmds.move(targetPos[0],targetPos[1],targetPos[2],ctrlGrp)
	return [ctrl,ctrlGrp]


def bdBuildSphereController(target,ctrlName,scale):
	circleA = cmds.circle(n = ctrlName + 'A',nr=(0, 1, 0), c=(0, 0, 0),radius=scale )
	circleB = cmds.circle(n = ctrlName + 'B',nr=(1, 0, 0), c=(0, 0, 0), radius=scale  )
	circleBShape = cmds.listRelatives(circleB[0],c=True)
	circleC = cmds.circle(n = ctrlName + 'C',nr=(0, 0, 1), c=(0, 0, 0),radius=scale  )
	circleCShape = cmds.listRelatives(circleC[0],c=True)
	cmds.parent(circleBShape[0],circleA[0],r=True,s=True)
	cmds.parent(circleCShape[0],circleA[0],r=True,s=True)
	cmds.delete(circleB,circleC)
	ctrl = cmds.rename(circleA[0],ctrlName)
	ctrlGrp = cmds.group(ctrl,n=ctrlName.replace("anim","anim_CON"))	
	targetPos = cmds.xform(target,q=True,ws=True,t=True)
	targetRot = cmds.xform(target,q=True,ws=True,ro=True)
	cmds.move(targetPos[0],targetPos[1],targetPos[2],ctrlGrp)
	cmds.rotate(targetRot[0],targetRot[1],targetRot[2],ctrlGrp)
	
def bdAddDamp(attribute, axes ):
	selection = cmds.ls(sl=True)
	source  = selection[0]
	target = selection[1]
	
	multDivName = target.replace("jnt","MD")
	multDivNode = cmds.createNode('multiplyDivide',name= multDivName)
	for axis in axes:
		cmds.connectAttr((source + '.' + attribute + axis.upper()),multDivName + '.input1' + axis.upper(),force=True)
		cmds.connectAttr( multDivName+ '.output' + axis.upper() ,target + '.' + attribute + axis.upper(),force=True)	
	