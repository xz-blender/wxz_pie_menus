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

from numpy.core.function_base import linspace
from numpy.lib.function_base import average
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
)

# from . import gui
import pprint


class SmallSet:
    def __init__(self) -> None:
        self.members = set()


class Untriangulate:

    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm

    def process(self):
        bm = self.get_bm()
        jomap = {}
        smap = []
        for e1 in bm.edges:
            if e1.select ==  False:
                continue
            if len(e1.link_faces) != 2:
                continue
            deg = e1.calc_face_angle()
            if deg == None:
                continue
            if deg < math.radians(0.1):                
                f1, f2 = e1.link_faces
                k1 = f1 in jomap
                k2 = f2 in jomap
                if k1 and k2:
                    s1 = jomap[f1]
                    s2 = jomap[f2]
                    if s1 == s2:
                        continue
                    items = list(s2.members)
                    s1.members.update(items)
                    for f3 in items:                        
                        jomap[f3] = s1
                    if s2 in smap:
                        smap.remove(s2)
                    
                elif k1 and (k2 == False):
                    s1 = jomap[f1]
                    jomap[f2] = s1
                    s1.members.add(f2)                    
                elif k2 and (k1 == False):
                    s1 = jomap[f2]
                    jomap[f1] = s1
                    s1.members.add(f1)                    
                else:
                    s1 = SmallSet()
                    s1.members.add(f1)
                    s1.members.add(f2)                    
                    smap.append(s1)
                    jomap[f1] = s1
                    jomap[f2] = s1

        for p in smap:
            es = []
            for f1 in p.members:
                for e1 in f1.edges:
                    if len(e1.link_faces) != 2:                        
                        continue
                    f2, f3 = e1.link_faces
                    if f2 in p.members and f3 in p.members:
                        es.append(e1)
                        f2.select_set(True)
                        f3.select_set(True)
            es = list(set(es))
            es = sorted(es, key=lambda e: e.calc_length() * -1)
            res = bmesh.ops.dissolve_edges(bm, edges=es, use_verts=True, use_face_split=False)            
        
        self.join_edges(bm)
        #bpy.ops.mesh.select_all(action='SELECT')
        bm.select_flush(True)
        bpy.ops.mesh.select_mode(type="FACE")

        obj = bpy.context.active_object
        me = obj.data        
        bmesh.update_edit_mesh(me)
       

    def join_edges(self, bm):
        ps = []
        for f1 in bm.faces:
            for p in f1.loops:
                if len(p.vert.link_edges) == 2:
                    if abs(math.degrees(p.calc_angle()) - 180) < 0.001:
                        ps.append(p.vert)
        ps = list(set(ps))
        for p in ps:
            bmesh.ops.dissolve_verts(bm, verts=[p])
