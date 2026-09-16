from ...module.reg import register_classes, unregister_classes
import bpy
from bpy.props import BoolProperty, CollectionProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup



class PIP_Prefs_Props:
    use_china_mirror: BoolProperty(
        name="使用中国pip镜像源",
        default=True,
    )  # type: ignore
    install_custom_pip_packages: StringProperty(
        name="安装自定义pip包名称",
        default="",
    )  # type: ignore


class PIE_PIPOutput_LINE(PropertyGroup):
    line: StringProperty()  # type: ignore


class PIE_PIP_OutputItem(PropertyGroup):
    RETRUNCODE_OUTPUT: StringProperty(default="")  # type: ignore
    ERROR_OUTPUT: CollectionProperty(type=PIE_PIPOutput_LINE)  # type: ignore
    TEXT_OUTPUT: CollectionProperty(type=PIE_PIPOutput_LINE)  # type: ignore


CLASSES = [PIE_PIPOutput_LINE, PIE_PIP_OutputItem]


@register_classes(CLASSES)
def register():
    bpy.types.Scene.PIE_pip_output = PointerProperty(type=PIE_PIP_OutputItem)


@unregister_classes(CLASSES)
def unregister():
    del bpy.types.Scene.PIE_pip_output
