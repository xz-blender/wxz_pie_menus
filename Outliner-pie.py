import bpy
import os
from bpy.types import Menu, Panel, Operator

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class OUTLINER_PIE_MT_Bottom_A(Menu):
    bl_label = 'Outliner-A'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode
        radius = context.preferences.view.pie_menu_radius
        if context.area.type == 'OUTLINER':
            radius = 50
        else:
            radius = 100
        # 4 - LEFT
        pie.operator(
            'outliner.show_one_level', icon='REMOVE', icon_only=True
        ).open = False
        # 6 - RIGHT
        pie.operator('outliner.show_one_level', icon='ADD', icon_only=True)
        # 2 - BOTTOM
        pie.separator()
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
    OUTLINER_PIE_MT_Bottom_A,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Outliner", space_type='OUTLINER')
    kmi = km.keymap_items.new("wm.call_menu_pie", 'A', 'CLICK_DRAG')
    kmi.properties.name = "OUTLINER_PIE_MT_Bottom_A"
    kmi = km.keymap_items.new("outliner.show_active", 'F', 'CLICK')
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
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
#     bpy.ops.wm.call_menu_pie(name="OUTLINER_PIE_MT_Bottom_A")
