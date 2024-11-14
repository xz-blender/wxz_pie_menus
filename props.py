import importlib

import bpy
from bpy.props import *
from bpy.types import PropertyGroup

from .pie.Translate_key import enum_languages
from .utils import *


class WXZ_PIE_Prefs_Props:
    tabs: EnumProperty(
        items=(
            ("DEPENDENCIES", "依赖包", ""),
            ("ADDON_MENUS", "饼菜单&插件", ""),
            ("RESOURCE_CONFIG", "资源配置", ""),
            ("Other_Addons_Setting", "其他插件设置", ""),
        ),
        default="ADDON_MENUS",
    )  # type: ignore

    debug: BoolProperty(name="调试输出", default=True)  # type: ignore

    # 资源设置
    load_assets_library_presets: BoolProperty(name="加载资源库预设", default=False)  # type: ignore
    assets_library_path_sync: StringProperty(name="远程路径", subtype="DIR_PATH", default=get_sync_path())  # type: ignore
    assets_library_path_local: StringProperty(name="本地路径", subtype="DIR_PATH", default=get_local_path())  # type: ignore
    load_xz_keys_presets: BoolProperty(name="加载XZ快捷键预设", default=False)  # type: ignore
    load_xz_setting_presets: BoolProperty(name="加载XZ配置预设", default=False)  # type: ignore
    download_official_addons: BoolProperty(name="下载常用内置插件", default=False)  # type: ignore
    enable_addon_presets_items: BoolProperty(name="开启常用插件预设", default=False)  # type: ignore
    xz_download_offical_extensions: BoolProperty(name="安装常用官方插件", default=False)  # type: ignore
    xz_download_parts_extensions: BoolProperty(name="安装作者常用插件", default=False)  # type: ignore

    # 饼菜单面板
    pie_modules: CollectionProperty(type=PropertyGroup)  # type: ignore
    pie_modules_index: IntProperty()  # type: ignore
    other_modules: CollectionProperty(type=PropertyGroup)  # type: ignore
    other_modules_index: IntProperty()  # type: ignore
    setting_modules: CollectionProperty(type=PropertyGroup)  # type: ignore
    setting_modules_index: IntProperty()  # type: ignore
    # 依赖包面板
    pip_use_china_sources: BoolProperty(name="使用清华镜像源", default=True)  # type: ignore
    pip_modules_home: BoolProperty(default=False)  # type: ignore
    pip_user_flag: BoolProperty(default=True)  # type: ignore
    pip_advanced_toggle: BoolProperty(default=False)  # type: ignore
    pip_module_name: StringProperty()  # type: ignore
    default_pkg: EnumProperty(
        name="default package",
        description="本插件需要安装的第三方包",
        items=[
            # (identifier, pip_display_name, pip_import_name)
            ("PILLOW", "pillow", "PIL"),
            # ("OPENAI", "openai", "openai"),
            ("HTTPX", "httpx", "httpx"),
            # ("requests", "requests", "requests"),
            ("pyclipper", "pyclipper", "pyclipper"),
            ("pulp", "pulp", "pulp"),
            ("shapely", "shapely", "shapely"),
        ],
        default="PILLOW",
    )  # type: ignore

    ### 其他插件设置
    show_other_module_prop: BoolProperty(name="其他小工具设置")  # type: ignore
    modifier_profiling: BoolProperty(name="修改器-耗时统计面板", default=False)  # type: ignore
    change_overlay_and_shading_sets: BoolProperty(name="个性化更改视图着色", default=False)  # type: ignore
    force_AutoPackup_startup: BoolProperty(name="强制自动打包-启动时", default=True)  # type: ignore
    force_AutoPackup_presave: BoolProperty(name="强制自动打包-保存时", default=False)  # type: ignore
    AutoSwitch_ActiveCam_Default: BoolProperty(name="自动切换选择相机", default=False)  # type: ignore

    ## formula to nodes
    show_formula2nodes_submenu: BoolProperty(name="表达式转节点")  # type: ignore
    debug_prints: BoolProperty(name="调试输出", description="在终端中启用调试打印", default=False)  # type: ignore
    generate_previews: BoolProperty(name="生成逻辑预览树", description="在创建节点树之前生成节点树的预览", default=True)  # type: ignore
    from .parts_addons.formula_to_nodes import VariableSortMode

    sort_vars: EnumProperty(items=VariableSortMode, name="变量排序模式", description="对变量进行排序的顺序", default="INSERTION")  # type: ignore
    ## MeshMachine
    show_meshmachine_submenu: BoolProperty(name="MeshMachine-剥离版")  # type: ignore
    modal_hud_color: FloatVectorProperty(name="显示字体颜色", subtype="COLOR", default=[1, 1, 1], size=3, min=0, max=1)  # type: ignore
    modal_hud_scale: FloatProperty(name="显示图形缩放", default=1, min=0.5, max=10)  # type: ignore
    modal_hud_hints: BoolProperty(name="显示提示", default=True)  # type: ignore
    symmetrize_flick_distance: IntProperty(name="轻拂确认距离", default=75, min=20, max=1000)  # type: ignore
    ## language swith
    show_language_switch_submenu: BoolProperty(name="双语切换设置")  # type: ignore
    first_lang: EnumProperty(name="首选语言", default="zh_HANS", items=enum_languages)  # type: ignore
    second_lang: EnumProperty(name="次选语言", default="en_US", items=enum_languages)  # type: ignore
    ## 资产浏览器滚动放大缩小预览图
    show_asset_browser_scroll: BoolProperty(name="资产浏览器-滚轮缩放快捷键")  # type: ignore
    tby_bsr_multiplier_resize_factor: IntProperty(name="缩放因子", default=10)  # type: ignore
    ## M4功能合集
    show_m4_submenu: BoolProperty(name="M4功能")  # type: ignore
    focus_view_transition: BoolProperty(name="视口补间", default=True)  # type: ignore
    focus_lights: BoolProperty(name="忽略灯光（使它们始终可见）", default=False)  # type: ignore
    ah_show_text: BoolProperty(name="Show Button Text", default=True)  # type: ignore
    ## punch it
    show_punchit: BoolProperty(name="挤出流形插件")  # type: ignore
    push_default: IntProperty(name="推-默认值", description="将挤压扩大解决精度问题", default=1, min=0)  # type: ignore
    pull_default: IntProperty(name="拉-默认值", description="拉动最初选择的面并后退一点,解决精度问题", default=1, min=0)  # type: ignore
    non_manifold_extrude: BoolProperty(name="支持非流形网格", description="允许在非流形网格上进行拉伸", default=False)  # type: ignore
    modal_hud_timeout: FloatProperty(name="HUD 超时", description="HUD元素的持续时间", default=1, min=0.1, max=10)  # type: ignore


