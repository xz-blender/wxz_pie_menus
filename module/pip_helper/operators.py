from ...module.reg import register_classes, unregister_classes
# -*- coding: utf-8 -*-
from bpy.types import Operator

from ...utils import get_prefs
from .commands import run_pip_command
from .manifest import PIP_Packeges_Dict


class PIE_OT_PIPInstall(Operator):
    bl_idname = "pie.pip_install"
    bl_label = "安装"
    bl_description = "安装PIP包"

    def execute(self, context):
        prefs = get_prefs()
        returncode = run_pip_command(
            "install",
            *prefs.install_custom_pip_packages.split(),
            use_china_mirror=prefs.use_china_mirror,
            debug=prefs.debug,
        )
        return {"FINISHED"} if returncode == 0 else {"CANCELLED"}


class PIE_OT_PIPInstall_Default(Operator):
    bl_idname = "pie.pip_install_default"
    bl_label = "一键安装本插件需要的包"
    bl_description = "安装本插件需要的PIP默认包"

    def execute(self, context):
        prefs = get_prefs()
        returncode = run_pip_command(
            "install",
            *PIP_Packeges_Dict,
            use_china_mirror=prefs.use_china_mirror,
            debug=prefs.debug,
        )
        if returncode != 0:
            self.report({"ERROR"}, "默认包安装失败，请查看输出信息")
            return {"CANCELLED"}
        self.report({"INFO"}, "默认包已安装,需要重启Blender！")
        return {"FINISHED"}


class PIE_OT_PIPRemove(Operator):
    bl_idname = "pie.pip_remove"
    bl_label = "卸载(需重启)"
    bl_description = "移除PIP包"

    def execute(self, context):
        prefs = get_prefs()
        returncode = run_pip_command("uninstall", *prefs.install_custom_pip_packages.split(), "-y", debug=prefs.debug)
        return {"FINISHED"} if returncode == 0 else {"CANCELLED"}


class PIE_OT_ClearText(Operator):
    bl_idname = "pie.pip_cleartext"
    bl_label = "清除文本"
    bl_description = "清除输出的文本"

    def execute(self, context):
        pip_output = context.scene.PIE_pip_output
        pip_output.RETRUNCODE_OUTPUT = ""
        pip_output.TEXT_OUTPUT.clear()
        pip_output.ERROR_OUTPUT.clear()
        return {"FINISHED"}


class PIE_OT_PIPList(Operator):
    bl_idname = "pie.pip_show_list"
    bl_label = "列出已安装包"
    bl_description = "列出已安装的PIP软件包"

    def execute(self, context):
        returncode = run_pip_command("list", debug=get_prefs().debug)
        return {"FINISHED"} if returncode == 0 else {"CANCELLED"}


class PIE_OT_EnsurePIP(Operator):
    bl_idname = "pie.ensure_pip"
    bl_label = "验证PIP程序"
    bl_description = "尝试确保PIP安装程序存在"

    def execute(self, context):
        returncode = run_pip_command("--default-pip", run_module="ensurepip", debug=get_prefs().debug)
        return {"FINISHED"} if returncode == 0 else {"CANCELLED"}


class PIE_OT_UpgradePIP(Operator):
    bl_idname = "pie.upgrade_pip"
    bl_label = "升级PIP"
    bl_description = "升级PIP"

    def execute(self, context):
        prefs = get_prefs()
        returncode = run_pip_command(
            "install", "--upgrade", "pip", use_china_mirror=prefs.use_china_mirror, debug=prefs.debug
        )
        return {"FINISHED"} if returncode == 0 else {"CANCELLED"}


CLASSES = [
    PIE_OT_PIPInstall,
    PIE_OT_PIPInstall_Default,
    PIE_OT_PIPRemove,
    PIE_OT_ClearText,
    PIE_OT_PIPList,
    PIE_OT_EnsurePIP,
    PIE_OT_UpgradePIP,
]


@register_classes(CLASSES)
def register():
    pass


@unregister_classes(CLASSES)
def unregister():
    pass
