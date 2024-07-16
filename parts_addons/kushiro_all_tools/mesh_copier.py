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

from email.policy import default
import math


import bpy
import bmesh
import bmesh.utils

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
# from . import gui



class MeshCopierOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.mesh_copier_operator"
    bl_label = "Mesh Copier —— 网格基准复制"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "复制网格整体到网格面上"
    #, "GRAB_CURSOR", "BLOCKING"


    # prop_plen: IntProperty(
    #     name="Select the Copy Region",
    #     description="Define the region to be copied",
    #     default=0,
    #     min = 0,
    # )    

    operation_mode : EnumProperty(
                #(identifier, name, description, icon, number)
        items = [
                ('None0','需执行3次：','','',0),
                ('None1','切换边模式，1.选择复制边界基准','','',0),
                ('None2','2.选择需要复制的网格,3.选择面进行复制','','',0),
                ('Setsource','Set as Source','','',1),
                ('Copy','Copy Selected Mesh','','',2), 
                ('Paste','Paste','','',3),
                 ],
        name = "Operation",
        default = 'None0')



    prop_plen : EnumProperty(
        name="区域",
        description="定义要复制的区域",
        items=[
            ('A', "内部", "Inside"),
            ('B', "外部", "Outside"),
        ],
        default='A',
    )    


    prop_base_edge: IntProperty(
        name="对齐编号",
        description="设置边缘的方向",
        default=0,
        step=1,
        min = 0,
    )    


    prop_base_rotation: IntProperty(
        name="绕法线旋转次数",
        description="设置旋转次数",
        default=0,
        step=1,
        min = 0,
    )    



    prop_merge_distance: FloatProperty(
        name="Merge Distance",
        description="定义合并新零件的距离",
        default=0.01,
        step=1.0,
        min = 0,
    )    


    prop_z_scale: FloatProperty(
        name="深度缩放",
        description="定义Z轴缩放",
        default=1.0,
        step=1.0,
    )    



    prop_inverse: BoolProperty(
        name="反转粘贴",
        description="反转粘贴",
        default=False,

    )       


    prop_flip : BoolProperty(
        name="水平翻转",
        description="翻转粘贴的网格",
        default=False
    )    

    prop_donot_resize : BoolProperty(
        name="不缩放",
        description="不缩放源网格以适合目标",
        default=False
    )    

    prop_donot_merge : BoolProperty(
        name="不按间距合并",
        description="不合并目标上的顶点",
        default=False
    )    


    def draw(self, context):
        # if self.actions > 1:
        #     return
        layout = self.layout     

        layout.label(text='Operation:')
        layout.prop(self, "operation_mode", expand=True)

        layout.separator_spacer()

        layout.label(text='Copying:')
        sub1 = layout.row().column()
        sub1.prop(self, "prop_plen", expand=True)
        sub1.enabled = False

        layout.separator_spacer()

        layout.label(text='Pasting:')
        sub2 = layout.row().column()
        sub2.prop(self, "prop_base_edge")
        sub2.prop(self, "prop_base_rotation")
        sub2.prop(self, "prop_merge_distance")
        sub2.prop(self, "prop_z_scale")
        sub2.prop(self, "prop_inverse")
        sub2.prop(self, "prop_flip")
        sub2.prop(self, "prop_donot_resize")
        sub2.prop(self, "prop_donot_merge")
        sub2.enabled = False

        # sub3 = layout.row().column()
        # sub3.label(text="Setting separated mesh.")

        # sub4 = layout.row().column()
        # sub4.label(text="Setting base edges.")

        if self.mode == 0:
            sub1.enabled = True
        elif self.mode == 1:
            sub2.enabled = True
        # elif self.mode == 2:
        #     sub3.enabled = True
        # elif self.mode == 3:
        #     sub4.enabled = True

         


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def process(self, context, event):
        bm = self.get_bm()        
        walkloop = bm.loops.layers.int.get('copyregion_loop')
        if walkloop == None:
            walkloop = bm.loops.layers.int.new('copyregion_loop')

        walkface = bm.faces.layers.int.get('copyregion_face')
        if walkface == None:
            walkface = bm.faces.layers.int.new('copyregion_face')

        self.walkloop = walkloop
        self.walkface = walkface

        fsel = [f1 for f1 in bm.faces if f1.select]
        esel = [e1 for e1 in bm.edges if e1.select]


        # if event != None and event.shift or self.operation_mode == 'Copy':
        #     self.set_sep_mesh(bm, fsel)
        #     self.mode = 2
        # elif event != None and event.ctrl or self.operation_mode == 'Setsource':
        #     # self.set_sep_edge(bm, esel)
        #     self.copyobject_face(bm, esel)
        #     self.mode = 3
        # else:
        #     if len(fsel) == 0 and len(esel) > 2:
        #         self.copyobject(bm, esel)
        #         self.mode = 0
        #     elif len(fsel) > 0:
        #         self.pasteobject(bm, fsel)
        #         self.mode = 1
        if self.operation_mode == 'Copy':
            self.set_sep_mesh(bm, fsel)
            self.mode = 2

        elif self.operation_mode == 'Setsource':
            # self.set_sep_edge(bm, esel)
            if len(fsel) == 0 and len(esel) > 2:
                self.copyobject(bm, esel)
                self.mode = 0
            else:
                self.copyobject_face(bm, esel)
                self.mode = 3

        elif self.operation_mode == 'Paste':
            if len(fsel) > 0:
                self.pasteobject(bm, fsel)
                self.mode = 1


                
        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me) 
        return False  


    def set_sep_mesh(self, bm, fsel):
        walkface = self.walkface
        for f1 in bm.faces:
            f1[walkface] = 0

        for f1 in fsel:
            f1[walkface] = 1
        



    def invalid_esel(self, bm):
        walkloop = self.walkloop
        ps = []
        for f1 in bm.faces:
            for p in f1.loops:
                p1 = p[walkloop]
                if p1 > 0:
                    if p1 in ps:
                        return True
                    else:
                        ps.append(p1)   
        return False  


    def get_all_loop(self, p, f1):
        total = len(f1.loops)
        res = []
        p0 = p
        for i in range(total):
            res.append(p0.vert.co)
            p0 = p0.link_loop_next
            if p0 == p:
                break
        return res


    def sort_e(self, esel):
        p0 = esel[0]
        res = []
        for i in range(len(esel)):
            res.append(p0)
            v1 = p0.vert
            e1 = p0.edge
            v2 = e1.other_vert(v1)
            p3 = None
            for p2 in esel:
                if p2 == p0:
                    continue
                if p2.vert == v2:
                    if (p2 in res) == False:
                        p3 = p2
                        break
            if p3 == None:
                break
            else:
                p0 = p3
        return res


    def get_esel(self, bm):
        walkloop = self.walkloop
        esel = []
        es = []
        for f1 in bm.faces:
            for p in f1.loops:
                # if p[walkloop] == 1:
                if p[walkloop] > 0:
                    esel.append(p)
                    es.append(p.edge)    
        return esel, es   



    def get_reg(self, es, esel, bm):
        e1 = es[0]
        p1 = esel[0]
        reg = []
        self.get_all(p1.face, es, reg)     

        walkface = self.walkface
        for f1 in bm.faces:
            if f1[walkface] == 1:
                reg.append(f1)
        
        reg = list(set(reg))
        return reg



    def rotate_p(self, p2):
        roi = self.prop_base_rotation
        p3 = p2
        for i in range(roi):
            p3 = p3.link_loop_next        
        return p3


    def get_esel_base(self, esel, ecen):
        index = self.prop_base_edge % len(esel)
        p0 = esel[index]
        pall = [(ecen, p0)]
        a0 = p0.vert
        b0 = p0.edge.other_vert(a0) 
        m0 = b0.co - a0.co        
        return pall, m0


    def pasteobject(self, bm, fsel):
        walkloop = self.walkloop
        reg = []

        if self.invalid_esel(bm):
            return

        esel, es = self.get_esel(bm)
        if len(esel) <3:
            return

        reg = self.get_reg(es, esel, bm)
        if len(reg) == 0:
            return

        for f1 in fsel:
            f1.select = False

        for p in esel:
            p[walkloop] = 0


        extra = []
        walkface = self.walkface
        for f1 in bm.faces:
            if f1[walkface] == 1:
                extra.append(f1)


        ecen, regcen, sn = self.get_esel_normal(reg, esel)
        if sn == None:
            return

        pall, m0 = self.get_esel_base(esel, ecen)

        dupvs = []

        fsel2 = list(fsel)
        while len(fsel2) > 0:
            pdis = []
            for f1 in fsel2:
                fcen = self.get_center(f1)
                for c1, px in pall:
                    m1 = c1 - fcen
                    pdis.append((m1.length, c1, px, f1))

            _, fcen2, p1, f1 = min(pdis, key=lambda e: e[0])
            fsel2.remove(f1)
            fcen = self.get_center(f1)

            em1, p2 = self.get_near_axis(p1, f1, fcen2, fcen)
            p3 = self.rotate_p(p2)

            c = p3.vert
            d = p3.edge.other_vert(c)
            em2 = d.co - c.co
            pall.append((fcen, p2))

            # all from copy source
            mat = self.get_esel_mat2(esel, ecen, sn, m0)
            mat2 = mat.inverted()
            w, h = self.check_dimension(esel, mat2)
            if w == 0 or h == 0:
                return
            dmat = self.get_fsel_mat2(f1, em2)
            dmat2 = dmat.inverted()
            w2, h2 = self.check_f1_dimension(f1, dmat.inverted())

            # ssel = self.sort_e(esel)
            # f_loops = self.get_all_loop(p3, f1)
            # if len(ssel) != len(f_loops):
            #     return

            res = bmesh.ops.duplicate(bm, geom=reg)
            resv = res['geom']
            resv = [v1 for v1 in resv if isinstance(v1, bmesh.types.BMVert)]

            if self.prop_donot_resize == False:
                sm1 = Matrix.Scale(w2/w, 4, Vector((1,0,0)))
                sm2 = Matrix.Scale(h2/h, 4, Vector((0,1,0)))
                dp =  self.prop_z_scale
                sm3 = Matrix.Scale(dp, 4, Vector((0,0,1)))
                sm = sm1 @ sm2 @ sm3
            else:
                sm = Matrix.Identity(4)

            for v1 in resv:
                v1.co = dmat @ (sm @ (mat2 @ v1.co))
            dupvs.extend(resv)

        for p in esel:
            if p.is_valid:
                p[walkloop] = 0

        for f1 in bm.faces:
            if (f1 in extra) == False:
                f1[walkface] = 0

        if self.prop_donot_merge == False:
            checkvs = []
            for f1 in fsel:
                checkvs.extend(list(f1.verts))
            
            checkvs.extend(dupvs)
            checkvs = list(set(checkvs))        

            for f1 in fsel:
                if f1.is_valid:
                    try:
                        bmesh.ops.delete(bm, geom=[f1], context='FACES_ONLY')
                    except:
                        pass            
            # bmesh.ops.remove_doubles(bm, verts=vs1, dist=self.prop_merge_distance)
            bmesh.ops.remove_doubles(bm, verts=checkvs, dist=self.prop_merge_distance)



        cc = 1
        for f1 in reg:
            if f1.is_valid:
                for e1 in f1.edges:
                    if len(e1.link_loops) == 2:
                        p1, p2 = e1.link_loops
                        if p1.face in reg and (p2.face in reg) == False:
                            p1[walkloop] = cc
                            cc = cc + 1
                        if (p1.face in reg) == False and p2.face in reg:
                            p2[walkloop] = cc
                            cc = cc + 1
                    elif len(e1.link_loops) == 1:
                        e1.link_loops[0][walkloop] = cc
                        cc = cc + 1
        


                    


    def get_fsel_mat2(self, f1, em2):
        m1 = em2
        sn = f1.normal
        if self.prop_inverse:
            sn = sn * -1
        m2 = m1.cross(sn)
        if self.prop_flip:
            m2 = m2 * -1        
        cen = self.get_center(f1)
        mat = self.get_matrix(m1, m2, sn, cen)
        return mat



    def get_center(self, f1):
        ecen = Vector()
        for e1 in f1.edges:
            a, b = e1.verts
            ecen = ecen + a.co
            ecen = ecen + b.co
        ecen = ecen / (len(f1.edges) * 2)
        return ecen




    # def get_near_axis(self, esel, ecen, sn1, f1, fcen):
    def get_near_axis(self, p1, f1, ecen, fcen):
        ps = []
        a = p1.vert
        b = p1.edge.other_vert(a)
        a1 = a.co - ecen
        b1 = b.co - ecen
        m1 = (a1 + b1)/2
        # m1 = (a.co + b.co)/2
        k1 = b.co - a.co
        
        # m1 = b.co - a.co
        for p2 in f1.loops:
            c = p2.vert
            d = p2.edge.other_vert(c)
            c1 = c.co - fcen
            d1 = d.co - fcen
            m2 = (d1 + c1)/2
            # m2 = (c.co + d.co)/2
            # m2 = d.co - c.co
            k2 = d.co - c.co
            d = (m1 - m2).length
            ps.append((d, k1, p2))

        ps = sorted(ps, key=lambda e: e[0])
        p1 = ps[0]
        _, k1, p2 = p1

        return k1, p2

   

    def get_esel_mat2(self, esel, ecen, sn, em1):
        m1 = em1
        mat = self.get_matrix(m1, m1.cross(sn), sn, ecen)
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
        



    def get_linked(self, p1, es):
        for p2 in p1.vert.link_loops:
            if p2.edge == p1.edge:
                continue
            if p2.edge in es:
                return p2
        return None

            
    def cross_p(self, p1, p2):
        a = p1.vert
        b = p1.edge.other_vert(a)
        m1 = b.co - a.co
        c = p2.vert
        d = p2.edge.other_vert(c)
        m2 = d.co - c.co
        return m1.cross(m2).normalized()
                
    def get_esel_normal(self, reg, esel):        
        regcen = Vector()        
        for f1 in reg:
            c = f1.calc_center_median()
            regcen = regcen + c
        regcen = regcen / len(reg)

        ecen = Vector()
        for p1 in esel:
            e1 = p1.edge
            a, b = e1.verts
            ecen = ecen + a.co
            ecen = ecen + b.co
        ecen = ecen / (len(esel) * 2)

        es = [p.edge for p in esel]
        p1 = esel[0]
        p2 = self.get_linked(p1, es)
        if p2 == None:
            return None,None,None

        sn = self.cross_p(p1, p2)
        
        sn = sn.normalized()
        return ecen, None, sn



    def check_dimension(self, esel, mat):
        vs = []
        for p in esel:
            v1 = p.vert
            c1 = mat @ v1.co
            vs.append(c1)
        x1 = min(vs, key=lambda e: e.x)
        x2 = max(vs, key=lambda e: e.x)
        y1 = min(vs, key=lambda e: e.y)
        y2 = max(vs, key=lambda e: e.y)
        x = abs(x2.x-x1.x)
        y = abs(y2.y-y1.y)
        return x, y


    def check_f1_dimension(self, f1, mat):
        vs = []
        for v1 in f1.verts:
            c1 = mat @ v1.co
            vs.append(c1)
        x1 = min(vs, key=lambda e: e.x)
        x2 = max(vs, key=lambda e: e.x)
        y1 = min(vs, key=lambda e: e.y)
        y2 = max(vs, key=lambda e: e.y)
        x = abs(x2.x-x1.x)
        y = abs(y2.y-y1.y)
        return x, y 



    def copyobject_face(self, bm, esel):
        fsel = [f1 for f1 in bm.faces if f1.select]
        if len(fsel) == 0:
            return
            
        s = [fsel[0]]

        for f1 in bm.faces:
            f1.select = False

        for f1 in s:
            f1.select = True

        walkloop = self.walkloop
        for f1 in bm.faces:
            for p in f1.loops:
                p[walkloop] = 0
        
        cc = 1
        for f1 in s:
            for p in f1.loops:
                if p.edge in esel:
                    p[walkloop] = cc
                    cc = cc + 1

        walkface = self.walkface
        for f1 in bm.faces:
            f1[walkface] = 0   





    def copyobject(self, bm, esel):
        e1 = esel[0]
        ss = []
        for p1 in e1.link_loops:
            s2 = []
            self.get_all(p1.face, esel, s2)
            ss.append(s2)

        if self.prop_plen == 'A':
            index = 0
        else:
            index = 1

        ss2 = []
        for s in ss:
            area = 0
            for f1 in s:
                area = area + f1.calc_area()
            ss2.append((area, s))

        # index = self.prop_plen % 2
        # ss = sorted(ss, key=lambda e: len(e))
        # s = ss[index]
        ss2 = sorted(ss2, key=lambda e: e[0])
        _, s = ss2[index]

        for f1 in bm.faces:
            f1.select = False

        for f1 in s:
            f1.select = True

        walkloop = self.walkloop
        for f1 in bm.faces:
            for p in f1.loops:
                p[walkloop] = 0
        
        cc = 1
        for f1 in s:
            for p in f1.loops:
                if p.edge in esel:
                    p[walkloop] = cc
                    cc = cc + 1

        walkface = self.walkface
        for f1 in bm.faces:
            f1[walkface] = 0                    
                    


    def get_all2(self, f1, esel, res):
        for e1 in f1.edges:
            if e1 in esel:
                continue            
            for f2 in e1.link_faces:
                if f2 == f1:
                    continue
                if f2 in res:
                    continue
                res.append(f2)
                self.get_all(f2, esel, res)




    def get_all(self, f0, esel, res):
        fs = [f0]
        for f1 in fs:
            for e1 in f1.edges:
                if e1 in esel:
                    continue            
                for f2 in e1.link_faces:
                    if f2 == f1:
                        continue
                    if f2 in res:
                        continue
                    res.append(f2)
                    fs.append(f2)
                    # self.get_all(f2, esel, res)
        



    def execute(self, context):
        self.process(context, None)      
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
        self.operation_mode = 'None'
        self.prop_base_edge = 0


        if context.edit_object:
            self.process(context, event)
            return {'FINISHED'}  
        else:
            return {'CANCELLED'}

