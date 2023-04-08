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


class VIEW3D_PIE_MT_Bottom_V(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        if ob_mode == 'OBJECT':
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
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

        elif ob_mode == 'EDIT':
            if ob_type == 'CURVE':
                # 4 - LEFT
                pie.operator(
                    'curve.handle_type_set', text='矢量', icon='HANDLE_VECTOR'
                ).type = 'VECTOR'
                # 6 - RIGHT
                pie.operator(
                    'curve.handle_type_set', text='对齐', icon='HANDLE_ALIGNED'
                ).type = 'ALIGNED'
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                pie.operator(
                    'curve.handle_type_set',
                    text='自由/对齐',
                    icon='HANDLE_AUTOCLAMPED',
                ).type = 'TOGGLE_FREE_ALIGN'
                # 7 - TOP - LEFT
                pie.operator(
                    'curve.handle_type_set', text='自由', icon='HANDLE_FREE'
                ).type = 'FREE_ALIGN'
                # 9 - TOP - RIGHT
                pie.operator(
                    'curve.handle_type_set', text='自动', icon='HANDLE_AUTO'
                ).type = 'AUTOMATIC'
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()

            elif ob_type == 'MESH':
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.operator('uv.cube_project', text='块面投影')
                # 2 - BOTTOM
                pie.operator('uv.muv_uvw_box_map').assign_uvmap = True
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
    VIEW3D_PIE_MT_Bottom_V,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View",space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'V', 'CLICK_DRAG')
    kmi.properties.name = 'VIEW3D_PIE_MT_Bottom_V'
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_V")
