import bpy
from bpy.types import UIList

from .utils import *


class PIE_UL_pie_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod_name = item.name
        row = layout.row()
        row.label(text=mod_name)
        row.prop(data, "use_" + mod_name, text="")


class PIE_UL_other_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod_name = item.name
        row = layout.row()
        row.label(text=mod_name)
        row.prop(data, "use_" + mod_name, text="")


class PIE_UL_setting_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod_name = item.name
        row = layout.row()
        row.label(text=mod_name)
        row.prop(data, "use_" + mod_name, text="")


def draw_dependencies(self, layout):
    prefs = get_prefs()
    pip_output = bpy.context.scene.PIE_pip_output
    output: bool = any([pip_output.TEXT_OUTPUT, pip_output.ERROR_OUTPUT, pip_output.RETRUNCODE_OUTPUT])
    main_sp_fac = 0.65
    layout.label(text="依赖包设置")

    # ---
    layout = self.layout
    row = layout.box().row()
    split = row.split(factor=main_sp_fac)

    row = split.row()

    sub_split = row.split(factor=0.7)
    row = sub_split.row()
    row.prop(self, "pip_user_flag", text="本地Py路径")
    row.prop(self, "pip_use_china_sources", text="清华镜像源")
    row = sub_split.row()
    row.prop(self, "debug")

    row = split.row()
    row.operator("pie.pip_install_default")
    # ---
    layout = self.layout.box()

    row = layout.row()
    split = row.split(factor=main_sp_fac)
    row_l = split.row()
    row_l.operator("pie.ensure_pip")
    row_r = split.row(align=True)
    row_r.operator("pie.upgrade_pip")
    row_r.operator("pie.pip_show_list")

    row = layout.row(align=True)
    split = row.split(factor=main_sp_fac)
    split.scale_y = 1.4
    row_l = split.row()
    split_l = row_l.split(factor=0.4, align=True)
    row_ll = split_l.row()
    row_ll.label(text="输入包名(空格分割):")
    row_lr = split_l.row()
    row_lr.prop(self, "pip_module_name", text="")
    row_r = split.row(align=True)
    row_r.operator("pie.pip_install")
    row_r.operator("pie.pip_remove")

    row = layout.row(align=True)
    for item in self.bl_rna.properties["default_pkg"].enum_items:
        box = row.box()
        try:
            __import__(item.description)
            icon = "CHECKMARK"
        except ImportError:
            icon = "PANEL_CLOSE"
        box.label(text=item.name, icon=icon)

    # ---
    row = layout.row()
    row.label(text="最后一次输出:", icon="CONSOLE")
    if output:
        row = layout.row()
        row.operator("pie.pip_cleartext", text="清除文本")

        row = layout.row()
        box = row.box().column(align=True)

        if pip_output.RETRUNCODE_OUTPUT:
            row = box.row().box()
            row.label(text=f"执行结果:   {pip_output.RETRUNCODE_OUTPUT}")

        box.separator()

        if pip_output.TEXT_OUTPUT:
            row = box.row().box().column(align=True)
            row.label(text="输出结果:")
            for item in pip_output.TEXT_OUTPUT:
                # row = box.row()
                col = row.column()
                col.label(text=item.line)

        box.separator()

        if pip_output.ERROR_OUTPUT and prefs.debug:
            row = box.row().box().column(align=True)
            row.label(text="错误信息:")
            for item in pip_output.ERROR_OUTPUT:
                # row = box.row()
                col = row.column()
                col.label(text=item.line)


def draw_addon_menus(self, layout, context, module_path_name_list):
    layout.label(text="内置饼菜单 & 内置插件开关")
    top_row = layout.row()
    draw_pie_modules(self, top_row, module_path_name_list)


def draw_pie_modules(self, top_row, module_path_name_list):
    for lable_name, module_name in {
        "已启用饼菜单:": "pie",
        "已启用内置插件:": "parts_addons",
        "已应用设置:": "operator",
    }.items():
        split = top_row.split()
        box = split.box()
        sub_row = box.row()
        sub_row.alignment = "CENTER"
        sub_row.label(text=lable_name)
        sub_row = box.row()
        column = sub_row.column()

        name = module_path_name_list[module_name].split("_")[0]
        # print(module_name, "__________", name)
        column.template_list(
            f"PIE_UL_{name}_modules", "", self, f"{name}_modules", self, f"{name}_modules_index", rows=8
        )


