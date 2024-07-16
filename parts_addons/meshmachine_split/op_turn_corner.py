import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty

from .draw import *
from .math import *
from .tools import *
from .ui import *
from .utils import *


class PIE_TurnCorner(bpy.types.Operator):
    bl_idname = "pie.mm_turn_corner"
    bl_label = "斜角 -> 旋转面方向"
    bl_description = "选择角的交汇处的四边面，执行本操作"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="宽度", default=0.1, min=0.01, step=0.1)  # type: ignore
    sharps: BoolProperty(name="标记锐边", default=False)  # type: ignore
    bweights: BoolProperty(name="设置边倒角权重", default=False)  # type: ignore
    bweight: FloatProperty(name="权重值", default=1, min=0, max=1)  # type: ignore
    passthrough: BoolProperty(default=False)  # type: ignore
    allowmodalwidth: BoolProperty(default=True)  # type: ignore

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "width")

        column.prop(self, "sharps")

        row = column.row()
        row.prop(self, "bweights")
        row.prop(self, "bweight")

    def draw_HUD(self, context):
        if context.area == self.area:
            draw_init(self)

            draw_title(self, self.bl_label)

            draw_prop(self, "拐角编号", self.count, hint="滚轮")
            self.offset += 10

            draw_prop(self, "宽度", self.width, active=self.allowmodalwidth, offset=18, hint="W 开关, 左右调整大小")

            self.offset += 10

            draw_prop(self, "标记-锐边", self.sharps, offset=18, hint="S 开关")
            draw_prop(self, "设置-边倒角权重", self.bweights, offset=18, hint="B 开关")

            if self.bweights:
                draw_prop(self, " | 权重值", self.bweight, offset=18, decimal=1, hint="ALT + 滚轮")

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            bm = bmesh.from_edit_mesh(context.active_object.data)
            faces = [f for f in bm.faces if f.select]
            verts = [v for v in bm.verts if v.select]

            if len(faces) == 1 and len(verts) == 4:
                v3s = [v for v in verts if len(v.link_edges) == 3]
                v4s = [v for v in verts if len(v.link_edges) == 4]
                return len(v3s) == len(v4s) == 2

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "MOUSEMOVE":
            wrap_cursor(self, context, event)
            update_HUD_location(self, event)

        events = ["WHEELUPMOUSE", "UP_ARROW", "ONE", "WHEELDOWNMOUSE", "DOWN_ARROW", "TWO", "S", "B"]

        if self.allowmodalwidth:
            events.append("MOUSEMOVE")

        if event.type in events:

            if event.type == "MOUSEMOVE":
                if self.passthrough:
                    self.passthrough = False

                else:
                    divisor = 100 if event.shift else 1 if event.ctrl else 10

                    delta_x = event.mouse_x - self.last_mouse_x
                    delta_width = delta_x / divisor * self.factor

                    self.width += delta_width

            elif event.type in {"WHEELUPMOUSE", "UP_ARROW", "ONE"} and event.value == "PRESS":
                if event.alt:
                    self.bweight += 0.1
                else:
                    self.count += 1
                    if self.count > 2:
                        self.count = 1

            elif event.type in {"WHEELDOWNMOUSE", "DOWN_ARROW", "TWO"} and event.value == "PRESS":
                if event.alt:
                    self.bweight -= 0.1
                else:
                    self.count -= 1
                    if self.count < 1:
                        self.count = 2

            elif event.type == "S" and event.value == "PRESS":
                self.sharps = not self.sharps

            elif event.type == "B" and event.value == "PRESS":
                self.bweights = not self.bweights

            try:
                ret = self.main(self.active, modal=True)

                if not ret:
                    self.finish()
                    return {"FINISHED"}

            except Exception as e:
                self.finish()

                output_traceback(self, e)
                return {"FINISHED"}

        elif event.type == "W" and event.value == "PRESS":
            self.allowmodalwidth = not self.allowmodalwidth

        elif (
            event.type in {"MIDDLEMOUSE"}
            or (event.alt and event.type in {"LEFTMOUSE", "RIGHTMOUSE"})
            or event.type.startswith("NDOF")
        ):
            self.passthrough = True
            return {"PASS_THROUGH"}

        elif event.type in {"LEFTMOUSE", "SPACE"}:
            self.finish()
            return {"FINISHED"}

        elif event.type in {"RIGHTMOUSE", "ESC"}:
            self.cancel_modal()
            return {"CANCELLED"}

        self.last_mouse_x = event.mouse_x
        self.last_mouse_y = event.mouse_y

        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, "WINDOW")

        finish_status(self)

    def cancel_modal(self):
        self.finish()

        bpy.ops.object.mode_set(mode="OBJECT")
        self.initbm.to_mesh(self.active.data)
        bpy.ops.object.mode_set(mode="EDIT")

    def invoke(self, context, event):
        self.active = context.active_object

        context.object.update_from_editmode()

        self.count = 1

        self.initbm = bmesh.new()
        self.initbm.from_mesh(context.object.data)

        self.factor = get_zoom_factor(
            context, self.active.matrix_world @ average_locations([v.co for v in self.initbm.verts if v.select])
        )

        init_cursor(self, event)

        if not self.allowmodalwidth:
            try:
                ret = self.main(self.active, modal=True)

                if not ret:
                    return {"FINISHED"}

            except Exception as e:
                output_traceback(self, e)
                return {"FINISHED"}

        init_status(self, context, "Turn Corner")

        self.area = context.area
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context,), "WINDOW", "POST_PIXEL")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        self.count = 1
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

        for i in range(self.count):
            bm = bmesh.new()
            bm.from_mesh(active.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            bw = ensure_custom_data_layers(bm)[1]

            verts = [v for v in bm.verts if v.select]
            faces = [f for f in bm.faces if f.select]

            new_edges = turn_corner(bm, verts, faces, self.width, debug=debug)

            if any([self.sharps, self.bweights]):
                if self.sharps:
                    bpy.context.space_data.overlay.show_edge_sharp = True
                if self.bweights:
                    bpy.context.space_data.overlay.show_edge_bevel_weight = True

                for e in new_edges:
                    if self.sharps:
                        e.smooth = False
                    if self.bweights:
                        e[bw] = self.bweight

            bm.to_mesh(active.data)

        bpy.ops.object.mode_set(mode="EDIT")

        if new_edges:
            return True

        return False
