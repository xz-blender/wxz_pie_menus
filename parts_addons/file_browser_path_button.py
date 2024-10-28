bl_info = {
    "name": "File Browser Path Button",
    "author": "wxz",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "文件浏览器面板左上角",
    "description": "当前文件夹 & 在资源管理器中打开当前文件夹",
    "category": "System",
}
import sys
from os.path import basename, dirname, exists, isfile, normpath, realpath, split
from shutil import which

import bpy
from bpy.types import Operator, Panel


def openFolder(folderpath):
    """
    open the folder at the path given
    with cmd relative to user's OS
    on window, select
    """
    import subprocess

    myOS = sys.platform
    if myOS.startswith(("linux", "freebsd")):
        cmd = "xdg-open"

    elif myOS.startswith("win"):
        cmd = "explorer"
        if not folderpath:
            return "/"
    else:
        cmd = "open"

    if not folderpath:
        return "//"

    if isfile(folderpath):  # When pointing to a file
        select = False
        if myOS.startswith("win"):
            # Keep same path but add "/select" the file (windows cmd option)
            cmd = "explorer /select,"
            select = True

        elif myOS.startswith(("linux", "freebsd")):
            if which("nemo"):
                cmd = "nemo --no-desktop"
                select = True
            elif which("nautilus"):
                cmd = "nautilus --no-desktop"
                select = True

        if not select:
            # Use directory of the file
            folderpath = dirname(folderpath)

    folderpath = normpath(folderpath)
    fullcmd = cmd.split() + [folderpath]
    # print('Opening command :', fullcmd)
    subprocess.Popen(fullcmd)
    return " ".join(fullcmd)


class PATH_OT_browser_to_blend_folder(Operator):
    """current blend path to the browser filepath"""

    bl_idname = "path.paste_path"
    bl_label = "Browser to blend folder"

    def execute(self, context):
        bpy.ops.file.select_bookmark(dir="//")
        return {"FINISHED"}


class PATH_OT_open_filepath_folder(Operator):
    """在资源管理器中打开浏览器文件路径目录"""

    bl_idname = "path.open_filepath"
    bl_label = "在外部打开当前文件路径文件夹"

    def execute(self, context):
        try:  # handle error if context isn't filebrowser (if operator is launched from search)
            folder = context.space_data.params.directory  # give the path, params.filename give the tail (file)
            openFolder(folder.decode())
        except:
            self.report({"WARNING"}, "仅在文件浏览器界面中有效")
        return {"FINISHED"}


class PATH_PT_top_filebrowser_ui(Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOLS"
    bl_category = "Bookmarks"
    bl_label = "Filebrowser"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        from bpy_extras.asset_utils import SpaceAssetInfo

        if SpaceAssetInfo.is_asset_browser_poll(context):
            return
        return context.region.alignment in {"LEFT", "RIGHT"}

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 1.3
        layout.scale_y = 1.3

        row = layout.row(align=True)
        if bpy.data.filepath:
            row.operator("path.paste_path", text="当前文件夹", icon="FILE_BLEND")

        row.operator("path.open_filepath", text="从外部打开", icon="FILE_FOLDER")


CLASSES = [
    PATH_OT_browser_to_blend_folder,
    PATH_OT_open_filepath_folder,
    PATH_PT_top_filebrowser_ui,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