def draw_resource_config(self, layout):
    row = layout.row()
    split = row.split(factor=0.8)
    row = split.row()
    row.label(text="这会严重更改您的软件设置!请备份配置!(重启自动运行)", icon="ERROR")
    row = split.row()
    row.operator("pie.one_click_enable_all_presets", text="一键启用")

    box = layout.column()
    split_main_factor = 0.7

    row = box.row().box()
    text = "加载插件 - 常用外部插件预设 -- (自动下载安装)"
    if self.download_official_addons:
        row.prop(self, "download_official_addons", text=text)

        main_split = row.split(factor=split_main_factor)
        row = main_split.row(align=True)
        row.operator("pie.enable_relay_addons", text="手动执行")
        row.operator("pie.enable_relay_addons", text="手动执行")
        row = main_split.row()
        row.operator("pie.open_custom_xz_presets_file_in_new_window", text="编辑插件列表").path_name = "Addons"
    else:
        row.prop(self, "download_official_addons", text=text)

    row = box.row().box()
    text = "加载预设 - 资源库路径 -- (会增加许多对您无用的资产路径!)"
    if not self.load_assets_library_presets:
        row.prop(self, "load_assets_library_presets", text=text)
    else:
        row.prop(self, "load_assets_library_presets", text=text)
        split = row.split(factor=split_main_factor)
        box_l = split.column(align=True)
        box_l.prop(self, "assets_library_path_sync")
        box_l.separator(factor=0.5)
        box_l.prop(self, "assets_library_path_local")
        box_r = split.column(align=True)
        box_r_split = box_r.split(factor=0.5)
        row = box_r_split.row()
        row.operator("pie.change_assets_library_path", text="手动执行")
        row.scale_y = 2.15
        box_r_split_col = box_r_split.column(align=True)
        box_r_split_col.scale_y = 1.075
        box_r_split_col.operator("pie.change_assets_library_path", text="移除路径").remove = True
        box_r_split_col.operator("pie.open_custom_xz_presets_file_in_new_window", text="打开文件").path_name = "Assets"

    row = box.row().box()
    text = "加载预设 - 快捷键 -- (请备份好您的快捷键!)"
    if self.load_xz_keys_presets:
        split = row.column().split(factor=split_main_factor)
        split.prop(self, "load_xz_keys_presets", text=text)
        split.alignment = "RIGHT"
        split.operator("pie.load_xz_keys_presets", text="手动执行")
    else:

        row.prop(self, "load_xz_keys_presets", text=text)

    row = box.row().box()
    text = "加载预设 - 通用设置 -- (请备份好您的userpref.blend文件!)"
    if self.load_xz_setting_presets:
        split = row.column().split(factor=split_main_factor)
        split.prop(self, "load_xz_setting_presets", text=text)
        split.alignment = "RIGHT"
        split.operator("pie.load_xz_setting_presets", text="手动执行")
    else:
        row.prop(self, "load_xz_setting_presets", text=text)


def draw_other_addons_setting(self, layout):
    layout.label(text="其他插件设置")
    layout = self.layout.column(align=False)

    # 实用小工具设置
    attr, col = prefs_show_sub_panel(self, layout, "show_other_module_prop")
    if attr:
        box = col.box()
        col = box.column(align=True)
        row = col.row()
        row.prop(self, "modifier_profiling")
        row.prop(self, "change_overlay_and_shading_sets")

    # 表达式转节点
    attr, col = prefs_show_sub_panel(self, layout, "show_formula2nodes_submenu")
    if attr:
        box = col.box()
        box.label(text="检查键映射设置以编辑激活。默认为Ctrl+M")
        row = box.row(align=True)
        row.prop(self, "debug_prints")
        row.prop(self, "generate_previews")
        row = box.row()
        row.label(text="变量排序依据...")
        row.prop(self, "sort_vars", expand=True)

    # meshmachine剥离版
    attr, col = prefs_show_sub_panel(self, layout, "show_meshmachine_submenu")
    if attr:
        box = col.box()
        col = box.column(align=True)
        row = col.row()
        row.prop(self, "modal_hud_color")
        row.prop(self, "modal_hud_scale")
        row = col.row()
        row.prop(self, "modal_hud_hints")
        row.prop(self, "symmetrize_flick_distance")
    # 双语切换设置
    attr, col = prefs_show_sub_panel(self, layout, "show_language_switch_submenu")
    if attr:
        box = col.box()
        col = box.column(align=True)
        col.label(text="双语切换设置:设置不同的两种语言以供切换", icon="SETTINGS")
        row = col.row(align=True)
        row.prop(self, "first_lang")
        row.separator()
        row.prop(self, "second_lang")
    # 资产浏览器缩略图缩放快捷键
    attr, col = prefs_show_sub_panel(self, layout, "show_asset_browser_scroll")
    if attr:
        box = col.box()
        col = box.column(align=True)
        row = col.row()
        row.prop(self, "tby_bsr_multiplier_resize_factor")

    # 挤出流形插件
    attr, col = prefs_show_sub_panel(self, layout, "show_punchit")
    if attr:
        box = col.box()
        col = box.column(align=True)
        row = col.row()
        row.prop(self, "push_default")
        row.prop(self, "pull_default")
        row = col.row()
        row.prop(self, "non_manifold_extrude")
        row.prop(self, "modal_hud_timeout")


CLASSES = [
    PIE_UL_pie_modules,
    PIE_UL_other_modules,
    PIE_UL_setting_modules,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
