import bpy
from bpy.app.handlers import persistent

from ..items import *
from ..utils import addon_name, get_prefs, manage_app_handlers

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}


#### def ####
def change_key_value(A_dir, value):
    for space_type in A_dir:
        s_idname = space_type.lower().replace(" ", "_").replace("_editor", "").replace("_mode", "") + ".select_all"

        keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
        for ks_name, ks_data in keymaps.items():
            if ks_name == space_type:
                list_keymaps = []
                for id_name, id_data in ks_data.keymap_items.items():
                    if id_name == s_idname and id_data.value != "DOUBLE_CLICK":
                        list_keymaps.append(id_data)
                for data in list_keymaps:
                    data.value = value
                list_keymaps.clear()


def change_key_value_base(change_dir):
    # 访问快捷键的名称会因翻译而改变,先改变为英文状态
    bpy.context.preferences.view.use_translate_interface = False
    # stored_value_list = {}
    # stored_prop_list = {}
    for dir_list in change_dir:
        keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
        for ks_name, ks_data in keymaps.items():
            if ks_name == dir_list[0][0]:
                list_keymaps = []
                for id_name, id_data in ks_data.keymap_items.items():
                    if id_name == dir_list[0][1]:
                        if id_data.name == dir_list[0][2]:
                            list_keymaps.append(id_data)
                        else:
                            None
                            # print('Not found ',dir_list[0][1],'in',dir_list[0][0],'|name:',dir_list[0][2])
                for data in list_keymaps:
                    for value in dir_list[1]:
                        # stored_value_list[data] = [value[0],getattr(data, value[0])]
                        setattr(data, value[0], value[1])
                    if dir_list[2] != None:
                        for prop in dir_list[2]:
                            # stored_prop_list[data] = [prop[0],getattr(data.properties, prop[0])]
                            try:
                                setattr(data.properties, prop[0], prop[1])
                            except:
                                print(data.name, "--keys_prop_error-->", prop[0], ":", prop[1])
                list_keymaps.clear()
    # 更改完之后切换回中文翻译
    bpy.context.preferences.view.use_translate_interface = True
    # return (stored_value_list, stored_prop_list)


# 其他键位设置
def change_keys_value():
    keys = bpy.context.window_manager.keyconfigs.default.keymaps
    for keys_name, keys_data in keys.items():
        if keys_name in ["Object Mode", "Mesh", "Curve", "Curves", "Pose", "Armatrue", "Littice"]:
            for key_name, key_data in keys_data.keymap_items.items():
                if key_data.name == "Move" and key_name == "transform.translate":
                    if key_data.type == "G":
                        key_data.value = "CLICK"
        elif keys_name == "Window":
            for key_name, key_data in keys_data.keymap_items.items():
                if (
                    key_name == "wm.save_mainfile"
                    and key_data.name == "Save Blender File"
                    and key_data.type == "S"
                    and key_data.ctrl == True
                    and key_data.alt == True
                ):
                    key_data.active = False
        elif keys_name == "Object Mode" or "Pose":
            for key_name, key_data in keys_data.keymap_items.items():
                if key_name == "object.hide_collection" and key_data.type != "H":
                    key_data.active = False


A_select_dir = [
    "Pose",
    "Object Mode",
    "Curve",
    "Mesh",
    "UV Editor",
    "NLA Editor",
    "Outliner" "Clip Editor",
    "Node Editor",
    "Graph Editor",
    "Sequencer",
    "Armature",
    "Metaball",
    "Lattice",
    "Particle",
    "Sculpt Curves",
]

