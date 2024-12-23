import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class PIE_Space_KEY(Operator):
    bl_idname = "pie.key_space"
    bl_label = get_pyfilename()
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ob_mode = get_ob_mode(context)
        ob_type = get_ob_type(context)
        ui_type = get_area_ui_type(context)
        # print(context.area.ui_type)
        # 3D视图
        if ui_type == "VIEW_3D":
            if context.object is not None:
                if ob_mode in ["OBJECT", "EDIT"]:
                    bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
                elif ob_mode in ["SCULPT", "WEIGHT_PAINT", "TEXTURE_PAINT", "VERTEX_PAINT"]:
                    bpy.ops.wm.tool_set_by_index(index=1)
            else:
                bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        # UV编辑器
        elif ui_type == "UV":
            bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        # 图像编辑器
        elif ui_type == "IMAGE_EDITOR":
            if bpy.context.space_data.ui_mode == "VIEW":
                bpy.ops.wm.tool_set_by_index(index=1)
            elif bpy.context.space_data.ui_mode == "MASK":
                bpy.ops.screen.animation_play("INVOKE_DEFAULT")
        elif ui_type in ["GeometryNodeTree", "ShaderNodeTree", "CompositorNodeTree"]:
            bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
            # elif bpy.context.space_data.ui_mode == 'PAINT':
            #     bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")
        # 动画类
        elif ui_type in [
            "SEQUENCE_EDITOR",
            "NODE_EDITOR",
            "CLIP_EDITOR",
            "DOPESHEET",
            "TIMELINE",
            "FCURVES",
            "DRIVERS",
            "NLA_EDITOR",
        ]:
            bpy.ops.screen.animation_play("INVOKE_DEFAULT")
        return {"FINISHED"}


CLASSES = [
    PIE_Space_KEY,
]


addon_keymaps = []

keymap_areas = [
    ("3D View", "VIEW_3D"),
    ("SequencerCommon", "SEQUENCE_EDITOR"),
    ("NLA Editor", "NLA_EDITOR"),
    ("Graph Editor", "GRAPH_EDITOR"),
    ("Dopesheet", "DOPESHEET_EDITOR"),
    ("UV Editor", "IMAGE_EDITOR"),
    ("Image", "IMAGE_EDITOR"),
    ("Node Editor", "NODE_EDITOR"),
]


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    # KEY:
    for area in keymap_areas:
        km = addon.keymaps.new(name=area[0], space_type=area[1])  # ----视频序列播放器
        kmi = km.keymap_items.new(PIE_Space_KEY.bl_idname, "SPACE", "CLICK")  # space
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("wm.search_menu", "SPACE", "DOUBLE_CLICK")  # 搜索栏
        addon_keymaps.append((km, kmi))

        if area[0] == "3D View" or "Node Editor":  # shift-space
            km.keymap_items.new("screen.animation_play", "SPACE", "CLICK", shift=True)
            addon_keymaps.append((km, kmi))
        else:
            kmi = km.keymap_items.new("screen.animation_play", "SPACE", "CLICK", shift=True)
            kmi.properties.reverse = True
            addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
