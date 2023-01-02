import bpy
import os
import sys
from bpy.types import Menu, Operator
from .utils import check_rely_addon, rely_addons, set_pie_ridius, change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_F(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.emboss = 'PULLDOWN_MENU'
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        # addon1:"Edit Mesh Tools"
        addon1 = check_rely_addon(rely_addons[0][0], rely_addons[0][1])
        # addon2:"Straight Skeleton"
        addon2 = check_rely_addon(rely_addons[1][0], rely_addons[1][1])
        # addon3:"Curve Tools"
        addon3 = check_rely_addon(rely_addons[10][0], rely_addons[10][1])

        if ob_mode == 'OBJECT' and ob_type in [
            'MESH',
            'CURVE',
            'SURFACE',
            'FONT',
            'GPENCIL',
            'ARMATURE',
            'LATTICE',
            'LIGHT',
        ]:
            # 4 - LEFT
            op = pie.operator('object.make_single_user',
                              text='单一化', icon='UNLINKED')
            op.object = True
            op.obdata = True
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator('object.join', text='合并', icon='SELECT_EXTEND')
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            if ob_type == "MESH":
                pie.operator('object.parent_clear')
            elif ob_type == 'ARMATURE':
                pie.operator('armature.parent_clear')
            # 9 - TOP - RIGHT
            if ob_type == "MESH":
                pie.operator('object.parent_set')
            elif ob_type == 'ARMATURE':
                pie.operator('armature.parent_set')
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.operator(
                Clean_Custom_Normal.bl_idname,
                text='批量删自定法线',
                icon='NORMALS_VERTEX_FACE',
            )

        if ob_mode == 'EDIT':
            if ob_type == 'MESH':
                # 4 - LEFT
                pie.operator('wm.tool_set_by_id',
                             text='切刀工具').name = "builtin.knife"
                # 6 - RIGHT
                if addon1 == '0':
                    pie.operator('pie.empty_operator',
                                 text='启用"Edit Mesh Tools"插件!')
                elif addon1 == '1':
                    pie.operator('mesh.offset_edges', text='偏移边线')
                # 2 - BOTTOM
                pie.operator('mesh.subdivide', text='细分')
                # 8 - TOP
                pie.operator('mesh.separate', text='分离选中').type = 'SELECTED'
                # 7 - TOP - LEFT
                pie.operator('mesh.split', text='拆分')
                # 9 - TOP - RIGHT
                if addon1 == '0':
                    pie.operator('pie.empty_operator',
                                 text='启用"Edit Mesh Tools"插件!')
                elif addon1 == '1':
                    pie.operator('mesh.edgetools_extend', text='延伸边')
                # 1 - BOTTOM - LEFT
                if addon2 == '2':
                    pie.operator('pie.empty_operator',
                                 text='未找到"Straight Skeleton"插件!')
                elif addon2 == '0':
                    pie.operator('pie.empty_operator',
                                 text='启用"Straight Skeleton"插件!')
                elif addon2 == '1':
                    pie.operator('mesh.inset_polygon', text='连续偏移')
                # 3 - BOTTOM - RIGHT
                if addon1 == '0':
                    pie.operator('pie.empty_operator',
                                 text='启用"Edit Mesh Tools"插件!')
                elif addon1 == '1':
                    pie.operator('object.mesh_edge_length_set', text='设边长')
            if ob_type == 'CURVE':
                # 4 - LEFT
                pie.operator('curve.smooth', text='光滑')
                # 6 - RIGHT
                if addon3 == '2':
                    pie.operator('pie.empty_operator',
                                 text='未找到"Straight Skeleton"插件!')
                elif addon3 == '0':
                    pie.operator('pie.empty_operator',
                                 text='启用"Straight Skeleton"插件!')
                elif addon3 == '1':
                    pie.operator(
                        'curvetools.add_toolpath_offset_curve', text='曲线偏移')
                pie.separator()
                # 2 - BOTTOM
                pie.operator('curve.subdivide', text='细分')
                # 8 - TOP
                pie.operator('curve.separate', text='分离')
                # 7 - TOP - LEFT
                pie.operator('curve.switch_direction', text='切换方向')
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()


class Clean_Custom_Normal(Operator):
    bl_idname = "pie.clear_custom_normal"
    bl_label = "Clear Custom Data"
    bl_description = "Clear Custom Data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = bpy.context.selected_objects
        for o in selection:
            bpy.context.view_layer.objects.active = o
            try:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            except:
                None
        return {'FINISHED'}


classes = [
    VIEW3D_PIE_MT_Bottom_F,
    Clean_Custom_Normal,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        'Object Mode',
        'Mesh',
        'Curve',
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", 'F', 'CLICK_DRAG')
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_F"
        addon_keymaps.append(km)

    km = addon.keymaps.new(name='Mesh')#,space_type ='VIEW_3D')
    kmi = km.keymap_items.new("mesh.vert_connect_path", 'F', 'CLICK',shift=True)
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

    global key1
    key1 = change_default_keymap(
        'Mesh','mesh.edge_face_add',
        [('value','CLICK')],
        )
    global key2
    key2 = change_default_keymap(
        'Curve','curve.make_segment',
        [('value','CLICK')],
        )
    # global key3
    # key3 = change_default_keymap(
    #     'Node Editor','node.link_make',
    #     [('value','CLICK')],
    #     )

def unregister():
    restored_default_keymap(key1)
    restored_default_keymap(key2)
    # restored_default_keymap(key3)

    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()