import math

import bpy
import numpy as np
from mathutils import Matrix, Vector, kdtree
from mathutils.bvhtree import BVHTree

if not bpy.app.background:
    import gpu
    from gpu_extras.batch import batch_for_shader

import blf
import bmesh
from bpy_extras import view3d_utils

from .volume_preserve_smoothing import CommonSmoothMethods, close_bmesh, get_mirrored_verts

# round_to_n = lambda x, n: round(x, -int(math.floor(math.log10(x))) + (n - 1))
round_to_first_digit = lambda x: math.pow(10, math.floor(math.log10(x)))


def get_obj_mesh_bvht(obj, depsgraph, with_mods=True, world_space=True):
    if with_mods:
        if world_space:
            # ? OLD way: wont work if mod uses some helper, or there is parent or something, but faster
            obj.data.transform(obj.matrix_world)
            depsgraph.update()  # fixes bad transformation baing applied to obj
            bvh = BVHTree.FromObject(obj, depsgraph)  # ? not required to get with mod: obj.evaluated_get(depsgraph)
            obj.data.transform(obj.matrix_world.inverted())

            # * better but slower - even 5-10 times (0.05 sec), wont work on non meshes (curves?)
            # obj_eval = obj.evaluated_get(depsgraph)
            # bm = bmesh.new()   # create an empty BMesh
            # bm.from_mesh(obj_eval.to_mesh())   # with modifiers
            # bm.transform(obj.matrix_world)
            # bm.normal_update()
            # bvh = BVHTree.FromBMesh(bm)  # ? not required to get with mod: obj.evaluated_get(depsgraph)
            # bm.free()  # free and prevent further access
            # obj_eval.to_mesh_clear()
            return bvh
        else:
            return BVHTree.FromObject(obj, depsgraph)  # with modes
    else:
        if world_space:
            # 4 times slower than data.transform
            # bvh1 =  BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
            # bmesh - same time as data.transform
            obj.data.transform(obj.matrix_world)
            bvh = BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])
            obj.data.transform(obj.matrix_world.inverted())
            return bvh
        else:
            return BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices for p in obj.data.polygons])


def raycast(context, mouse_2d_co):
    if not MyCustomShapeWidget.snap_surface_BVHT:
        depsgraph = context.evaluated_depsgraph_get()
        MyCustomShapeWidget.snap_surface_BVHT = get_obj_mesh_bvht(
            context.active_object, depsgraph, with_mods=False, world_space=False
        )
    snap_surface_BVHT = MyCustomShapeWidget.snap_surface_BVHT

    region = context.region
    rv3d = context.region_data
    ray_max = 1000.0
    mat_inv = context.active_object.matrix_world.inverted()

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_2d_co)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_2d_co)

    if rv3d.view_perspective == "ORTHO":  # move ortho origin back
        ray_origin = ray_origin - (view_vector * (ray_max / 2.0))

    ray_target = ray_origin + (view_vector * ray_max)

    ray_origin_obj = mat_inv @ ray_origin  # not sure why this order works, whatever...
    ray_target_obj = mat_inv @ ray_target
    view_vector_obj = ray_target_obj - ray_origin_obj

    # ray_direction = ray_origin - ray_target
    hit_local, normal, face_index, depth = snap_surface_BVHT.ray_cast(ray_origin_obj, view_vector_obj)
    return hit_local, normal


def get_view_vec(context):
    rv3d = context.region_data
    view_mat = rv3d.view_matrix.to_3x3()
    # screen_depth = view_ma[2].xyz
    # screen_up = view_ma[1].xyz
    # screen_right = view_ma[1].xyz
    return view_mat[2].xyz


def circle_coords_calc(circle_resol):
    import math

    m_2pi = 2 * math.pi
    coords = ()
    for a in range(circle_resol + 1):
        ang = (m_2pi * a) / circle_resol
        coords += ((math.sin(ang), math.cos(ang), 0.0),)
    return coords


circle_co = circle_coords_calc(32)

shader_3d_uniform = gpu.shader.from_builtin("UNIFORM_COLOR")


