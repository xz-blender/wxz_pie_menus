import os
import time
from pathlib import Path

import addon_utils
import bpy
from bpy.types import Operator

from .utils import get_local_path, get_sync_path

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}

sync_path = get_sync_path()
local_path = get_local_path()


def change_addon_key_value(change_dir):
    bpy.context.preferences.view.use_translate_interface = False
    for dir_list in change_dir:
        keymaps = bpy.context.window_manager.keyconfigs["Blender addon"].keymaps
        for ks_name, ks_data in keymaps.items():
            if ks_name == dir_list[0][0]:
                list_keymaps = []
                for id_name, id_data in ks_data.keymap_items.items():
                    if id_name == dir_list[0][1] and id_data.name == dir_list[0][2]:
                        list_keymaps.append(id_data)
                for data in list_keymaps:
                    for value in dir_list[1]:
                        setattr(data, value[0], value[1])
                        # print(value[0], value[1])
                    if dir_list[2] != None:
                        for prop in dir_list[2]:
                            setattr(data.properties, prop[0], prop[1])
                list_keymaps.clear()
    bpy.context.preferences.view.use_translate_interface = True


addon_path = Path(bpy.utils.user_resource("SCRIPTS")) / "addons"


class Enable_Pie_Menu_Relay_Addons(Operator):
    bl_idname = "pie.enable_relay_addons"
    bl_label = "一次性打开多个常用插件,会非常耗时!"
    bl_description = "一键打开常用内置插件"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        # return self.execute(context)

    # def draw(self, context):
    #     layout = self.layout
    #     layout.label(text="一次性打开多个常用插件,会非常耗时!", icon="ERROR")

    def execute(self, context):
        addon_utils.modules_refresh()
        addons_list = []
        for mod in addon_utils.modules():
            addons_list.append(mod.__name__)

        user_path = bpy.utils.resource_path("USER")
        config_path = os.path.join(user_path, "config")

        join = os.path.join

        addons_officials_list = {
            #   addon_name : [[addon_settings],[addon_keys]]
            #### 官方插件&自带插件####
            "curve_tools": [[], []],
            "add_curve_extra_objects": [[], []],
            "curve_simplify": [[], []],
            "add_mesh_BoltFactory": [[], []],
            "add_mesh_extra_objects": [[], []],
            "development_edit_operator": [[], []],
            "development_icon_get": [[], []],
            "space_view3d_copy_attributes": [[], []],
            "materials_utils": [
                [],
                [(["3D View", "wm.call_menu", "Material Utilities"], [("value", "CLICK"), ("ctrl", True)], [])],
            ],
            "object_print3d_utils": [[], []],
            "mesh_f2": [[("ajustuv", True)], [(["Mesh", "mesh.f2", "Make Edge/Face"], [("value", "CLICK")], [])]],
            "mesh_looptools": [[], []],
            "mesh_snap_utilities_line": [[], []],
            "mesh_tiny_cad": [[], []],
            "node_presets": [[("search_path", join(sync_path, "Nodes Presets"))], []],  # addon path
            "node_wrangler": [[], []],
            "object_boolean_tools": [
                [],
                [(["Object Mode", "wm.call_menu", "Bool Tool"], [("value", "CLICK")], [])],
            ],  # key
            "magic_uv": [[], []],
            # 'io_import_images_as_planes':[[],[]],
            "space_view3d_modifier_tools": [[], []],
            "sun_position": [[], []],
            "object_edit_linked": [[], []],
            "mesh_tools": [[], []],
            "mesh_inset": [[], []],
            "io_import_dxf": [[], []],
            "io_export_dxf": [[], []],
            ####第三方####
            # ————资产类————
            # HDRI
            "hdri_maker": [
                [
                    ("addon_default_library", str(Path(local_path) / "HDRI MAKER LIBRARY" / "HDRI_MAKER_DEFAULT_LIB")),
                    ("addon_user_library", str(Path(local_path) / "HDRI MAKER LIBRARY" / "HDRI_MAKER_USER_LIB")),
                ],
                [],
            ],
            # Photographer
            "photographer": [
                [("hdri_lib_path", str(Path(sync_path) / "Custom HDRI"))],
                [(["3D View", "wm.call_menu_pie", "Photographer Camera Pie"], [("value", "CLICK_DRAG")], [])],
            ],
            # Object Asset Wizard
            "object_asset_wizard": [[("root", str(Path(sync_path) / "Blender Assets Wizard"))], []],
            # Vegtation
            "Vegetation": [[("assets_path", str(Path(local_path) / "vegetation"))], []],
            # Engon
            "engon": [
                [("auto_check_update", False)],
                [
                    (["Window", "engon.browser_toggle_area", "Toggle Engon Browser"], [("type", "BACK_SLASH")], []),
                ],
            ],
            "True-Assets": [
                [("ta_directory", str(Path(sync_path) / "True Assets"))],
                [(["3D View", "ta.saveassetsfromthisfile", "Mark Assets and Quit"], [("active", False)], [])],
            ],
            "BagaBatch": [
                [
                    ("render_exposition", -1),
                    ("render_resolution", 512),
                    ("sun_orientation", 30),
                    ("camera_orientation", 0),
                ],
                [],
            ],
            "memsaver_personal": [[], []],
            # ————导入导出————
            # sketchup 导入导出
            "sketchup_importer": [[], []],
            "RedHalo_M2B": [[], []],
            # Super IO
            "super_io": [
                [
                    ("force_unicode", True),
                    ("cpp_obj_importer", True),
                    ("cpp_obj_exporter", True),
                    ("extend_export_menu", True),
                ],
                [
                    (["3D View", "wm.super_import", "Super Import"], [("value", "CLICK")], []),
                    (["3D View", "wm.super_export", "Super Export"], [("value", "CLICK"), ("type", "E")], []),
                    (["Node Editor", "wm.super_import", "Super Import"], [("value", "CLICK")], []),
                    (["Node Editor", "wm.super_export", "Super Export"], [("value", "CLICK"), ("type", "E")], []),
                    (["Image Generic", "wm.super_export", "Super Export"], [("value", "CLICK"), ("type", "E")], []),
                    (["File Browser", "wm.super_import", "Super Import"], [("value", "CLICK")], []),
                    (["File Browser", "wm.super_export", "Super EXport"], [("value", "CLICK"), ("type", "E")], []),
                ],
            ],
            # ————建模工具————编辑模式————
            "EdgeFlow": [[], []],
            "slide_edge": [[], []],
            "straight_skeleton": [[], []],
            "face_cutter": [[], []],
            "bend_face": [[], []],
            "simple_bend": [[], []],
            "kushiro_tools": [[], []],
            "niche-loops": [[], []],
            "smart_loops_toolkit": [[], []],
            "Inset_Outset": [[], []],
            "NGon Loop Select": [
                [],
                [
                    # (['Mesh','ls.select','Loop Select'],[('value','CLICK')],[]),
                ],
            ],
            # ————建模工具————物体模式————
            "drop_it": [[], [(["3D View", "object.drop_it", "Drop It"], [("value", "CLICK")], [])]],
            "Bagapie": [
                [],
                [
                    (["3D View", "bagapie.duplicatelinkedgroup", "Duplicate Linked Group"], [("active", False)], []),
                    (["3D View", "bagapie.duplicategroup", "Duplicate Group"], [("active", False)], []),
                    (["3D View", "wm.call_menu_pie", "BagaPie GeoPack"], [("active", False)], []),
                ],
            ],  # key alt N
            "leafig": [[], []],
            "Text_input": [[], []],
            "distributeobjects": [[], []],
            "autoMaterial": [[], []],
            "Auto_Reload": [[("update_check_launch", False)], []],
            # ————生成类工具————
            "FenceMaker": [[], []],
            "PoleMaker": [[], []],
            "ocd_addon": [[], []],
            # ————界面工具————
            "simple-tabs": [[("startup_delay", 1)], []],  # 导入json设置
            "Synchronize Workspaces": [[], []],
            "viewport_timeline_scrub": [[], []],
            "Quick Files": [[("include subfolders", False)], []],
            # ————节点类工具————
            "BB_Nodes": [[], []],
            "ETK_core": [[], []],
            "Node Kit": [[("nodes_path", str(Path(sync_path) / "NodeKit"))], []],
            "node_pie": [[], [(["Node Editor", "wm.call_menu_pie", "Node pie"], [("value", "CLICK_DRAG")], [])]],
            "uber_compositor": [[], []],
            "b3dsdf": [[], []],
            "wxz_nodes_presets": [[], []],
            # ————UV编辑器————
            "TexTools": [[], []],
            "UvSquares": [[], []],
            # ————辣椒酱插件集————
            "popoti_align_helper": [[], []],
            "lattice_helper": [[], []],
        }

        addon_disable_list = [
            "io_anim_bvh",
            "io_mesh_ply",
            # 'mesh_f2',
        ]

        # ads_lis_dir = addons_officials_list.update(addons_thirds_list)
        # 打开插件并设置
        for addon_name, addon_change in addons_officials_list.items():
            if addon_name in addons_list:
                if addon_utils.check(addon_name)[0] == False:
                    #  # check addon is enabled
                    try:
                        bpy.ops.preferences.addon_enable(module=addon_name)
                        time.sleep(0.1)
                        bpy.ops.preferences.addon_refresh()
                        print(addon_name, "is enabled")
                    except:
                        print(addon_name, "is enable error")
                if addon_change[0]:
                    for pref_change in addon_change[0]:
                        setattr(context.preferences.addons[addon_name].preferences, pref_change[0], pref_change[1])
                if addon_change[1]:
                    change_addon_key_value(addon_change[1])
        # 关闭插件
        for disable in addon_disable_list:
            if disable in addons_list and addon_utils.check(disable)[0] == True:
                bpy.ops.preferences.addon_disable(module=disable)

        # 部分插件其他设置
        self.report({"INFO"}, "已开启预设插件")
        return {"FINISHED"}


def change_addons():
    bpy.context.preferences.filepaths.texture_directory = (
        str(Path(sync_path).parent.parent / "Texture") + os.sep
    ).replace("\\", "/")
    bpy.context.preferences.filepaths.font_directory = (str(Path(sync_path).parent.parent / "Fonts") + os.sep).replace(
        "\\", "/"
    )

    bpy.ops.pie.enable_relay_addons()
    print('"WXZ_Pie_Menu" Enable Relay Addons!')


def register():
    # try:
    bpy.utils.register_class(Enable_Pie_Menu_Relay_Addons)
    # except:
    #     pass
    if not bpy.app.timers.is_registered(change_addons):
        bpy.app.timers.register(change_addons, first_interval=5)


def unregister():
    if bpy.app.timers.is_registered(change_addons):
        bpy.app.timers.unregister(change_addons)

    bpy.utils.unregister_class(Enable_Pie_Menu_Relay_Addons)


if __name__ == "__main__":
    register()
