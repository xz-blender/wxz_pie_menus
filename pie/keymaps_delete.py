import bpy
from bpy.types import Menu, Panel, Operator

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Setting",
}


def disable_default_keymaps():
    bpy.context.window_manager.keyconfigs.default.keymaps['3D View'].keymap_items.get(
        'view3d.select')


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        'Mesh',
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", 'U', 'CLICK_DRAG')
        kmi.properties.name = "PIE_MT_Bottom_U"
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
#     bpy.ops.wm.call_menu_pie(name="PIE_MT_Bottom_U")