def draw_circle_px(self, color):
    gpu.state.line_width_set(2)
    gpu.state.blend_set("ALPHA")
    with gpu.matrix.push_pop():
        gpu.matrix.multiply_matrix(self.matrix_basis)
        batch = batch_for_shader(shader_3d_uniform, "LINE_LOOP", {"pos": circle_co})
        shader_3d_uniform.bind()
        shader_3d_uniform.uniform_float("color", color)
        batch.draw(shader_3d_uniform)

    gpu.state.blend_set("NONE")
    gpu.state.line_width_set(1)


# function that draws gls text in 2d mouse position
def draw_text_px(self, color):
    gpu.state.blend_set("ALPHA")
    font_id = 0
    blf.color(font_id, *color)
    blf.position(font_id, self.mouse_2d_co[0] - 20, self.mouse_2d_co[1], 0)
    blf.size(font_id, 30, 72)
    blf.draw(font_id, str(int(self.strength + 0.5)))
    gpu.state.blend_set("NONE")


class ToolVpsSmooting(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"

    bl_idname = "pie.my_vol_smooth"
    bl_label = "Volume Smooth"
    bl_description = "Volume Smooth Tool"
    bl_icon = "ops.mesh.vertices_smooth"
    bl_widget = "MESH_GGT_brush_circle"
    bl_keymap = (
        (
            "mesh.smooth_brush_vps",
            {"type": "LEFTMOUSE", "value": "PRESS"},
            {
                "properties": [
                    ("draw", True),
                ]
            },
        ),
        (
            "mesh.smooth_brush_vps",
            {"type": "F", "value": "PRESS"},
            {
                "properties": [
                    ("resize", True),
                ]
            },
        ),
        (
            "mesh.smooth_brush_vps",
            {"type": "F", "value": "PRESS", "shift": True},
            {
                "properties": [
                    ("strengthen", True),
                ]
            },
        ),
    )

    def draw_settings(context, layout, tool):
        smooth_props = tool.operator_properties("mesh.smooth_brush_vps")
        row = layout.row(align=True)
        row.prop(smooth_props, "radius")
        row.prop(smooth_props, "only_selected", icon="VERTEXSEL", icon_only=True)
        row.prop(smooth_props, "back_face_mask", icon="SNAP_NORMAL", icon_only=True)
        ic = "LOCKED" if smooth_props.freeze_border else "UNLOCKED"
        row.prop(smooth_props, "freeze_border", icon=ic, icon_only=True)

        layout.prop(smooth_props, "strength")
        layout.prop(smooth_props, "method", text="")
        layout.prop(smooth_props, "tension", text="")

        row = layout.row(align=True)
        row.prop(smooth_props, "pull_strength")
        row.prop(smooth_props, "use_pressure", icon="STYLUS_PRESSURE", icon_only=True)


# NOTE: gizmo wont show up when LMB is clicked (for this we draw using modal drawing)
class MyCustomShapeWidget(bpy.types.Gizmo):
    bl_idname = "VIEW3D_GT_Circle_Gizmo"
    __slots__ = (
        "last_depth",
        "depsgraph",
        "first_run",  # do not run gizmo draw till we inith matrix_basis
    )
    bvh_run_update = False
    snap_surface_BVHT = None

    def handler(self, scene, arg):
        if MyCustomShapeWidget.bvh_run_update is False:
            MyCustomShapeWidget.bvh_run_update = self.depsgraph.id_type_updated(
                "MESH"
            ) or self.depsgraph.id_type_updated("OBJECT")
            # print(f"{self.depsgraph.id_type_updated('MESH')=}")
            # print(f"{self.depsgraph.id_type_updated('OBJECT')=}\n")

    def update_matrix(self, context, location):
        hit_local, normal = raycast(context, location)
        hover_over_mesh = hit_local is not None
        if hit_local is None:
            rv3d = context.region_data
            normal = get_view_vec(context)
            hit_local = view3d_utils.region_2d_to_location_3d(context.region, rv3d, location, self.last_depth)

        self.last_depth = hit_local.copy()
        quat = normal.to_track_quat("Z", "Y")  # to_track_quat(track, up)
        rot_mat = quat.to_matrix().to_4x4()

        # NOTE get circle radius, from vps_tool radius prop
        tool = context.workspace.tools.from_space_view3d_mode(context.mode)
        tool_props = tool.operator_properties("mesh.smooth_brush_vps")
        rad_scale_mat = Matrix.Scale(tool_props.radius, 4)

        if hover_over_mesh:
            hit_world = context.active_object.matrix_world @ hit_local
            # self.matrix_basis = context.active_object.matrix_world @ Matrix.Translation(hit_local) @ rot_mat @ rad_scale_mat
            self.matrix_basis = Matrix.Translation(hit_world) @ rot_mat @ rad_scale_mat
        else:
            self.matrix_basis = Matrix.Translation(hit_local) @ rot_mat @ rad_scale_mat

    def finish_gizmo(self):
        handler = object.__getattribute__(self, "handler")
        if handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(handler)

    def draw(self, context):
        # print("Gizmo draw")
        if not self.first_run:  # avoids drawing brush circle at Vector((0, 0, 0))
            draw_circle_px(self, (0.9, 0.9, 0.9, 1))

    # def draw_select(self, context, select_id): #XXX breaks test_select !
    #     mat = context.active_object.matrix_world
    #     self.draw_preset_circle(mat, axis='POS_Z', select_id=select_id)

    def setup(self):
        # print("Gizmo setup")
        self.first_run = True
        self.use_draw_offset_scale = True
        self.last_depth = Vector((0, 0, 0))

    # def invoke(self, context, event): #seems it is not executed eve onec..
    #     # print("Gizmo invoke !!")
    #     return {'RUNNING_MODAL'}

    # def exit(self, context, cancel): #seems it is not executed eve onec..
    #     print("gizmo Exit")

    def test_select(self, context, location):
        # makes it possible to hover higlight, wont work f draw_select() is used at same time
        self.update_matrix(context, location)
        if self.first_run:
            self.depsgraph = context.evaluated_depsgraph_get()
            bpy.app.handlers.depsgraph_update_post.append(self.handler)
        else:
            if MyCustomShapeWidget.bvh_run_update:
                last_operator = context.window_manager.operators[-1] if bpy.context.window_manager.operators else None
                if not last_operator or last_operator.name not in {"Select", "Loop Select", "(De)select All"}:
                    context.active_object.update_from_editmode()
                    self.depsgraph = (
                        context.evaluated_depsgraph_get()
                    )  # XXX: be careful to not trigger depsgraph update loop
                    MyCustomShapeWidget.snap_surface_BVHT = get_obj_mesh_bvht(
                        context.active_object, self.depsgraph, with_mods=False, world_space=False
                    )
                MyCustomShapeWidget.bvh_run_update = False

        self.first_run = False
        context.area.tag_redraw()
        return -1

    # def modal(self, context, event, tweak): #seems it is not executed eve onec..
    #     print('Gizmo modal')
    #     return {'RUNNING_MODAL'}


class BrushCircleGizmoGroup(bpy.types.GizmoGroup):
    bl_idname = "MESH_GGT_brush_circle"
    bl_label = "Side of Plane Gizmo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D"}

    @classmethod
    def poll(cls, context):
        is_ht_on = (
            context.mode == "EDIT_MESH"
            and context.workspace.tools.from_space_view3d_mode(mode="EDIT_MESH").idname == "pie.my_vol_smooth"
        )
        if not is_ht_on or not context.scene.vps_gizmo_show:
            wm = context.window_manager
            wm.gizmo_group_type_unlink_delayed(BrushCircleGizmoGroup.bl_idname)
            return False
        return True

    def setup(self, context):  # executed once on gizmo start
        self.widget = self.gizmos.new("VIEW3D_GT_Circle_Gizmo")
        depsgraph = context.evaluated_depsgraph_get()
        MyCustomShapeWidget.snap_surface_BVHT = get_obj_mesh_bvht(
            context.active_object, depsgraph, with_mods=False, world_space=False
        )

    # def draw_prepare(self, context): #we can update gizmo here, eg mat_basisa
    #     pass

    def __del__(self):
        if hasattr(self, "widget"):
            object.__getattribute__(self.widget, "finish_gizmo")()


