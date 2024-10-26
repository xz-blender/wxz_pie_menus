import bpy
from bpy.types import Menu, Operator

from .pie_utils import *


class VIEW3D_PIE_MT_Bottom_G(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if context.area.ui_type == "VIEW_3D":
            get_orient = context.scene.transform_orientation_slots[0].type

            if ob_mode == "OBJECT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                rotate_Y = pie.operator("transform.translate", text="Y", icon="EVENT_Y")
                rotate_Y.orient_type = get_orient
                rotate_Y.constraint_axis = (False, True, False)
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT
            elif ob_mode == "EDIT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                rotate_Y = pie.operator("transform.translate", text="Y", icon="EVENT_Y")
                rotate_Y.orient_type = get_orient
                rotate_Y.constraint_axis = (False, True, False)
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT

        elif context.area.ui_type == "UV":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT

            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


classes = [
    VIEW3D_PIE_MT_Bottom_G,
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
        kmi = km.keymap_items.new("wm.call_menu_pie", "G", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_G"
        addon_keymaps.append((km, kmi))

    # kmi.properties.Mode = "MOVE"


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
