import bpy
import os
from bpy.types import Menu, Panel, Operator
from .utils import check_rely_addon, rely_addons, set_pie_ridius, pie_check_rely_addon_op
from .utils import change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}

import_export_relay_default_addons = {
    'STL format': 'io_mesh_stl',
    'FBX format': 'io_scene_fbx',
    'Scalable Vector Graphics (SVG) 1.1 format': 'io_curve_svg',
    'glTF 2.0 format': 'io_scene_gltf2',
    'Import AutoCAD DXF Format (.dxf)': 'io_import_dxf',
    'Export Autocad DXF Format (.dxf)': 'io_export_dxf',
}

for name, path in import_export_relay_default_addons.items():
    if check_rely_addon(name, path) == '0':
        try:
            bpy.ops.preferences.addon_enable(module=path)
        except:
            print("%s插件启用失败,请手动开启!" % (name))

# SketchUp IO Addon:
su_name, su_path = rely_addons[5][0], rely_addons[5][1]
su_check = check_rely_addon(su_name, su_path)

# DXF import
i_dxf_name, i_dxf_path = rely_addons[11][0], rely_addons[11][1]
i_dxf_check = check_rely_addon(i_dxf_name, i_dxf_path)

# DXF export
e_dxf_name, e_dxf_path = rely_addons[12][0], rely_addons[12][1]
e_dxf_check = check_rely_addon(e_dxf_name, e_dxf_path)


