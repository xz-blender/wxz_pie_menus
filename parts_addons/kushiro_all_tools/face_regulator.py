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


# from . import gui
import numpy as np



def solve(bm, steps, alignface, alignedge, alleq, flatten):
    moved = 0
    vs = [v for v in bm.verts if v.select]
    sfs = [f for f in bm.faces if f.select]
    # edges = [e for e in bm.edges if e.select]

    if len(vs) == 0:
        return

    for step in range(steps):
    # for step in range(1):
        vmap = {}
        for v1 in vs:
            vmap[v1] = []

        if alleq:
            for f1 in sfs:
                if len(f1.loops) != 4:
                    continue
                v1 = f1.loops[0].vert
                v2 = f1.loops[1].vert
                v3 = f1.loops[2].vert
                v4 = f1.loops[3].vert
                m1 = v2.co - v1.co
                m2 = v3.co - v2.co
                m3 = v4.co - v3.co
                m4 = v1.co - v4.co       
                avg = (m1.length + m2.length + m3.length + m4.length) / 4  
                k1, k2 = extend(v1, v2, m1, avg - m1.length)
                vmap[v1].append(k1)
                vmap[v2].append(k2)
                k1, k2 = extend(v3, v4, m3, avg - m3.length)
                vmap[v3].append(k1)
                vmap[v4].append(k2)
                k1, k2 = extend(v2, v3, m2, avg - m2.length)
                vmap[v2].append(k1)
                vmap[v3].append(k2)
                k1, k2 = extend(v4, v1, m4, avg - m4.length)
                vmap[v4].append(k1)
                vmap[v1].append(k2)
        else:
            for f1 in sfs:
                if len(f1.loops) != 4:
                    continue
                v1 = f1.loops[0].vert
                v2 = f1.loops[1].vert
                v3 = f1.loops[2].vert
                v4 = f1.loops[3].vert
                m1 = v2.co - v1.co
                m2 = v3.co - v2.co
                m3 = v4.co - v3.co
                m4 = v1.co - v4.co         
                d1 = m3.length - m1.length
                k1, k2 = extend(v1, v2, m1, d1/2)
                vmap[v1].append(k1)
                vmap[v2].append(k2)
                k1, k2 = extend(v3, v4, m3, -1 * d1/2)
                vmap[v3].append(k1)
                vmap[v4].append(k2)
                d2 = m4.length - m2.length  
                k1, k2 = extend(v2, v3, m2, d2/2)
                vmap[v2].append(k1)
                vmap[v3].append(k2)
                k1, k2 = extend(v4, v1, m4, -1 * d2/2)
                vmap[v4].append(k1)
                vmap[v1].append(k2)
            
        for f1 in sfs:
            if len(f1.loops) != 4:
                continue            
            for p1 in f1.loops:
                p2 = p1.link_loop_next
                p3 = p1.link_loop_prev
                m1 = p2.vert.co - p1.vert.co
                m2 = p3.vert.co - p1.vert.co
                if m1.length < 0.0001 or m2.length < 0.0001:
                    continue
                pro1 = m2.project(m1)
                k1 = p3.vert.co - pro1/2
                k2 = p1.vert.co + pro1/2
                vmap[p3.vert].append(k1)
                vmap[p1.vert].append(k2)
                pro2 = m1.project(m2)
                k3 = p2.vert.co - pro2/2
                k4 = p1.vert.co + pro2/2
                vmap[p2.vert].append(k3)
                vmap[p1.vert].append(k4)

        if flatten:
            sn_all = sum([f1.normal for f1 in sfs], Vector())/len(sfs)
        else:
            sn_all = Vector()

        for f1 in sfs:
            f1.normal_update()
            if f1.normal.length == 0:
                continue

            sn = f1.normal.copy()
            if alignface:       
                sn = align_local(f1.normal)
            else:
                if flatten:
                    sn = sn_all                
            balance(bm, f1, vmap, sn)       


        if alignedge:
            align_edges(bm, vmap, sfs)

       
        for v1 in vs:
            if len(vmap[v1]) == 0:
                continue        
            k1 = sum(vmap[v1], Vector()) / len(vmap[v1])
            # k1 = vmap[v1]
            mv = k1 - v1.co
            moved += mv.length
            # v1.co = v1.co * 0.5 + k1 * 0.5
            v1.co = k1




