import os

import bpy
from bpy.types import AddonPreferences, Operator

from ..utils import get_addon_name

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


def modify_package(command, options, names):
    """
    通过pip安装或删除Python软件包
    """
    import subprocess
    import sys

    python_exe = sys.executable

    res = subprocess.call([python_exe, "-m", "ensurepip", "--upgrade"])
    if res > 0:
        return False
    # res = subprocess.call([python_exe, "-m", "pip", command, option, name])
    for name in names:
        res = subprocess.call(
            [python_exe, "-m", "pip", command] + options + [name] + ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple/"]
        )
        if res > 0:
            return False
    bpy.ops.pie.check_dependencies()
    return True


class DetectDependencies(Operator):
    """
    检查是否安装了所需的Python包
    """

    bl_idname = "pie.check_dependencies"
    bl_label = "检查依赖包"
    bl_description = "检查是否安装了所需的Python包"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        preferences = context.preferences.addons[get_addon_name()].preferences
        required_packages = ["pyclipper", "pillow", "openai", "httpx", "requests"]
        for package in required_packages:
            setattr(preferences, f"package_{package}", True)
            try:
                __import__(package)
            except ImportError:
                setattr(preferences, f"package_{package}", False)

        return {"FINISHED"}


class PIE_Install_Dependencies(Operator):
    bl_idname = "pie.dependencies_install"
    bl_label = "安装"
    bl_description = "通过pip管理软件包"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        packages = ["pyclipper", "pillow", "openai", "httpx", "requests"]
        res = modify_package("install", ["--no-input"], packages)
        if res:
            self.report({"INFO"}, "Python包安装成功")
        else:
            self.report({"ERROR"}, "无法安装所需的软件包")
        return {"FINISHED"}


class PIE_Remove_Dependencies(Operator):
    bl_idname = "pie.dependencies_remove"
    bl_label = "移除"
    bl_description = "通过pip管理软件包"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        packages = ["pyclipper", "pillow", "openai", "httpx", "requests"]
        res = modify_package("uninstall", ["-y"], packages)
        self.report({"INFO"}, "Blender需重启")
        return {"FINISHED"}


classes = [
    DetectDependencies,
    PIE_Install_Dependencies,
    PIE_Remove_Dependencies,
]


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except:
            print(__name__, "->", cls, " error")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
