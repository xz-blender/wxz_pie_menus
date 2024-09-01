from math import sqrt
from typing import Set, Tuple, Union

import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
from mathutils import Vector
from mathutils.geometry import intersect_line_line, intersect_point_line

from ...utils import get_prefs
from .draw import draw_init, draw_label, draw_line, draw_lines, draw_point, draw_tris, draw_vector
from .items import *
from .math import average_locations, average_normals, dynamic_format, get_center_between_verts
from .raycast import cast_bvh_ray_from_point
from .selection import get_boundary_edges, get_edges_vert_sequences, get_selected_vert_sequences, get_selection_islands
from .snap import Snap
from .system import printd
from .ui import finish_status, force_ui_update, get_mouse_pos, ignore_events, init_status, navigation_passthrough
from .utils import *


def draw_punchit_status(op):
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)

        text = "Punch It"
        row.label(text=text)

        if not op.finalizing:
            if op.is_numeric_input:
                row.label(text="", icon="EVENT_RETURN")
                row.label(text="Finalize")

                row.label(text="", icon="MOUSE_MMB_DRAG")
                row.label(text="Navigation")

                row.label(text="", icon="EVENT_ESC")
                row.label(text="Cancel")

                row.label(text="", icon="EVENT_TAB")
                row.label(text="Abort Numeric Input")

                row.separator(factor=10)

                row.label(text="Numeric Input...")

            else:

                row.label(text="", icon="MOUSE_LMB")
                row.label(text="Finalize")

                row.label(text="", icon="MOUSE_MMB_DRAG")
                row.label(text="Navigation")

                row.label(text="", icon="MOUSE_RMB")
                row.label(text="Cancel")

                row.label(text="", icon="EVENT_TAB")
                row.label(text="Enter Numeric Input")

                row.separator(factor=10)

                row.label(text="", icon="MOUSE_MOVE")
                row.label(text="Set Amount")

                row.separator(factor=2)

                row.label(text=f"Extrusion Mode:")

                row.separator(factor=1)

                row.label(text="", icon="EVENT_A")
                row.label(text=f"Averaged")

                row.separator(factor=1)

                row.label(text="", icon="EVENT_E")
                row.label(text=f"Edge")

                row.separator(factor=1)

                row.label(text="", icon="EVENT_N")
                row.label(text=f"Normal")

                row.separator(factor=2)

                row.label(text="", icon="EVENT_R")
                row.label(text="Reset Amount")

        else:
            row.label(text="", icon="MOUSE_LMB")
            row.label(text="Finish")

            row.label(text="", icon="MOUSE_MMB_DRAG")
            row.label(text="Navigation")

            row.label(text="", icon="MOUSE_RMB")
            row.label(text="Go Back")

            row.separator(factor=10)
            row.label(text="", icon="EVENT_S")
            row.label(text=f"Self-Boolean: {op.self_boolean}")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_A")
            row.label(text=f"Auto Mesh Cleanup: {op.auto_cleanup}")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_W")
            row.label(text=f"Push and Pull")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_Q")
            row.label(text=f"Just Pull")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_E")
            row.label(text=f"Just Push")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_R")
            row.label(text=f"Reset Push/Pull")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_SHIFT")
            row.label(text=f"Invert Push/Pull")

            row.separator(factor=2)

            row.label(text="", icon="EVENT_CTRL")
            row.label(text=f"Push/Pull x 100")

    return draw


