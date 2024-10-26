import bgl
import blf
import bmesh
import bpy
import numpy as np
from bpy.types import Context, Menu, Operator, Panel, PropertyGroup

from .pie_utils import *


class VIEW3D_PIE_MT_Bottom_E(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "EDIT" and ob_type == "MESH":
            # 4 - LEFT
            pie.operator("mesh.flip_normals")
            # 6 - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_y = 1.1
            col.operator("pie.mm_fuse")
            col.operator("pie.mm_change_width")
            col.operator("pie.mm_unchamfer")
            col.operator("pie.mm_turn_corner")
            col.operator("pie.mm_quad_corner")
            col.separator(factor=0.1)
            col.operator("pie.mm_unfuse")
            col.operator("pie.mm_refuse")
            col.operator("pie.mm_unbevel")
            col.separator(factor=0.1)
            col.operator("pie.mm_offset_cut")
            col.operator("pie.mm_unfuck")
            col.operator("pie.mm_boolean_cleanup")
            col.separator(factor=0.1)
            col.operator("pie.mm_symmetrize")
            # 2 - BOTTOM
            pie.operator("mesh.normals_make_consistent")
            # 8 - TOP
            col = pie.split().box().column(align=True)
            col.scale_y = 1.4
            col.operator("mesh.extrude_manifold", text="挤出流形")
            col.operator("pie.punchit", text="负向流形")
            # 7 - TOP - LEFT
            pie.operator("mesh.bridge_edge_loops", text="桥接循环边")
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            col = pie.split().box().column()
            add_operator(col, "mesh.set_edge_flow")
            add_operator(col, "mesh.set_edge_linear")
            # 3 - BOTTOM - RIGHT
            pie.separator()

        if ob_mode == "OBJECT" and ob_type == "MESH":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.operator("pie.ke_lineararray")
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("pie.ke_radial_instances")
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


class PIE_Shift_E_KEY(Operator):
    bl_idname = "pie.shift_e"
    bl_label = "设置折痕"
    bl_description = "在不同网格选择模式下设置不同的折痕"
    bl_options = {"REGISTER", "UNDO"}

    first_mouse_x: bpy.props.IntProperty()  # type: ignore
    set_value: bpy.props.FloatProperty(min=0, max=1)  # type: ignore
    attr_name: bpy.props.StringProperty()  # type: ignore

    attr_name_item = {
        "bevel_weight_edge": "边 - 倒角权重",
        "bevel_weight_vert": "顶点 - 倒角权重",
        "crease_vert": "顶点 - 折痕",
        "crease_edge": "边 - 折痕",
    }

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def get_suffix_name(self, context):
        mode = context.tool_settings.mesh_select_mode
        if mode[0]:
            return "_vert"
        elif mode[1] or mode[2]:
            return "_edge"

    def get_mode_name(self, context):
        mode = context.tool_settings.mesh_select_mode
        if mode[0]:
            return "POINT"
        elif mode[1] or mode[2]:
            return "EDGE"

    def get_mode_string(self, context):
        mode = context.tool_settings.mesh_select_mode
        if mode[0]:
            return "vertices"
        elif mode[1] or mode[2]:
            return "edges"

    def modal(self, context, event):
        """Old Operator - Bad Performance"""
        """
        bpy.ops.object.mode_set(mode="OBJECT")
        if event.type == "MOUSEMOVE":
            delta = event.mouse_x - self.first_mouse_x
            self.set_value = delta * 0.005

            ac_data = bpy.context.object.data
            ac_attr = ac_data.attributes
            attr_name = self.attr_name + self.get_suffix_name(context)

            if attr_name not in ac_attr:
                attr = ac_attr.new(attr_name, "FLOAT", self.get_mode_name(context))
                for idx, e in enumerate(getattr(ac_data, self.get_mode_string(context))):
                    if e.select:
                        attr.data[idx].value = self.set_value
            else:
                attr = ac_data.attributes[attr_name]
                for idx, e in enumerate(getattr(ac_data, self.get_mode_string(context))):
                    if e.select:
                        attr.data[idx].value = self.set_value

        elif event.type == "MIDDLEMOUSE":
            return {"PASS_THROUGH"}
        elif event.type == "LEFTMOUSE":
            bpy.ops.object.mode_set(mode="EDIT")
            context.area.tag_redraw()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            context.area.tag_redraw()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            bpy.ops.object.mode_set(mode="EDIT")
            return {"CANCELLED"}
        bpy.ops.object.mode_set(mode="EDIT")
        return {"RUNNING_MODAL"}
        """
        if event.type == "MOUSEMOVE":
            delta = event.mouse_x - self.first_mouse_x
            self.set_value = delta * 0.005

            ac_data = bpy.context.object.data
            ac_attr = ac_data.attributes
            attr_name = self.attr_name + self.get_suffix_name(context)

            bpy.ops.object.mode_set(mode="OBJECT")

            if attr_name not in ac_attr:
                attr = ac_attr.new(attr_name, "FLOAT", self.get_mode_name(context))
            else:
                attr = ac_attr[attr_name]

            elements = np.array([e.select for e in getattr(ac_data, self.get_mode_string(context))])
            selected_indices = np.where(elements)[0]

            for idx in selected_indices:
                attr.data[idx].value = self.set_value

            bpy.ops.object.mode_set(mode="EDIT")

        elif event.type == "MIDDLEMOUSE":
            return {"PASS_THROUGH"}
        elif event.type == "LEFTMOUSE":
            context.area.tag_redraw()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            context.area.tag_redraw()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x
            context.window_manager.modal_handler_add(self)

            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback, (context,), "WINDOW", "POST_PIXEL"
            )
            context.area.tag_redraw()
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

    def draw_callback(self, context):
        region = context.region
        mid_x = region.width / 2 - 200
        mid_y = region.height * 0.1

        font_id = 0
        blf.position(font_id, mid_x, mid_y, 0)
        blf.size(font_id, 50)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        blf.draw(font_id, f"{self.attr_name_item[self.attr_name+self.get_suffix_name(context)]} : {self.set_value:.2f}")


classes = [
    VIEW3D_PIE_MT_Bottom_E,
    PIE_Shift_E_KEY,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "E", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_E"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", shift=True)
    kmi.properties.attr_name = "crease"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", ctrl=True, shift=True)
    kmi.properties.attr_name = "bevel_weight"
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():

    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
