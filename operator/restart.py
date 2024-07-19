import os
import subprocess

import bpy

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}


def restart_blender():
    """
    使用当前文件重新启动Blender.
    """
    blender_exe = bpy.app.binary_path
    file_path = bpy.data.filepath

    cmd = [blender_exe]
    if file_path:
        cmd.append(file_path)

    subprocess.Popen(cmd)
    bpy.ops.wm.quit_blender()


class SaveAndRestartOperator(bpy.types.Operator):
    """保存文件并重启Blender"""

    bl_idname = "wm.save_and_restart"
    bl_label = "保存并重启Blender"

    def execute(self, context):
        if bpy.data.is_saved:
            bpy.ops.wm.save_mainfile()
            restart_blender()
        else:
            bpy.ops.wm.save_as_mainfile("INVOKE_DEFAULT")
        return {"FINISHED"}


class RestartWithoutSavingOperator(bpy.types.Operator):
    """未保存文件，并重启Blender"""

    bl_idname = "wm.restart_without_saving"
    bl_label = "Restart without Saving"

    def execute(self, context):
        restart_blender()
        return {"FINISHED"}


class SaveBeforeRestartOperator(bpy.types.Operator):
    """运算符在重新启动前显示保存对话框"""

    bl_idname = "wm.save_before_restart"
    bl_label = "重启前，请保存！"

    action: bpy.props.EnumProperty(
        items=[
            ("SAVE_RESTART", "保存并重启", ""),
            ("RESTART", "不保存并重启", ""),
        ],
        name="Action",
    )  # type: ignore

    def execute(self, context):
        if self.action == "SAVE_RESTART":
            bpy.ops.wm.save_and_restart("INVOKE_DEFAULT")
        elif self.action == "RESTART":
            bpy.ops.wm.restart_without_saving()
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="重启Blender前，有未保存的更改！")
        layout.prop(self, "action", expand=True)


class RelaunchOperator(bpy.types.Operator):
    """Operator to restart Blender"""

    bl_idname = "wm.relaunch_blender"
    bl_label = "Restart"

    def execute(self, context):
        if bpy.data.is_dirty:
            bpy.ops.wm.save_before_restart("INVOKE_DEFAULT")
        else:
            restart_blender()
        return {"FINISHED"}


def menu_func(self, context):
    """Add the restart option to the File menu"""
    self.layout.operator(RelaunchOperator.bl_idname, text="重启", icon="HAND")


classes = [
    SaveAndRestartOperator,
    RestartWithoutSavingOperator,
    SaveBeforeRestartOperator,
    RelaunchOperator,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()
    bpy.types.TOPBAR_MT_file.append(menu_func)


def unregister():
    class_unregister()
    bpy.types.TOPBAR_MT_file.remove(menu_func)