class PunchIt(bpy.types.Operator):
    bl_idname = "pie.punchit"
    bl_label = "Punch It"
    bl_description = "Manifold Extruding that works"
    bl_options = {"REGISTER", "UNDO"}

    self_boolean: BoolProperty(
        name="使用自相交",
        description="神奇地修复问题(较慢)\n如果禁用，您通常需要更大的推拉值(更快)",
        default=True,
    )  # type: ignore
    mode: EnumProperty(name="Mode", items=extrude_mode_items, default="AVERAGED")  # type: ignore

    amount: FloatProperty(name="Amount", description="Extrusion Depth", default=0.4, min=0, precision=4, step=0.1)  # type: ignore

    is_numeric_input: BoolProperty()  # type: ignore
    is_numeric_input_marked: BoolProperty()  # type: ignore
    numeric_input_amount: StringProperty(
        name="Numeric Amount to Move Face", description="Amount to Move the Face Selection by", default="0"
    )  # type: ignore

    pushed: IntProperty(name="Pushed", description="Push Side Faces out", default=0)  # type: ignore
    pulled: IntProperty(name="Pulled", description="Pull Front Face back", default=0)  # type: ignore

    auto_cleanup: BoolProperty(
        name="Auto-Cleanup", description="Run an automatic mesh cleanup at the end", default=True
    )  # type: ignore

    passthrough = False

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)

        row = column.row(align=True)
        row.label(text="Mode")
        row.prop(self, "mode", expand=True)
        row.prop(self, "use_self", text="", icon="SHADERFX", toggle=True)

        row = column.split(factor=0.5, align=True)
        row.prop(self, "amount", expand=True)

        r = row.row(align=True)
        r.prop(self, "pushed", text="Push", expand=True)
        r.prop(self, "pulled", text="Pull", expand=True)

    def draw_HUD(self, context):
        if context.area == self.area:

            draw_init(self)

            if self.finalizing:
                dims = draw_label(
                    context,
                    title=f"Finalizing ",
                    coords=Vector((self.HUD_x, self.HUD_y)),
                    center=False,
                    color=white,
                    alpha=1,
                )

                if self.self_boolean:
                    draw_label(
                        context,
                        title="self-boolean",
                        coords=Vector((self.HUD_x + dims[0], self.HUD_y)),
                        center=False,
                        color=white,
                        alpha=0.5,
                    )

                self.offset += 18
                dims = draw_label(
                    context,
                    title=f"Pushed: {self.pushed}  ",
                    coords=Vector((self.HUD_x, self.HUD_y)),
                    offset=self.offset,
                    center=False,
                    color=blue,
                    alpha=0.75,
                )
                draw_label(
                    context,
                    title=f"Pulled: {self.pulled}",
                    coords=Vector((self.HUD_x + dims[0], self.HUD_y)),
                    offset=self.offset,
                    center=False,
                    color=green,
                    alpha=0.75,
                )

                if self.auto_cleanup:
                    self.offset += 18
                    dims = draw_label(
                        context,
                        title=f"Auto-Cleanup ",
                        coords=Vector((self.HUD_x, self.HUD_y)),
                        offset=self.offset,
                        center=False,
                        color=red,
                        alpha=1,
                    )

                    if self.cleaned_up:
                        draw_label(
                            context,
                            title=f"{self.cleaned_up} Verts Removed ✔️",
                            coords=Vector((self.HUD_x + dims[0], self.HUD_y)),
                            offset=self.offset,
                            center=False,
                            size=10,
                            color=white,
                            alpha=1,
                        )

                    else:
                        draw_label(
                            context,
                            title=f"Nothing",
                            coords=Vector((self.HUD_x + dims[0], self.HUD_y)),
                            offset=self.offset,
                            center=False,
                            size=10,
                            color=white,
                            alpha=0.5,
                        )

                elif self.is_mesh_non_manifold:
                    self.offset += 18
                    draw_label(
                        context,
                        title=f"Non-manifold meshes tend to require higher",
                        coords=Vector((self.HUD_x, self.HUD_y)),
                        offset=self.offset,
                        center=False,
                        color=orange,
                        alpha=1,
                    )

                    self.offset += 18
                    draw_label(
                        context,
                        title=f"values with Auto-Cleanup disabled",
                        coords=Vector((self.HUD_x, self.HUD_y)),
                        offset=self.offset,
                        center=False,
                        color=orange,
                        alpha=1,
                    )

            else:

                dims = draw_label(
                    context, title="Punch ", coords=Vector((self.HUD_x, self.HUD_y)), center=False, color=white, alpha=1
                )
                dims2 = draw_label(
                    context,
                    title="along ",
                    coords=Vector((self.HUD_x + dims[0], self.HUD_y)),
                    center=False,
                    size=10,
                    color=white,
                    alpha=0.5,
                )

                if self.mode == "EDGE":
                    draw_label(
                        context,
                        title="Edge",
                        coords=Vector((self.HUD_x + dims[0] + dims2[0], self.HUD_y)),
                        center=False,
                        color=yellow,
                        alpha=1,
                    )

                elif self.mode in ["AVERAGED", "NORMAL"]:
                    if self.mode == "AVERAGED":
                        dims3 = draw_label(
                            context,
                            title="Averaged ",
                            coords=Vector((self.HUD_x + dims[0] + dims2[0], self.HUD_y)),
                            center=False,
                            color=blue,
                            alpha=1,
                        )

                    else:
                        dims3 = draw_label(
                            context,
                            title="Individual ",
                            coords=Vector((self.HUD_x + dims[0] + dims2[0], self.HUD_y)),
                            center=False,
                            color=normal,
                            alpha=1,
                        )

                    draw_label(
                        context,
                        title="Normals",
                        coords=Vector((self.HUD_x + dims[0] + dims2[0] + dims3[0], self.HUD_y)),
                        center=False,
                        color=white,
                        alpha=0.5,
                    )

                self.offset += 18
                dims = draw_label(
                    context,
                    title="Amount:",
                    coords=Vector((self.HUD_x, self.HUD_y)),
                    offset=self.offset,
                    center=False,
                    color=white,
                    alpha=0.5,
                )

                title = "🖩" if self.is_numeric_input else " "
                dims2 = draw_label(
                    context,
                    title=title,
                    coords=Vector((self.HUD_x + dims[0], self.HUD_y)),
                    offset=self.offset + 3,
                    center=False,
                    size=20,
                    color=green,
                    alpha=0.5,
                )

                if self.is_numeric_input:
                    dims3 = draw_label(
                        context,
                        title=self.numeric_input_amount,
                        coords=Vector((self.HUD_x + dims[0] + dims2[0], self.HUD_y)),
                        offset=self.offset,
                        center=False,
                        color=green,
                        alpha=1,
                    )

                    if self.is_numeric_input_marked:
                        scale = context.preferences.system.ui_scale * get_prefs().modal_hud_scale
                        coords = [
                            Vector((self.HUD_x + dims[0] + dims2[0], self.HUD_y - (self.offset - 5) * scale, 0)),
                            Vector(
                                (self.HUD_x + dims[0] + dims2[0] + dims3[0], self.HUD_y - (self.offset - 5) * scale, 0)
                            ),
                        ]
                        draw_line(coords, width=12 + 8 * scale, color=green, alpha=0.1, screen=True)

                else:
                    draw_label(
                        context,
                        title=dynamic_format(self.amount, decimal_offset=1),
                        coords=Vector((self.HUD_x + dims[0] + dims2[0], self.HUD_y)),
                        offset=self.offset,
                        center=False,
                        color=white,
                        alpha=1,
                    )

                if self.pick_edge_dir:
                    self.offset += 18
                    edge_dir = self.data["edge_dir"]

                    if self.edge_coords and edge_dir:
                        draw_label(
                            context,
                            title="valid",
                            coords=Vector((self.HUD_x, self.HUD_y)),
                            offset=self.offset,
                            center=False,
                            color=yellow,
                            alpha=1,
                        )

                    elif self.edge_coords:
                        draw_label(
                            context,
                            title="invalid",
                            coords=Vector((self.HUD_x, self.HUD_y)),
                            offset=self.offset,
                            center=False,
                            color=red,
                            alpha=1,
                        )

                    else:
                        draw_label(
                            context,
                            title="none",
                            coords=Vector((self.HUD_x, self.HUD_y)),
                            offset=self.offset,
                            center=False,
                            color=red,
                            alpha=1,
                        )

    def draw_VIEW3D(self, context):
        if context.area == self.area:
            data = self.data
            orig_verts = data["original_verts"]
            extr_verts = data["extruded_verts"]

            if self.finalizing:
                tri_coords = [orig_verts[idx]["co"] for idx in data["original_tri_indices"]]
                draw_tris(tri_coords, mx=self.mx, color=green, alpha=0.05, xray=False)

                tri_coords = [(orig_verts | extr_verts)[idx]["co"] for idx in data["side_tri_indices"]]
                draw_tris(tri_coords, mx=self.mx, color=blue, alpha=0.05, xray=False)

                coords = [orig_verts[vidx]["co"] for vidx in data["sorted_boundary"]]
                draw_line(coords, indices=data["sorted_boundary_indices"], mx=self.mx, color=white, alpha=0.05)

                coords = [extr_verts[data["vert_map"][vidx]]["co"] for vidx in data["sorted_boundary"]]
                draw_line(coords, indices=data["sorted_boundary_indices"], mx=self.mx, color=white, alpha=0.05)

                coords = [
                    (orig_verts | extr_verts)[idx]["co"]
                    for vidx in data["sorted_boundary"]
                    for idx in [vidx, data["vert_map"][vidx]]
                ]
                draw_lines(coords, mx=self.mx, color=white, alpha=0.05)

            else:
                data = self.data
                orig_verts = data["original_verts"]
                extr_verts = data["extruded_verts"]

                avg_co = self.mx @ data["avg_co"]
                edge_dir = data["edge_dir"]

                draw_point(avg_co, color=red if self.amount == 0 else white)

                if self.amount:
                    extr_dir = self.loc - self.init_loc
                    draw_vector(extr_dir, origin=avg_co, fade=True, alpha=0.5)
                    draw_point(avg_co + extr_dir, size=4, alpha=0.5)

                    tri_coords = [
                        (orig_verts | extr_verts)[idx]["co"]
                        for idx in data["original_tri_indices"]
                        + data["extruded_tri_indices"]
                        + data["side_tri_indices"]
                    ]
                    draw_tris(tri_coords, mx=self.mx, color=green, alpha=0.1)

                    coords = [extr_verts[data["vert_map"][vidx]]["co"] for vidx in data["sorted_boundary"]]
                    draw_line(coords, indices=data["sorted_boundary_indices"], mx=self.mx, color=green, alpha=0.2)

                    color, alpha = (
                        (yellow, 0.5) if self.mode == "EDGE" else (blue, 1) if self.mode == "AVERAGED" else (normal, 1)
                    )
                    coords = [
                        (orig_verts | extr_verts)[idx]["co"]
                        for vidx in data["sorted_boundary"]
                        for idx in [vidx, data["vert_map"][vidx]]
                    ]
                    draw_lines(coords, mx=self.mx, color=color, alpha=alpha)

                if self.pick_edge_dir and self.edge_coords:
                    color = yellow if self.edge_coords and edge_dir else red
                    draw_line(self.edge_coords, color=color, width=2, alpha=0.99)

                exit_coords = [
                    orig_verts[vidx]["exit_co"] for vidx in data["sorted_boundary"] if orig_verts[vidx]["exit_co"]
                ]

                if exit_coords:
                    exit_coords.append(exit_coords[0])
                    draw_line(exit_coords, mx=self.mx, alpha=0.1)

    def modal(self, context, event):
        if ignore_events(event):
            return {"RUNNING_MODAL"}

        context.area.tag_redraw()

        if ret := self.numeric_input(context, event):
            return ret

        else:
            return self.interactive_input(context, event)

    def finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, "WINDOW")

        finish_status(self)

        self.S.finish()

    def invoke(self, context, event):
        debug = False

        self.active = context.active_object
        self.active.update_from_editmode()

        self.mx = self.active.matrix_world
        self.is_mesh_non_manifold = False

        self.init_bm = bmesh.new()
        self.init_bm.from_mesh(self.active.data)
        self.init_bm.normal_update()

        self.bm = bmesh.from_edit_mesh(self.active.data)
        self.bm.normal_update()

        self.cache = None

        selection = self.get_selection(context, self.bm, debug=debug)

        if selection:

            self.data = self.get_data(*selection)

            self.get_exit_coords()

            self.get_extruded_data()

            self.get_side_data()

            if not context.region_data:
                return self.execute(context)

            get_mouse_pos(self, context, event)

            self.amount = 0
            self.setup_extrusion_direction(context, "AVERAGED")

            if self.init_loc:

                self.pushed = get_prefs().push_default
                self.pulled = get_prefs().pull_default
                self.finalizing = False
                self.cleaned_up = 0

                self.pick_edge_dir = False
                self.edge_coords = None

                self.prev_mode = "AVERAGED"

                self.is_numeric_input = False
                self.is_numeric_input_marked = False
                self.numeric_input_amount = "0"

                self.S = Snap(context, debug=False)

                init_status(self, context, func=draw_punchit_status(self))

                force_ui_update(context)

                self.area = context.area
                self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context,), "WINDOW", "POST_PIXEL")
                self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(
                    self.draw_VIEW3D, (context,), "WINDOW", "POST_VIEW"
                )

                context.window_manager.modal_handler_add(self)
                return {"RUNNING_MODAL"}

        return {"CANCELLED"}

    def execute(self, context):
        if self.amount:
            if self.mode == "EDGE" and not self.data["edge_dir"]:
                self.mode = "AVERAGED"  # avoid EDGE mode when an edge dir was never set

            self.active = context.active_object

            self.bm = bmesh.from_edit_mesh(self.active.data)
            self.bm.normal_update()

            self.set_extrusion_amount(context, interactive=False)

            self.set_push_and_pull_amount(context)

            self.create_extruded_geo(self.active, self.bm)

            bpy.ops.mesh.intersect_boolean(operation="DIFFERENCE", use_self=self.self_boolean, solver="EXACT")

        return {"FINISHED"}

    def get_mouse_intersection(self, context):
        view_origin = region_2d_to_origin_3d(context.region, context.region_data, self.mouse_pos)
        view_dir = region_2d_to_vector_3d(context.region, context.region_data, self.mouse_pos)

        i = intersect_line_line(
            self.amount_origin, self.amount_origin + self.amount_dir, view_origin, view_origin + view_dir
        )

        if i:
            return i[0]

    def get_edge_dir(self, context):
        self.S.get_hit(self.mouse_pos)

        if self.mode != "EDGE":
            self.prev_mode = self.mode

        if self.S.hit:
            hitmx = self.S.hitmx
            hit_co = hitmx.inverted_safe() @ self.S.hitlocation
            hitface = self.S.hitface

            edge = min(
                [
                    (
                        e,
                        (hit_co - intersect_point_line(hit_co, e.verts[0].co, e.verts[1].co)[0]).length,
                        (hit_co - get_center_between_verts(*e.verts)).length,
                    )
                    for e in hitface.edges
                    if e.calc_length()
                ],
                key=lambda x: (x[1] * x[2]) / x[0].calc_length(),
            )
            edge_dir = (edge[0].verts[1].co - edge[0].verts[0].co).normalized()

            self.edge_coords = [hitmx @ v.co for v in edge[0].verts]

            closest_point_on_edge = intersect_point_line(hit_co, edge[0].verts[0].co, edge[0].verts[1].co)[0]

            if self.S.hitobj != self.active:
                edge_dir = self.mx.inverted_safe().to_3x3() @ hitmx.to_3x3() @ edge_dir
                closest_point_on_edge = self.mx.inverted_safe() @ hitmx @ closest_point_on_edge

            dot = edge_dir.dot(self.data["avg_dir"])

            if dot < 0:
                edge_dir.negate()

            if round(dot, 4) == 0:

                self.data["edge_dir"] = None

            elif round(dot, 4) != 0:
                self.data["edge_co"] = closest_point_on_edge
                self.data["edge_dir"] = edge_dir

                self.setup_extrusion_direction(context, direction="EDGE")
                self.set_extrusion_amount(context)
                return

        else:
            self.edge_coords = None
            self.data["edge_dir"] = None

        self.mode = self.prev_mode

        self.setup_extrusion_direction(context, direction=self.mode)
        self.set_extrusion_amount(context)

    def setup_extrusion_direction(self, context, direction="AVERAGED"):

        self.mode = direction

        if direction in ["AVERAGED", "NORMAL"]:

            self.amount_origin = self.mx @ self.data["avg_co"]
            self.amount_dir = self.mx.to_3x3() @ self.data["avg_dir"]

        elif direction == "EDGE":

            self.amount_origin = self.mx @ self.data["edge_co"]
            self.amount_dir = self.mx.to_3x3() @ self.data["edge_dir"]

        i = self.get_mouse_intersection(context)

        self.init_loc = i - self.amount_dir * self.amount
        self.loc = i

        self.get_exit_coords(direction=direction)

    def set_extrusion_amount(self, context, interactive=True):

        if interactive:
            amount_vector = self.loc - self.init_loc
            self.amount = amount_vector.length if amount_vector.dot(self.amount_dir) > 0 else 0

        if self.amount:
            for vdata in self.data["extruded_verts"].values():

                if self.mode == "AVERAGED":
                    vdata["co"] = vdata["init_co"] + self.data["avg_dir"] * self.amount
                elif self.mode == "EDGE":
                    vdata["co"] = vdata["init_co"] + self.data["edge_dir"] * self.amount
                elif self.mode == "NORMAL":
                    vdata["co"] = vdata["init_co"] + vdata["vert_dir"] * self.amount

        else:
            self.init_loc = self.get_mouse_intersection(context)
            self.loc = self.init_loc

    def set_push_and_pull_amount(self, context):

        data = self.data
        mode = self.mode

        orig_verts = data["original_verts"]
        extr_verts = data["extruded_verts"]

        push_pull_scale = sqrt(data["area"]) * 0.00001

        for vidx, vdata in (orig_verts | extr_verts).items():
            co = vdata["init_co"].copy()

            extr_dir = self.amount * (
                data["avg_dir"] if mode == "AVERAGED" else data["edge_dir"] if mode == "EDGE" else vdata["vert_dir"]
            )

            if vidx in extr_verts:
                co += extr_dir

            if vdata["push_dir"] and self.pushed:
                co += vdata["push_dir"] * push_pull_scale * self.pushed

            if vidx in orig_verts and self.pulled:
                co -= extr_dir.normalized() * push_pull_scale * self.pulled

            vdata["co"] = co

    def reset_mesh(self, init_bm, return_bmesh=False):

        bpy.ops.object.mode_set(mode="OBJECT")
        init_bm.to_mesh(self.active.data)
        bpy.ops.object.mode_set(mode="EDIT")

        if return_bmesh:
            bm = bmesh.from_edit_mesh(self.active.data)
            bm.normal_update()

            return bm

    def get_selection(self, context, bm, debug=False):

        coords = (context.region.width / 2, 200)
        self.is_mesh_non_manifold = not all(e.is_manifold for e in bm.edges)

        if self.is_mesh_non_manifold and not get_prefs().non_manifold_extrude:
            bpy.ops.machin3.draw_punchit_labels(
                text="Mesh is non-manifold!",
                text2="Try enabling non-manifold mesh support in the addon preferences",
                coords=coords,
                color=red,
                color2=yellow,
                color3=white,
                alpha=1,
                alpha2=0.8,
                time=3,
            )
            return

        faces = [f for f in bm.faces if f.select]

        if not faces and (
            tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False)
            or tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False)
        ):
            verts = [v for v in bm.verts if v.select]

            if verts:
                vert_mode = False

                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
                    vert_mode = True
                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")

                sequences = get_selected_vert_sequences(verts, ensure_seq_len=True, debug=False)

                if len(sequences):
                    seq, cyclic = max(sequences, key=lambda x: len(x[0]))

                    if len(sequences) > 1:
                        for s, c in sequences:
                            if s != seq:
                                for idx, v in enumerate(s):
                                    if idx != len(s) - 1:
                                        nextv = s[idx + 1]
                                        e = bm.edges.get([v, nextv])
                                        e.select_set(False)

                    if not cyclic:
                        path = get_shortest_path(bm, seq[0], seq[-1], topo=False, ignore_selected=True, select=True)

                        for idx, v in enumerate(path):
                            if idx != len(path) - 1:
                                nextv = path[idx + 1]
                                e = bm.edges.get([v, nextv])
                                e.select_set(True)

                    bpy.ops.mesh.loop_to_region()
                    faces = [f for f in bm.faces if f.select]

                    if vert_mode:
                        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")

                else:
                    if vert_mode:
                        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")

                    bpy.ops.machin3.draw_punchit_labels(
                        text="Illegal Selection!",
                        text2="You need to select at least one edge",
                        coords=coords,
                        color=red,
                        color2=yellow,
                        alpha=1,
                        alpha2=0.5,
                        time=3,
                    )
                    return

            else:
                bpy.ops.machin3.draw_punchit_labels(
                    text="Illegal Selection!",
                    text2="Make a Selection, will ya...",
                    coords=coords,
                    color=red,
                    color2=yellow,
                    alpha=1,
                    alpha2=0.5,
                    time=3,
                )
                return

        islands = get_selection_islands(faces, debug=debug)

        if not islands:
            bpy.ops.machin3.draw_punchit_labels(
                text="Pay attention, numbnuts!",
                text2="Uh, try to select a face, maybe. Or an edge at least.",
                coords=coords,
                color=red,
                color2=yellow,
                alpha=1,
                alpha2=0.5,
                time=3,
            )
            return

        faces = max(islands, key=lambda x: len(x[2]))[2]

        if set(faces) == {f for f in bm.faces}:
            bpy.ops.machin3.draw_punchit_labels(
                text="Illegal Selection!",
                text2="Let's think this through. You want to select all the faces? At the same time?",
                coords=coords,
                color=red,
                color2=yellow,
                alpha=1,
                alpha2=0.5,
                time=3,
            )
            return

        loop_triangles = get_loop_triangles(bm, faces=faces)

        verts = {v for f in faces for v in f.verts}

        boundary = get_boundary_edges(faces)
        boundary_verts = list(set(v for e in boundary for v in e.verts))

        has_non_manifold_verts = any(any(not e.is_manifold for e in v.link_edges) for v in boundary_verts)

        if has_non_manifold_verts:
            bpy.ops.machin3.draw_punchit_labels(
                text="Selection is next to non-manifold edges!",
                text2="Fix your shit 💩",
                text3="No soup for you",
                coords=coords,
                color=red,
                color2=yellow,
                color3=white,
                alpha=1,
                alpha2=0.5,
                alpha3=0.5,
                time=3,
            )
            return

        inner_verts = [v for v in verts if v not in boundary_verts]

        sequences = get_edges_vert_sequences(boundary_verts, boundary, debug=debug)

        if len(sequences) > 1:
            bpy.ops.machin3.draw_punchit_labels(
                text="Illegal Selection!",
                text2="Face Selection can't be cyclic 🚴 ",
                coords=coords,
                color=red,
                color2=yellow,
                alpha=1,
                alpha2=0.5,
                time=3,
            )
            return

        sorted_boundary_verts = sequences[0][0]

        first_edge = bm.edges.get(sorted_boundary_verts[:2])

        for loop in first_edge.link_loops:
            if loop.face in faces:
                if loop.vert != sorted_boundary_verts[0]:
                    sorted_boundary_verts.reverse()

        smallest = min(sorted_boundary_verts, key=lambda x: x.index)

        if smallest != sorted_boundary_verts[0]:
            rotate_list(sorted_boundary_verts, sorted_boundary_verts.index(smallest))

        if debug:
            print()
            print("faces:", [f.index for f in faces])
            print("sorted boundary verts:", [v.index for v in sorted_boundary_verts])
            print("inner verts:", [v.index for v in inner_verts])

        return faces, loop_triangles, sorted_boundary_verts, inner_verts

    def get_data(self, faces, loop_triangles, sorted_boundary_verts, inner_verts):

        data = {
            "original_verts": {},
            "extruded_verts": {},
            "original_faces": {},
            "extruded_faces": {},
            "side_faces": {},
            "original_tri_indices": [],
            "extruded_tri_indices": [],
            "side_tri_indices": [],
            "sorted_boundary": [],
            "sorted_boundary_indices": [],
            "side_edges": {},
            "vert_map": {},
            "face_map": {},
            "avg_co": average_locations([f.calc_center_median() for f in faces]),
            "avg_dir": -average_normals([f.normal for f in faces]),
            "edge_co": None,
            "edge_dir": None,
            "area": 0,
        }

        seen = {}

        orig_verts = data["original_verts"]
        orig_faces = data["original_faces"]

        vidx = 0

        for fidx, f in enumerate(faces):
            fdata = []

            for v in f.verts:

                if v not in seen:

                    seen[v] = vidx

                    orig_verts[vidx] = {
                        "co": v.co.copy(),
                        "init_co": v.co.copy(),
                        "exit_co": None,
                        "vert_dir": -average_normals([f.normal for f in v.link_faces if f in faces]),
                        "push_dir": None,
                        "bound_idx": -1 if v in inner_verts else sorted_boundary_verts.index(v),
                    }

                    fdata.append(vidx)

                    vidx += 1

                else:
                    fdata.append(seen[v])

            orig_faces[fidx] = fdata

            data["area"] += f.calc_area()

        data["original_tri_indices"] = [seen[l.vert] for lt in loop_triangles for l in lt]

        sorted_boundary = [seen[v] for v in sorted_boundary_verts]
        data["sorted_boundary"] = sorted_boundary
        data["sorted_boundary_indices"] = [
            (idx, (idx + 1) % len(sorted_boundary)) for idx, _ in enumerate(sorted_boundary)
        ]

        for idx, vidx in enumerate(sorted_boundary):
            v_co = orig_verts[vidx]["co"]
            vert_dir = orig_verts[vidx]["vert_dir"]

            next_vidx = sorted_boundary[(idx + 1) % len(sorted_boundary)]
            prev_vidx = sorted_boundary[(idx - 1) % len(sorted_boundary)]

            fwd_co = v_co + (orig_verts[next_vidx]["co"] - v_co).normalized()
            bwd_co = v_co + (orig_verts[prev_vidx]["co"] - v_co).normalized()

            fwd_dir = (fwd_co - bwd_co).normalized()
            push_dir = vert_dir.cross(fwd_dir)

            data["original_verts"][vidx]["push_dir"] = push_dir

        return data

    def get_exit_coords(self, direction="AVERAGED"):

        self.cache = None
        offset = sqrt(self.data["area"]) * 0.00001

        if direction == "AVERAGED":
            direction = self.data["avg_dir"]

        elif direction == "EDGE":
            direction = self.data["edge_dir"]

        else:
            direction = None

        for idx in self.data["sorted_boundary"]:
            vdata = self.data["original_verts"][idx]
            ray_dir = direction if direction else vdata["vert_dir"]

            ray_origin = vdata["init_co"] - vdata["push_dir"] * offset + ray_dir * offset

            _, hitloc, _, _, _, self.cache = cast_bvh_ray_from_point(
                ray_origin, direction=ray_dir, cache=self.cache, candidates=[self.active], debug=False
            )

            if hitloc:
                vdata["exit_co"] = hitloc

    def get_extruded_data(self):

        data = self.data

        vert_len = len(data["original_verts"])
        face_len = len(data["original_faces"])

        for vidx, vdata in data["original_verts"].items():

            extr_vdata = vdata.copy()

            extr_vidx = vidx + vert_len

            data["extruded_verts"][extr_vidx] = extr_vdata

            data["vert_map"][vidx] = extr_vidx
            data["vert_map"][extr_vidx] = vidx

        for fidx, fdata in data["original_faces"].items():

            extr_fidx = fidx + face_len

            extr_fdata = [data["vert_map"][vidx] for vidx in fdata]

            data["extruded_faces"][extr_fidx] = extr_fdata

            data["face_map"][fidx] = extr_fidx
            data["face_map"][extr_fidx] = fidx

        data["extruded_tri_indices"] = [data["vert_map"][idx] for idx in data["original_tri_indices"]]

    def get_side_data(self):

        data = self.data

        sorted_boundary = data["sorted_boundary"]

        face_idx = len(data["original_faces"]) + len(data["extruded_faces"])

        for idx, vidx in enumerate(sorted_boundary):
            extr_vidx = data["vert_map"][vidx]

            next_vidx = sorted_boundary[(idx + 1) % len(sorted_boundary)]
            next_extr_vidx = data["vert_map"][next_vidx]

            data["side_faces"][face_idx] = [vidx, extr_vidx, next_extr_vidx, next_vidx]
            face_idx += 1

            data["side_tri_indices"].extend([vidx, extr_vidx, next_extr_vidx, vidx, next_extr_vidx, next_vidx])

    def debug_data(self, context, debug=False):
        data = self.data

        printd(data)

        sorted_boundary = data["sorted_boundary"]
        bound_len = len(sorted_boundary)

        avg_dir = data["avg_dir"]
        edge_dir = data["edge_dir"]

        draw_point(data["avg_co"], mx=self.mx, color=yellow, modal=False)

        if edge_dir:
            draw_vector(edge_dir * 0.5, origin=data["avg_co"], mx=self.mx, color=blue, modal=False)

        if data["original_verts"]:

            for v in data["original_verts"].values():
                co = v["co"]
                vert_dir = v["vert_dir"]
                push_dir = v["push_dir"]
                bidx = v["bound_idx"]

                draw_point(co, mx=self.mx, color=red if bidx == -1 else (0, bidx / (bound_len - 1), 0), modal=False)
                draw_vector(vert_dir * 0.3, origin=co + (vert_dir * 0.02), mx=self.mx, color=green, modal=False)
                draw_vector(avg_dir * 0.2, origin=co + (avg_dir * 0.02), mx=self.mx, color=yellow, modal=False)

                if edge_dir:
                    draw_vector(edge_dir * 0.1, origin=co + (edge_dir * 0.02), mx=self.mx, color=blue, modal=False)

                if push_dir:
                    draw_vector(push_dir * 0.1, origin=co + push_dir * 0.02, mx=self.mx, color=red, modal=False)

            coords = [data["original_verts"][idx]["co"] for idx in data["original_tri_indices"]]
            draw_tris(coords, mx=self.mx, color=green, alpha=0.1, modal=False)

            exit_coords = [
                data["original_verts"][vidx]["exit_co"]
                for vidx in data["sorted_boundary"]
                if data["original_verts"][vidx]["exit_co"]
            ]

            if exit_coords:
                exit_coords.append(exit_coords[0])
                draw_line(exit_coords, mx=self.mx, color=red, modal=False)

        if data["extruded_verts"]:

            coords = [data["extruded_verts"][data["vert_map"][vidx]]["co"] for vidx in data["sorted_boundary"]]
            draw_line(coords, indices=data["sorted_boundary_indices"], mx=self.mx, color=blue, modal=False)

            for v in data["extruded_verts"].values():
                co = v["co"]
                vert_dir = v["vert_dir"]
                push_dir = v["push_dir"]
                bidx = v["bound_idx"]

                draw_point(co, mx=self.mx, color=red if bidx == -1 else (0, 0, bidx / (bound_len - 1)), modal=False)
                draw_vector(vert_dir * 0.3, origin=co + (vert_dir * 0.02), mx=self.mx, color=green, modal=False)
                draw_vector(avg_dir * 0.2, origin=co + (avg_dir * 0.02), mx=self.mx, color=yellow, modal=False)

                if edge_dir:
                    draw_vector(edge_dir * 0.1, origin=co + (edge_dir * 0.02), mx=self.mx, color=blue, modal=False)

                if push_dir:
                    draw_vector(push_dir * 0.1, origin=co + push_dir * 0.02, mx=self.mx, color=red, modal=False)

            coords = [data["extruded_verts"][idx]["co"] for idx in data["extruded_tri_indices"]]
            draw_tris(coords, mx=self.mx, color=blue, alpha=0.1, modal=False)

        if data["side_faces"]:

            for idx, (fidx, fdata) in enumerate(data["side_faces"].items()):

                all_verts = data["original_verts"] | data["extruded_verts"]

                face_center = average_locations([all_verts[idx]["co"] for idx in fdata])

                gradient = idx / (len(data["side_faces"]) - 1)
                draw_point(face_center, mx=self.mx, color=(gradient, gradient, 0), size=10, modal=False)

            coords = [(data["original_verts"] | data["extruded_verts"])[idx]["co"] for idx in data["side_tri_indices"]]
            draw_tris(coords, mx=self.mx, color=yellow, alpha=0.1, modal=False)

        context.area.tag_redraw()

    def numeric_input(self, context, event) -> Union[Set[str], None]:

        if not self.finalizing:

            if event.type == "TAB" and event.value == "PRESS":
                self.is_numeric_input = not self.is_numeric_input

                force_ui_update(context)

                if self.is_numeric_input:
                    self.numeric_input_amount = str(self.amount)
                    self.is_numeric_input_marked = True

                else:
                    return

            if self.is_numeric_input:
                events = [*numbers, "BACK_SPACE", "DELETE", "PERIOD", "COMMA", "NUMPAD_PERIOD", "NUMPAD_COMMA"]

                if event.type in events and event.value == "PRESS":

                    if self.is_numeric_input_marked:
                        self.is_numeric_input_marked = False

                        if event.type == "BACK_SPACE":

                            if event.alt:
                                self.numeric_input_amount = self.numeric_input_amount[:-1]

                            else:
                                self.numeric_input_amount = shorten_float_string(self.numeric_input_amount, 4)

                        else:
                            self.numeric_input_amount = input_mappings[event.type]

                    else:
                        if event.type in numbers:
                            self.numeric_input_amount += input_mappings[event.type]

                        elif event.type == "BACK_SPACE":
                            self.numeric_input_amount = self.numeric_input_amount[:-1]

                        elif (
                            event.type in ["COMMA", "PERIOD", "NUMPAD_COMMA", "NUMPAD_PERIOD"]
                            and "." not in self.numeric_input_amount
                        ):
                            self.numeric_input_amount += "."

                    try:
                        self.amount = float(self.numeric_input_amount)

                    except:
                        return {"RUNNING_MODAL"}

                    self.set_extrusion_amount(context, interactive=False)

                elif navigation_passthrough(event, alt=True, wheel=True):
                    return {"PASS_THROUGH"}

                elif event.type in {"RET", "NUMPAD_ENTER"}:
                    self.set_push_and_pull_amount(context)

                    self.create_extruded_geo(self.active, self.bm)

                    bpy.ops.mesh.intersect_boolean(operation="DIFFERENCE", use_self=self.self_boolean, solver="EXACT")

                    if self.auto_cleanup:
                        self.cleanup()

                    self.active.update_from_editmode()

                    self.finalizing = True
                    return {"RUNNING_MODAL"}

                elif event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
                    self.finish(context)

                    return {"CANCELLED"}

                return {"RUNNING_MODAL"}

    def interactive_input(self, context, event) -> Set[str]:

        if event.type == "MOUSEMOVE":
            get_mouse_pos(self, context, event)

            if self.passthrough:
                self.passthrough = False

                i = self.get_mouse_intersection(context)
                self.init_loc = i - self.amount_dir * self.amount

        if not self.finalizing:
            events = ["MOUSEMOVE", "A", "E", *ctrl, "N", "X", "R"]

            if event.type in events:

                if event.type == "MOUSEMOVE":

                    if self.pick_edge_dir:
                        self.get_edge_dir(context)

                    else:
                        self.loc = self.get_mouse_intersection(context)
                        self.set_extrusion_amount(context)

                elif event.type in ["E", *ctrl]:
                    if event.value == "PRESS":
                        self.pick_edge_dir = True
                        self.get_edge_dir(context)

                    elif event.value == "RELEASE":
                        self.pick_edge_dir = False

                elif event.type == "A" and event.value == "PRESS":
                    self.setup_extrusion_direction(context, direction="AVERAGED")
                    self.set_extrusion_amount(context)

                elif event.type in ["X", "N"] and event.value == "PRESS":
                    self.setup_extrusion_direction(context, direction="NORMAL")
                    self.set_extrusion_amount(context)

                elif event.type == "R" and event.value == "PRESS":
                    self.init_loc = self.get_mouse_intersection(context)
                    self.set_extrusion_amount(context)

            elif navigation_passthrough(event, alt=True, wheel=True):
                self.passthrough = True
                return {"PASS_THROUGH"}

            if self.amount and event.type in {"LEFTMOUSE", "SPACE"} and event.value == "PRESS":

                self.set_push_and_pull_amount(context)

                self.create_extruded_geo(self.active, self.bm)

                bpy.ops.mesh.intersect_boolean(operation="DIFFERENCE", use_self=self.self_boolean, solver="EXACT")

                if self.auto_cleanup:
                    self.cleanup()

                self.active.update_from_editmode()

                self.finalizing = True
                return {"RUNNING_MODAL"}

            elif event.type in {"RIGHTMOUSE", "ESC"} and event.value == "PRESS":
                self.finish(context)

                return {"CANCELLED"}

        else:
            if event.type in ["Q", "W", "E", "R", "S", "A"] and event.value == "PRESS":
                bm = self.reset_mesh(self.init_bm, return_bmesh=True)

                factor = 100 if event.ctrl else 1

                if event.type == "W":
                    self.pushed += -factor if event.shift else factor
                    self.pulled += -factor if event.shift else factor

                elif event.type == "E":
                    self.pushed += -factor if event.shift else factor

                elif event.type == "Q":
                    self.pulled += -factor if event.shift else factor

                elif event.type == "R":
                    self.pushed = get_prefs().push_default
                    self.pulled = get_prefs().pull_default

                elif event.type == "S":
                    self.self_boolean = not self.self_boolean

                elif event.type in ["A", "C"]:
                    self.auto_cleanup = not self.auto_cleanup

                self.set_push_and_pull_amount(context)

                self.create_extruded_geo(self.active, bm)

                bpy.ops.mesh.intersect_boolean(operation="DIFFERENCE", use_self=self.self_boolean, solver="EXACT")

                if self.auto_cleanup:
                    self.cleanup()

                self.active.update_from_editmode()

                return {"RUNNING_MODAL"}

            elif navigation_passthrough(event, alt=True, wheel=True):
                return {"PASS_THROUGH"}

            elif event.type in {"LEFTMOUSE", "SPACE"} and event.value == "PRESS":
                self.finish(context)
                return {"FINISHED"}

            elif event.type in {"RIGHTMOUSE", "ESC"} and event.value == "PRESS":
                self.bm = self.reset_mesh(self.init_bm, return_bmesh=True)
                self.finalizing = False
                self.passthrough = True
                return {"RUNNING_MODAL"}

        return {"RUNNING_MODAL"}

    def create_extruded_geo(self, active, bm):

        data = self.data

        vert_map = {}
        face_map = {}
        faces = []

        for vidx, vdata in (data["original_verts"] | data["extruded_verts"]).items():
            v = bm.verts.new(vdata["co"])
            vert_map[vidx] = v

        for fidx, indices in (data["original_faces"] | data["extruded_faces"] | data["side_faces"]).items():
            verts = [vert_map[vidx] for vidx in indices]

            f = bm.faces.new(verts)
            face_map[fidx] = f
            faces.append(f)

        bmesh.ops.recalc_face_normals(bm, faces=faces)

        bpy.ops.mesh.select_all(action="DESELECT")

        for f in faces:
            f.select_set(True)

        bmesh.update_edit_mesh(active.data)

    def cleanup(self):

        bm = bmesh.from_edit_mesh(self.active.data)
        bm.normal_update()

        init_vert_count = len([v for v in bm.verts])

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.0001)

        loose_verts = [v for v in bm.verts if not v.link_edges]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context="VERTS")

        loose_edges = [e for e in bm.edges if not e.link_faces]
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context="EDGES")

        loose_faces = [f for f in bm.faces if all([not e.is_manifold for e in f.edges])]
        if loose_faces:
            bmesh.ops.delete(bm, geom=loose_faces, context="FACES")

        vert_count = len([v for v in bm.verts])

        bmesh.update_edit_mesh(self.active.data)

        self.cleaned_up = init_vert_count - vert_count
