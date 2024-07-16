import bpy
import bmesh
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from .items import *
from .selection import *
from .math import *
from .utils import *
from .ui import *
from .props import *
from .draw import *


class PIE_BooleanCleanup(bpy.types.Operator):
    bl_idname = "pie.mm_boolean_cleanup"
    bl_label = "清理布尔交汇边线"
    bl_description = "选择布尔交汇处的循环边(Ngons),执行本操作"
    bl_options = {"REGISTER", "UNDO"}

    sideselection: EnumProperty(name="AB面", items=side_selection_items, default="A")  # type: ignore
    flip: BoolProperty(name="将红色翻转为绿色", default=False)  # type: ignore
    threshold: FloatProperty(name="阈值", default=0, min=0, step=0.1)  # type: ignore
    triangulate: BoolProperty(name="三角化", default=False)  # type: ignore
    allowmodalthreashold: BoolProperty(default=True)  # type: ignore
    sharp: BoolProperty(default=False)  # type: ignore
    debuginit: BoolProperty(default=True)  # type: ignore
    passthrough: BoolProperty(default=False)  # type: ignore

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(self, "sideselection", expand=True)

        column.prop(self, "threshold")

        row = column.row(align=True)

        row.prop(self, "flip", text="Flip", toggle=True)

        row.prop(self, "triangulate", toggle=True)

    def draw_HUD(self, context):
        if context.area == self.area:
            draw_init(self)

            draw_title(self, self.bl_label)

            draw_prop(self, "AB面", self.sideselection, hint="滚轮")
            self.offset += 10

            draw_prop(
                self,
                "阈值",
                self.threshold,
                offset=18,
                decimal=4,
                active=self.allowmodalthreashold,
                hint="W 开关, 左右移动调整, ALT + W 重置",
            )
            self.offset += 10

            draw_prop(self, "翻转", self.flip, offset=18, hint="F 切换")

            draw_prop(self, "三角化", self.triangulate, offset=18, hint="T 开关")

    def draw_VIEW3D(self, context):
        if context.area == self.area:
            mx = self.active.matrix_world

            draw_points(self.fixed_verts, mx=mx, color=green, size=6)
            draw_points(self.unmoved_verts, mx=mx, color=red, size=8)

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            bm = bmesh.from_edit_mesh(context.active_object.data)
            mode = tuple(context.tool_settings.mesh_select_mode)

            if mode == (True, False, False) or mode == (False, True, False):
                return len([v for v in bm.verts if v.select]) >= 1

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "MOUSEMOVE":
            wrap_cursor(self, context, event)
            update_HUD_location(self, event)

        events = ["WHEELUPMOUSE", "ONE", "WHEELDOWNMOUSE", "TWO", "W", "T", "F"]

        if self.allowmodalthreashold:
            events.append("MOUSEMOVE")

        if event.type in events:

            if event.type == "MOUSEMOVE":
                if self.allowmodalthreashold:
                    if self.passthrough:
                        self.passthrough = False

                    else:
                        divisor = 100 if event.shift else 1 if event.ctrl else 10

                        delta_x = event.mouse_x - self.last_mouse_x
                        delta_threshold = delta_x / divisor * self.factor

                        self.threshold += delta_threshold

            elif event.type == "W" and event.value == "PRESS":
                if event.alt:
                    self.allowmodalthreashold = False
                    self.threshold = 0
                else:
                    self.allowmodalthreashold = not self.allowmodalthreashold

            elif event.type == "T" and event.value == "PRESS":
                self.triangulate = not self.triangulate

            elif event.type == "F" and event.value == "PRESS":
                self.flip = not self.flip

            elif event.type in ["WHEELUPMOUSE", "ONE"] and event.value == "PRESS":
                self.sideselection = step_enum(self.sideselection, side_selection_items, 1)

            elif event.type in ["WHEELDOWNMOUSE", "TWO"] and event.value == "PRESS":
                self.sideselection = step_enum(self.sideselection, side_selection_items, -1)

            try:
                ret = self.main(self.active, modal=True)

                if ret is False:
                    self.finish()
                    return {"FINISHED"}

            except Exception as e:
                self.finish()

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

        self.threshold = 0
        self.sharp = False
        self.flip = False

        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        self.factor = get_zoom_factor(
            context, self.active.matrix_world @ average_locations([v.co for v in self.initbm.verts if v.select])
        )

        init_cursor(self, event)

        init_status(self, context, "Boolean Cleanup")

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
        debug = False

        mesh = active.data

        bpy.ops.object.mode_set(mode="OBJECT")

        if modal:
            self.initbm.to_mesh(active.data)

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]

        if any([not e.smooth for e in edges]):
            self.sharp = True

        sideA, sideB, cyclic, err = get_sides(bm, verts, edges, debug=debug)

        if sideA and sideB:
            self.tag_fixed_verts(sideA, sideB)

            if not cyclic:
                sideA[0]["vert"].tag = True
                sideA[-1]["vert"].tag = True

            if self.flip:
                for el in sideA:
                    v = el["vert"]
                    v.tag = not v.tag

            mg = build_edge_graph(verts, edges, debug=debug)

            self.fixed_verts, self.unmoved_verts = self.move_merts(bm, mg, cyclic, debug=debug)

            if self.triangulate:
                self.triangulate_side(bm, sideA, sideB)

            bmesh.ops.remove_doubles(bm, verts=verts, dist=0.00001)

            if self.triangulate and self.sharp:
                for e in bm.edges:
                    if e.select:
                        e.smooth = False

            bm.to_mesh(mesh)
            bpy.ops.object.mode_set(mode="EDIT")

            return True

        else:
            popup_message(err[0], title=err[1])
            bpy.ops.object.mode_set(mode="EDIT")

            return False

    def triangulate_side(self, bm, sideA, sideB):
        faces = []
        if self.sideselection == "A":
            for sB in sideB:
                for f in sB["faces"]:
                    if f not in faces:
                        faces.append(f)
        else:
            for sA in sideA:
                for f in sA["faces"]:
                    if f not in faces:
                        faces.append(f)

        bmesh.ops.triangulate(bm, faces=faces)

    def move_merts(self, bm, mg, cyclic, debug=False):
        fixed_vert_coords = []
        unmoved_vert_coords = []

        if debug:
            print("cylclic selection:", cyclic)

        for eidx, vidx in enumerate(mg):
            if debug:
                print("vert:", vidx)

            fixed = mg[vidx]["fixed"]
            if debug:
                print(" • fixed:", fixed)

            if fixed:
                fixed_vert_coords.append(bm.verts[vidx].co.copy())
                continue

            else:
                A = mg[vidx]["connected"][0]
                B = mg[vidx]["connected"][1]

                Aidx, Afixed, Adist = A
                Bidx, Bfixed, Bdist = B

                lsort = [A, B]
                lsort = sorted(lsort, key=lambda l: l[2])
                closest = lsort[0]
                furthest = lsort[1]

                if closest[2] <= self.threshold:
                    closestidx = closest[0]
                    closestdist = closest[2]

                    furthestidx = furthest[0]

                    bm.verts[vidx].co = bm.verts[closestidx].co
                    if debug:
                        print(" • moved to vert %d - distance: %f" % (closestidx, closestdist))

                    for childidx in mg[vidx]["children"]:
                        bm.verts[childidx].co = bm.verts[closestidx].co
                        if debug:
                            print("  • moved the child vert %d as well" % (childidx))

                    mg[closestidx]["children"].append(vidx)
                    if debug:
                        print(" • updated %d's mg 'children' entry with vert %d" % (closestidx, vidx))

                    for childidx in mg[vidx]["children"]:
                        mg[closestidx]["children"].append(childidx)

                        if debug:
                            print("  • updated %d's mg 'children' entry with vert %d" % (closestidx, childidx))

                    closest_conected = mg[closestidx]["connected"]
                    furthest_connected = mg[furthestidx]["connected"]

                    newdist = get_distance_between_verts(bm.verts[closestidx], bm.verts[furthestidx])

                    for i, con in enumerate(closest_conected):
                        if con[0] == vidx:
                            mg[closestidx]["connected"][i] = (furthestidx, furthest[1], newdist)

                    if debug:
                        print(
                            " • updated %d's mg 'connected' entry with vert %d replacing vert %d"
                            % (closestidx, furthestidx, vidx)
                        )

                    for i, con in enumerate(furthest_connected):
                        if con[0] == vidx:
                            mg[furthestidx]["connected"][i] = (closestidx, closest[1], newdist)

                    if debug:
                        print(
                            " • updated %d's mg 'connected' entry with vert %d replacing vert %d"
                            % (furthestidx, closestidx, vidx)
                        )

                else:
                    unmoved_vert_coords.append(bm.verts[vidx].co.copy())

        return fixed_vert_coords, unmoved_vert_coords

    def tag_fixed_verts(self, sideA, sideB):
        if self.sideselection == "A":
            for sA in sideA:
                if sA["edges"]:

                    sA["vert"].tag = True
        else:
            for sB in sideB:
                if sB["edges"]:

                    sB["vert"].tag = True
