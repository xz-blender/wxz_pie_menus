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


class PIE_Unchamfer(bpy.types.Operator):
    bl_idname = "pie.mm_unchamfer"
    bl_label = "斜角 -> 直角"
    bl_description = "选择斜角的循环面，执行本操作，即可转换为直角"
    bl_options = {"REGISTER", "UNDO"}

    handlemethod: EnumProperty(name="Unchamfer Method", items=handle_method_items, default="FACE")  # type: ignore
    slide: FloatProperty(name="Slide", default=0, min=-1, max=1)  # type: ignore
    reverse: BoolProperty(name="Reverse", default=False)  # type: ignore
    sharps: BoolProperty(name="Set Sharps", default=True)  # type: ignore
    bweights: BoolProperty(name="Set Bevel Weights", default=False)  # type: ignore
    bweight: FloatProperty(name="Weight", default=1, min=0, max=1)  # type: ignore
    cyclic: BoolProperty(name="Cyclic", default=False)  # type: ignore
    single: BoolProperty(name="Single", default=False)  # type: ignore
    passthrough: BoolProperty(default=False)  # type: ignore
    allowmodalslide: BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return len([f for f in bm.faces if f.select]) >= 1 or len([e for e in bm.edges if e.select]) > 0

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row()
        row.prop(self, "handlemethod", expand=True)

        if self.handlemethod == "FACE":
            column.prop(self, "slide")

        column.prop(self, "sharps")

        row = column.row()
        row.prop(self, "bweights")
        row.prop(self, "bweight")

        if self.single:
            column.prop(self, "reverse")

    def draw_HUD(self, context):
        if context.area == self.area:
            draw_init(self)

            draw_title(self, self.bl_label)

            draw_prop(self, "Handles", self.handlemethod, hint="scroll UP/Down")
            self.offset += 10

            if self.handlemethod == "FACE":
                draw_prop(
                    self,
                    "Slide",
                    self.slide,
                    offset=18,
                    decimal=2,
                    active=self.allowmodalslide,
                    hint="move LEFT/RIGHT, toggle W, rest ALT + W",
                )
                self.offset += 10

            draw_prop(self, "Set Sharps", self.sharps, offset=18, hint="toggle S")
            draw_prop(self, "Set BWeights", self.bweights, offset=18, hint="toggle B")
            if self.bweights:
                draw_prop(self, "BWeight", self.bweight, offset=18, hint="ALT scroll UP/DOWN")
            self.offset += 10

            if self.single:
                draw_prop(self, "Reverse", self.reverse, offset=18, hint="toggle R")

    def draw_VIEW3D(self, context):
        # if context.scene.MM.debug:
        #     if context.area == self.area:
        #         if self.loops:
        #             draw_lines(self.loops, mx=self.active.matrix_world, color=(0.4, 0.8, 1))

        #         if self.handles:
        #             draw_lines(self.handles, mx=self.active.matrix_world, color=(1, 0.8, 0.4))
        return None

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "MOUSEMOVE":
            wrap_cursor(self, context, event)
            update_HUD_location(self, event)

        events = ["WHEELUPMOUSE", "UP_ARROW", "ONE", "WHEELDOWNMOUSE", "DOWN_ARROW", "TWO", "S", "B", "W", "R"]

        if self.allowmodalslide:
            events.append("MOUSEMOVE")

        if event.type in events:

            if event.type == "MOUSEMOVE":
                if self.passthrough:
                    self.passthrough = False

                else:
                    if self.allowmodalslide:
                        divisor = 1000 if event.shift else 10 if event.ctrl else 100

                        delta_x = event.mouse_x - self.last_mouse_x
                        delta_slide = delta_x / divisor

                        self.slide += delta_slide

            elif event.type in {"WHEELUPMOUSE", "UP_ARROW", "ONE"} and event.value == "PRESS":
                if event.alt:
                    self.bweight += 0.1
                else:
                    self.handlemethod = step_enum(self.handlemethod, handle_method_items, 1)

            elif event.type in {"WHEELDOWNMOUSE", "DOWN_ARROW", "TWO"} and event.value == "PRESS":
                if event.alt:
                    self.bweight -= 0.1
                else:
                    self.handlemethod = step_enum(self.handlemethod, handle_method_items, -1)

            elif event.type == "S" and event.value == "PRESS":
                self.sharps = not self.sharps

            elif event.type == "B" and event.value == "PRESS":
                self.bweights = not self.bweights

            elif event.type == "R" and event.value == "PRESS":
                self.reverse = not self.reverse

            elif event.type == "W" and event.value == "PRESS":
                if event.alt:
                    self.allowmodalslide = False
                    self.slide = 0
                else:
                    self.allowmodalslide = not self.allowmodalslide

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
        self.active = context.view_layer.objects.active

        self.active.update_from_editmode()

        self.slide = 0
        self.reverse = False
        self.allowmodalslide = False
        self.init = True
        self.loops = []
        self.handles = []

        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        init_cursor(self, event)

        try:
            ret = self.main(self.active, modal=True)

            if not ret:
                self.cancel_modal(removeHUD=False)
                return {"FINISHED"}
        except Exception as e:
            if bpy.context.mode == "OBJECT":
                bpy.ops.object.mode_set(mode="EDIT")

            output_traceback(self, e)
            return {"FINISHED"}

        init_status(self, context, "Unchamfer")

        self.area = context.area
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (context,), "WINDOW", "POST_PIXEL")
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (context,), "WINDOW", "POST_VIEW")

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        active = context.active_object
        success = False

        try:
            self.success = self.main(active)
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

        if self.init:
            self.init = False

            self.sharps = any(f.smooth for f in faces)

        ret = get_2_rails_from_chamfer(bm, mg, verts, faces, self.reverse, debug=debug)

        if ret:
            rails, self.cyclic = ret

            sweeps = init_sweeps(bm, active, rails, debug=debug)

            # if bpy.context.scene.MM.debug:
            #     initial_locations = [v.co.copy() for sweep in sweeps for v in sweep["verts"]]

            get_loops(bm, bw, faces, sweeps, debug=debug)

            if self.handlemethod == "FACE":
                create_face_intersection_handles(bm, sweeps, tension=1, debug=debug)
                double_verts = unchamfer_face_intersection(bm, sweeps, slide=self.slide, debug=debug)

            elif self.handlemethod == "LOOP":
                create_loop_intersection_handles(bm, sweeps, tension=1, debug=debug)
                double_verts = unchamfer_loop_intersection(bm, sweeps, debug=debug)

            # if bpy.context.scene.MM.debug:
            #     self.handles = [co for ico, v in zip(initial_locations, double_verts) for co in [ico, v.co.copy()]]
            #     debug_draw_sweeps(self, sweeps, draw_loops=True)

            self.clean_up(bm, sweeps, faces, double_verts, debug=debug)

            if double_verts:
                set_sharps_and_bweights([e for e in bm.edges if e.select], bw, self.sharps, self.bweights, self.bweight)

                bm.to_mesh(active.data)

                bpy.ops.object.mode_set(mode="EDIT")

                return True

            else:
                if self.single:
                    popup_message(
                        ["Loop edges don't intersect. You can't unchamfer in this direction!", "Try toggling Reverse."]
                    )
                else:
                    popup_message(["Loop edges don't intersect."])

        bpy.ops.object.mode_set(mode="EDIT")
        return False

    def init_panel_decal(self, active):
        self.handlemethod = "LOOP"
        self.reverse = True
        self.sharps = False
        self.bweights = False

    def clean_up(self, bm, sweeps, faces, double_verts=None, debug=False):
        if debug:
            print()
            print("Removing faces:", ", ".join(str(f.index) for f in faces))

        bmesh.ops.delete(bm, geom=faces, context="FACES")

        if double_verts:
            bmesh.ops.remove_doubles(bm, verts=double_verts, dist=0.00001)

            two_edged_verts = [v for v in double_verts if v.is_valid and len(v.link_edges) == 2]

            bmesh.ops.dissolve_verts(bm, verts=two_edged_verts)
