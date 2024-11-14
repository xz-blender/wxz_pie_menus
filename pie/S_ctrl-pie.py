import bpy
from bpy.types import Menu, Operator, Panel

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class PIE_Click_Deep_Clean_Purge(bpy.types.Operator):
    bl_idname = "pie.one_purge_orphaned_data"
    bl_label = "清理未使用"
    bl_description = "清理未使用的数据"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        return {"FINISHED"}


class VIEW3D_PIE_MT_Bottom_S_ctrl_Files(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        # 4 - LEFT
        pie.operator("wm.open_mainfile", text="打开文件", icon="FILEBROWSER")
        # 6 - RIGHT
        pie.operator("wm.read_homefile", text="新建文件", icon="FILE_NEW")
        # 2 - BOTTOM
        pie.menu("PIE_MT_S_Ctrl_Export", text="导出", icon="EXPORT")
        # 8 - TOP
        pie.menu("PIE_MT_S_Ctrl_Import", text="导入", icon="IMPORT")

        # 7 - TOP - LEFT
        col = pie.split().column(align=True)
        col.scale_y = 1.1
        row = col.box().row()
        row.prop(context.blend_data, "use_autopack")
        row.prop(context.preferences.filepaths, "use_load_ui")
        # col.separator(factor=0.2)

        col = col.row().box().column(align=True)
        col.scale_y = 0.9
        row = col.row(align=True)
        row.operator("file.pack_all", icon="UGLYPACKAGE")
        row.separator(factor=0.4)
        row.operator("file.unpack_all", icon="PACKAGE")
        col.separator(factor=0.4)
        row = col.row(align=True)
        row.operator("file.report_missing_files", text="报告 缺失文件")
        row.separator(factor=0.4)
        row.operator("file.find_missing_files", text="查找 缺失文件")

        # 9 - TOP - RIGHT
        col = pie.split().box().column(align=True)
        col.scale_x = 1.3
        col.scale_y = 1.2
        row = col.row()
        row.operator("wm.link", text="关联数据", icon="LINKED")
        row = col.row()
        row.operator("wm.append", text="追加数据", icon="APPEND_BLEND")

        # 1 - BOTTOM - LEFT
        pie.operator("pie.one_purge_orphaned_data", text="清理未使用(不提示)", icon="ORPHAN_DATA")

        # 3 - BOTTOM - RIGHT
        # pie.operator('rf.callpanel', text='打开附近文件', icon='FILE_TICK')
        rencent = pie.operator("wm.call_menu", text="最近打开文件", icon="FILE_TICK")
        rencent.name = "TOPBAR_MT_file_open_recent"
        # auto_smooth = pie.operator('wm.call_menu', text='打开附近文件', icon='FILE_TICK', emboss=True)
        # auto_smooth.
        # auto_smooth.keep_open = True


class PIE_MT_S_Ctrl_Import(Menu):
    bl_idname = __qualname__  # Python 3.3+
    bl_label = ""

    def draw(self, context):

        layout = self.layout
        layout.scale_x = 0.4
        col = layout.column(align=True)
        col.scale_y = 1.2

        row = col.row()
        add_operator(row, "import_scene.dxf", text="—— DXF ——", icon="EVENT_D")

        row = col.row()
        row.operator("import_scene.fbx", text="—— FBX ——", icon="EVENT_F")

        row = col.row()
        row.operator("import_scene.gltf", text="—— gltf ——", icon="EVENT_G")

        row = col.row()
        row.operator("wm.obj_import", text="—— obj ——", icon="EVENT_O")

        row = col.row()
        row.operator("wm.stl_import", text="—— stl ——", icon="EVENT_S")

        row = col.row()
        row.operator("import_curve.svg", text="—— svg ——", icon="EVENT_S")

        row = col.row()
        add_operator(row, "import_scene.skp", text="—— skp ——", icon="EVENT_S")


class PIE_MT_S_Ctrl_Export(Menu):
    bl_idname = __qualname__  # Python 3.3+
    bl_label = ""

    def draw(self, context):

        layout = self.layout
        layout.scale_x = 0.4
        col = layout.column(align=True)
        col.scale_y = 1.2

        row = col.row()
        add_operator(row, "export.dxf", text="—— DXF ——", icon="EVENT_D")

        row = col.row()
        row.operator("export_scene.fbx", text="—— FBX ——", icon="EVENT_F")

        row = col.row()
        row.operator("export_scene.gltf", text="—— GLTF", icon="EVENT_G")

        row = col.row()
        row.operator("wm.obj_export", text="—— OBJ", icon="EVENT_O")

        row = col.row()
        row.operator("wm.stl_export", text="—— STL ——", icon="EVENT_S")

        # row = col.row()
        # row.operator('import_curve.svg', text='—— svg ——', icon='EVENT_S')


CLASSES = [
    VIEW3D_PIE_MT_Bottom_S_ctrl_Files,
    PIE_MT_S_Ctrl_Import,
    PIE_MT_S_Ctrl_Export,
    PIE_Click_Deep_Clean_Purge,
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
        ("Window", "EMPTY"),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("wm.call_menu_pie", "S", "CLICK_DRAG", ctrl=True)
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_S_ctrl_Files"
        addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
