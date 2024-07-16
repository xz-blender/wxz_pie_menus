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

import random 


from . import convert_to_ngons


class Vert:
    def __init__(self, co) -> None:
        self.co = co
        self.vnew = None


class SafeNgonOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.safe_ngon_operator"
    bl_label = "Safe Ngon —— 重构Ngon结构线"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "重构N边面结构线"
    #, "GRAB_CURSOR", "BLOCKING"


    prop_merge: FloatProperty(
        name="合并距离",
        description="合并重复顶点的距离",
        default=0.01,
        step=0.1,
        min = 0.0001
    )    

    prop_angle: FloatProperty(
        name="平行角度",
        description="平行基础边的最大角度",
        default=10,
        step=10,
        min = 0.0001
    )    

    prop_splitall: BoolProperty(
        name="多重拆分",
        description="拆分多个位置",
        default=False,
    )    

    prop_convert_ngon: BoolProperty(
        name="转换为Ngons",
        description="转换所有面为ngons",
        default=False,
    )

    prop_move_edges: BoolProperty(
        name="移动边 (默认)",
        description="将边缘移动到更好的位置",
        default=True,
    )

    prop_seed: IntProperty(
        name="随机种子",
        description="随机溶解边缘的种子",
        default=0
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "prop_convert_ngon", expand=True)
        layout.prop(self, "prop_move_edges", expand=True)
        layout.prop(self, "prop_merge", expand=True)
        layout.prop(self, "prop_angle", expand=True)
        layout.prop(self, "prop_splitall", expand=True)
        layout.prop(self, "prop_seed", expand=True)
        #layout.label(text="")


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def get_borders(self, ps):
        borders = []        
        if self.prop_seed != 0:
            ps2 = list(ps)
            random.seed(self.prop_seed)
            random.shuffle(ps2)
        else:
            ps2 = sorted(ps, key=lambda e: e.edge.calc_length() * -1)
        #ps2=ps
        for p2 in ps2:
            e1 = p2.edge
            if len(e1.link_faces) != 2:
                continue
            deg = e1.calc_face_angle()
            if deg == None:
                continue
            if deg > math.radians(0.1):
                borders.append(p2)
        return borders

    
    def is_parallel(self, m1, m2, para):
        if m1.length == 0 or m2.length == 0:
            return False
        deg = math.degrees(m2.angle(m1))
        if ((deg > 180 - para and deg < 180 + para) \
            or (deg > 0 - para and deg < para)) == False:
            return False
        return True
    
    def get_mids(self, m1, m2, a, b, c, d):
        if m1.length < m2.length:
            mid1 = (b.co + a.co)/2
            mid2 = mid1 - c.co
            mid2 = mid2.project(m2) + c.co
            if self.isInside(mid2, c.co, d.co) == False:
                return None
            else:
                return (mid1, mid2)
        else:
            mid2 = (c.co + d.co)/2
            mid1 = mid2 - a.co
            mid1 = mid1.project(m1) + a.co                    
            if self.isInside(mid1, a.co, b.co) == False:
                return None
            else:
                return (mid1, mid2)

    def check_intersect(self, mid1, mid2, p1, p2, f1, ps):
        m3 = mid2 - mid1
        if m3.length == 0:
            return False
        a1 = p1.vert
        a2 = p1.edge.other_vert(a1)
        t1 = a1.co - a2.co
        if t1.length == 0:
            return False
        t2 = t1.cross(f1.normal)   
        if t2.length == 0:
            return False
        d1 = t2.angle(m3)
        d2 = (t2 * -1).angle(m3)
        if d1 > d2:
            return False            
        if self.isIntersect(mid1, mid2, p1, p2, ps):
            return False    
        return True


    def get_pairs(self, p, f1):
        para = self.prop_angle
        pairs = []
        ps = self.loop_all(p)
        borders = self.get_borders(ps)
        if len(borders) < 2:
            return []
        for p1 in borders:
            for p2 in borders:
                if p1 == p2:
                    continue
                a, b = p1.edge.verts
                c, d = p2.edge.verts
                m1 = b.co - a.co
                m2 = d.co - c.co
                if self.is_parallel(m1, m2, para) == False:
                    continue

                mids = self.get_mids(m1, m2, a, b, c, d)
                if mids == None:
                    continue
                mid1, mid2 = mids
                    
                if self.check_intersect(mid1, mid2, p1, p2, f1, ps) == False:
                    continue

                if self.prop_splitall:
                    pairs.append((p1, p2, mid1, mid2))                    
                else:
                    return [(p1, p2, mid1, mid2)]                    
        return pairs


    def put_es_list(self, es, mid):
        merge = self.prop_merge
        for m in es:
            if (mid.co - m.co).length <= merge:
                return m
        es.append(mid)
        return mid


    def sort_vs(self, v1s, p):
        a = p.vert.co
        s2 = sorted(v1s, key=lambda v1: (v1.co - a).length)
        return s2


    def isInside(self, v1, p1, p2):
        len1 = (p2 - p1).length
        return abs((v1 - p1).length + (v1 - p2).length - len1) < 0.001


    def isIntersect(self, mid1, mid2, p1, p2, ps):
        for p in ps:
            if p == p1 or p == p2:
                continue
            a = p.vert
            b = p.edge.other_vert(a)
            v1 = self.find_inter(mid1, mid2, a.co, b.co)
            if v1 != None:
                if self.isInside(v1, mid1, mid2):
                    if self.isInside(v1, a.co, b.co):                    
                        return True
        return False
        

    def find_inter(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        if (p2 - p1).length < 0.0001:
            return p1
        else:
            return None



    def process(self, context):
        bm = self.get_bm()
        espair = []
        clean = []
        clean2 = []
        emap = {}
        for f1 in bm.faces:
            if f1.select == False:
                continue
            if len(f1.loops) == 3:
                continue
            for p in f1.loops:
                e1 = p.edge
                if len(e1.link_faces) != 2:
                    continue
                deg = e1.calc_face_angle()
                if deg == None:
                    continue
                if deg < math.radians(0.1):                    
                    if p.calc_angle() < math.radians(179):
                        res = self.get_pairs(p, f1)
                        for p1, p2, mid1, mid2 in res:
                            m1 = Vert(mid1)
                            m2 = Vert(mid2)
                            if p1.edge in emap:
                                m1 = self.put_es_list(emap[p1.edge], m1)
                            else:
                                emap[p1.edge] = [m1]

                            if p2.edge in emap:                                
                                m2 = self.put_es_list(emap[p2.edge], m2)
                            else:
                                emap[p2.edge] = [m2]

                            espair.append((m1, m2))
                            clean.append(p.edge)

        for e1 in emap:
            mids = emap[e1]
            vs = []
            for m in mids:
                v1 = bm.verts.new(m.co)
                m.vnew = v1
                vs.append(v1)
            emap[e1] = vs

        for e1 in emap:
            for f1 in e1.link_faces:
                v1s = emap[e1]
                vs = []
                for p in f1.loops:
                    vs.append(p.vert)
                    if p.edge == e1:
                        v2s = self.sort_vs(v1s, p)
                        vs += v2s
                bm.faces.new(vs)
            fs = list(e1.link_faces)
            bmesh.ops.delete(bm, geom=fs, context='FACES')
        
        for m1, m2 in espair:
            v1 = m1.vnew
            v2 = m2.vnew
            res = bmesh.ops.connect_verts(bm, verts=[v1, v2])
            if res != None and 'edges' in res:
                clean2.extend(res['edges'])

        clean = list(set(clean))
        for p in clean:
            es = [p]
            try:
                bmesh.ops.dissolve_edges(bm, edges=es, use_verts=True, use_face_split=False)
            except:
                pass


        if self.prop_seed != 0:
            flat_e = []
            for f1 in bm.faces:
                if f1.select == False:
                    continue            
                for e1 in f1.edges:                
                    if len(e1.link_faces) != 2:
                        continue
                    deg = e1.calc_face_angle()
                    if deg == None:
                        continue
                    if deg < math.radians(0.1): 
                        flat_e.append(e1)
        
            random.seed(self.prop_seed)
            random.shuffle(flat_e)

            for e1 in flat_e:
                es = [e1]
                try:
                    bmesh.ops.dissolve_edges(bm, edges=es, use_verts=True, use_face_split=False)
                except:
                    pass

        obj = bpy.context.active_object
        me = obj.data        
        bmesh.update_edit_mesh(me)
        bpy.ops.mesh.select_all(action='DESELECT')


    def loop_all(self, p):
        ps = []
        pc = p
        while True:
            ps.append(pc)
            pc = pc.link_loop_next
            if pc == p:
                break
        return ps


    def execute(self, context):
        if self.prop_convert_ngon:
            u1 = convert_to_ngons.Untriangulate()
            u1.process()
        if self.prop_move_edges:
            self.process(context)
            
        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing 


    def start_process(self, context):
        if self.prop_convert_ngon:
            u1 = convert_to_ngons.Untriangulate()
            u1.process()    
        if self.prop_move_edges:
            self.process(context)


    def invoke(self, context, event):
        if context.edit_object:
            #self.setup(context)

            self.start_process(context)

            #return {'RUNNING_MODAL'} 
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