class VIEW3D_PIE_MT_Bottom_S_ctrl_Files(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        if context.selected_objects != [] and context.active_object != None:
            if context.object.type == 'OBJECT':
                    # 4 - LEFT
                    pie.separator()
                    # 6 - RIGHT
                    # 2 - BOTTOM
                    pie.menu('PIE_MT_S_Ctrl_export', text='导出', icon='EXPORT')
                    # 8 - TOP
                    pie.menu('PIE_MT_S_Ctrl_import', text='导入', icon='IMPORT')
                    # 7 - TOP - LEFT
                    # col.separator(factor=0.2)
                    # 9 - TOP - RIGHT
                    # 1 - BOTTOM - LEFT
                    # 3 - BOTTOM - RIGHT
            else:
                 # 4 - LEFT
                    pie.separator()
                    # 6 - RIGHT
                    # 2 - BOTTOM
                    # 8 - TOP
                    # 7 - TOP - LEFT
                    # col.separator(factor=0.2)
                    # 9 - TOP - RIGHT
                    # 1 - BOTTOM - LEFT
                    # 3 - BOTTOM - RIGHT
            pass
        else:
            # 4 - LEFT
            pie.operator('wm.open_mainfile', text='打开文件', icon='FILEBROWSER')
            # 6 - RIGHT
            pie.operator('wm.read_homefile', text='新建文件',
                        icon='FILE_NEW').app_template = ""
            # 2 - BOTTOM
            pie.menu('PIE_MT_S_Ctrl_export', text='导出', icon='EXPORT')
            # 8 - TOP
            pie.menu('PIE_MT_S_Ctrl_import', text='导入', icon='IMPORT')

            # 7 - TOP - LEFT
            col = pie.split().column(align=True)
            col.scale_y = 1.1
            row = col.box().row()
            row.prop(context.blend_data, 'use_autopack')
            row.prop(context.preferences.filepaths, 'use_load_ui')
            # col.separator(factor=0.2)

            col = col.row().box().column(align=True)
            col.scale_y = 0.9
            row = col.row(align=True)
            row.operator('file.pack_all', icon='UGLYPACKAGE')
            row.separator(factor=0.4)
            row.operator('file.unpack_all', icon='PACKAGE')
            col.separator(factor=0.4)
            row = col.row(align=True)
            row.operator('file.report_missing_files', text='报告 缺失文件')
            row.separator(factor=0.4)
            row.operator('file.find_missing_files', text='查找 缺失文件')

            # 9 - TOP - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.2
            row = col.row()
            row.operator('wm.link', text='关联数据', icon='LINKED')
            row = col.row()
            row.operator('wm.append', text='追加数据', icon='APPEND_BLEND')

            # 1 - BOTTOM - LEFT
            pie.operator('outliner.orphans_purge', text='清理未使用',
                        icon='ORPHAN_DATA').do_recursive = True

            # 3 - BOTTOM - RIGHT
            if pie_check_rely_addon_op(pie, 'Atomic Data Manager'):
                pie.operator('atomic.clean_all', text='清理所有', icon='PARTICLEMODE')


class PIE_MT_S_Ctrl_import(Menu):
    bl_idname = __qualname__  # Python 3.3+
    bl_label = ""

    def draw(self, context):

        layout = self.layout
        layout.scale_x = 0.4
        col = layout.column(align=True)
        col.scale_y = 1.2

        row = col.row()
        row.operator('wm.collada_import', text='—— dae ——', icon='EVENT_D')

        row = col.row()
        if i_dxf_check == '0':
            row.operator('pie.empty_operator',
                         text='启用DXF导入插件', icon='QUESTION')
        elif i_dxf_check == '1':
            row.operator('import_scene.dxf', text='—— DXF ——', icon='EVENT_D')

        row = col.row()
        row.operator('import_scene.fbx', text='—— fbx ——', icon='EVENT_F')

        row = col.row()
        row.operator('import_scene.gltf', text='—— gltf ——', icon='EVENT_G')

        row = col.row()
        row.operator('wm.obj_import', text='—— obj ——', icon='EVENT_O')

        row = col.row()
        if su_check == '2':
            row.operator('pie.empty_operator', text='安装SU导入插件', icon='ERROR')
        elif su_check == '0':
            row.operator('pie.empty_operator',
                         text='启用SU导入插件', icon='QUESTION')
        elif su_check == '1':
            row.operator('import_scene.skp', text='—— skp ——', icon='EVENT_S')

        row = col.row()
        row.operator('wm.stl_import', text='—— stl ——', icon='EVENT_S')

        row = col.row()
        row.operator('import_curve.svg', text='—— svg ——', icon='EVENT_S')


class PIE_MT_S_Ctrl_export(Menu):
    bl_idname = __qualname__  # Python 3.3+
    bl_label = ""

    def draw(self, context):

        layout = self.layout
        layout.scale_x = 0.4
        col = layout.column(align=True)
        col.scale_y = 1.2

        row = col.row()
        row.operator('wm.collada_export', text='—— DAE ——', icon='EVENT_D')

        row = col.row()
        if e_dxf_check == '0':
            row.operator('pie.empty_operator',
                         text='启用DXF导出插件', icon='QUESTION')
        elif e_dxf_check == '1':
            row.operator('export.dxf', text='—— DXF ——', icon='EVENT_D')

        row = col.row()
        row.operator('export_scene.fbx', text='—— FBX ——', icon='EVENT_F')

        row = col.row()
        row.operator('export_scene.gltf', text='—— GLTF', icon='EVENT_G')

        row = col.row()
        row.operator('wm.obj_export', text='—— OBJ', icon='EVENT_O')

        row = col.row()
        row.operator('export_mesh.stl', text='—— STL ——', icon='EVENT_S')

        # row = col.row()
        # row.operator('import_curve.svg', text='—— svg ——', icon='EVENT_S')


classes = [
    VIEW3D_PIE_MT_Bottom_S_ctrl_Files,
    PIE_MT_S_Ctrl_import,
    PIE_MT_S_Ctrl_export,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        # ('3D View', 'VIEW_3D'),
        # ('UV Editor', 'IMAGE_EDITOR'),
        # ('Node Editor', 'NODE_EDITOR'),
        # ('Text', 'TEXT_EDITOR'),
        # ('Console', 'CONSOLE'),
        # ('Outliner', 'OUTLINER'),
        # ('Property Editor', 'PROPERTIES'),
        # ('File Browser', 'FILE_BROWSER'),
        ('Window', 'EMPTY'),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("wm.call_menu_pie", 'S', 'CLICK_DRAG', ctrl=True)
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_S_ctrl_Files"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_C")
