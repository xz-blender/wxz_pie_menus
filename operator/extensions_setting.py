import os
from pathlib import Path

from ..utils import *

join = os.path.join

sync_path = get_sync_path()
local_path = get_local_path()


system_extensions = {
    "node_wrangler": [[], []],
}
blender_org_extensions = {
    "curve_tools": [[], []],
    "extra_mesh_objects": [[], []],
    "extra_curve_objectes": [[], []],
    "simplify_curves_plus": [[], []],
    "boltfactory": [[], []],
    "edit_operator_source": [[], []],
    "icon_viewer": [[], []],
    "copy_attributes_menu": [[], []],
    "material_utilities": [
        [],
        [(["3D View", "wm.call_menu", "Material Utilities"], [("value", "CLICK"), ("ctrl", True)], [])],
    ],
    "print3d_toolbox": [[], []],
    "f2": [[("ajustuv", True)], [(["Mesh", "mesh.f2", "Make Edge/Face"], [("value", "CLICK")], [])]],
    "looptools": [[], []],
    "snap_utilities_line": [[], []],
    "tinycad_mesh_tools": [[], []],
    "node_presets": [[("search_path", join(sync_path, "Nodes Presets"))], []],  # addon path
    "bool_tool": [
        [],
        [(["Object Mode", "wm.call_menu", "Bool Tool"], [("value", "CLICK")], [])],
    ],
    "magic_uv": [[], []],
    "modifier_tools": [[], []],
    "sun_position": [[], []],
    "edit_linked_library": [[], []],
    "edit_mesh_tools": [[], []],
    "import_autocad_dxf_format_dxf": [[], []],
    "export_autocad_dxf_format_dxf": [[], []],
    "synchronize_workspaces": [[], []],
    "NodePie": [[], []],
    "improved_node_search": [[], []],
}
addons_officials_list = {
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
    # "True-Assets": [
    #     [("ta_directory", str(Path(sync_path) / "True Assets"))],
    #     [(["3D View", "ta.saveassetsfromthisfile", "Mark Assets and Quit"], [("active", False)], [])],
    # ],
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
    "NodeRelax": [[], []],
    "BB_Nodes": [[], []],
    "ETK_core": [[], []],
    "node_pie": [[], [(["Node Editor", "wm.call_menu_pie", "Node pie"], [("value", "CLICK_DRAG")], [])]],
    "uber_compositor": [[], []],
    "b3dsdf": [[], []],
    # ————UV编辑器————
    "TexTools": [[], []],
    "UvSquares": [[], []],
    # ————辣椒酱插件集————
    "popoti_align_helper": [[], []],
    "lattice_helper": [[], []],
}
