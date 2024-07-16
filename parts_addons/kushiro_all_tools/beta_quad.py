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
    FloatVectorProperty,
)

import pprint
import time

from . import gui





# class Vert:
#     def __init__(self) -> None:
#         self.co = None
#         self.plist = []
#         self.move = Vector()
#         self.boundary = False
#         self.face_boundary = False
#         self.links = []


# class Vloop:
#     def __init__(self, co=None) -> None:
#         self.vert = None        
#         self.next = None
#         self.prev = None        
#         if co != None:
#             self.vert = Vert()
#             self.vert.co = co

#         self.ptype = ''
#         self.v2 = None
#         self.vk1 = None
#         self.vk2 = None
#         self.pv1 = None
#         self.pv2 = None
#         self.pvk1 = None
#         self.pvk2 = None



#     def angle(self):
#         m1 = self.next.vert.co - self.vert.co
#         m2 = self.prev.vert.co - self.vert.co
#         if m1.length == 0 or m2.length == 0:
#             return 0
#         return m1.angle(m2)

#     def link_next(self, v2):
#         self.next = v2
#         v2.prev = self

#     def link_prev(self, v2):
#         self.prev = v2
#         v2.next = self

#     def copy(self):
#         vp = Vloop()
#         vp.vert = self.vert
#         return vp

#     def copy_new(self):
#         vp = Vloop(Vector())
#         vp.vert.co = self.vert.co.copy()
#         return vp        

#     def is_concave(self, sn):
#         m2 = self.vert.co - self.prev.vert.co
#         c1 = m2.cross(sn)
#         m1 = self.next.vert.co - self.vert.co

#         if m1.cross(m2).length < 0.001:
#             return False

#         if c1.length == 0 or m1.length == 0:
#             return False
#         if c1.angle(m1) < math.radians(90):
#             return True
#         else:
#             return False
        

class BetaQuadOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.beta_quad_operator"
    bl_label = "Beta Quad —— 四边面重拓扑"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "四边面重拓扑工具"
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Quad size",
        description="定义四边形的大小",
        default=0.4,
        min = 0.4,
        step=1,
    )    



    prop_size_multiplier: FloatProperty(
        name="Size Multipler (auto reset)",
        description="四边面的尺寸倍增器",
        default=1.0,
        step=0.1,
        min = 0.01,
    )    


    prop_boundary_edge_flow: BoolProperty(
        name="Boundary Edge Flow",
        description="尽量保持边界范围的流形",
        default=True,
    )



    prop_inset_boundary: BoolProperty(
        name="Inset boundary",
        description="内插锐边边界",
        default=False,
    )


 
    prop_inset_width: FloatProperty(
        name="Inset Width",
        description="内插的大小 (相对于四边形大小)",
        default=0.05,
        step=0.1,
        min = 0.01,
    )       

    prop_inset_angle: FloatProperty(
        name="Inset sharp angle",
        description="定义锐边的角度限制",
        default=5,
        step=10,
        min = 0.01,
    )    



    prop_keep_edge: BoolProperty(
        name="Keep sharp edge",
        description="不要平滑锋利的边缘",
        default=False,
    )    



    prop_keep_edge_angle: FloatProperty(
        name="Edge Angle",
        description="定义用于保持锋利边缘的边缘角度",
        default=75,
        min = 0,
        max = 180,
        step=10,
    )    




    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm




    def process(self, context):
        gui.lines = []
        gui.textpos = []
        self.plen = 0.05
        self.cuts = 1
        self.part = self.prop_plen * self.prop_size_multiplier
        bm = self.get_bm()   

        
        # f1 = bm.faces[0]
        # self.check_grid_direct(bm, f1)

        # obj = bpy.context.active_object                
        # me = bpy.context.active_object.data
        # bmesh.update_edit_mesh(me)  

        # return
        self.bm = bm  
        sel = [f1 for f1 in bm.faces if f1.select]
        self.cen = self.get_center()
        original = set(sel)
        excluded = self.get_excluded(bm, original)
        flatedges = self.get_flat_edges(bm, sel)

        # for f1 in sel:
        #     self.even_cut_simple(bm, f1)
        for f1 in sel:
            f1.select = False

        fss = sel
        
        # for i in range(1):
        #     # self.current_milli_time()
        #     fss = []
        #     for f1 in sel:
        #         fs = self.div_faces_base_ext(bm, f1)
        #         if fs == []:
        #             fss.append(f1)
        #         else:
        #             sel.extend(fs)

        #     # self.current_milli_time()
        #     self.dissolve(bm, flatedges)   
        #     sel = self.get_current(bm, excluded)
        
        
        # sel = fss
        # fss = []
        # for f1 in sel:
        #     f1.select = False
        #     # finner, fss = self.inseting(bm, f1)             
        #     # self.even_cut(bm, f1)
        #     fs = self.div_faces_base(bm, f1)            
        #     if fs == []:
        #         fss.append(f1)
        #     else:
        #         sel.extend(fs)

        # self.current_milli_time()

        # fss = self.get_current(bm, excluded)
        # self.fss = fss
        # fss2 = []
        # totalset = self.group_faces(fss)
        # for f2 in totalset:  
        #     self.div_inset(bm, f2)
        # # self.div_inset(bm, fss)


        for f2 in fss:  
            if f2.is_valid == False:
                continue
            fs = self.div_faces_quad_any(bm, f2)             
        self.dissolve(bm, flatedges)  


        fss = self.get_current(bm, excluded)
        self.fss = fss
        fss2 = []
        for f2 in fss:  
            if f2.is_valid == False:
                continue
            fs = self.div_faces_quad(bm, f2)
            # fs = self.check_double_div(bm, fs, f2)
            if fs == []:
                fss2.append(f2)
            else:
                fss.extend(fs)
        # # self.current_milli_time()

        for f2 in fss2:
            if f2.is_valid:
                self.fix_concave(bm, f2, 0)
        # self.current_milli_time()
        self.sub_div(bm, excluded)
        # self.current_milli_time()        
        self.process_smooth(bm, excluded) 
        # self.current_milli_time()

        fss = self.get_current(bm, excluded) 
        if self.prop_inset_boundary:
            totalset = self.group_faces(fss)
            self.group_inset(bm, totalset)

                   

        # bmesh.ops.delete(bm, geom=[f1], context='FACES')       
        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)   



    def draw_edge(self, e1):
        a, b = e1.verts
        gui.lines += [a.co.copy(), b.co.copy()]


    def draw_loop(self, p):
        c1 = p.vert.co
        p3 = p.link_loop_prev
        m1 = p3.vert.co - c1
        m1 = m1.normalized() * 0.01 + c1
        p4 = p.link_loop_next
        m2 = p4.vert.co - c1
        m2 = m2.normalized() * 0.01 + c1
        gui.lines += [m1, m2]




    def shifting(self, p1, pm):        
        lim1 = 2
        m1 = pm.vert.co - p1.vert.co
        m2 = p1.link_loop_next.vert.co - p1.vert.co
        m3 = p1.link_loop_prev.vert.co - p1.vert.co
        if m2.length == 0 or m3.length == 0:
            return        
        if abs(m2.angle(m3) - math.radians(180)) > math.radians(lim1):
            return        
        pro1 = m1.project(m2)
        if pro1.length == 0:
            return
        if pro1.angle(m2) < pro1.angle(m3):
            if pro1.length > m2.length:
                return
            p1.vert.co = p1.vert.co + pro1/2
            # gui.lines += [p1.vert.co.copy() , p1.vert.co + pro1/2]
            print(pro1)
        else:
            if pro1.length > m3.length:
                return
            # p1.vert.co = p1.vert.co - pro1/2
            # gui.lines += [p1.vert.co , p1.vert.co - pro1/2]
            

        



    def get_center(self):
        obj = bpy.context.active_object
        vs = [Vector(corner) for corner in obj.bound_box]
        v1 = Vector()
        for v2 in vs:
            v1 = v1 + v2
        v1 = v1 / len(vs)
        return v1


    def current_milli_time(self):
        if hasattr(self, 'ptime') == False:
            self.ptime = 0
        p = round(time.time() * 1000)
        print(p - self.ptime)
        self.ptime = p


    def inseting(self, bm, f1):    
        plen = self.plen 
        sn = f1.normal
        coss = [p.vert.co for p in f1.loops]        
        vmap = {}
        inner1 = []
        fss = []
        for co in coss:
            p1 = None
            for p2 in f1.loops:
                if p2.vert.co == co:
                    p1 = p2
                    break
            if p1 == None:
                break            
            m1 = p1.link_loop_next.vert.co - p1.vert.co
            m2 = p1.link_loop_prev.vert.co - p1.vert.co
            m3 = self.mid_line(m1, m2, sn)
            m3 = m3.normalized() * plen
            co3 = p1.vert.co + m3               
            
            if p1.is_convex == False:                
                if p1.calc_angle() < math.radians(120):
                    leng1 = p1.link_loop_next.vert.co - p1.vert.co
                    leng2 = p1.link_loop_prev.vert.co - p1.vert.co
                    off1 = m2.normalized() * min(plen, leng1.length * 0.4)
                    off2 = m1.normalized() * min(plen, leng2.length * 0.4)
                    k1 = p1.vert.co - off1
                    k2 = p1.vert.co - off2
                    k3 = p1.vert.co - off1 - off2                 
                    vmap[p1] = ['b', (k1, k2, k3)]
                else:
                    vmap[p1] = ['c', co3]
                    pass
            else:                
                leng1 = p1.link_loop_next.vert.co - p1.vert.co
                leng2 = p1.link_loop_prev.vert.co - p1.vert.co
                off1 = m1.normalized() * min(plen, leng1.length * 0.4)
                off2 = m2.normalized() * min(plen, leng2.length * 0.4)
                k1 = p1.vert.co + off1
                k2 = p1.vert.co + off2
                e1 = p1.edge
                e2 = p1.link_loop_prev.edge
                v1, v2 = self.chop_edge(bm, [e1, e2], [k1, k2])
                vmap[p1] = ['a', co3]        

        for p1 in vmap:
            bag = vmap[p1]
            t, item = bag
            if t == 'a':                
                v1 = bm.verts.new(item)
                bag[1] = v1
            elif t == 'b':
                a, b, c = item
                v1 = bm.verts.new(a)
                v2 = bm.verts.new(b)
                v3 = bm.verts.new(c)
                bag[1] = (v1,v2,v3)
            elif t == 'c':
                v1 = bm.verts.new(item)
                bag[1] = v1

        coss2 = coss[1:] + [coss[0]]
        for co, co2 in zip(coss, coss2):
            p1 = None
            pn = None
            for p2 in f1.loops:
                if p2.vert.co == co:
                    p1 = p2
                if p2.vert.co == co2:
                    pn = p2
            if p1 == None or pn == None:
                break

            sides = []
            t1, item1 = vmap[p1]
            t2, item2 = vmap[pn]

            if t1 == 'b':                
                k1, k2, k3 = item1
                f2 = bm.faces.new((p1.vert, k1, k3, k2))
                f2.normal_update()         
                fss.append(f2)
                sides.append((p1.vert, k1)) 
                inner1.append(k2)   
                inner1.append(k3)
                inner1.append(k1)            
            elif t1 == 'c':
                v3 = item1
                sides.append((p1.vert, v3))   
                inner1.append(v3)             
            elif t1 == 'a':
                v3 = item1
                v1 = p1.link_loop_next.vert
                v2 = p1.link_loop_prev.vert
                f2 = bm.faces.new((p1.vert, v1, v3, v2))
                f2.normal_update()
                fss.append(f2)
                sides.append((v1, v3))
                inner1.append(v3) 

            if t2 == 'b':                
                k1, k2, k3 = item2
                sides.append((pn.vert, k2)) 
            elif t2 == 'c':
                v3 = item2
                sides.append((pn.vert, v3)) 
            elif t2 == 'a':
                v3 = item2
                v1 = pn.link_loop_next.vert
                v2 = pn.link_loop_prev.vert
                sides.append((v2, v3))
            
            (a, b), (c, d) = sides     
            f3 = bm.faces.new((a, c, d, b))
            f3.normal_update()      
            fss.append(f3)   

        finner = bm.faces.new(inner1)
        finner.normal_update()

        bmesh.ops.delete(bm, geom=[f1], context='FACES')        
        return finner, fss


    def chop_line(self, bm, v1, v2):
        res = bmesh.ops.connect_verts(bm, verts=[v1, v2], check_degenerate=False)
        es = res['edges']
        if len(es) == 0:
            return None
        return es[0]
      


    def chop_edge(self, bm, es, cs):
        res = bmesh.ops.bisect_edges(bm, edges=es, cuts=1)
        vs = [e for e in res['geom_split'] if isinstance(e, bmesh.types.BMVert)]
        for v, co in zip(vs, cs):
            v.co = co
        return vs


    def get_excluded(self, bm, fss):
        excluded = set(bm.faces) - fss
        return excluded


    def sub_div(self, bm, excluded):
        cuts = self.cuts
        fs2 = []
        esall = set()
        remaining = set(bm.faces) - excluded

        for f1 in remaining:
            es = f1.edges            
            esall = esall.union(set(es))
            if len(es) != 4:
                fs2.append(f1)            

        bmesh.ops.subdivide_edges(bm, edges=list(esall), 
            cuts=1, use_grid_fill=True, use_only_quads=True)
    

        for f1 in fs2:
            cen = f1.calc_center_median()
            v1 = bm.verts.new(cen)            
            for i, p in enumerate(f1.loops):
                if i % 2 == 1:
                    p2 = p.link_loop_next
                    p3 = p2.link_loop_next
                    vs = [v1, p.vert, p2.vert, p3.vert]                    
                    f2 = bm.faces.new(vs)                
                    f2.normal_update()
        
        bmesh.ops.delete(bm, geom=fs2, context='FACES')

        remaining = set(bm.faces) - excluded
        esall2 = set()
        for f1 in remaining:
            esall2 = esall2.union(set(f1.edges))
        esall2 = list(esall2)            

        cuts = cuts - 1
        if cuts > 0:        
            bmesh.ops.subdivide_edges(bm, edges=esall2, 
                cuts=cuts, use_grid_fill=True, use_only_quads=True)


    def get_current(self, bm, excluded):
        remaining = set(bm.faces) - excluded
        return list(remaining)
                


    def process_smooth(self, bm, excluded):
        inners = set()
        bounding = set()
        # for v1 in bm.verts:
        #     bound = any([e1.is_boundary for e1 in v1.link_edges])                
        #     if bound == False:
        #         inners.append(v1)
        keep = self.prop_keep_edge
        keepangle = self.prop_keep_edge_angle
        remaining = self.get_current(bm, excluded)

        fbound = set()
        finner = set()

        for f1 in remaining:
            bound = False
            for e1 in f1.edges:
                if e1.is_boundary:                    
                    bound = True                    
                    break

                if keep:
                    if len(e1.link_faces) == 2:
                        d1 = e1.calc_face_angle()                        
                        if d1 > math.radians(keepangle):
                            bound = True                            
                            break
                for f2 in e1.link_faces:
                    if f2 in excluded:                        
                        bound = True                        
                        break
            if bound:                
                fbound.add(f1)
            else:
                finner.add(f1)

        for f1 in fbound:
            for v1 in f1.verts:
                bounding.add(v1)
            
        for f1 in finner:
            for v1 in f1.verts:
                inners.add(v1)
        
        inners = inners - bounding
        inners = list(inners)

        self.smoothing(inners)
        





    def smoothing(self, vs):
        vmap = {}
        keep = self.prop_keep_edge
        for v1 in vs:            
            cs = []
            for f1 in v1.link_faces:
                cen = f1.calc_center_median()
                cs.append(cen)
            vmap[v1] = cs

        for v1 in vmap:
            p1 = Vector()
            cs = vmap[v1]
            for c1 in cs:
                p1 = p1 + c1
            p1 = p1 / len(cs)  
            
            # cross = False
            # eset = set()
            # for f2 in v1.link_faces:
            #     for e1 in f2.edges:
            #         eset.add(e1)
            # for e1 in v1.link_edges:
            #     eset.remove(e1)

            # for e1 in v1.link_edges:
            #     v2 = e1.other_vert(v1)
            #     m1 = v2.co - v1.co
            #     c1 = v2.co + m1 * 0.95
            #     for e2 in eset:
            #         a, b = e2.verts                    
            #         pin = self.get_cross_inside(c1, p1,
            #             a.co, b.co)
            #         if pin != None:
            #             cross = True
            #             break
            # if cross:
            #     continue                      

            if keep:
                m1 = p1 - v1.co
                pro1 = m1.project(v1.normal)
                v1.co = p1 - pro1
            else:
                v1.co = p1
            # pint = self.overflow(v1, p1)            
            # if pint == False:
            #     v1.co = p1
            # else:
            #     m1 = pint - v1.co
            #     v1.co = v1.co + m1 * 0.5


    def fix_reverse(self, bm, fss):
        for f1 in fss:
            for p in f1.loops:
                p2 = p.link_loop_next
                p3 = p.link_loop_prev
                a = p.vert
                b = p3.vert
                c = p2.vert
                d = p2.link_loop_next.vert
                pin = self.get_cross_inside(a.co, b.co,
                    c.co, d.co)
                if pin != None:
                    v1 = b.co.copy()
                    v2 = d.co.copy()
                    b.co = v2
                    d.co = v1
            f1.normal_update()



    def overflow(self, v1, p1):
        es = set()
        es2 = set()
        for f1 in v1.link_faces:
            for e1 in f1.edges:
                es.add(e1)
        for e1 in v1.link_edges:
            es2.add(e1)
        es3 = es - es2
        for e1 in es3:
            a, b = e1.verts
            p2 = (p1 - v1.co) * 2 + v1.co
            res = self.get_cross_inside(v1.co, p2, a.co, b.co)
            if res != None:
                return res
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
    


    def inseting2(self, vs, bm, f1):     
        plen = self.plen
        sn = f1.normal
        vs2 = []        
        # vmap = {}
        # kvmap = {}
        fss = []
        for v1 in vs:
            m1 = v1.next.vert.co - v1.vert.co
            m2 = v1.prev.vert.co - v1.vert.co
            m3 = self.mid_line(m1, m2, sn)
            m3 = m3.normalized() * plen
            co = v1.vert.co + m3
            v2 = Vloop(co)
            vs2.append(v2)
            #
            if v1.is_concave(sn):
                if v1.angle() < math.radians(120):
                    leng1 = v1.next.vert.co - v1.vert.co
                    leng2 = v1.prev.vert.co - v1.vert.co
                    off1 = m2.normalized() * min(plen, leng1.length * 0.4)
                    off2 = m1.normalized() * min(plen, leng2.length * 0.4)
                    k1 = v1.vert.co - off1
                    k2 = v1.vert.co - off2
                    vk1 = Vloop(k1)
                    vk2 = Vloop(k2)
                    # vmap[v1] = ['c', v2, vk1, vk2]   
                    v1.ptype = 'c'
                    v1.v2 = v2
                    v2.co = v1.vert.co - off1 - off2
                    v1.vk1 = vk1
                    v1.vk2 = vk2
                else:
                    # vmap[v1] = ['b', v2]
                    v1.ptype = 'b'
                    v1.v2 = v2
            else:                
                leng1 = v1.next.vert.co - v1.vert.co
                leng2 = v1.prev.vert.co - v1.vert.co
                k1 = v1.vert.co + m1.normalized() * min(plen, leng1.length * 0.4)
                k2 = v1.vert.co + m2.normalized() * min(plen, leng2.length * 0.4)
                vk1 = Vloop(k1)
                vk2 = Vloop(k2)
                # vmap[v1] = ['a', v2, vk1, vk2]
                v1.ptype = 'a'
                v1.v2 = v2
                v1.vk1 = vk1
                v1.vk2 = vk2                
        self.link_all(vs2)       
        pvs1 = []        
        for v1 in vs:            
            if v1.ptype == 'a':
                v1.pv1 = bm.verts.new(v1.vert.co)  
                v1.pv2 = bm.verts.new(v1.v2.vert.co)
                v1.pvk1 = bm.verts.new(v1.vk1.vert.co)
                v1.pvk2 = bm.verts.new(v1.vk2.vert.co)
                pvs1.append(v1.pv2)
            elif v1.ptype == 'c':
                v1.pv1 = bm.verts.new(v1.vert.co)  
                v1.pv2 = bm.verts.new(v1.v2.vert.co)
                v1.pvk1 = bm.verts.new(v1.vk1.vert.co)
                v1.pvk2 = bm.verts.new(v1.vk2.vert.co)
                pvs1.append(v1.pvk2)
                pvs1.append(v1.pv2)  
                pvs1.append(v1.pvk1)                
            elif v1.ptype == 'b':                
                v1.pv1 = bm.verts.new(v1.vert.co)
                v1.pv2 = bm.verts.new(v1.v2.vert.co)                
                pvs1.append(v1.pv2)                

        for v1 in vs:            
            vnext = v1.next
            sides = []
            if v1.ptype == 'a':                
                f3 = bm.faces.new([v1.pv1, v1.pvk1, v1.pv2, v1.pvk2])
                f3.normal_update()
                sides.append((v1.pvk1, v1.pv2))
                fss.append(f3)
            elif v1.ptype == 'c':                
                f3 = bm.faces.new([v1.pv1, v1.pvk1, v1.pv2, v1.pvk2])
                f3.normal_update()
                sides.append((v1.pv1, v1.pvk1))
                fss.append(f3)                
            elif v1.ptype == 'b':                
                sides.append((v1.pv1, v1.pv2))

            if vnext.ptype == 'a':                
                sides.append((vnext.pvk2, vnext.pv2))
            elif vnext.ptype == 'c':                
                sides.append((vnext.pv1, vnext.pvk2))
            elif vnext.ptype == 'b':                
                sides.append((vnext.pv1, vnext.pv2))

            pa, pb = sides[0]
            pc, pd = sides[1]
            f4 = bm.faces.new([pa, pc, pd, pb])
            f4.normal_update()
            fss.append(f4)

        f2 = bm.faces.new(pvs1)
        f2.normal_update()    
        #fss.append(f2)        
        # bmesh.ops.delete(bm, geom=[f1], context='FACES')        
        return f2, fss

       

    def shift(self, vs):
        vs2 = vs[1:] + [vs[0]]
        return zip(vs, vs2)
    

    def quad_fix(self, bm, f1):
        ct = len(f1.edges)
        if ct % 4 != 0:
            q1 = 4 - (ct % 4)
            for i in range(q1):
                ps = [(p.edge.calc_length(), p) for p in f1.loops]
                _, pm = max(ps, key=lambda e: e[0])
                self.cut_quad(bm, f1, pm)


    def cut_quad(self, bm, f1, pm, ct):
        f2 = self.near_face(f1, pm.edge)
        fp = self.loop_from_edge(f2, pm.edge)    
        fp2 = fp.link_loop_next.link_loop_next
        res1 = bmesh.ops.subdivide_edges(bm, edges=[pm.edge, fp2.edge], 
            cuts=ct, use_grid_fill=False)

                
    def loop_from_edge(self, f1, e1):
        for p in f1.loops:
            if p.edge == e1:
                return p
        return None


    def near_face(self, f1, e1):
        f2, f3 = e1.link_faces
        if f2 == f1:
            fp = f3
        else:
            fp = f2        
        return fp


    def is_concave(self, p, sn):
        m2 = p.vert.co - p.link_loop_prev.vert.co
        c1 = m2.cross(sn)
        m1 = p.link_loop_next.vert.co - p.vert.co

        if m1.cross(m2).length < 0.001:
            return False

        if c1.length == 0 or m1.length == 0:
            return False
        if c1.angle(m1) < math.radians(90):
            return True
        else:
            return False


    def is_crossed(self, p, p4, ft, fvm):
        a = fvm[p]
        b = fvm[p4]
        pmath = PlaneMath()
        for pn in ft.loops:
            pn2 = pn.link_loop_next            
            if p == pn or p4 == pn:
                continue
            if p == pn2 or p4 == pn2:
                continue
            c = fvm[pn]
            d = fvm[pn2]
            if pmath.is_inter(a, b, c, d):
                return True            
        return False


    def is_crossed_old(self, p, p4, ft):
        for pn in ft.loops:
            pn2 = pn.link_loop_next
            pn3 = pn.link_loop_prev
            if p == pn or p4 == pn:
                continue
            if p == pn2 or p4 == pn2:
                continue
            
            pin = self.get_cross_inside(p.vert.co, p4.vert.co, 
                pn.vert.co, pn2.vert.co)
            if pin != None:
                # self.draw_point(pin)
                return True       
        return False 

        
    def is_crossed_old_2(self, p, p4, co, ft):
        for pn in ft.loops:
            pn2 = pn.link_loop_next
            if p == pn or p4 == pn:
                continue
            # if p == pn2 or p4 == pn2:
            #     continue
            if p == pn2:
                continue
            
            pin = self.get_cross_inside(p.vert.co, co, 
                pn.vert.co, pn2.vert.co)
            if pin != None:
                #self.draw_point(pin)
                #gui.lines += [p.vert.co, pin]
                return pin       
        return False 



    def get_crossed_all(self, p, co, ft):
        css = []
        for pn in ft.loops:
            pn2 = pn.link_loop_next
            if p == pn or p == pn2:
                continue
            
            pin = self.get_cross_inside(p.vert.co, co, 
                pn.vert.co, pn2.vert.co)
            if pin != None:
                m1 = pin - p.vert.co
                css.append((m1.length, pin, pn))
        return css




    def get_angles(self, p, pm):
        p2 = p.link_loop_next
        p3 = p.link_loop_prev
        m2 = p2.vert.co - p.vert.co
        m3 = p3.vert.co - p.vert.co
        m1 = pm.vert.co - p.vert.co
        if m1.length == 0 or m2.length == 0 or m3.length == 0:
            return 0, 0
        d1 = m1.angle(m2)
        d2 = m1.angle(m3)
        return d1, d2


    def cut_face(self, bm, v1, v2):
        res = bmesh.ops.connect_verts(bm, verts=[v1, v2])
        es = res['edges']
        if len(es) == 0:
            return None
        e1 = es[0]
        if len(e1.link_faces) != 2:
            return None
        efs = list(e1.link_faces)
        # self.even_cut_single(bm, e1)
        return efs




    def div_faces_base(self, bm, f1):     
        if len(f1.loops) <= 4:
            return []

        self.even_cut_simple(bm, f1)
        # fvm = self.get_fvm(f1)

        d179 = math.radians(179)
        fcon = [p for p in f1.loops if p.is_convex == False and p.calc_angle() <= d179]
        if len(fcon) == 0:
            return []

        for p in fcon:                     
            # ps = []            
            spt = None
            sdm = None            
            for p2 in f1.loops:
                if p == p2:
                    continue
                d1, d2 = self.get_angles(p, p2)
                d3, d4 = self.get_angles(p2, p)
                # d90 = math.radians(90)
                # dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)
                dm = abs(d1-d2) + abs(d3-d4)                
                if sdm != None and dm > sdm:
                    continue

                d30 = math.radians(75)
                if d1 < d30 or d2 < d30:
                    continue
                if d3 < d30 or d4 < d30:
                    continue
                
                if self.get_real_angle_cmp(p, p2, f1.normal):
                    continue

                # if self.is_crossed(p, p2, f1, fvm):
                #     continue

                if self.is_crossed_old(p, p2, f1):
                    continue                

                # d1, d2 = self.get_real_angle(p, p2, f1.normal)
                # if d1 < d2:
                #     continue           
                
                # ps.append((dm, p2))
                if sdm == None or dm < sdm:
                    sdm = dm
                    spt = p2              

            #_, pm = min(ps, key=lambda e:e[0])
            # ps2 = [e for e in ps if (e[1].vert in used) == False]
            
            # ps2 = ps
            # if len(ps2) == 0:
            #     continue        
            # _, pm = min(ps2, key=lambda e:e[0])  
            if spt == None:
                continue
            pm = spt

            # self.draw_point(pm.vert.co)            
            # used.add(pm.vert)
            # used.add(p.vert)
            # gui.lines += [p.vert.co, pm.vert.co]
            cf = self.cut_face(bm, p.vert, pm.vert)
            if cf == None:
                continue
            lencf = len(cf)
            if lencf == 0:
                continue
            elif lencf == 1:
                # cf2 = self.div_faces_base(bm, cf[0])
                # return cf2
                return cf
            else:
                # cf2 = self.div_faces_base(bm, cf[0])
                # cf3 = self.div_faces_base(bm, cf[1])
                # return cf2 + cf3
                return cf
            # return cf
        return []


        
    def get_crossed(self, p1, p2, ft):
        for e1 in p1.vert.link_edges:
            k1 = e1.other_vert(p1.vert)
            m1 = p1.vert.co - k1.co
            a1 = p1.vert.co + m1 * 1000
            p3 = p2.link_loop_next
            if p3 == p1 or k1 == p2 or k1 == p3:
                continue
            pin = self.get_cross_inside(p1.vert.co, a1, 
                p2.vert.co, p3.vert.co)
            if pin != None:
                # self.draw_point(pin)
                # gui.lines += [pin, p1.vert.co]
                return pin       
        return False 


    def cut_forward(self, bm, e1, c1):
        res1 = bmesh.ops.subdivide_edges(bm, edges=[e1], 
            cuts=1, use_grid_fill=False)
        # pprint.pprint(res1)
        g1 = res1['geom_inner']
        if len(g1) == 0:
            return
        v2 = g1[0]        
        v2.co = c1
        return v2




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

        # p1 = pprev.link_loop_next
        # p2 = p1.link_loop_next
        # p3 = p2.link_loop_next
        # return v1, [p1, p2, p3]


    def cut_forward_bisect_loop(self, bm, p1, c1):
        e1 = p1.edge
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


    def loop_vec(self, p):
        m1 = p.link_loop_next.vert.co - p.vert.co
        return m1.normalized()


    def div_faces_base_ext(self, bm, f1):  
        if len(f1.loops) <= 4:
            return []
        cuts = [] 
        for p1 in f1.loops:      
            # concave = p1.is_convex == False and p1.calc_angle() < math.radians(179)
            # if concave == False:
            #     continue
            if p1.is_convex:
                continue

            for p2 in f1.loops:
                if p2 == p1:
                    continue
                
                if len(p2.edge.link_faces) == 2:
                    if p2.edge.calc_face_angle() < math.radians(2):
                        continue
                m1 = p1.vert.co - p2.vert.co
                m2 = p2.link_loop_next.vert.co - p2.vert.co
                pin = m1.project(m2)
                tco = pin + p2.vert.co

                if pin.length < 0.001:
                    # gui.lines += [p1.vert.co, tco]
                    # gui.addtext(tco, 'pin.length 0')
                    continue

                if abs(pin.length - m2.length) < 0.001:
                    # gui.addtext(tco, 'pin.length max')
                    continue

                if pin.length > m2.length:                    
                    # gui.addtext(tco, 'pin outside')
                    continue

                if (pin - m2).length > m2.length:
                    # gui.addtext(tco, 'pin behind')
                    continue

                if pin.length < m2.length / 10:
                    # gui.addtext(tco, 'pin small')
                    continue
                if (m2 - pin).length < m2.length / 10:
                    # gui.addtext(tco, 'pin small')
                    continue                

                t1 = pin - p1.vert.co
                t2 = p1.link_loop_prev.vert.co - p1.vert.co
                t3 = p1.link_loop_next.vert.co - p1.vert.co
                if t1.length == 0 or t2.length == 0 or t3.length == 0:
                    continue
                if t1.angle(t2) < math.radians(30):
                    continue
                if t1.angle(t3) < math.radians(30):
                    continue

                # gui.lines += [p1.vert.co, tco]                

                # if self.get_real_angle_cmp_ext(p1, tco, f1.normal):
                #     # gui.addtext(tco, 'pin angle')
                #     continue
                # if self.get_real_angle_cmp_ext(p1, tco, f1.normal):
                #     continue                

                d1, d2 = self.get_real_angle_co(p1, tco, f1.normal)
                # print(math.degrees(d1), math.degrees(d2))
                # gui.lines = []
                # gui.lines += [p1.vert.co, tco]
                # gui.lines += [p1.vert.co, p1.link_loop_next.vert.co]
                if d1 < d2:
                    continue    

                crx = self.is_crossed_old_2(p1, p2, tco, f1)
                if crx != False:                    
                    continue
                    # pass                    
                    # self.draw_point(crx)
                # gui.lines += [pin, p1.vert.co]
                cuts.append(((pin - p1.vert.co).length, p1, p2, tco))
                
        if len(cuts) == 0:
            return []
        _, p1, p2, tco = min(cuts, key=lambda e:e[0])

        # gui.lines += [p1.vert.co.copy(), tco]
        # gui.lines += [p2.vert.co.copy(), tco]
        # crx = self.is_crossed_old_2(p1, p2, tco, f1)
        # self.draw_point(crx)

        vpm = self.cut_forward(bm, p2.edge, tco)
        cf = self.cut_face(bm, p1.vert, vpm)
        if cf == None:
            # continue
            return []
        lencf = len(cf)
        if lencf == 0:
            # continue    
            return []
        return cf        
                # gui.lines += [p1.vert.co, pin]
        return []
        gs = list(bm.faces) + list(bm.edges)

        # gs = [f1] + list(f1.edges)
        # mk = tco - p1.vert.co
        # mk2 = f1.normal.cross(mk)
        # result = bmesh.ops.bisect_plane(bm,
        #                       dist=0.01,
        #                       geom=gs,
        #                       plane_co=p1.vert.co,
        #                       plane_no=mk2)
        # gf1 = [p for p in result['geom'] if isinstance(p, bmesh.types.BMFace)]
        # return gf1
        # return []



    def div_faces_base_ext2(self, bm, f1):  
        if len(f1.loops) <= 4:
            return []
        cuts = [] 
        for p1 in f1.loops:
            for p2 in f1.loops:
                if p2 == p1:
                    continue
                pin = self.get_crossed(p1, p2, f1)
                if pin == False:
                    continue
                if (pin-p2.vert.co).length < 0.01:
                    continue
                p3 = p2.link_loop_next
                if (pin-p3.vert.co).length < 0.01:
                    continue
                m1 = p1.vert.co - pin
                m2 = p2.vert.co - pin
                if m1.length == 0 or m2.length == 0:
                    continue
                # d1 = m1.angle(m2)
                # if abs(d1 - math.radians(90)) > math.radians(20):
                #     continue

                if self.get_real_angle_cmp_ext(p1, pin, f1.normal):
                    continue
                # gui.lines += [pin, p1.vert.co]
                cuts.append((p1, p2, pin))

        for p1, p2, pin in cuts:
            vpm = self.cut_forward(bm, p2.edge, pin)
            cf = self.cut_face(bm, p1.vert, vpm)
            if cf == None:
                continue
            lencf = len(cf)
            if lencf == 0:
                continue    
            return cf        

        return []

        # if len(f1.loops) <= 4:
        #     return []

        # self.even_cut_simple(bm, f1)
        # # fvm = self.get_fvm(f1)

        # d179 = math.radians(179)
        # fcon = [p for p in f1.loops if p.is_convex == False and p.calc_angle() <= d179]
        # if len(fcon) == 0:
        #     return []

        # for p in fcon:                     
        #     # ps = []            
        #     spt = None
        #     sdm = None            
        #     for p2 in f1.loops:
        #         if p == p2:
        #             continue
        #         d1, d2 = self.get_angles(p, p2)
        #         d3, d4 = self.get_angles(p2, p)
        #         # d90 = math.radians(90)
        #         # dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)
        #         dm = abs(d1-d2) + abs(d3-d4)                
        #         if sdm != None and dm > sdm:
        #             continue

        #         d30 = math.radians(75)
        #         if d1 < d30 or d2 < d30:
        #             continue
        #         if d3 < d30 or d4 < d30:
        #             continue
                
        #         if self.get_real_angle_cmp(p, p2, f1.normal):
        #             continue

        #         # if self.is_crossed(p, p2, f1, fvm):
        #         #     continue

        #         if self.is_crossed_old(p, p2, f1):
        #             continue                

        #         # d1, d2 = self.get_real_angle(p, p2, f1.normal)
        #         # if d1 < d2:
        #         #     continue           
                
        #         # ps.append((dm, p2))
        #         if sdm == None or dm < sdm:
        #             sdm = dm
        #             spt = p2              

        #     #_, pm = min(ps, key=lambda e:e[0])
        #     # ps2 = [e for e in ps if (e[1].vert in used) == False]
            
        #     # ps2 = ps
        #     # if len(ps2) == 0:
        #     #     continue        
        #     # _, pm = min(ps2, key=lambda e:e[0])  
        #     if spt == None:
        #         continue
        #     pm = spt

        #     # self.draw_point(pm.vert.co)            
        #     # used.add(pm.vert)
        #     # used.add(p.vert)
        #     # gui.lines += [p.vert.co, pm.vert.co]
        #     cf = self.cut_face(bm, p.vert, pm.vert)
        #     if cf == None:
        #         continue
        #     lencf = len(cf)
        #     if lencf == 0:
        #         continue
        #     elif lencf == 1:
        #         # cf2 = self.div_faces_base(bm, cf[0])
        #         # return cf2
        #         return cf
        #     else:
        #         # cf2 = self.div_faces_base(bm, cf[0])
        #         # cf3 = self.div_faces_base(bm, cf[1])
        #         # return cf2 + cf3
        #         return cf
        #     # return cf
        # return []


 

    def get_fvm(self, f1):
        v1 = f1.verts[0]
        v2 = f1.verts[1]
        m1 = v2.co - v1.co
        sn = f1.normal
        vm = self.get_matrix(m1, sn.cross(m1), sn, v1.co)
        #return vm.inverted()
        fvm = {}
        for p in f1.loops:            
            fvm[p] = vm @ p.vert.co
        return fvm



    def fill_grid(self, bm, ps1, ps2, ps3, ps4):
        c1 = len(ps1)
        c2 = len(ps2)
        c3 = len(ps3)
        c4 = len(ps4)
        if c1 != c3 or c2 != c4:
            return 

        if c1 > c2:     
            if c1 < 4:
                return
            pp1 = ps1
            pp2 = list(reversed(ps3))
        else:
            pp1 = ps2
            pp2 = list(reversed(ps4))

        pp1.pop()
        pp2.pop()
        pp1.pop(0)
        pp1.append(pp1[-1].link_loop_next)
        cfs = set
        for a, b in zip(pp1, pp2):
            # gui.lines += [a.vert.co.copy(), b.vert.co.copy()]
            cf = self.cut_face(bm, a.vert, b.vert)
            if cf == None:
                continue
            cfs = cfs.union(set(cf))
        return list(cfs)
        



    def check_grid_direct(self, bm, f1):    
        sp = []
        t1 = 78
        t2 = 92        
        for p in f1.loops:
            d1 = p.calc_angle()
            d1 = math.floor(math.degrees(d1))
            if p.is_convex == False and d1 != 180:
                return
            elif d1 < t1:
                return
            elif d1 >= t1 and d1 <= t2:
                sp.append(p)
            elif d1 > t2 and d1 <= 179:
                return
            else:
                continue
        if len(sp) != 4:
            return
        ps1 = self.get_next_items(sp[0], sp[1])
        ps2 = self.get_next_items(sp[1], sp[2])
        ps3 = self.get_next_items(sp[2], sp[3])
        ps4 = self.get_next_items(sp[3], sp[0])
        
        # cf = self.fill_grid(bm, ps1, ps2, ps3, ps4)
        # return cf
        c1 = len(ps1)
        c2 = len(ps2)
        c3 = len(ps3)
        c4 = len(ps4)
        if c1 != c3 or c2 != c4:
            return        
        es = []
        if c1 > c2:
            if c1 == 1:
                return
            es1 = [p.edge for p in ps1]
            es2 = [p.edge for p in reversed(ps3)]
        else:
            if c2 == 1:
                return
            es1 = [p.edge for p in ps2]
            es2 = [p.edge for p in reversed(ps4)]

        # print(c1,c2,c3,c4)
        
        # cen = f1.calc_center_median()
        # for e in es1:
        #     a, b = e.verts
        #     v1 = a.co * 0.9 + cen * 0.1
        #     v2 = b.co  * 0.9 + cen * 0.1
        #     gui.lines += [v1, v2]

        # for e in es2:
        #     a, b = e.verts
        #     v1 = a.co * 0.9 + cen * 0.1
        #     v2 = b.co  * 0.9 + cen * 0.1            
        #     gui.lines += [v1, v2]

        es = es1 + es2   

        f1vs = [p.vert for p in f1.loops]
        if c1 > c2:
            if c1 == 1:
                return
            pst = list(reversed(ps3))
            pst.pop()
            ps1.pop(0)
            psp = [(a.vert, b.vert) for a, b in zip(ps1, pst)]
        else:
            if c2 == 1:
                return
            pst = list(reversed(ps4))
            pst.pop()
            ps2.pop(0)
            psp = [(a.vert, b.vert) for a, b in zip(ps2, pst)]

        bmesh.ops.delete(bm, geom=[f1], context='FACES_ONLY')
        res = bmesh.ops.grid_fill(bm, edges=es)   
        fs2 = res['faces']
        if fs2 != []:
            return fs2
        else:   
            f1b = bmesh.ops.contextual_create(bm, geom=f1vs)
            return self.simple_fill_cut(bm, f1b, psp)
        # return


        

    def simple_fill_cut(self, bm, f1b, psp):
        fs1 = set()
        for a, b in psp:
            # gui.lines += [a.vert.co.copy(), b.vert.co.copy()]
            fs = self.cut_face(bm, a, b)
            if fs == None:
                continue            
            fs1 = fs1.union( set(fs))
        return list(fs1)        


        
        
    def get_next_items(self, p1, p2):
        pm = p1
        ps = []
        while True:
            ps.append(pm)
            pm = pm.link_loop_next                        
            if pm == p2:
                break            
        return ps


    def get_linked_faces(self, f1, s1, fss):
        d1 = math.radians(self.prop_inset_angle)
        fs2 = []
        for e1 in f1.edges:
            if len(e1.link_faces) != 2:
                continue
            if e1.calc_face_angle() > d1:
                continue
            fs = list(e1.link_faces)
            fs.remove(f1)
            f2 = fs[0]
            if f2 in s1:
                continue
            if (f2 in fss) == False:
                continue
            fs2.append(f2)
            s1.add(f2)
        return fs2
            

    
    def group_faces(self, fss):
        s1 = set()
        total = []
        for f0 in fss:
            if f0 in s1:
                continue
            fst = [f0]
            s1.add(f0)
            for f1 in fst:
                fs = self.get_linked_faces(f1, s1, fss)
                if fs != []:
                    fst.extend(fs)
            total.append(fst)
        return total


    def group_inset(self, bm, total):
        plen = self.part * self.prop_inset_width
        for ps in total: 
            bmesh.ops.inset_region(bm, faces=ps, 
                use_even_offset=True,
                use_boundary=True, thickness=plen)



    def group_inset2(self, bm, total):
        plen = self.part * self.prop_inset_width
        for ps in total: 
            bmesh.ops.inset_region(bm, faces=ps, 
                use_even_offset=True,
                use_boundary=True, thickness=plen)
        
        ess = []
        for ps in total:            
            for f1 in ps:
                for e1 in f1.edges:
                    ess.append(e1)

        exte = []
        added = set()
        for ps in total:
            for f1 in ps:                
                for p in f1.loops:
                    for p2 in p.vert.link_loops:
                        if (p2.edge in ess) == False:
                            if p2.edge in added:
                                continue
                            else:
                                exte.append((p, p2))
                                added.add(p2.edge)
        cons = []
        dis = []
        backward = []
        cons2 = []
        over_angle = 180 - self.prop_inset_angle
        for p, pe in exte:
            p2 = pe.link_loop_radial_next
            p3 = pe.link_loop_next              
            d1 = p2.calc_angle()
            d2 = p3.calc_angle()
            d3 = d1+d2
            if d3 < math.radians(100):             
                self.cut_both_sides(pe, p2, p3, bm, cons, dis)
            elif d3 > math.radians(250):
                self.cut_both_concave(pe, p2, p3, bm, cons, dis, backward)

        for a, b in cons:
            self.chop_line(bm, a.vert, b.vert)
            # gui.lines += [a.vert.co.copy(), b.vert.co.copy()]

        for p1 in backward:
            self.cut_both_backward(p1, bm, cons2)
            # print(p1.vert.co)

        for a, b in cons2:
            self.chop_line(bm, a.vert, b.vert)
            # gui.lines += [a.vert.co.copy(), b.vert.co.copy()]

        dis = list(set(dis))
        bmesh.ops.dissolve_edges(bm, edges=dis, 
            use_verts=False, use_face_split=False)     




    def get_edge_point(self, p1, plen):
        e1 = p1.edge
        v1 = p1.vert
        v2 = e1.other_vert(v1)
        m1 = v2.co - v1.co
        c1 = m1.normalized() * plen + v1.co
        return c1


    def get_edge_point_far(self, p1, plen):
        e1 = p1.edge
        v1 = p1.vert
        v2 = e1.other_vert(v1)
        m1 = v1.co - v2.co
        c1 = m1.normalized() * plen + v2.co
        return c1


    def loop_anti(self, p1):
        p2 = p1.link_loop_prev.link_loop_radial_next
        return p2

    def is_same_length(self, p1, plen):
        e1 = p1.edge
        e1len = e1.calc_length()
        if e1len < plen or abs(e1len - plen) < 0.001:
            return True
        else:
            return False


    def cut_both_backward(self, p1, bm, cons2):
        plen = self.part * self.prop_inset_width 
        p2 = p1.link_loop_radial_next
        p3 = p2.link_loop_next.link_loop_next
        # self.draw_loop(p2)
        if self.is_same_length(p2, plen):
            c1 = self.get_edge_point(p3, plen)
            self.cut_forward_bisect(bm, p3.edge, c1)
            cons2.append((p2, p3.link_loop_next))

            if self.prop_inset_square_quad:
                p4 = p3.link_loop_radial_next
                p5 = self.nextloop(p4, 3)
                cons2.append((p4, p5))

        p4 = self.loop_anti(p1)
        p4 = self.loop_anti(p4)
        p4 = self.loop_anti(p4)
        p4 = self.loop_anti(p4)
        p5 = p4.link_loop_prev.link_loop_prev
        if self.is_same_length(p4, plen):
            c1 = self.get_edge_point_far(p5, plen)
            self.cut_forward_bisect(bm, p5.edge, c1)
            cons2.append((p4.link_loop_next, p5.link_loop_next))

            if self.prop_inset_square_quad:
                p6 = self.loop_anti(p4.link_loop_prev)
                p6 = p6.link_loop_next
                p7 = self.prevloop(p6, 3)
                cons2.append((p6, p7))
        # self.draw_loop(p4.link_loop_next)



    def cut_both_concave(self, p, p2, p3, bm, cons, dis, backward):        
        plen = self.part * self.prop_inset_width 

        pv = p2.link_loop_prev.link_loop_radial_next
        backward.append(pv)
        
        p4 = p2.link_loop_next        
        m1 = p4.link_loop_next.vert.co - p4.vert.co
        c1 = p4.vert.co + m1.normalized() * plen

        p5 = p.link_loop_prev
        m2 = p5.vert.co - p.vert.co
        c2 = p.vert.co + m2.normalized() * plen  

        e1 = p4.edge
        e1len = e1.calc_length()
        if e1len < plen or abs(e1len - plen) < 0.001:
            pass
        else:
            self.cut_forward_bisect(bm, e1, c1)

        e2 = p5.edge
        e2len = e2.calc_length()
        if e2len < plen or abs(e2len - plen) < 0.001:
            pass
        else:
            self.cut_forward_bisect(bm, p5.edge, c2)

        cons.append((p2, p.link_loop_prev))
        cons.append((p2, p4.link_loop_next))
        dis.append(p.edge)
        
        # self.chop_line(bm, p2.vert, p.link_loop_prev.vert)
        # # self.draw_loop(p4)
        # self.chop_line(bm, p2.vert, p4.link_loop_next.vert)
        # e1 = p.edge                
        # bmesh.ops.dissolve_edges(bm, edges=[e1], 
        #     use_verts=False, use_face_split=False)   

        

                        
    def cut_both_sides(self, p, p2, p3, bm, cons, dis):                
        plen = self.part * self.prop_inset_width
        c1 = p2.vert.co
        m1 = p.vert.co - c1
        m2 = p2.link_loop_prev.vert.co - c1
        m3 = p3.link_loop_next.vert.co - c1
        pro1 = m2.normalized() * plen
        pro2 = m3.normalized() * plen  
        e1 = p2.link_loop_prev.edge
        e1len = e1.calc_length()
        if e1len < plen or abs(e1len - plen) < 0.001:
            pass
        else:
            self.cut_forward_bisect(bm, e1, pro1+c1)

        e2 = p3.edge
        e2len = e2.calc_length()
        if e2len < plen or abs(e2len - plen) < 0.001:
            pass
        else:
            self.cut_forward_bisect(bm, e2, pro2+c1)  

        # self.chop_line(bm, p.vert, p2.link_loop_prev.vert)        
        # self.chop_line(bm, p.vert, p3.link_loop_next.vert)
        # e1 = p.edge                
        # bmesh.ops.dissolve_edges(bm, edges=[e1], 
        #     use_verts=False, use_face_split=False)   
        cons.append((p, p2.link_loop_prev))
        cons.append((p, p3.link_loop_next))        
        dis.append(p.edge)







    # def group_inset_adv(self, bm, total):
    #     d1 = math.radians(self.prop_inset_angle)
    #     plen = self.prop_plen * self.prop_inset_width        
    #     vslist = []
    #     for ps in total:
    #         inner_set = set()
    #         for f1 in ps:
    #             for p1 in f1.loops:
    #                 e1 = p1.edge                    
    #                 bound = False
    #                 if len(e1.link_faces) != 2:
    #                     bound = True
    #                 else:
    #                     if e1.calc_face_angle() > d1:
    #                         bound = True
    #                 if bound:
    #                     # inner_set.append(p1)
    #                     inner_set.add(p1.vert)

    #         res = bmesh.ops.inset_region(bm, faces=ps, 
    #             use_even_offset=True,
    #             use_boundary=True, thickness=plen)

    #         # pprint.pprint(res)
    #         fs2 = res['faces']
    #         outter_set = []
    #         for f1 in fs2:                
    #             for p1 in f1.loops:
    #                 e1 = p1.edge                    
    #                 bound = False
    #                 if len(e1.link_faces) != 2:
    #                     bound = True
    #                 else:
    #                     if e1.calc_face_angle() > d1:
    #                         bound = True
    #                 if bound:
    #                     outter_set.append(p1)

    #         # for p in outter_set:
    #         #     a = p.vert.co.copy()
    #         #     b = p.link_loop_next.vert.co.copy()
    #         #     gui.lines += [a, b]

    #         vslist.append((inner_set, outter_set))
    #         # inner_set.append((ess, fs2))
    #         # inner_set.append(fs2)
    #     self.connect_corners(bm, vslist)


    # def connect_corners(self, bm, vslist):
    #     part = self.prop_inset_width * 0.2
    #     cuts = []
    #     cuts2 = []
    #     cutsb = []
    #     cuts2b = []

    #     for inner_set, outter_set in vslist:
    #         for p2 in outter_set:
    #             p22 = p2.link_loop_next                
    #             deg = math.degrees(p22.calc_angle())
    #             if deg <= 60:                       
    #                 p3 = p22.link_loop_next                
    #                 if p3.vert in inner_set:                    
    #                     cuts.append((p22, p3))
    #                     p4 = p22.link_loop_radial_next
    #                     # self.draw_point(p4.vert.co.copy())
    #                     p5 = p4.link_loop_next
    #                     if p4.vert in inner_set:
    #                         cuts2.append((p5, p4))
    #             elif deg > 100:                    
    #                 p3 = p22.link_loop_next
    #                 if (p3.vert in outter_set) == False:                                      
    #                     cutsb.append((p22, p3))
    #                     p4 = p22.link_loop_radial_next
    #                     # self.draw_point(p4.vert.co.copy())
    #                     p5 = p4.link_loop_next
    #                     if (p4.vert in outter_set) == False:    
    #                         cuts2b.append((p5, p4))                    
        
    #     for a, b in cuts:            
    #         p2 = a.link_loop_prev            
    #         m1 = b.vert.co - a.vert.co
    #         m2 = p2.vert.co - a.vert.co
    #         pro1 = m1.project(m2)
    #         c1 = a.vert.co + pro1
    #         v3 = self.cut_forward_bisect(bm, p2.edge, c1)
    #         bmesh.ops.connect_verts(bm, verts=[v3, b.vert])


    #     for a, b in cuts2:
    #         p2 = a.link_loop_next
    #         m1 = b.vert.co - a.vert.co
    #         m2 = p2.vert.co - a.vert.co
    #         pro1 = m1.project(m2)
    #         c1 = a.vert.co + pro1
    #         if abs(pro1.length - a.edge.calc_length()) < 0.001:
    #             v3 = p2.vert
    #         else:
    #             v3 = self.cut_forward_bisect(bm, a.edge, c1)
    #         bmesh.ops.connect_verts(bm, verts=[v3, b.vert])

    #     for a, b in cutsb:
    #         p2 = b.link_loop_next
    #         m1 = a.vert.co - b.vert.co
    #         m2 = p2.vert.co - b.vert.co
    #         pro1 = m1.project(m2)            
    #         c1 = b.vert.co + pro1
    #         v3 = self.cut_forward_bisect(bm, b.edge, c1)
    #         bmesh.ops.connect_verts(bm, verts=[v3, a.vert])

    #     for a, b in cuts2b:
    #         p2 = b.link_loop_prev
    #         m1 = a.vert.co - b.vert.co
    #         m2 = p2.vert.co - b.vert.co
    #         pro1 = m1.project(m2)
    #         c1 = b.vert.co + pro1
    #         v3 = self.cut_forward_bisect(bm, p2.edge, c1)
    #         bmesh.ops.connect_verts(bm, verts=[v3, a.vert])

    #     for a, b in cutsb:       
    #         self.fix_concave_inset_a(bm, a, b)
    #         self.fix_concave_inset_b(bm, a, b)

    #     for a, b in cuts:
    #         e1 = a.edge
    #         res = bmesh.ops.dissolve_edges(bm, edges=[e1], 
    #             use_verts=False, use_face_split=False)            

    #     for a, b in cutsb:
    #         e1 = a.edge
    #         res = bmesh.ops.dissolve_edges(bm, edges=[e1], 
    #             use_verts=False, use_face_split=False)


                
            
    # def fix_concave_inset_a(self, bm, a, b):
    #     p2 = a.link_loop_prev
    #     p3 = p2.link_loop_radial_next      
    #     clen = p2.edge.calc_length()  
    #     if abs(p3.edge.calc_length() - clen) > 0.001:
    #         return
    #     p4 = p3.link_loop_prev
    #     p5 = p3.link_loop_next
    #     m1 = p5.edge.other_vert(p5.vert).co - p5.vert.co
    #     m2 = p4.vert.co - p5.vert.co            
    #     pro1 = m2.project(m1)
    #     c1 = p5.vert.co + pro1
    #     v3 = self.cut_forward_bisect(bm, p5.edge, c1)
    #     bmesh.ops.connect_verts(bm, verts=[v3, p4.vert])
    #     # self.fix_concave_outter(bm, a.link_loop_next.link_loop_radial_next)
        

    # def fix_concave_inset_b(self, bm, a, b):
    #     p2 = a.link_loop_radial_next.link_loop_next
    #     p3 = p2.link_loop_radial_next.link_loop_next
    #     clen = p2.edge.calc_length()
    #     if abs(p3.edge.calc_length() - clen) > 0.001:
    #         return
    #     p4 = p3.link_loop_next
    #     p5 = p3.link_loop_prev
    #     m1 = p5.link_loop_prev.vert.co - p5.vert.co
    #     m2 = p4.vert.co - p5.vert.co
    #     pro1 = m2.project(m1)
    #     c1 = p5.vert.co + pro1
    #     v3 = self.cut_forward_bisect(bm, p5.link_loop_prev.edge, c1)
    #     bmesh.ops.connect_verts(bm, verts=[v3, p4.vert])
    #     # k1 = a.link_loop_radial_next.link_loop_prev.link_loop_radial_next
    #     # self.fix_concave_outter(bm, k1.link_loop_next)


    # def fix_concave_outter(self, bm, a):                
    #     p1 = a.link_loop_next.link_loop_next.link_loop_next
    #     bmesh.ops.connect_verts(bm, verts=[p1.vert, a.vert])


    def get_between(self, p1, p2, fmax):
        pm = p1
        ps = []
        for i in range(fmax):
            pm = pm.link_loop_next
            if pm.vert == p2.vert:
                return ps
            ps.append(pm)
        return ps


    def div_inset(self, bm, fs):   
        # insmap = set()
        pss = []        
        for f1 in fs:
            ps = list(f1.loops)
            pss.append((f1, ps))

        pss2 = []
        for f1, ps in pss:
            psn = self.inset_con_adv(bm, f1, ps)
            pss2.append((f1, ps, psn))

        for f1, ps, psn in pss2:
            self.inset_con_adv_cut(bm, f1, ps, psn)
            

    # def inset_p_make_inner(self, bm, ps, plen):
    #     ffs = []       
    #     for p in ps:
    #         v1 = bm.verts.new(p.vert.co.copy())
    #         ffs.append(v1)
    #     f2 = bm.faces.new(ffs)
    #     f2.normal_update()
    #     psn = list(f2.loops)
    #     return psn

    # def inset_p_fix_pos(self, ps, psn, f1, plen):
    #     for p, pm in zip(ps, psn):
    #         p2 = p.link_loop_next
    #         p3 = p.link_loop_prev
    #         m1 = (p2.vert.co - p.vert.co).normalized()
    #         m2 = (p3.vert.co - p.vert.co).normalized()
    #         if m1.length == 0 or m2.length == 0:
    #             return
    #         conc = self.check_concave(p)
    #         if conc == False:
    #             co1 = p.vert.co + (m1+m2).normalized() * plen
    #         elif conc == True or conc == None:
    #             sn = f1.normal
    #             m3 = self.mid_line(m1, m2, sn)
    #             co1 = p.vert.co + m3.normalized() * plen
    #         pm.vert.co = co1        

    # def inset_p_cut_outter(self, ps, psn, bm, plen):
    #     for p, pm in zip(ps, psn):
    #         conc =self.check_concave(p)
    #         if conc == True:
    #             continue            
    #         elif conc == False:            
    #             self.loop_near_cut(p, True, plen, bm)
    #             self.loop_near_cut(p, False, plen, bm)                
    #             # insmap.add((p.vert, p.edge))
    #             # insmap.add((p.vert, p.link_loop_prev.edge))

    # def inset_p_cut_inner(self, ps, psn, bm, plen):
    #     for p, pm in zip(ps, psn):
    #         conc = self.check_concave(p)                           
    #         if conc == True:
    #             self.loop_near_cut(pm, True, plen, bm)
    #             self.loop_near_cut(pm, False, plen, bm)

    # def inset_p_make_corner(self, ps, psn, bm):
    #     for p, pm in zip(ps, psn):
    #         conc = self.check_concave(p)                           
    #         if conc == True:        
    #             p2 = pm.link_loop_next
    #             p3 = pm.link_loop_prev
    #             vs2 = [p2.vert, pm.vert, p3.vert, p.vert]
    #             bmesh.ops.contextual_create(bm, geom=vs2)
    #         elif conc == False:
    #             p2 = p.link_loop_next
    #             p3 = p.link_loop_prev                
    #             vs2 = [pm.vert, p2.vert, p.vert, p3.vert]
    #             bmesh.ops.contextual_create(bm, geom=vs2)        


    # def inset_p_make_border(self, ps, psn, bm, f1):
    #     ps2 = ps[1:] + [ps[0]]
    #     psn2 = psn[1:] + [psn[0]]
    #     for p, pm, p2, pm2 in zip(ps, psn, ps2, psn2):            
    #         conc = self.check_concave(p)            
    #         if conc == True:
    #             pa = pm.link_loop_next
    #         elif conc == False:
    #             pa = pm
    #         elif conc == None:
    #             pa = pm

    #         conc = self.check_concave(p2)
    #         if conc == False:
    #             pb = pm2
    #         elif conc == True:
    #             pb = pm2.link_loop_prev
    #         elif conc == None:
    #             pb = pm2

    #         conc = self.check_concave(p)
    #         if conc == False:
    #             pc = p.link_loop_next
    #         elif conc == True:
    #             pc = p
    #         elif conc == None:
    #             pc = p

    #         conc = self.check_concave(p2)
    #         if conc == False:
    #             pd = p2.link_loop_prev
    #         elif conc == True:
    #             pd = p2
    #         elif conc == None:
    #             pd = p2

    #         vs = [pa.vert, pb.vert, pd.vert, pc.vert]
    #         try:
    #             bmesh.ops.contextual_create(bm, geom=vs)
    #         except:
    #             pass
    #     bmesh.ops.delete(bm, geom=[f1], context='FACES_ONLY')        



    # def inset_con_adv(self, bm, f1, ps):
    #     plen = self.prop_inset_width   
    #     psn = self.inset_p_make_inner(bm, ps, plen)
    #     self.inset_p_fix_pos(ps, psn, f1, plen)
    #     return psn

    # def inset_con_adv_cut(self, bm, f1, ps, psn):
    #     plen = self.prop_inset_width   
    #     self.inset_p_cut_outter(ps, psn, bm, plen)
    #     self.inset_p_cut_inner(ps, psn, bm, plen)
    #     self.inset_p_make_corner(ps, psn, bm)
    #     self.inset_p_make_border(ps, psn, bm, f1)




    def check_concave(self, p):
        d1 = round(abs(math.degrees(p.calc_angle())))     
        # gui.addtext(p.vert.co.copy(), str(p.is_convex) + ',' + str(d1))   
        
        if p.is_convex and (d1 > 160):
            return None

        if p.is_convex == False and d1 == 180:            
            return None

        if p.is_convex:
            return False
        else:
            return True
            

    def loop_near_cut(self, p, forward, plen, bm):
        if forward:
            p2 = p.link_loop_next
            # k1 = (p.edge, p.vert)
        else:
            p2 = p.link_loop_prev
            # k1 = (p2.edge, p.vert)
        m1 = p2.vert.co - p.vert.co
        m1 = m1.normalized() * plen 
        if forward:
            elen = p.edge.calc_length()
            if plen > elen:
                return
            if abs(plen - elen) < 0.001:
                return
        else:
            elen = p2.edge.calc_length()
            if plen > elen:
                return
            if abs(plen - elen) < 0.001:
                return

        c1 = p.vert.co + m1     
        if forward:
            v1 = self.cut_forward_bisect(bm, p.edge, c1)
        else:
            v1 = self.cut_forward_bisect(bm, p2.edge, c1)

        
    def edge_near_cut(self, v1, e1, plen, bm):
        v2 = e1.other_vert(v1)        
        m1 = v2.co - v1.co
        c1 = v1.co + m1.normalized() * plen
        v3 = self.cut_forward_bisect(bm, e1, c1)
        return v3

                    

    # def inset_con_skip(self, bm, a, b, bs, sn):
    #     plen = self.prop_inset_width
    #     blen = len(bs)
    #     p2 = b.link_loop_next
    #     p3 = a.link_loop_prev
    #     m1 = (p2.vert.co - b.vert.co).normalized()
    #     m2 = (p3.vert.co - a.vert.co).normalized()
    #     if m1.length == 0 or m2.length == 0:
    #         return
    #     c1 = b.vert.co + m1 * plen
    #     c2 = a.vert.co + m2 * plen
    #     self.cut_forward_bisect(bm, b.edge, c1)
    #     self.cut_forward_bisect(bm, p3.edge, c2)
    #     p2 = b.link_loop_next
    #     p3 = a.link_loop_prev  
    #     e1 = self.chop_line(bm, p2.vert, p3.vert)
    #     if e1 == None:            
    #         return            
    #     if blen > 0:
    #         ep1 = None
    #         ep2 = None
    #         for pk in e1.link_loops:
    #             if pk.vert == p3.vert:
    #                 ep1 = pk
    #             if pk.vert == p2.vert:
    #                 ep2 = pk
    #         if ep1 == None or ep2 == None:
    #             return
    #         res = bmesh.ops.subdivide_edges(bm, edges=[e1], 
    #             cuts=blen, use_grid_fill=False)            
    #         bs2 = self.get_between(ep1, ep2, blen * 2)
    #         for a, b in zip(bs, bs2):
    #             self.inset_con_link(bm, a, b, sn)            
        

        
    def inset_con_link(self, bm, a, b, sn):
        plen = self.prop_inset_width
        p1 = b.link_loop_prev
        p2 = b.link_loop_next
        m1 = a.link_loop_prev.vert.co - a.vert.co
        m2 = a.link_loop_next.vert.co - a.vert.co
        m3 = self.mid_line(m1, m2, sn) * -1
        b.vert.co = a.vert.co + m3.normalized() * plen
        p1 = b.link_loop_prev        
        p2 = b.link_loop_next
        c1 = b.vert.co + m1.normalized() * plen
        c2 = b.vert.co + m2.normalized() * plen
        self.cut_forward_bisect(bm, p1.edge, c1)
        self.cut_forward_bisect(bm, b.edge, c2)
        p1 = b.link_loop_prev        
        p2 = b.link_loop_next
        self.chop_line(bm, p1.vert, a.vert)
        self.chop_line(bm, p2.vert, a.vert)
        # p1 = b.link_loop_prev        
        # p2 = b.link_loop_next
        # m5 = p1.vert.co - a.vert.co
        # m6 = p2.vert.co - a.vert.co
        # p1.vert.co = a.vert.co + m5.normalized() * max(plen, m5.length)
        # p2.vert.co = a.vert.co + m6.normalized() * max(plen, m6.length)


                    

    # def inset_two(self, bm, p, sn):
    #     plen = self.prop_inset_width
    #     p2 = p.link_loop_next
    #     p3 = p.link_loop_prev
    #     m1 = (p2.vert.co - p.vert.co).normalized()
    #     m2 = (p3.vert.co - p.vert.co).normalized()
    #     if m1.length == 0 or m2.length == 0:
    #         return
    #     c1 = p.vert.co + m1 * plen / 2
    #     c2 = p.vert.co + m2 * plen / 2
    #     self.cut_forward_bisect(bm, p.edge, c1)
    #     self.cut_forward_bisect(bm, p3.edge, c2)
    #     p2 = p.link_loop_next
    #     p3 = p.link_loop_prev
    #     e1 = self.chop_line(bm, p2.vert, p3.vert)
    #     if e1 == None:
    #         return
    #     bmesh.ops.subdivide_edges(bm, edges=[e1], 
    #         cuts=3, use_grid_fill=False)
        
    #     p2 = p.link_loop_next
    #     p3 = p.link_loop_prev
    #     m4 = sn.cross(self.loop_vec(p)).normalized()
    #     p2.link_loop_next.vert.co = p2.vert.co + m4 * plen
    #     m5 = sn.cross(self.loop_vec(p3)).normalized()
    #     p3.link_loop_prev.vert.co = p3.vert.co + m5 * plen
        
    #     m3 = (m1 + m2).normalized()
    #     sk = sk = m3.cross(m1).length
    #     c3 = p.vert.co + (plen/ sk) * m3
    #     pm = p3.link_loop_prev.link_loop_prev
    #     pm.vert.co = c3
    #     self.chop_line(bm, p.vert, pm.vert)




    # def inset_con(self, bm, p, sn):
    #     plen = self.prop_inset_width
    #     p2 = p.link_loop_next
    #     p3 = p.link_loop_prev
    #     m1 = (p2.vert.co - p.vert.co).normalized()
    #     m2 = (p3.vert.co - p.vert.co).normalized()
    #     if m1.length == 0 or m2.length == 0:
    #         return
    #     m3 = (m1 + m2).normalized()
    #     sk2 = m3.cross(m1).length / m3.dot(m1)
    #     c1 = p.vert.co + m1 * (plen/sk2)
    #     c2 = p.vert.co + m2 * (plen/sk2)
    #     self.cut_forward_bisect(bm, p.edge, c1)
    #     self.cut_forward_bisect(bm, p3.edge, c2)
    #     p2 = p.link_loop_next
    #     p3 = p.link_loop_prev
    #     e1 = self.chop_line(bm, p2.vert, p3.vert)
    #     if e1 == None:
    #         return        
    #     # d1 = m1.angle(m2) / 2
    #     # c3 = p.vert.co + (plen/ math.sin(d1)) * m3
    #     sk = m3.cross(m1).length
    #     c3 = p.vert.co + (plen/ sk) * m3
    #     self.cut_forward_bisect(bm, e1, c3)
        
        
        


        
    # def get_next_items(self, p1, p2):
    #     pm = p1
    #     ps = []
    #     while True:
    #         pm = pm.link_loop_next                        
    #         if pm == p2:
    #             break
    #         ps.append(pm)
    #     return ps

    def is_bound(self, p):        
        keepangle = self.prop_keep_edge_angle
        for e1 in p.vert.link_edges:            
            if e1.is_boundary:
                return True
            
            if len(e1.link_faces) == 2:
                d1 = e1.calc_face_angle()                        
                if d1 > math.radians(keepangle):
                    return True
        return False


    def is_edge_bound(self, e1):
        keepangle = self.prop_keep_edge_angle
        if e1.is_boundary:
            return True
        
        if len(e1.link_faces) == 2:
            d1 = e1.calc_face_angle()                        
            if d1 > math.radians(keepangle):
                return True
        return False        


    def filter_pole(self, f1):
        sn = f1.normal
        if sn.length == 0:
            return []
        ps3 = []
        dmin = math.radians(2)
        # keepangle = self.prop_keep_edge_angle
        # boundary = []
        concaves = []
        for p in f1.loops:
            if p.is_convex == False:
                concaves.append(p)
                continue
            if self.is_bound(p):
                fs = p.vert.link_faces
                ct = 0
                for f2 in fs:
                    if f2.normal.length == 0:
                        continue
                    d2 = f2.normal.angle(sn)
                    if d2 < dmin:
                        ct += 1
                # gui.addtext(p.vert.co.copy(), ct)
                if ct < 2:
                    ps3.append(p)
                    # boundary.append(p)
            else:
                ps3.append(p)
        
        return concaves + ps3
        # return ps3, boundary
               

    def div_faces_quad(self, bm, f1):
        self.even_cut_simple(bm, f1)        
        # for p in fps:
        #     self.draw_point(p.vert.co.copy())

        fps = list(f1.loops)
        if len(fps) <= 4:
            return []  

        if self.prop_boundary_edge_flow:
            fps = self.filter_pole(f1)        
            
        fss1 = self.check_grid_direct(bm, f1)
        if fss1 != None:
            return fss1        
        
        # return []
        spt = None
        sdm = None        
        # self.vec_find_min(f1)
        for i1, p in enumerate(fps):
            # if p.vert in used:
            #     continue
            for i2, p2 in enumerate(fps):
                if p == p2:
                    continue
                if i1 > i2:
                    continue
                d1, d2 = self.get_angles(p, p2)
                d3, d4 = self.get_angles(p2, p)
                d90 = math.radians(90)
                dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)

                if sdm != None and dm > sdm:
                    continue
                # dm = abs(d1-d2) + abs(d3-d4)
                d30 = math.radians(30)
                if d1 < d30 or d2 < d30:
                    continue
                if d3 < d30 or d4 < d30:
                    continue
                d1, d2 = self.get_real_angle(p, p2, f1.normal)
                if d1 < d2:
                    continue                

                if self.is_crossed_old(p, p2, f1):
                    continue

                # if self.is_parallel_close(p, p2, f1):
                #     continue

                if sdm == None or dm < sdm:
                    sdm = dm
                    spt = (p, p2)

        if spt == None:
            return []
        p, pm = spt

        cf = self.cut_face(bm, p.vert, pm.vert)
        if cf == None:
            return []
        lencf = len(cf)
        if lencf == 0:
            return []
        else:            
            # self.auto_dissolve(bm, cf)
            return cf


    def is_parallel_close(self, p, p2, f1):
        m1 = p2.vert.co - p.vert.co
        plen = self.part / 2
        for pm in f1.loops:
            if pm == p or pm == p2:
                continue
            # pm2 = pm.link_loop_next
            # mx = pm2.vert.co - pm.vert.co
            # if m1.cross(mx).length > 0.0001:
            #     continue
            m2 = pm.vert.co - p.vert.co
            pro1 = m2.project(m1)
            m3 = m2 - pro1
            if m3.length < plen:
                # gui.lines += [p.vert.co, p2.vert.co]
                return True
            # v1 = p.vert.co
            # v2 = p2.vert.co
            # v3 = pm.vert.co
            # v4 = pm2.vert.co
            # res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)
            # if res == None:
            #     continue
            # k1, k2 = res        
            # gui.lines += [k1, k2]
            # print((k2 - k1).length)
            # if (k2 - k1).length < plen:
            #     return True
            
        return False



    def div_faces_quad_concave(self, bm, f1):
        self.even_cut_simple(bm, f1)        
        if len(f1.loops) <= 4:
            return []
        # fss1 = self.check_grid_direct(bm, f1)
        # if fss1 != None:
        #     return fss1
        # return []
        spt = None
        sdm = None
        fcon = [p for p in f1.loops if p.is_convex == False \
            and self.degree_int(p) != 180 ]
        # self.vec_find_min(f1)
        for p in fcon:
            # if p.vert in used:
            #     continue
            for p2 in f1.loops:
                if p == p2:
                    continue
                d1, d2 = self.get_angles(p, p2)
                d3, d4 = self.get_angles(p2, p)
                d90 = math.radians(90)
                dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)

                if sdm != None and dm > sdm:
                    continue
                # dm = abs(d1-d2) + abs(d3-d4)
                d30 = math.radians(5)
                if d1 < d30 or d2 < d30:
                    continue
                if d3 < d30 or d4 < d30:
                    continue
                d1, d2 = self.get_real_angle(p, p2, f1.normal)
                if d1 < d2:
                    continue                

                if self.is_crossed_old(p, p2, f1):
                    continue

                if sdm == None or dm < sdm:
                    sdm = dm
                    spt = (p, p2)

        if spt == None:
            return []
        p, pm = spt

        cf = self.cut_face(bm, p.vert, pm.vert)
        if cf == None:
            return []
        lencf = len(cf)
        if lencf == 0:
            return []
        else:            
            # self.auto_dissolve(bm, cf)
            return cf





    def div_faces_quad_p1(self, bm, f1):
        self.even_cut_simple(bm, f1)        
        if len(f1.loops) <= 4:
            return []        
        # fvm = self.get_fvm(f1)
        # d179 = math.radians(179)
        # fcon = [p for p in f1.loops if p.is_convex == False and p.calc_angle() <= d179]
        # if len(fcon) == 0:
        #     return [f1]
        # ps = []
        spt = None
        sdm = None

        # self.vec_find_min(f1)
        for i1, p in enumerate(f1.loops):
            # if p.vert in used:
            #     continue
            for i2, p2 in enumerate(f1.loops):
                if p == p2:
                    continue
                if i1 > i2:
                    continue
                # if self.get_count(p, p2, f1) < 3:
                #     continue
                # if p2.vert in used:
                #     continue
                d1, d2 = self.get_angles(p, p2)
                d3, d4 = self.get_angles(p2, p)
                d90 = math.radians(90)
                dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)

                if sdm != None and dm > sdm:
                    continue
                # dm = abs(d1-d2) + abs(d3-d4)
                d30 = math.radians(30)
                if d1 < d30 or d2 < d30:
                    continue
                if d3 < d30 or d4 < d30:
                    continue

                d1, d2 = self.get_real_angle(p, p2, f1.normal)
                if d1 < d2:
                    continue                

                # if self.get_real_angle_cmp(p, p2, f1.normal):
                #     continue

                # if self.is_crossed(p, p2, f1, fvm):
                #     continue
                if self.is_crossed_old(p, p2, f1):
                    continue
                # short1 = self.get_shortest(p, p2, f1)
                # if short1 < self.plen * 2:
                #     continue                
                # ps.append((dm, (p, p2)))
                if sdm == None or dm < sdm:
                    sdm = dm
                    spt = (p, p2)
        #_, pm = min(ps, key=lambda e:e[0])
        # print('total', len(f1.loops))
        # print(len(ps2), len(ps3))            
        
        # if len(ps) == 0:
        #     return [f1]
        # _, pt = min(ps, key=lambda e:e[0])            
        # p, pm = pt
        if spt == None:
            return []
        p, pm = spt

        # self.draw_point(pm.vert.co)            
        # used.add(pm.vert)
        # used.add(p.vert)
        # gui.lines += [p.vert.co, pm.vert.co]   

        cf = self.cut_face(bm, p.vert, pm.vert)
        if cf == None:
            return []
        lencf = len(cf)
        if lencf == 0:
            return []
        else:
            # self.auto_dissolve(bm, cf)
            return cf
        # elif lencf == 1:
        #     cf2 = self.div_faces_quad(bm, cf[0])
        #     return cf2
        # else:
        #     cf2 = self.div_faces_quad(bm, cf[0])
        #     cf3 = self.div_faces_quad(bm, cf[1])
        #     return cf2 + cf3        
        # cf2 = self.div_faces_quad(bm, cf[0])
        # cf3 = self.div_faces_quad(bm, cf[1])
        # return cf2 + cf3
            # return cf
        # return [f1]


    def nextloop(self, p1, n):
        for i in range(n):
            p1 = p1.link_loop_next
        return p1



    def prevloop(self, p1, n):
        for i in range(n):
            p1 = p1.link_loop_prev
        return p1



    def div_faces_quad_any_2(self, bm, f1):
        fps = list(f1.loops)
        if len(fps) <= 4:
            return []    
        spt = None
        sdm = None        
        for i1, p in enumerate(fps):
            # if p.vert in used:
            #     continue
            for i2, p2 in enumerate(fps):
                if p == p2:
                    continue
                if i1 > i2:
                    continue
                d1, d2 = self.get_angles(p, p2)
                d3, d4 = self.get_angles(p2, p)
                d90 = math.radians(90)
                dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)

                if sdm != None and dm > sdm:
                    continue

                if self.nextloop(p, 2) == p2:
                    continue
                if self.nextloop(p2, 2) == p:
                    continue
                
                # dm = abs(d1-d2) + abs(d3-d4)
                d1, d2 = self.get_real_angle(p, p2, f1.normal)
                if d1 < d2:
                    continue

                if self.is_crossed_old(p, p2, f1):
                    continue

                # if self.is_parallel_close(p, p2, f1):
                #     continue

                if sdm == None or dm < sdm:
                    sdm = dm
                    spt = (p, p2)
        if spt == None:
            return []
        p, pm = spt
        cf = self.cut_face(bm, p.vert, pm.vert)
        if cf == None:
            return []
        lencf = len(cf)
        if lencf == 0:
            return []
        else:
            # self.auto_dissolve(bm, cf)
            return cf



    def div_faces_quad_any(self, bm, f1):
        self.even_cut_simple(bm, f1)        
        fps = list(f1.loops)
        if len(fps) <= 4:
            return []    

        if self.prop_boundary_edge_flow:
            fps = self.filter_pole(f1)                    

        fss1 = self.check_grid_direct(bm, f1)
        if fss1 != None:
            return fss1
        spt = None
        sdm = None        
        for i1, p in enumerate(fps):
            # if p.vert in used:
            #     continue
            for i2, p2 in enumerate(fps):
                if p == p2:
                    continue
                if i1 > i2:
                    continue
                d1, d2 = self.get_angles(p, p2)
                d3, d4 = self.get_angles(p2, p)
                d90 = math.radians(90)
                dm = abs(d1-d90) + abs(d2-d90) + abs(d3-d90) + abs(d4-d90)

                if sdm != None and dm > sdm:
                    continue
                # dm = abs(d1-d2) + abs(d3-d4)
                d1, d2 = self.get_real_angle(p, p2, f1.normal)
                if d1 < d2:
                    continue

                if self.is_crossed_old(p, p2, f1):
                    continue

                if self.is_parallel_close(p, p2, f1):
                    continue                

                if sdm == None or dm < sdm:
                    sdm = dm
                    spt = (p, p2)
        if spt == None:
            return []
        p, pm = spt
        cf = self.cut_face(bm, p.vert, pm.vert)
        if cf == None:
            return []
        lencf = len(cf)
        if lencf == 0:
            return []
        else:
            # self.auto_dissolve(bm, cf)
            return cf
   

    def fix_concave(self, bm, f1, depth):
        if len(f1.loops) <=4:
            return []
        if depth > 5:
            return []
        # d179 = math.radians(179)
        # and p.calc_angle() <= d179
        fcon = [p for p in f1.loops if p.is_convex == False \
            and self.degree_int(p) != 180 ]
        # fcon = [p for p in f1.loops if p.is_convex == False and p.calc_angle() <= d179]
        for p in fcon:
            cf = self.direct_cut(bm, p, f1)
            cf2 = []
            if cf == None:
                return []
            for f2 in cf:
                cf2 += self.fix_concave(bm, f2, depth + 1)
            return cf2
        return []


    def degree_int(self, p):
        d1 = p.calc_angle()
        d2 = math.degrees(d1)
        return math.floor(d2)


    def direct_cut(self, bm, p1, f1):
        ths = self.part * 0.05
        sn = f1.normal
        p2 = p1.link_loop_next
        p3 = p1.link_loop_prev
        m1 = p2.vert.co - p1.vert.co
        m2 = p3.vert.co - p1.vert.co
        m3 = self.mid_line(m1,m2, sn)        
        pco = p1.vert.co + m3.normalized() * 1000            
        css = self.get_crossed_all(p1, pco, f1)
        if len(css) == 0:
            return
        _, pin, pn = min(css, key=lambda e: e[0])
        a, b = pn.edge.verts 
        # gui.lines += [p1.vert.co, pco]
        # print(m3)       
        # if (a.co - pin).length < ths:
        #     cf = self.cut_face(bm, p1.vert, a)
        # elif (b.co - pin).length < ths:
        #     cf = self.cut_face(bm, p1.vert, b)
        # else:            
        #     v2 = self.cut_forward(bm, pn.edge, pin)
        #     cf = self.cut_face(bm, p1.vert, v2)
        # return cf
        v2 = self.cut_forward(bm, pn.edge, pin)
        cf = self.cut_face(bm, p1.vert, v2)
        return cf        




    def auto_dissolve(self, bm):
        flats = self.flatedges
        for e1 in flats:
            if (e1 in flats) == False:
                continue
            if self.has_flat_faces(e1) == False:
                continue
            if self.is_edge_sharp_angles(e1) == False:
                continue                
            res = bmesh.ops.dissolve_edges(bm, edges=[e1], 
                use_verts=False, use_face_split=False)
        
                
                

    def is_edge_sharp_angles(self, e1):
        sharp = math.radians(45)
        ps = e1.link_loops        
        for p in ps:
            d = p.calc_angle()            
            d2 = p.link_loop_next.calc_angle()
            if d < sharp:
                return True
            if d2 < sharp:
                return True
        return False
        



    def has_flat_faces(self, e1):
        if e1.is_boundary:
            return False
        if len(e1.link_faces) != 2:
            return False
        deg = e1.calc_face_angle()
        if deg > math.radians(1):
            return False
        else:
            return True



    def get_flat_edges(self, bm, sel):
        deg1 = math.radians(1)
        es = []
        for f1 in sel:
            for e1 in f1.edges:            
                if len(e1.link_faces) != 2:
                    continue
                d1 = e1.calc_face_angle()
                if d1 < deg1:
                    f2, f3 = e1.link_faces
                    if (f2.select and f3.select == False) or \
                        (f2.select == False and f3.select):
                        pass
                    else:
                        es.append(e1)
        es = list(set(es))
        return es


    def dissolve(self, bm, es):
        for e1 in es:
            if e1.is_valid:
                es2 = [e1]
                bmesh.ops.dissolve_edges(bm, edges=es2, 
                    use_verts=False, use_face_split=False)



    def get_shortest(self, p, p2, f1):        
        sn = f1.normal
        m1 = p2.vert.co - p.vert.co
        vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        vm2 = vm.inverted()
        ms = []
        for p3 in f1.loops:
            if p3 == p or p3 == p2:
                continue
            if p3.link_loop_next == p or p3.link_loop_next == p2:
                continue
            k1 = vm2 @ p3.vert.co
            k2 = vm2 @ p3.link_loop_next.vert.co
            ms.append(abs(k1.y))
            ms.append(abs(k2.y))
        return min(ms, key=lambda e:e)
           




    def get_real_angle_cmp(self, p, pm, sn):
        # p3 = p.link_loop_next
        # m1 = p3.vert.co - p.vert.co
        # vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        # vm2 = vm.inverted()        
        # vp = vm2 @ pm.vert.co
        # return vp.y < 0
        p3 = p.link_loop_next
        m1 = p3.vert.co - p.vert.co
        vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        vm2 = vm.inverted()        
        vp = vm2 @ pm.vert.co
        knext = vp.y > 0
        p4 = p.link_loop_prev
        m1 = p.vert.co - p4.vert.co
        vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        vm2 = vm.inverted()        
        vp = vm2 @ pm.vert.co
        knext2 = vp.y > 0
        if knext and knext2:
            return False
        else:
            return True        



    def get_real_angle_cmp_ext(self, p, co, sn):
        p3 = p.link_loop_next
        m1 = p3.vert.co - p.vert.co
        vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        vm2 = vm.inverted()        
        vp = vm2 @ co
        knext = vp.y > 0

        p4 = p.link_loop_prev
        m2 = p.vert.co - p4.vert.co
        vm3 = self.get_matrix(m2, sn.cross(m2), sn, p.vert.co)
        vm4 = vm3.inverted()        
        vp2 = vm4 @ co
        knext2 = vp2.y > 0
        if knext and knext2:
            # gui.lines = []
            # gui.lines += [p.vert.co, co]
            # gui.lines += [p.vert.co, vm @ Vector((1, 0, 0))]
            # gui.lines += [p.vert.co, vm3 @ Vector((1,0,0))]
            return False
        else:
            return True


    def get_real_angle(self, p, pm, sn):
        p2 = p.link_loop_prev
        m1 = p2.vert.co - p.vert.co
        vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        vm2 = vm.inverted()
        p3 = p.link_loop_next
        vp = vm2 @ pm.vert.co
        deg = math.atan2(vp.y, vp.x)        
        if deg < 0:
            deg += math.radians(360)
        vp2 = vm2 @ p3.vert.co
        deg2 = math.atan2(vp2.y, vp2.x)        
        if deg2 < 0:
            deg2 += math.radians(360)        
        return abs(deg), abs(deg2)


    def get_real_angle_co(self, p, co, sn):
        p2 = p.link_loop_prev
        m1 = p2.vert.co - p.vert.co
        vm = self.get_matrix(m1, sn.cross(m1), sn, p.vert.co)
        vm2 = vm.inverted()
        p3 = p.link_loop_next
        vp = vm2 @ co
        deg = math.atan2(vp.y, vp.x)        
        if deg < 0:
            deg += math.radians(360)
        vp2 = vm2 @ p3.vert.co
        deg2 = math.atan2(vp2.y, vp2.x)        
        if deg2 < 0:
            deg2 += math.radians(360)        
        return abs(deg), abs(deg2)


    
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



    def check_double_div(self, bm, fs, f1):
        if fs != []:
            return fs

        if f1.is_valid == False:
            return []

        if len(f1.loops) <= 4:
            return []

        res = self.even_cut_simple(bm, f1, 1)
        if res:
            return [f1]
        else:
            return []



    def even_cut_simple(self, bm, f1):
        partlen = self.part
        es = []
        part2 = partlen
        
        for p in f1.loops:            
            mlen = p.edge.calc_length()
            if mlen > part2:
                ct = round(mlen / part2) - 1
                if ct > 0:
                    es.append((p.edge, ct))
        
        for e1, ct in es:
            # res1 = bmesh.ops.subdivide_edges(bm, edges=[e1], 
            #     cuts=ct, use_grid_fill=False)        
            bmesh.ops.bisect_edges(bm, edges=[e1], cuts=ct)


    def even_cut_single(self, bm, e1):
        partlen = self.part
        mlen = e1.calc_length()
        if mlen > partlen:
            ct = math.ceil(mlen / partlen) - 1            
            res1 = bmesh.ops.subdivide_edges(bm, edges=[e1], 
                cuts=ct, use_grid_fill=False)        
            # bmesh.ops.bisect_edges(bm, edges=[e1], cuts=ct)


    def even_cut(self, bm, f1):
        partlen = self.part
        for p in f1.loops:
            mlen = p.edge.calc_length()
            if mlen > partlen:
                ct = math.ceil(mlen / partlen) - 1
                self.cut_quad(bm, f1, p, ct)


  
    def get_count(self, p1, p2, f1):
        i = 0
        s1 = 0
        s2 = 0
        for p in f1.loops:            
            if p == p1:
                s1 = i
            if p == p2:
                s2 = i
            i += 1
        return abs(s1 - s2)





    def mid_line(self, m1, m2, sn):
        fm1 = sn.cross(m1.normalized())
        fm2 = m2.normalized().cross(sn)
        m3 = (fm1 + fm2).normalized()
        return m3
       
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

            self.prop_size_multiplier = 1.0

            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}

    
    # @classmethod
    # def poll(cls, context):
    #     active_object = context.active_object
    #     selecting = active_object is not None and active_object.type == 'MESH'        
    #     editing = context.mode == 'EDIT_MESH' 
    #     is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
    #     return selecting and editing 


    # def invoke2(self, context, event):
    #     if context.edit_object:
    #         self.process(context)
    #         return {'FINISHED'} 
    #     else:
    #         return {'CANCELLED'}


    # def draw_point(self, p1):
    #     gui.lines += [p1 + Vector((0.02, 0, 0)), p1 - Vector((0.02, 0, 0))]
    #     gui.lines += [p1 + Vector((0, 0.02, 0)), p1 - Vector((0, 0.02, 0))]



    # def step(self):
    #     bm = self.bm
    #     gui.lines = []
    #     gui.textpos = []

    #     if len(self.fss) == 0:
    #         return
    #     f2 = self.fss.pop(0)        
    #     fsnew = self.div_faces_quad(bm, f2)
    #     self.fss.extend(fsnew)  

    #     obj = bpy.context.active_object                
    #     me = bpy.context.active_object.data
    #     bmesh.update_edit_mesh(me)           


    # def modal(self, context, event):        
    #     context.area.tag_redraw()
    #     if event.type == 'Q':
    #         if event.value == 'PRESS':
    #             self.step()
    #             return {'RUNNING_MODAL'}

    #     elif event.type == 'ESC':
    #         if event.value == 'PRESS':
    #             gui.draw_handle_remove()
    #             return {'CANCELLED'}

    #     if 'MOUSE' in event.type:
    #         return {'PASS_THROUGH'}

    #     return {'PASS_THROUGH'}


    # def invoke(self, context, event):
    #     if context.edit_object:
    #         context.window_manager.modal_handler_add(self)
    #         gui.draw_handle_add((self, context))
    #         gui.text_handle_add((self, context))
    #         gui.txtall = ['Please press Esc to exit']

    #         self.process(context)            
    #         return {'RUNNING_MODAL'} 
    #     else:
    #         return {'CANCELLED'}

