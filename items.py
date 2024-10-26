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
