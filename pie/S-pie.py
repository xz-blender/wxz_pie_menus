import bpy
import os
from bpy.types import Menu, Panel, Operator
from .utils import check_rely_addon, rely_addons, set_pie_ridius, pie_op_check

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_S(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        set_pie_ridius(context, 100)

        ui = context.area.ui_type

        if ui == "VIEW_3D":
            ob_type = context.object.type
            ob_mode = context.object.mode

            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            if ob_mode == 'EDIT':
                pie.operator(PIE_S_flat_op.bl_idname, text='Z拍平')
            else:
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
        elif ui == "UV":
            # 4 - LEFT
            pie.operator('uv.align', text='对齐到 X 轴').axis = 'ALIGN_X'
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator('uv.align', text='对齐到 Y 轴').axis = 'ALIGN_Y'
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


class PIE_S_flat_op(Operator):
    bl_idname = "pie.view_s_flat_z"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.transform.resize(
            value=(1, 1, -0),
            # orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            # orient_matrix_type='GLOBAL',
            # constraint_axis=(False, False, True),
            # mirror=True,
            # use_proportional_edit=False,
            # proportional_edit_falloff='SMOOTH',
            # proportional_size=1,
            # use_proportional_connected=False,
            # use_proportional_projected=False,
        )
        return {"FINISHED"}


classes = [VIEW3D_PIE_MT_Bottom_S, PIE_S_flat_op]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        ('3D View', 'VIEW_3D'),
        ('UV Editor', 'EMPTY'),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("wm.call_menu_pie", 'S', 'CLICK_DRAG')
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_S"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_S")
