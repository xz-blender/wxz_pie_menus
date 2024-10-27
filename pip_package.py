# -*- coding: utf-8 -*-
import site
import subprocess
import sys
from pathlib import Path

import bpy
from bpy.types import Operator

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


global ERROR_OUTPUT
global TEXT_OUTPUT
ERROR_OUTPUT = []
TEXT_OUTPUT = []
RETRUNCODE_OUTPUT = []
RETRUNCODE_DICT = {
    0: "成功",
    1: "通用错误",
    2: "误用 shell 命令",
    126: "命令不可执行",
    127: "命令未找到",
    128: "无效的参数",
}


def run_pip_command(self, *cmds, cols=False, run_module="pip"):
    """使用user spec命令运行P IP进程"""
    global ERROR_OUTPUT
    global TEXT_OUTPUT

    cmds = [c for c in cmds if c is not None]

    command = [python_bin, "-m", run_module, *cmds]

    if get_prefs().pip_use_china_sources:
        command += ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]
    print("RUN_CMD:", command)
    output = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

    if get_prefs().debug:
        print(">>>------------ 错误 ------------")
        print(">>> 返回代码 :", output.returncode)
        print(">>> 输出信息 :", output.stdout)
        print(">>> STD信息 :", output.stderr)

    ERROR_OUTPUT = save_text(output.stderr)
    TEXT_OUTPUT = save_text(output.stdout, cols=cols)


def save_text(text, cols=False):
    """将输入文本字符串转换为2列的列表"""
    out = []
    for i in text.split("\n"):
        if len(i) <= 1:
            continue
        subs = i.split()
        parts = []
        if cols:
            for s in subs:
                parts.append(s)
        else:
            parts.append(" ".join(subs))
        out.append(parts)
    return out


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
    bl_label = "安装本插件需要的包"
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
        global TEXT_OUTPUT
        TEXT_OUTPUT = []
        global ERROR_OUTPUT
        ERROR_OUTPUT = []
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


classes = [
    PIE_OT_PIPInstall,
    PIE_OT_PIPInstall_Default,
    PIE_OT_PIPRemove,
    PIE_OT_ClearText,
    PIE_OT_PIPList,
    PIE_OT_EnsurePIP,
    PIE_OT_UpgradePIP,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    global ERROR_OUTPUT
    global TEXT_OUTPUT
    class_register()


def unregister():
    class_unregister()


if __name__ == "__main__":
    register()
