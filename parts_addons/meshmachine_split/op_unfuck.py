import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
from .utils import *
from .ui import *
from .draw import *
from .props import *
from .items import *
from .selection import *
from .math import *
from .loop import *
from .tools import *
from .handle import *


class PIE_Unfuck(bpy.types.Operator):
    bl_idname = "pie.mm_unfuck"
    bl_label = "调整倒角边缘廓线大小"
    bl_description = "选择倒角轮廓边，每次只能调整一个角的半径，至少选择3条线或四个点"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="Width", default=0, step=0.1)  # type: ignore
    width2: FloatProperty(name="Width 2", default=0, step=0.1)  # type: ignore
    widthlinked: BoolProperty(name="Width Linked", default=True)  # type: ignore
    tension: FloatProperty(name="Tension", default=0.7, min=0.01, max=10, step=0.1)  # type: ignore
    tension_preset: EnumProperty(name="Tension Presets", items=tension_preset_items, default="CUSTOM")  # type: ignore
    tension2: FloatProperty(name="Tension 2", default=0.7, min=0.01, max=10, step=0.1)  # type: ignore
    tension2_preset: EnumProperty(name="Tension Presets", items=tension_preset_items, default="CUSTOM")  # type: ignore
    tensionlinked: BoolProperty(name="Tension Linked", default=True)  # type: ignore
    propagate: IntProperty(name="Propagate", default=0, min=0)  # type: ignore
    fade: FloatProperty(name="Fade", default=1, min=0, max=1, step=0.1)  # type: ignore
    merge: BoolProperty(name="Merge", default=False)  # type: ignore
    advanced: BoolProperty(name="Advanced Mode", default=False)  # type: ignore
    passthrough: BoolProperty(default=False)  # type: ignore
    allowmodalwidth: BoolProperty(default=True)  # type: ignore
    allowmodaltension: BoolProperty(default=False)  # type: ignore

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "merge", toggle=True)

        if not self.merge:
            if self.advanced:
                row = column.row().split(factor=0.2)
                row.prop(self, "widthlinked", icon="LINKED", text="Linked")
                row.prop(self, "width")
                r = row.row()
                r.active = not self.widthlinked
                r.prop(self, "width2")

                row = column.row().split(factor=0.2)
                row.prop(self, "tensionlinked", icon="LINKED", text="Linked")
                row.prop(self, "tension")
                r = row.row()
                r.active = not self.tensionlinked
                r.prop(self, "tension2")
                row = column.row()
                row.prop(self, "tension_preset", expand=True)
                row.prop(self, "tension2_preset", expand=True)
            else:
                column.prop(self, "width")
                column.prop(self, "tension")
                row = column.row()
                row.prop(self, "tension_preset", expand=True)

        column.separator()
        row = column.row().split(factor=0.6)
        row.prop(self, "propagate")

        if not self.merge:
            row.prop(self, "fade")

            column.separator()
            column.prop(self, "advanced")

    def draw_HUD(self, context):
        if context.area == self.area:
            draw_init(self)

            draw_title(self, "Unf*ck")

            draw_prop(self, "Merge", self.merge, hint="toggle M")
            self.offset += 10

            if not self.merge:
                draw_prop(
                    self,
                    "Width",
                    self.width,
                    offset=18,
                    decimal=3,
                    active=self.allowmodalwidth,
                    hint="move LEFT/RIGHT, toggle W, reset ALT + W",
                )
                draw_prop(
                    self,
                    "Tension",
                    self.tension,
                    offset=18,
                    decimal=2,
                    active=self.allowmodaltension,
                    hint="move UP/DOWN, toggle T, presets Z/Y, X, C, V",
                )
                self.offset += 10

            draw_prop(self, "Propagate", self.propagate, offset=18, hint="scroll UP/DOWN")
            if self.propagate > 0 and not self.merge:
                draw_prop(self, "Fade", self.fade, offset=18, decimal=1, hint="ALT scroll  UP/DOWN")

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            mode = bpy.context.scene.tool_settings.mesh_select_mode
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return len([e for e in bm.edges if e.select]) >= 2 and (mode[0] or mode[1])

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "MOUSEMOVE":
            wrap_cursor(self, context, event)
            update_HUD_location(self, event)

        events = [
            "WHEELUPMOUSE",
            "UP_ARROW",
            "ONE",
            "WHEELDOWNMOUSE",
            "DOWN_ARROW",
            "TWO",
            "Y",
            "Z",
            "X",
            "C",
            "V",
            "W",
            "T",
            "M",
        ]

        if any([self.allowmodalwidth, self.allowmodaltension]):
            events.append("MOUSEMOVE")

        if event.type in events:

            if event.type == "MOUSEMOVE":
                if self.passthrough:
                    self.passthrough = False

                else:
                    if self.allowmodalwidth:
                        divisor = 100 if event.shift else 1 if event.ctrl else 10

                        delta_x = event.mouse_x - self.last_mouse_x
                        delta_width = delta_x / divisor * self.factor

                        self.width += delta_width

                    if self.allowmodaltension:
                        divisor = 1000 if event.shift else 10 if event.ctrl else 100

                        delta_y = event.mouse_y - self.last_mouse_y
                        delta_tension = delta_y / divisor

                        self.tension_preset = "CUSTOM"
                        self.tension += delta_tension

            elif event.type == "M" and event.value == "PRESS":
                self.merge = not self.merge

            elif event.type in {"WHEELUPMOUSE", "UP_ARROW", "ONE"} and event.value == "PRESS":
                if event.alt:
                    self.fade += 0.1
                else:
                    self.propagate += 1

            elif event.type in {"WHEELDOWNMOUSE", "DOWN_ARROW", "TWO"} and event.value == "PRESS":
                if event.alt:
                    self.fade -= 0.1
                else:
                    self.propagate -= 1

            elif (event.type == "Y" or event.type == "Z") and event.value == "PRESS":
                self.tension_preset = "0.55"

            elif event.type == "X" and event.value == "PRESS":
                self.tension_preset = "0.7"

            elif event.type == "C" and event.value == "PRESS":
                self.tension_preset = "1"

            elif event.type == "V" and event.value == "PRESS":
                self.tension_preset = "1.33"

            elif event.type == "W" and event.value == "PRESS":
                if event.alt:
                    self.allowmodalwidth = False
                    self.width = 0
                else:
                    self.allowmodalwidth = not self.allowmodalwidth

            elif event.type == "T" and event.value == "PRESS":
                self.allowmodaltension = not self.allowmodaltension

            try:
                ret = self.main(self.active, modal=True)

                if not ret:
                    self.finish()
                    return {"FINISHED"}
            except Exception as e:
                output_traceback(self, e)

                self.finish()

                self.merge = False
                return {"FINISHED"}

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

        finish_status(self)

    def invoke(self, context, event):
        self.active = context.active_object

        self.active.update_from_editmode()

        self.width = 0
        self.propagate = 0

        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        self.factor = get_zoom_factor(
            context, self.active.matrix_world @ average_locations([v.co for v in self.initbm.verts if v.select])
        )

        init_cursor(self, event)

        self.init_tension = self.tension

        init_status(self, context, "Unf*ck")

        self.area = context.area
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context,), "WINDOW", "POST_PIXEL")

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
        if self.tension_preset != "CUSTOM":
            self.tension = float(self.tension_preset)

        if self.tension2_preset != "CUSTOM":
            self.tension2 = float(self.tension2_preset)

        debug = False

        bpy.ops.object.mode_set(mode="OBJECT")

        if modal:
            self.initbm.to_mesh(active.data)

        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        mg = build_mesh_graph(bm)

        seq = get_vert_sequence(bm, mg, verts, debug=debug)

        if seq:
            if len(seq) > 3:
                self.merge_verts = []

                align_vert_sequence_to_spline(
                    bm,
                    seq,
                    self.width,
                    self.width2,
                    self.tension,
                    self.tension2,
                    0,
                    self.merge,
                    self.merge_verts,
                    False,
                    self.widthlinked,
                    self.tensionlinked,
                    self.advanced,
                    debug=debug,
                )

                if self.propagate:
                    propagate_edge_loops(
                        bm,
                        seq,
                        self.propagate,
                        self.width,
                        self.width2,
                        self.tension,
                        self.tension2,
                        self.fade,
                        self.merge,
                        self.merge_verts,
                        self.widthlinked,
                        self.tensionlinked,
                        self.advanced,
                        debug=debug,
                    )

                if self.merge:
                    for mvs in self.merge_verts:
                        bmesh.ops.remove_doubles(bm, verts=mvs, dist=0.00001)

        bm.to_mesh(active.data)
        bpy.ops.object.mode_set(mode="EDIT")

        if seq:
            return True
        else:
            return False
