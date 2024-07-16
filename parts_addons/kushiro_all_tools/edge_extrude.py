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

from mathutils import Matrix, Vector, Quaternion

import mathutils
import time


import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    StringProperty,
    FloatVectorProperty,
)

import pprint
import itertools

import bpy
import random





class EdgeExtrudeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.edge_extrude_operator"
    bl_label = "Edge Extrude —— 挤出边(增强)"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "挤出选择的边(增强)"
    #, "GRAB_CURSOR", "BLOCKING"



    prop_size: FloatProperty(
        name="挤出大小",
        description="挤出尺寸",
        default=1,
        step=1
    )    


    prop_rotate: FloatProperty(
        name="旋转量 (r)",
        description="挤出边后旋转",
        default=0,
        step=50,
    )    


    prop_steps: IntProperty(
        name="步数 (i)",
        description="步骤数",
        default=1,
        min=0,
    )    


    prop_delta_text: StringProperty(
        name="旋转增量",
        description="旋转变化公式",
        default='r + i * 0.0'
    )        


    prop_twist: FloatProperty(
        name="扭曲 (t)",
        description="扭曲地进行旋转",
    )      


    prop_twist_text: StringProperty(
        name="扭曲增量",
        description="扭曲公式",
        default='t'
    )      



    prop_seed: IntProperty(
        name="随机种",
        description="随机种子",
        default=1,
    )    


    prop_var1: FloatProperty(
        name="变量 1 (v1)",
        description="公式的变量1",
    )      

    prop_var2: FloatProperty(
        name="变量 2 (v2)",
        description="公式的变量2",
    )      



    prop_shift: FloatVectorProperty(
        name="向量移位",
        description="每个步骤移动",
    )    



    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def divedges(self, sel):
        ct = len(sel)
        if ct == 0:
            return [], []
        selall = set(sel)
        base = set(sel)
        ss1 = []
        while True:
            if len(base) == 0:
                break
            e1 = base.pop()
            es = [e1]
            s1 = set()
            for e1 in es:
                s1.add(e1)
                a, b = e1.verts
                ps1 = set(a.link_edges)
                ps2 = set(b.link_edges)
                ps1 = ps1 | ps2
                ps1 = ps1 & selall
                ps1 = ps1 - s1
                for e2 in ps1:
                    if (e2 in es) == False:
                        es.append(e2)
            ss1.append(list(s1))
            base = base - s1
        return ss1


    def div_pset(self, es):
        s1 = set(es)
        hhes = []
        while len(s1) > 0:
            hs = []
            for e1 in s1:
                for v1 in e1.verts:
                    s2 = set(v1.link_edges)
                    s3 = s1 & s2 
                    if len(s3) == 1:
                        hs.append((e1, v1))
                        break
            if len(hs) == 0:
                e1 = list(s1)[0]
                v1 = e1.verts[0]
            else:
                h1 = hs[0]
                e1, v1 = h1
            hes = [v1]
            while True:
                ves2 = set(v1.link_edges)
                ves2 = ves2 & s1
                ves2 = list(ves2)
                if len(ves2) == 0:
                    break
                e1 = ves2[0]
                v1 = e1.other_vert(v1)
                hes.append(v1)
                s1.remove(e1)
            s1 = s1 - set(hes)
            hhes.append(hes)
        return hhes



    def compare_v(self, m1p, p1, p2, hhes):
        t1 = self.face_inner(p1)
        t2 = self.face_inner(p2)
        d1 = t1.angle(m1p)
        d2 = t2.angle(m1p)
        d3 = abs(d2 - d1)
        if d3 < math.radians(0.1):
            for hs in hhes:
                if (p1.vert in hs) and (p2.vert in hs):
                    d1 = hs.index(p1.vert)
                    d2 = hs.index(p2.vert)
                    return d1 < d2
            return True
        res = t1.angle(m1p) > t2.angle(m1p)        
        return res


    def face_inner(self, p1):
        f1 = p1.face
        a = p1.vert
        b = p1.edge.other_vert(a)
        m1 = b.co - a.co
        s1 = f1.normal.cross(m1)
        return s1


    def edges_only_vmap(self, bm, vs, es, vmap):
        mp = None
        if len(es) <= 1:
            mp = Vector((0,0,1))
        else:
            k1 = None
            e1 = None
            e2 = None
            for v1 in vs:
                ves = v1.link_edges
                if len(ves) == 2:
                    e1, e2 = ves
                    if (e1 in es) and (e1 in es):
                        k1 = v1
                        break
            if k1 == None:
                mp = Vector((0,0,1))
            else:
                a, b = e1.verts
                c, d = e2.verts
                # a, b = self.get_edge_vs(svs, e1)
                # c, d = self.get_edge_vs(svs, e2)
                m1 = b.co - a.co
                m2 = d.co - c.co
                m1.normalize()
                m2.normalize()
                mp = m1.cross(m2).normalized()
        for v1 in vs:
            vmap[v1] = mp


    def sortes(self, es):
        es2 = list(es)
        vs = []
        while len(es2) > 0:
            ve = {}
            for e1 in es2:
                for v in e1.verts:
                    if v in ve:
                        ve[v].append(e1)
                    else:
                        ve[v] = [e1]
            if len(ve) == 0:
                return es
            veq = []
            for v in ve:
                # veq.append((len(ve[v]) * 1e+9 + v.co.x * 1e+6 + v.co.y *1e+3 + v.co.z, v))
                veq.append((len(ve[v]), v))
            _, v1 = min(veq, key=lambda e:e[0])
            # v1 = min(ve, key=lambda e:len(ve[e]))            
            vs.append(v1)
            while True:
                ves = v1.link_edges
                v2 = None
                for e1 in ves:
                    if e1 in es2:
                        es2.remove(e1)
                        v2 = e1.other_vert(v1)
                        break
                if v2 == None:
                    break
                v1 = v2
                vs.append(v1)
        return vs
                    

    def make_vmap(self, bm, es):
        vmap = {}
        snall = Vector()
        vs = []
        sns = []        
        for e1 in es:
            vs.extend(e1.verts)    
        vs = list(set(vs))
        for e1 in es:
            ps = e1.link_loops
            if len(ps) == 1:
                p1 = ps[0]
                sn = p1.face.normal
                p2 = p1.link_loop_next
                m1 = p2.vert.co - p1.vert.co
                m2 = sn.cross(m1) * -1
                m2 = m2.normalized()
                for v1 in e1.verts:
                    if v1 in vmap:
                        vmap[v1] = vmap[v1] + m2
                    else:
                        vmap[v1] = m2
            elif len(ps) >= 2:
                p1 = ps[0]
                sn = p1.face.normal.normalized()
                p2 = ps[1]
                sn2 = p2.face.normal.normalized()
                sn.freeze()
                sn2.freeze()
                sns.append(sn)
                sns.append(sn2)

        if len(sns) > 0:
            snsv = list(set(sns))
            sns2 = []
            for s in snsv:
                c = sns.count(s)
                sns2.append((c, s))
            _, snall = max(sns2, key=lambda e:e[0])
            for v1 in vs:
                if (v1 in vmap) == False:
                    vmap[v1] = snall
        if len(vmap) == 0:
            self.edges_only_vmap(bm, vs, es, vmap)
        return vs, vmap


    def eval_fun(self, origin, delta, del_i):
        res = origin
        td = self.prop_twist
        rotd = self.prop_rotate
        v1 = self.prop_var1
        v2 = self.prop_var2
        try:
            pname = {'math':math, 
                'random':random,
                'i': del_i, 
                'r':rotd,
                't':td,
                'v1':v1,
                'v2':v2
                }

            val = eval(delta, pname)
            res = math.radians(val)
        except Exception as e:
            print(e)
        return res





    def get_rotated_vmap(self, es, vs, vmap, hhes, del_i):
        vmap2 = {}
        for v1 in vs:
            vmap2[v1] = Vector()
        # pdelta = delta * self.prop_delta
        rot = math.radians(self.prop_rotate)
        rot = self.eval_fun(rot, self.prop_delta_text, del_i)

        esmap = {}
        for e1 in es:
            a, b = e1.verts
            # a, b = self.get_edge_vs(svs, e1)
            m1p = vmap[a]
            if len(e1.link_loops) == 1:
                p3 = e1.link_loops[0]
                a = p3.vert
                b = e1.other_vert(a)
                mp = b.co - a.co
                
            elif len(e1.link_loops) == 2:
                p1 = e1.link_loops[0]
                p2 = e1.link_loops[1]
                if self.compare_v(m1p, p1, p2, hhes):
                    p3 = p1
                else:
                    p3 = p2
                a = p3.vert
                b = e1.other_vert(a)
                mp = b.co - a.co
            else:
                a, b = e1.verts   
                mp = b.co - a.co

            m1 = vmap[a].normalized()
            m2 = vmap[b].normalized()   
            q1 = Quaternion(mp, rot)
            m1.rotate(q1)
            m2.rotate(q1)
            vmap2[a] = vmap2[a] + m1
            vmap2[b] = vmap2[b] + m2 
            esmap[e1] = (a, b)
        return vmap2, esmap


    def copying(self, bm, es, plen, vmap, vs, esmap, del_i):
        # dbg = Dbg(bm)
        # dbg.line(Vector(), svs[0].co)

        res = bmesh.ops.duplicate(bm, geom=es)
        gmap = res['vert_map']
        shift = Vector(self.prop_shift)
        for v1 in vs:
            v2 = gmap[v1]
            m1 = vmap[v1]
            m1 = m1.normalized()
            v2.co = v2.co + m1 * plen + shift

        emap = res['edge_map']
        es2 = []
        for e1 in es:
            e2 = emap[e1]
            es2.append(e2)

        for e1 in es:
            a, b = esmap[e1]
            c = gmap[a]
            d = gmap[b]
            pp = [b,a,c,d]
            bm.faces.new(pp)

        tt = math.radians(self.prop_twist)
        twist = self.eval_fun(tt, self.prop_twist_text, del_i)
        
        if twist != 0:
            for e1 in es:
                a, b = esmap[e1]
                c = gmap[a]
                d = gmap[b]
                mid1 = (a.co + b.co)/2
                mid2 = (c.co + d.co)/2
                m1 = mid2 - mid1
                p1 = c.co - mid2
                p2 = d.co - mid2
                p1.rotate(Quaternion(m1, twist))
                p2.rotate(Quaternion(m1, twist))
                c.co = p1 + mid2
                d.co = p2 + mid2

        for e1 in es2:
            e1.select = True
        bm.normal_update()

            

    def moving(self, bm, es, hhes, delta):
        if len(es) == 0:
            return
        plen = self.prop_size
        vs, vmap = self.make_vmap(bm, es)
        vmap, esmap = self.get_rotated_vmap(es, vs, vmap, hhes, delta)
        self.copying(bm, es, plen, vmap, vs, esmap, delta)





    # def get_edge_vs(self, svs, e1):
    #     a, b = e1.verts
    #     p1 = svs.index(a)
    #     p2 = svs.index(b)
    #     if p1 < p2:
    #         return a, b
    #     else:
    #         return b, a


    def process_proc(self, bm, delta):
        sel = [v for v in bm.edges if v.select]
        ess = self.divedges(sel)
        for e1 in sel:
            e1.select = False
        for es in ess:
            # svs = self.sortes(es)
            hhes = self.div_pset(es)
            self.moving(bm, es, hhes, delta)


    def process(self, context):
        bm = self.get_bm()
        random.seed(self.prop_seed)
        for i in range(self.prop_steps):
            self.process_proc(bm, i)
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

        self.prop_steps = 1

        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}



