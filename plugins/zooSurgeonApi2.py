import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
# from maya.OpenMayaUI import MProgressWindow
import maya.OpenMayaMPx as OpenMayaMpx
import sys
import math


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class ZooSurgeonCommand(om.MPxCommand):
    cmdName = "zooSurgeon"
    proxy_groups = ''
    proxies = []
    average_weights = []
    faces_weights = {}
    proxy_influence_pairs = {}
    ac_translate = {}
    ac_rotate = {}
    ac_scale = {}
    in_plug = om.MPlug()
    selection_iter = None
    selection_prev = None

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def creator():
        return ZooSurgeonCommand()

    def doIt(self,argList):
        self.selection_prev = om.MGlobal.getActiveSelectionList()
        self.redoIt()

    def redoIt(self):
        if self.selection_prev.length() > 0:
            self.selection_iter = om.MItSelectionList(self.selection_prev, om.MFn.kInvalid)
            while not self.selection_iter.isDone():
                dag_path = self.selection_iter.getDagPath()

                if dag_path.hasFn(om.MFn.kMesh):
                    mesh_fn = om.MFnMesh(dag_path)
                    skin_fn = self.get_skin_cluster(mesh_fn)
                    if skin_fn:
                        self.create_proxies(dag_path, mesh_fn, skin_fn)
                        # self.reset_attr()
                        # self.group_all_proxies()
                self.selection_iter.next()
        else:
            print 'Nothing selected !!!'

    def undoIt(self):
        print 'Undo Called'
        dg_mod = om.MDagModifier()
        print self.proxies
        if len(self.proxies) > 0:
            for p in self.proxies:
                dg_mod.commandToExecute('delete ' + p)
                dg_mod.doIt()
        om.MGlobal.setActiveSelectionList(self.selection_prev, om.MGlobal.kReplaceList)
        self.reset_attr()

    def isUndoable(self):
        return True

    def reset_attr(self):
        self.average_weights = []
        self.faces_weights = {}
        self.proxy_influence_pairs = {}
        self.ac_translate = {}
        self.ac_rotate = {}
        self.ac_scale = {}
        self.selection_prev = None
        self.selection_iter = None

    def create_proxies(self, node, mesh_fn, skin_fn):
        components = om.MFnSingleIndexedComponent()

        try:
            skin_influences = skin_fn.influenceObjects()
        except:
            sys.stderr.write('Object has no influences')
            return

        num_faces = mesh_fn.numPolygons
        self.proxies = []

        poly_iter = om.MItMeshPolygon(node)
        while not poly_iter.isDone():
            self.average_weights = [0] * len(skin_influences)
            face_verts = poly_iter.getVertices()
            vert_comp = components.create(om.MFn.kMeshVertComponent)
            components.addElements(face_verts)
            vert_iter = om.MItMeshVertex(node,vert_comp)
            while not vert_iter.isDone():
                weights, infIndex = skin_fn.getWeights(node, vert_iter.currentItem())
                self.average_face_weights(weights)
                vert_iter.next()
            self.set_face_weights(poly_iter.index(), self.average_weights, skin_influences)
            poly_iter.next(None)

        faces_list = [i for i in range(num_faces)]

        translation = om.MFloatVector(0,0,0)
        for inf, faces in self.faces_weights.iteritems():
            mesh_name = node.partialPathName()
            proxy_name = mesh_name.split('|')[-1] + '_' + inf + '_proxy'

            dg_mod = om.MDagModifier()
            dg_mod.commandToExecute('duplicate -n ' + proxy_name + ' ' + mesh_name)
            dg_mod.commandToExecute('parent -w ' + proxy_name)
            dg_mod.doIt()

            mesh_duplicate_dag = self.get_object_path(proxy_name)
            self.unlock_channels(mesh_duplicate_dag)
            mesh_duplicate_fn = om.MFnMesh(mesh_duplicate_dag)
            faces_to_delete = list(set(faces_list) - set(faces))

            if len(faces_to_delete) > 0:
                mesh_duplicate_fn.extractFaces(faces_to_delete,translation)
                mesh_duplicate_fn.collapseFaces(faces_to_delete)
                mesh_duplicate_fn.updateSurface()

            # self.set_proxy_pivot(mesh_duplicate_dag,inf)
            # self.proxy_influence_pairs[mesh_duplicate_dag] = self.get_object_path(inf)
            self.proxies.append(proxy_name)

        # self.animate_proxy()
        # self.create_proxy_group(node)
    
    def create_proxy_group(self,node):
        dg_mod = om.MDagModifier()
        proxies_str = ''
        for proxy in self.proxy_influence_pairs.keys():
            proxies_str = proxies_str + proxy.partialPathName() + ' '
        dg_mod.commandToExecute('group -w -n ' + node.partialPathName() + '_proxies_grp ' + proxies_str) 
        dg_mod.doIt()
        self.proxy_groups = self.proxy_groups + node.partialPathName() + '_proxies_grp '
    
    def group_all_proxies(self):
        rig_node = self.get_object_path('*RIG')
        proxy_group_name = ''

        if rig_node:
            proxy_group_name = rig_node.partialPathName()
        if proxy_group_name != '':
            proxy_group_name += '_proxies_grp'
        else:
            proxy_group_name = 'proxies_grp'
            
        dg_mod = om.MDagModifier()
        dg_mod.commandToExecute('group -w -n ' + proxy_group_name +' ' + self.proxy_groups) 
        dg_mod.doIt()
    
    def animate_proxy(self):
        start_time = oma.MAnimControl.minTime()
        end_time = oma.MAnimControl.maxTime()
        start_val = int(start_time.asUnits(om.MTime.kPALFrame))
        end_val = int(end_time.asUnits(om.MTime.kPALFrame))
        
        start_translation = {}
        self.create_proxy_ac()
        
        for i in range(start_val,end_val+1):
            current_time = om.MTime(i, om.MTime.kPALFrame)
            oma.MAnimControl.setCurrentTime(current_time)
            for proxy_dag, jntDag in self.proxy_influence_pairs.iteritems():
                if i == start_val:
                    start_translation[jntDag] = self.get_joint_value(jntDag, 't')
                    jnt_rotation = self.get_joint_value(jntDag, 'r')
                    jnt_scale = self.get_joint_value(jntDag, 's')
                    self.add_proxy_key(current_time,proxy_dag, om.MVector(0,0,0),jnt_rotation,jnt_scale)
                else:
                    jnt_translation = self.get_joint_value(jntDag, 't')
                    delta_translation = start_translation[jntDag] - jnt_translation
                    delta_translation = om.MVector(-1*delta_translation.x, -1*delta_translation.y, -1*delta_translation.z)
                    
                    jnt_rotation = self.get_joint_value(jntDag, 'r')
                    jnt_scale = self.get_joint_value(jntDag, 's')

                    self.add_proxy_key(current_time,proxy_dag, delta_translation, jnt_rotation, jnt_scale)

        oma.MAnimControl.setCurrentTime(start_time)        
                
    # def constrain_proxy(self):
    #     dg_mod = om.MDagModifier()
    #     for proxy_dag,jntDag in self.proxy_influence_pairs.iteritems():
    #         proxy_transform_fn = om.MFnTransform(proxy_dag)
    #         jntTransformFn = om.MFnTransform(jntDag)
    #
    #         dg_mod.commandToExecute('parentConstraint -mo ' + jntTransformFn.name() + ' '
    #                                           + proxy_transform_fn.name() )
    #         dg_mod.doIt()
    
    def add_proxy_key(self, time, proxy_dag, translate, rotate,scale):
        self.ac_translate[proxy_dag][0].addKeyframe(time, translate.x)
        self.ac_translate[proxy_dag][1].addKeyframe(time, translate.y)
        self.ac_translate[proxy_dag][2].addKeyframe(time, translate.z)

        self.ac_rotate[proxy_dag][0].addKeyframe(time, math.radians(rotate[0]))
        self.ac_rotate[proxy_dag][1].addKeyframe(time, math.radians(rotate[1]))
        self.ac_rotate[proxy_dag][2].addKeyframe(time, math.radians(rotate[2]))

        self.ac_scale[proxy_dag][0].addKeyframe(time, scale[0])
        self.ac_scale[proxy_dag][1].addKeyframe(time, scale[1])
        self.ac_scale[proxy_dag][2].addKeyframe(time, scale[2])
        
    def create_proxy_ac(self):
        for proxy_dag in self.proxy_influence_pairs.keys():
            proxy_dag_fn = om.MFnDagNode(proxy_dag)
            
            x_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'translateX')
            y_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'translateY')
            z_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'translateZ')

            self.ac_translate[proxy_dag] = [x_ac, y_ac, z_ac]
            
            x_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'rotateX')
            y_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'rotateY')
            z_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'rotateZ')
        
            self.ac_rotate[proxy_dag] = [x_ac,y_ac,z_ac]
            
            x_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'scaleX')
            y_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'scaleY')
            z_ac = self.create_ac(proxy_dag_fn,proxy_dag, 'scaleZ')
        
            self.ac_scale[proxy_dag] = [x_ac, y_ac, z_ac]
            
    def create_ac(self, dag_fn, dag, attribute):
        attr = dag_fn.attribute(attribute)
        anim_curve = oma.MFnAnimCurve()
        anim_curve.create(dag.transform(), attr, None)
        return anim_curve
        
    def unlock_channels(self, dag_mesh):
        dep_node = om.MFnDependencyNode(dag_mesh.node())
        dep_node.findPlug("translateX", False).isLocked = False
        dep_node.findPlug("translateY", False).isLocked = False
        dep_node.findPlug("translateZ", False).isLocked = False
        
        dep_node.findPlug("rotateX", False).isLocked = False
        dep_node.findPlug("rotateY", False).isLocked = False
        dep_node.findPlug("rotateZ", False).isLocked = False

        dep_node.findPlug("scaleX", False).isLocked = False
        dep_node.findPlug("scaleY", False).isLocked = False
        dep_node.findPlug("scaleZ", False).isLocked = False
        
    def set_proxy_pivot(self, proxy, jnt):
        proxy_transform_fn = om.MFnTransform(proxy)
        jnt_dag_path = self.get_object_path(jnt)
        jnt_pivot = self.get_joint_value(jnt_dag_path,'t')
        proxy_transform_fn.setRotatePivot(om.MPoint(jnt_pivot.x, jnt_pivot.y, jnt_pivot.z), om.MSpace.kWorld,1)
        proxy_transform_fn.setScalePivot(om.MPoint(jnt_pivot.x, jnt_pivot.y, jnt_pivot.z), om.MSpace.kWorld,1)
        
        proxy_points = self.get_proxy_points(proxy)
        proxy_uv = self.get_proxy_uv(proxy)
        
        jnt_scale = self.get_joint_value(jnt_dag_path, 's')
        
        # scaleDoubleArray = om.MScriptUtil()
        # scaleDoubleArray.createFromList( [jnt_scale[0], jnt_scale[1], jnt_scale[2]], 3 )
        # scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
        proxy_transform_fn.setScale(jnt_scale)
        
        jnt_rotation = self.get_joint_value(jnt_dag_path,'r')
        euler_rotation = om.MEulerRotation(math.radians(jnt_rotation[0]), math.radians(jnt_rotation[1]),
                                           math.radians(jnt_rotation[2]))
        proxy_transform_fn.setRotation(euler_rotation)
        self.set_proxy_points(proxy, proxy_points)
        self.set_proxy_uv(proxy, proxy_uv)
        
    def get_proxy_uv(self ,proxy):
        proxy_mesh_fn = om.MFnMesh(proxy)
        u = om.MFloatArray()
        v= om.MFloatArray()
        proxy_mesh_fn.getUVs(u,v)
        return [u,v]

    def set_proxy_uv(self, proxy, uvs):
        proxy_mesh_fn = om.MFnMesh(proxy)
        proxy_mesh_fn.setUVs(uvs[0],uvs[1])

    def get_proxy_points(self, proxy):
        proxy_mesh_fn = om.MFnMesh(proxy)
        all_points = proxy_mesh_fn.getPoints(om.MSpace.kWorld)
        return all_points
    
    def set_proxy_points(self, proxy, points):
        proxy_mesh_fn = om.MFnMesh(proxy)
        proxy_mesh_fn.setPoints(points, om.MSpace.kWorld)
        
    def get_joint_value(self,jntDag,val):
        jnt_dag_path = self.get_object_path(jntDag)
        jnt_matrix = jnt_dag_path.inclusiveMatrix()
        jnt_transform_matrix = om.MTransformationMatrix(jnt_matrix)
        if val == 't':
            jnt_translation = jnt_transform_matrix.getTranslation(om.MSpace.kWorld)
            return jnt_translation
        elif val == 'r':
            euler_rotation = jnt_transform_matrix.euler_rotation()
            jnt_rotation = [math.degrees(angle) for angle in (euler_rotation.x, euler_rotation.y, euler_rotation.z)]
            return jnt_rotation 
        elif val == 's':
            jnt_scale = jnt_transform_matrix.getScale(om.MSpace.kWorld)
            return jnt_scale
        
    def average_face_weights(self, weights):
        for i in range(len(self.average_weights)):
            self.average_weights[i] += weights[i] 
            
    def set_face_weights(self, polyIndex, weights, skin_influences):
        max_value = sorted(weights)[-1]
        index = list(weights).index(max_value)
        self.append_face_weights(polyIndex, skin_influences[index].partialPathName())
        
    def append_face_weights(self, polyIndex, infName):
        if self.faces_weights.has_key(infName):
            val = self.faces_weights[infName]
            val.append(polyIndex)
            self.faces_weights[infName] = val
        else:
            self.faces_weights[infName] = [polyIndex]
        
    def get_object_path(self,proxy_name):
        sel_list =  om.MSelectionList()
        try:
            sel_list.add(proxy_name)
        except:
            return None
        
        dag_path = sel_list.getDagPath(0)
        return dag_path
    
    def get_skin_cluster(self, mesh_fn):
        '''
        get a list of all the skin clusters in the file, iterate and see if the shapes connected match our selection
        '''
        print mesh_fn.fullPathName()
        self.in_plug = mesh_fn.findPlug('inMesh', False)
        print self.in_plug.name()
        connections = self.in_plug.connectedTo(True, False)
        for c in connections:
            obj = c.node()
            try:
                skin_cluster_fn = oma.MFnSkinCluster(obj)
                return skin_cluster_fn
            except:
                sys.stderr.write("No skin cluster found! ")
                return None

    
def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.registerCommand(ZooSurgeonCommand.cmdName, ZooSurgeonCommand.creator)
    except:
        sys.stderr.write("Failed to register command: " + ZooSurgeonCommand.cmdName)

def uninitializePlugin(mobject):
    plugin_fn = om.MFnPlugin(mobject)
    try:
        plugin_fn.deregisterCommand(ZooSurgeonCommand.cmdName)
    except:
        sys.stderr.write("Failed to un-register command: " + ZooSurgeonCommand.cmdName)