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

import mathutils
import time


from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
)

import pprint
from . import guiva

import itertools
# import numpy as np




class VisualAxisOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.visual_axis_operator"
    bl_label = "Visual Axis —— 显示面轴向"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "显示激活的面的轴向，同时游标旋转量和轴向对齐，在操作符复选框进行删除"
    #, "GRAB_CURSOR", "BLOCKING"

    handle = None


    prop_edge: IntProperty(
        name="边编号",
        description="用于定义X轴的边",
        default=0,
        min=0
    )    


    prop_axis_size: FloatProperty(
        name="轴大小",
        description="定义轴大小",
        default=10,
        step=10,
        min=0
    )    


    prop_remove: BoolProperty(
        name="删除轴",
        description="您可以通过选中此框来移除轴，或在没有任何选定面的情况下再次运行该工具",
        default=False,
    )    


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


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



    # def pro1(self, context, bm):
    #     slot = bpy.context.scene.transform_orientation_slots[0]
    #     slot.type = 'GLOBAL'
    #     if SDModelerOperator.handle != None:
    #         gui.handle3d = SDModelerOperator.handle
    #         gui.draw_handle_remove()
    #         SDModelerOperator.handle = None        

    #     sel = [f1 for f1 in bm.faces if f1.select]
    #     if len(sel) == 0:
    #         return
        
    #     gui.draw_handle_add((self, context))
    #     SDModelerOperator.handle = gui.handle3d
    #     f1 = sel[0]
    #     sn = f1.normal
    #     cen = f1.calc_center_median()
    #     p1 = f1.loops[0]
    #     v1 = p1.vert
    #     e1 = p1.edge
    #     v2 = e1.other_vert(v1)
    #     m1 = v2.co - v1.co
    #     m2 = m1.cross(sn) * -1
    #     mat = self.get_mat(m1, m2, sn, cen)

    #     obj = bpy.context.active_object
    #     wmat = obj.matrix_world
    #     bpy.ops.transform.create_orientation(name="Tran", use_view=False, use=True, overwrite=True)
    #     # ori = bpy.context.scene.orientations.get("TransViewer")
    #     # ori.matrix = mat.to_3x3()

    #     slot = bpy.context.scene.transform_orientation_slots[0]
    #     custom = slot.custom_orientation
    #     if custom == None:
    #         mat = Matrix.Identity(4)
    #     else:
    #         # mat = custom.matrix.to_4x4()
    #         custom.matrix = mat.to_3x3()
    #     # pprint.pprint(mat)
    #     gui.lines = [wmat @ (mat @ Vector((-10,0,0))), wmat @ (mat @ Vector((10,0,0)))]
    #     gui.lines2 = [wmat @ (mat @ Vector((0,-10,0))), wmat @ (mat @ Vector((0,10,0)))]



    def pro2(self, context, bm):
        if VisualAxisOperator.handle != None:
            guiva.handle3d = VisualAxisOperator.handle
            guiva.draw_handle_remove()
            VisualAxisOperator.handle = None   

        sel = [f1 for f1 in bm.faces if f1.select]
        if len(sel) == 0 or self.prop_remove:
            bpy.context.scene.cursor.matrix = Matrix.Identity(4)
            slot = bpy.context.scene.transform_orientation_slots[0]
            slot.type = 'GLOBAL'
            return
        
        obj = bpy.context.active_object
        wmat = obj.matrix_world      

        guiva.draw_handle_add((self, context))
        VisualAxisOperator.handle = guiva.handle3d        
        f1 = sel[0]
        sn = f1.normal
        sn = (wmat @ sn) - (wmat @ Vector())
        sn = sn.normalized()
        cen = wmat @ f1.calc_center_median()
        id = self.prop_edge % len(f1.loops)
        p1 = f1.loops[id]
        v1 = p1.vert
        e1 = p1.edge
        v2 = e1.other_vert(v1)
        m1 = (wmat @ v2.co) - (wmat @ v1.co)
        m2 = m1.cross(sn) * -1
        mat = self.get_mat(m1, m2, sn, cen)

        bpy.context.scene.cursor.matrix = mat
        slot = bpy.context.scene.transform_orientation_slots[0]
        slot.type = 'CURSOR'        
        plen = self.prop_axis_size
        guiva.lines = [mat @ Vector((-1 * plen,0,0)), mat @ Vector((plen,0,0))]
        guiva.lines2 = [mat @ Vector((0,-1 * plen,0)), mat @ Vector((0,plen,0))]





    def process(self, context):        
        bm = self.get_bm()
        # self.pro1(bm)
        self.pro2(context, bm)
 
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


    # def invoke(self, context, event):
    #     self.plen_old = 0.2

    #     if context.edit_object:
    #         self.process(context)
    #         return {'FINISHED'} 
    #     else:
    #         return {'CANCELLED'}




    def draw_point(self, p1):
        guiva.lines += [p1 + Vector((0.02, 0, 0)), p1 - Vector((0.02, 0, 0))]
        guiva.lines += [p1 + Vector((0, 0.02, 0)), p1 - Vector((0, 0.02, 0))]


    def modal(self, context, event):    
      
        return {'RUNNING_MODAL'}




    def invoke(self, context, event):  

        self.prop_remove = False

        if context.edit_object:
            # context.window_manager.modal_handler_add(self)            

            # gui.draw_handle_add((self, context))
            # gui.text_handle_add((self, context))
            # gui.txtall = ['Please press Esc to exit']

            self.process(context)            
            # return {'RUNNING_MODAL'} 
            return {'FINISHED'}  
        else:
            return {'CANCELLED'}


