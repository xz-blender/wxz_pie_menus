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
import bmesh.utils

from mathutils import Matrix, Vector, Quaternion
from bpy_extras import view3d_utils

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
from . import gui


class Chain:
    def __init__(self) -> None:
        self.loop = None
        self.next = None
        self.prev = None
        self.head = False
        self.run = False



class SlideEdgeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.slide_edge_operator"
    bl_label = "Slide Edge —— 滑移边线"
    bl_options = {"REGISTER", "UNDO", 'GRAB_CURSOR', 'BLOCKING'}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="滑移大小",
        description="定义滑动大小",
        default=0.04,
        step=0.5,        
    )    


    prop_select: BoolProperty(
        name="选择结果",
        description="选择结果循环",
        default=False,
    )    

    prop_original_select: BoolProperty(
        name="选择原始边",
        description="选择原始边",
        default=False,
    )    




    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def restore(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        me = bpy.context.active_object.data
        self.bm2.to_mesh(me)
        bpy.ops.object.mode_set(mode='EDIT')          
               


    def process_sub(self, bm, flip):
        sel = [e1 for e1 in bm.edges if e1.select]
        sel = [e1 for e1 in sel if len(e1.link_faces) > 0]        
        ess = self.div_set(sel)        
        for es in ess:          
            # print(len(es))  
            if len(es) == 0:
                continue       
            elif len(es) == 1:
                self.shift_one(bm, es)
            else:
                ends = self.get_end(es)        
                # print(len(ends))
                endcount = len(ends)
                if endcount == 0:
                    ps1 = self.get_flow_circle(es, True)
                    ps2 = self.get_flow_circle(es, False)
                    ps = self.get_near_ps(ps1, ps2)

                    if ps == None or len(ps) == 0:
                        continue                                     
                    self.cut_break_circle(bm, ps, es)
                    
                elif endcount == 1:        
                    ps = self.get_flow(es, ends[0])
                    if ps == None or len(ps) == 0:
                        continue            
                    self.cut_break(bm, ps, es)

                elif endcount == 2:
                    # ps = self.get_flow(es, ends[0])
                    # if len(ps) == 0 or flip:                        
                    #     ps = self.get_flow(es, ends[1])
                    ps1 = self.get_flow(es, ends[0])
                    ps2 = self.get_flow(es, ends[1])
                    ps = self.get_near_ps(ps1, ps2)

                    if ps == None or len(ps) == 0:
                        continue             
                    self.cut_break(bm, ps, es)
        

    def get_near_ps(self, ps1, ps2):   
        if ps1 == None or ps2 == None:
            return None

        if len(ps1) == 0:
            return ps2
        if len(ps2) == 0:
            return ps1

        v1 = Vector()
        for p1 in ps1:
            p2 = p1.loop.link_loop_prev
            v1 = v1 + p2.vert.co
        v1 = v1 / len(ps1)
        v2 = Vector()
        for p1 in ps2:
            p2 = p1.loop.link_loop_prev
            v2 = v2 + p2.vert.co
        v2 = v2 / len(ps2)
        d1 = self.pro2d(v1)
        d2 = self.pro2d(v2)
        if d2.x > d1.x:
            ps = ps2
        else:
            ps = ps1

        if self.prop_plen < 0:
            if ps == ps1:
                ps = ps2
            elif ps == ps2:
                ps = ps1         
        return ps   



    def process(self, context, cur=Vector()):        
        self.restore()
        # self.restore2()
        bm = self.get_bm()
        self.process_sub(bm, False)
        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me) 

        # bpy.ops.object.mode_set(mode='OBJECT')
        # me = bpy.context.active_object.data
        # bm.to_mesh(me)
        # bpy.ops.object.mode_set(mode='EDIT')          



    def get_shift_one_positive(self, e1):
        ps = e1.link_loops
        if len(ps) == 1:
            return ps[0]

        p1 = ps[0]
        p2 = ps[1]
        b1 = p1.link_loop_prev
        b2 = p2.link_loop_prev
        d1 = self.pro2d(b1.vert.co)
        d2 = self.pro2d(b2.vert.co)
        plen = self.prop_plen
        if d1.x > d2.x:
            ps = p1
        else:
            ps = p2
        if plen < 0:
            if ps == p1:
                ps = p2
            else:
                ps = p1
        return ps


    def shift_one(self, bm, es):
        plen = self.prop_plen
        e1 = es[0]
        if len(e1.link_loops) == 0:
            return
        e1.select = False

        plen = abs(plen)
        p1 = self.get_shift_one_positive(e1)
        
        p2 = p1.link_loop_next
        k1 = p1.link_loop_prev
        m1 = k1.vert.co - p1.vert.co
        # c1 = m1.normalized() * plen + p1.vert.co

        d1 = p1.calc_angle()- math.radians(90)       
        # d1 = deg/2
        h1 = math.cos(d1)        
        if h1 == 0:
            d2 = plen / 0.000001
        else:
            d2 = plen / h1   

        d1 = min(k1.edge.calc_length(), d2)
        c1 = m1.normalized() * d1 + p1.vert.co
        self.cut_forward_bisect(bm, k1.edge, c1)
        k2 = p2.link_loop_next
        m2 = k2.vert.co - p2.vert.co
        # c2 = m2.normalized() * plen + p2.vert.co

        d1 = p2.calc_angle()- math.radians(90)       
        # d1 = deg/2
        h1 = math.cos(d1)        
        if h1 == 0:
            d2 = plen / 0.000001
        else:
            d2 = plen / h1   

        d2 = min(p2.edge.calc_length(), d2)
        c2 = m2.normalized() * d2 + p2.vert.co
        self.cut_forward_bisect(bm, p2.edge, c2)
        k1 = p1.link_loop_prev
        k2 = p2.link_loop_next
        e2 = self.chop_line(bm, k1.vert, k2.vert)
        if self.prop_select:
            e2.select = True
        # pvs = [(c1,c2), (c2,c2)]
        # return pvs
        if self.prop_original_select:
            e1.select = True




    def extra_geo(self, bm, es):       
        has_bound = False
        for e1 in es:
            for v1 in e1.verts:
                for e2 in v1.link_edges:
                    if e2.is_boundary:
                        has_bound = True
                        break

        if has_bound == False:
            return None

        es2 = []
        for e1 in bm.edges:
            if e1.is_boundary:
                es2.append(e1)        
        
        res = bmesh.ops.extrude_edge_only(bm, edges=es2)
        gs = res["geom"]
        gs = [e for e in gs if isinstance(e, bmesh.types.BMFace)]
        return gs
        # pprint.pprint(gs)


    def cut_break(self, bm, ps, es):
        gs = self.extra_geo(bm, es)
        res = bmesh.ops.split_edges(bm, edges=es)
        eall = res['edges']
        head = ps[0]
        tail = ps[-1]
        esel = []
        for p in ps:            
            e1 = p.loop.edge
            esel.append(e1)

        pall = set(eall)
        psel = set(esel)
        pout = pall - psel
        for e1 in bm.edges:
            e1.select = False   

        psel = list(psel)
        pout = list(pout)

        pvs = self.process_side(bm, psel, pout, head, tail, ps)

        if gs != None:
            bmesh.ops.delete(bm, geom=gs, context='FACES')

        if self.prop_original_select:
            for e1 in pout:
                e1.select = True

        # return pvs


    def cut_break_circle(self, bm, ps, es):
        gs = self.extra_geo(bm, es)
        res = bmesh.ops.split_edges(bm, edges=es)
        eall = res['edges']

        head = ps[0]
        tail = ps[-1]

        esel = []
        for p in ps:
            e1 = p.loop.edge
            esel.append(e1)

        pall = set(eall)
        psel = set(esel)
        pout = pall - psel
        for e1 in bm.edges:
            e1.select = False   

        psel = list(psel)
        pout = list(pout)
        pvs = self.process_side_circle(bm, psel, pout, head, tail, ps)

        if self.prop_original_select:
            for e1 in pout:
                e1.select = True

        if gs != None:
            bmesh.ops.delete(bm, geom=gs, context='FACES')
        return pvs 



    def process_side(self, bm, psel, pout, head, tail, ps1):
        plen = abs(self.prop_plen)
        # p1 = self.get_head_side(psel, pout, head)
        p1 = self.cut_head_side(bm, head.loop, plen)
        p2 = self.cut_tail_side(bm, tail.loop, plen)

        pvs = self.calc_pvs2(plen, ps1)   

        bmesh.ops.bridge_loops(bm, edges=psel + pout)

        self.merge_both(bm, head, tail, psel, p1, p2)
        
        self.move_pvs(bm, pvs, plen)

        bm.normal_update()
        return pvs
        



    def calc_pvs2(self, plen, ps1):
        pvs = []
        pselect = self.prop_select
        for p1 in ps1[1:]:
            c1 = self.get_dir(p1, plen)
            pvs.append((p1.loop.vert, c1))
            if pselect:
                p1.loop.edge.select = True
        return pvs


    def calc_pvs2_circle(self, plen, ps1):
        pvs = []
        pselect = self.prop_select
        for p1 in ps1:
            c1 = self.get_dir(p1, plen)
            pvs.append((p1.loop.vert, c1))
            if pselect:
                p1.loop.edge.select = True
        return pvs
                    
            





    def process_side_circle(self, bm, psel, pout, head, tail, ps1):
        plen = abs(self.prop_plen)
        # p1 = self.get_head_side(psel, pout, head)
        # p1 = self.cut_head_side(bm, head.loop, plen)
        # p2 = self.cut_tail_side(bm, tail.loop, plen)

        pvs = self.calc_pvs2_circle(plen, ps1)   

        bmesh.ops.bridge_loops(bm, edges=psel + pout)
        # self.merge_both(bm, head, tail, psel, p1, p2)        
        self.move_pvs(bm, pvs, plen)
        bm.normal_update()
        return pvs


            

    def get_dir(self, p1, plen, neg=False):        
        p2 = p1.prev
        p3 = p1.next
        if p2 == None:            
            px = p1.loop.link_loop_prev
            m1 = px.vert.co - p1.loop.vert.co
            return m1.normalized() * plen + p1.loop.vert.co
        else:            
            # pr = self.get_loop(p1.loop.vert, p2.loop.edge)
            # if pr == None:
            #     return self.calc_zero_inner(p1, p2, p3, plen, neg)
            rod = self.get_round_between_half(p1)
            if len(rod) == 0:                
                return self.calc_zero_inner(p1, p2, p3, plen, neg)
            elif len(rod) == 1:
                px = p1.loop.link_loop_prev
                m1 = px.vert.co - p1.loop.vert.co                
                d1 = self.calc_single_len(p1, plen)                
                # return m1.normalized() * d1 + p1.loop.vert.co
                d2 = min(px.edge.calc_length(), d1)                
                return m1.normalized() * d2 + p1.loop.vert.co
            else:                
                return self.calc_zero_inner(p1, p2, p3, plen, neg)


    def calc_single_len(self, p1, plen):
        p2 = p1.prev        
        if p2 == None:
            return plen
        px = p2.loop
        m1 = px.vert.co - p1.loop.vert.co
        v1 = p1.loop.vert
        m2 = p1.loop.edge.other_vert(v1).co - v1.co
        
        sn1 = p1.loop.face.normal
        sn2 = p2.loop.face.normal

        if sn1.length !=0 and sn2.length != 0:
            if sn1.angle(sn2) > math.radians(5):                
                return plen

        sn = (sn1 + sn2).normalized()
        if sn.length == 0:
            sn = sn1        

        deg = self.get_angle(m1, m2, sn)                
        d1 = deg / 2 - math.radians(90)        
        # d1 = deg/2
        h1 = math.cos(d1)        
        if h1 == 0:
            d2 = plen / 0.000001
        else:
            d2 = plen / h1
        return d2
        




    def get_round_between_half(self, p1):
        ps = []        
        for p in p1.loop.vert.link_loops:
            if p != p1.loop:
                ps.append(p)           
        return ps





    def calc_zero_inner(self, p1, p2, p3, plen, neg):
        sn1 = p1.loop.face.normal
        sn2 = p2.loop.face.normal
        sn = (sn1 + sn2).normalized()
        if sn.length == 0:
            sn = sn1

        v1 = p1.loop.vert
        if p3 == None:
            a = p1.loop.edge.other_vert(v1)
        else:
            a = p3.loop.vert
        b = p2.loop.vert
        m1 = a.co - v1.co
        m2 = b.co - v1.co
        # m3 = m1.normalized() + m2.normalized()
        # c1 = m3.normalized() * plen + v1.co
        deg = self.get_angle(m1, m2, sn)                        
        d1 = deg / 2 - math.radians(90)
        if math.cos(d1) == 0:
            d2 = plen / 0.000001
        else:
            d2 = plen / math.cos(d1)            
        m1.rotate(Quaternion(sn, deg/2))

        if neg:
            d2 = d2 * -1        
        c1 = m1.normalized() * d2 + v1.co
        return c1




    def get_mid(self, v1, pvs, plen, neg=False):
        vs = []
        for e1 in v1.link_edges:            
            v2 = e1.other_vert(v1)
            if v2 in pvs:
                vs.append(v2)
        if len(vs) == 2:
            a, b = vs
            m1 = a.co - v1.co
            m2 = b.co - v1.co
            # m3 = m1.normalized() + m2.normalized()
            # c1 = m3.normalized() * plen + v1.co
            deg = self.get_angle(m1, m2)            
            sn = m1.cross(m2).normalized()
            d1 = deg / 2 - math.radians(90)
            if math.cos(d1) == 0:
                d2 = plen / 0.000001
            else:
                d2 = plen / math.cos(d1)            
            m1.rotate(Quaternion(sn, deg/2))

            if neg:
                d2 = d2 * -1
            c1 = m1.normalized() * d2 + v1.co
            return c1
        return v1.co    


    def move_pvs(self, bm, pvs, plen):
        for v1, v2 in pvs:
            if v1.is_valid:
                v1.co = v2


    def get_outer_edge(self, p1):
        f1 = p1.face
        es = list(f1.edges)
        for e1 in p1.vert.link_edges:
            if (e1 in es) == False:
                return e1
        return None


    def sel_group(self, bm, psel):
        for e1 in bm.edges:
            e1.select = False

        for e1 in psel:
            e1.select = True


    def open_loop(self, v1):        
        p1 = self.get_bound(v1, None)
        if p1 == None:
            return None
        ps = [p1]
        for px in ps:
            v2 = px.vert
            v3 = px.edge.other_vert(v2)
            px2 = self.get_bound(v3, px.edge)
            if px2 == None:
                continue
            if (px2 in ps) == False:
                ps.append(px2)
        vs = [p.vert for p in ps]
        return vs
        

    def get_bound(self, v1, exp):
        for p1 in v1.link_loops:
            if p1.edge.is_boundary and p1.edge != exp:
                return p1
        return None        


    def merge_both(self, bm, head, tail, psel, p1, p2):
        tail2 = tail.loop.link_loop_next
        ks1 = self.open_loop(head.loop.vert)
        ks2 = self.open_loop(tail2.vert)

        if ks1 == None or ks2 == None:
            return None
        if len(ks1) == 0 or len(ks2) == 0:
            return None        

        s1 = p1.face.smooth
        s2 = p2.face.smooth
        res = bmesh.ops.contextual_create(bm, geom=ks1)
        if len(res['faces']) > 0:
            f1 = res['faces'][0]
            f1.smooth = s1

        res = bmesh.ops.contextual_create(bm, geom=ks2)
        if len(res['faces']) > 0:
            f1 = res['faces'][0]
            f1.smooth = s2

        # res['faces']

        pe1 = self.get_outer_edge(head.loop)
        pe2 = self.get_outer_edge(tail2)

        if pe1 == None or pe2 == None:
            return None

        p3 = p1.link_loop_prev

        edges1 = list(set([pe1, pe2]))
        verts1 = list(set([head.loop.vert, tail2.vert]))
        bmesh.ops.dissolve_edges(bm, edges=edges1)
        bmesh.ops.dissolve_verts(bm, verts=verts1)

        # p1.edge.select = True
        if self.prop_select:
            p2.link_loop_prev.edge.select = True
            p3.link_loop_next.edge.select = True

 



    def cut_tail_side(self, bm, p1, plen):
        p2 = p1.link_loop_next
        p3 = p2.link_loop_next
        m1 = p3.vert.co - p2.vert.co

        d1 = p2.calc_angle()- math.radians(90)       
        # d1 = deg/2
        h1 = math.cos(d1)        
        if h1 == 0:
            d2 = plen / 0.000001
        else:
            d2 = plen / h1        
        
        d1 = min(d2, p2.edge.calc_length())
        c1 =(m1.normalized() * d1) + p2.vert.co

        self.cut_forward_bisect(bm, p2.edge, c1)
        p3 = p2.link_loop_next
        bmesh.ops.split_edges(bm, edges=[p2.edge])
        p3 = p2.link_loop_next
        return p3



    def cut_head_side(self, bm, p1, plen):
        p2 = p1.link_loop_prev
        m1 = p2.vert.co - p1.vert.co        

        d1 = p1.calc_angle()- math.radians(90)       
        # d1 = deg/2
        h1 = math.cos(d1)        
        if h1 == 0:
            d2 = plen / 0.000001
        else:
            d2 = plen / h1

        d1 = min(d2, p2.edge.calc_length())
        c1 =(m1.normalized() * d1) + p1.vert.co
        self.cut_forward_bisect(bm, p2.edge, c1)
        p2 = p1.link_loop_prev
        bmesh.ops.split_edges(bm, edges=[p2.edge])
        p2 = p1.link_loop_prev
        return p2




    
    def get_matrix(self, m1, m2, m3, cen):
        if m1.length == 0 or m2.length == 0 or m3.length == 0:
            return Matrix.Identity(4)            
        m = Matrix.Identity(4)        
        m[0][0:3] = m1.normalized()
        m[1][0:3] = m2.normalized()
        m[2][0:3] = m3.normalized()
        m[3][0:3] = cen.copy()
        m = m.transposed()
        return m    


    def get_angle(self, n1, n2, sn):
        m1 = n1.normalized()
        m2 = n2.normalized()
        # sn = m1.cross(m2)
        k1 = sn.cross(m1)
        vm = self.get_matrix(m1, k1, sn, Vector())
        vm2 = vm.inverted()
        x2 = vm2 @ m2
        if x2.length == 0:
            return 0
        deg = x2.angle(Vector((1,0,0)))        
        if x2.y < 0:
            deg = (math.pi * 2) - deg
        return deg




    def draw_loop(self, p):
        c1 = p.vert.co
        p3 = p.link_loop_prev
        m1 = p3.vert.co - c1
        m1 = m1.normalized() * 0.01 + c1
        p4 = p.link_loop_next
        m2 = p4.vert.co - c1
        m2 = m2.normalized() * 0.01 + c1
        gui.lines += [m1, m2]




    def mid_line(self, m1, m2, sn):
        fm1 = sn.cross(m1.normalized())
        fm2 = m2.normalized().cross(sn)
        m3 = (fm1 + fm2).normalized()
        return m3


    def get_round_between(self, p1, p2):
        plen = len(p1.vert.link_loops)
        ps = []
        pc = p1
        for i in range(plen):            
            pc = self.rad_next(pc)
            if pc == p1 or pc == p2:
                break
            ps.append(pc)

        return ps
        

    def rad_next(self, p1):
        p2 = p1.link_loop_radial_next   
        p3 = p2.link_loop_next
        return p3


    def sel_ps(self, bm, ps):
        for p in ps:
            p2 = p.link_loop_next
            p2.edge.select = True



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



    def get_flow(self, es, end):
        d1 = end
        ds = [d1]
        found = []
        ps = []        
        for d2 in ds:            
            sel = [e1 for e1 in d2.link_edges if (e1 in es)]
            if len(sel) > 2:
                return None
            sel = [e1 for e1 in sel if ((e1 in found) == False)]
            if len(sel) > 0:
                e1 = sel[0]
                p1 = self.get_loop(d2, e1)
                if p1 == None:
                    continue
                ps.append(p1)
                d3 = e1.other_vert(d2)                    
                ds.append(d3)
                found.append(e1)                
        
        cc = self.make_chain(ps)

        if len(cc) == 0:
            return []

        cc[0].prev = None
        cc[-1].next = None

        # c1 = Chain()
        # c1.prev = cc[-1]        
        # c1.loop = None
        # c1.next = None
        # cc[-1].next = c1
        # cc.append(c1)
        # cc[0].head = True
        return cc
        

    def make_chain(self, ps):
        chain = []
        for p in ps:
            ch = Chain()
            ch.loop = p
            chain.append(ch)

        if len(chain) == 0:
            return []

        chain2 = chain[1:] + [chain[0]]

        for a, b in zip(chain, chain2):
            a.next = b
            b.prev = a
        return chain

    def phash2(self, e1):
        a, b = e1.verts
        m1 = (a.co + b.co)/2
        return m1.z + 100 * m1.y + 10000 * m1.x


    def get_flow_circle(self, es, first):
        es2 = list(es)
        es2 = sorted(es2, key=self.phash2)
        plen = self.prop_plen        
        e1 = es2[0]
        # if len(e1.link_loops) > 1:
        #     if plen < 0:
        #         print('reverse')
        #         p1 = e1.link_loops[1]
        #     else:                
        #         p1 = e1.link_loops[0]
        # else:
        #     p1 = e1.link_loops[0]
        
        p1 = e1.link_loops[0]
        end = p1.vert
        ds = [end]
        found = []
        ps = []        
        for d2 in ds:            
            sel = [e1 for e1 in d2.link_edges if (e1 in es)]
            if len(sel) > 2:
                return None
            sel = [e1 for e1 in sel if ((e1 in found) == False)]
            if len(sel) > 0:
                if len(sel) == 1:
                    e1 = sel[0]
                elif len(sel) > 1:

                    if first:
                        s1 = sel[0]
                        s2 = sel[1]
                    else:
                        s1 = sel[1]
                        s2 = sel[0]

                    e1 = s1

                    # if plen < 0:
                    #     e1 = s2
                    # else:
                    #     e1 = s1
                # if plen < 0:
                #     if len(sel) == 1:
                #         e1 = sel[0]
                #     else:
                #         e1 = sel[1]
                # else:
                #     e1 = sel[0]
                p1 = self.get_loop(d2, e1)   
                if p1 == None:
                    continue
                ps.append(p1)
                d3 = e1.other_vert(d2)                    
                ds.append(d3)
                found.append(e1)                

        cc = self.make_chain(ps)        
        # cc[0].head = True
        return cc



                    
    def get_loop(self, v1, e1):
        for p in e1.link_loops:
            if p.vert == v1:
                return p
        return None
            

    def get_end(self, es):
        vs = set()
        for e1 in es:
            a, b = e1.verts
            vs.add(a)
            vs.add(b)
        vs = list(vs)
        ends = []
        for v1 in vs:
            cc = 0
            for e1 in v1.link_edges:
                if e1 in es:
                    cc += 1
            if cc == 1:
                ends.append(v1)

        plen = self.prop_plen
        ends = sorted(ends, key=self.phash)

        # if plen < 0:            
        #     ends = list(reversed(ends))
        
        return ends


    def phash(self, e):
        # return e.index
        c1 = e.co
        return c1.x * 10000 + c1.y * 100 + c1.z


    def div_set(self, sel):
        eall = set(sel)
        ess = []
        while len(eall) > 0:
            e1 = eall.pop()
            es = set([e1])
            ep = [e1]
            for e2 in ep:
                es2 = self.linked(e2)
                for e3 in es2:
                    if (e3 in es) == False:
                        es.add(e3)
                        ep.append(e3)
            eall = eall - es
            ess.append( list(es))
        # pprint.pprint(ess)
        return ess



    def linked(self, e1):
        es = []
        for v1 in e1.verts:        
            for e2 in v1.link_edges:
                if e2 == e1:
                    continue
                if e2.select:
                    es.append(e2)
        return es
            


    def on_move(self, context, event):        
        gui.lines = []        
        plen = self.get_relative_pos(context, event)
        if plen != None:
            self.prop_plen = plen
        
        px = event.mouse_region_x
        py = event.mouse_region_y
        region = bpy.context.region
        sx = px/region.width
        sy = py/region.height
        c1 = Vector((sx, sy, 0)) - Vector((0.5, 0.5, 0))
        c1 = c1 * 2        
        self.pos = Vector((sx, sy, 0))
        self.process(context, c1)
        


    def get_mats(self):
        vm = bpy.context.space_data.region_3d.view_matrix
        wm = bpy.context.space_data.region_3d.window_matrix
        wm2 = wm.inverted()
        vm2 = vm.inverted()
        return (vm, vm2, wm, wm2)



    def get_relative_pos(self, context, event):
        px = event.mouse_region_x
        py = event.mouse_region_y

        if self.px == px and self.py == py:
            return None
        self.px = px
        self.py = py

        region = bpy.context.region
        fpx = px / region.width - 0.5

        f2 = self.pmx / region.width - 0.5
        
        # bm = self.bm2
        dis = self.get_zoom_dis(self.bm2)
        if event.shift:
            slow = 0.2
        else:
            slow = 1
        return (fpx - f2) * dis * 2 * slow



        

    def get_zoom_dis(self, bm):
        obj = bpy.context.active_object
        ori = Vector()
        for p in obj.bound_box:
            ori = ori + Vector(p)
        ori = ori / 8

        vm, vm2, wm, wm2 = self.get_mats()                
        o2 = vm @ ori
        p1 = wm2 @ Vector((1, 0, 0))
        p2 = wm2 @ Vector()
        p1.z = o2.z
        p2.z = o2.z
        p1 = vm2 @ p1
        p2 = vm2 @ p2
        d1 = self.pro2d(p1)
        d2 = self.pro2d(p2)
        m1 = p2 - p1
        m2 = d2 - d1
        if m2.length == 0:
            return 1
        fp = m1.length / m2.length
        return fp        


    def pro2d(self, loc, mat2=None):        
        if mat2 != None:
            mat = mat2
        else:
            mat = bpy.context.space_data.region_3d.perspective_matrix        

        loc2 = mat @ Vector((loc.x, loc.y, loc.z, 1.0))
        if loc2.w > 0.0:
            return Vector((loc2.x / loc2.w, loc2.y / loc2.w, 0))
        else:
            return Vector()        
    
     
    def get_mats(self):
        vm = bpy.context.space_data.region_3d.view_matrix
        wm = bpy.context.space_data.region_3d.window_matrix
        wm2 = wm.inverted()
        vm2 = vm.inverted()
        return (vm, vm2, wm, wm2)



    def get_3d_cursor(self, context, event):
        #object = context.edit_object
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        #object = bpy.context.object
        region = bpy.context.region
        region3D = bpy.context.space_data.region_3d
        view_vector = view3d_utils.region_2d_to_vector_3d(
            region, region3D, mouse_pos)
        view_point = view3d_utils.region_2d_to_origin_3d(
            region, region3D, mouse_pos)
        world_loc = view3d_utils.region_2d_to_location_3d(region,
            region3D, mouse_pos, view_vector)
        return view_vector, view_point, world_loc



    def calc_pos_view(self, context, event):
        obj = context.edit_object
        view_vector, view_point, world_loc = self.get_3d_cursor(context, event)
        world = obj.matrix_world
        world2 = world.inverted()
        viewer = world2 @ view_point
        tar = world2 @ world_loc
        return viewer, tar



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
    #     if context.edit_object:
    #         self.prop_plen = 0.04
    #         self.process(context)
    #         return {'FINISHED'} 
    #     else:
    #         return {'CANCELLED'}



    def draw_point(self, p1):
        gui.lines += [p1 + Vector((0.02, 0, 0)), p1 - Vector((0.02, 0, 0))]
        gui.lines += [p1 + Vector((0, 0.02, 0)), p1 - Vector((0, 0.02, 0))]


    def modal(self, context, event):    
        # import random
        # print(random.random())
        # print(event.type, event.value, event.mouse_prev_y, event.mouse_y)
        context.area.tag_redraw()
        if event.type == 'Q':
            if event.value == 'PRESS':                                    
                gui.draw_handle_remove()                
                #self.process(context)
                self.bm2.free()
                return {'FINISHED'}
                # gui.lines = []
                # self.proc2()
                #self.process(context)
                # return {'RUNNING_MODAL'}       

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                gui.draw_handle_remove()
                return {'FINISHED'}


        elif event.type == 'MOUSEMOVE':             
            # self.process(context)
            self.on_move(context, event)
            return {'PASS_THROUGH'}

        elif event.type == 'ESC':
            if event.value == 'PRESS':
                self.restore()        
                obj = bpy.context.active_object                
                me = bpy.context.active_object.data
                bmesh.update_edit_mesh(me)                                       
                gui.draw_handle_remove()  
                self.bm2.free()
                return {'CANCELLED'}

        if 'MOUSE' in event.type:
            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}
        


    def invoke(self, context, event):
        # self.pan_value = 0
        if context.edit_object:

            bm = self.get_bm()
            self.bm2 = bm.copy()
            # self.pmat = bpy.context.space_data.region_3d.perspective_matrix
            self.pmx = event.mouse_region_x
            self.pos = Vector()
            self.px = 0
            self.py = 0           
            gui.draw_handle_add((self, context))
            gui.text_handle_add((self, context))
            gui.txtall = ['按Esc键退出', '左键单击以提交', '按住Shift键进行慢速滑动']
            self.process(context)            
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'} 
        else:
            return {'CANCELLED'}

