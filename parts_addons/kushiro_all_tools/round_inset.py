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
import bmesh.utils

from mathutils import Matrix, Vector, Quaternion
import mathutils



import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
)

import pprint


class RoundInsetOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.round_inset_operator"
    bl_label = "Round Inset —— 精准内插"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="内插尺寸",
        description="定义Inset",
        default=1.0
    )    


    prop_fix: FloatProperty(
        name="阈值大小",
        description="低于此尺寸的任何东西都将被转移",
        default=1.0,
        min=0
    )    

    prop_scale: FloatProperty(
        name="倒角大小",
        description="定义比例",
        default=1.0,
        min = 0,
        step = 0.5
    )    


    prop_prevent: BoolProperty(
        name="防止重叠",
        description="防止边缘重叠",
        default=True,
    )        

    prop_merge: BoolProperty(
        name="合并顶点",
        description="合并折叠的顶点",
        default=False,
    )          

    prop_merge_dis: FloatProperty(
        name="合并距离",
        description="合并顶点的距离",
        default=0.0001,
    )      

    # prop_scale_limit: FloatProperty(
    #     name="Limit for scaling",
    #     description="Only apply scale to corners with edges shorter than the limit",
    #     default=1.0
    # )        


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm





    def inter(self, a, b, c, d):
        pin = mathutils.geometry.intersect_line_line_2d(a,b,c,d)
        if pin == None:
            return None
        else:
            pin = Vector((pin.x, pin.y, 0))
            return pin
        
        
    def get_face_mat(self, f1):
        p1 = f1.loops[0]
        a = p1.vert
        b = p1.link_loop_next.vert
        m1 = b.co - a.co
        m1 = m1.normalized()
        sn = f1.normal
        m2 = m1.cross(sn)
        cen = f1.calc_center_median()
        mat = self.get_matrix(m2, m1, sn, cen)
        return mat


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



    def same(self, a, b):
        if a.length == 0 or b.length == 0:
            return True
        d = a.angle(b)
        if d < 0.0001:
            return True
        else:
            return False
        

    def get_sides(self, es, es2, p, lenall):
        if len(es) < 2:
            return None, None
        p2 = p
        right = None
        left = None
        for i in range(lenall):
            p2 = p2.link_loop_next
            if p2 == p:
                break
            if p2 in es:
                right = p2
                break
    
        p2 = p
        for i in range(lenall):
            p2 = p2.link_loop_prev
            if p2 == p:
                break
            if p2 in es2:
                left = p2
                break
        return left, right


    def inset_normal(self, p, sn, plen):
        p2 = p.link_loop_prev
        v2 = p.edge.other_vert(p.vert)
        m1 = v2.co - p.vert.co
        m2 = p2.vert.co - p.vert.co
        m1.normalize()
        m2.normalize()
        m3 = m1 + m2
        # print(m3.length)
        # if m3.length < 0.0001:
        #     m3 = m1.cross(sn) * -1
        # else:
        #     m3.normalize()
        m4 = m3.normalized()
        if m3.length < 0.00001:
            m4 = m1.cross(sn) * -1
        else:
            sn1 = m1.cross(m2)
            if self.same(sn1, sn) == False:
                m4 = m4 * -1

        if self.prop_plen < 0:
            m4 = m4 * -1
            
        # m4 = m4 * abs(plen)
        klen = abs(plen)
        deg = m1.angle(m2)
        k1 = math.sin(deg/2)
        if k1 < 0.0001:
            return Vector()        
        # if k1 == 0:
        #     k1 += 0.00000001
        k1 = klen / k1 
        m4 = m4 * k1

        return m4
        

    def inseting(self, a, b, sn, plen):
        a2 = a.link_loop_prev
        b2 = b.link_loop_next
        m1 = a2.vert.co - a.vert.co
        m2 = b2.vert.co - b.vert.co
        m3 = m1.normalized() + m2.normalized()
        m3 = m3.normalized()
        sn1 = m2.normalized().cross(m1.normalized())
        if self.same(sn1, sn) == False:
            m3 = m3 * -1

        if self.prop_plen < 0:
            m3 = m3 * -1

        klen = abs(plen)
        deg = m1.angle(m2)
        k1 = math.sin(deg/2)
        if k1 < 0.0001:
            return Vector()
        # if k1 == 0:
            # k1 = 0.00000001
            return 
        k1 = klen / k1 
        m3 = m3 * k1
        return m3


    def prescale(self, f2, pmap, es, es2, remain):
        scale = self.prop_scale
        lenall = len(f2.loops)
        for p in remain:
            a, b = self.get_sides(es, es2, p, lenall)
            if a == None or b == None:
                continue
            a2 = a.link_loop_prev
            b2 = b.link_loop_next
            # m1 = a2.vert.co - a.vert.co
            # m2 = b2.vert.co - b.vert.co
            # if m1.length > self.prop_scale_limit \
            #     and m2.length > self.prop_scale_limit:
            #     continue

            v1 = a.vert.co
            v2 = a2.vert.co
            v3 = b.vert.co
            v4 = b2.vert.co
            gin = mathutils.geometry.intersect_line_line(v1,v2,v3,v4)
            if gin == None:
                continue
            g1, g2 = gin
            g3 = (g1 + g2)/2
            scale2 = scale - 1.0
            gshift = (p.vert.co - g3) * scale2
            pmap[p] = pmap[p] + gshift

            if p.link_loop_prev == a:
                gshifta = (a.vert.co - g3) * scale2
                pmap[a] = pmap[a] + gshifta

            if p.link_loop_next == b:
                gshiftb = (b.vert.co - g3) * scale2
                pmap[b] = pmap[b] + gshiftb


    def process_face(self, bm, f1):
        ps = []
        for p1 in f1.loops:
            p2 = p1.link_loop_radial_next
            ps.append(p2)

        plen = abs(self.prop_plen * 0.05)
        f1.select = True

        bmesh.ops.inset_individual(bm, 
            faces=[f1], thickness=0, depth=0)

        ps2 = []
        for p1 in ps:
            p2 = p1.link_loop_radial_next
            # p3 = p2.link_loop_next
            ps2.append(p2)
        
        inner = [f for f in bm.faces if f.select]
        f2 = inner[0]

        for f1 in bm.faces:
            f1.select = False

        pfix = self.prop_fix * 0.1
        es = []
        es2 = []
        # ip1.select = True
        remain = []
        for p in f2.loops:
            e1 = p.edge
            if e1.calc_length() > pfix:
                es.append(p)
            else:
                p2 = p.link_loop_prev
                e2 = p2.edge
                if e2.calc_length() > pfix:
                    es2.append(p)
                else:
                    remain.append(p)
        
        lenall = len(f2.loops)
        pmap = {}
        pgroup = {}

        for p in remain:
            a, b = self.get_sides(es, es2, p, lenall)
            if a == None or b == None:
                continue
            key = (a, b)
            if key in pgroup:
                pgroup[key].append(p)
                pgroup[key].append(a)
                pgroup[key].append(b)
            else:
                pgroup[key] = [p,a,b]
            m3 = self.inseting(a, b, f2.normal, plen)
            pmap[p] = m3
            pmap[a] = m3
            pmap[b] = m3                

        for p in es2:
            if (p in pmap) == False:
                a = p
                b = p.link_loop_next
                key = (a, b)
                if key in pgroup:
                    pgroup[key].append(a)
                    pgroup[key].append(b)
                else:
                    pgroup[key] = [a,b]                    
                m3 = self.inseting(a, b, f2.normal, plen)
                pmap[a] = m3
                pmap[b] = m3                    

        for p in es:
            if (p in pmap) == False:
                m3 = self.inset_normal(p, f2.normal, plen)
                pmap[p] = m3
        # for p in remain:
        #     a, b = self.get_sides(es, es2, p, lenall)
        #     if a == None or b == None:
        #         continue

        #     m3 = self.inseting(a, b, f2.normal, plen)
        #     pmap[p] = m3
        #     pmap[a] = m3
        #     pmap[b] = m3

        # for p in es2:
        #     if (p in pmap) == False:
        #         a = p
        #         b = p.link_loop_next
        #         m3 = self.inseting(a, b, f2.normal, plen)
        #         pmap[a] = m3
        #         pmap[b] = m3

        # for p in es:
        #     if (p in pmap) == False:
        #         m3 = self.inset_normal(p, f2.normal, plen)
        #         pmap[p] = m3

        if self.prop_scale != 1.0:
            self.prescale(f2, pmap, es, es2, remain)

        if self.prop_prevent:
            self.limiting(f2, pmap, pgroup)

        for p in pmap:
            m3 = pmap[p]
            p.vert.co = p.vert.co + m3

        return f2
        # f2.select = True
        # for p in es:
        #     p.edge.select = True


    # def ploop(self, p1, p2):
    #     p3 = p1
    #     ps = []
    #     while True:
    #         ps.append(p3)
    #         if p3 == p2:
    #             break
    #         p3 = p3.link_loop_next

    #     ps2 = []
    #     p3 = p1
    #     while True:
    #         ps2.append(p3)
    #         if p3 == p2:
    #             break
    #         p3 = p3.link_loop_prev
        
    #     if len(ps) < len(ps2):
    #         return ps
    #     else:
    #         return ps2

    def update_group(self, pgroup, pmap, p):
        mv = pmap[p]
        for key in pgroup:
            plist = pgroup[key]
            for p2 in plist:
                if p2 == p:
                    for p3 in plist:
                        m1 = pmap[p3]
                        if mv.length < m1.length:
                            pmap[p3] = m1.normalized() * mv.length
                    return


    # def get_dint(self, f2, pmap):
    #     lines = {}
    #     for p in pmap:
    #         m3 = pmap[p]
    #         k = p.vert.co + m3.normalized() * 10000
    #         lines[p] = (p.vert.co, k)        
    #     mat = self.get_face_mat(f2)
    #     mat2 = mat.inverted()
    #     dint = {}
    #     for p in lines:
    #         for p2 in lines:
    #             a, b = lines[p]
    #             c, d = lines[p2]
    #             a = mat2 @ a
    #             b = mat2 @ b
    #             c = mat2 @ c
    #             d = mat2 @ d
    #             pin = self.inter(a, b, c, d)
    #             if pin != None:
    #                 mv = (mat @ pin) - p.vert.co
    #                 if p in dint:
    #                     if mv.length < dint[p].length:
    #                         dint[p] = mv
    #                 else:
    #                     dint[p] = mv
    #     return dint
            


    def limiting(self, f2, pmap, pgroup):
        lines = {}
        # cmap = {}
        for p in pmap:
            m3 = pmap[p]
            k = p.vert.co + m3
            # lines.append((p.vert.co, k))
            lines[p] = (p.vert.co, k)        
        mat = self.get_face_mat(f2)
        mat2 = mat.inverted()
        # dint = self.get_dint(f2, pmap)
        for p in lines:
            for p2 in lines:
                # if p2 == p:
                #     continue
                # p3 = p2.link_loop_next
                a, b = lines[p]
                c, d = lines[p2]
                # if p2 in dint:
                #     c = p2.vert.co
                #     d = p2.vert.co + dint[p2]
                # e, f = lines[p3]
                a = mat2 @ a
                b = mat2 @ b
                c = mat2 @ c
                d = mat2 @ d
                # e = mat2 @ e
                # f = mat2 @ f
                pin = self.inter(a, b, c, d)
                if pin != None:
                    mv = (mat @ pin) - p.vert.co
                    if mv.length < pmap[p].length:
                        pmap[p] = mv
                        self.update_group(pgroup, pmap, p)



    def process(self, context):
        bm = self.get_bm()      
        # selected faces
        sel = [f for f in bm.faces if f.select]
        if len(sel) == 0:
            return
        
        for f1 in bm.faces:
            f1.select = False

        fs = []
        for f1 in sel:
            f2 = self.process_face(bm, f1)
            fs.append(f2)

        bm.normal_update()

        for f2 in fs:
            f2.select = True

        if self.prop_merge:
            dis = self.prop_merge_dis
            bpy.ops.mesh.remove_doubles(threshold=dis, 
                use_unselected=False, use_sharp_edge_from_normals=False)

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
        self.mode = 0
        self.prop_base_edge = 0

        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}



