import addon_utils
import bpy

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "PIE",
}

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


def set_pie_ridius(context, radius=100):
    context.preferences.view.pie_menu_radius = radius


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


def change_default_keymap(keys_class, keys_idname, value_list, prop_list=None):
    keys_config = bpy.context.window_manager.keyconfigs.default.keymaps[keys_class].keymap_items

    keys_list = []

    stored_value_list = {}
    stored_prop_list = {}

    for keys_name, keys_bpy in keys_config.items():
        if keys_name == keys_idname:
            keys_list.append(keys_bpy)
    for keys in keys_list:
        for value in value_list:
            # ----stored----
            stored_value_list[keys] = [value[0], getattr(keys, value[0])]
            setattr(keys, value[0], value[1])
        if prop_list and prop_list is not None:
            for prop in prop_list:
                # ----stored----
                stored_prop_list[keys] = [prop[0], getattr(keys.properties, prop[0])]
                try:
                    setattr(keys.properties, prop[0], prop[1])
                except:
                    None
    keys_list.clear()
    return (stored_value_list, stored_prop_list)


def restored_default_keymap(stored_keys):
    stored_value_list = stored_keys[0]
    stored_prop_list = stored_keys[1]

    for value_bpy, value in stored_value_list.items():
        setattr(value_bpy, value[0], value[1])
    if len(stored_prop_list) is not None:
        for prop_bpy, prop in stored_prop_list.items():
            try:
                setattr(prop_bpy.properties, prop[0], prop[1])
            except:
                print("error:", prop_bpy, prop[0], prop[1])
    stored_value_list.clear()
    stored_prop_list.clear()
