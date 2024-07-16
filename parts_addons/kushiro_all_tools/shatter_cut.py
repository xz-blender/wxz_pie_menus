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

from bpy_extras import view3d_utils

import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
    StringProperty
)


import random
import itertools

from pprint import pprint


import timeit



def inside(p1, v1, v2):
    m1 = p1 - v1
    m2 = p1 - v2
    m3 = v2 - v1
    if (m1.length + m2.length) - m3.length < 0.001:
        return True
    else:
        return False


def get_intersect_point(v1, v2, v3, v4):
    res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
    if res == None:
        return None
    p1, p2 = res        
    if (p2 - p1).length < 0.001:
        if inside(p1, v1, v2) and inside(p1, v3, v4):
            return p1
    else:
        return None
        

def get_pine(f1, e1, p1, mid):
    ms = []
    for e2 in f1.edges:
        if e2 == e1:
            continue
        v1 = e2.verts[0].co
        v2 = e2.verts[1].co
        pin = get_intersect_point(p1, p1 + mid * 10000, v1, v2)
        if pin != None:
            ms.append(((pin - p1).length, e2, pin))
    if len(ms) == 0:
        return None, None
    d1, e2, pin = min(ms, key=lambda x: x[0])
    return e2, pin



def conn_verts(bm, v1, v2):
    res = bmesh.ops.connect_verts(bm, verts=[v1, v2])
    e1 = res['edges'][0]
    return e1, e1.link_faces


def cut_point(bm, e1, c1):
    res = bmesh.ops.bisect_edges(bm, edges=[e1], cuts=1)
    ge = res['geom_split']
    vs = [g for g in ge if isinstance(g, bmesh.types.BMVert)]
    if len(vs) == 0:
        return None
    v1 = vs[0]
    v1.co = c1
    return v1


def cut_face(bm, f1, p1, emin, tilt):
    a = p1.vert
    b = p1.link_loop_next.vert
    m1 = b.co - a.co
    dis = random.random()
    c1 = a.co + m1 * dis
    if m1.length * dis < emin:
        return None
    if m1.length * (1.0 - dis) < emin:
        return None    
    sn = f1.normal
    mid = m1.cross(sn).normalized() * -1

    if tilt != 0:
        tr = (random.random() * math.pi - math.pi/2) * tilt
        mid = Quaternion(sn, tr).to_matrix() @ mid

    e2, pin = get_pine(f1, p1.edge, c1, mid)
    if e2 == None:
        return None
    c2 = pin
    if (c2 - c1).length < emin:
        return None
    v1 = cut_point(bm, p1.edge, c1)
    v2 = cut_point(bm, e2, c2)
    if v1 == None or v2 == None:
        return None
    e3, fs2 = conn_verts(bm, p1.link_loop_next.vert, v2)
    return fs2


def calc_factor(f1, irregular):
    area = f1.calc_area()
    res = area * ((1.0 - irregular)) + irregular
    # return math.sin(area) + 1.0
    return res



def shatter(bm, faces, count, emin, tilt, irregular):
    fs = list(faces)
    area = [calc_factor(f1, irregular) for f1 in fs]
    
    for i in range(count):
        f1 = random.choices(fs, weights=area, k=1)[0]
        # f1 = random.choice(fs)
        ps = f1.loops
        ew = [p.edge.calc_length() for p in ps]
        # p1 = random.choice(ps)
        p1 = random.choices(ps, weights=ew, k=1)[0]
        res = cut_face(bm, f1, p1, emin, tilt)
        # return
        if res == None:
            continue
        f2, f3 = res        
        fid = fs.index(f1)
        fs.pop(fid)
        area.pop(fid)        
        fs.extend([f2, f3])
        area.extend([calc_factor(f2, irregular), calc_factor(f3, irregular)])
         
  


class ShatterCutOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.shatter_cut_operator"
    bl_label = "Shatter Cut —— 随机切割面"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "随机切割选择的面，默认与夹角边呈90度"
    # , "GRAB_CURSOR", "BLOCKING"


    # prop_steps: IntProperty(
    #     name="Solver steps",
    #     description="Solver steps",
    #     default=500,
    #     min=1
    # )    
 

    prop_seed: IntProperty(
        name="随机种",
        description="随机种",
        default=0,
    )   

    prop_cut: IntProperty(
        name="切割次数",
        description="切割次数",
        default=500,
        min=0
    )   

    prop_min: FloatProperty(
        name="最小距离",
        description="最小距离",
        default=0.001,
        min=0
    )   


    prop_tilt: FloatProperty(
        name="倾斜量",
        description="切割两侧的倾斜量",
        default=0,
        min=0,
        max=1.0,
        step=0.05
    )   

    prop_irregular: FloatProperty(
        name="不规则尺寸",
        description="不规则尺寸",
        default=0,
        min=0,
        max=1.0,
        step=0.05
    )   



    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def process(self, context):
        bm = self.get_bm()
        sel = [f1 for f1 in bm.faces if f1.select]

        for f1 in sel:
            f1.select = False

        random.seed(self.prop_seed)

        shatter(bm, sel, self.prop_cut, self.prop_min, self.prop_tilt, self.prop_irregular)

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
        
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}

