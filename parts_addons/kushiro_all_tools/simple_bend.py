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
from bpy_extras import view3d_utils



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
from . import gui

import itertools
import numpy as np



import bpy
import random




class SimpleBendOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.simple_bend_operator"
    bl_label = "Simple Bend —— 简单弯曲"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    #, "GRAB_CURSOR", "BLOCKING"



    prop_bend: FloatProperty(
        name="弯曲角度",
        description="弯曲量",
        default=0,
        max = 360,
        min = -360
        # step=1,
        # max = 1.0,
        # min = -1.0
    )    


    prop_selectonly: BoolProperty(
        name="仅选定",
        description="仅折弯所选零件",
        default=False,
    )    


    prop_edge: BoolProperty(
        name="边线轴模式",
        description="使用选定的2条持续边作为旋转轴和方向",
        default=False,
    )    


    prop_edge_swap: IntProperty(
        name="交换边线轴",
        description="交换边轴",
        default=0,
        max = 2,
        min = 0
    )    


    prop_fixed: IntProperty(
        name="固定模式",
        description="固定部分编号",
        default=0,
        min = 0,
        max = 2
    )    



    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def is_same(self, m1, m2, dif):
        if m1.length == 0 or m2.length == 0:
            return False
        if m1.angle(m2) < math.radians(dif):
            return True
        else:
            return False

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


    def get_vm_gx(self, va1):
        va1 = va1.normalized()
        gx = [Vector((1,0,0)), Vector((0,1,0)), Vector((0,0,1))]
        gs = []
        if va1.length == 0:
            return Vector((0,0,1))
        for p in gx:
            d1 = p.angle(va1)
            gs.append((d1, p))
            p2 = p * -1
            d1 = p2.angle(va1)
            gs.append((d1, p2))
        _, g1 = min(gs, key=lambda e:e[0])
        return g1.normalized()


    def check_px(self, event):
        if self.prop_edge:
            wd = bpy.context.region.width
            px = event.mouse_region_x        
            px2 = self.px
            dx = px/wd - px2/wd
            dv = dx * -1
        else:
            vm = bpy.context.space_data.region_3d.view_matrix.copy()
            wm = bpy.context.space_data.region_3d.window_matrix.copy()            
            wd = bpy.context.region.width
            px = event.mouse_region_x        
            px2 = self.px
            dx = px/wd - px2/wd
            dv = dx

            wh = bpy.context.region.height
            py = event.mouse_region_y
            py2 = self.py
            dy = py/wh - py2/wh
            if self.selaxis != None:
                a, b, sn = self.selaxis
                # vm2 = vm.inverted()
                v1 = vm @ a
                v2 = vm @ b
                v1.z = 0
                v2.z = 0
                m1 = v2 - v1
                if m1.length > 0:
                    ds = [(Vector((0,1,0)), dy), (Vector((0,-1,0)), dy * -1), 
                        (Vector((1,0,0)), dx), (Vector((-1,0,0)), dx * -1)]
                    ds2 = []
                    for d2, daxis in ds:
                        ds2.append((d2.angle(m1), daxis))
                    _, dv = min(ds2, key=lambda e:e[0])

        # self.prop_bend = dx * 4
        self.prop_bend = dv * 720
        if event.shift:
            delta = self.prop_bend % 5
            self.prop_bend = self.prop_bend - delta


    def get_center(self, sel):
        cs = []
        for v1 in sel:
            cs.append(v1.co)
        cx1 = max(cs, key=lambda e:e.x)
        cx2 = min(cs, key=lambda e:e.x)
        cy1 = max(cs, key=lambda e:e.y)
        cy2 = min(cs, key=lambda e:e.y)
        cz1 = max(cs, key=lambda e:e.z)
        cz2 = min(cs, key=lambda e:e.z)                
        return Vector(((cx1.x+cx2.x)/2, (cy1.y+cy2.y)/2, (cz1.z+cz2.z)/2))


    def process_core(self, bm, sel, event):       
        if event != None:
            self.check_px(event)

        world = bpy.context.active_object.matrix_world
        # for v1 in sel:
        #     cen = cen + v1.co
        # cen = cen / len(sel)
        if len(sel) == 0:
            self.empty_edges = True
            return
        cen = self.get_center(sel)

        vm = self.vm.inverted()
        wm = self.wm.inverted()
        ori = vm @ (wm @ Vector())
        va1 = (vm @ Vector((0,0,1)) ) - ori

        if self.prop_edge == False:            
            # va2 = (vm @ (wm @ Vector((0,1,0))) ) - ori            
            # gz = self.get_vm_gx(va1)
            # gy = self.get_vm_gx(va2)
            # gx = gy.cross(gz)
            gx = self.gx
            gy = self.gy
            gz = self.gz
        else:
            if len(bm.select_history) < 2:
                self.empty_edges = True
                return
            e2 = bm.select_history[-1]
            e1 = bm.select_history[-2]
            if len(e1.verts) != 2 or len(e2.verts) != 2:
                return
            a, b = e1.verts
            c, d = e2.verts
            # gui.lines += [a.co, b.co]
            # gui.lines += [c.co, d.co]
            gx = b.co - a.co
            gy = d.co - c.co
            gx = gx.normalized()
            gy = gy.normalized()
            gz = gx.cross(gy)
            if gz.length == 0:
                gz = Vector((0,0,1))
            gy = gz.cross(gx)

            sw = self.prop_edge_swap
            if sw == 1:
                g4 = gx
                gx = gy
                gy = g4
            elif sw == 2:
                g4 = gy
                gy = gz
                gz = g4

        mat = self.get_matrix(gx, gy, gz, cen)
        mat2 = mat.inverted()

        ps = []
        for v1 in sel:
            p = mat2 @ v1.co
            ps.append(p)
        maxx = max(ps, key=lambda e:e.x)
        minx = min(ps, key=lambda e:e.x)
        dif = abs(maxx.x - minx.x)

        # gui.lines += [world @ (mat @ Vector((-1 * dif,0,0))), world @ (mat @ Vector((1 * dif,0,0)))]

        w1 = dif/2

        if w1 == 0:
            return
        bend = self.prop_bend
        # if bend == 0:
        #     bend = 0.0000001
        # bend = 1.0 / bend
       
        b1 = bend
        if bend < 0:
            b1 = b1 * -1

        # if b1 == 0:
        #     b1 = 0.0000001
        # barm = (1.0 / b1) - 1.0
        barm = b1
        vmap = {}
        used = set()

        for v1 in sel:     
            p = mat2 @ v1.co   
            s1 = p.x 
            if s1 > 0:
                vmap[v1] = 0
            elif s1 < 0:
                vmap[v1] = 1
            else:
                vmap[v1] = 2
            g1,_ = self.get_base_bend(p, w1, barm, bend)
            v1.co = mat @ g1
            used.add(v1)
            
         
        pm1 = Vector((w1, 0, 0))
        pm2 = Vector((w1 * -1, 0, 0))
        con1, deg1 = self.get_base_bend(pm1, w1, barm, bend)
        con2, deg2 = self.get_base_bend(pm2, w1, barm, bend)

        if self.prop_edge:
            gui.lines = []
            gui.lines += [world @ (mat @ con1), world @ (mat @ con2)]
            tline1 = (world @ (mat @ Vector((0,1,0)))).normalized() * 0.1
            tline2 = (world @ (mat @ Vector((0,-1,0)))).normalized() * 0.1
            gui.lines += [tline1, tline2]


        if self.prop_selectonly == False:
            psel = set(sel)
            bpy.ops.mesh.select_linked()
            sel2 = [v1 for v1 in bm.verts if v1.select]
            psel2 = set(sel2)
            psel2 = psel2 - psel     
            p90 = math.pi/2
            
            # for v1 in psel2:
            #     p = mat2 @ v1.co     
            #     s1 = p.x
            #     if s1 > w1:
            #         p2 = p - pm1
            #         p2.rotate(Quaternion(Vector((0,0,1)), deg1 - p90))
            #         p2 = p2 + con1
            #         v1.co = mat @ p2
            #     elif s1 < w1 * -1:
            #         p2 = p - pm2
            #         p2.rotate(Quaternion(Vector((0,0,1)), deg2 - p90))
            #         p2 = p2 + con2
            #         v1.co = mat @ p2     
            #     else:
            #         g1,_ = self.get_base_bend(p, w1, barm, bend)
            #         v1.co = mat @ g1  
                        
            for v0 in sel:
                used.add(v0)
                vs = [v0]
                for v1 in vs:
                    p = mat2 @ v1.co  
                    s1 = p.x
                    for e1 in v1.link_edges:
                        v2 = e1.other_vert(v1)
                        if v2 in used:
                            continue
                        if v2 in psel2:                            
                            vmap[v2] = vmap[v1]                            
                            vs.append(v2)
                            used.add(v2)

            fixed = self.prop_fixed
            
            for v1 in psel2:
                p = mat2 @ v1.co                            
                k = vmap[v1]
                if k == 0:
                    if fixed != 1:
                        p2 = p - pm1
                        p2.rotate(Quaternion(Vector((0,0,1)), deg1 - p90))
                        p2 = p2 + con1
                        v1.co = mat @ p2
                elif k == 1:
                    if fixed != 2:
                        p2 = p - pm2
                        p2.rotate(Quaternion(Vector((0,0,1)), deg2 - p90))
                        p2 = p2 + con2
                        v1.co = mat @ p2     
                else:
                    g1,_ = self.get_base_bend(p, w1, barm, bend)
                    v1.co = mat @ g1                                      
                # g1,_ = self.get_base_bend(p, w1, barm, bend)
                # v1.co = mat @ g1                                                      

            for v1 in psel2:
                p = mat2 @ v1.co   
                k = vmap[v1]
                if fixed == 1:
                    if k != 0:
                        p2 = p - pm1
                        p2.rotate(Quaternion(Vector((0,0,1)), deg2- p90))
                        p2 = p2 + con1
                        v1.co = mat @ p2                        
                elif fixed == 2:
                    if k != 1:
                        p2 = p - pm2
                        p2.rotate(Quaternion(Vector((0,0,1)), deg1- p90))
                        p2 = p2 + con2
                        v1.co = mat @ p2

            for v1 in sel:
                p = mat2 @ v1.co   
                k = vmap[v1]
                if fixed == 1:
                    p2 = p - pm1
                    p2.rotate(Quaternion(Vector((0,0,1)), deg2- p90))
                    p2 = p2 + con1
                    v1.co = mat @ p2                        
                elif fixed == 2:
                    p2 = p - pm2
                    p2.rotate(Quaternion(Vector((0,0,1)), deg1- p90))
                    p2 = p2 + con2
                    v1.co = mat @ p2

        self.draw_text()


            
    def get_base_bend(self, p, w1, barm, bend):
        s1 = p.x
        z = p.z             
        p90 = math.pi/2
        # arm = math.sqrt(w1*w1 + barm*barm)
        deg = math.radians(barm / 2)
        if deg == 0:
            deg = 0.0000001
        tdeg = math.tan(deg)
        if tdeg == 0:
            tdeg = 0.0000001
        harm = w1 / tdeg
        arm = math.sqrt(w1*w1 + harm*harm)

        if bend >= 0:
            sp = s1/w1     
            d1 = sp * deg * -1 + p90
            arm2 = arm + p.y            
            px = math.cos(d1) * arm2
            py = math.sin(d1) * arm2 - harm    
            g1 = Vector((px, py , z)) 
        else:
            sp = s1/w1
            d1 = sp * deg  + p90
            arm2 = arm * -1 + p.y
            px = math.cos(d1) * arm2
            py = math.sin(d1) * arm2 + harm     
            g1 = Vector((px, py , z))             
        return g1, d1        

        # s1 = p.x
        # z = p.z             
        # p90 = math.pi/2
        # arm = math.sqrt(w1*w1 + barm*barm)
        # deg = math.atan2(w1, barm) * -1           

        # if bend >= 0:
        #     sp = s1/w1     
        #     d1 = sp * deg + p90
        #     arm2 = arm + p.y            
        #     px = math.cos(d1) * arm2
        #     py = math.sin(d1) * arm2 - barm    
        #     g1 = Vector((px, py , z)) 
        # else:
        #     sp = s1/w1
        #     d1 = sp * deg * -1 + p90
        #     arm2 = arm * -1 + p.y
        #     px = math.cos(d1) * arm2
        #     py = math.sin(d1) * arm2 + barm     
        #     g1 = Vector((px, py , z))             
        # return g1, d1


    def setup_axis(self, bm, sel, event):        
        gui.lines = []
        world = bpy.context.active_object.matrix_world
        vs = [v1.co for v1 in sel]
        if len(vs) == 0:
            return

        x1 = min(vs, key=lambda e:e.x)
        x2 = max(vs, key=lambda e:e.x)
        y1 = min(vs, key=lambda e:e.y)
        y2 = max(vs, key=lambda e:e.y)        
        z1 = min(vs, key=lambda e:e.z)
        z2 = max(vs, key=lambda e:e.z)
        cen = Vector(( (x1.x+x2.x)/2, (y1.y+y2.y)/2, (z1.z+z2.z)/2 ))

        mx = Vector(((x2 - x1).x, 0, 0))
        my = Vector((0, (y2 - y1).y, 0))
        mz = Vector((0,0,(z2 - z1).z))

        if mx.length < 0.5:
            mx = Vector((0.5, 0, 0))
        if my.length < 0.5:
            my = Vector((0, 0.5, 0))
        if mz.length < 0.5:
            mz = Vector((0, 0, 0.5))                        

        minlen = min([mx.length, my.length, mz.length])
        maxlen = max([mx.length, my.length, mz.length])
        minlen = max(minlen * 0.8, maxlen * 0.2)
        # mxlen = min(mx.length * 0.8, minlen)
        # mylen = min(my.length * 0.8, minlen)
        # mzlen = min(mz.length * 0.8, minlen)

        # mxlen = min(mx.length * 0.8, 2.0)
        # mylen = min(my.length * 0.8, 2.0)
        # mzlen = min(mz.length * 0.8, 2.0)
        # mxlen = mx.length * 0.8
        # mylen = my.length * 0.8
        # mzlen = mz.length * 0.8

        mx2 = mx.normalized() * minlen/2
        my2 = my.normalized() * minlen/2
        mz2 = mz.normalized() * minlen/2

        ax1 = cen + mx/2 + my2
        ax2 = cen + mx/2 - my2
        pax1 = cen + mx/2 + mz2
        pax2 = cen + mx/2 - mz2

        ay1 = cen + my/2 + mx2
        ay2 = cen + my/2 - mx2
        pay1 = cen + my/2 + mz2
        pay2 = cen + my/2 - mz2

        az1 = cen + mz/2 + mx2
        az2 = cen + mz/2 - mx2
        paz1 = cen + mz/2 + my2
        paz2 = cen + mz/2 - my2
        ##
        self.axis = []
        self.arrow(world, ax1, ax2, mx)
        self.arrow(world, pax1, pax2, mx) 
        self.arrow(world, ay2, ay1, my) 
        self.arrow(world, pay1, pay2, my) 
        self.arrow(world, az2, az1, mz) 
        self.arrow(world, paz2, paz1, mz) 
        # self.bound(cen, mx, my, mz)
        


    def bound(self, cen, mx, my, mz):
        gui.lines += [cen + mx, cen - mx]
        gui.lines += [cen + my, cen - my]
        gui.lines += [cen + mz, cen - mz]
        


    def arrow(self, world, p1, p2, sn):
        m1 = p2 - p1        
        c1 = m1.copy() * 0.1
        c2 = m1.copy() * 0.1
        c1.rotate(Quaternion(sn, math.radians(45)))
        c2.rotate(Quaternion(sn, math.radians(-45)))
        gui.lines += [world @ p1, world @ p2]
        gui.lines += [world @ p1, world @ (p1 + c1)]
        gui.lines += [world @ p1, world @ (p1 + c2)]
        gui.lines += [world @ p2, world @ (p2 - c1)]
        gui.lines += [world @ p2, world @ (p2 - c2)]
        self.axis.append((p1, p2, sn))
        

    def process(self, context, event):
        # mode = bpy.context.tool_settings.mesh_select_mode[:]
        # if mode[1] == True:
        #     self.prop_edge = True
        # elif mode[2] == True:
        #     self.prop_edge = False

        # if self.prop_edge:            
        self.reset_all()
        bm = self.get_bm()
        fsel = [f for f in bm.faces if f.select] 
        sel = [v for v in bm.verts if v.select]            
        self.process_core(bm, sel, event)

        bm.normal_update()

        for f1 in bm.faces:
            f1.select = False
        for f1 in fsel:
            f1.select = True

        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)  





    def check_axis(self, context, event):
        res = self.get_sel_edge(context, event)
        if res == None:
            return
        p1, p2, sn = res
        # print(p1, p2, sn)
        m1 = (p2 - p1).normalized()
        self.gx = m1.cross(sn)
        self.gy = m1
        self.gz = sn
        self.selaxis = (p1, p2, sn)
        self.drag = True



    def get_inter_dis(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        return (p1, (p2 - p1).length)


    def get_sel_edge(self, context, event):
        sel = None
        es = []
        p1, p2 = self.calc_pos_view(context, event)
        for k1, k2, sn in self.axis:            
            res = self.get_inter_dis(k1, k2, p1, p2)
            if res != None:
                pint, dis = res
                if self.isInside(pint, k1, k2):
                    es.append((dis, k1, k2, sn))
        if len(es) == 0:
            return None
        _, a, b, sn = min(es, key=lambda e:e[0])
        return (a, b, sn)
		
		
    def calc_pos_view(self, context, event):
        obj = context.edit_object
        view_vector, view_point, world_loc = self.get_3d_cursor(context, event)
        world = obj.matrix_world
        world2 = world.inverted()
        viewer = world2 @ view_point
        tar = world2 @ world_loc
        return viewer, tar


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

    def isInside(self, v1, p1, p2):
        len1 = (p2 - p1).length
        return abs((v1 - p1).length + (v1 - p2).length - len1) < 0.001


		



    def process_setup(self, event):
        bm = self.get_bm()
        # fsel = [f for f in bm.faces if f.select] 
        sel = [v for v in bm.verts if v.select]

        mode = bpy.context.tool_settings.mesh_select_mode[:]
        if mode[1] == True:
            self.prop_edge = True
        elif mode[2] == True:
            self.prop_edge = False

        if self.prop_edge == False:
        # self.process1(bm, sel, event)
            self.setup_axis(bm, sel, event)

        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)  



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


    def reset_all(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        me = bpy.context.object.data
        bm = self.bm
        bm.to_mesh(me)
        bpy.ops.object.mode_set(mode='EDIT')        



    def moving(self, context, event):        
        world = bpy.context.active_object.matrix_world
        if event != None and self.prop_edge == False and self.drag == False:
            res = self.get_sel_edge(context, event)
            if res == None:
                return
            p1, p2, sn = res                
            gui.lines2 = []
            gui.lines2 += [world @ p1, world @ p2]

        if self.drag or self.prop_edge:
            self.process(context, event)


    # def invoke(self, context, event):

    #     self.prop_steps = 1

    #     if context.edit_object:
    #         self.process(context)
    #         return {'FINISHED'} 
    #     else:
    #         return {'CANCELLED'}


    def draw_text(self):
        status = ''
        deg = str.format("{:.2f}", self.prop_bend) 
        if self.prop_edge:
            status += '[Edge mode]'
        if self.prop_edge_swap:
            status += '[Swap]'            
        if self.prop_selectonly:
            status += '[Select-only]'
        
        if self.prop_edge and self.empty_edges:
            status = '错误: 选择的边为空。请在选择历史记录中设置轴-边。'

        gui.txtall = [deg, status,  '按住Shift键: 5度捕捉', 
            'S键: 仅选择, C键: 未选择部分,再次按则更改轴','Esc键：退出','Q键: 确认']


    def draw_point(self, p1):
        gui.lines += [p1 + Vector((0.02, 0, 0)), p1 - Vector((0.02, 0, 0))]
        gui.lines += [p1 + Vector((0, 0.02, 0)), p1 - Vector((0, 0.02, 0))]


    def modal(self, context, event):    
        # print(event.type, event.value, event.mouse_prev_y, event.mouse_y)
        context.area.tag_redraw()


        if event.type == 'Q':
            if event.value == 'PRESS':                                
                gui.draw_handle_remove()
                return {'FINISHED'}   

        elif event.type == 'S':
            if event.value == 'PRESS':                                
                if self.prop_selectonly:
                    self.prop_selectonly = False
                else:
                    self.prop_selectonly = True
                self.draw_text()
                self.process(context, None)
         


        elif event.type == 'W':
            if event.value == 'PRESS':  
                if self.prop_edge:
                    self.prop_edge_swap = (self.prop_edge_swap + 1) % 3
                    self.draw_text()
                    self.process(context, None)     


        elif event.type == 'C':
            if event.value == 'PRESS':
                self.prop_fixed = (self.prop_fixed + 1) % 3
                self.draw_text()
                self.process(context, None) 


        elif event.type == 'ESC':
            if event.value == 'PRESS':
                gui.draw_handle_remove()
                self.reset_all()
                return {'CANCELLED'}

        elif event.type == 'MOUSEMOVE':
            px = event.mouse_region_x
            py = event.mouse_region_y
            if self.event_x != px or self.event_y != py:                
                self.moving(context, event)
                self.event_x = px
                self.event_y = py
            return {'RUNNING_MODAL'}

        # elif event.type == 'MOUSEMOVE':
        #     px = event.mouse_region_x
        #     py = event.mouse_region_y
        #     if self.event_x != px or self.event_y != py:
        #         self.moving(event)
        #         self.event_x = px
        #         self.event_y = py
        #     return {'RUNNING_MODAL'}


        # elif event.type == 'WHEELUPMOUSE' and event.shift:
        #     self.wheel += 1
        #     self.moving(event)
        #     return {'RUNNING_MODAL'}


        # elif event.type == 'WHEELDOWNMOUSE' and event.shift:
        #     self.wheel -= 1
        #     self.moving(event)
        #     return {'RUNNING_MODAL'}


        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.prop_edge:
                    gui.draw_handle_remove()                
                    return {'FINISHED'}     
                else:
                    self.px = event.mouse_region_x
                    self.py = event.mouse_region_y
                    self.check_axis(context, event)
                    # gui.draw_handle_remove()
                    # return {'FINISHED'}                                                             
                    return {'RUNNING_MODAL'}
            elif event.value == 'RELEASE':
                self.drag = False
                # self.selaxis2 = self.selaxis
                # self.selaxis = None
                # gui.draw_handle_remove()
                # return {'FINISHED'}                   


        if 'MOUSE' in event.type:
            return {'PASS_THROUGH'}

        if 'PAN' in event.type:
            return {'PASS_THROUGH'}
        

        return {'RUNNING_MODAL'}

            
    def invoke(self, context, event):  
        # mat = bpy.context.space_data.region_3d.view_matrix
        vm = bpy.context.space_data.region_3d.view_matrix.copy()
        wm = bpy.context.space_data.region_3d.window_matrix.copy()
        self.vm = vm
        self.wm = wm
        px = event.mouse_region_x
        py = event.mouse_region_y
        self.px = px
        self.py = py
        self.wheel = 0
        self.event_x = None
        self.event_y = None
        self.empty_edges = False
        self.axis = []
        self.gx = Vector()
        self.gy = Vector()
        self.gz = Vector()
        self.selaxis = None
        self.drag = False
        gui.lines = []
        gui.lines2 = []

        self.prop_selectonly = False
        

        bpy.ops.object.mode_set(mode='OBJECT')
        me = bpy.context.active_object.data
        bm = bmesh.new()
        bm.from_mesh(me)
        self.bm = bm
        bpy.ops.object.mode_set(mode='EDIT')
        

        if context.edit_object:
            context.window_manager.modal_handler_add(self)
            gui.draw_handle_add((self, context))
            gui.text_handle_add((self, context))
            self.draw_text()

            self.process_setup(event)            
            return {'RUNNING_MODAL'} 
        else:
            return {'CANCELLED'}





