import bpy
import rna_keymap_ui
from bpy.types import UIList

from ..module.lifecycle_blender import draw_module_item
from ..module.reg import register_classes, unregister_classes
from ..utils import get_prefs


def prefs_show_sub_panel(self, layout, show_prop, prop_name=""):
    # AddonPreferences may not support IDProperties; use registered RNA properties.
    attr = getattr(self, show_prop)
    # 创建 UI 布局
    col = layout.box().column()
    col.scale_y = 1.1
    col.use_property_split = False
    name: str = prop_name if prop_name != "" else show_prop
    col.prop(self, show_prop, text=name, icon="TRIA_DOWN" if attr else "TRIA_RIGHT")

    return (attr, col)


class PIE_UL_pie_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        draw_module_item(layout, data, item)


class PIE_UL_other_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        draw_module_item(layout, data, item)


class PIE_UL_setting_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        draw_module_item(layout, data, item)


def draw_addon_menus(self, layout, context, module_path_name_list):
    layout.label(text="内置饼菜单 & 内置插件开关")
    top_row = layout.row()
    draw_pie_modules(self, top_row, module_path_name_list)

    # box = layout.row().box()
    # box.label(text="饼菜单快捷键配置:")
    # col = box.column()
    # from ..items import All_Pie_keymaps

    # kc = bpy.context.window_manager.keyconfigs.addon

    # for km, kmi in All_Pie_keymaps:
    #     col.context_pointer_set("keymap", km)
    #     km = kc.keymaps.get(km.name)
    #     if km:
    #         try:
    #             kmi = km.keymap_items.get(kmi.idname, get_kmi_operator_properties(kmi))
    #             if kmi:
    #                 rna_keymap_ui.draw_kmi(["ADDON", "DEFAULT"], kc, km, kmi, col, 0)
    #         except:
    #             pass

    # for km, kmi in All_Pie_keymaps:
    #     km = km.active()
    #     col.context_pointer_set("keymap", km)
    #     try:
    #         rna_keymap_ui.draw_kmi([], kc, kc.keymaps.get(km.name), kmi, col, 0)
    #     except:
    #         pass


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
    text = "这会严重更改您的软件设置!请备份配置!(重启自动运行)"
    if get_prefs().debug:
        row = split.row()
        row.label(text=text, icon="ERROR")
        row = split.row()
        row.operator("pie.one_click_enable_all_presets", text="一键启用")
    else:
        row.label(text=text, icon="ERROR")

    box = layout.column()
    split_main_factor = 0.7

    row = box.row().box().row()
    text = "加载插件 - 常用外部插件预设 -- (自动下载安装)"
    if self.download_official_addons:
        split = row.split(factor=split_main_factor)
        row_sp = split.row()
        row_sp.prop(self, "download_official_addons", text=text)
        row_sp = split.row()
        row_sp.operator("pie.set_all_addons_presets", text="应用插件设置")

        row = box.row().box()

        main_split = row.split(factor=split_main_factor)
        row = main_split.row(align=True)
        row.operator("pie.enable_relay_addons", text="内置插件").ex_dirs = "sys_ex"
        row.operator("pie.enable_relay_addons", text="安装所需插件（官方源）").ex_dirs = "org_ex"
        row.operator("pie.enable_relay_addons", text="作者预设").ex_dirs = "third_ex"
        row = main_split.row()
        row.operator("pie.open_custom_xz_presets_file_in_new_window", text="编辑列表").path_name = "Addons"
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
        box_r_split_col.operator("pie.open_custom_xz_presets_file_in_new_window", text="编辑路径").path_name = "Assets"

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
    sep_deffac = 0.4

    attr, col = prefs_show_sub_panel(self, layout, "show_quick_crease_weight", "快速折痕 / 倒角权重")
    if attr:
        if not self.use_E_pie:
            col.label(text="请在饼菜单列表中启用 E_pie 以使用此工具", icon="INFO")
        self.quick_crease_weight.draw_settings(col, bpy.context)

    # 实用小工具设置
    attr, col = prefs_show_sub_panel(self, layout, "show_other_module_prop", "其他小工具设置")
    if attr:
        box = col.box()
        col = box.column(align=True)
        row = col.row().box().row()
        row.label(text="强制自动打包资源:")
        row.prop(self, "force_AutoPackup_startup", text="启动时")
        row.prop(self, "force_AutoPackup_presave", text="保存时")
        row.separator(factor=sep_deffac)
        row = col.row().box().row()
        row.prop(self, "modifier_profiling", text="显示修改器耗时")
        row.prop(self, "change_overlay_and_shading_sets")
        row.prop(self, "AutoSwitch_ActiveCam_Default")

    # 表达式转节点
    attr, col = prefs_show_sub_panel(self, layout, "show_formula2nodes_submenu", "表达式转节点")
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
    attr, col = prefs_show_sub_panel(self, layout, "show_meshmachine_submenu", "MeshMachine-剥离版")
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
    attr, col = prefs_show_sub_panel(self, layout, "show_language_switch_submenu", "双语切换设置")
    if attr:
        box = col.box()
        col = box.column(align=True)
        col.label(text="双语切换设置:设置不同的两种语言以供切换", icon="SETTINGS")
        row = col.row(align=True)
        row.prop(self, "first_lang")
        row.separator()
        row.prop(self, "second_lang")
    # 资产浏览器缩略图缩放快捷键
    attr, col = prefs_show_sub_panel(self, layout, "show_asset_browser_scroll", "资产浏览器-滚轮缩放快捷键")
    if attr:
        box = col.box()
        col = box.column(align=True)
        row = col.row()
        row.prop(self, "tby_bsr_multiplier_resize_factor")

    # MACHIN4 功能集合
    attr, col = prefs_show_sub_panel(self, layout, "show_MACHIN4_tools", "MACHIN4 功能集合")
    if attr:
        box = col.box()
        col = box.column(align=True)

        row = col.row().box()
        row.label(text="Punch It 设置")
        row = row.row()
        row.prop(self, "push_default")
        row.prop(self, "pull_default")
        row = row.row()
        row.prop(self, "non_manifold_extrude")
        row.prop(self, "modal_hud_timeout")

        row = col.row().box()
        row.label(text="对齐插件设置")
        row = row.row()
        row.prop(self, "show_text", text="POPOTI对齐助手")

    # 拖动UV孤岛快捷键设置
    attr, col = prefs_show_sub_panel(self, layout, "show_drag_uv_island", "拖动UV孤岛快捷键设置")
    if attr:
        box = col.box()
        col = box.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        from ..parts_addons.uv_drag_island import addon_keymaps

        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


CLASSES = [
    PIE_UL_pie_modules,
    PIE_UL_other_modules,
    PIE_UL_setting_modules,
]


@register_classes(CLASSES)
def register():
    pass


@unregister_classes(CLASSES)
def unregister():
    pass
