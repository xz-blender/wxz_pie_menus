import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty

from .draw import *
from .handle import *
from .items import *
from .loop import *
from .math import *
from .props import *
from .selection import *
from .tools import *
from .ui import *
from .utils import *


class PIE_Fuse(bpy.types.Operator):
    bl_idname = "pie.mm_fuse"
    bl_label = "斜角 -> 圆角"
    bl_description = "请选择斜角面的循环面，进行操作"
    bl_options = {"REGISTER", "UNDO"}

    method: EnumProperty(name="方法", items=fuse_method_items, default="FUSE")  # type: ignore
    handlemethod: EnumProperty(name="斜角转直角方法", items=handle_method_items, default="FACE")  # type: ignore
    segments: IntProperty(name="分段数", default=6, min=0, max=30)  # type: ignore
    tension: FloatProperty(name="张力", default=0.7, min=0.01, max=4, step=0.1)  # type: ignore
    tension_preset: EnumProperty(name="张力预设", items=tension_preset_items, default="CUSTOM")  # type: ignore
    average: BoolProperty(name="平均张力", default=False)  # type: ignore
    force_projected_loop: BoolProperty(name="强制循环投影", default=False)  # type: ignore
    width: FloatProperty(name="宽度", default=0.0, step=0.1)  # type: ignore
    capholes: BoolProperty(name="端侧-填充孔洞", default=True)  # type: ignore
    capdissolveangle: IntProperty(name="端侧-融并角度", min=0, max=180, default=10)  # type: ignore
    smooth: BoolProperty(name="平滑着色", default=False)  # type: ignore
    reverse: BoolProperty(name="翻转", default=False)  # type: ignore
    cyclic: BoolProperty(name="循环闭合", default=False)  # type: ignore
    single: BoolProperty(name="单一", default=False)  # type: ignore
    passthrough: BoolProperty(default=False)  # type: ignore
    allowmodalwidth: BoolProperty(default=False)  # type: ignore
    allowmodaltension: BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return len([f for f in bm.faces if f.select]) >= 1

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row()
        row.prop(self, "method", expand=True)
        column.separator()

        if self.method == "FUSE":
            row = column.row()
            row.prop(self, "handlemethod", expand=True)
            column.separator()

        column.prop(self, "segments")
        column.prop(self, "tension")
        row = column.row()
        row.prop(self, "tension_preset", expand=True)

        if self.method == "FUSE":
            if self.handlemethod == "FACE":
                column.prop(self, "average")
            column.prop(self, "force_projected_loop")

            column.separator()
            column.prop(self, "width")
            if not self.cyclic:
                column.separator()
                row = column.row().split(factor=0.3)
                row.prop(self, "capholes")
                row.prop(self, "capdissolveangle")

            column.prop(self, "smooth")

        if self.single:
            column.separator()
            column.prop(self, "reverse")

    def draw_HUD(self, context):

        if context.area == self.area:
            draw_init(self)

            draw_title(self, "斜角 -> 圆角")

            draw_prop(self, "圆角方法", self.method, offset=0, hint="SHIFT + 滚轮")
            if self.method == "FUSE":
                draw_prop(self, "控制方法", self.handlemethod, offset=18, hint="CTRL + 滚轮")
            self.offset += 10

            draw_prop(self, "分段数", self.segments, offset=18, hint="滚轮")
            draw_prop(
                self,
                "张力",
                self.tension,
                offset=18,
                decimal=2,
                active=self.allowmodaltension,
                hint="T 开启，上下移动调整，Z/Y 重置, X/C/V 预设值",
            )

            if self.method == "FUSE":
                if self.handlemethod == "FACE":
                    draw_prop(self, "平均张力", self.average, offset=18, hint="A 切换")
                draw_prop(self, "投影循环", self.force_projected_loop, offset=18, hint="P 切换")

                self.offset += 10

                draw_prop(
                    self,
                    "宽度",
                    self.width,
                    offset=18,
                    decimal=3,
                    active=self.allowmodalwidth,
                    hint="W 开启，左右移动调整，ALT + W 重置",
                )
                self.offset += 10

                if not self.cyclic:
                    draw_prop(self, "端侧-填充孔洞", self.capholes, offset=18, hint="F 切换")
                    draw_prop(self, "端侧-融并角度", self.capdissolveangle, offset=18, hint="ALT + 滚轮")
                    self.offset += 10

                draw_prop(self, "平滑着色", self.smooth, offset=18, hint="S 切换")

            if self.single:
                self.offset += 10
                draw_prop(self, "转换方向", self.reverse, offset=18, hint="R 切换")

    def draw_VIEW3D(self, context):
        # if context.scene.MM.debug:
        #     if context.area == self.area:
        #         if self.loops:
        #             draw_lines(self.loops, mx=self.active.matrix_world, color=blue)

        #         if self.handles:
        #             draw_lines(self.handles, mx=self.active.matrix_world, color=yellow)
        return None

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
            "R",
            "S",
            "F",
            "Y",
            "Z",
            "X",
            "C",
            "V",
            "W",
            "T",
            "A",
            "P",
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

            elif event.type in {"WHEELUPMOUSE", "UP_ARROW", "ONE"} and event.value == "PRESS":
                if event.shift:
                    self.method = step_enum(self.method, fuse_method_items, 1)
                elif event.ctrl:
                    self.handlemethod = step_enum(self.handlemethod, handle_method_items, 1)
                elif event.alt:
                    self.capdissolveangle += 5
                else:
                    self.segments += 1

            elif event.type in {"WHEELDOWNMOUSE", "DOWN_ARROW", "TWO"} and event.value == "PRESS":
                if event.shift:
                    self.method = step_enum(self.method, fuse_method_items, -1)
                elif event.ctrl:
                    self.handlemethod = step_enum(self.handlemethod, handle_method_items, -1)
                elif event.alt:
                    self.capdissolveangle -= 5
                else:
                    self.segments -= 1

            elif event.type == "R" and event.value == "PRESS":
                self.reverse = not self.reverse

            elif event.type == "S" and event.value == "PRESS":
                self.smooth = not self.smooth

            elif event.type == "F" and event.value == "PRESS":
                self.capholes = not self.capholes

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

            elif event.type == "A" and event.value == "PRESS":
                self.average = not self.average

            elif event.type == "P" and event.value == "PRESS":
                self.force_projected_loop = not self.force_projected_loop

            try:
                ret = self.main(self.active, modal=True)

                if not ret:
                    self.finish()
                    return {"FINISHED"}
            except Exception as e:
                self.finish()

                if bpy.context.mode == "OBJECT":
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
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, "WINDOW")

        finish_status(self)

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            self.finish()

        bpy.ops.object.mode_set(mode="OBJECT")
        self.initbm.to_mesh(self.active.data)
        bpy.ops.object.mode_set(mode="EDIT")

    def invoke(self, context, event):
        self.active = context.active_object

        self.active.update_from_editmode()

        self.width = 0
        self.reverse = False
        self.force_projected_loop = False
        self.init = True
        self.loops = []
        self.handles = []

        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        self.factor = get_zoom_factor(
            context, self.active.matrix_world @ average_locations([v.co for v in self.initbm.verts if v.select])
        )

        init_cursor(self, event)

        try:
            ret = self.main(self.active, modal=True)
            if not ret:
                self.cancel_modal(removeHUD=False)
                return {"FINISHED"}
        except Exception as e:
            output_traceback(self, e)

            if bpy.context.mode == "OBJECT":
                bpy.ops.object.mode_set(mode="EDIT")
            return {"FINISHED"}

        init_status(self, context, self.bl_label)

        self.area = context.area
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context,), "WINDOW", "POST_PIXEL")
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (context,), "WINDOW", "POST_VIEW")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        active = context.active_object
        success = False

        try:
            success = self.main(active)

        except Exception as e:
            output_traceback(self, e)

        return {"FINISHED"}

    def main(self, active, modal=False):
        if self.segments > 0 or modal is True:

            if self.tension_preset != "CUSTOM":
                self.tension = float(self.tension_preset)

            debug = True
            debug = False

            bpy.ops.object.mode_set(mode="OBJECT")

            if modal:
                self.initbm.to_mesh(active.data)
                if self.segments == 0:
                    bpy.ops.object.mode_set(mode="EDIT")
                    return True

            bm = bmesh.new()
            bm.from_mesh(active.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            vg, bw, _ = ensure_custom_data_layers(bm)

            mg = build_mesh_graph(bm, debug=debug)
            verts = [v for v in bm.verts if v.select]
            faces = [f for f in bm.faces if f.select]

            self.single = True if len(faces) == 1 else False

            if self.init:
                self.init = False
                self.smooth = True if any(f.smooth for f in faces) else False

            ret = get_2_rails_from_chamfer(bm, mg, verts, faces, self.reverse, debug=debug)

            if ret:
                rails, self.cyclic = ret

                if self.method == "FUSE":
                    sweeps = init_sweeps(bm, active, rails, debug=debug)

                    get_loops(bm, bw, faces, sweeps, force_projected=self.force_projected_loop, debug=debug)

                    if self.width != 0:
                        change_width(bm, sweeps, self.width, debug=debug)

                    if self.handlemethod == "FACE":
                        create_face_intersection_handles(
                            bm, sweeps, tension=self.tension, average=self.average, debug=debug
                        )
                    elif self.handlemethod == "LOOP":
                        create_loop_intersection_handles(bm, sweeps, self.tension, debug=debug)

                    # if bpy.context.scene.MM.debug:
                    #     debug_draw_sweeps(self, sweeps, draw_loops=True, draw_handles=True)

                    spline_sweeps = create_splines(bm, sweeps, self.segments, debug=debug)

                    self.clean_up(bm, sweeps, faces, debug=debug)

                    fuse_faces, _ = fuse_surface(
                        bm, spline_sweeps, self.smooth, self.capholes, self.capdissolveangle, self.cyclic, debug=debug
                    )

                    set_sweep_sharps_and_bweights(bm, bw, sweeps, spline_sweeps, vg=vg)
                    clear_rail_sharps_and_bweights(bm, bw, rails, self.cyclic)

                elif self.method == "BRIDGE":
                    # if bpy.context.scene.MM.debug:
                    # self.loops.clear()
                    # self.handles.clear()

                    for f in bm.faces:
                        f.select = False

                    bmesh.ops.delete(bm, geom=faces, context="FACES")

                    clear_rail_sharps_and_bweights(bm, bw, rails, self.cyclic, select=True)

                bm.to_mesh(active.data)

                bpy.ops.object.mode_set(mode="EDIT")

                if self.method == "BRIDGE":
                    bpy.ops.mesh.bridge_edge_loops(
                        number_cuts=self.segments, smoothness=self.tension, interpolation="SURFACE"
                    )

                return True

            else:
                bpy.ops.object.mode_set(mode="EDIT")

        return False

    def init_panel_decal(self, active):
        self.reverse = True
        self.capholes = False
        self.handlemethod = "LOOP"

    def clean_up(self, bm, sweeps, faces, debug=False):
        if debug:
            print()
            print("Removing faces:", ", ".join(str(f.index) for f in faces))

        bmesh.ops.delete(bm, geom=faces, context="FACES")
