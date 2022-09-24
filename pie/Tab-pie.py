import bpy
import os
from bpy.types import Menu, Operator, AddonPreferences
from .utils import set_pie_ridius


submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "PIE",
}


class VIEW3D_PIE_MT_Tab(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        # print(context.area.type, context.area.ui_type)

        if context.active_object:
            if context.object.type == 'MESH':
                VIEW3D_MT_object_mode_pie
                view3d.object_mode_pie_or_toggle
                object.mode_set
            # 4 - LEFT
            # 6 - RIGHT
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT


classes = [
    VIEW3D_PIE_MT_Tab,
]


addon_keymaps = []


def register_keymaps():
    keymap_items = {
        '3D View': 'VIEW_3D',
        'Node Editor': 'NODE_EDITOR',
        'Image': 'IMAGE_EDITOR',
    }
    for name, space in keymap_items.items():
        addon = bpy.context.window_manager.keyconfigs.addon
        km = addon.keymaps.new(name=name, space_type=space)
        kmi = km.keymap_items.new(
            idname='wm.call_menu_pie',
            type="TAB",
            value="CLICK_DRAG",
            ctrl=False,
            shift=False,
            alt=False,
        )
        kmi.properties.name = "VIEW3D_PIE_MT_Tab"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Tab")
