import bmesh
import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty
from mathutils import Matrix, Vector

from .draw import *
from .loop import *
from .selection import *
from .tools import *
from .ui import *
from .utils import *


class PIE_ChangeWidth(bpy.types.Operator):
    bl_idname = "pie.mm_change_width"
    bl_label = "斜角 -> 改宽度"
    bl_description = "请选择倒斜角的循环面，再执行本操作"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="宽度", default=0.0, step=0.1)  # type: ignore
    reverse: BoolProperty(name="反转", default=False)  # type: ignore
    taper: BoolProperty(name="Taper", default=False)  # type: ignore
    taperflip: BoolProperty(name="Taper Flip", default=False)  # type: ignore
    single: BoolProperty(name="Single", default=False)  # type: ignore
    cyclic: BoolProperty(name="Cyclic", default=False)  # type: ignore
    passthrough: BoolProperty(default=False)  # type: ignore

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "width")

        if self.single:
            column.prop(self, "reverse")

        if not self.cyclic:
            row = column.row()
            row.prop(self, "taper")
            row.prop(self, "taperflip")

    def draw_HUD(self, context):
        if context.area == self.area:
            draw_init(self)

            draw_title(self, self.bl_label)

            draw_prop(self, "宽度", self.width, decimal=3, hint="左右移动")

            if self.single:
                draw_prop(self, "反转", self.reverse, offset=18, hint="R 切换")

            if not self.cyclic:
                draw_prop(self, "Taper", self.taper, offset=18, hint="T 切换")

                if self.taper:
                    draw_prop(self, "Taper Flip", self.taperflip, offset=18, hint="F 切换")

    def draw_VIEW3D(self, context):
        # if context.scene.MM.debug:
        # if context.area == self.area:
        #     if self.loops:
        #         draw_lines(self.loops, mx=self.active.matrix_world, color=(0.4, 0.8, 1))
        return None

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return len([f for f in bm.faces if f.select]) >= 1

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "MOUSEMOVE":
            wrap_cursor(self, context, event)
            update_HUD_location(self, event)

        if event.type in ["MOUSEMOVE", "R", "T", "F"]:

            if event.type == "MOUSEMOVE":
                if self.passthrough:
                    self.passthrough = False

                else:
                    divisor = 100 if event.shift else 1 if event.ctrl else 10

                    delta_x = event.mouse_x - self.last_mouse_x
                    delta_width = delta_x / divisor * self.factor

                    self.width += delta_width

            elif event.type == "R" and event.value == "PRESS":
                self.reverse = not self.reverse

            elif event.type == "T" and event.value == "PRESS":
                if not self.cyclic:
                    self.taper = not self.taper

            elif event.type == "F" and event.value == "PRESS":
                if not self.cyclic:
                    self.taperflip = not self.taperflip

            try:
                ret = self.main(self.active, modal=True)

                if ret is False:
                    self.finish()
                    return {"FINISHED"}
            except Exception as e:
                self.finish()

                if context.mode == "OBJECT":
                    bpy.ops.object.mode_set(mode="EDIT")

                output_traceback(self, e)
                return {"FINISHED"}

        elif (
            event.type in {"MIDDLEMOUSE"}
            or (event.alt and event.type in {"LEFTMOUSE", "RIGHTMOUSE"})
            or event.type.startswith("NDOF")
        ):
            self.passthrough = True
            return {"PASS_THROUGH"}

        elif event.type in ["LEFTMOUSE", "SPACE"]:
            self.finish()
            return {"FINISHED"}

        elif event.type in {"RIGHTMOUSE", "ESC"}:
            self.finish()

            bpy.ops.object.mode_set(mode="OBJECT")
            self.initbm.to_mesh(self.active.data)
            bpy.ops.object.mode_set(mode="EDIT")

            return {"CANCELLED"}

        self.last_mouse_x = event.mouse_x
        self.last_mouse_y = event.mouse_y

        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, "WINDOW")

        finish_status(self)

    def invoke(self, context, event):
        self.active = context.active_object

        self.active.update_from_editmode()

        self.width = 0
        self.reverse = False
        self.loops = []

        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        self.factor = get_zoom_factor(
            context, self.active.matrix_world @ average_locations([v.co for v in self.initbm.verts if v.select])
        )

        init_cursor(self, event)

        init_status(self, context, "Change Width")

        self.area = context.area
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context,), "WINDOW", "POST_PIXEL")
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (context,), "WINDOW", "POST_VIEW")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        active = context.active_object

        try:
            self.main(active)
        except Exception as e:
            output_traceback(self, e)

        return {"FINISHED"}

    def main(self, active, modal=False):
        debug = True
        debug = False

        bpy.ops.object.mode_set(mode="OBJECT")

        if modal:
            self.initbm.to_mesh(active.data)

        bm = bmesh.new()
        bm.from_mesh(active.data)

        bm.normal_update()
        bm.verts.ensure_lookup_table()

        bw = ensure_custom_data_layers(bm)[1]

        mg = build_mesh_graph(bm, debug=debug)
        verts = [v for v in bm.verts if v.select]
        faces = [f for f in bm.faces if f.select]

        if len(faces) == 1:
            self.single = True
        else:
            self.single = False

        ret = get_2_rails_from_chamfer(bm, mg, verts, faces, self.reverse, debug=debug)

        if ret:
            rails, self.cyclic = ret

            if not self.cyclic:
                if self.taper and self.taperflip:
                    r1, r2 = rails

                    r1.reverse()
                    r2.reverse()

                    rails = (r1, r2)

            sweeps = init_sweeps(bm, active, rails, debug=debug)

            get_loops(bm, bw, faces, sweeps, debug=debug)

            # if bpy.context.scene.MM.debug:
            # debug_draw_sweeps(self, sweeps, draw_loops=True)

            changed_width = change_width(bm, sweeps, self.width, taper=self.taper, debug=debug)

            if changed_width:
                bm.to_mesh(active.data)
            else:
                popup_message("Something went wrong, likely not a valid chamfer selection.", title="Chamfer Width")

        bpy.ops.object.mode_set(mode="EDIT")

        if ret:
            if changed_width:
                return True

        return False
