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
    FloatVectorProperty,
)

import pprint
import itertools
import bpy




class QuickBridgeOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.quick_bridge_operator"
    bl_label = "Quick Bridge —— 桥接面"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "快速桥接两个面"
    #, "GRAB_CURSOR", "BLOCKING"



    prop_cut: IntProperty(
        name="切割次数",
        description="定义桥接切割的数量",
        default=3,
        min=1
    )    


    prop_size: FloatProperty(
        name="尺寸",
        description="桥接的尺寸",
        default=5,
        min = 0
    )    

    prop_rotation: FloatProperty(
        name="旋转",
        description="沿桥接路径旋转",
        default=0,
    )    


    prop_auto_fit: BoolProperty(
        name="自动调整旋转",
        description="自动调整端点",
        default=True,
    )    


    prop_simple: BoolProperty(
        name="循环模式",
        description="通过两个面的圆形中心进行简单拟合",
        default=False,
    )    




    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def get_cross(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        if (p2 - p1).length < 0.001:
            return p1
        else:
            return None


    def check_line(self, a, b, plane, sn):
        co = mathutils.geometry.intersect_line_plane(a, 
            b.normalized() * 10000, plane, sn)
        return co



    # def get_rot_basic(self, bm, f1, f2, fact):
    #     cuts = self.prop_cut
    #     cen1 = f1.calc_center_median()
    #     cen2 = f2.calc_center_median()
    #     s1 = f1.normal
    #     s2 = f2.normal
    #     crot = Matrix.Identity(4)
    #     vp = s2        
    #     rots = []
    #     rotdeg = self.prop_rotation
    #     rotm2 = None
    #     smooth = self.prop_size
    #     ps = mathutils.geometry.interpolate_bezier(cen2, 
    #         cen2+s2*smooth, cen1+s1*smooth, cen1, cuts+2)
        
    #     psm = []
    #     ps2 = ps + [cen1 + s1*-1]
    #     for i in range(cuts+1):
    #         p1 = ps2[i+1]
    #         pp = ps2[i]
    #         pn = ps2[i+2]
    #         off = p1 - cen2
    #         m1 = p1 - pp
    #         m2 = pn - p1
    #         m3 = m1.normalized() + m2.normalized()    
    #         ax = m1.cross(m2)    
    #         psm.append((m2, m3, ax, off, p1))

    #     psm = [(s2, s2, s2, s2, cen2)] + psm
    #     for i in range(cuts+1):
    #         crot, off = self.get_dest_rot(bm, psm[i], psm[i+1], crot, 
    #             cen2, rotdeg)
    #         rots.append((i, crot.copy(), off))
    #         rotm2 = m2
    #     return rots, rotm2



    # def get_dest_rot(self, bm, pa, pb, crot, cen2, rotdeg):
    #     _, vp, _, _, p1 = pa
    #     m2, m3, ax, off, p2 = pb
    #     if vp.length == 0 or m3.length == 0:
    #         return None, None
    #     d2 = vp.angle(m3)
    #     if ax.length > 0:
    #         rot2 = Quaternion(ax, d2).to_matrix().to_4x4()
    #         crot = rot2 @ crot
    #     zrot = Quaternion(m2, math.radians(rotdeg)).to_matrix().to_4x4()
    #     crot = zrot @ crot        
    #     return crot, off


    def get_rot_basic(self, ps, s1, s2, cen1, cen2):
        cuts = self.prop_cut
        crot = Matrix.Identity(4)
        vp = s2        
        rots = []
        rotdeg = self.prop_rotation
        rotm2 = None
        for i in range(cuts):
            p2 = ps[i]
            p3 = ps[i+2]
            p1 = ps[i+1]
            off = p1 - cen2
            m1 = p1 - p2
            m2 = p3 - p1
            m3 = m1.normalized() + m2.normalized()
            if vp.length == 0 or m3.length == 0:
                return None, None
            d2 = vp.angle(m3)
            vp = m3
            ax = m1.cross(m2)
            if ax.length > 0:
                rot2 = Quaternion(ax, d2).to_matrix().to_4x4()
                crot = rot2 @ crot
            zrot = Quaternion(m2, math.radians(rotdeg)).to_matrix().to_4x4()
            crot = zrot @ crot
            rots.append((i, crot.copy(), off))
            rotm2 = m2
        return rots, rotm2




    def check_rot_v_basic(self, bm, fs1, fs2, s1, s2, cen1, cen2, rots, fact, rotm2, ps):
        cuts = self.prop_cut
        i, crot, off = rots[-1]
        m1 = ps[-1] - ps[-2]
        m2 = ps[-2] - ps[-3]
        vp = m1.normalized() + m2.normalized()
        if vp.length == 0:
            return 0
        sp1 = s1 * -1
        d1 = vp.angle(sp1)
        ax = m1.cross(sp1)
        if ax.length > 0:
            rot2 = Quaternion(ax, d1).to_matrix().to_4x4()
            crot = rot2 @ crot
        off = cen1 - cen2
        mata = Matrix.Scale(1.0 - (1.0-fact)/(cuts+1) * (i+1), 4)
        f2vs = fs2[1]
        f1vs = fs1[1]
        v1 = f2vs[0]
        k1 = v1.co - cen2
        k1 = crot @ k1
        p1 = cen2 + k1 + off
        # p1 = crot @ v1.co
        ms = []
        # c1 = self.check_line(p1, rotm2, cen1, s1)#s1 * -1
        c1 = p1
        for pv1 in f1vs:
            m1 = pv1.co - c1
            ms.append((m1.length, pv1.co))
        _, p2 = min(ms, key=lambda e:e[0])
        m1 = c1 - cen1
        m2 = p2 - cen1
        d1 = m1.angle(m2)
        drot = Quaternion(rotm2, d1).to_matrix().to_4x4()
        r1 = mata @ (drot @ k1)
        tp1 = cen2 + r1 + off
        drot2 = Quaternion(rotm2, d1 * -1).to_matrix().to_4x4()
        r2 = (mata @ drot2 @ k1)
        tp2 = cen2 + r2 + off
        th1 = (tp1-p2).length
        th2 = (tp2-p2).length
        # if math.degrees(d1) < self.prop_auto_threshold:
        #     return None
        if th1 < th2:
            return d1/(cuts+0)
        else:
            return d1 * -1 / (cuts+0)            
        
       

    def connect(self, bm, f1, f2):
        a2 = f2.calc_area()
        a1 = f1.calc_area()
        fact = math.pow(a1/a2, 0.5)
        cen1 = f1.calc_center_median()
        cen2 = f2.calc_center_median()
        s1 = f1.normal
        s2 = f2.normal
        fs1 = (f1.edges[:], f1.verts[:])
        fs2 = (f2.edges[:], f2.verts[:])
        self.connect_pro(bm, fs1, fs2, s1, s2, cen1, cen2, fact)
        bmesh.ops.delete(bm, geom=[f1,f2], context='FACES_ONLY')



    def connect_pro(self, bm, fs1, fs2, s1, s2, cen1, cen2, fact):
        cuts = self.prop_cut
        esp = []
        smooth = self.prop_size
        ps = mathutils.geometry.interpolate_bezier(cen2, 
            cen2+s2*smooth, cen1+s1*smooth, cen1, cuts+2)        
        rots, rotm2 = self.get_rot_basic(ps, s1, s2, 
            cen1, cen2)
        if rots == None:
            return
        dbase = self.check_rot_v_basic(bm, fs1, fs2, 
            s1, s2, cen1, cen2, rots, fact, rotm2, ps)
        for i, crot, off in rots:
            ret = bmesh.ops.duplicate(bm,
                geom=fs2[0] + fs2[1])
            gm = ret['geom']
            vs = [v for v in gm if isinstance(v, bmesh.types.BMVert)]
            mata = Matrix.Scale(1.0 - (1.0-fact)/(cuts+1) * (i+1), 4)
            if dbase != None:
                drot = Quaternion(rotm2, dbase * i).to_matrix().to_4x4()
                if self.prop_auto_fit:
                    crot = drot @ crot
            for v1 in vs:
                k1 = v1.co - cen2
                k1 = mata @ (crot @ k1)
                v1.co = cen2 + k1 + off
            es = [v for v in gm if isinstance(v, bmesh.types.BMEdge)]
            esp.append(es)
        esp = [fs2[0]] + esp + [fs1[0]]
        for a, b in zip(esp[:-1], esp[1:]):
            bmesh.ops.bridge_loops(bm,
                edges=a + b)
        



    def connect2(self, bm, f1, f2):
        a2 = f2.calc_area()
        a1 = f1.calc_area()
        fact = math.pow(a1/a2, 0.5)        
        cen1 = f1.calc_center_median()
        cen2 = f2.calc_center_median()
        s1 = f1.normal
        s2 = f2.normal
        fs1 = (f1.edges[:], f1.verts[:])
        fs2 = (f2.edges[:], f2.verts[:])        
        self.connect2_core(bm, fs1, fs2, s1, s2, cen1, cen2, fact)
        bmesh.ops.delete(bm, geom=[f1,f2], context='FACES_ONLY')


    def connect2_core(self, bm, fs1, fs2, s1, s2, cen1, cen2, fact):
        cuts = self.prop_cut
        sn1 = (s1+s2)/2
        sn1 = sn1.normalized()
        if sn1.length == 0:
            sn1 = s1
        mk = cen2 - cen1
        c1 = mk.cross(sn1)
        rotdeg = self.prop_rotation
        if s1.angle(s2) > math.radians(0.5):
            p1 = s1.cross(c1)
            p2 = s2.cross(c1)
            cx = self.get_cross(cen1, cen1+p1, cen2, cen2+p2)
            if cx == None:
                return
            mid = cx
        else:
            mid = (cen1 + cen2)/2            
        m1 = cen1 - mid
        m2 = cen2 - mid
        if m1.length == 0 or m2.length == 0:
            return
        d1 = m1.angle(sn1) + m2.angle(sn1)
        dc = d1 / (cuts+1)
        esp = []
        for i in range(cuts):
            mp = m2.copy()
            rot = Quaternion(c1, dc * (i+1))
            mp.rotate(rot)
            ret = bmesh.ops.duplicate(bm,
                geom=fs2[0] + fs2[1])
            gm = ret['geom']
            vs = [v for v in gm if isinstance(v, bmesh.types.BMVert)]
            mata = Matrix.Scale(1.0 - (1.0-fact)/(cuts+1) * (i+1), 4)
            zrot = Quaternion(s2, math.radians(rotdeg * (i+1))).to_matrix().to_4x4()
            for v1 in vs:
                vb = v1.co - cen2
                vb = mata @ (zrot @ vb)
                vb = vb + cen2
                mp = vb - mid
                mp.rotate(rot)
                v1.co = mp + mid
            es = [v for v in gm if isinstance(v, bmesh.types.BMEdge)]
            esp.append(es)
        esp = [fs2[0]] + esp + [fs1[0]]
        for a, b in zip(esp[:-1], esp[1:]):
            bmesh.ops.bridge_loops(bm,
                edges=a + b)
        

    def connect_multi_circular(self, bm, sel):
        fsel = self.divset(sel)
        if len(fsel) != 2:
            return
        fa, fb = fsel
        fs1 = self.edgeloop(fa)
        fs2 = self.edgeloop(fb)
        c1 = self.get_cen_loop(fs1)
        c2 = self.get_cen_loop(fs2)
        s1 = self.get_avg_vs([f1.normal for f1 in fa])
        s2 = self.get_avg_vs([f1.normal for f1 in fb])     
        self.connect2_core(bm, fs1, fs2, s1, s2, c1, c2, 1)
        bmesh.ops.delete(bm, geom=sel, context='FACES')



    def connect_multi(self, bm, sel):
        fsel = self.divset(sel)
        if len(fsel) != 2:
            return
        fa, fb = fsel
        fs1 = self.edgeloop(fa)
        fs2 = self.edgeloop(fb)
        c1 = self.get_cen_loop(fs1)
        c2 = self.get_cen_loop(fs2)
        s1 = self.get_avg_vs([f1.normal for f1 in fa])
        s2 = self.get_avg_vs([f1.normal for f1 in fb])
        self.connect_pro(bm, fs1, fs2, s1, s2, c1, c2, 1)
        bmesh.ops.delete(bm, geom=sel, context='FACES')


    def get_avg_vs(self, ps):
        p1 = Vector()
        for p2 in ps:
            p1 = p1 + p2
        p1 = p1 / len(ps)
        return p1



    def get_sn_loop(self, vs):
        vs2 = vs[1:] + vs[:1]
        vs3 = vs[-1:] + vs[:-1]
        vm = Vector()
        for a, b, c in zip(vs, vs2, vs3):
            m1 = b.co - a.co
            m2 = c.co - a.co
            if m1.length == 0 or m2.length == 0:
                continue
            sn = m1.cross(m2)
            vm = vm + sn
        vm = vm.normalized()
        return vm


    def get_cen_loop(self, fs):
        vs = fs[1]
        cs = [v1.co for v1 in vs]
        return self.get_avg_vs(cs)


    def edgeloop(self, fa):
        es = []
        for f1 in fa:
            for e1 in f1.edges:
                ef = list(e1.link_faces)
                if len(ef) == 2:
                    f2, f3 = ef
                    if (f2 in fa) and (f3 in fa):
                        pass
                    else:
                        es.append(e1)
                else:
                    es.append(e1)
        return self.sortedge(es)


    def sortedge(self, es):
        vmap = []
        elen = len(es)
        e1 = es[0]
        v1 = e1.verts[0]
        es2 = [e1]
        vmap.append(v1)
        for i in range(elen):
            v2 = None
            for e2 in v1.link_edges:
                if e2 == e1:
                    continue
                if (e2 in es) == False:
                    continue
                e1 = e2
                v2 = e1.other_vert(v1)
                break
            if v2 == None:
                break
            else:
                v1 = v2
            if v1 in vmap:
                break
            es2.append(e1)       
            vmap.append(v1)
        return (es2, vmap)


    def bridge_edges(self, bm):
        sel = [e1 for e1 in bm.edges if e1.select]
        if len(sel) < 2:
            return
        # pprint.pprint(sel)
        esel = self.divedges(sel)
        if len(esel) != 2:
            return
        esel1, esel2 = esel
        if len(esel1) < 3 or len(esel2) < 3:
            return
        res = bmesh.ops.contextual_create(bm, geom=esel1)
        fs1 = res['faces']
        res = bmesh.ops.contextual_create(bm, geom=esel2)
        fs2 = res['faces']
        if len(fs1) == 0 or len(fs2) == 0:
            return
        f1 = fs1[0]
        f2 = fs2[0]
        if self.prop_simple:
            self.connect2(bm, f1, f2)
        else:
            self.connect(bm, f1, f2)


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






    def divset(self, sel1):
        sel = list(sel1)
        fset = []
        while True:
            if len(sel) == 0:
                break
            fs = [sel[0]]
            for f1 in fs:
                #print(f1)
                for p in f1.loops:
                    e1 = p.edge
                    if len(e1.link_faces) == 1:
                        continue
                    a, b = e1.link_faces[:2]
                    if a == f1:
                        a = b
                    if a.select:
                        if (a in fs) == False:
                            fs.append(a)
            fset.append(fs)
            for f1 in fs:
                sel.remove(f1)
        return fset



    def process(self, context):
        bm = self.get_bm()
        sel = [f1 for f1 in bm.faces if f1.select]
        if len(sel) == 0:
            self.bridge_edges(bm)
        if len(sel) > 2:
            if self.prop_simple:
                self.connect_multi_circular(bm, sel)
            else:
                self.connect_multi(bm, sel)
        elif len(sel) == 2:
            f1, f2 = sel
            if self.prop_simple:
                self.connect2(bm, f1, f2)
            else:
                self.connect(bm, f1, f2)
 
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
        self.plen_old = 0.2

        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}