class PIE_HistoryObjectsCollection(bpy.types.PropertyGroup):
    name: StringProperty()  # type: ignore
    obj: PointerProperty(name="History Object", type=bpy.types.Object)  # type: ignore


class PIE_HistoryUnmirroredCollection(bpy.types.PropertyGroup):
    name: StringProperty()  # type: ignore
    obj: PointerProperty(name="History Unmirror", type=bpy.types.Object)  # type: ignore


class PIE_HistoryEpochCollection(bpy.types.PropertyGroup):
    name: StringProperty()  # type: ignore
    objects: CollectionProperty(type=PIE_HistoryObjectsCollection)  # type: ignore
    unmirrored: CollectionProperty(type=PIE_HistoryUnmirroredCollection)  # type: ignore


class M4_split_SceneProperties(bpy.types.PropertyGroup):
    align_mode: EnumProperty(
        name="Align Mode", items=[("VIEW", "View", ""), ("AXES", "Axes", "")], default="VIEW"
    )  # type: ignore
    focus_history: CollectionProperty(type=PIE_HistoryEpochCollection)  # type: ignore


class PIE_PIPOutput_LINE(bpy.types.PropertyGroup):
    line: StringProperty()  # type: ignore


class PIE_PIP_OutputItem(bpy.types.PropertyGroup):
    RETRUNCODE_OUTPUT: StringProperty(default="")  # type: ignore
    ERROR_OUTPUT: CollectionProperty(type=PIE_PIPOutput_LINE)  # type: ignore
    TEXT_OUTPUT: CollectionProperty(type=PIE_PIPOutput_LINE)  # type: ignore


CLASSES = [
    PIE_HistoryObjectsCollection,
    PIE_HistoryUnmirroredCollection,
    PIE_HistoryEpochCollection,
    M4_split_SceneProperties,
    PIE_PIPOutput_LINE,
    PIE_PIP_OutputItem,
]


def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)

    bpy.types.Scene.M4_split = PointerProperty(type=M4_split_SceneProperties)
    bpy.types.Scene.PIE_pip_output = PointerProperty(type=PIE_PIP_OutputItem)


def unregister():
    del bpy.types.Scene.M4_split
    del bpy.types.Scene.PIE_pip_output

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
