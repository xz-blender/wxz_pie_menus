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
from . import pref


class BendFaceOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.bend_face_operator"
    bl_label = "Bend Face"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "旋转、平移、混合面"
    #, "GRAB_CURSOR", "BLOCKING"


    prop_extend_mode: BoolProperty(
        name="Sliding rotation",
        description="Slide the vertices along edges when rotate",
        default=False,
    )    


    prop_rotate: FloatProperty(
        name="Rotation",
        description="Define the rotation angle",
        default=0,
        step = 20,
    )    

    prop_movement: FloatProperty(
        name="Movement",
        description="Define the movement distance",
        default=0,
        step = 0.5
    )


    prop_rotate_extrude: BoolProperty(
        name="Rotate Extrude",
        description="Use rotate extrude function",
        default=False,
    )    



    prop_copy: IntProperty(
        name="Number of copies",
        description="Define the number of copies in-between",
        default=1,
        step=1,
        min=1
    )        

    prop_clean: BoolProperty(
        name="Remove double edges",
        description="Check to cleanup overlapping edges",
        default=False,
    )        


    prop_offset: FloatProperty(
        name="Axis offset",
        description="Axis offset for rotation axis",
        default=0,
        step = 1
    )        

    prop_offset_angle: FloatProperty(
        name="Axis offset angle",
        description="An angle applied to axis offset",
        default=0,
        step = 10
    )            

    prop_cooffset: FloatProperty(
        name="Axis offset (colinear)",
        description="Axis offset along the axis",
        default=0,
        step = 1
    )    

    def draw(self, context):
        # if self.actions > 1:
        #     return
        layout = self.layout                
        layout.prop(self, "prop_extend_mode", expand=True)
        layout.prop(self, "prop_rotate", expand=True)
        layout.prop(self, "prop_movement", expand=True)
        layout.prop(self, "prop_rotate_extrude", expand=True)
        layout.prop(self, "prop_copy", expand=True)            
        layout.prop(self, "prop_offset", expand=True)
        layout.prop(self, "prop_offset_angle", expand=True)        
        layout.prop(self, "prop_cooffset", expand=True)        
        layout.prop(self, "prop_clean", expand=True)           


    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm


    def get_edge(self, bm):
        esels = []
        if self.prop_use_active:
            if bm.select_history:
                elem = bm.select_history[-1]
                if isinstance(elem, bmesh.types.BMEdge):
                    return elem
            return None
        else:
            for e1 in bm.edges:
                if len(e1.link_faces) < 2:
                    continue
                a, b = e1.link_faces[:2]
                s1 = a.select
                s2 = b.select
                if (s1 and s2 == False) or (s2 and s1 == False):
                    esels.append(e1)

            if len(esels) == 0:
                return None

            index = self.prop_edge_index % len(esels)
            esel = esels[index]
            return esel



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



    def draw_edge(self, a, b):
        world = bpy.context.active_object.matrix_world
        m1 = b - a
        m2 = m1 * -1
        s1 = b + m2.normalized() * max(m2.length * 0.9, m2.length - 0.05)
        s2 = a + m1.normalized() * max(m1.length * 0.9, m1.length - 0.05)
        gui.lines += [world @ (s1), world @ (s2)]


    def draw_edge_thick(self, a, b):
        world = bpy.context.active_object.matrix_world
        m1 = b - a
        m2 = m1 * -1
        s1 = a
        s2 = b
        gui.lines += [world @ s1, world @ s2]
        c1 = m1.cross(Vector((0,0,1)))
        if c1.length == 0:
            c1 = m1.cross(Vector((1,0,0)))
            if c1.length == 0:
                c1 = m1.cross(Vector((0,1,0)))
        rot = Quaternion(m1, math.radians(360/12))
        mlen = min(0.1, m1.length * 0.1)        
        t1 = c1.normalized() * mlen        
        for i in range(12 + 1):
            t2 = t1.copy()            
            t2.rotate(rot)
            gui.lines += [world @ (t1 + s1), world @ (t2 + s1)]
            gui.lines += [world @ (t1 + s2), world @ (t2 + s2)]
            t1 = t2



    def get_inter_dis(self, v1, v2, v3, v4):
        res = mathutils.geometry.intersect_line_line(v1, v2, v3, v4)        
        if res == None:
            return None
        p1, p2 = res        
        return (p1, (p2 - p1).length)


    def get_sel_edge(self, context, event, bm):
        sel = None
        es = []
        p1, p2 = self.calc_pos_view(context, event)
        for e1 in bm.edges:
            a, b = e1.verts
            res = self.get_inter_dis(a.co, b.co, p1, p2)
            if res != None:
                pint, dis = res
                if self.isInside(pint, a.co, b.co):
                    es.append((a, b, dis))
        if len(es) == 0:
            return None
        a, b, _ = min(es, key=lambda e:e[2])
        return (a, b)


    def check_sel(self, context, event):
        bm = self.bm
        fp = self.get_zoom_dis(bm)
        if self.fn_mode:
            if self.rayface != None:                
                f1 = self.rayface
                cen = f1.calc_center_bounds()
                p = cen + f1.normal * 0.1 * fp
                self.sel = (cen, p)
        else:
            sel = self.get_sel_edge(context, event, bm)
            if sel != None:
                a, b = sel
                self.sel = (a.co.copy(), b.co.copy())


    def process_draw(self, context):
        gui.lines = []
        sel = self.sel
        if sel != None:
            a, b = sel
            self.draw_edge_thick(a, b)



    def prepare_fn(self):
        bm = self.bm        
        self.bvh = mathutils.bvhtree.BVHTree.FromBMesh(bm)


    def get_fn_face(self, context, event):
        bm = self.bm
        #bvh = mathutils.bvhtree.BVHTree.FromBMesh(bm)
        bvh = self.bvh
        vec1, vp, loc = self.get_3d_cursor(context, event)
        obj = bpy.context.active_object
        world = obj.matrix_world
        world2 = world.inverted()
        vec1 = world2 @ vec1
        vp = world2 @ vp
        loc = world2 @ loc
        vec2 = loc - vp
        location, normal, index, distance = bvh.ray_cast(vp, vec2)
        if index == None:
            return
        #self.bm.faces.ensure_lookup_table()
        f1 = bm.faces[index]
        self.rayface = f1
        

    def pro2d(self, loc):
        mat = bpy.context.space_data.region_3d.perspective_matrix
        loc2 = mat @ Vector((loc.x, loc.y, loc.z, 1.0))
        if loc2.w > 0.0:
            return Vector((loc2.x / loc2.w, loc2.y / loc2.w, 0))
        else:
            return Vector()


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


    def mouse_process(self, context, event):        
        if self.sel == None:
            return
        self.px = event.mouse_region_x
        self.py = event.mouse_region_y            
        a, b = self.sel
        gui.lines = []
        self.draw_edge_thick(a, b)



    def mouse_release(self, context):
        self.process_draw(context)
        #self.sel = None
        #self.bm = None
        #self.bmmap = {}
        self.hint()
        self.prepare_fn()
        #self.down = False
        self.last_sel = self.sel    
        # if self.geo_new != None:
        #     self.geo_all += self.geo_new
        #     self.geo_new = None
        #     if self.last_face != None:
        #         self.change_select_face()
        #         self.last_face = None
        
        
    def change_select_face(self):
        bm = self.bm
        for f1 in bm.faces:
            if f1.select:
                f1.select_set(False)
        
        for e1 in bm.edges:
            if e1.select:
                e1.select_set(False)

        bm.select_flush(False)

        lastfs = self.last_face

        for f1 in lastfs:
            f1.select_set(True)
        bm.select_flush(True)
        self.update_mesh(bm)



    # def clean_geo(self):
    #     bm = self.bm
    #     if self.geo_new != None:
    #         bmesh.ops.delete(bm, geom=self.geo_new, context='VERTS')
    #         self.geo_new = None


    # def clean_all_geo(self):
    #     bm = self.bm
    #     if self.geo_all != []:
    #         bmesh.ops.delete(bm, geom=self.geo_all, context='VERTS')
    #         self.geo_all = []


    def copy_select(self, gs):
        bm = self.bm
        ret = bmesh.ops.duplicate(bm, geom=gs)
        #pprint.pprint(ret)
        #print(ret.keys())        
        return ret['geom'], ret['edge_map']


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



    def process_move_copy(self, esel, dis):
        bm = self.bm
        a, b = esel
        m1 = b - a        
        loc = a.copy()        
        sel = [e for e in bm.faces if e.select]               
        fsel = self.divset(sel)
        lastfs = []
        for s1 in fsel:
            lastfs += self.process_rotate_move_single_set(esel, dis, s1, loc)

        self.last_face = lastfs
        if self.prop_clean:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
                    
        self.change_select_face()
        bm.normal_update()
        self.update_mesh(bm)    


    def process_rotate_move_single_set(self, esel, dis, facesel, loc):
        #self.clean_geo()
        # gs1 = [e for e in bm.faces if e.select]
        # gs2 = [e for e in bm.edges if e.select]
        # gs3 = [e for e in bm.verts if e.select]
        a, b = esel
        m1 = b - a        
        #loc = a.copy()
        vs = []
        bm = self.bm

        gs1 = facesel
        gs2 = []
        for f1 in gs1:
            gs2.extend(f1.edges)
        gs2 = list(set(gs2))

        gs3 = []
        for f1 in gs1:
            gs3.extend(f1.verts)
        gs3 = list(set(gs3))

        gs = gs1 + gs2 + gs3

        #self.geo_new = []
        fs2 = self.get_boundary(gs2)     
        edgeset = self.group_loops(fs2)
        # gcopy = [fs2]
        fs2map = {}
        for e1 in fs2:
            fs2map[e1] = e1
        gcopy = [fs2map]        

        fp = self.get_zoom_dis(bm)

        lastfs = None
        geo_count = self.prop_copy
        fss2 = [gs1]
        
        for i in range(geo_count):            
            dis2 = (dis / geo_count) * (i + 1)
            mat = Matrix.Translation(m1.normalized() * dis2 * fp)     
            gsn, edge_map = self.copy_select(gs)
            #self.geo_new += gsn
            vs = [v1 for v1 in gsn if isinstance(v1, bmesh.types.BMVert)]
            for v1 in vs:
                v1.co = mat @ v1.co
            # es = [e1 for e1 in gsn if isinstance(e1, bmesh.types.BMEdge)]
            # es2 = []
            # for e1 in es:
            #     if e1.is_boundary:
            #         es2.append(e1)
            # if len(es2) > 0:
            #     gcopy.append(es2)
            gcopy.append(edge_map)
            lastfs = [f1 for f1 in gsn if isinstance(f1, bmesh.types.BMFace)]
            fss2.append(lastfs)

        try:
            if len(gcopy) > 1:
                for eset in edgeset:
                    for a, b in zip(gcopy[:-1], gcopy[1:]):
                        a2 = []
                        b2 = []
                        for e1 in eset:
                            a2.append(a[e1])
                            b2.append(b[e1])
                        loopsall = a2 + b2
                        bmesh.ops.bridge_loops(bm, edges=loopsall)                
                # for a, b in zip(gcopy[:-1], gcopy[1:]):
                #     bmesh.ops.bridge_loops(bm, edges=a + b)            
                # fs3 = []
                # for fs in fss2[:-1]:
                #     fs3 += fs               
                # res = bmesh.ops.delete(bm, geom=fs3, context='FACES')
                if len(fs2) > 0:
                    fs3 = []
                    for fs in fss2[:-1]:
                        fs3 += fs               
                    res = bmesh.ops.delete(bm, geom=fs3, context='FACES')                
        except Exception as e:
            print(e)

        return lastfs



    def get_rotate_offset_loc(self, gs1, a, b, loc):
        m1 = b - a
        if len(gs1) >= 1:
            f1 = gs1[0]
            neg = -1
            for p in f1.loops:
                v1 = p.vert
                v2 = p.edge.other_vert(v1)
                if v1.co == a and v2.co == b:
                    neg = 1
                    break
            off = m1.cross(f1.normal).normalized() * neg
            ang = self.prop_offset_angle
            off.rotate(Quaternion(m1, math.radians(ang)))
            loc = loc + off * self.prop_offset      
        return loc


    def process_rotate_copy(self, esel, deg):
        bm = self.bm
        a, b = esel
        m1 = b - a        
        loc = a.copy()        
        sel = [e for e in bm.faces if e.select]
        loc = self.get_rotate_offset_loc(sel, a, b, loc)        
        fsel = self.divset(sel)
        lastfs = []
        for s1 in fsel:
            lastfs += self.process_rotate_copy_single_set(esel, deg, s1, loc)

        self.last_face = lastfs
        if self.prop_clean:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
                    
        self.change_select_face()
        bm.normal_update()
        self.update_mesh(bm)       


    def get_boundary(self, gs2):
        fs2 = []
        for e1 in gs2:
            if e1.is_boundary:
                fs2.append(e1)
                continue
            if len(e1.link_faces) >= 2:
                p1, p2 = e1.link_faces[:2]
                if p1.select == False and p2.select:
                    fs2.append(e1)
                elif p1.select and p2.select == False:
                    fs2.append(e1)  
        return fs2         

    def process_rotate_copy_single_set(self, esel, deg, facesel, loc):
        #self.clean_geo()
        # gs1 = [e for e in bm.faces if e.select]
        # gs2 = [e for e in bm.edges if e.select]
        # gs3 = [e for e in bm.verts if e.select]
        a, b = esel
        m1 = b - a        
        #loc = a.copy()
        vs = []
        bm = self.bm

        gs1 = facesel
        gs2 = []
        for f1 in gs1:
            gs2.extend(f1.edges)
        gs2 = list(set(gs2))

        gs3 = []
        for f1 in gs1:
            gs3.extend(f1.verts)
        gs3 = list(set(gs3))

        gs = gs1 + gs2 + gs3

        #self.geo_new = []
        fs2 = self.get_boundary(gs2)  
        edgeset = self.group_loops(fs2)
        #gcopy = [fs2]
        fs2map = {}
        for e1 in fs2:
            fs2map[e1] = e1
        gcopy = [fs2map]

        lastfs = None
        geo_count = self.prop_copy
        
        cooff = self.prop_cooffset
        fss2 = [gs1]

        for i in range(geo_count):
            deg2 = (deg / geo_count) * (i + 1)
            mat = Matrix.Translation(loc).inverted()
            mat = Quaternion(m1, deg2).to_matrix().to_4x4() @ mat
            mat = Matrix.Translation(loc) @ mat
            mat = Matrix.Translation(m1.normalized() * cooff * (i+1)) @ mat
            gsn, edge_map = self.copy_select(gs)
            #self.geo_new += gsn
            vs = [v1 for v1 in gsn if isinstance(v1, bmesh.types.BMVert)]
            for v1 in vs:
                v1.co = mat @ v1.co
            # es = [e1 for e1 in gsn if isinstance(e1, bmesh.types.BMEdge)]
            # es2 = []
            # for e1 in es:
            #     if e1.is_boundary:
            #         es2.append(e1)

            # # ess2 = self.group_loops(es2)
            # # gcopy.append(ess2)
            # if len(es2) > 0:
            #     gcopy.append(es2)
            gcopy.append(edge_map)
            lastfs = [f1 for f1 in gsn if isinstance(f1, bmesh.types.BMFace)]
            fss2.append(lastfs)

        try:
            if len(gcopy) > 1:
                for eset in edgeset:
                    for a, b in zip(gcopy[:-1], gcopy[1:]):
                        a2 = []
                        b2 = []
                        for e1 in eset:
                            a2.append(a[e1])
                            b2.append(b[e1])
                        loopsall = a2 + b2
                        bmesh.ops.bridge_loops(bm, edges=loopsall)
                # for a, b in zip(gcopy[:-1], gcopy[1:]):
                #     #pprint.pprint(a)                    
                #     bmesh.ops.bridge_loops(bm, edges=a + b)            
                #     # for sub1, sub2 in zip(a, b):
                #     #     loops = sub1 + sub2
                #     #     bmesh.ops.bridge_loops(bm, edges=loops)

                if len(fs2) > 0:
                    fs3 = []
                    for fs in fss2[:-1]:
                        fs3 += fs               
                    res = bmesh.ops.delete(bm, geom=fs3, context='FACES')
        except Exception as e:
            print(e)

        return lastfs


    def group_loops(self, es2):
        es3 = list(es2)
        if len(es3) == 0:
            return []
        esur = []
        while True:
            e0 = es3[0]
            linked = [e0]
            for e1 in linked:
                for v1 in e1.verts:
                    for e2 in v1.link_edges:
                        if e2 == e1:
                            continue
                        if (e2 in es3) == False:
                            continue
                        if e2 in linked:
                            continue
                        linked.append(e2)
            esur.append(linked)
            for e1 in linked:
                es3.remove(e1)
            if len(es3) == 0:
                break
        return tuple(esur)




    def process_rotate(self, esel, deg):        
        # if self.prop_copy > 0:            
        if self.prop_rotate_extrude:
            return self.process_rotate_copy(esel, deg)

        bmap = self.bmmap
        a, b = esel
        m1 = b - a
        loc = a.copy()
        vs = []
        bm = self.bm

        for f1 in bm.faces:
            if f1.select:
                vs.extend(f1.verts)        
        vs = list(set(vs))
        obj = bpy.context.edit_object
        mat = Matrix.Translation(loc).inverted()
        qot = Quaternion(m1, deg).to_matrix().to_4x4()
        mat2 = qot @ mat
        mat3 = Matrix.Translation(loc) @ mat2

        if deg == 0:
            sign = 1
        else:
            sign = deg / abs(deg)

        extended = self.prop_extend_mode

        if extended:
            fsel = [f1 for f1 in bm.faces if f1.select]
            if len(fsel) != 1:
                return

        for v1 in vs:
            if extended:
                self.extend_rotate(bmap, v1, loc, m1, qot, sign)
            else:
                v1.co = mat3 @ bmap[v1]

        bm.normal_update()
        self.update_mesh(bm)


    def extend_rotate(self, bmap, v1, loc, m1, qot, sign):
        p1 = bmap[v1] - loc
        pro = p1.project(m1)
        p1b = p1 - pro
        p2 = qot @ p1b
        if p1b.length == 0 or p2.length == 0:
            return
        #deg2 = p2.angle(p1b)
        #high = p1b.length * math.tan(deg2) * sign
        es = [e1 for e1 in v1.link_edges if e1.select == False]
        if len(es) == 0:
            return
        e1 = es[0]
        v2 = e1.other_vert(v1)
        sp = bmap[v1] - bmap[v2]
        sn = sp.normalized()

        fd = p2.cross(m1)                
        res = self.calc_pos(p2, fd, p1b, sn)
        if res == None:
            return
        high = (res - p1b).length                
        v1.co = bmap[v1] + sn * high * sign * -1
        #v1.co = bmap[v1] + Vector((0,0,1))     

   


    def calc_pos(self, center, sn, p, u):
        w = p - center
        snd = sn.dot(u)
        if snd != 0:
            s1 = sn.dot(w) * -1 / snd
            s2 = p + u * s1
            return s2
        else:
            return None



    def process_shift(self, esel, dis):
        # if self.prop_copy > 0:
        if self.prop_rotate_extrude:
            return self.process_move_copy(esel, dis)

        bmap = self.bmmap
        a, b = esel
        m1 = b - a
        loc = a.copy()
        vs = []
        bm = self.bm

        fp = self.get_zoom_dis(bm)

        for f1 in bm.faces:
            if f1.select:
                vs.extend(f1.verts)        
        vs = list(set(vs))
        obj = bpy.context.edit_object
        mat = Matrix.Translation(m1.normalized() * dis * fp)
     
        for v1 in vs:
            v1.co = mat @ bmap[v1]

        self.update_mesh(bm)


    def update_mesh(self, bm):
        me = bpy.context.active_object.data
        #bpy.ops.object.editmode_toggle()
        bmesh.update_edit_mesh(me)
        # bm.to_mesh(me)
        # bpy.ops.object.editmode_toggle()        


    def run_rotate(self, context, event):
        if self.sel == None:
            return
        a, b = self.sel
        gui.lines = []
        self.draw_edge_thick(a, b)
        px = event.mouse_region_x
        py = event.mouse_region_y
        plen1 = px - self.px
        plen2 = bpy.context.region.width
        p3 = plen1 / plen2   
        p4 = p3 * 2 * 360
        if event.ctrl:
            p4 = p4 - (p4 % 5)
        
        gui.txtall = ['旋转角度 : ' + "{:0.2f}".format(p4) + '' ]
        deg = math.radians(p4)
        self.prop_rotate = p4        
        self.process_rotate(self.sel, deg)        


    def run_move(self, context, event):
        if self.sel == None:
            return
        a, b = self.sel
        gui.lines = []
        self.draw_edge_thick(a, b)
        px = event.mouse_region_x
        py = event.mouse_region_y
        plen1 = px - self.px
        plen2 = bpy.context.region.width
        a, b = self.sel
        p3 = plen1 / plen2
        p4 = p3 * 3
        if event.ctrl:
            p4 = p4 - (p4 % 0.25)            
        gui.txtall = ['移动量 : ' + "{:0.2f}".format(p4) + '' ]
        self.prop_movement = p4
        self.process_shift(self.sel, p4)

          

    def get_mats(self):
        vm = bpy.context.space_data.region_3d.view_matrix
        wm = bpy.context.space_data.region_3d.window_matrix
        wm2 = wm.inverted()
        vm2 = vm.inverted()
        return (vm, vm2, wm, wm2)




                        
    def process_init(self):
        self.bmmap = {}
        for v1 in self.bm.verts:
            self.bmmap[v1] = v1.co.copy()
        self.bm2 = self.bm.copy()
        

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        me = bpy.context.active_object.data
        self.bm2.to_mesh(me)
        bpy.ops.object.mode_set(mode='EDIT')

        self.bm = self.get_bm()
        # self.process_init()
        
        self.bmmap = {}
        for v1 in self.bm.verts:
            self.bmmap[v1] = v1.co.copy()

        
        if self.lastmode == 'rotate':
            deg1 = self.prop_rotate
            deg = math.radians(deg1)            
            self.process_rotate(self.last_sel, deg)
        elif self.lastmode == 'move':
            dis = self.prop_movement            
            self.process_shift(self.last_sel, dis)

        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing 


    def invoke2(self, context, event):
        if context.edit_object:

            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}



    def reset_all(self):
        pass
        # self.clean_all_geo()
        # bm = self.bm        
        # for v1 in bm.verts:
        #     v1.co = self.back[v1]          
        # bm.normal_update()  
        # self.update_mesh(bm)


    def backup_all(self):
        bm = self.bm
        self.back = {}
        for v1 in bm.verts:
            self.back[v1] = v1.co.copy()            

                     
    def load_undo(self, context, event):
        bm = self.bm
        bmap = self.bmmap
        for v1 in bm.verts:
            v1.co = bmap[v1]
        bm.normal_update()  
        self.update_mesh(bm)
        if self.fn_mode:
            if event.shift == False:
                self.prepare_fn()
                self.get_fn_face(context, event)


    def draw_point(self, p1):
        gui.lines += [p1 + Vector((0.01, 0, 0)), p1 - Vector((0.01, 0, 0))]
        gui.lines += [p1 + Vector((0, 0.01, 0)), p1 - Vector((0, 0.01, 0))]



    def degree_key(self, d1):
        self.sel = self.last_sel
        if self.sel == None:
            return
        neg = 1
        if self.prop_rotate == d1:
            neg = -1
        dvalue = d1 * neg
        deg = math.radians(dvalue)
        self.prop_rotate = dvalue
        self.process_rotate(self.sel, deg)        


    def overall(self, context, event):        

        if event.type == 'Q':
            if event.value == 'PRESS':
                # print(self.actions)
                gui.draw_handle_remove()
                return {'FINISHED'}        

        elif event.type == 'ONE':
            if event.value == 'PRESS':
                self.degree_key(-30)
                return {'RUNNING_MODAL'}

        elif event.type == 'TWO':
            if event.value == 'PRESS':
                self.degree_key(-45)
                return {'RUNNING_MODAL'}

        elif event.type == 'THREE':
            if event.value == 'PRESS':
                self.degree_key(-60)
                return {'RUNNING_MODAL'}

        elif event.type == 'FOUR':
            if event.value == 'PRESS':
                self.degree_key(-90)
                return {'RUNNING_MODAL'}                
                

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.actions += 1
                self.lastmode = 'rotate'
                self.process_init()
                self.mouse_process(context, event)
                self.handlers.append(self.handle_rotate)
                #self.process(context)
                return {'RUNNING_MODAL'}

        elif event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                self.actions += 1
                self.lastmode = 'move'
                self.process_init()
                self.mouse_process(context, event)
                self.handlers.append(self.handle_move)
                return {'RUNNING_MODAL'}

        elif event.type == 'MOUSEMOVE':
            if self.fn_mode:
                if event.shift == False:
                    self.get_fn_face(context, event)
                    self.check_sel(context, event)
                    self.process_draw(context)
            else:
                self.check_sel(context, event)
                self.process_draw(context)
            return {'PASS_THROUGH'}      


        elif event.type == 'F':
            if event.value == 'PRESS':
                if self.fn_mode:
                    self.fn_mode = False                    
                else:
                    self.fn_mode = True
                    self.prepare_fn()
                    self.get_fn_face(context, event)
                self.check_sel(context, event)
                self.process_draw(context)
            return {'RUNNING_MODAL'}


        elif event.type == 'S':
            if event.value == 'PRESS':
                if self.prop_extend_mode:
                    self.prop_extend_mode = False                    
                else:
                    self.prop_extend_mode = True
                self.hint()
            return {'RUNNING_MODAL'}

        elif event.type == 'ESC':
            if event.value == 'PRESS':
                self.reset_all()
                gui.draw_handle_remove()
                return {'CANCELLED'}                

        return None




    def handle_rotate(self, context, event):
        # if self.copy_mode:
        #     if event.type == 'WHEELUPMOUSE':                
        #         self.geo_count += 1                
        #         self.run_rotate(context, event)
        #         return {'RUNNING_MODAL'} 
        #     elif event.type == 'WHEELDOWNMOUSE':
        #         self.geo_count -= 1
        #         if self.geo_count < 1:
        #             self.geo_count = 1
        #         self.run_rotate(context, event)
        #         return {'RUNNING_MODAL'} 

        if event.type == 'MOUSEMOVE':            
            self.run_rotate(context, event)
            return {'RUNNING_MODAL'}
        elif event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                self.mouse_release(context)
                if self.prefs['bool_con']:
                    self.handlers.pop()
                    return {'RUNNING_MODAL'}
                else:
                    gui.draw_handle_remove()
                    return {'FINISHED'}                
        return None


    def handle_move(self, context, event):
        if event.type == 'MOUSEMOVE':            
            self.run_move(context, event)
            return {'RUNNING_MODAL'}
        elif event.type == 'RIGHTMOUSE':
            if event.value == 'RELEASE':
                self.mouse_release(context)

                if self.prefs['bool_con']:
                    self.handlers.pop()
                    return {'RUNNING_MODAL'}
                else:
                    gui.draw_handle_remove()
                    return {'FINISHED'}
                
        return None



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



    def invoke(self, context, event):  
        if context.edit_object:
            context.window_manager.modal_handler_add(self)

            self.prefs = pref.get_pref()            

            self.bm = self.get_bm()     
            self.bm2 = self.bm.copy()       
            #self.backup_all()
            self.sel = None
            self.fn_mode = False
            self.rayface = None
            self.bvh = None        
            self.handlers = [self.overall]
            self.lastmode = None
            self.last_sel = None
            #self.number_mode = False
            self.copy_mode = False
            #self.geo_new = None
            #self.geo_all = []
            #self.geo_count = 1

            self.prop_movement = 0
            self.prop_rotate = 0
            # self.prop_copy = 0
            # self.prop_offset = 0
            # self.prop_offset_angle = 0
            # self.prop_cooffset = 0
            self.prop_rotate_extrude = False
            
            #self.prop_clean = False
            self.actions = 0

            gui.draw_handle_add((self, context))
            gui.text_handle_add((self, context))
            self.hint()
            
            self.process_draw(context)
            return {'RUNNING_MODAL'} 
        else:
            return {'CANCELLED'}


    def hint(self):
        extra_text = ["1键=30°，2键=60°，3键=45°，4键=90°,再次按下相同的键将设置为负值."]
        base_text = ['鼠标左键：旋转', '鼠标右键：移动', '按住Ctrl键：吸附到整数量，F键：面法线模式', 'S键：滑动模式', 'Q键-确认，Esc键-取消']
        if self.prop_extend_mode:
            gui.txtall = ['滑动旋转' ]+base_text+extra_text
        else:
            gui.txtall = base_text+extra_text



