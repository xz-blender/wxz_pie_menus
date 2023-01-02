import bpy
import os
from bpy.types import Menu, Panel, Operator
from .utils import set_pie_ridius, change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_U(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        if ob_mode == 'EDIT':
            if ob_type == 'MESH':
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.operator('uv.cube_project', text='块面投影')
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                pie.operator('uv.project_from_view', text='视角投影')
                # 7 - TOP - LEFT
                pie.separator()
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()


classes = [
    VIEW3D_PIE_MT_Bottom_U,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        'Mesh',
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", 'U', 'CLICK_DRAG')
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_U"
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

    # global key1 # Object X delete
    # key1 = change_default_keymap(
    #     'UV Editor','wm.call_menu',
    #     [('value','CLICK')]
    #     )


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_U")