A_dir = [
    (["3D View", "transform.skin_resize", "Skin Resize"], [("value", "CLICK")], []),  # ctrl A - mesh
    (["Object Mode", "wm.call_menu", "Apply"], [("value", "CLICK")], []),  # ctrl A - object
    (["Object Mode", "wm.call_menu", "Add"], [("value", "CLICK")], []),  # shift A - object
    (["Mesh", "wm.call_menu", "Mesh"], [("value", "CLICK")], []),  # shift A - mesh
]
B_dir = [
    (["3D View", "view3d.select_box", "Box Select"], [("active", False)], []),
    (["3D View", "view3d.clip_border", "Clipping Region"], [("active", False)], []),
    (["3D View", "view3d.zoom_border", "Zoom to Border"], [("active", False)], []),
    (["UV Editor", "uv.select_box", "Box Select"], [("active", False)], []),
    (["Node Editor", "node.select_box", "Box Select"], [("active", False)], []),
    (["Node Editor", "node.viewer_border", "Viewer Region"], [("active", False)], []),
    (["Node Editor", "node.clear_viewer_border", "Clear Viewer Region"], [("active", False)], []),
    (["Outliner", "outliner.select_box", "Box Select"], [("active", False)], []),
    (["NLA Editor", "nla.select_box", "Box Select"], [("active", False)], []),
    (["Mesh", "mesh.bevel", "Bevel"], [("value", "CLICK")], []),
    (["3D View", "view3d.render_border", "Set Render Region"], [("value", "CLICK")], []),
    (["Object Mode", "object.hide_collection", "Hide Collection"], [("active", False)], []),
]
Brush_dir = [
    (["Sculpt", "wm.call_menu_pie", "Mask Edit"], [("value", "CLICK_DRAG")], []),  # A
]
C_dir = [
    (["3D View", "view3d.select_circle", "Circle Select"], [("active", False)], []),
    (["UV Editor", "uv.select_circle", "Circle Select"], [("active", False)], []),
    (["Graph Editor", "graph.select_circle", "Circle Select"], [("active", False)], []),
    (["Node Editor", "node.select_circle", "Circle Select"], [("active", False)], []),
    (["3D View", "view3d.copybuffer", "Copy Objects"], [("value", "CLICK")], []),  # ctrl C
]
D_dir = [
    (["Mesh", "ls.select", "Loop Select"], [("active", False)], []),
]
E_dir = [
    (["Curve", "curve.extrude_move", "Extrude Curve and Move"], [("value", "CLICK")], []),
    (["Mesh", "view3d.edit_mesh_extrude_move_normal", "Extrude and Move on Normals"], [("value", "CLICK")], []),
    (["Mesh", "transform.edge_crease", "Edge Crease"], [("active", False)], []),  # shift E
    (["Graph Editor", "transform.transform", "Transform"], [("value", "CLICK")], []),
    (["Armature", "armature.extrude_move", "Extrude"], [("value", "CLICK")], []),
]
F_dir = [
    (["Curve", "curve.make_segment", "Make Segment"], [("value", "CLICK")], []),
    (["Mesh", "mesh.edge_face_add", "Make Edge/Face"], [("value", "DOUBLE_CLICK")], []),  # config[Blender addon]
    (["Mesh", "mesh.f2", "Make Edge/Face"], [("value", "CLICK")], []),
    (["Mesh", "mesh.edge_face_add", "Make Edge/Face"], [("value", "CLICK")], []),
    (["Mesh", "mesh.fill", "Fill"], [("value", "CLICK")], []),  # default fill
    (["Mesh", "wm.call_menu", "Face"], [("value", "CLICK")], []),  # ctrl F
    (["Node Editor", "node.link_make", "Make Links"], [("value", "CLICK")], []),  # ctrl F
]
G_dir = [
    (
        ["Object Mode", "collection.objects_add_active", "Add Selected to Active Collection"],
        [("active", False)],
        [],
    ),  # G ctrl shift
    (
        ["Object Mode", "collection.objects_remove_all", "Remove from All Collections"],
        [("active", False)],
        [],
    ),  # G ctrl shift alt
    (["Object Mode", "collection.objects_remove", "Remove from Collection"], [("active", False)], []),  # G ctrl alt
    (["Object Mode", "collection.create", "Create New Collection"], [("active", False)], []),  # G ctrl
    (["Object Mode", "object.select_grouped", "Select Grouped"], [("active", False)], []),  # Shift G - Object
    (["Mesh", "wm.call_menu", "Select Similar"], [("active", False)], []),  # Shift G - Mesh
]
H_dir = [
    (["Outliner", "outliner.hide", "Hide"], [("type", "B")], []),
    (["Outliner", "outliner.unhide_all", "Unhide All"], [("type", "B")], []),
    (["Object Mode", "object.hide_view_clear", "Show Hidden Objects"], [("type", "B")], []),
    (["Object Mode", "object.hide_view_set", "Hide Objects"], [("type", "B")], []),
    (["Object Mode", "object.hide_collection", "Hide Collection"], [("type", "B")], []),
    (["Curve", "curve.reveal", "Reveal Hidden"], [("type", "B")], []),
    (["Curve", "curve.hide", "Hide Selected"], [("type", "B")], []),
    (["Curve", "wm.call_menu", "Hooks"], [("type", "B")], []),
    (["Sculpt", "sculpt.face_set_change_visibility", "Face Sets Visibility"], [("type", "B")], []),
    (["Mesh", "mesh.reveal", "Reveal Hidden"], [("type", "B")], []),
    (["Mesh", "mesh.hide", "Hide Selected"], [("type", "B")], []),
    (["Mesh", "wm.call_menu", "Hooks"], [("type", "B")], []),
    (["Lattice", "wm.call_menu", "Hooks"], [("type", "B")], []),
    (["Armature", "armature.reveal", "Reveal Hidden"], [("type", "B")], []),
    (["Armature", "armature.hide", "Hide Selected"], [("type", "B")], []),
    (["Metaball", "mball.reveal_metaelems", "Reveal Hidden"], [("type", "B")], []),
    (["Metaball", "mball.hide_metaelems", "Hide Selected"], [("type", "B")], []),
    (["UV Editor", "uv.reveal", "Reveal Hidden"], [("type", "B")], []),
    (["UV Editor", "uv.hide", "Hide Selected"], [("type", "B")], []),
    (["Graph Editor Generic", "graph.reveal", "Reveal Curves"], [("type", "B")], []),
    (["Graph Editor Generic", "graph.hide", "Hide Selected"], [("type", "B")], []),
    (["Node Editor", "node.hide_toggle", "Hide"], [("type", "B")], []),
    (["Node Editor", "node.preview_toggle", "Toggle Node Preview"], [("type", "B")], []),
    (["Node Editor", "node.hide_socket_toggle", "Toggle Hidden Node Sockets"], [("type", "B")], []),
    (["NLA Editor", "nla.mute_toggle", "Toggle Muting"], [("type", "B")], []),
    (["Mesh", "wm.call_menu", "Hooks"], [("active", False), ("type", "H")], []),
]
M_dir = [
    (["Object Mode", "object.move_to_collection", "Move to Collection"], [("value", "CLICK")], []),
]
Outliner_dir = [
    (["Outliner", "outliner.select_all", "Toggle Selected"], [("active", False)], []),  # A
    (["Outliner", "outliner.collection_exclude_set", "Disable from View Layer"], [("value", "CLICK")], []),  # E
    (["Outliner", "outliner.collection_exclude_clear", "Enable in View Layer"], [("value", "CLICK")], []),  # alt E
    (["Outliner", "outliner.collection_new", "New Collection"], [("value", "CLICK")], []),  # C
    (["Outliner", "outliner.delete", "Delete"], [("value", "CLICK")], []),  # X
]
Q_dir = [
    (["Window", "wm.call_menu", "Quick Favorites"], [("active", False)], []),  # Q
    (["Window", "wm.quit_blender", "Quit Blender"], [("active", False)], []),  # ctrl Q
    # (['Object Non-modal','object.transfer_mode','Transfer Mode'],[('active',False)],[]), # alt Q  和 alt w 设置冲突
    (["Screen", "screen.region_quadview", "Toggle Quad View"], [("active", False)], []),  # ctrl alt Q - 四窗格
    # (['Screen','screen.region_quadview','Toggle Quad View'],[('value',"CLICK")],[]), # ctrl alt Q - 四窗格
]
R_dir = [
    (["3D View", "transform.rotate", "Rotate"], [("value", "CLICK")], []),
    (["Object Mode", "transform.rotate", "Rotate"], [("value", "CLICK")], []),
    (["Mesh", "transform.rotate", "Rotate"], [("value", "CLICK")], []),
    (["Curve", "transform.rotate", "Rotate"], [("value", "CLICK")], []),
    (["UV Editor", "transform.rotate", "Rotate"], [("value", "CLICK")], []),
    (["Node Editor", "transform.rotate", "Rotate"], [("value", "CLICK")], []),
    (["Screen", "screen.repeat_last", "Repeat Last"], [("value", "CLICK")], []),
]
S_dir = [
    (["Window", "wm.save_mainfile", "Save Blender File"], [("value", "CLICK")], []),  # ctrl S -- save file
    (["Window", "wm.save_as_mainfile", "Save As"], [("value", "CLICK")], []),  # ctrl shift S -- save file
    (["3D View", "transform.resize", "Resize"], [("value", "CLICK")], []),
    (["Object Mode", "transform.resize", "Resize"], [("value", "CLICK")], []),
    (["Mesh", "transform.resize", "Resize"], [("value", "CLICK")], []),
    (["Curve", "transform.resize", "Resize"], [("value", "CLICK")], []),
    (["UV Editor", "transform.resize", "Resize"], [("value", "CLICK")], []),
    (["Graph Editor", "transform.resize", "Resize"], [("value", "CLICK")], []),
    (["Node Editor", "transform.resize", "Resize"], [("value", "CLICK")], []),
]
SPACE_dir = [
    (["Window", "wm.toolbar", "Toolbar"], [("active", False)], []),  # shift space
    (["Window", "wm.search_menu", "Search Menu"], [("type", "SPACE"), ("value", "DOUBLE_CLICK")], []),  # search
    (["Frames", "screen.animation_play", "Play Animation"], [("active", False)], []),  # space
]
T_dir = [
    (["3D View Generic", "wm.context_toggle", "Context Toggle"], [("value", "CLICK")], []),
    (["Image Generic", "wm.context_toggle", "Context Toggle"], [("value", "CLICK")], []),
    (["Node Generic", "wm.context_toggle", "Context Toggle"], [("value", "CLICK")], []),
]
TAB_dir = [
    (["Object Non-modal", "object.mode_set", "Set Object Mode"], [("value", "CLICK")], []),
    (
        ["Object Non-modal", "view3d.object_mode_pie_or_toggle", "Object Mode Menu"],
        [("value", "CLICK_DRAG"), ("type", "TAB"), ("ctrl", False)],
        [],
    ),
    (["Node Editor", "wm.call_menu", "Edit Group"], [("value", "CLICK")], []),
    (["UV Editor", "wm.call_menu", "UV Select Mode"], [("value", "CLICK")], []),
    (["Screen", "screen.space_context_cycle", "Cycle Space Context"], [("active", False)], []),
]
U_dir = [
    (["Mesh", "wm.call_menu", "UV Mapping"], [("value", "CLICK")], []),
    (["UV Editor", "wm.call_menu", "Unwrap"], [("value", "CLICK")], []),
]
V_dir = [
    (["Curve", "curve.handle_type_set", "Set Handle Type"], [("value", "CLICK")], []),  # V
    (["Mesh", "mesh.rip_move", "Rip"], [("value", "CLICK")], []),  # V
    (["UV Editor", "uv.stitch", "Stitch"], [("value", "CLICK")], []),  # alt V
    (["UV Editor", "uv.rip_move", "UV Rip Move"], [("value", "CLICK")], []),
    (["3D View", "view3d.pastebuffer", "Paste Objects"], [("value", "CLICK")], []),  # ctrl V
    (["3D View", "object.fl_paste_in_place", "Paste in place"], [("active", False)], []),  # ctrl shift V
]
W_dir = [
    (["3D View", "wm.tool_set_by_id", "Set Tool by Name"], [("active", False)], []),  # W
    (["Window", "wm.toolbar_fallback_pie", "Fallback Tool Pie Menu"], [("value", "CLICK_DRAG")], []),  # alt W Pie
    (
        ["Object Non-modal", "object.transfer_mode", "Transfer Mode"],
        [("type", "W"), ("value", "CLICK")],
        [],
    ),  # alt W Pie
]
X_dir = [
    (["Object Mode", "object.delete", "Delete"], [("value", "CLICK")], [("use_global", False), ("confirm", False)]),
    (["Mesh", "wm.call_menu", "Delete"], [("active", False)], []),
    (["Curve", "wm.call_menu", "Delete"], [("active", False)], []),
    (["Outliner", "outliner.delete", "Delete"], [("value", "CLICK")], []),
    (["Graph Editor", "wm.call_menu", "Delete"], [("value", "CLICK")], []),
    (["Node Editor", "node.delete", "Delete"], [("value", "CLICK")], []),
]
Z_dir = [
    (["3D View", "wm.call_menu_pie", "Shading"], [("value", "CLICK")], []),  # Z
    (["3D View", "view3d.toggle_shading", "Toggle Shading Type"], [("active", False)], []),  # shift Z
]
Text_dir = [
    (["Text", "text.move_lines", "Move Lines"], [("shift", False), ("ctrl", False), ("alt", True)], []),
]
Others_dir = [
    (["Curves", "curves.disable_selection", "CURVES_OT_disable_selection"], [("active", False)], []),
    (["Window", "curves.disable_selection", "Toggle engon Browser"], [("type", "BACK_SLASH")], []),  # engon
]


