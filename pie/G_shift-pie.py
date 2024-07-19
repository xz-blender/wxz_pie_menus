import bpy
from bpy.types import Menu, Operator

from .utils import change_default_keymap, restored_default_keymap, set_pie_ridius

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_XZ_Shift_G(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        if context.area.ui_type == "VIEW_3D":

            ob_type = context.object.type
            ob_mode = context.object.mode

            set_pie_ridius(context, 100)

            if ob_mode == "OBJECT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                split = pie.split().box().column()
                split.operator_enum("object.select_grouped", "type")
                # 2 - BOTTOM
                # 8 - TOP
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT
            elif ob_mode == "EDIT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                split = pie.split().box().column()
                split.menu_contents("VIEW3D_MT_edit_mesh_select_similar")
                # 2 - BOTTOM
                # 8 - TOP
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT

        elif context.area.ui_type == "UV":

            set_pie_ridius(context, 100)
            # 4 - LEFT
            # 6 - RIGHT
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


classes = [
    VIEW3D_PIE_MT_XZ_Shift_G,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = []


def register_keymaps():
    spaces = {
        "3D View": "VIEW_3D",
        "UV Editor": "EMPTY",
    }
    for name, space_type in spaces.items():
        kc = bpy.context.window_manager.keyconfigs.addon
        km = kc.keymaps.new(name=name, space_type=space_type)
        kmi = km.keymap_items.new("wm.call_menu_pie", "G", "CLICK_DRAG", shift=True)
        kmi.properties.name = "VIEW3D_PIE_MT_XZ_Shift_G"
        kmi = km.keymap_items.new("pie.ke_mouse_axis_move", "G", "CLICK", shift=True)

        addon_keymaps.append((km, kmi))


def unregister_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    class_register()
    register_keymaps()


def unregister():
    class_unregister()
    # unregister_keymaps()
