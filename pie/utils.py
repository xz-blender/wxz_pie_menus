import inspect
import json
from pathlib import Path

import addon_utils
import bpy

submoduname = Path(__file__).stem

rely_addons = [
    ("Edit Mesh Tools", "mesh_tools"),  # 0
    ("Straight Skeleton", "straight_skeleton"),  # 1
    ("LoopTools", "mesh_looptools"),  # 2
    ("Modifier Tools", "space_view3d_modifier_tools"),  # 3
    ("DPFR Distribute Objects", "distributeobjects"),  # 4
    ("SketchUp Importer", "sketchup_importer"),  # 5
    ("Atomic Data Manager", "atomic_data_manager"),  # 6
    ("EdgeFlow", "slide_edge"),  # 7
    ("Bend Face", "bend_face"),  # 8
    ("Face Cutter", "face_cutter"),  # 9
    ("Curve Tools", "curve_tools"),  # 10
    ("Import AutoCAD DXF Format (.dxf)", "io_import_dxf"),  # 11
    ("Export Autocad DXF Format (.dxf)", "io_export_dxf"),  # 12
]

# rely_addons.sort(key=lambda name: name[0])

addon_lists = []
for mod in addon_utils.modules():
    addon_lists.append(mod.bl_info.get("name"))


addons_dir = {}
for mod in addon_utils.modules():
    addons_dir[mod.bl_info.get("name")] = mod.__name__


def check_rely_addon(a_name, p_name):  # addon name & path name
    if a_name in addon_lists:
        if addon_utils.check(p_name)[0] == False:
            # return: (loaded_default, loaded_state) 元组
            return "0"  # 安装未启用
        else:
            return "1"  # 安装已启用
    else:
        return "2"  # 未安装


def set_pie_ridius(default_radius=100):
    bpy.context.preferences.view.pie_menu_radius = default_radius


def pie_op_check(pie, check_op, op_text):
    if check_op == "2":
        pie.operator("pie.empty_operator", text="未安装%s插件" % (op_text))
        return False
    elif check_op == "0":

        return False
    elif check_op == "1":
        return True


def pie_check_rely_addon_op(pie, addon_name):  # addon name & path name
    if addon_name in addon_lists:
        if addon_utils.check(addons_dir[addon_name])[0] == False:
            # return: (loaded_default, loaded_state) 元组
            pie.operator("pie.empty_operator", text="未启用%s插件" % (addon_name))
            return False  # 安装未启用
        else:
            return True  # 安装已启用
    else:
        pie.operator("pie.empty_operator", text="未安装%s插件" % (addon_name))
        return False  # 未安装


def operator_exists(idname):
    names = idname.split(".")
    # print(names)
    a = bpy.ops
    for prop in names:
        a = getattr(a, prop)
    try:
        name = a.__repr__()
    except Exception as e:
        # print(e)
        return False
    return True


def get_op_id_name_dic() -> dict:
    op_id_filepath = Path(__file__).parent / "operator_id.json"
    with open(op_id_filepath, "r") as file:
        data = json.load(file)
    # 转换数据结构
    new_dict = {}
    for key, value_list in data.items():
        for item in value_list:
            new_dict[item] = key
    return new_dict


def add_operator(pie, op_id, **kwargs):
    if operator_exists(op_id):
        pie.operator(op_id, **kwargs)
    else:
        op_dic = get_op_id_name_dic()
        if op_id in op_dic:
            pie.operator("pie.empty_operator", text=f"未开启 {op_dic[op_id]} 插件", icon="ERROR")
        else:
            pie.operator("pie.empty_operator", text=f"未找到 {op_id} 操作的插件", icon="QUESTION")


def get_ob_type(context, NoActive_else="MESH") -> str:
    ob_type: str = context.object.type if context.object else NoActive_else
    return ob_type


def get_ob_mode(context, NoActive_else="OBJECT") -> str:
    ob_mode: str = context.object.mode if context.object else NoActive_else
    return ob_mode


def get_area_ui_type(context):
    return context.area.ui_type


def get_pyfilename() -> str:  # 获取当前运行脚本的文件名
    # 获取当前堆栈帧，并回溯一层到调用者
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename  # 调用者文件的完整路径
    return Path(caller_filename).stem  # 提取文件名（不包含路径和扩展名）


def keymap_safe_unregister(addon_keymaps: list):
    from ..module.keymaps import unregister_owned
    unregister_owned(addon_keymaps)
