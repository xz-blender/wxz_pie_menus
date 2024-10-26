import bpy
from bpy.types import Menu, Operator, Panel

from .pie_utils import *


class PIE_Set_Ctrl_B_HotKey(Operator):
    bl_idname = "pie.set_render_region"
    bl_label = "Set_Render_Region"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.selectable_objects:
            return True

    def execute(self, context):
        if context.object.mode == "EDIT":
            if context.space_data.region_3d.view_perspective == "CAMERA":
                bpy.ops.view3d.render_border("INVOKE_DEFAULT")
            else:
                # change_key_value_base([(["3D View", "view3d.select_box", "Box Select"], [("active", False)], [])])
                bpy.ops.mesh.bevel("INVOKE_DEFAULT")
        elif context.object.mode == "OBJECT":
            if context.space_data.region_3d.view_perspective == "CAMERA":
                bpy.ops.view3d.render_border("INVOKE_DEFAULT")

        return {"FINISHED"}


class VIEW3D_PIE_MT_Ctrl_B(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "EDIT":
            if ob_type == "MESH":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.operator("pie.unbevel")
                # 8 - TOP
                pie.separator()
                # 7 - TOP - LEFT
                pie.separator()
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()


classes = [
    VIEW3D_PIE_MT_Ctrl_B,
    PIE_Set_Ctrl_B_HotKey,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("pie.set_render_region", "B", "CLICK", ctrl=True)

    kmi = km.keymap_items.new("wm.call_menu_pie", "B", "CLICK_DRAG", ctrl=True)
    kmi.properties.name = "VIEW3D_PIE_MT_Ctrl_B"

    km = addon.keymaps.new(name="MESH")
    kmi = km.keymap_items.new("pie.set_render_region", "B", "CLICK", ctrl=True)

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
