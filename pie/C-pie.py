import bpy
import os
from bpy.types import Menu, Operator
from .utils import set_pie_ridius,change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_C(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode
        region = context.space_data.region_3d.view_perspective

        set_pie_ridius(context, 100)

        # addon1:"LoopTools"
        # addon1 = check_rely_addon(rely_addons[2][0], rely_addons[2][1])

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.operator("view3d.walk", text="行走漫游", icon="MOD_DYNAMICPAINT")
        # 2 - BOTTOM
        if ob_type == 'CAMERA' or region == 'CAMERA':
            pie.prop(context.space_data, "lock_camera", text="锁定相机视图")
        else:
            pie.separator()
        # 8 - TOP
        pie.operator("mesh.select_mode",text = '边').type='EDGE'
        # 7 - TOP - LEFT
        pie.operator("mesh.select_mode", text = '点').type='VERT'
        # 9 - TOP - RIGHT
        pie.operator("mesh.select_mode",text = '面').type='FACE'
        # 1 - BOTTOM - LEFT
        pie.operator("view3d.camera_to_view", text="对齐相机至视图")
        # 3 - BOTTOM - RIGHT
        if ob_type == 'CAMERA':
            pie.operator("view3d.object_as_camera", text="激活选择相机")


classes = [
    VIEW3D_PIE_MT_Bottom_C,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'C', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_C"
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


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_C")
