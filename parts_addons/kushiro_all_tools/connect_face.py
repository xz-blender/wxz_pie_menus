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

import bpy
import bmesh
import bmesh.utils

from mathutils import Matrix, Vector, Quaternion




import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
)

import pprint




class CONNECTFACE_OT_operator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.connectface_operator"
    bl_label = "Connect Face —— 桥接挤出"
    bl_options = {"REGISTER", "UNDO"}
    bl_description  = "挤出桥接工具的结合，挤出方向若存在相同面，则自动连接"
    #, "GRAB_CURSOR", "BLOCKING"


    prop_auto_link_unsel: BoolProperty(
        name="链接未选中",
        description="链接未选定的面",
        default=True,
    )    


    prop_remove_internal: BoolProperty(
        name="删除内部面",
        description="删除内部面",
        default=True,
    )    



    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def connect_faces_pair(self, f1, f2):
        bm = self.get_bm()
        # bridge f1 and f2
        es1 = [e for e in f1.edges]
        es2 = [e for e in f2.edges]
        es3 = list(set(es1 + es2))
        bmesh.ops.bridge_loops(bm, edges=es3)




    def is_facing(self, f1, f2):
        cen1 = f1.calc_center_median()
        cen2 = f2.calc_center_median()
        vec = cen2 - cen1
        vec.normalize()
        if vec.length == 0:
            return False
        if f1.normal.length == 0 or f2.normal.length == 0:
            return False
        ang = vec.angle(f1.normal)
        vec2 = vec * -1
        ang2 = vec2.angle(f2.normal)
        if ang < 0.01 and ang2 < 0.01:
            return True
        else:
            return False


    def get_near_face(self, sel, f1):
        if f1.is_valid == False:
            return None
        fs = []
        cen1 = f1.calc_center_median()
        for f2 in sel:
            if f2.is_valid:
                if f1 != f2:
                    if self.is_facing(f1, f2):
                        cen2 = f2.calc_center_median()
                        dis = (cen1 - cen2).length
                        fs.append((f2, dis))
        if len(fs) == 0:
            return None
        min1 = min(fs, key=lambda x: x[1])
        return min1[0]


    def connect_faces(self, bm, sel, sel2):
        dfs = []
        connected = []
        for f1 in sel:
            if (f1 in connected) == False:
                f2 = self.get_near_face(sel2, f1)
                if f2 != None and (f2 in connected) == False:
                    self.connect_faces_pair(f1, f2)
                    dfs += [f1, f2]
                    connected += [f1, f2]

        dfs = list(set(dfs))
        dfs = [f for f in dfs if f.is_valid]
        bmesh.ops.delete(bm, geom=dfs, context='FACES')



    def clean_internal_faces(self, bm):
        # deselect all faces
        for f in bm.faces:
            f.select = False

        bpy.ops.mesh.select_interior_faces()
        fs = [f for f in bm.faces if f.select]
        bmesh.ops.delete(bm, geom=fs, context='FACES')



    def process(self, context):
        bm = self.get_bm()     
        sel = [f for f in bm.faces if f.select]  

        if self.prop_auto_link_unsel:
            fs_all = [f for f in bm.faces]
            self.connect_faces(bm, sel, fs_all)
        else:
            self.connect_faces(bm, sel, sel)

        if self.prop_remove_internal == True:
            self.clean_internal_faces(bm)

        # deselect all edges
        for e in bm.edges:
            e.select = False


        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)   



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
        self.mode = 0
        self.prop_base_edge = 0

        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}
