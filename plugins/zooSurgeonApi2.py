import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import sys
import math
# from maya.OpenMayaUI import MProgressWindow


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class ZooSurgeonCommand(om.MPxCommand):
    """Command that breaks selected skinned poly meshes in non-skinned meshes based on the skin influences

    If the character has animations, all the proxies will be animated based on each influence (joint) animation.
    
    Attributes:
        cmd_name (str): The name of the command , to be called using cmds / pymel or MEL
        proxy_groups (str): a long string holding the names of all the proxy groups
        proxies (list): list holding all the proxy names
        average_weights (list): list holding a sum of all the face vertices weights, used to get the max influence value
        faces_weights (dict): keys are the name of influences, values are list of faces indexes
        proxy_influence_pairs (dict): keys are proxy names, values are the influence to whom they belong
        ac_translate = {}
        ac_rotate = {}
        ac_scale = {}
        in_plug = om.MPlug()
        selection_iter = None
        selection_prev = None
       """
    cmd_name = "zooSurgeon"
    proxy_group_name = ''
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

    def doIt(self, argList):
        """ Initializes the selection_prev with the current selection to be used for the undo"""
        self.selection_prev = om.MGlobal.getActiveSelectionList()
        self.redoIt()

    def redoIt(self):
        """Implements the command zooSurgeon"""
        if self.selection_prev.length() > 0:
            self.selection_iter = om.MItSelectionList(self.selection_prev, om.MFn.kInvalid)
            while not self.selection_iter.isDone():
                dag_path = self.selection_iter.getDagPath()
                if dag_path.hasFn(om.MFn.kMesh):
                    mesh_fn = om.MFnMesh(dag_path)
                    skin_fn = self.get_skin_cluster(mesh_fn)
                    if skin_fn:
                        current_time = om.MTime(0, om.MTime.kPALFrame)
                        oma.MAnimControl.setCurrentTime(current_time)
                        self.create_proxies(dag_path, mesh_fn, skin_fn)
                        self.reset_attr()
                self.selection_iter.next()
            self.group_all_proxies()
        else:
            print 'Nothing selected !!!'

    def undoIt(self):
        dg_mod = om.MDagModifier()
        if self.proxy_group_name != '':
            dg_mod.commandToExecute('delete ' + self.proxy_group_name)
            dg_mod.doIt()
        om.MGlobal.setActiveSelectionList(self.selection_prev, om.MGlobal.kReplaceList)
        # self.reset_attr()

    def isUndoable(self):
        return True

    def reset_attr(self):
        self.average_weights = []
        self.faces_weights = {}
        self.proxy_influence_pairs = {}
        self.ac_translate = {}
        self.ac_rotate = {}
        self.ac_scale = {}
        self.proxies = []
        # self.selection_prev = None
        # self.selection_iter = None

    def create_proxies(self, node, mesh_fn, skin_fn):
        components = om.MFnSingleIndexedComponent()
        try:
            skin_influences = skin_fn.influenceObjects()
        except:
            sys.stderr.write('Object has no influences')
            return

        self.reset_attr()
        num_faces = mesh_fn.numPolygons

        poly_iter = om.MItMeshPolygon(node)
        # iterates through all the selected mesh faces
        while not poly_iter.isDone():
            # initialize average_weights as a zero list with the length of number of influences
            self.average_weights = [0] * len(skin_influences)
            face_verts = poly_iter.getVertices()
            vert_comp = components.create(om.MFn.kMeshVertComponent)
            components.addElements(face_verts)
            vert_iter = om.MItMeshVertex(node, vert_comp)
            # iterates through all the face vertices, computes the max influence per face
            while not vert_iter.isDone():
                weights, inf_index = skin_fn.getWeights(node, vert_iter.currentItem())
                self.average_face_weights(weights)
                vert_iter.next()
            self.set_face_weights(poly_iter.index(), self.average_weights, skin_influences)
            poly_iter.next(None)

        # list holding the num faces, will be used to get the faces that need to be deleted
        faces_list = [i for i in range(num_faces)]

        for inf, faces in self.faces_weights.iteritems():
            mesh_name = node.partialPathName()
            proxy_name = mesh_name.split('|')[-1] + '_' + inf + '_proxy'

            dg_mod = om.MDagModifier()
            dg_mod.commandToExecute('duplicate -n ' + proxy_name + ' ' + mesh_name)
            dg_mod.commandToExecute('parent -w ' + proxy_name)
            dg_mod.doIt()

            # duplicates the skinned mesh, named as above
            mesh_duplicate_dag = self.get_object_path(proxy_name)
            self.unlock_channels(mesh_duplicate_dag)
            mesh_duplicate_fn = om.MFnMesh(mesh_duplicate_dag)
            # faces is read from the self.faces_weights attribute, holds the indexes of the faces that will be kept
            faces_to_delete = list(set(faces_list) - set(faces))

            if len(faces_to_delete) > 0:
                mesh_duplicate_fn.extractFaces(faces_to_delete)
                mesh_duplicate_fn.collapseFaces(faces_to_delete)
                mesh_duplicate_fn.updateSurface()

            # sets the proxy pivot based on the joint position / rotation
            self.set_proxy_pivot(mesh_duplicate_dag, inf)
            self.proxy_influence_pairs[mesh_duplicate_dag.partialPathName()] = self.get_object_path(inf)
            self.proxies.append(proxy_name)

        self.animate_proxy()
        self.create_proxy_group(node)
    
    def create_proxy_group(self, node):
        dg_mod = om.MDagModifier()
        # build a string containing all the proxy names to be used for grouping
        proxies_str = ''
        for proxy in self.proxy_influence_pairs.keys():
            proxies_str = proxies_str + proxy + ' '
        dg_mod.commandToExecute('group -w -n ' + node.partialPathName() + '_proxies_grp ' + proxies_str) 
        dg_mod.doIt()
        self.proxy_groups = self.proxy_groups + node.partialPathName() + '_proxies_grp '

    def group_all_proxies(self):
        self.proxy_group_name = 'proxies_grp'
        try:
            om.MGlobal.getSelectionListByName(self.proxy_group_name)

            dg_mod = om.MDagModifier()
            dg_mod.commandToExecute('parent ' + self.proxy_groups + ' ' + self.proxy_group_name)
            dg_mod.doIt()
        except:
            dg_mod = om.MDagModifier()
            dg_mod.commandToExecute('group -w -n ' + self.proxy_group_name + ' ' + self.proxy_groups)
            dg_mod.doIt()


    def animate_proxy(self):
        """Animates each proxy based on the influence animation
        """
        start_time = oma.MAnimControl.minTime()
        end_time = oma.MAnimControl.maxTime()
        start_val = int(start_time.asUnits(om.MTime.kPALFrame))
        end_val = int(end_time.asUnits(om.MTime.kPALFrame))

        self.create_proxy_ac()

        # holds the start position for each proxy
        start_joint_translation = {}

        for i in range(start_val, end_val+1):
            current_time = om.MTime(i, om.MTime.kPALFrame)
            oma.MAnimControl.setCurrentTime(current_time)
            for proxy, jnt_dag in self.proxy_influence_pairs.iteritems():
                if i == start_val:
                    start_joint_translation[proxy] = self.get_value(jnt_dag, 't')
                else:
                    jnt_translation = self.get_value(jnt_dag, 't')
                    jnt_rotation = self.get_value(jnt_dag, 'r')
                    euler_rotation = self.get_angular(jnt_rotation.asEulerRotation())
                    delta_translation = -1.0 * (start_joint_translation[proxy] - jnt_translation)
                    jnt_scale = self.get_value(jnt_dag, 's')

                    self.add_proxy_key(current_time, proxy, delta_translation, euler_rotation, jnt_scale)
        #
        oma.MAnimControl.setCurrentTime(start_time)

    def create_proxy_ac(self):
        for proxy in self.proxy_influence_pairs.keys():
            proxy_dag = self.get_object_path(proxy)
            proxy_dag_fn = om.MFnDagNode(proxy_dag)

            proxy_translation = self.get_value(proxy_dag, 't')
            proxy_rotation = self.get_value(proxy_dag, 'r')
            proxy_scale = self.get_value(proxy_dag, 's')

            x_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'translateX', om.MFn.kAnimCurveTimeToDistance)
            y_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'translateY', om.MFn.kAnimCurveTimeToDistance)
            z_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'translateZ', om.MFn.kAnimCurveTimeToDistance)

            self.ac_translate[proxy] = [x_ac, y_ac, z_ac]

            x_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'rotateX', oma.MFnAnimCurve.kAnimCurveTA)
            y_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'rotateY', oma.MFnAnimCurve.kAnimCurveTA)
            z_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'rotateZ', oma.MFnAnimCurve.kAnimCurveTA)

            self.ac_rotate[proxy] = [x_ac, y_ac, z_ac]

            x_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'scaleX', om.MFn.kAnimCurveTimeToUnitless)
            y_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'scaleY', om.MFn.kAnimCurveTimeToUnitless)
            z_ac = self.create_ac(proxy_dag_fn, proxy_dag, 'scaleZ', om.MFn.kAnimCurveTimeToUnitless)

            self.ac_scale[proxy] = [x_ac, y_ac, z_ac]

            current_time = om.MTime(0, om.MTime.kPALFrame)
            oma.MAnimControl.setCurrentTime(current_time)

            euler_rotation = self.get_angular(proxy_rotation.asEulerRotation())

            self.add_proxy_key(current_time, proxy, proxy_translation, euler_rotation, proxy_scale)

    def create_ac(self, dag_fn, dag, attribute, curve_type):
        attr = dag_fn.attribute(attribute)
        anim_curve = oma.MFnAnimCurve()
        anim_curve.create(dag.transform(), attr, curve_type)
        return anim_curve

    def add_proxy_key(self, time, proxy, translate, rotate, scale):
        self.ac_translate[proxy][0].addKey(time, translate.x)
        self.ac_translate[proxy][1].addKey(time, translate.y)
        self.ac_translate[proxy][2].addKey(time, translate.z)

        self.ac_rotate[proxy][0].addKey(time, math.radians(rotate[0]))
        self.ac_rotate[proxy][1].addKey(time, math.radians(rotate[1]))
        self.ac_rotate[proxy][2].addKey(time, math.radians(rotate[2]))

        self.ac_scale[proxy][0].addKey(time, scale[0])
        self.ac_scale[proxy][1].addKey(time, scale[1])
        self.ac_scale[proxy][2].addKey(time, scale[2])
        
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
        jnt_pivot = self.get_value(jnt_dag_path, 't')
        proxy_transform_fn.setRotatePivot(om.MPoint(jnt_pivot.x, jnt_pivot.y, jnt_pivot.z), om.MSpace.kWorld, 1)
        proxy_transform_fn.setScalePivot(om.MPoint(jnt_pivot.x, jnt_pivot.y, jnt_pivot.z), om.MSpace.kWorld, 1)
        
        proxy_points = self.get_proxy_points(proxy)
        proxy_uv = self.get_proxy_uv(proxy)

        jnt_scale = self.get_value(jnt_dag_path, 's')
        proxy_transform_fn.setScale(jnt_scale)

        jnt_rotation = self.get_value(jnt_dag_path, 'r', om.MSpace.kWorld)
        proxy_transform_fn.setRotation(jnt_rotation, om.MSpace.kWorld)
        self.set_proxy_points(proxy, proxy_points)
        self.set_proxy_uv(proxy, proxy_uv)
        
    def get_proxy_uv(self, proxy):
        proxy_mesh_fn = om.MFnMesh(proxy)
        u,v = proxy_mesh_fn.getUVs()
        return [u, v]

    def set_proxy_uv(self, proxy, uvs):
        proxy_mesh_fn = om.MFnMesh(proxy)
        proxy_mesh_fn.setUVs(uvs[0], uvs[1])

    def get_proxy_points(self, proxy):
        proxy_mesh_fn = om.MFnMesh(proxy)
        all_points = proxy_mesh_fn.getPoints(om.MSpace.kWorld)
        return all_points
    
    def set_proxy_points(self, proxy, points):
        proxy_mesh_fn = om.MFnMesh(proxy)
        proxy_mesh_fn.setPoints(points, om.MSpace.kWorld)
        
    def get_value(self, jnt_dag, val, space=om.MSpace.kWorld):
        jnt_dag_path = self.get_object_path(jnt_dag)
        jnt_transform = om.MFnTransform(jnt_dag_path)

        if val == 't':
            jnt_translation = jnt_transform.translation(space)
            return jnt_translation
        elif val == 'r':
            euler_rotation = jnt_transform.rotation(space, True)
            # jnt_rotation = [math.degrees(angle) for angle in (euler_rotation.x, euler_rotation.y, euler_rotation.z)]
            return euler_rotation
        elif val == 's':
            jnt_scale = jnt_transform.scale()
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
        
    def get_object_path(self, proxy_name):
        sel_list = om.MSelectionList()
        try:
            sel_list.add(proxy_name)
        except:
            return None
        
        dag_path = sel_list.getDagPath(0)

        return dag_path

    def get_angular(self, rotation):
        angular_rotation = [math.degrees(angle) for angle in (rotation.x, rotation.y, rotation.z)]
        return angular_rotation
    
    def get_skin_cluster(self, mesh_fn):
        '''
        get a list of all the skin clusters in the file, iterate and see if the shapes connected match our selection
        '''
        self.in_plug = mesh_fn.findPlug('inMesh', False)
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
        plugin_fn.registerCommand(ZooSurgeonCommand.cmd_name, ZooSurgeonCommand.creator)
    except:
        sys.stderr.write("Failed to register command: " + ZooSurgeonCommand.cmd_name)

def uninitializePlugin(mobject):
    plugin_fn = om.MFnPlugin(mobject)
    try:
        plugin_fn.deregisterCommand(ZooSurgeonCommand.cmd_name)
    except:
        sys.stderr.write("Failed to un-register command: " + ZooSurgeonCommand.cmd_name)