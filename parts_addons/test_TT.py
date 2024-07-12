bl_info = {
    "name": "panel geonodes",
    "author": "wxz",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "文件浏览器面板左上角",
    "description": "当前文件夹 & 在资源管理器中打开当前文件夹",
    "category": "System",
}
import sys
from os.path import basename, dirname, exists, realpath, split

import bpy
from bpy.types import Operator


class NODES_PT_top_make_button(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_category = "Bookmarks"
    bl_label = "Filebrowser"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return context.region.alignment in {"LEFT", "RIGHT"}

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 1.3
        layout.scale_y = 1.3

        row = layout.row(align=True)
        row.operator("pie.empty_operator", text="这是一个按钮", icon="FILE_FOLDER")


classes = NODES_PT_top_make_button
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()


def unregister():
    class_unregister()
