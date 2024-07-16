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


class CutCornerOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.cut_corner_operator"
    bl_label = "Cut Corner —— 面拐切角"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="切角大小",
        description="定义切角的大小",
        default=0.1,
        step=0.5,
        min=0.001
    )    

    prop_angle: FloatProperty(
        name="角度限制",
        description="仅当角度小于此值时才切割",
        default=100,
        step=10,
        min=0
    )    


    prop_merge: FloatProperty(
        name="合并距离",
        description="产生的切角点如果小于此距离，则合并",
        default=0.02,
        step=0.1,
        min=0
    )    



    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm




    def process(self, context):
        bm = self.get_bm()
        #f1 = bm.faces[0] 
        # self.vec_find_min(f1)
        self.cut_corner(bm)

        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)            


    def cut_corner(self, bm):
        plen = self.prop_plen       
        anglim = self.prop_angle
        merge = self.prop_merge
        sel = [f1 for f1 in bm.faces if f1.select]

        for f1 in sel:
            f1.select = False
        for v1 in bm.verts:
            v1.select = False
        for e1 in bm.edges:
            e1.select = False            

        ps = []
        for f1 in sel:
            for p in f1.loops:
                deg = math.degrees(p.calc_angle())
                if p.is_convex and deg < anglim:
                    p3 = p.link_loop_prev
                    if self.is_bound(p, sel) and self.is_bound(p3, sel):
                        ps.append(p)
        cs = []
        for p in ps:
            p2 = p.link_loop_next
            p3 = p.link_loop_prev
            m1 = p2.vert.co - p.vert.co
            m2 = p3.vert.co - p.vert.co
            e1 = p.edge
            c1 = p.vert.co + m1.normalized() * plen
            e2 = p3.edge
            c2 = p.vert.co + m2.normalized() * plen
            elen1 = e1.calc_length()
            elen2 = e2.calc_length()       

            if elen1 < plen - (merge/2) or elen2 < plen - (merge/2):
                continue

            if elen1 - plen > merge:
                self.cut_forward_bisect(bm, e1, c1)            

            if elen2 - plen > merge:
                self.cut_forward_bisect(bm, e2, c2)

            p2 = p.link_loop_next
            p3 = p.link_loop_prev            
            cs.append((p2, p3))

        for p2, p3 in cs:
            self.chop_line(bm, p2.vert, p3.vert)




    def chop_line(self, bm, v1, v2):
        res = bmesh.ops.connect_verts(bm, verts=[v1, v2], check_degenerate=False)
        es = res['edges']
        if len(es) == 0:
            return None
        return es[0]



    def cut_forward_bisect(self, bm, e1, c1):
        res = bmesh.ops.bisect_edges(bm, edges=[e1], cuts=1)
        # pprint.pprint(res)
        vs = [e for e in res['geom_split'] if isinstance(e, bmesh.types.BMVert)]
        # es = [e for e in res['geom_split'] if isinstance(e, bmesh.types.BMEdge)]
        if len(vs) == 0:
            return
        v1 = vs[0]
        if c1 != None:
            v1.co = c1
        return v1            
                    

    def is_bound(self, p, sel):        
        if p.edge.is_boundary:
            return True
        e1 = p.edge
        if len(e1.link_faces) != 2:
            return True
        else:
            fs = list(e1.link_faces)
            f1 = p.face
            fs.remove(f1)
            f2 = fs[0]
            if f2 in sel:
                return False
            else:
                return True

                        


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

