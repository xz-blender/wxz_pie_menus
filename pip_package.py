# -*- coding: utf-8 -*-
import site
import subprocess
import sys
from pathlib import Path

import bpy
from bpy.types import Operator

from .items import RETRUNCODE_DICT
from .utils import get_prefs

sys.stdout.reconfigure(encoding="utf-8")

MODULES_FOLDER = Path(bpy.utils.system_resource("SCRIPTS")) / "modules"
python_bin = sys.executable
print("python_bin:", python_bin)

app_path = site.getusersitepackages()
print("Blender PIP user site:", app_path)

if app_path not in sys.path:
    print("已添加用户模块包目录到 sys.path 路径中")
    sys.path.append(app_path)


def run_pip_command(self, *cmds, cols=False, run_module="pip"):
    """使用user spec命令运行P IP进程"""
    prefs = get_prefs()
    pip_output = bpy.context.scene.PIE_pip_output

    pip_output.RETRUNCODE_OUTPUT = ""
    pip_output.ERROR_OUTPUT.clear()
    pip_output.TEXT_OUTPUT.clear()

    cmds = [c for c in cmds if c is not None]
    command = [python_bin, "-m", run_module, *cmds]

    if prefs.pip_use_china_sources and run_module == "pip":
        command += ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]

    output = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

    pip_output.RETRUNCODE_OUTPUT = RETRUNCODE_DICT.get(output.returncode, "其他错误")
    for line in output.stderr.splitlines():
        if line.strip() == "":
            continue
        item = pip_output.ERROR_OUTPUT.add()
        item.line = line

    for line in output.stdout.splitlines():
        if line.strip() == "":
            continue
        item = pip_output.TEXT_OUTPUT.add()
        item.line = line

    if prefs.debug:
        print(">>> run_pip_command调试信息 <<<")
        print("RUN_CMD:", command)
        print(">>> 返回代码 :\n", output.returncode)
        print(">>> 输出信息 :\n", output.stdout)
        print(">>> STD信息 :\n", output.stderr)


class PIE_OT_PIPInstall(Operator):
    bl_idname = "pie.pip_install"
    bl_label = "安装"
    bl_description = "安装PIP包"

    def execute(self, context):
        chosen_path = "--user" if get_prefs().pip_user_flag else None
        run_pip_command(
            self,
            "install",
            *get_prefs().pip_module_name.split(" "),
            chosen_path,
        )
        return {"FINISHED"}


class PIE_OT_PIPInstall_Default(Operator):
    bl_idname = "pie.pip_install_default"
    bl_label = "一键安装本插件需要的包"
    bl_description = "安装本插件需要的PIP默认包"

    def execute(self, context):
        chosen_path = "--user" if get_prefs().pip_user_flag else None
        pkg = [p.name for p in get_prefs().bl_rna.properties["default_pkg"].enum_items]
        run_pip_command(
            self,
            "install",
            *pkg,
            chosen_path,
        )
        self.report({"INFO"}, "默认包已安装,需要重启Blender！")
        return {"FINISHED"}


class PIE_OT_PIPRemove(Operator):
    bl_idname = "pie.pip_remove"
    bl_label = "卸载(需重启)"
    bl_description = "移除PIP包"

    def execute(self, context):
        save_prop = get_prefs().pip_use_china_sources
        setattr(get_prefs(), "pip_use_china_sources", False)
        run_pip_command(self, "uninstall", *get_prefs().pip_module_name.split(" "), "-y")
        setattr(get_prefs(), "pip_use_china_sources", save_prop)
        return {"FINISHED"}


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
        run_pip_command(self, "list", cols=True)
        return {"FINISHED"}


class PIE_OT_EnsurePIP(Operator):
    bl_idname = "pie.ensure_pip"
    bl_label = "验证PIP程序"
    bl_description = "尝试确保PIP安装程序存在"

    def execute(self, context):
        pkg = [
            "-Xfrozen_modules=off",
        ]
        run_pip_command(self, "--default-pip", run_module="ensurepip")
        return {"FINISHED"}


class PIE_OT_UpgradePIP(Operator):
    bl_idname = "pie.upgrade_pip"
    bl_label = "升级PIP"
    bl_description = "升级PIP"

    def execute(self, context):
        run_pip_command(self, "install", "--upgrade", "pip")
        return {"FINISHED"}


CLASSES = [
    PIE_OT_PIPInstall,
    PIE_OT_PIPInstall_Default,
    PIE_OT_PIPRemove,
    PIE_OT_ClearText,
    PIE_OT_PIPList,
    PIE_OT_EnsurePIP,
    PIE_OT_UpgradePIP,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
