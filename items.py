packup_main_exclude_list = [
    "__pycache__",
    "README.md",
    "LISENCE",
    ".vscode",
    ".genaiscript",
    ".gitignore",
    ".git",
]
packup_split_exclude_list = [
    "__pycache__",
    "blender_assets.cats.txt~",
    "blends_savetime.txt",
]
packup_split_file_list = [
    "ui_font.ttf",
    "workspace.blend",
    "workspace_online.blend",
]
packup_split_folder_list = [
    "nodes_presets",
    "parts_addons",
]

handler_on_default_blender_list = ["load_pre", "load_factory_startup_post", "load_post"]
handler_on_depsgraph = ["depsgraph_update_post"]
handlers_Force_AutoPackup = ["load_factory_startup_post", "save_pre"]

view3d_handlder_sets = [
    ("overlay", "show_stats", True),
    ("overlay", "show_light_colors", True),
    ("overlay", "show_floor", False),
    ("overlay", "show_ortho_grid", False),
    ("shading", "show_cavity", True),
    ("shading", "cavity_type", "BOTH"),
]

RETRUNCODE_DICT = {
    0: "成功",
    1: "通用错误",
    2: "误用 shell 命令",
    126: "命令不可执行",
    127: "命令未找到",
    128: "无效的参数",
}

oneclick_enable_preset_prop_list = [
    # "download_official_addons",
    "load_assets_library_presets",
    "load_xz_keys_presets",
    "load_xz_setting_presets",
]
