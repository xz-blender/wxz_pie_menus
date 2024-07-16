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
import itertools


import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
)

import pprint
# from . import gui

class SelectSimOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.select_sim_operator"
    bl_label = "Select Sim —— 选择相似面"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "选择相似的面"
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="相似性",
        description="定义所选面之间的相似性",
        default=0.01,
        step=0.4,
        min = 0
    )    


    prop_face_sim: IntProperty(
        name="面的搜索层级",
        description="附近的人脸检查级别 (高层级时慢)",
        default=0,
        step = 1,
        min = 0,
        max = 5
    )    





    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm




    def process(self, context):
        bm = self.get_bm()
        mode = bm.select_mode.pop()
        plen = self.prop_plen

        if mode == 'FACE':
            if self.prop_face_sim:
                self.sel_sim_face_near(bm, plen)
            else:
                self.sel_sim_face(bm, plen)

        elif mode == 'EDGE':
            self.sel_sim_edge_near(bm, plen)

        elif mode == 'VERT':
            self.sel_sim_vert_near(bm, plen)
                
        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)   



    def sel_sim_vert_near(self, bm, plen):        
        de = self.prop_face_sim
        sel = [v1 for v1 in bm.verts if v1.select]
        psel = []
        for v1 in sel:
            total = 0
            for f1 in v1.link_faces:
                fp = self.get_near_area(f1, de, [])
                total += fp
            psel.append((v1, total))


        for v1 in bm.verts:
            if v1 in sel:
                continue
            total = 0
            for f1 in v1.link_faces:
                fp = self.get_near_area(f1, de, [])
                total += fp

            for v2, total2 in psel:                
                if abs(total2 - total) < plen:
                    v1.select = True



    def sel_sim_edge_near(self, bm, plen):
        de = self.prop_face_sim
        sel = [e1 for e1 in bm.edges if e1.select]
        psel = []
        for e1 in sel:
            total = 0
            for f1 in e1.link_faces:
                fp = self.get_near_area(f1, de, [])
                total += fp
            psel.append((e1, total))


        for e1 in bm.edges:
            if e1 in sel:
                continue
            total = 0
            for f1 in e1.link_faces:
                fp = self.get_near_area(f1, de, [])
                total += fp

            for e2, total2 in psel:            
                d1 = e1.calc_length() - e2.calc_length()
                if abs(d1) < plen:
                    if abs(total2 - total) < plen:
                        e1.select = True




    def sel_sim_face_near(self, bm, plen):
        de = self.prop_face_sim
        sel = [f1 for f1 in bm.faces if f1.select]
        psel = []
        for f1 in sel:
            fp = self.get_near_area(f1, de, [])
            psel.append(fp)        

        for f1 in bm.faces:
            if f1 in sel:
                continue
            fp = self.get_near_area(f1, de, [])
            for fp2 in psel:
                if abs(fp - fp2) < plen:
                    f1.select = True        




    def get_hash(self, f1):
        fp = f1.calc_area()
        for p in f1.loops:
            a = p.calc_angle()
            b = p.edge.calc_length()
            p2 = p.link_loop_prev
            c = p2.edge.calc_length()
            k = a * a + (b + c) * (b + c)
            k2 = (b-c) * (b-c)
            k3 = (k + k2) * (k + k2)
            fp = fp + k3
        return fp


    def get_near_area(self, f1, depth, checked):
        # lens = [p1.edge.calc_length() + p1.calc_angle() for p1 in f1.loops]
        # emax = sum(lens)
        # total = f1.calc_area() + emax
        total = self.get_hash(f1)       
        if depth == 0:
            return total

        for e1 in f1.edges:            
            if len(e1.link_faces) == 2:
                a, b = e1.link_faces
                if a == f1:
                    f2 = b
                else:
                    f2 = a
                if f2 in checked:
                    continue
                cin = checked + [f1]
                d1 = max(depth, 1)
                d1 = d1 * d1
                total += self.get_near_area(f2, depth-1, cin) * d1
        return total



    def sel_sim_face(self, bm, plen):
        sel = [f1 for f1 in bm.faces if f1.select]
        psel = []
        for f1 in sel:
            fp = self.get_hash(f1)
            psel.append(fp)        

        for f1 in bm.faces:
            if f1 in sel:
                continue
            fp = self.get_hash(f1)
            for fp2 in psel:
                if self.check_sim(fp, fp2):
                    f1.select = True        



    def sel_sim_edge(self, bm, plen):
        sel = [e1 for e1 in bm.edges if e1.select]
        psel = []
        for e1 in sel:
            fps = []
            for f1 in e1.link_faces:
                fp = self.get_hash(f1)
                fps.append(fp)
            psel.append((e1, fps))
        
        for e1 in bm.edges:
            fps = []
            for f1 in e1.link_faces:
                fp = self.get_hash(f1)
                fps.append(fp)

            for e2, fps2 in psel:
                dif = e1.calc_length() - e2.calc_length()
                if abs(dif) > plen:
                    continue
                if len(fps) != len(fps2):
                    continue
                if len(fps) == 1:                        
                    if self.check_sim(fps[0], fps2[0]):
                        e1.select = True
                elif len(fps) == 2:
                    s1 = False
                    s2 = False
                    if self.check_sim(fps[0], fps2[0]):
                        s1 = True
                    elif self.check_sim(fps[0], fps2[1]):
                        s1 = True
                    if self.check_sim(fps[1], fps2[0]):
                        s2 = True
                    elif self.check_sim(fps[1], fps2[1]):
                        s2 = True
                    if s1 and s2:
                        e1.select = True        



    def check_sim(self, fp1, fp2):
        plen = self.prop_plen
        if abs(fp1 - fp2) < plen:
            return True
        else:
            return False


    # def check_sim(self, fp1, fp2):
    #     plen = self.prop_plen
    #     if len(fp1) != len(fp2):
    #         return False

    #     p1 = np.array(fp1)       
    #     p2 = np.array(fp2)
    #     ct = len(fp1)
    #     for i in range(ct):
    #         p1 = np.roll(p1, 1, axis=0)
    #         p3 = np.abs(p1 - p2)
    #         p4 = np.sum(p3)
    #         if p4 <= plen:
    #             return True

    #     np.flip(p1)

    #     for i in range(ct):
    #         p1 = np.roll(p1, 1, axis=0)
    #         p3 = np.abs(p1 - p2)
    #         p4 = np.sum(p3)
    #         if p4 <= plen:
    #             return True                
        
    #     return False




    # def check_sim(self, fp1, fp2):
    #     plen = self.prop_plen
    #     if len(fp1) != len(fp2):
    #         return False

    #     p1 = np.array(fp1)       
    #     p2 = np.array(fp2)
    #     p1 = np.sort(p1)
    #     p2 = np.sort(p2)
    #     p3 = np.abs(p1 - p2)
    #     p4 = np.sum(p3)
    #     if p4 <= plen:
    #         return True
    #     else:
    #         return False



    # def get_hash(self, f1):
    #     fp = []
    #     for p in f1.loops:
    #         a = p.calc_angle()
    #         b = p.edge.calc_length()
    #         fp.append(a)
    #         fp.append(b)
    #     return fp





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
        if context.edit_object:

            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