class PIE_Load_XZ_Keys_Presets(bpy.types.Operator):
    bl_idname = "pie.load_xz_keys_presets"
    bl_label = "更改为xz的快捷键预设"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        change_key_value(A_select_dir, "CLICK")

        for _dir in [
            A_dir,
            B_dir,
            Brush_dir,
            C_dir,
            D_dir,
            E_dir,
            F_dir,
            G_dir,
            H_dir,
            Outliner_dir,
            Q_dir,
            R_dir,
            S_dir,
            SPACE_dir,
            T_dir,
            TAB_dir,
            U_dir,
            V_dir,
            W_dir,
            X_dir,
            Z_dir,
            Text_dir,
        ]:
            change_key_value_base(_dir)

        # 其他键位设置
        change_keys_value()
        print(f"{addon_name()} 已更改快捷键!!")

        return {"FINISHED"}


@persistent
def run_set_load_xz_keys_presets(dummy):
    if get_prefs().load_xz_keys_presets:
        bpy.ops.pie.load_xz_keys_presets()


def register():
    bpy.utils.register_class(PIE_Load_XZ_Keys_Presets)
    manage_app_handlers(handler_on_default_blender_list, run_set_load_xz_keys_presets)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, run_set_load_xz_keys_presets, True)
    bpy.utils.unregister_class(PIE_Load_XZ_Keys_Presets)


# def register():
#     if not bpy.app.timers.is_registered(changes_keys):
#         bpy.app.timers.register(changes_keys, first_interval=1)


# def unregister():
#     if bpy.app.timers.is_registered(changes_keys):
#         bpy.app.timers.unregister(changes_keys)


if __name__ == "__main__":
    register()