class VPS_OT_DrawSmooth(bpy.types.Operator, CommonSmoothMethods):
    bl_idname = "mesh.smooth_brush_vps"
    bl_label = "VPS Smooth Brush"
    bl_description = "VPS Smooth Brush"
    bl_options = {"REGISTER", "UNDO"}

    draw: bpy.props.BoolProperty(name="draw", description="", default=False)
    resize: bpy.props.BoolProperty(name="resize", description="", default=False)
    strengthen: bpy.props.BoolProperty(name="strengthen", description="", default=False)

    radius: bpy.props.FloatProperty(name="Radius", description="Brush Radius", default=0.5, soft_min=0.001, soft_max=1)
    strength: bpy.props.FloatProperty(
        name="Smoothing", description="Smoothing strength", default=50, min=0, max=100, subtype="PERCENTAGE"
    )
    pull_strength: bpy.props.FloatProperty(
        name="Pull", description="Pull strength", default=50, min=0, max=100, subtype="PERCENTAGE"
    )
    use_pressure: bpy.props.BoolProperty(
        name="Use Pressure", description="Affects only mesh pulling (not smooting)", default=True
    )
    only_selected: bpy.props.BoolProperty(
        name="Only selected", description="Affect only selected geometry", default=False
    )
    back_face_mask: bpy.props.BoolProperty(
        name="Backface mask", description="Affect only vertexes that face the viewer", default=False
    )
    freeze_border: bpy.props.BoolProperty(name="Freeze border", description="Freeze border verts", default=False)
    tension: bpy.props.EnumProperty(
        items=(
            ("UNIFORM", "Uniform", "Makes Faces shape square", "", 0),
            ("INVERSE", "Keep", "Keep Faces proportions", "", 1),
            ("PROPORTIONAL", "More Uniform", "Stronger Equalize", "", 2),
        ),
        name="Face shape",  # -- aka Inverse to edge lengthj
        default="UNIFORM",
    )
    method: bpy.props.EnumProperty(
        items=(
            ("LC", "Laplacian", "Fast but medium quailty"),
            ("INFlATE", "Inflate", "Good for round surfaces"),
            ("VOL", "Volume", "Hight Quailty but slower"),
        ),
        name="Smooth Method",
        default="LC",
    )

    _circel2d_handle = None
    _text2d_handle = None

    def smooth_write(self, context):
        sm_strength = self.strength / 100 / 5
        pull_strength = self.pull_strength / 200
        if self.back_face_mask:
            back_face_dot = np.einsum("i,ji->j", self.view_local, self.o_normal)  #  view_perpendicular.dot(normal_li)
            bf_mask = back_face_dot < 0

        move_perp_normal_comp = None
        if self.prev_hit_loc and self.pull_strength:  # hit_world = mat @ self.hit_loc
            move_3d = self.hit_local - self.prev_hit_loc  # N: we want to obtain move_perp_to_normal_comp

            # N: split move_3d into  view parallel and perpendicular components
            move_view_component = move_3d.dot(self.view_local) * self.view_local
            move_view_perp_comp = np.array(
                move_3d - move_view_component
            )  # view_perpendicular component  of move_3d to view vector

            # N: split move_view_perp_comp into vert normal parallel and perpendicular components
            # masked = np.maximum(move_dot_normal, 0)
            move_dot_normal = np.einsum(
                "i,ji->j", move_view_perp_comp, self.o_normal
            )  #  view_perpendicular.dot(normal_li)
            move_normal_vec = move_dot_normal[:, None] * self.o_normal
            move_perp_normal_comp = (
                move_view_perp_comp[None, :] - move_normal_vec
            )  # N: this is the actuall movement of vert in local space

            if self.back_face_mask:
                move_perp_normal_comp = np.where(bf_mask[:, None], 0, move_perp_normal_comp)

            for axis_id, mirror_mask in self.on_axis_vmask.items():
                move_perp_normal_comp[mirror_mask, axis_id] = 0
            # N:  view_perpendicular.dot(self.o_normal)

        vpull_mask = {}  # local - holds current stroke affected verts offset
        stroke_mask = {i: 0 for i in range(self.sel_v_len)}  # mostly for use_mirror.
        radius = self.radius / (context.active_object.scale.length / math.sqrt(3))
        for co, v_id, dist in self.kd.find_range(self.hit_local, radius):
            factor = 1 - dist / radius
            self.vsmooth_mask[v_id] = min(self.vsmooth_mask[v_id] + factor * sm_strength, 1.0)
            stroke_mask[v_id] = factor
            if move_perp_normal_comp is not None:
                vpull_mask[v_id] = min(factor * pull_strength * self.stored_pressure, 1.0)
        if sm_strength:
            smooth_mask = np.fromiter(self.vsmooth_mask.values(), "f", self.sel_v_len)  # zero out masked verts
            smooth_co = self.p_co * smooth_mask[:, None] + self.o_co * (
                1.0 - smooth_mask[:, None]
            )  # blend o_co with p_co (smoothed verts)
            if self.back_face_mask:
                smooth_co = np.where(bf_mask[:, None], self.o_co, smooth_co)
        else:
            smooth_co = np.copy(self.o_co)

        if move_perp_normal_comp is not None:
            # we store pull_co (pre vert offset) for all sel_v, thus pull_mask also has to have same shape as pull_co
            self.pull_mask.fill(0)  # zero out, next fill with only affected verts
            np.put(self.pull_mask, tuple(vpull_mask.keys()), tuple(vpull_mask.values()))
            self.pull_co = move_perp_normal_comp * self.pull_mask[:, None] + self.pull_co
            if self.freeze_border:
                self.pull_co[self.freeze_verts] = 0  # do not move theese
            smooth_co += self.pull_co
        # print(f"{stroke_mask=}")
        # print(f"{self.sorig_to_new_id=}")
        # print(f"{[(i,m) for i,m in enumerate(self.mirror_map)]}")
        if context.object.data.use_mirror_x:
            # brush_mask = np.array([stroke_mask[v.index] for v in self.sel_v])  # zero out masked verts
            np_x_axis = np.array([-1, 1, 1], "f")
            for i, v in enumerate(self.sel_v):  # smooth_co etc. are not using original v.indices
                mirror_vert_idx = self.mirror_map[
                    v.index
                ]  # uses original  v.index since mirror_mas is using all mesh verts
                if mirror_vert_idx in (-1, -2):  # on axis (sym_vert_id == current_v_id), or no symmterical vert
                    # print(f'set vert {i}({v.index}) ')
                    v.co = smooth_co[i]
                else:
                    new_mid = self.sorig_to_new_id.get(
                        mirror_vert_idx
                    )  # conver mirror_id from original v.index to sel_v idx
                    if new_mid is None:  # when symmetry, but one side is not selected
                        v.co = smooth_co[i]  # then in means just write to original vert.
                        self.bm.verts[mirror_vert_idx].co = smooth_co[i] * np_x_axis
                        continue  # to next loop

                    if new_mid in stroke_mask:  # mirrored vert is in brush_vert_mask?
                        if stroke_mask[i] > stroke_mask[new_mid]:
                            # print(f'Mirror from {i}({v.index}) to {new_mid}({mirror_vert_idx})')
                            v.co = smooth_co[i]
                            m_co = smooth_co[i] * np_x_axis
                            self.bm.verts[mirror_vert_idx].co = m_co
                            stroke_mask[new_mid] = stroke_mask[i]  # copy ifluence
                            self.vsmooth_mask[new_mid] = self.vsmooth_mask[i]  # copy ifluence
                            self.pull_co[new_mid] = self.pull_co[i] * np_x_axis
                        else:  # current vert smooth_mask is lower than on mirrored side
                            pass  # it will be processed when we go to corresponding mirrored vert with bigger vsmooth_mask
                    else:  # no mirrored vert so just copy
                        # print(f'No mirror set vert {i}({v.index})')
                        v.co = smooth_co[i]
                        self.bm.verts[mirror_vert_idx].co = smooth_co[i]
                        self.bm.verts[mirror_vert_idx].co.x *= -1
        else:
            for i, v in enumerate(self.sel_v):
                v.co = smooth_co[i]
        self.step += 1
        if self.pull_co is not None and self.step % 10 == 0:
            self.bm.normal_update()
            self.o_normal = np.array(
                [v.normal for v in self.sel_v]
            )  # does not break smoooth_init since we used cached ver anyway.

    def adjust_size(self, context, event):
        region = context.region
        rv3d = context.region_data
        curr_loc3d_from_2d = view3d_utils.region_2d_to_location_3d(
            region, rv3d, (event.mouse_region_x, 0), self.hit_world
        )
        start_loc3d_from_2d = view3d_utils.region_2d_to_location_3d(
            region, rv3d, (self.f_start_xloc, 0), self.hit_world
        )
        diff = (curr_loc3d_from_2d - start_loc3d_from_2d).length
        if self.f_start_xloc > event.mouse_region_x:
            diff *= -1
        tool = context.workspace.tools.from_space_view3d_mode(context.mode)
        min_size = context.active_object.dimensions.length * 0.001
        mit_size_first_dec = round_to_first_digit(min_size)
        if self.resize:
            tool_props = tool.operator_properties("mesh.smooth_brush_vps")
            tool_props.radius = max(
                mit_size_first_dec, self.f_start_rad + diff
            )  # cos self.radius  is not updated when changes from workspace tool...vol
            self.radius = max(mit_size_first_dec, self.f_start_rad + diff)  # now mostly for UI drawing
        elif self.strengthen:
            tool_props = tool.operator_properties("mesh.smooth_brush_vps")
            tool_props.strength = max(
                0.01, self.f_start_strength + int(diff * 300)
            )  # cos self.radius  is not updated when changes from workspace tool...vol
            self.strength = tool_props.strength
            if self.strength >= 100:
                self.f_start_xloc = event.mouse_region_x
                self.f_start_strength = 100
            elif self.strength <= 0.01:
                self.f_start_xloc = event.mouse_region_x
                self.f_start_strength = 0
            #     # self.f_start_strength = 0

    def get_hit(self, context, event):
        mouse_2d_co = event.mouse_region_x, event.mouse_region_y
        mat = context.active_object.matrix_world
        self.hit_local, normal = raycast(context, mouse_2d_co)
        hover_over_mesh = self.hit_local is not None
        if self.hit_local:
            self.hit_world = mat @ self.hit_local
            if self.resize or self.strengthen:
                normal = get_view_vec(context)
        else:
            rv3d = context.region_data
            location_from_2d = view3d_utils.region_2d_to_location_3d(
                context.region, rv3d, mouse_2d_co, self.hit_world
            )  #  depth)
            self.hit_world = location_from_2d
            self.hit_local = mat.inverted() @ location_from_2d
            normal = get_view_vec(context)
        quat = normal.to_track_quat("Z", "Y")  # to_track_quat(track, up)
        rot_mat = quat.to_matrix().to_4x4()

        rad_scale_mat = Matrix.Scale(self.radius, 4)
        self.matrix_basis = Matrix.Translation(self.hit_world) @ rot_mat @ rad_scale_mat

    def finalize(self, context):
        self.resize = False
        self.strengthen = False
        context.scene.vps_gizmo_show = True
        wm = context.window_manager
        wm.gizmo_group_type_ensure("MESH_GGT_brush_circle")  # link back gizmo - brush outline
        bpy.types.SpaceView3D.draw_handler_remove(self._circel2d_handle, "WINDOW")
        if self._text2d_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._text2d_handle, "WINDOW")
        close_bmesh(context, self.bm, context.active_object.data)
        context.area.tag_redraw()

    def modal(self, context, event):
        if event.type == "MOUSEMOVE":
            self.prev_hit_loc = self.hit_local
            self.mouse_2d_co = event.mouse_region_x, event.mouse_region_y
            self.get_hit(context, event)  # sets new self.hit_loc
            if self.lmb:
                self.stored_pressure = event.pressure**2 if self.use_pressure else 1
                # self.numpy_smooth_init(context, method=self.method, from_brush = True, tension=self.tension) # inits self.bm, self.p_co etc. Too slow without chache
                if self.hit_local:
                    self.smooth_write(context)
                if context.object.mode == "EDIT":
                    bmesh.update_edit_mesh(context.active_object.data, loop_triangles=False, destructive=False)
                else:
                    self.bm.to_mesh(context.active_object.data)
                context.active_object.data.update()
            if self.resize or self.strengthen:
                self.adjust_size(context, event)
            context.area.tag_redraw()

        elif event.type == "LEFTMOUSE":
            # we could handle PRESS and RELEASE individually if necessary
            self.lmb = event.value == "PRESS"
            if event.value == "PRESS" and not (self.resize or self.strengthen):  # dealed in WorkTool keybindings
                context.scene.vps_gizmo_show = True
                pass

            if event.value == "RELEASE":
                self.finalize(context)
                return {"FINISHED"}

        elif event.type == "RIGHTMOUSE" and event.value == "PRESS":
            tool = context.workspace.tools.from_space_view3d_mode(context.mode)
            tool_props = tool.operator_properties("mesh.smooth_brush_vps")
            if self.strengthen:
                tool_props.strength = self.reset_strength
            if self.resize:
                tool_props.radius = self.reset_rad

            self.finalize(context)
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "MESH"

    def invoke(self, context, event):
        active_obj = context.active_object
        context.scene.vps_gizmo_show = False

        self.prev_hit_loc = None  # raycast on object loc
        self.hit_local = None  # raycast on object loc

        self.lmb = self.draw

        if self.resize or self.strengthen:  # f - start as brush resize oper
            self.mouse_2d_co = event.mouse_region_x, event.mouse_region_y
            self.f_start_xloc = event.mouse_region_x
            self.f_start_rad = self.radius
            self.f_start_strength = self.strength
            self.reset_rad = self.radius
            self.reset_strength = self.strength

        if active_obj.type == "MESH":
            # self.snap_surface_BVHT = get_obj_mesh_bvht(active_obj, context.evaluated_depsgraph_get() , with_mods=False, world_space=False)
            pass
        else:
            self.report({"ERROR"}, "Select proper mesh object for particle hair drawing. Cancelling")
            return {"CANCELLED"}

        # NOTE: mostly to init  vps smooth operator
        self.smooth_amount = 1
        self.Inflate = 1
        self.normal_smooth = 0.5
        self.iteration_amount = 5 if self.strength > 0 else 0  # hack to skip processing smooth, but init props
        self.sharp_edge_weight = 1
        self.alpha = 0.5

        ret = self.numpy_smooth_init(
            context, method=self.method, from_brush=True, tension=self.tension
        )  # sets self.bm and self.p_co
        if ret == "CANCELLED":
            return {"CANCELLED"}

        vert_n = len(self.sel_v)
        self.sel_v_len = vert_n
        self.vsmooth_mask = {i: 0 for i in range(vert_n)}
        self.pull_mask = np.zeros(vert_n, "f")
        self.pull_co = np.zeros(vert_n * 3, "f").reshape(
            vert_n, 3
        )  # init target pull co from the start... too slow for continuous eveluation
        self.sorig_to_new_id = {
            v.index: i for i, v in enumerate(self.sel_v)
        }  # self.orig_to_new_idx - wont work since in there we have sel_V + adj_verts

        # for grabbing verts inside radius r, we need kdtree
        self.kd = kdtree.KDTree(vert_n)
        for i, v in enumerate(self.sel_v):
            self.kd.insert(v.co, i)
        self.kd.balance()

        # init kd for symmetry handling
        if context.object.data.use_mirror_x:
            self.mirror_map = get_mirrored_verts(active_obj.data)

        normal = get_view_vec(context)
        view_local = active_obj.matrix_world.inverted() @ Vector(
            (normal.x, normal.y, normal.z, 0)
        )  # XXX: cos it is dir. check with blender build-in raycast
        self.view_local = view_local.to_3d()
        # screen_up = view_ma[1].xyz
        # screen_right = view_ma[1].xyz
        self.step = 0  # counter for normal udpate  every 1-th step
        self.hit_world = Vector((0, 0, 0))

        self.get_hit(context, event)  # init self.hit_loc, and self.ui_cursor_3d_co
        args = (self, (0.9, 0.9, 0.5, 1))
        self._circel2d_handle = bpy.types.SpaceView3D.draw_handler_add(draw_circle_px, args, "WINDOW", "POST_VIEW")
        if self.strengthen:
            self._text2d_handle = bpy.types.SpaceView3D.draw_handler_add(draw_text_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
