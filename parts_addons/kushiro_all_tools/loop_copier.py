# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Kushiro

import math
from operator import indexOf

import bpy
import bmesh
import bmesh.utils

from mathutils import Matrix, Vector, Quaternion, Euler

import mathutils
import time


import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
    StringProperty
)

from pprint import pprint
# from . import gui

import itertools

import numpy as np
import json


# install_package('scipy')
# import scipy

# install_package('numba')
# import numba
# # from scipy.spatial import Delaunay



class LoopCopierOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.loop_copier_operator"
    bl_label = "Loop Copier —— 阵列复制"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "将网格沿选择的边进行阵列复制(可环形阵列、曲线阵列)"
    #, "GRAB_CURSOR", "BLOCKING"


    operation_mode : EnumProperty(
                #(identifier, name, description, icon, number)
        items = [('None','执行两次:先设置阵列边(选项2),再阵列操作(选项3)','','',0),
                 ('Setsource','存储选择的边','','',1),
                 ('Copy','阵列复制到存储边','','',2), 
                 ],
        name = "Operation:",
        default = 'None')


    prop_geo: BoolProperty(
        name="使用几何节点",
        description="使用的几何图形节点进行创建。它是非破坏性的，你可以动画循环.",
        default=False,
    )    


    prop_shift: FloatProperty(
        name="位移",
        description="Shift",
        default=0,
        step=1,
    )   


    prop_num: IntProperty(
        name="复制数量",
        description="Number of copies",
        default=8,
        step=1,
        min=1
    )    


    prop_normal: BoolProperty(
        name="对齐到法线",
        description="Aligned to normal",
        default=True,  
    )    


    prop_follow_surface: BoolProperty(
        name="跟随曲线的曲面",
        description="遵循曲线曲面，而不是对所有点使用一个法线",
        default=False,  
    )    



    prop_rotation: FloatVectorProperty(
        name="Rotation",
        description="Rotation",
        default=Vector(),
        step=10,
    )    

    prop_rotation_order: StringProperty(
        name="Rotation Order",
        description="Rotation Order",
        default='XYZ',
    )       

    prop_scale: FloatVectorProperty(
        name="Scale",
        description="Scale",
        default=Vector((1,1,1)),

    ) 


    prop_offset: FloatVectorProperty(
        name="Offset",
        description="Offset",
        default=Vector(),

    )        


    # prop_shift: FloatProperty(
    #     name="Extrude shift",
    #     description="Center shifting between two faces",
    #     default=0,
    # )    

    ps = []
    opened = False

    def draw(self, context):
        layout = self.layout     

        layout.label(text='Operation:')
        layout.prop(self, "operation_mode", expand=True)

        layout.separator_spacer()

        layout.label(text='Copying:')
        sub1 = layout.row().column()        
        sub1.prop(self, "prop_follow_surface", expand=True)
        sub1.prop(self, "prop_geo", expand=True)

        sub1.prop(self, "prop_shift", expand=True)
        sub1.prop(self, "prop_num", expand=True)        

        sub1.prop(self, "prop_rotation", expand=True)
        sub1.prop(self, "prop_rotation_order", expand=True)   
        sub1.prop(self, "prop_scale", expand=True)   
        sub1.prop(self, "prop_offset", expand=True)     
        
        sub1.enabled = False

        if self.operation_mode == 'Setsource':
            sub1.enabled = False
        elif self.operation_mode == 'Copy':
            sub1.enabled = True


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def copymesh(self, bm, fs, ps, opened, ns):
        # obj = bpy.context.active_object
        # mat = obj.matrix_world
        if len(fs) == 0:
            return

        plen = len(ps)
        if plen == 0:
            return

        selv = []
        for f1 in fs:
            selv.extend(f1.verts)
        selv = list(set(selv))

        gs = fs
        cen = Vector()
        for v1 in selv:
            cen = cen + v1.co
        cen = cen / len(selv)

        pcen = Vector()
        for v1 in ps:
            pcen = pcen + v1
        pcen = pcen / len(ps)

        total = 0
        if opened == False:
            for i in range(plen):
                i2 = (i+1) % plen
                m1 = ps[i2] - ps[i]
                total += m1.length
        else:
            for i in range(plen - 1):
                i2 = i + 1
                m1 = ps[i2] - ps[i]
                total += m1.length            

        clen = total / self.prop_num
        shift = self.prop_shift    

        sn = self.get_normal(ps, opened)
        ms = []
        for i in range(plen):
            i2 = (i+1) % plen
            m1 = ps[i2] - ps[i]
            ms.append(m1)
        main = max(ms, key=lambda e:e.length)
        loopmat = self.get_mat(main, main.cross(sn) * -1, sn, pcen)
        loopmat2 = loopmat.inverted()
        #loopmat @ Vector((0,0,1))      

        rad1 = self.prop_rotation
        rad2 = Vector((math.radians(rad1[0]), math.radians(rad1[1]), math.radians(rad1[2])))
        try:
            p_rotate = Euler(rad2, self.prop_rotation_order).to_matrix().to_4x4()
        except:
            self.prop_rotation_order = 'XYZ'
            p_rotate = Euler(rad2, 'XYZ').to_matrix().to_4x4()

        scale1 = Matrix.Scale(self.prop_scale[0], 4, Vector((1,0,0)))
        scale2 = Matrix.Scale(self.prop_scale[1], 4, Vector((0,1,0)))
        scale3 = Matrix.Scale(self.prop_scale[2], 4, Vector((0,0,1)))
        scale = scale1 @ (scale2 @ scale3)


        p_shift = Matrix.Translation(self.prop_offset)

        for k in range(self.prop_num):
            shift2 = shift + k * clen
            p1, i = self.get_mapped(ps, shift2, total, opened)
            if p1 == None:
                # print('none')
                continue
            ret = bmesh.ops.duplicate(bm, geom=gs)
            geom = ret["geom"]        
            matcen = Matrix.Translation(cen)
            matcen2 = matcen.inverted()

            if self.prop_follow_surface:
                loopmat = self.map_for_point(opened, plen, i, ps, ns, p1)
                loopmat2 = loopmat.inverted()            

            matplace = Matrix.Translation(loopmat2 @ p1)
            # matplace = Matrix.Identity(4)

            matrot = Quaternion(Vector((1,0,0)), math.pi/2 * -1).to_matrix().to_4x4()     
            if self.prop_normal:
                if opened == False:                    
                    i2 = (i+1) % plen
                    m1 = loopmat2 @ ps[i2] - loopmat2 @ ps[i]
                    d1 = math.atan2(m1.y, m1.x)
                    rot = Quaternion(Vector((0,0,1)), d1).to_matrix().to_4x4()                         
                    matplace = matplace @ (rot @ (p_shift @ p_rotate))
                else:
                    i2 = i+1
                    m1 = loopmat2 @ ps[i2] - loopmat2 @ ps[i]    
                    d1 = math.atan2(m1.y, m1.x)         
                    rot = Quaternion(Vector((0,0,1)), d1).to_matrix().to_4x4()           
                    matplace = matplace @ (rot @ (p_shift @ p_rotate))
            else:
                rot = Matrix.Identity(4)

            fmat = loopmat @ (matplace @ (matrot @ (scale @ (matcen2 @ Matrix.Identity(4)))))
            for v1 in geom:
                if isinstance(v1, bmesh.types.BMVert):
                    v1.co = fmat @ v1.co

        bm.normal_update()



    def get_mat(self, m1, m2, m3, cen):
        if m1.length == 0 or m2.length == 0 or m3.length == 0:
            return Matrix.Identity(4)            
        m = Matrix.Identity(4)        
        m[0][0:3] = m1.normalized()
        m[1][0:3] = m2.normalized()
        m[2][0:3] = m3.normalized()
        m[3][0:3] = cen.copy()
        m = m.transposed()
        return m    



    def get_normal(self, ps, opened):
        plen = len(ps)
        if opened:
            sn = Vector()
            for i in range(plen-2):
                i2 = i+1
                i3 = i+2
                m1 = ps[i3] - ps[i2]
                m2 = ps[i] - ps[i2]
                sn = sn + m1.cross(m2)
            return sn.normalized()
        else:
            sn = Vector()
            for i in range(plen):
                i2 = (i+1) % plen
                i3 = (i+2) % plen
                m1 = ps[i3] - ps[i2]
                m2 = ps[i] - ps[i2]
                sn = sn + m1.cross(m2)      
            return sn.normalized() * -1



    def map_for_point(self, opened, plen, i, ps, ns, p1):
        if opened == False:                    
            i2 = (i+1) % plen
        else:
            i2 = i+1
        m1 = ps[i2] - ps[i]
        sn = (ns[i] + ns[i2])/2
        if sn.length == 0:
            sn = Vector((0,0,1))
        sn = sn.normalized()
        y = m1.cross(sn)
        sn2 = m1.cross(y)        
        loopmat = self.get_mat(m1, y, sn2, p1)
        return loopmat



    def get_mapped(self, ps, p, total, opened):
        plen = len(ps)
        p2 = p % total
        if opened == False:
            for i in range(plen):            
                i2 = (i+1) % plen
                m1 = ps[i2] - ps[i]
                if p2 < m1.length:
                    m2 = m1.normalized() * p2
                    return ps[i] + m2, i
                else:
                    p2 = p2 - m1.length
            return None
        else:
            for i in range(plen - 1):
                i2 = i+1
                m1 = ps[i2] - ps[i]            
                if p2 < m1.length:
                    m2 = m1.normalized() * p2
                    return ps[i] + m2, i
                else:
                    p2 = p2 - m1.length
            return None            
            


    def setedge(self, bm, es):
        vs = []
        for e1 in es:
            vs.extend(e1.verts)
        vs = list(set(vs))
        if len(es) == 0 or len(vs) == 0:
            return [], False, []
        pp1 = vs[0]
        opened = False
        # pps = []
        for v1 in vs:
            fes = [e for e in v1.link_edges if e.select]
            if len(fes) == 1:
                # pps.append(v1)
                pp1 = v1
                opened = True
                break   
    
        ps = self.get_ps(pp1)        
        ps2 = [p.co.copy() for p in ps]
        ns = [p.normal.copy() for p in ps]

        return ps2, opened, ns
        # pprint(self.ps)


        

    def get_ps(self, pp1):        
        pp = pp1
        ps = []
        es2 = set()
        cc = 0
        while True:
            cc += 1
            ps.append(pp)
            es = pp.link_edges
            es = [e for e in es if e.select]
            if len(es) == 0:
                return ps
            elif len(es) == 1:                
                e1 = es[0]
                if e1 in es2:
                    return ps
            else:
                if (es[0] in es2) == False:
                    e1 = es[0]
                elif (es[1] in es2) == False:
                    e1 = es[1]
                else:
                    return ps
            es2.add(e1)
            pp = e1.other_vert(pp)
            if pp == pp1:
                break
        return ps




    def process2(self, context):        
        bm = self.get_bm()
        es = [e1 for e1 in bm.edges if e1.select]
        sel = [f1 for f1 in bm.faces if f1.select]

        # if len(LoopCopierOperator.ps) == 0 or (len(es) > 0 and len(sel) == 0):
        #     self.operation_mode = 'Setsource'
        # else:
        #     self.operation_mode = 'Copy'

        if self.operation_mode == 'Setsource':            
            ps, opened, ns = self.setedge(bm, es)
            LoopCopierOperator.ps = ps
            LoopCopierOperator.opened = opened
            LoopCopierOperator.ns = ns

        elif self.operation_mode == 'Copy':            
            ps = LoopCopierOperator.ps
            ns = LoopCopierOperator.ns
            opened = LoopCopierOperator.opened
            self.copymesh(bm, sel, ps, opened, ns)
 
        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)  



    def copymesh_geo(self, context, sel, ps, opened):
        obj1 = bpy.context.active_object
        world = obj1.matrix_world
        world2 = world.inverted()

        bpy.ops.object.mode_set(mode = 'OBJECT') 
        bpy.ops.object.select_all(action='DESELECT')
        obj1.select_set(True)
        bpy.ops.object.mode_set(mode = 'EDIT') 

        bpy.ops.mesh.separate(type='SELECTED')

        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)  
        bpy.ops.object.mode_set(mode = 'OBJECT')  

        objs = list(bpy.context.selected_objects)
        if len(objs) != 2:
            return
        objs.remove(obj1)
        part = objs[0]
        part.name = 'Loop_Copier_part'
        override = context.copy()
        override["selected_editable_objects"] = [part]        
        with context.temp_override(**override):                      
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        me = bpy.data.meshes.new('Loop_Copier_mesh')
        obj2 = bpy.data.objects.new('Loop_Copier_loop', me)
        bpy.context.collection.objects.link(obj2)
        bm = bmesh.new()      
        vs = []
        for p in ps:
            v1 = bm.verts.new( world @ p)
            vs.append(v1)
        plen = len(ps)
        es = []
        for i in range(plen - 1):
            i2 = i+1
            e1 = bm.edges.new((vs[i], vs[i2]))
            es.append(e1)
        if opened == False:
            e1 = bm.edges.new((vs[-1], vs[0]))
            es.append(e1)        

        bm.to_mesh(me)
        # obj2.matrix_world = obj1.matrix_world.copy()
        obj1.select_set(False)
        part.select_set(False)
        obj2.select_set(True)

        self.make_geo(context, part, obj2)    
        bpy.ops.object.mode_set(mode = 'EDIT') 



    def setup_node(self, obj, node_group):
        if 'input_sockets' in obj:  
            if len(node_group.inputs) > 0:
                node_group.inputs.remove(node_group.inputs[0])
            for p in obj['input_sockets']:                
                try:                    
                    node_group.inputs.new(type=p['type'], name=p['name'])
                except Exception as e:
                    print(e)            
        
        if 'output_sockets' in obj:  
            if len(node_group.outputs) > 0:
                node_group.outputs.remove(node_group.outputs[0])
            for p in obj['output_sockets']:                
                try:
                    node_group.outputs.new(type=p['type'], name=p['name'])
                except Exception as e:
                    print(e)

        for node in obj['nodes']:
            node1 = node_group.nodes.new( type=node['bl_idname'])
            node1.name = node['name']            
            node1.location = Vector(node['location'])
            if node['bl_idname'] == 'ShaderNodeMath':
                node1.operation = node['operation']
            if node['bl_idname'] == 'FunctionNodeInputInt':
                node1.integer = node['integer']            
            if node['bl_idname'] == 'GeometryNodeGroup':
                node1.node_tree = bpy.data.node_groups['LoopCopierCore']
           
            for k in node['inputs']:
                v = node['inputs'][k]
                for p in node1.inputs:
                    if p.identifier == k:                        
                        p.default_value = v['value']
                        break
                
        for link in obj['links']:
            node1 = None
            out1 = None
            for p in node_group.nodes:
                if p.name == link['from_node']:
                    node1 = p
                    break
            node2 = None
            out2 = None
            for p in node_group.nodes:
                if p.name == link['to_node']:
                    node2 = p
                    break
            if node1 == None or node2 == None:
                continue

            if node1.bl_idname == 'ShaderNodeMath':
                idx = link['from_index']                
                out1 = node1.outputs[idx]
            else:
                for p in node1.outputs:
                    if p.name == link['from_socket']:
                        out1 = p
                        break

            if node2.bl_idname == 'ShaderNodeMath':
                idx2 = link['to_index']
                out2 = node2.inputs[idx2]
            else:
                for p in node2.inputs:
                    if p.name == link['to_socket']:
                        out2 = p
                        break
            if out1 == None or out2 == None:
                continue
            node_group.links.new(out1, out2)

            # for p in node_group.nodes:
            #     if p.name == link['from_node']:
            #         node1 = p
            #         break
            # if node1 == None:
            #     continue

            # idx = link['from_index']
            # if idx < len(node1.outputs):
            #     tmp1 = node1.outputs[idx]
            #     if tmp1.name == link['from_socket']:
            #         out1 = tmp1

            # if out1 == None:          
            #     continue  

            # node2 = None
            # out2 = None
            # for p in node_group.nodes:
            #     if p.name == link['to_node']:
            #         node2 = p
            #         break
            # if node2 == None:
            #     continue

            # idx2 = link['to_index']
            # if idx2 < len(node2.inputs):
            #     tmp2 = node2.inputs[idx2]
            #     if tmp2.name == link['to_socket']:
            #         out2 = tmp2
          
            # if out2 == None:            
            #     continue  
            # node_group.links.new(out1, out2)



    def make_geo(self, context, part, obj2):
        data = '''{"nodes": [{"location": [-807.22, -197.23], "bl_idname": "ShaderNodeValue", "name": "Value", "inputs": {}}, {"location": [-811.92, -312.16], "bl_idname": "GeometryNodeObjectInfo", "name": "Object Info", "inputs": {"As Instance": {"type": "bool", "value": false}}}, {"location": [43.42, -110.52], "bl_idname": "NodeGroupOutput", "name": "Group Output", "inputs": {}}, {"location": [-808.42, 1.45], "bl_idname": "NodeGroupInput", "name": "Group Input", "inputs": {}}, {"location": [-807.6, -86.61], "bl_idname": "FunctionNodeInputInt", "name": "Integer", "integer": 36, "inputs": {}}, {"location": [-368.74, -52.44], "bl_idname": "GeometryNodeGroup", "name": "Group", "inputs": {}}], "links": [{"from_node": "Group", "from_socket": "Instances", "from_index": 0, "to_node": "Group Output", "to_socket": "Geometry", "to_index": 0}, {"from_node": "Integer", "from_socket": "Integer", "from_index": 0, "to_node": "Group", "to_socket": "Count", "to_index": 0}, {"from_node": "Value", "from_socket": "Value", "from_index": 0, "to_node": "Group", "to_socket": "Value", "to_index": 1}, {"from_node": "Group Input", "from_socket": "Geometry", "from_index": 0, "to_node": "Group", "to_socket": "Geometry", "to_index": 2}, {"from_node": "Object Info", "from_socket": "Geometry", "from_index": 3, "to_node": "Group", "to_socket": "Geometry 2", "to_index": 3}], "output_sockets": [{"name": "Geometry", "type": "NodeSocketGeometry", "identifier": "Output_1"}], "input_sockets": [{"name": "Geometry", "type": "NodeSocketGeometry", "identifier": "Input_0"}]}
        '''
        data_core = '''{"nodes": [{"location": [-259.45, -65.6], "bl_idname": "ShaderNodeMath", "name": "Math.002", "operation": "ADD", "inputs": {"Value_002": {"type": "float", "value": 0.5}}}, {"location": [-435.97, -64.95], "bl_idname": "ShaderNodeMath", "name": "Math.001", "operation": "DIVIDE", "inputs": {"Value_002": {"type": "float", "value": 0.5}}}, {"location": [369.51, 188.81], "bl_idname": "GeometryNodeSetPosition", "name": "Set Position.001", "inputs": {"Selection": {"type": "bool", "value": true}}}, {"location": [-63.03, -122.66], "bl_idname": "ShaderNodeMath", "name": "Math", "operation": "MODULO", "inputs": {"Value_001": {"type": "float", "value": 1.0}, "Value_002": {"type": "float", "value": 0.5}}}, {"location": [-613.94, -243.8], "bl_idname": "GeometryNodeInputIndex", "name": "Index", "inputs": {}}, {"location": [-773.79, -80.62], "bl_idname": "ShaderNodeMath", "name": "Math.003", "operation": "DIVIDE", "inputs": {"Value_001": {"type": "float", "value": 20.0}, "Value_002": {"type": "float", "value": 0.5}}}, {"location": [-425.59, 190.12], "bl_idname": "GeometryNodeMeshToCurve", "name": "Mesh to Curve", "inputs": {"Selection": {"type": "bool", "value": true}}}, {"location": [-40.31, 243.8], "bl_idname": "GeometryNodeCurveToPoints", "name": "Curve to Points", "inputs": {"Length": {"type": "float", "value": 0.10000000149011612}}}, {"location": [-1027.84, 27.65], "bl_idname": "NodeGroupInput", "name": "Group Input", "inputs": {}}, {"location": [-69.95, -293.81], "bl_idname": "GeometryNodeTransform", "name": "Transform", "inputs": {}}, {"location": [1038.9, 212.2], "bl_idname": "GeometryNodeInstanceOnPoints", "name": "Instance on Points", "inputs": {"Selection": {"type": "bool", "value": true}, "Pick Instance": {"type": "bool", "value": false}, "Instance Index": {"type": "int", "value": 0}}}, {"location": [841.12, -74.23], "bl_idname": "FunctionNodeAlignEulerToVector", "name": "Align Euler to Vector.001", "inputs": {"Factor": {"type": "float", "value": 1.0}}}, {"location": [170.12, 11.82], "bl_idname": "GeometryNodeSampleCurve", "name": "Sample Curve", "inputs": {"Value_Float": {"type": "float", "value": 0.0}, "Value_Int": {"type": "int", "value": 0}, "Value_Bool": {"type": "bool", "value": false}, "Length": {"type": "float", "value": 0.0}, "Curve Index": {"type": "int", "value": 0}}}, {"location": [623.53, -74.17], "bl_idname": "FunctionNodeAlignEulerToVector", "name": "Align Euler to Vector.002", "inputs": {"Factor": {"type": "float", "value": 1.0}}}, {"location": [1486.99, 39.82], "bl_idname": "NodeGroupOutput", "name": "Group Output", "inputs": {}}, {"location": [1266.75, 113.29], "bl_idname": "GeometryNodeRealizeInstances", "name": "Realize Instances", "inputs": {}}], "links": [{"from_node": "Realize Instances", "from_socket": "Geometry", "from_index": 0, "to_node": "Group Output", "to_socket": "Instances", "to_index": 0}, {"from_node": "Group Input", "from_socket": "Count", "from_index": 0, "to_node": "Curve to Points", "to_socket": "Count", "to_index": 1}, {"from_node": "Group Input", "from_socket": "Count", "from_index": 0, "to_node": "Math.001", "to_socket": "Value", "to_index": 1}, {"from_node": "Group Input", "from_socket": "Value", "from_index": 1, "to_node": "Math.003", "to_socket": "Value", "to_index": 0}, {"from_node": "Group Input", "from_socket": "Geometry", "from_index": 2, "to_node": "Mesh to Curve", "to_socket": "Mesh", "to_index": 0}, {"from_node": "Group Input", "from_socket": "Geometry 2", "from_index": 3, "to_node": "Transform", "to_socket": "Geometry", "to_index": 0}, {"from_node": "Group Input", "from_socket": "Translation", "from_index": 4, "to_node": "Transform", "to_socket": "Translation", "to_index": 1}, {"from_node": "Group Input", "from_socket": "Rotation", "from_index": 5, "to_node": "Transform", "to_socket": "Rotation", "to_index": 2}, {"from_node": "Group Input", "from_socket": "Scale", "from_index": 6, "to_node": "Transform", "to_socket": "Scale", "to_index": 3}, {"from_node": "Transform", "from_socket": "Geometry", "from_index": 0, "to_node": "Instance on Points", "to_socket": "Instance", "to_index": 2}, {"from_node": "Mesh to Curve", "from_socket": "Curve", "from_index": 0, "to_node": "Curve to Points", "to_socket": "Curve", "to_index": 0}, {"from_node": "Set Position.001", "from_socket": "Geometry", "from_index": 0, "to_node": "Instance on Points", "to_socket": "Points", "to_index": 0}, {"from_node": "Curve to Points", "from_socket": "Points", "from_index": 0, "to_node": "Set Position.001", "to_socket": "Geometry", "to_index": 0}, {"from_node": "Sample Curve", "from_socket": "Position", "from_index": 5, "to_node": "Set Position.001", "to_socket": "Position", "to_index": 2}, {"from_node": "Index", "from_socket": "Index", "from_index": 0, "to_node": "Math.001", "to_socket": "Value", "to_index": 0}, {"from_node": "Math.001", "from_socket": "Value", "from_index": 0, "to_node": "Math.002", "to_socket": "Value", "to_index": 0}, {"from_node": "Math.003", "from_socket": "Value", "from_index": 0, "to_node": "Math.002", "to_socket": "Value", "to_index": 1}, {"from_node": "Math", "from_socket": "Value", "from_index": 0, "to_node": "Sample Curve", "to_socket": "Factor", "to_index": 6}, {"from_node": "Math.002", "from_socket": "Value", "from_index": 0, "to_node": "Math", "to_socket": "Value", "to_index": 0}, {"from_node": "Mesh to Curve", "from_socket": "Curve", "from_index": 0, "to_node": "Sample Curve", "to_socket": "Curves", "to_index": 0}, {"from_node": "Align Euler to Vector.002", "from_socket": "Rotation", "from_index": 0, "to_node": "Align Euler to Vector.001", "to_socket": "Rotation", "to_index": 0}, {"from_node": "Sample Curve", "from_socket": "Normal", "from_index": 7, "to_node": "Align Euler to Vector.002", "to_socket": "Vector", "to_index": 2}, {"from_node": "Sample Curve", "from_socket": "Tangent", "from_index": 6, "to_node": "Align Euler to Vector.001", "to_socket": "Vector", "to_index": 2}, {"from_node": "Align Euler to Vector.001", "from_socket": "Rotation", "from_index": 0, "to_node": "Instance on Points", "to_socket": "Rotation", "to_index": 5}, {"from_node": "Instance on Points", "from_socket": "Instances", "from_index": 0, "to_node": "Realize Instances", "to_socket": "Geometry", "to_index": 0}], "output_sockets": [{"name": "Instances", "type": "NodeSocketGeometry", "identifier": "Output_0"}], "input_sockets": [{"name": "Count", "type": "NodeSocketInt", "identifier": "Input_1"}, {"name": "Value", "type": "NodeSocketFloat", "identifier": "Input_2"}, {"name": "Geometry", "type": "NodeSocketGeometry", "identifier": "Input_3"}, {"name": "Geometry 2", "type": "NodeSocketGeometry", "identifier": "Input_4"}, {"name": "Translation", "type": "NodeSocketVectorTranslation", "identifier": "Input_5"}, {"name": "Rotation", "type": "NodeSocketVectorEuler", "identifier": "Input_6"}, {"name": "Scale", "type": "NodeSocketVectorXYZ", "identifier": "Input_7"}]}

        '''
             
        mod = obj2.modifiers.new('Geometry Nodes', 'NODES')

        if obj2.modifiers[-1].node_group:
            node_group = mod.node_group    
        else:
            node_group = bpy.data.node_groups.new('LoopCopierGroup', 'GeometryNodeTree')    
            # mod.node_group = node_group

        geo1 = json.loads(data_core)      
        node_group_core = bpy.data.node_groups.new('LoopCopierCore', 'GeometryNodeTree')
        self.setup_node(geo1, node_group_core)  

        geo2 = json.loads(data)      
        self.setup_node(geo2, node_group)     

        node_group.nodes["Object Info"].inputs[0].default_value = part
        node_group.nodes["Integer"].integer = self.prop_num
        node_group.nodes["Value"].outputs[0].default_value = self.prop_shift        
        node_group.nodes["Group"].inputs[4].default_value[0]
        node_group.nodes["Group"].inputs[4].default_value[0] = self.prop_offset[0]
        node_group.nodes["Group"].inputs[4].default_value[1] = self.prop_offset[1]
        node_group.nodes["Group"].inputs[4].default_value[2] = self.prop_offset[2]
        node_group.nodes["Group"].inputs[5].default_value[0] = math.radians(self.prop_rotation[0])
        node_group.nodes["Group"].inputs[5].default_value[1] = math.radians(self.prop_rotation[1])
        node_group.nodes["Group"].inputs[5].default_value[2] = math.radians(self.prop_rotation[2])
        node_group.nodes["Group"].inputs[6].default_value[0] = self.prop_scale[0]
        node_group.nodes["Group"].inputs[6].default_value[1] = self.prop_scale[1]
        node_group.nodes["Group"].inputs[6].default_value[2] = self.prop_scale[2]
        
        node_group_core.nodes["Align Euler to Vector.001"].axis = 'X'
        node_group_core.nodes["Align Euler to Vector.002"].axis = 'Z'

        node_group_core.nodes["Sample Curve"].mode = 'FACTOR'

        out1 = self.get_inputs(node_group_core, 'Mesh to Curve', 'Curve', 'outputs')
        out2 = self.get_inputs(node_group_core, 'Sample Curve', 'Curve', 'inputs')
        out3 = self.get_inputs(node_group_core, 'Sample Curve', 'Curves', 'inputs')
        if out1 != None:
            if out2 != None:
                node_group_core.links.new(out1, out2)
            elif out3 != None:
                node_group_core.links.new(out1, out3)
        
        obj2.modifiers[-1].node_group = node_group



    def get_inputs(self, gp, name1, name2, mode):
        for p in gp.nodes:
            if p.name == name1:
                if mode == 'inputs':
                    for p2 in p.inputs:
                        if p2.identifier == name2:
                            return p2
                elif mode == 'outputs':
                    for p2 in p.outputs:
                        if p2.identifier == name2:
                            return p2                    
        return None


    def print_geo(self, context):
        # obj = bpy.data.objects['Cube.018']
        mo = bpy.context.object.modifiers[0]
        gp = [mo.node_group, bpy.data.node_groups['LoopCopierCore_origin']]

        for node_group in gp:
            nodes = list(node_group.nodes)
            geo = {}
            geo['nodes'] = []
            geo['links'] = []

            geo['output_sockets'] = []
            for p in node_group.outputs:
                p2 = {}
                p2['name'] = p.name
                p2['type'] = p.bl_socket_idname
                p2['identifier'] = p.identifier
                geo['output_sockets'].append(p2)

            geo['input_sockets'] = []
            for p in node_group.inputs:                
                p2 = {}
                p2['name'] = p.name
                p2['type'] = p.bl_socket_idname
                p2['identifier'] = p.identifier
                geo['input_sockets'].append(p2)  


            for node in nodes:
                inputs = []
                outputs = []
                # print(node.location, node.bl_idname, inputs, outputs)
                obj = {}
                obj['location'] = [round(p, 2) for p in node.location[:]]
                obj['bl_idname'] = node.bl_idname
                obj['name'] = node.name
                if node.bl_idname == 'ShaderNodeMath':
                    obj['operation'] = node.operation

                if node.bl_idname == 'FunctionNodeInputInt':
                    obj['integer'] = node.integer   

                obj['inputs'] = {}
                for i in range(len(node.inputs)):
                    p = node.inputs[i]
                    name = p.identifier

                    # for attr in dir(p):
                    #     print(str(attr), getattr(p, attr))
                    if p.is_linked == False and hasattr(p, 'default_value'):
                        val = {}                    
                        ptype = p.default_value.__class__.__name__
                        if ptype == 'bool' or ptype == 'int' or ptype == 'float':
                            val['type'] = ptype
                            val['value'] = p.default_value
                            obj['inputs'][name] = val
                geo['nodes'].append(obj)

            links = list(node_group.links)
            for pk in links:
                # pk.from_node.name
                # pk.from_socket.identifier
                id = pk.from_node.name
                sid = pk.from_socket.name
                idx1 = list(pk.from_node.outputs).index(pk.from_socket)

                id2 = pk.to_node.name
                sid2 = pk.to_socket.name
                idx2 = list(pk.to_node.inputs).index(pk.to_socket)
                # print(id, sid, '=>', id2, sid2)
                obj = {}
                obj['from_node'] = id
                obj['from_socket'] = sid
                obj['from_index'] = idx1
                obj['to_node'] = id2
                obj['to_socket'] = sid2
                obj['to_index'] = idx2
                geo['links'].append(obj)

            # pprint(geo)
            print(json.dumps(geo))  


    def process(self, context):     
        # self.print_geo(context)   
        # # self.make_geo(context)
        # return     

        # obj2 = bpy.context.active_object   
        # self.make_geo(None, None, obj)
        # return

        if self.prop_geo:            
            bm = self.get_bm()
            es = [e1 for e1 in bm.edges if e1.select]
            sel = [f1 for f1 in bm.faces if f1.select]

            if self.operation_mode == 'Setsource':            
                ps, opened, _ = self.setedge(bm, es)
                LoopCopierOperator.ps = ps
                LoopCopierOperator.opened = opened

            elif self.operation_mode == 'Copy':            
                ps = LoopCopierOperator.ps
                opened = LoopCopierOperator.opened
                self.copymesh_geo(context, sel, ps, opened)        
    
            # obj = bpy.context.active_object                
            # me = bpy.context.active_object.data
            # bmesh.update_edit_mesh(me)           
            # bpy.ops.object.editmode_toggle()
            # bpy.ops.object.editmode_toggle()
        else:
            self.process2(context)


    def execute(self, context):
        self.process(context)      
        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing 


    def invoke(self, context, event): 
        self.operation_mode = 'None'
        # self.mark = None
        # bm = self.get_bm()
        # es = [e1 for e1 in bm.edges if e1.select]
        # sel = [f1 for f1 in bm.faces if f1.select]

        # if len(es) > 0 and len(sel) == 0:
        #     self.operation_mode = 'Setsource'
        # else:
        #     self.operation_mode = 'Copy'                            
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}




    # def draw_point(self, p1):
    #     gui.lines += [p1 + Vector((0.02, 0, 0)), p1 - Vector((0.02, 0, 0))]
    #     gui.lines += [p1 + Vector((0, 0.02, 0)), p1 - Vector((0, 0.02, 0))]


    # def modal(self, context, event):    
    #     # print(event.type, event.value, event.mouse_prev_y, event.mouse_y)

    #     context.area.tag_redraw()
    #     if event.type == 'Q':
    #         if event.value == 'PRESS':                                
    #             gui.draw_handle_remove()
    #             return {'FINISHED'}   

    #     if event.type == 'A':
    #         if event.value == 'PRESS':                                
    #             gui.lines = []
    #             self.process(context)
    #             return {'RUNNING_MODAL'}   


    #     elif event.type == 'ESC':
    #         if event.value == 'PRESS':
    #             gui.draw_handle_remove()
    #             return {'CANCELLED'}


    #     if 'MOUSE' in event.type:
    #         return {'PASS_THROUGH'}

    #     if 'PAN' in event.type:
    #         return {'PASS_THROUGH'}
        

    #     return {'RUNNING_MODAL'}


    # def invoke(self, context, event):  

    #     self.mark = None

    #     if context.edit_object:
    #         context.window_manager.modal_handler_add(self)
    #         gui.draw_handle_add((self, context))
    #         gui.text_handle_add((self, context))
    #         gui.txtall = ['Please press Esc to exit']

    #         self.process(context)            
    #         return {'RUNNING_MODAL'} 
    #     else:
    #         return {'CANCELLED'}


