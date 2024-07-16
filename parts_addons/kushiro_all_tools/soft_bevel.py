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

import itertools
import numpy as np


class SoftBevelOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.soft_bevel_operator"
    bl_label = "Soft Bevel —— 面软倒角"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "对选择的面进行倒角，自动合并倒角出现的破面情况"
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="扩展大小",
        description="扩展大小",
        default=0.05,
        step=0.2,
        min=0
    )    


    prop_cut: IntProperty(
        name="切割次数",
        description="切割次数",
        default=1,
        min=1
    )     


    prop_inner_margin: FloatProperty(
        name="内边距",
        description="内边距",
        default=0.01,
        step=0.1,
        min=0
    )     

    # prop_round: FloatProperty(
    #     name="Rounding",
    #     description="The rounding of bevel area",
    #     default=0.7,        
    #     min=0,
    #     max=1.0
    # )    

    prop_fix: BoolProperty(
        name="修复损坏的边缘",
        description="删除零长度的边",
        default=True,
    )            
 
    prop_merge: BoolProperty(
        name="倒角后合并",
        description="倒角后合并顶点",
        default=False,
    )            
 
    prop_offset: IntProperty(
        name="便宜量",
        description="增加偏移以获得更大的安全检查距离",
        default=0,
        min = 0
    )     


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def bevel3(self, bm, es):  
        ths = 0.00001  
        cut = self.prop_cut
        if cut > 1:
            cut = 2

        if self.prop_fix:
            es = self.merge_fix(bm, es)

        res = bmesh.ops.bevel(bm, geom=es, offset=ths, offset_type='OFFSET', affect='EDGES',
                profile=0.5, segments=cut, clamp_overlap=False)                    
        fs2 = list(res['faces'])        
        es2 = list(res['edges'])
        esinner, esouter = self.get_es_set(es2, fs2)
        fsa, fsb = self.get_fsa(fs2, esouter)

        fsall = fsa + fsb
        fvmap = self.get_base(bm, fsall, esinner, esouter)        
        if fvmap == None:
            return

        self.moving_test(bm, fvmap, fsall)
        # self.moving_test_fsb(bm, fsa, fsb, esinner, esouter)
        self.smoothing(bm, esinner, esouter, fsall)

        if self.prop_merge:
            self.merging(bm, fsall)
        # for f1 in fs2:
        #     f1.select = True

    def merging(self, bm, fsall):
        vsall = []
        for f1 in fsall:
            vs = [p1.vert for p1 in f1.loops]
            vsall.extend(vs)
            # merge vertice
        vsall = list(set(vsall))
        bmesh.ops.remove_doubles(bm, verts=vsall, dist=0.0001)        



    def moving_test_fsb(self, bm, fsa, fsb, esinner, esouter):
        plen = self.prop_plen
        ps = set()
        for i, f1 in enumerate(fsb):            
            for k, p1 in enumerate(f1.loops):
                if p1.edge in esouter:
                    # p1.edge.select = True
                    ps.add(p1)
        ps = list(ps)

        vmap = {}
        for i, p1 in enumerate(ps):
            p2 = p1.link_loop_next
            p3 = p2.link_loop_next
            p4 = p1.link_loop_prev
            m1 = p3.vert.co - p2.vert.co
            m2 = p4.vert.co - p1.vert.co
            vmap[p1.vert] = m2.normalized() * min(plen, m2.length)
            vmap[p2.vert] = m1.normalized() * min(plen, m1.length)

        step = 20
        # smax = {}
        # for i, p1 in enumerate(ps):
        #     smax[p1.vert] = float('inf')

        pin2 = step
        for s1 in range(step):
            # mask = set()
            for i, p1 in enumerate(ps):
                # j = (i + 1) % len(ps)
                p1e = p1.link_loop_next
                a = vmap[p1.vert] / step * s1
                b = vmap[p1e.vert] / step * s1
                for k, p2 in enumerate(p1.face.loops):
                    # q = (k + 1) % len(ps)
                    p3 = p2.link_loop_next
                    if p1.vert == p2.vert or p1.vert == p3.vert:
                        continue
                    if p1e.vert == p2.vert or p1e.vert == p3.vert:
                        continue

                    pin = self.get_cross_inside(p2.vert.co, p3.vert.co, 
                        p1.vert.co + a, p1e.vert.co + b)
                    if pin != None:
                        pin2 = min(s1, pin2)
                        break
                    
        # pprint(smax)
        for i, p1 in enumerate(ps):
            # a = vmap[p1.vert] / step * min(smax[p1.vert], step)
            a = vmap[p1.vert] / step * max((pin2 - 1), 0)
            p1.vert.co += a






    def moving_test_fsb2(self, bm, fsa, fsb, esinner, esouter):
        plen = self.prop_plen
        ps = set()
        for i, f1 in enumerate(fsb):
            for k, p1 in enumerate(f1.loops):
                if p1.edge in esouter:
                    # p1.edge.select = True
                    ps.add(p1)
        ps = list(ps)
        vmap = {}
        for i, p1 in enumerate(ps):
            p2 = p1.link_loop_next
            p3 = p2.link_loop_next
            p4 = p1.link_loop_prev
            m1 = p3.vert.co - p2.vert.co
            m2 = p4.vert.co - p1.vert.co
            vmap[p1.vert] = m2.normalized() * min(plen, m2.length)
            vmap[p2.vert] = m1.normalized() * min(plen, m1.length)

        step = 20
        # smax = {}
        # for i, p1 in enumerate(ps):
        #     smax[p1.vert] = float('inf')

        pin2 = step
        for s1 in range(step):
            # mask = set()
            for i, p1 in enumerate(ps):
                # j = (i + 1) % len(ps)
                p1e = p1.link_loop_next
                a = vmap[p1.vert] / step * s1
                b = vmap[p1e.vert] / step * s1
                for k, p2 in enumerate(p1.face.loops):
                    # q = (k + 1) % len(ps)
                    p3 = p2.link_loop_next
                    if p1.vert == p2.vert or p1.vert == p3.vert:
                        continue
                    if p1e.vert == p2.vert or p1e.vert == p3.vert:
                        continue

                    pin = self.get_cross_inside(p2.vert.co, p3.vert.co, 
                        p1.vert.co + a, p1e.vert.co + b)
                    if pin != None:
                        pin2 = min(s1, pin2)
                        break
                    
        # pprint(smax)
        for i, p1 in enumerate(ps):
            # a = vmap[p1.vert] / step * min(smax[p1.vert], step)
            a = vmap[p1.vert] / step * max((pin2 - 1), 0)
            p1.vert.co += a
            
                


    def merge_fix(self, bm, es):
        # es2 = []
        # for e1 in es:
        #     if e1.is_valid == False:
        #         continue
        #     if e1.calc_length() < 0.001:
        #         bmesh.ops.pointmerge(bm, verts=e1.verts, merge_co=e1.verts[0].co.copy())
        #     else:
        #         es2.append(e1)
        vs = []
        for e1 in es:
            for v1 in e1.verts:
                vs.append(v1)
        vs = list(set(vs))
        bmesh.ops.remove_doubles(bm, verts=vs, dist=0.0001)
        es2 = [e for e in es if e.is_valid]
        return es2




    def smoothing(self, bm, esinner, esouter, fsall):
        plen = self.prop_plen
        cut = self.prop_cut
        if cut <= 1:
            return        
        
        # outer
        evs = set()
        for e1 in esouter:
            for v1 in e1.verts:
                evs.add(v1)

        # inner all
        vs = set()
        # fsc = set(fsall)
        for e1 in esinner:            
            for v1 in e1.verts:
                if v1 not in evs:
                    vs.add(v1)
                    # vs.select = True
                # if all([f1 not in fsc for f1 in v1.link_faces]):
                #     vs.add(v1)                
                    # v1.select = True
        # vs = list(vs)
        # core
        cens = set()
        for v1 in vs:
            linked = 0
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)
                if v2 in vs:
                    linked += 1
            if len(v1.link_edges) == linked:
                cens.add(v1)
        cens = list(cens)

        # core single side
        cens2 = set()
        for v1 in vs:
            linked = 0
            linked_inner = 0
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)
                if v2 in evs:
                    linked += 1
                elif v2 in vs:
                    linked_inner += 1
            if linked == 2 and linked_inner == 2:
                cens2.add(v1)
        cens2 = list(cens2)

        # side
        sides = set()
        for v1 in cens:
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)
                if v2 not in cens:
                    sides.add(v2)
        sides = list(sides)       
        sub = set()

        # side 1 move
        vmap = {}
        for v1 in sides:
            ms = []            
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)                
                if v2 in vs:                    
                    m1 = v2.co - v1.co
                    m2 = m1.normalized() * min(plen, m1.length/2)
                    # v1.co = v1.co + m2
                    vmap[v1] = m2        
        for v1 in vmap:
            v1.co = v1.co + vmap[v1]            


        # side 1 move 2
        vmap = {}
        for v1 in sides:            
            ms = []
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)                
                if v2 not in vs:                    
                    ms.append(v2.co)
                    sub.add(e1)
            if len(ms) == 0:
                continue
            mv = sum(ms, Vector()) / len(ms)
            vmap[v1] = mv
        for v1 in vmap:
            v1.co = (v1.co + vmap[v1])/2

        # cen move 1
        vmap = {}        
        for v1 in cens:
            ms = []
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)
                if v2 not in cens:
                    ms.append(v2.co)
                    sub.add(e1)
            mv = sum(ms, Vector()) / len(ms)
            vmap[v1] = mv
        round1 = 1.0
        for v1 in vmap:
            v1.co = v1.co * (1.0 - round1) + vmap[v1] * round1

        # cen move 2
        vmap = {}
        for v1 in cens2:
            ms = []
            for e1 in v1.link_edges:
                v2 = e1.other_vert(v1)
                if (v2 not in cens2) and (v2 not in vs):
                    ms.append(v2.co)
                    sub.add(e1)
            if len(ms) > 0:
                vmap[v1] = sum(ms, Vector()) / len(ms)
        round2 = 0.5
        for v1 in vmap:
            v1.co = v1.co * (1.0 - round2) + vmap[v1] * round2        

        sub = list(sub)
        if cut > 2:
            cut = cut - 2
            res = bmesh.ops.subdivide_edges(bm, edges=sub, cuts=cut, use_grid_fill=True, smooth=0.5)
  



    def point_triangle(self, k, a, b, c):
        v0 = b - a
        v1 = c - a
        v2 = k - a        
        d00 = v0.dot(v0)
        d01 = v0.dot(v1)
        d11 = v1.dot(v1)
        d20 = v2.dot(v0)
        d21 = v2.dot(v1)        
        denom = d00 * d11 - d01 * d01
        if denom == 0:
            # return True
            return False
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1 - v - w        
        return (u >= 0) and (v >= 0) and (w >= 0)
        

    def is_point_quad(self, k1, v1, v2, v3, v4):        
        verts = [v1, v2, v3, v4]
        triangle1 = (verts[0], verts[1], verts[2])
        triangle2 = (verts[2], verts[3], verts[0])        
        return self.point_triangle(k1, *triangle1) or self.point_triangle(k1, *triangle2)


    def is_point_face(self, k1, f1):        
        verts = [v.co for v in f1.verts]        
        triangle1 = (verts[0], verts[1], verts[2])
        triangle2 = (verts[2], verts[3], verts[0])        
        return self.point_triangle(k1, *triangle1) or self.point_triangle(k1, *triangle2)



    def get_vs2(self, bm, f1, base, inv, stage, plen2, ths, sel, mod, fid, sid):
        vs2 = [None] * len(f1.loops)
        for k, p1 in enumerate(f1.loops):                   
            k2 = (k + 1) % len(f1.loops)                    
            k3 = (k - 1) % len(f1.loops)
            b1 = base[k]
            b2 = base[k2]
            b3 = base[k3]             
            s1 = min(stage[k] -1,sid) + mod
            s2 = min(stage[k3] -1,sid) + mod
            if s1 < 0:
                s1 = 0
            if s2 < 0:
                s2 = 0
            in1 = inv[k] * (s1 * plen2) + inv[k].normalized() * ths
            in2 = inv[k3] * (s2 * plen2) + inv[k3].normalized() * ths
            if sel[k] == False:
                in1 = Vector()
            if sel[k3] == False:
                in2 = Vector()

            # mid = self.mid_line((b2-b1), (b3-b1), f1.normal) * 0.02
            # debug.line_edge(bm, b1+mid, b1+mid + in1)  
            # mid = self.mid_line((b2-b1), (b3-b1), f1.normal) * 0.05
            # debug.line_edge(bm, b1+mid, b1+mid + in1.normalized() * 0.5)   
            # print(in1.length)         
            # debug.line_edge(bm, b1+mid, b2+mid)

            # debug.line_edge(bm, b1+in1, b2+in1)
            # debug.line_edge(bm, b3+in2, b1+in2)

            m1 = b1 + in1 - (b2 + in1)
            m2 = b3 + in2 - (b1 + in2)
            if abs(m1.normalized().dot(m2.normalized())) > 0.99:
                vs2[k] = b1 + in1
                continue

            pin = self.get_cross(b1 + in1, b2 + in1, b3 + in2, b1 + in2)       

            # if fid == self.prop_k:
            #     mid = self.mid_line((b2-b1), (b3-b1), p1.face.normal) * 0.05
            #     debug.line_edge(bm, b1+mid, b1+mid + in1.normalized() * 0.5)
            #     debug.line_edge(bm, b1 + in1, b2 + in1)
            #     debug.line_edge(bm, b3 + in2, b1 + in2)
            #     if pin != None:
            #         debug.line_edge(bm, b1, pin)

            if pin == None:
                vs2[k] = b1 + in1                
            else:
                vs2[k] = pin
        return vs2    
    


    def set_mask_inside(self, bm, mask, f1, vs2, base, k, k2, b1, b2, v1, v2):
        for j1, p2 in enumerate(f1.loops):
            if j1 == k or j1 == k2:
                continue
            v3 = vs2[j1]
            b3 = base[j1]
            m1 = (b2 - b1).normalized()
            m2 = v1 - b1
            # m3 = (v2 - b1).normalized()
            # m3 = (v2 - b2).normalized()
            # m4 = (v3 - b1).normalized()            
            
            # debug.line_edge(bm, b2, b2 + (v2-b2).normalized())
            # debug.line_edge(bm, b1, b1 + (v1-b1).normalized())

            if abs(m2.normalized().dot(m1)) > 0.99:
                # or \
                # abs(m3.dot(m1)) > 0.99:
                # or abs(m4.dot(m1)) > 0.99:
                # debug.line_edge(bm, v1, b1)
                # debug.line_edge(bm, b2, b1)
                continue            
            # m5 = v1 - b1
            m6 = v2 - b2
            if m2.length < 0.001 or m6.length < 0.001:
                continue

            if self.is_point_quad(v3, b1, b2, v2, v1):                 
                mask[k] = 1
                # mask[k2] = 1
                mask[j1] = 1
                j2 = (j1 - 1) % len(f1.loops)
                mask[j2] = 1




    def get_inv(self, f1, base, sn):
        plen = self.prop_plen
        inv = [None] * len(f1.loops)
        for k, p1 in enumerate(f1.loops):
            k2 = (k + 1) % len(f1.loops)
            b1 = base[k]
            b2 = base[k2]
            m1 = (b2 - b1).normalized()
            inv[k] = m1.cross(sn).normalized() * -1
        return inv


    def set_stage(self, bm, steps, f1, base, inv, stage, plen2, ths, sel, fid):
        for st in range(steps):
            # vs2 = [None] * len(f1.loops)
            mask = [0] * len(f1.loops)
            # vsall.append(vs2)
            vs2 = self.get_vs2(bm, f1, base, inv, stage, plen2, ths, 
                sel, 0, fid, st + self.prop_offset - 1)

            for k, p1 in enumerate(f1.loops):
                k2 = (k + 1) % len(f1.loops)
                b1 = base[k]
                b2 = base[k2]
                v1 = vs2[k]
                v2 = vs2[k2]
                # debug.line_edge(bm, b1, v1)
                # debug.line_edge(bm, b2, v2)
                # debug.line_edge(bm, v1, v2)

                cross = self.check_cross(bm, f1, vs2, base, k, k2, b1, b2, v1, v2)
                if cross:
                    mask[k] = 1
                    # mask[k2] = 1
                    continue

                self.set_mask_inside(bm, mask, f1, vs2, base, k, k2, b1, b2, v1, v2)


            for k, p1 in enumerate(f1.loops):
                if mask[k] == 1:
                    stage[k] = min(st, stage[k])
                # if mask[k] == 0:
                #     stage[k] += 1        
                # else:
                #     stage[k] -= 1


    def check_cross(self, bm, f1, vs2, base, k, k2, b1, b2, v1, v2):
        for j1, p2 in enumerate(f1.loops):
            j2 = (j1 + 1) % len(f1.loops)
            if j1 == k or j1 == k2:
                continue
            if j2 == k or j2 == k2:
                continue
            b3 = base[j1]
            b4 = base[j2]
            pin = self.get_cross_inside(b1, v1, b3, b4)
            if pin != None:
                return True
            # pin = self.get_cross_inside(b2, v2, b3, b4)
            # if pin != None:
            #     return True
        return False
            



        
    def check_collapse(self, f1, vs3, base, plen2):
        for k, p1 in enumerate(f1.loops):
            k2 = (k + 1) % len(f1.loops)
            m1 = vs3[k2] - vs3[k]
            m2 = base[k2] - base[k]
            if m1.length < plen2 or m1.normalized().dot(m2.normalized()) <= 0:
                pin = (vs3[k2] + vs3[k])/2
                vs3[k] = pin
                vs3[k2] = pin        


    def check_lines(self, bm, f1, base, inv):
        for k, p1 in enumerate(f1.loops):
            b1 = base[k]
            b2 = base[(k+1) % len(f1.loops)]
            b3 = base[(k-1) % len(f1.loops)]
            in1 = inv[k]
            mid = self.mid_line((b2-b1), (b3-b1), p1.face.normal) * 0.05
            # debug.line_edge(bm, b1+mid, b1+mid + in1.normalized() * 0.5)          


    def moving_test(self, bm, fvmap, fsall):   
        steps = 20
        ths = self.prop_inner_margin
        plen = self.prop_plen
        plen2 = plen / steps
        vmap = {}
        for fid, f1 in enumerate(fsall):            
            base, sel = fvmap[fid]      
            stage = [steps+1] * len(f1.loops)
            sn = f1.normal            
            inv = self.get_inv(f1, base, sn)
            # self.check_lines(bm, f1, base, inv)
            self.set_stage(bm, steps, f1, base, inv, stage, plen2, ths, sel, fid)            
            vs3 = self.get_vs2(bm, f1, base, inv, stage, plen2, 0, sel, -1, fid, steps)
            self.check_collapse(f1, vs3, base, plen2)            
                       
            for k, p1 in enumerate(f1.loops):
                pin = vs3[k]
                # p1.vert.co = pin  
                if p1.vert not in vmap:
                    am = (pin - p1.vert.co).length
                    vmap[p1.vert] = (am, pin)
                else:                    
                    am1, k1 = vmap[p1.vert]
                    am2 = (pin - p1.vert.co).length
                    if am2 < am1:
                        vmap[p1.vert] = (am2, pin)
                    # m1 = (pin - p1.vert.co).length
                    # m2 = (k1 - p1.vert.co).length
                    # if m1 < m2:
                    #     vmap[p1.vert] = pin
        
        for v1 in vmap:
            am, pin = vmap[v1]
            v1.co = pin

        for f1 in fsall:
            f1.normal_update()

                

        
                        




    def convert_base(self, f1):
        base = []
        c1 = f1.calc_center_median()        
        for p1 in f1.loops:
            a = p1.vert.co
            res = a - (a - c1).dot(f1.normal) * f1.normal
            base.append(res)
        return base


    def get_base(self, bm, fsa, esinner, esouter):
        fvmap = []
        for f1 in fsa:
            base = self.convert_base(f1)
            sel = [False] * len(f1.loops)
            for i, p1 in enumerate(f1.loops):
                res = p1.edge in esouter
                sel[i] = res

            fvmap.append((base, sel))
        return fvmap





    def get_es_set(self, es2, fs2):
        esinner = set()
        esouter = set()
        for e1 in es2:
            # e1.select = True
            if len(e1.link_faces) < 2:
                continue
            a, b = e1.link_faces
            if a in fs2 and b in fs2:
                esinner.add(e1)
            else:
                esouter.add(e1)
                # e1.select = True
        return esinner, esouter    
                

    def get_fsa(self, fs2, esouter):
        fsa = set()
        fsb = set()
        for e1 in esouter:
            # e1.select = True
            for f1 in e1.link_faces:
                if f1 not in fs2: 
                    inc = [e for e in f1.edges if e in esouter]
                    if len(inc) > 1:
                        fsa.add(f1)  
                    else:
                        fsb.add(f1)
        return list(fsa), list(fsb)
        


                    
    def get_edge(self, p1, es):
        for e1 in es:
            for p2 in e1.link_loops:
                if p2.vert == p1.vert:
                    return p2
        return None


    def is_same_vert(self, e1, e2):
        a, b = e1.verts
        c, d = e2.verts
        if a == c or a == d or b == c or b == d:
            return True
        return False    



    def inside(self, p1, v1, v2):
        m1 = p1 - v1
        m2 = p1 - v2
        m3 = v2 - v1
        if (m1.length + m2.length) - m3.length < 0.001:
            return True
        else:
            return False

    def get_cross_inside(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        if (p2 - p1).length < 0.001:
            if self.inside(p1, v1, v2) and self.inside(p1, v3, v4):
                return p1
        else:
            return None
        
    def get_cross(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        return (p1 + p2) / 2       


        
        
    def mid_line(self, m1, m2, sn):
        fm1 = sn.cross(m1.normalized())
        fm2 = m2.normalized().cross(sn)
        m3 = (fm1 + fm2).normalized()
        return m3



    def get_other_face(self, e1, f1):
        if len(e1.link_faces) != 2:
            return None
        f2 = e1.link_faces[0]
        if f2 == f1:
            f2 = e1.link_faces[1]
        return f2
        

    def process(self, context):
        bm = self.get_bm() 
        sel = [e1 for e1 in bm.edges if e1.select]
        self.bevel3(bm, sel)

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
        return selecting and editing and is_face_mode


    def invoke(self, context, event):                 
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


