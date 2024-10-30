SPACE_TYPE = ["VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR"]
SPACE_NAME_DIC = [
    # General
    ("3D_VIEW", "3D视图", ""),  # 0
    ("IMAGE_EDITOR", "图像编辑器", ""),  # 1
    ("UV", "UV编辑器", ""),  # 2
    ("CompositorNodeTree", "合成器", ""),  # 3
    ("TextureNodeTree", "纹理节点编辑器", ""),  # 4
    ("GeometryNodeTree", "几何节点编辑器", ""),  # 5
    ("ShaderNodeTree", "着色器编辑器", ""),  # 6
    ("SEQUENCE_EDITOR", "视频序列编辑器", ""),  # 7
    ("CLIP_EDITOR", "影片剪辑编辑器", ""),  # 8
    # Animation
    ("DOPESHEET", "动画摄影表", ""),  # 9
    ("TIMELINE", "时间线", ""),  # 10
    ("FCURVES", "曲线编辑器", ""),  # 11
    ("DRIVERS", "驱动器", ""),  # 12
    ("NLA_EDITOR", "非线性动画", ""),  # 13
    # Scripting
    ("TEXT_EDITOR", "文本编辑器", ""),  # 14
    ("CONSOLE", "Python 控制台", ""),  # 15
    ("INFO", "信息", ""),
    # Scripting
    ("OUTLINER", "大纲视图", ""),  # 16
    ("PROPERTIES", "属性", ""),  # 17
    ("FILES", "文件浏览器", ""),  # 18
    ("ASSETS", "资产浏览器", ""),  # 19
    ("SPREADSHEET", "电子表格", ""),  # 20
    ("PREFERENCES", "偏好设置", ""),  # 21
]

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
    "load_assets_library_presets",
    "load_xz_keys_presets",
    "load_xz_setting_presets",
]