def align_edges(bm, vmap, fs):
    for f1 in fs:
        for p1 in f1.loops:
            p2 = p1.link_loop_next
            m1 = p2.vert.co - p1.vert.co
            m2 = align_local(m1)
            pro1 = m1.project(m2)
            h1 = pro1 - m1
            vmap[p2.vert].append(p2.vert.co + h1/2)
            vmap[p1.vert].append(p1.vert.co - h1/2)



def align_local(sn):
    if sn.length == 0:
        return sn
    sn2 = sn.normalized()
    bx = abs(sn2.dot(Vector((1, 0, 0))))
    by = abs(sn2.dot(Vector((0, 1, 0))))
    bz = abs(sn2.dot(Vector((0, 0, 1))))
    if bx > by and bx > bz:
        sn = Vector((1, 0, 0))
    elif by > bx and by > bz:
        sn = Vector((0, 1, 0))
    else:
        sn = Vector((0, 0, 1))
    return sn
    



def balance(bm, f1, vmap, sn):    
    vs = list(f1.verts)
    cen = f1.calc_center_median()
    for v1 in vs:
        m1 = v1.co - cen
        pro = m1.project(sn)
        if v1 in vmap:            
            vmap[v1].append(v1.co - pro)
            vmap[v1].append(v1.co - pro)
            


def extend(v1, v2, m1, d1):
    mk = m1.normalized()
    d2 = d1 / 2
    v3 = v1.co - mk * d2
    v4 = v2.co + mk * d2
    return v3, v4




def cubic_spline_interpolation(x, y, resolution):
    n = len(x)
    h = np.diff(x)
    alpha = np.zeros(n)
    for i in range(1, n-1):
        alpha[i] = 3/h[i] * (y[i+1]-y[i]) - 3/h[i-1] * (y[i]-y[i-1])

    l = np.zeros(n)
    mu = np.zeros(n)
    z = np.zeros(n)
    l[0] = 1
    mu[0] = 0
    z[0] = 0

    for i in range(1, n-1):
        l[i] = 2 * (x[i+1] - x[i-1]) - h[i-1] * mu[i-1]
        mu[i] = h[i] / l[i]
        z[i] = (alpha[i] - h[i-1] * z[i-1]) / l[i]

    l[n-1] = 1
    z[n-1] = 0
    c = np.zeros(n)
    b = np.zeros(n)
    d = np.zeros(n)

    for j in range(n-2, -1, -1):
        c[j] = z[j] - mu[j] * c[j+1]
        b[j] = (y[j+1] - y[j]) / h[j] - h[j] * (c[j+1] + 2 * c[j]) / 3
        d[j] = (c[j+1] - c[j]) / (3 * h[j])

    x_interp = np.linspace(x[0], x[-1], resolution)
    y_interp = np.zeros(resolution)
    j = 0

    for i in range(resolution):
        if x_interp[i] > x[j+1]:
            j += 1
        y_interp[i] = y[j] + b[j] * (x_interp[i] - x[j]) + c[j] * (x_interp[i] - x[j])**2 + d[j] * (x_interp[i] - x[j])**3

    return x_interp, y_interp





class FaceRegulatorOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.face_regulator_operator"
    bl_label = "Face Regulator —— 四边面矫正"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "将四边形面矫正为正方形"
    # , "GRAB_CURSOR", "BLOCKING"


    prop_steps: IntProperty(
        name="解算步骤数",
        description="解算步骤数",
        default=500,
        min=1
    )    


    prop_flatten: BoolProperty(
        name="全部展平",
        description="全部展平",
        default=False
    )         
 

    prop_align_face: BoolProperty(
        name="面-对齐局部XYZ",
        description="将面对齐到局部X Y Z轴",
        default=False
    )     

    prop_align_edge: BoolProperty(
        name="边-对齐局部XYZ",
        description="将面边缘与局部X Y Z轴对齐",
        default=False
    )        


    prop_all_equal: BoolProperty(
        name="方形面",
        description="使所有面的边长度相等",
        default=False,
    )     





    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def process(self, context):
        bm = self.get_bm()
        steps = self.prop_steps
        alignface = self.prop_align_face
        alignedge = self.prop_align_edge
        # smooth = self.prop_smooth
        # bd = self.prop_boundary
        # findex = self.prop_align_face
        # fcenter = self.prop_align_center
        alleq = self.prop_all_equal
        flatten = self.prop_flatten

        solve(bm, steps, alignface, alignedge, alleq, flatten)

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
        self.prop_boundary = 0.5
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}



