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



class FaceCutterOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.face_cutter_operator"
    bl_label = "Face Cutter"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    def draw_edge(self, a, b):
        world = bpy.context.active_object.matrix_world
        m1 = b - a
        m2 = m1 * -1
        s1 = b + m2.normalized() * max(m2.length * 0.9, m2.length - 0.05)
        s2 = a + m1.normalized() * max(m1.length * 0.9, m1.length - 0.05)
        # gui.addline(world @ (s1), world @ (s2))
        gui.lines += [world @ (s1), world @ (s2)]



    def draw_edge_thick(self, a, b):
        world = bpy.context.active_object.matrix_world
        m1 = b - a
        m2 = m1 * -1
        s1 = a
        s2 = b
        # gui.addline(world @ s1, world @ s2)
        gui.lines += [world @ s1, world @ s2]

        c1 = m1.cross(Vector((0,0,1)))
        if c1.length == 0:
            c1 = m1.cross(Vector((1,0,0)))
            if c1.length == 0:
                c1 = m1.cross(Vector((0,1,0)))

        rot = Quaternion(m1, math.radians(360/12))
        mlen = min(0.05, m1.length * 0.05)        
        t1 = c1.normalized() * mlen
        
        for i in range(12 + 1):
            t2 = t1.copy()            
            t2.rotate(rot)
            # gui.addline(world @ (t1 + s1), world @ (t2 + s1))
            # gui.addline(world @ (t1 + s2), world @ (t2 + s2))
            gui.lines += [world @ (t1 + s1), world @ (t2 + s1)]
            gui.lines += [world @ (t1 + s2), world @ (t2 + s2)]
            t1 = t2




    def calc_pos_local(self, context, event):
        obj = context.edit_object
        view_vector, view_point, world_loc = self.get_3d_cursor(context, event)
        world = obj.matrix_world
        world2 = world.inverted_safe()
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


    def find_inter(self, v1, v2, v3, v4, delta):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        if (p2 - p1).length < delta:
            return (p1, (p2 - p1).length)
        else:
            return None

    def isInside(self, v1, p1, p2):
        len1 = (p2 - p1).length
        return abs((v1 - p1).length + (v1 - p2).length - len1) < 0.001


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def get_inter_dis(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        return (p1, (p2 - p1).length)



    def get_sel_edge(self, context, event):
        sel = None
        es = []
        p1, p2 = self.calc_pos_local(context, event)
        fsel = self.fsel
        for f1 in fsel:
            if f1.is_valid == False:
                continue
            for e1 in f1.edges:
                a, b = e1.verts
                res = self.get_inter_dis(a.co, b.co, p1, p2)
                if res != None:
                    pint, dis = res
                    if self.isInside(pint, a.co, b.co):
                        es.append((e1, dis))
        if len(es) == 0:
            return None
        sel, _ = min(es, key=lambda e:e[1])     
        return sel   



    def get_full_width(self, sel, a, b):
        m1 = b - a
        fsel = self.fsel
        es = [a, b]
        for f1 in fsel:
            for e1 in f1.edges:
                if e1 == sel:
                    continue
                c, d = e1.verts
                if self.colinear(a, b, c.co, d.co):
                    es.append(c.co)
                    es.append(d.co)

        f1 = self.selface
        if f1 == None:
            return
            
        sn = f1.normal
        mat = self.get_matrix(m1, m1.cross(sn), sn, a)
        mat2 = mat.inverted_safe()
        high = Vector()
        low = Vector()
        for p in es:
            p2 = mat2 @ p
            if p2.x < low.x:
                low = p2
            if p2.x > high.x:
                high = p2            
        p1 = mat @ low
        p2 = mat @ high
        return p1, p2



    def calc_pos(self, center, sn, p, u):
        w = p - center
        snd = sn.dot(u)
        if snd != 0:
            s1 = sn.dot(w) * -1 / snd
            s2 = p + u * s1
            return s2
        else:
            return None
            

    def get_screen_pos(self, pos):
        region = bpy.context.region
        region3D = bpy.context.space_data.region_3d        
        return view3d_utils.location_3d_to_region_2d(region, region3D, pos)


    def get_sel_face(self, context, event, fs, a, b):
        obj = bpy.context.active_object
        world = obj.matrix_world        
        selface = None 
        if len(fs) == 2:
            f1, f2 = fs
            if f1.normal.angle(f2.normal) > 0.01:
                # view, tar = self.calc_pos_view(context, event)
                # u = tar - view
                #p1, p2 = self.calc_pos_view(context, event)                
                _, p1, p2 = self.get_3d_cursor(context, event)
                cen1 = f1.calc_center_median()
                cen2 = f2.calc_center_median()
                pos1 = self.get_screen_pos(world @ cen1)
                pos2 = self.get_screen_pos(world @ cen2)
                cur = self.get_screen_pos(p2)
                if pos1 == None or pos2 == None or cur == None:
                    return
                #_, _, world_loc = self.get_3d_cursor(context, event)
                
                plen1 = pos1 - cur
                plen2 = pos2 - cur

                int1 = self.get_inter_dis(world @ a.co, world @ b.co, p1, p2)
                if int1 == None:
                    return
                int1, _ = int1
                int2 = self.get_screen_pos(int1)
                curlen = cur - int2
                pin1 = plen1 - int2
                pin2 = plen2 - int2

                if curlen.length == 0 or pin1.length == 0 or pin2.length == 0:
                    return                

                if curlen.angle(pin1) < curlen.angle(pin2):
                    cen = cen1
                    selface = f1
                else:
                    cen = cen2
                    selface = f2                                    
                # if plen1.length < plen2.length:
                #     cen = cen1
                #     selface = f1
                # else:
                #     cen = cen2
                #     selface = f2
                # acen1 = cen - a.co
                # procen1 = acen1.project(b.co - a.co)
                # arrow1 = (acen1 - procen1).normalized() * (b.co - a.co).length * 0.25
                #gui.lines += [procen1 + a.co, procen1 + a.co + arrow1]
            else:
                selface = f1
            
        else:
            selface = fs[0]
        
        return selface


    def process_move(self, context, event):
        gui.lines = []
        bm = self.bm
        sel = self.get_sel_edge(context, event)
        if sel == None:
            return None

        a, b = sel.verts
        m1 = b.co - a.co
        vp1 = None
        vp2 = None
        
        if self.full_width:
            vp1, vp2 = self.get_full_width(sel, a.co, b.co)
        else:
            vp1 = a.co
            vp2 = b.co        

        fs = [f1 for f1 in sel.link_faces if f1.select]

        selface = self.get_sel_face(context, event, fs, a, b)
        if selface == None:
            return None

        self.selface = selface        
        self.draw_edge_thick(vp1, vp2)
        self.sel = (vp1, vp2)
        self.seledge = sel

        cen = selface.calc_center_median()
        h1, h2 = self.get_limit(cen, selface.normal.cross(m1.normalized()))         

        obj = bpy.context.active_object
        world = obj.matrix_world              
                
        self.triangle_indicate(world, sel, selface)
        # self.dot_line_small(world @ h1, world @ h2)
        #mat = bpy.context.space_data.region_3d.view_matrix
        #mat = bpy.context.space_data.region_3d.perspective_matrix
        # mat2 = mat.inverted()
        # gui.lines += [mat2 @ Vector(), mat2 @ Vector((0,0,-1)) ]

    def triangle_indicate(self, world, sel, selface):
        for p in selface.loops:
            cen = selface.calc_center_median()
            if p.edge == sel:
                a, b = p.vert, sel.other_vert(p.vert)
                m1 = b.co - a.co
                sn = selface.normal
                plen = m1.length
                # h1 = plen * 0.5 * math.tan(math.radians(30))
                mid = (a.co + b.co)/2
                h2 = (cen - mid).length * 0.5
                m2 = sn.cross(m1).normalized() * h2
                pf = world @ (mid + m2)
                pfa = world @ a.co
                pfb = world @ b.co                
                gui.lines += [pf, pfa]
                gui.lines += [pf, pfb]
                break           
                # gui.lines += [world @ mid, world @ (mid + m2)]




    def dot_line(self, h1, h2):
        #gui.lines += [h1, h2]   
        plen = 0.1
        m1 = h2 - h1
        if m1.length < plen:
            # gui.addline(h1, h2)
            gui.lines += [h1, h2]
        else:
            # m2 = m1.normalized() * plen            
            # ct = math.floor(m1.length / plen)
            m2 = m1 / 10
            ct = 10
            lines = []
            for i in range(ct):
                lines += [h1 + m2 * i , h1 + m2 * (i+0.5) ]
            gui.lines.extend(lines)


    # def dot_line_small(self, h1, h2):
    #     #gui.lines += [h1, h2]   
    #     plen = 0.1
    #     m1 = h2 - h1
    #     if m1.length < plen:
    #         # gui.addline(h1, h2)
    #         gui.lines += [h1, h2]
    #     else:
    #         # m2 = m1.normalized() * plen            
    #         # ct = math.floor(m1.length / plen)
    #         m2 = m1 / 30
    #         ct = 30
    #         lines = []
    #         for i in range(ct):
    #             lines += [h1 + m2 * i , h1 + m2 * (i+0.5) ]
    #         gui.lines.extend(lines)


            
    def line_split_layer_state(self, bm):
        for e1 in bm.edges:
            e1.tag = 1


    def line_split_layer_split_co(self, bm, context, coes):
        es = coes
        if len(es) == 0:
            return
        for e1 in bm.edges:
            e1.tag = 0

        for e1 in es:
            e1.select_set(True)
            e1.tag = 1

        bm.select_flush_mode()   
        context.edit_object.data.update()
        bpy.ops.mesh.edge_split(type='EDGE')
        ess = self.fill_cap(bm)

        for e1 in bm.edges:
            e1.select_set(False)
        for f1 in bm.faces:
            f1.select_set(False)            
        bm.select_flush_mode()   
        #context.edit_object.data.update()

        for es in ess:
            if len(es) == 0:
                continue
            res = bmesh.ops.contextual_create(bm, geom=es)
            if res == None:
                continue
            if ('faces' in res) == False:
                continue
            for f1 in res['faces']:
                bmesh.ops.connect_verts_nonplanar(bm, faces=[f1])

        # me = bpy.context.active_object.data
        # bmesh.update_edit_mesh(me)   




    def line_split_layer_split(self, bm, context):
        es = []
        for e1 in bm.edges:
            if e1.tag != 1:
                es.append(e1)

        if len(es) == 0:
            return

        for e1 in es:
            e1.select_set(True)

        bm.select_flush_mode()   
        context.edit_object.data.update()
        bpy.ops.mesh.edge_split(type='EDGE')

        ess = self.fill_cap(bm)

        for e1 in bm.edges:
            e1.select_set(False)
        for f1 in bm.faces:
            f1.select_set(False)            
        bm.select_flush_mode()   
        #context.edit_object.data.update()

        for es in ess:
            if len(es) == 0:
                continue
            res = bmesh.ops.contextual_create(bm, geom=es)
            if res == None:
                continue
            if ('faces' in res) == False:
                continue
            for f1 in res['faces']:
                bmesh.ops.connect_verts_nonplanar(bm, faces=[f1])

        me = bpy.context.active_object.data
        #bpy.ops.object.editmode_toggle()
        bmesh.update_edit_mesh(me)   
        # bpy.ops.object.editmode_toggle()
        # bm2 = self.bm
        # bm2.to_mesh(me)  
        # bpy.ops.object.editmode_toggle()


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



    def cut_break(self, context):
        self.cut_face_each(context)
        # coes = self.cut_face(context, collect=True)
        # self.line_split_layer_split_co(bm, context, coes)
        # bpy.ops.mesh.select_all(action='SELECT')
        # bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(1))
        # bpy.ops.mesh.select_all(action='DESELECT')        

    def cut_break_core(self, context, bm, coes):
        self.line_split_layer_split_co(bm, context, coes)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(1))
        bpy.ops.mesh.select_all(action='DESELECT')        


    def colinear(self, a, b, c, d):
        m1 = b - a
        if m1.length == 0:
            return False
        m2 = d - c        
        if m1.cross(m2).length < 0.001:
            k = d - a
            if k.length > 0:                
                if abs(k.angle(m1)) < 0.001:        
                    return True
                if abs(k.angle(m1 * -1)) < 0.001:        
                    return True                    
            k2 = c - a
            if k2.length > 0:
                if abs(k2.angle(m1)) < 0.001:
                    return True       
                if abs(k2.angle(m1 * -1)) < 0.001:
                    return True                                    
        return False
                    


    def get_loops(self, p):
        head = p
        es = [p.edge]
        while True:
            p = p.link_loop_next
            if p == head:
                break
            es.append(p.edge)
        return es


    def get_con_loops(self, es):
        ess = [es[0]]
        for e1 in ess:
            for v1 in e1.verts:
                for e2 in v1.link_edges:
                    if e2 in es:
                        if e2 in ess:
                            continue
                        else:
                            ess.append(e2)
        return ess



    def fill_cap(self, bm):
        # bm = self.bm
        es = [e1 for e1 in bm.edges if e1.tag == 1]
        if len(es) == 0:
            return

        ess = []
        while len(es) > 0:
            es3 = self.get_con_loops(es)
            ess.append(es3)
            for e1 in es3:
                es.remove(e1)

        return ess



    def process(self, context):
        pass
        # bm = self.get_bm()
        # sel = [f1 for f1 in bm.faces if f1.select]
        # print(sel)

  

    def execute(self, context):
        #self.process(context)      
        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing 


    def invoke2(self, context, event):
        self.prop_angle = 0
        self.prop_edge_index = 0

        if context.edit_object:

            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}


    def draw_point_thick_blue(self, p1, scale):
        sc = scale * 0.5
        gui.lines2 += [p1 + sc * Vector((0.05, 0, 0)), p1 - sc * Vector((0.05, 0, 0))]
        gui.lines2 += [p1 + sc * Vector((0, 0.05, 0)), p1 - sc * Vector((0, 0.05, 0))]



    def draw_point_thick(self, p1, scale):
        sc = scale * 0.5
        gui.lines += [p1 + sc * Vector((0.05, 0, 0)), p1 - sc * Vector((0.05, 0, 0))]
        gui.lines += [p1 + sc * Vector((0, 0.05, 0)), p1 - sc * Vector((0, 0.05, 0))]


    def draw_point(self, p1):
        gui.lines += [p1 + Vector((0.01, 0, 0)), p1 - Vector((0.01, 0, 0))]
        gui.lines += [p1 + Vector((0, 0.01, 0)), p1 - Vector((0, 0.01, 0))]


    def fill_lines(self):
        s1 = self.get_snapping()
        sel = self.sel

        if sel == None:
            return
        a, b = sel
        m1 = b - a
        if m1.length == 0:
            return                
        deg = self.degree
        fsel = self.fsel
        f1 = self.selface
        inv = m1.normalized().cross(f1.normal).normalized()
        if deg != 0:
            qat = Quaternion(f1.normal, math.radians(deg))
            inv.rotate(qat)

        if self.aligning != None:
            c, d = self.aligning.verts
            inv = d.co - c.co
        
        for p in s1:
            p1, p2 = self.get_limit(p, inv)
            self.cutlines.append((p1, p2))
        self.draw_cuts()


    def get_snapping(self):
        sel = self.sel
        if sel == None:
            return []
        a, b = sel
        m1 = b - a
        div = m1 / (self.snaps + 1)
        s1 = []
        dir1, dir2 = self.get_limit(a, m1)
        c1 = dir1 - a
        ct1 = math.floor(c1.length / div.length)
        c2 = dir2 - a
        ct2 = math.floor(c2.length / div.length)
        s1.append(a)
        for i in range(ct1):
            s1.append(a + div * (i + 1))
        for i in range(ct2):
            s1.append(a - div * (i + 1))
        # for i in range(self.snaps + 2):
        #     s1.append(a + div * (i))            
        return s1        



    def snapping(self, mid, scale):
        obj = bpy.context.active_object
        world = obj.matrix_world
        s1 = self.get_snapping()
        dis = []
        # snapmin = 0.1
        sel = self.sel
        if sel == None:
            return []
        a, b = sel        
        snapmin = (b - a).length /30
        for p in s1:
            self.draw_point_thick( world @ p, scale)
            d = (p - mid).length
            if d < snapmin:
                dis.append((d, p))
        if len(dis) == 0:
            return mid
        else:
            _, mid2 = min(dis, key=lambda e : e[0])
            return mid2
        


    def get_screen_pos(self, loc):
        region = bpy.context.region
        region3D = bpy.context.space_data.region_3d
        pos = view3d_utils.location_3d_to_region_2d(region, region3D, loc)
        return pos



    def move_cut_point(self, context, event):
        obj = bpy.context.active_object
        world = obj.matrix_world
        gui.lines = []
        sel = self.sel
        if sel == None:
            return

        a, b = sel
        m1 = b - a
        if m1.length == 0:
            return

        p1, p2 = self.calc_pos_local(context, event)
        # mid = (a.co + b.co)/2
        # self.draw_edge_thick(a.co, b.co)
        # self.draw_point(mid)
        int1 = self.get_inter_dis(a, b, p1, p2)
        if int1 == None:
            return
        mid, midlen = int1

        # pos = self.get_screen_pos(mid)
        # gui.textpos = [(str(self.degree), pos.x + 10, pos.y + 10, 25)]
        if event.shift == False:
            mid = self.snapping(mid, m1.length)

        #gui.lines += [mid, mid + inv]        
        self.draw_edge_thick(a, b)
        fsel = self.fsel
        f1 = self.selface

        deg = self.degree
        inv = m1.normalized().cross(f1.normal).normalized()        

        if deg != 0:
            qat = Quaternion(f1.normal, math.radians(deg))
            inv.rotate(qat)
            pos = self.get_screen_pos(mid)
            if pos == None:
                gui.textpos = []
            else:
                sc = bpy.context.preferences.system.ui_scale 
                # gui.textpos = [(str(self.degree), pos.x + 10, pos.y + 10, 25)]
                gui.textpos = [(str(self.degree), pos.x  , pos.y , math.floor(16 * sc))]
        else:
            gui.textpos = []

        if self.aligning != None:
            e1 = self.aligning
            if e1 == self.seledge:
                cut = self.get_cut(mid, inv)
            else:
                a, b = e1.verts
                m1 = b.co - a.co
                cut = self.get_cut(mid, m1)
        else:
            cut = self.get_cut(mid, inv)

        self.cutting = cut
        #self.draw_point_thick(mid)
        self.draw_cuts()



    def get_limit(self, dcen, dy):
        fsel = self.fsel
        f1 = self.selface
        sn = f1.normal
        mat = self.get_matrix(dy.cross(sn), dy, sn, dcen)
        mat2 = mat.inverted_safe()
        high = Vector()
        low = Vector()
        for f2 in fsel:
            for v1 in f2.verts:
                p = mat2 @ v1.co
                if p.y > high.y:
                    high = p
                if p.y < low.y:
                    low = p        
        
        p1 = Vector((0, high.y + 0.1, 0))
        p2 = Vector((0, low.y - 0.1, 0))        
        return mat @ p1, mat @ p2        



    def get_cut(self, mid, inv):
        obj = bpy.context.active_object
        world = obj.matrix_world        
        p1, p2 = self.get_limit(mid, inv)
        #gui.lines += [world @ p1, world @ p2]
        self.dot_line(world @ p1, world @ p2)
        return (p1, p2)


    def draw_cuts(self):
        obj = bpy.context.active_object
        world = obj.matrix_world     
        #gui.lines = []
        if self.cutlines == None:
            return

        for p in self.cutlines:
            if p == None:
                continue
            a, b = p
            # gui.addline(world @ a, world @ b)
            gui.lines += [world @ a, world @ b]


    def symmetric(self):
        sel = self.sel
        if sel == None:
            return
        a, b = sel        
        m1 = b - a
        if m1.length == 0:
            return        
        fsel = self.fsel
        f1 = self.selface
        mid = m1/2 + a
        inv = m1.normalized().cross(f1.normal).normalized()
        lines = self.cutlines
        lines2 = []
        for p1, p2 in lines:
            c1 = p1 - mid
            c2 = p2 - mid
            qot = Quaternion(inv, math.radians(180))
            c1.rotate(qot)
            c2.rotate(qot)
            lines2.append((c1 + mid, c2 + mid))
        self.cutlines += lines2
        self.draw_cuts()


    def set_snaps(self, context, event, num):
        self.snaps = num
        self.move_cut_point( context, event)
        self.print_hint()        



    def handle_cut(self, context, event):
        if event.type == 'ONE':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 1)
                return {'RUNNING_MODAL'}
        elif event.type == 'TWO':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 2)
                return {'RUNNING_MODAL'}
        elif event.type == 'THREE':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 3)
                return {'RUNNING_MODAL'}         
        elif event.type == 'FOUR':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 4)
                return {'RUNNING_MODAL'}         
        elif event.type == 'FIVE':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 5)
                return {'RUNNING_MODAL'}        
        elif event.type == 'SIX':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 6)
                return {'RUNNING_MODAL'}                                      
        elif event.type == 'SEVEN':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 7)
                return {'RUNNING_MODAL'}
        elif event.type == 'EIGHT':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 8)
                return {'RUNNING_MODAL'}
        elif event.type == 'NINE':
            if event.value == 'PRESS':
                self.set_snaps(context, event, 9)
                return {'RUNNING_MODAL'}
 

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':                
                if self.cutting != None:
                    self.cutlines.append(self.cutting)
                self.cutting = None
                gui.lines = []
                self.draw_cuts()
                return {'RUNNING_MODAL'}

        elif event.type == 'LEFT_SHIFT' or event.type == 'RIGHT_SHIFT':
            self.move_cut_point( context, event)
            return {'RUNNING_MODAL'}

        elif event.type == 'MOUSEMOVE':
            self.move_cut_point( context, event)
            return {'PASS_THROUGH'}

        elif event.type == 'S':
            if event.value == 'PRESS':
                self.symmetric()
                return {'RUNNING_MODAL'}     


        elif event.type == 'D':
            if event.value == 'PRESS':
                if self.degree == 45:
                    self.degree = -45
                else:
                    self.degree = 45
                self.move_cut_point( context, event)
                return {'RUNNING_MODAL'}     

        elif event.type == 'A':
            if event.value == 'PRESS':
                self.align_line(context, event)    
                self.move_cut_point( context, event)            
                return {'RUNNING_MODAL'}


        elif event.type == 'Z':
            if event.value == 'PRESS':
                if event.ctrl:            
                    if len(self.cutlines) > 0:
                        self.cutlines.pop()
                    self.draw_cuts()
                    self.move_cut_point( context, event)
                    return {'RUNNING_MODAL'}  
                else:
                    self.degree -= 5
                    self.move_cut_point( context, event)
                    return {'RUNNING_MODAL'}

        elif event.type == 'X':
            if event.value == 'PRESS':
                self.degree += 5
                self.move_cut_point( context, event)
                return {'RUNNING_MODAL'}

        elif event.type == 'C':
            if event.value == 'PRESS':
                self.degree -= 1
                self.move_cut_point( context, event)
                return {'RUNNING_MODAL'}

        elif event.type == 'V':
            if event.value == 'PRESS':
                self.degree += 1
                self.move_cut_point( context, event)
                return {'RUNNING_MODAL'}                      

        elif event.type == 'F':
            if event.value == 'PRESS':
                self.fill_lines()
                return {'RUNNING_MODAL'}   

        elif event.type == 'Q':
            if event.value == 'PRESS':
                self.cut_face(context)
                # gui.lines = []
                # self.handlers.pop()
                gui.draw_handle_remove()
                return {'FINISHED'}            

        elif event.type == 'R':
            if event.value == 'PRESS':
                self.loop_mode = True
                self.loop_separate = event.shift
                self.cut_face(context)
                gui.draw_handle_remove()
                return {'FINISHED'}   


        elif event.type == 'T':
            if event.value == 'PRESS':
                self.loop_mode = True
                self.loop_separate = event.shift                
                self.cut_break(context)
                gui.draw_handle_remove()
                return {'FINISHED'}                   


        elif event.type == 'W':
            if event.value == 'PRESS':
                if self.full_width == False:
                    self.full_width = True                    
                else:
                    self.full_width = False
                self.print_hint()                
                return {'RUNNING_MODAL'}  


        elif event.type == 'ESC' or event.type == 'SPACE':
            if event.value == 'PRESS':
                self.handlers.pop()
                self.process_move( context, event)                
                self.draw_cuts()
                return {'RUNNING_MODAL'}

        elif event.type == 'WHEELUPMOUSE' and event.ctrl:
            self.snaps += 1
            self.move_cut_point( context, event)
            self.print_hint()
            return {'RUNNING_MODAL'}

        elif event.type == 'WHEELDOWNMOUSE' and event.ctrl:
            self.snaps -= 1
            if self.snaps < 1:
                self.snaps = 1
            self.move_cut_point( context, event)
            self.print_hint()
            return {'RUNNING_MODAL'}

        elif event.type == 'LEFT_BRACKET':
            self.snaps -= 1
            if self.snaps < 1:
                self.snaps = 1
            self.move_cut_point( context, event)      
            self.print_hint()      
            return {'RUNNING_MODAL'}

        elif event.type == 'RIGHT_BRACKET':
            self.snaps += 1
            self.move_cut_point( context, event)
            self.print_hint()
            return {'RUNNING_MODAL'}
            
        elif event.type == 'E':
            if event.value == 'PRESS':
                self.handlers.pop()
                self.handlers.append(self.handle_linked)
                self.draw_linked_mode(context, event)
                self.print_hint()
                self.draw_cuts()
                return {'RUNNING_MODAL'}                

        return None



    def overall(self, context, event):
        if event.type == 'Q':
            if event.value == 'PRESS':
                self.cut_face(context)
                gui.draw_handle_remove()
                self.cleanup()
                return {'FINISHED'}   


        elif event.type == 'T':
            if event.value == 'PRESS':
                self.loop_mode = True
                self.loop_separate = event.shift                
                self.cut_break(context)
                self.cleanup()
                gui.draw_handle_remove()
                return {'FINISHED'}     


        elif event.type == 'W':
            if event.value == 'PRESS':
                if self.full_width == False:
                    self.full_width = True                    
                else:
                    self.full_width = False
                self.print_hint()
                self.process_move( context, event)                
                return {'RUNNING_MODAL'}      

        elif event.type == 'Z' and event.ctrl:
            if event.value == 'PRESS':
                if len(self.cutlines) > 0:
                    self.cutlines.pop()
                self.draw_cuts()
                return {'RUNNING_MODAL'}    


        elif event.type == 'E':
            if event.value == 'PRESS':
                self.handlers.append(self.handle_linked)
                self.draw_linked_mode(context, event)
                self.print_hint()
                self.draw_cuts()
                return {'RUNNING_MODAL'}                                     


        elif event.type == 'R':
            if event.value == 'PRESS':
                self.loop_separate = event.shift
                self.loop_mode = True
                self.cut_face(context)
                self.cleanup()
                gui.draw_handle_remove()
                return {'FINISHED'}   


        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.sel != None:
                    #self.cutlines = []
                    self.aligning = None
                    self.handlers.append(self.handle_cut)
                    self.print_hint()
                    #  added for empty moving
                    self.move_cut_point( context, event)
                    #self.process(context)
                return {'RUNNING_MODAL'}

        elif event.type == 'MOUSEMOVE':
            self.process_move( context, event)
            self.draw_cuts()
            return {'PASS_THROUGH'}


        elif event.type == 'ESC':
            if event.value == 'PRESS':
                gui.draw_handle_remove()
                return {'CANCELLED'}

        return None



    def set_snaps_easy(self, context, event, num):
        self.snaps = num
        self.draw_linked_mode( context, event)
        self.draw_cuts()        


    def cleanup(self):
        bm = self.bm
        bm.free()
        self.bm = None


    def handle_linked(self, context, event):

        if event.type == 'ONE':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 1)
                return {'RUNNING_MODAL'}
        elif event.type == 'TWO':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 2)
                return {'RUNNING_MODAL'}
        elif event.type == 'THREE':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 3)
                return {'RUNNING_MODAL'}         
        elif event.type == 'FOUR':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 4)
                return {'RUNNING_MODAL'}         
        elif event.type == 'FIVE':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 5)
                return {'RUNNING_MODAL'}        
        elif event.type == 'SIX':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 6)
                return {'RUNNING_MODAL'}                                      
        elif event.type == 'SEVEN':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 7)
                return {'RUNNING_MODAL'}
        elif event.type == 'EIGHT':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 8)
                return {'RUNNING_MODAL'}
        elif event.type == 'NINE':
            if event.value == 'PRESS':
                self.set_snaps_easy(context, event, 9)
                return {'RUNNING_MODAL'}

        if event.type == 'Q':
            if event.value == 'PRESS':
                self.cut_face(context)
                self.cleanup()
                gui.draw_handle_remove()
                return {'FINISHED'}   

        elif event.type == 'T':
            if event.value == 'PRESS':
                self.loop_mode = True
                self.loop_separate = event.shift                
                self.cut_break(context)
                self.cleanup()
                gui.draw_handle_remove()
                return {'FINISHED'}                     

        elif event.type == 'ESC' or event.type == 'SPACE':
            if event.value == 'PRESS':
                gui.lines2 = []
                self.handlers.pop()
                self.temp_point = None
                self.draw_cuts()
                self.print_hint()                
                self.process_move( context, event)
                return {'RUNNING_MODAL'}     

        elif event.type == 'R':
            if event.value == 'PRESS':
                self.loop_separate = event.shift
                self.loop_mode = True
                self.cut_face(context)
                self.cleanup()
                gui.draw_handle_remove()
                return {'FINISHED'}            

        elif event.type == 'Z' and event.ctrl:
            if event.value == 'PRESS':
                if len(self.cutlines) > 0:
                    self.cutlines.pop()
                self.draw_linked_mode(context, event) 
                self.draw_cuts()
                return {'RUNNING_MODAL'}   


        elif event.type == 'MOUSEMOVE':
            self.draw_linked_mode(context, event) 
            self.draw_cuts()           
            return {'PASS_THROUGH'}

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.temp_point == None:                    
                    self.temp_point = self.mid_current
                else:
                    p, elen = self.temp_point
                    p2, elen2 = self.mid_current
                    self.cutlines.append((p, p2))
                    self.temp_point = None
                self.draw_linked_mode(context, event) 
                self.draw_cuts()
                return {'RUNNING_MODAL'}            

        elif event.type == 'E':
            if event.value == 'PRESS':
                gui.lines2 = []
                self.handlers.pop()                
                self.print_hint()                
                self.process_move( context, event)
                self.draw_cuts()
                return {'RUNNING_MODAL'}     

        elif event.type == 'WHEELUPMOUSE' and event.ctrl:
            self.snaps += 1
            self.draw_linked_mode( context, event)
            self.draw_cuts()
            return {'RUNNING_MODAL'}

        elif event.type == 'WHEELDOWNMOUSE' and event.ctrl:
            self.snaps -= 1
            if self.snaps < 1:
                self.snaps = 1
            self.draw_linked_mode( context, event)
            self.draw_cuts()
            return {'RUNNING_MODAL'}                

        elif event.type == 'LEFT_BRACKET':
            self.snaps -= 1
            if self.snaps < 1:
                self.snaps = 1
            self.draw_linked_mode( context, event)    
            self.draw_cuts()
            return {'RUNNING_MODAL'}

        elif event.type == 'RIGHT_BRACKET':
            self.snaps += 1
            self.draw_linked_mode( context, event)
            self.draw_cuts()
            return {'RUNNING_MODAL'}

        return None


    def snapping_all_edge(self, mid, es):
        obj = bpy.context.active_object
        world = obj.matrix_world    
        s1 = []
        bm = self.bm
        for a, b in es:
            m1 = b - a
            if m1.length == 0:
                continue
            m2 = m1/(self.snaps + 1)
            for i in range(self.snaps + 2):
                p = m2 * i + a
                s1.append((p, m1.length))

        dis = []
        for p, elen in s1:
            self.draw_point_thick( world @ p, elen)
            d = (p - mid).length
            dis.append((d, p))
        if len(dis) == 0:
            return mid
        else:
            _, mid2 = min(dis, key=lambda e : e[0])
            return mid2        


    def draw_linked_mode(self, context, event):
        gui.lines = []        
        gui.lines2 = []
        obj = bpy.context.active_object
        world = obj.matrix_world        
        p1, p2 = self.calc_pos_local(context, event)
        bm = self.bm
        near = []
        es = [(e1.verts[0].co, e1.verts[1].co) for e1 in bm.edges if e1.select]
        es = es + self.cutlines

        for a, b in es:
            int1 = self.get_inter_dis(a, b, p1, p2)
            if int1 == None:
                continue
            mid, midlen = int1
            near.append((midlen, mid, (a, b)))

        _, mid, esel = min(near, key=lambda e: e[0])
        if event.shift == False:
            mid = self.snapping_all_edge(mid, es)

        ea, eb = esel
        elen = (eb - ea).length
        self.draw_point_thick_blue( world @ mid, elen)
        self.mid_current = (mid, elen)

        if self.temp_point != None:
            p, elen = self.temp_point
            self.draw_point_thick_blue(world @ p, elen)




    def align_line(self, context, event):
        sel = self.get_sel_edge(context, event)
        self.aligning = sel       



    def modal(self, context, event):
        context.area.tag_redraw()        
        p = self.handlers[-1]

        if event.alt:
            return {'PASS_THROUGH'}
        res = p(context, event)
        if res == None:
            if event.type == 'RIGHTMOUSE':
                return {'RUNNING_MODAL'} 

            if 'MOUSE' in event.type or 'NUMPAD' in event.type:
                return {'PASS_THROUGH'}
            else:
                return {'RUNNING_MODAL'}
        else:            
            return res
        #return {'PASS_THROUGH'}

    def check_faces(self):        
        sel = self.fsel
        if len(sel) == 0:
            return True
        f1 = sel[0]
        sn = f1.normal
        for p in sel:
            if abs(p.normal.angle(sn)) > 0.001:
                return True
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


    def print_hint(self):
        last = self.handlers[-1]
        if last == self.overall:
            txt = [
                'W : 全宽模式',
                'E : 进入简易编辑模式',
                'Ctrl + Z : 撤消',
                'Q : 确认并退出',
                'R : 切穿',                 
                'Esc——退出']
        elif last == self.handle_cut:
            txt = [
                'Ctrl + 鼠标滚轮 : 切割次数 : ' + str(self.snaps), 
                '按住 Shift : 关闭吸附',
                'A : 对齐到最近的边缘',                
                'D : 45度',
                'S : 对称复制',
                'F : 填充全部',
                '1-9 : 设置对应切割次数',
                'Z / X / C / V : 旋转线',
                'R : 切穿 (Shift+R:限制)',
                'T : 切穿和融并原始面',
                'Ctrl + Z : 撤消',
                'Q : 确认并退出',
                'Esc——退出']        
        elif last == self.handle_linked:
            txt = ['E : 退出简易编辑模式',  
                'Ctrl + 鼠标滚轮 : 切割次数',
                'Ctrl + Z : 撤消',
                'Q : 确认并退出',
                'R : 切穿',                 
                '1-9 : 设置对应切割次数',
                'Esc——退出']                

        if self.full_width:
            txt = ['Full Width mode'] + txt
        if self.loop_mode:
            txt = ['Cut through'] + txt

        gui.txtall = txt



    def invoke(self, context, event):
        if context.edit_object:
            # self.bm = self.get_bm()

            bpy.ops.object.editmode_toggle()
            bm2 = bmesh.new()
            me = bpy.context.active_object.data
            bm2.from_mesh(me)
            self.bm = bm2
            bpy.ops.object.editmode_toggle()
            self.fsel = [f2 for f2 in self.bm.faces if f2.select]

            # if self.check_faces():
            #     gui.ShowMessageBox(['Support one face or multiple coplanar faces.', '(all faces have same normal)'])
            #     return {'CANCELLED'}

            self.sel = None
            self.seledge = None
            self.selface = None
            self.snaps = 1
            self.cutting = None
            self.cutlines = []            
            self.full_width = False            
            self.loop_mode = False
            self.handlers = [self.overall]
            self.aligning = None
            self.degree = 0
            self.loop_separate = False
            self.mid_current = None
            self.temp_point = None
            gui.lines2 = []
            gui.textpos = []

            context.window_manager.modal_handler_add(self)
            gui.draw_handle_add((self, context))
            gui.text_handle_add((self, context))
            self.print_hint()

            self.process(context)
            return {'RUNNING_MODAL'} 
        else:
            return {'CANCELLED'}


    def normalize_view_to_face(self, obj, f1):
        cen = f1.calc_center_median()
        move = Matrix.Translation(cen)
        sn2 = f1.normal * -1
        rot = sn2.rotation_difference(Vector((0,0,-1))).to_matrix().to_4x4()
        world2 = obj.matrix_world.inverted_safe()
        bpy.context.space_data.region_3d.view_matrix = move @ (rot @ world2)
        self.update_view()


    def update_view(self):        
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.update()





    def cut_face_each(self, context):
        cuts = self.cutlines
        if len(cuts) == 0:
            return
        # bm = self.bm
        bm = self.get_bm()
        sel = []
        hidden = []
        if self.loop_separate:
            bpy.ops.mesh.select_linked()
            sel = []
            for f1 in bm.faces:
                if f1.hide:
                    hidden.append(f1)
                if f1.select == False:
                    f1.hide_set(True)

            sel = self.fsel
            for f1 in bm.faces:
                if f1 in sel:
                    f1.select_set(True)
                else:
                    f1.select_set(False)
        else:                
            sel = self.fsel

        f1 = self.selface

        if f1 == None:
            return
        me = bpy.data.meshes.new('sword_temp_mesh')
        new_obj = bpy.data.objects.new('sword_temp', me) 
        new_obj.location = (0,0,0)
        new_obj.show_name = True
        bpy.context.collection.objects.link(new_obj)

        reg1 = bpy.context.space_data.region_3d.view_location.copy()
        reg2 = bpy.context.space_data.region_3d.view_rotation.copy()
        reg3 = bpy.context.space_data.region_3d.view_distance
        view1 = bpy.context.space_data.region_3d.view_matrix.copy()        
        pers = bpy.context.space_data.region_3d.view_perspective
        bpy.context.space_data.region_3d.view_perspective = 'ORTHO'        
        self.normalize_view_to_face(context.edit_object, f1)
        new_obj.matrix_world = context.edit_object.matrix_world
        override1 = context.copy()        
        #override1['space_data'].region_3d.view_matrix = mat2        
        override1['selected_objects'] = []
        override1['selected_objects'].append(new_obj)
        override1['selected_objects'].append(context.edit_object)        
        
        for cut in cuts:
            cuts2 = [cut]
            bm2 = bmesh.new()            
            self.make_slice(cuts2, bm2)
            bm2.to_mesh(me)            
            #old_world = context.edit_object.matrix_world.copy()
            #bpy.ops.mesh.knife_project(override1, cut_through=self.loop_mode)

            # with context.temp_override(override1):
            with context.temp_override(selected_objects=[new_obj, context.edit_object]):
                bpy.ops.mesh.knife_project(cut_through=True)
            # bpy.ops.mesh.knife_project(override1, cut_through=True)
            coes = self.collect_edges(bm, bm2)
            self.cut_break_core(context, bm, coes)

        bpy.data.objects.remove(new_obj, do_unlink=True)
        bpy.context.space_data.region_3d.view_perspective = pers
        #context.edit_object.matrix_world = old_world
        bpy.context.space_data.region_3d.view_matrix = view1
        bpy.context.space_data.region_3d.view_location = reg1
        bpy.context.space_data.region_3d.view_rotation = reg2
        bpy.context.space_data.region_3d.view_distance = reg3
        self.update_view()

        if self.loop_separate:
            for f1 in bm.faces:
                if f1 in hidden:
                    f1.hide_set(True)
                else:
                    f1.hide_set(False)
        
        me = bpy.context.active_object.data
        #bpy.ops.object.editmode_toggle()
        bmesh.update_edit_mesh(me)
        # bpy.ops.object.editmode_toggle()
        # bm2 = self.bm
        # bm2.to_mesh(me)  
        # bpy.ops.object.editmode_toggle()      
        



    def cut_face(self, context, collect=False):        
        cuts = self.cutlines
        if len(cuts) == 0:
            return

        # bm = self.bm
        bm = self.get_bm()
        sel = []
        hidden = []
        if self.loop_mode:
            if self.loop_separate:
                bpy.ops.mesh.select_linked()
                sel = []
                for f1 in bm.faces:
                    if f1.hide:
                        hidden.append(f1)
                    if f1.select == False:
                        f1.hide_set(True)

                sel = self.fsel
                for f1 in bm.faces:
                    if f1 in sel:
                        f1.select_set(True)
                    else:
                        f1.select_set(False)

            else:                
                sel = self.fsel
        else:
            sel = self.fsel
            for f1 in bm.faces:
                if f1.hide:
                    hidden.append(f1)
                if f1.select == False:
                    f1.hide_set(True)
                # if f1.hide == False:
                #     f1.hide_set(True)
                #     hidden.append(f1)

        f1 = self.selface
        if f1 == None:
            return

        # #edit
        # me = bpy.context.active_object.data
        # #bpy.ops.object.editmode_toggle()
        # bmesh.update_edit_mesh(me)               
        # #######

        me = bpy.data.meshes.new('sword_temp_mesh')
        new_obj = bpy.data.objects.new('sword_temp', me) 
        new_obj.location = (0,0,0)
        new_obj.show_name = True
        bpy.context.collection.objects.link(new_obj)
        bm2 = bmesh.new()
        bm2.from_mesh(me)
        self.make_slice(cuts, bm2)
        bm2.to_mesh(me)
        #old_world = context.edit_object.matrix_world.copy()
        reg1 = bpy.context.space_data.region_3d.view_location.copy()
        reg2 = bpy.context.space_data.region_3d.view_rotation.copy()
        reg3 = bpy.context.space_data.region_3d.view_distance
        view1 = bpy.context.space_data.region_3d.view_matrix.copy()        
        pers = bpy.context.space_data.region_3d.view_perspective
        bpy.context.space_data.region_3d.view_perspective = 'ORTHO'        
        self.normalize_view_to_face(context.edit_object, f1)
        new_obj.matrix_world = context.edit_object.matrix_world
        override1 = context.copy()        
        #override1['space_data'].region_3d.view_matrix = mat2        
        # override1['selected_objects'] = []
        # override1['selected_objects'].append(new_obj)
        # override1['selected_objects'].append(context.edit_object)

        with context.temp_override(selected_objects=[new_obj, context.edit_object]):
            bpy.ops.mesh.knife_project(cut_through=True)  

        #bpy.ops.mesh.knife_project(override1, cut_through=self.loop_mode)
        # bpy.ops.mesh.knife_project(override1, cut_through=True)  

        # #####
        # self.bm = self.get_bm()
        # bm = self.bm
        # #####


        if collect:
            coes = self.collect_edges(bm, bm2)
        else:
            coes = []
        bpy.data.objects.remove(new_obj, do_unlink=True)

        bpy.context.space_data.region_3d.view_perspective = pers
        #context.edit_object.matrix_world = old_world
        bpy.context.space_data.region_3d.view_matrix = view1
        bpy.context.space_data.region_3d.view_location = reg1
        bpy.context.space_data.region_3d.view_rotation = reg2
        bpy.context.space_data.region_3d.view_distance = reg3
        self.update_view()

        if self.loop_mode:
            if self.loop_separate:
                for f1 in bm.faces:
                    if f1 in hidden:
                        f1.hide_set(True)
                    else:
                        f1.hide_set(False)

        elif self.loop_mode == False:
            for f1 in bm.faces:
                if f1 in hidden:
                    f1.hide_set(True)
                else:
                    f1.hide_set(False)
        
        me = bpy.context.active_object.data
        #bpy.ops.object.editmode_toggle()
        bmesh.update_edit_mesh(me)    
        # bpy.ops.object.editmode_toggle()
        # bm2 = self.bm
        # bm2.to_mesh(me)  
        # bpy.ops.object.editmode_toggle()

        return coes


    def collect_edges(self, bm,  bm2):
        obj = bpy.context.active_object
        world = obj.matrix_world        
        # bm = self.bm
        vm = bpy.context.space_data.region_3d.view_matrix
        cs = []
        for e1 in bm2.edges:
            a, b = e1.verts
            v1 = vm @ (world @ a.co)
            v2 = vm @ (world @ b.co)
            v1.z = 0
            v2.z = 0
            cs.append((v1, v2))        

        res = []
        for e1 in bm.edges:
            if e1.hide:
                continue
            a, b = e1.verts
            v1 = vm @ (world @ a.co)
            v2 = vm @ (world @ b.co)            
            v1.z = 0
            v2.z = 0            
            for c1, c2 in cs:
                if self.is_online(c1, c2, v1) and self.is_online(c1, c2, v2):
                    res.append(e1)

        return res


    def is_online(self, p1, p2, k):
        m1 = p2 - p1
        m2 = k - p1
        deg = abs(m1.angle(m2))
        if deg < 0.01 or abs(math.radians(180) - deg) < 0.01:
            return True
        else:
            return False


    def make_slice(self, cuts, bm2):
        bm = self.bm

        if self.loop_mode == False:
            for cutting in cuts:
                if cutting == None:
                    continue
                a, b = cutting
                m1 = b - a
                if m1.length == 0:
                    continue
                v1 = bm2.verts.new(a)
                v2 = bm2.verts.new(b)
                e1 = bm2.edges.new((v1, v2))
        else:            
            hmax = 0
            for v1 in bm.verts:
                if v1.co.length > hmax:
                    hmax = v1.co.length

            for cutting in cuts:
                if cutting == None:
                    continue                
                a, b = cutting
                m1 = b - a
                if m1.length == 0:
                    continue
                m1.normalize()
                b = a + m1 * hmax * 2
                a = a - m1 * hmax * 2
                v1 = bm2.verts.new(a)
                v2 = bm2.verts.new(b)
                e1 = bm2.edges.new((v1, v2))



