from bpy.types import Menu, Panel, Operator
import bpy
import os
from .utils import set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_Z_Overlay(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        set_pie_ridius(context, 100)

        # 4 - LEFT
        if context.active_object:
            col = pie.column()

            row = col.row(align=True)
            row.alignment = "RIGHT"
            row.scale_y = 1.4
            row.scale_x = 1.8
            row.prop(context.object, 'show_bounds',
                     icon='SHADING_BBOX', icon_only=True)
            row.prop(context.object, 'show_wire', icon='CUBE', icon_only=True)

            row = col.row(align=True)
            row.scale_x = 0.8
            row.scale_y = 1.2
            row.prop(context.object, 'display_type',
                     expand=True, invert_checkbox=True)
        else:
            pie.separator()

        # 6 - RIGHT
        pie.operator('view3d.toggle_shading', text='实体',
                     icon='SHADING_SOLID').type = 'SOLID'
        # 2 - BOTTOM
        pie.operator('view3d.toggle_shading', text='预览',
                     icon='SHADING_TEXTURE').type = 'MATERIAL'
        # 8 - TOP
        if context.active_object and context.object.type == 'MESH':
            auto_smooth = pie.operator('wm.call_panel', text='自动光滑', icon='RADIOBUT_ON', emboss=True)
            auto_smooth.name = VIEW_PIE_PT_AutoSmooth.bl_idname
            auto_smooth.keep_open = True
        else:
            pie.separator()
        # 7 - TOP - LEFT    &     9 - TOP - RIGHT
        if context.active_object:
            if context.object.mode == 'OBJECT' and context.object.type == 'MESH':
                pie.operator("OBJECT_OT_shade_smooth", icon='ANTIALIASED')
                pie.operator("OBJECT_OT_shade_flat", icon='ALIASED')
            elif context.object.mode == 'EDIT' and context.object.type == 'MESH':
                pie.operator("MESH_OT_faces_shade_smooth", icon='ANTIALIASED')
                pie.operator("MESH_OT_faces_shade_flat", icon='ALIASED')
            else:
                pie.separator()
                pie.separator()
        else:
            pie.separator()
            pie.separator()
        # 1 - BOTTOM - LEFT
        pie.prop(
            context.space_data.overlay,
            'show_wireframes',
            text="所有线框",
            icon='SHADING_WIRE',
            toggle=False,
        )
        # 3 - BOTTOM - RIGHT
        pie.prop(
            context.space_data.overlay,
            'show_face_orientation',
            icon='NORMALS_FACE',
            toggle=False,
        )


class VIEW_PIE_PT_AutoSmooth(Panel):
    bl_idname = "pie.pie_pt_auto_smooth"
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.4
        row.prop(context.object.data, 'use_auto_smooth', icon='RADIOBUT_ON')

        row = layout.row()
        row.scale_y = 1.1
        row.prop(
            context.object.data,
            'auto_smooth_angle',
            text='角度',
            slider=True,
            expand=True,
            invert_checkbox=True,
        )


class VIEW3D_PIE_MT_Bottom_Z_Shift(Menu):
    bl_label = "Shift-Z"

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        # addon1:"LoopTools"
        # addon1 = check_rely_addon(rely_addons[2][0], rely_addons[2][1])

        # 4 - LEFT
        pie.prop(bpy.context.space_data, 'show_gizmo')
        # 6 - RIGHT
        pie.prop(bpy.context.space_data.overlay, 'show_overlays')
        # 2 - BOTTOM
        # 8 - TOP
        # 7 - TOP - LEFT
        # 9 - TOP - RIGHT
        # 1 - BOTTOM - LEFT
        # 3 - BOTTOM - RIGHT


classes = [
    VIEW3D_PIE_MT_Bottom_Z_Overlay,
    VIEW_PIE_PT_AutoSmooth,
    VIEW3D_PIE_MT_Bottom_Z_Shift,
]

addon_keymaps = []


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'Z', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Z_Overlay"

    kmi = km.keymap_items.new("wm.call_menu_pie", 'Z',
                              'CLICK_DRAG', shift=True)
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Z_Shift"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_Z_Overlay")
