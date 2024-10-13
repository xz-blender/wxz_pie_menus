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


import itertools
import math
from functools import reduce

import bgl
import blf
import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy_extras import view3d_utils
from mathutils import Matrix, Quaternion, Vector, bvhtree, geometry

from . import gui

if not bpy.app.background:
    import gpu
    from gpu_extras.batch import batch_for_shader

    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    shader.bind()


class SlowBevelOperator(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "mesh.slow_bevel_operator"
    bl_label = "Slow Bevel —— 安全斜角"
    bl_options = {"REGISTER", "UNDO"}
    # , "GRAB_CURSOR", "BLOCKING"

    propminface: FloatProperty(name="最小面", description="Min face", default=0.05)

    propoffset: FloatProperty(name="偏移量", description="Offset of bevel", default=0.2)

    propcut: IntProperty(name="迭代次数", description="Number of iteration", default=1)

    prop_removedouble: BoolProperty(name="移除重叠点", description="Remove doubles", default=False)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.prop(self, "propoffset", expand=True)
        layout.prop(self, "propcut", expand=True)
        layout.prop(self, "prop_removedouble", expand=True)
        layout.prop(self, "propminface", expand=True)

    def __init__(self):
        self.handlers = []
        self.eng = []
        self.eng2 = []
        pass

    def draw_text_callback(self, context):
        self.draw_text([90, 120], "Bevel")

    def draw_text(self, pos, text):
        if pos == None:
            return
        font_id = 0  # XXX, need to find out how best to get this.
        # draw some text
        blf.position(font_id, pos[0], pos[1], 0)
        blf.size(font_id, 16, 72)
        blf.draw(font_id, text)

    def draw_3d(self, context):
        obj = context.edit_object
        world = obj.matrix_world

        plist = []
        for a, b in self.eng:
            plist += [world @ a, world @ b]
        gui.draw_line(plist, (1, 1, 0, 1), True, True, 1)

        plist = []
        for a, b in self.eng2:
            plist += [world @ a, world @ b]
        gui.draw_line(plist, (1, 0, 0, 1), True, True, 1)
        pass

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == "MESH"
        editing = context.mode == "EDIT_MESH"
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return editing and (is_face_mode or is_edge_mode)

    def cleanup(self):

        bpy.types.SpaceView3D.draw_handler_remove(self.handle3d, "WINDOW")

        bpy.types.SpaceView3D.draw_handler_remove(self.handle3d_text, "WINDOW")

    def overall(self, context, event):
        obj = context.edit_object
        if event.type == "LEFTMOUSE":
            if event.value == "PRESS":
                self.cleanup()
                return {"FINISHED"}

        elif event.type == "ESC":
            if event.value == "PRESS":
                self.cleanup()
                return {"CANCELLED"}

    def modal(self, context, event):
        context.area.tag_redraw()
        editing = context.mode == "EDIT_MESH"
        if editing == False:
            return {"FINISHED"}

        if not context.edit_object:
            return {"FINISHED"}

        if len(self.handlers) > 0:
            handle = self.handlers[-1]
            p = handle(context, event)
            if p == None:
                if event.value == "NOTHING":
                    return {"PASS_THROUGH"}
                elif "NUM" in event.type:
                    return {"PASS_THROUGH"}
                elif "MOUSE" in event.type:
                    return {"PASS_THROUGH"}
                else:
                    return {"RUNNING_MODAL"}
            else:
                return p

        return {"RUNNING_MODAL"}

    def get_bm(self):
        obj = bpy.context.edit_object
        me = obj.data
        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        return bm

    def execute(self, context):
        self.process(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        if context.edit_object:

            # modalmode = True
            modalmode = False

            if modalmode:
                context.window_manager.modal_handler_add(self)

                self.handle3d = bpy.types.SpaceView3D.draw_handler_add(self.draw_3d, (context,), "WINDOW", "POST_VIEW")

                self.handle3d_text = bpy.types.SpaceView3D.draw_handler_add(
                    self.draw_text_callback, (context,), "WINDOW", "POST_PIXEL"
                )

                self.handlers.append(self.overall)

                self.process(context)
                return {"RUNNING_MODAL"}

            else:
                self.process(context)
                return {"FINISHED"}

        else:
            return {"CANCELLED"}

    def process(self, context):
        bm = self.get_bm()
        if bm == None:
            return None

        num_cut = max(0, self.propcut)
        if num_cut > 4:
            num_cut = 4
        offset = max(0, self.propoffset)

        for i in range(num_cut):
            div = i * i + 1
            self.slow_bevel_2(bm, offset / div)

            if self.prop_removedouble:
                bmesh.update_edit_mesh(context.edit_object.data)
                for f1 in bm.faces:
                    f1.select_set(True)
                bm.select_flush(True)
                bpy.ops.mesh.remove_doubles()

        for f1 in bm.faces:
            f1.select_set(False)
        bm.select_flush(False)
        bmesh.update_edit_mesh(context.edit_object.data)
        # print('finish')

    def ep_contain(self, e1, vp):
        o1, o2 = e1.verts
        main = o2.co - o1.co
        m1 = vp.co - o1.co
        p1 = m1.project(main)
        p1 = p1 + o1.co
        if (p1 - o1.co).length + (p1 - o2.co).length <= main.length:
            return True
        else:
            return False

    def ep_contain_double(self, e1, e2):
        o1, o2 = e1.verts
        v1, v2 = e2.verts
        if self.ep_contain(e1, v1):
            return True
        elif self.ep_contain(e1, v2):
            return True
        elif self.ep_contain(e2, o1):
            return True
        elif self.ep_contain(e2, o2):
            return True
        else:
            return False

    def check_proj_e(self, e1, e2, inv):
        v1, v2 = e1.verts
        a, b = e2.verts
        if self.ep_contain(e1, a):
            return True
        elif self.ep_contain(e1, b):
            return True
        else:
            pint = self.crossed(v1.co, v1.co + inv, a.co, b.co)
            if pint != None:
                # self.eng.append((v1.co.copy(), v1.co + inv))
                return True
            pint2 = self.crossed(v2.co, v2.co + inv, a.co, b.co)
            if pint2 != None:
                # self.eng.append((v2.co.copy(), v2.co + inv))
                return True
            return False

    def orient_points2(self, f1, ep, inv):
        ps = []
        ps2 = []
        es = [e1 for e1 in f1.edges]
        es.remove(ep)
        o1, o2 = ep.verts
        for e1 in es:
            # if self.ep_contain_double(ep, e1):
            if self.check_proj_e(ep, e1, inv):
                a, b = e1.verts
                """
                mid = (o1.co+o2.co)/2
                mid2 = (a.co+b.co)/2
                self.eng.append((mid, mid2))
                """
                ps.append(a)
                ps.append(b)
        if o1 in ps:
            ps.remove(o1)
        if o2 in ps:
            ps.remove(o2)
        if len(ps) == 0:
            return None

        for v1 in ps:
            # self.eng.append((mid1, mid1+inv1 * mp1))
            # self.eng.append((mid2, mid2+inv2 * mp2))
            # self.eng.append((v1.co.copy(), o1.co.copy()))
            m1 = v1.co - o1.co
            p1 = m1.project(inv)
            # self.eng.append((o1.co.copy(), o1.co.copy() + p1))
            """
            if p1.length == 0 or inv.length == 0:
                continue
            if p1.angle(inv) < 0.1:
                ps2.append(p1)
            """
            ps2.append(p1)
        if len(ps2) == 0:
            return None
        pm = min(ps2, key=lambda e: e.length)

        off2 = self.propminface
        if off2 > 0.5:
            off2 = 0.5
        elif off2 < 0:
            off2 = 0
        pm2 = pm.length * (0.5 - off2)
        return pm2

    def slow_bevel_2(self, bm, offset):
        vsall = list(bm.verts)
        esall = list(bm.edges)
        geos = vsall + esall

        res = bmesh.ops.bevel(
            bm,
            geom=geos,
            offset=0.0001,
            offset_type="OFFSET",
            affect="EDGES",
            profile=0.5,
            segments=1,
            clamp_overlap=False,
        )

        fss = set(res["faces"])
        vset = set(res["verts"])
        vset2 = list(bm.verts)
        fs3 = set(list(bm.faces))
        fs4 = fs3 - fss
        ves = {}

        for v1 in vset2:
            ves[v1] = []

        for f1 in fs4:
            emp = {}
            einvp = {}
            for pp in f1.loops:
                v1 = pp.vert
                e1 = pp.edge
                e1o = e1.other_vert(v1)
                inv1 = self.get_inv(f1, v1, e1o)
                if inv1 == None:
                    continue
                # mid = (v1.co + e1o.co)/2
                mp1 = self.orient_points2(f1, e1, inv1)
                mcen1 = self.tri_center(f1, e1)
                mp3 = self.minselect(mp1, mcen1)
                inv1 *= offset * 0.1
                # inv1 = self.min_vec(inv1, mp1)
                emp[e1] = mp3
                einvp[e1] = inv1

            for pp in f1.loops:
                v1 = pp.vert
                e1 = pp.edge
                e2 = pp.link_loop_prev.edge
                e1o = e1.other_vert(v1)
                e2o = e2.other_vert(v1)
                if e1 not in emp or e2 not in emp:
                    continue
                mp31 = emp[e1]
                mp32 = emp[e2]
                mp4 = min(mp31, mp32)
                inv1 = einvp[e1]
                inv2 = einvp[e2]
                inv1 = self.min_vec(inv1, mp4)
                inv2 = self.min_vec(inv2, mp4)
                p1 = self.slide_v2(v1.co, e1o.co, inv1, e2o.co, inv2)
                ves[v1].append(p1)

        for v1 in vset2:
            ps = ves[v1]
            if len(ps) == 0:
                continue
            mv = Vector()
            total = 0
            for p1 in ps:
                if p1 != None:
                    mv += p1
                    total += 1
            if total > 0:
                mv /= total
            v1.co += mv
            # self.eng.append((v1.co.copy(), v1.co + mv))

    def tri_center(self, f1, e1):
        if len(f1.edges) != 3:
            return None
        cen = f1.calc_center_median()
        v1, v2 = e1.verts
        mid = (v1.co + v2.co) / 2
        pm = (cen - mid).length / 2.5
        return pm

    def minselect(self, m1, m2):
        if m1 == None:
            if m2 == None:
                return None
            else:
                return m2
        else:
            if m2 == None:
                return m1
            else:
                return min(m1, m2)

    def crossed(self, v1, v2, v3, v4):
        pin = geometry.intersect_line_line(v1, v2, v3, v4)
        if pin == None:
            return None
        pa, pb = pin
        if pa == pb:
            return pa
        return None

    def min_vec(self, v1, m1):
        if m1 == None:
            return v1
        return v1.normalized() * min(v1.length, m1)

    def get_inv(self, f1, v1, v2):
        m1 = v2.co - v1.co
        inv = f1.normal.cross(m1).normalized()
        if inv.length == 0:
            return None
        else:
            return inv

    def slide_v2(self, v1co, e1o, inv1, e2o, inv2):
        plen = (e1o - v1co).length + (e2o - v1co).length
        b1 = (inv1 + inv2).normalized() * plen * 2
        if inv1.length > inv2.length:
            inv3 = inv1
        else:
            inv3 = inv2
        d1 = b1.normalized().dot(inv3.normalized())
        if d1 == 0:
            return None
        blen1 = inv3.length / d1
        if blen1 > b1.length:
            return None
        # blen1 = min(blen1, b1.length)
        # print(blen1, blen2)
        c1 = b1.normalized() * blen1  # v1co +
        return c1

    def find_inv(self, e1, v1, f1):
        for pp in f1.loops:
            if pp.edge == e1:
                c1 = pp.vert
                c2 = pp.edge.other_vert(c1)
                m1 = c2.co - c1.co
                inv = f1.normal.cross(m1).normalized()
                if inv.length == 0:
                    return None
                else:
                    return inv
        return None
