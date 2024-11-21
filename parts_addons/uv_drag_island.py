import bpy
from bpy.props import *

from ..pie.utils import keymap_safe_unregister
from ..utils import safe_register_class, safe_unregister_class

bl_info = {
    "name": "UV Drag Island",
    "author": "xz-blender",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "UV Editor",
    "description": "Quick Drag Move//Rotate Island",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UV",
}


class UVDRAG_OT_uv_Drag(bpy.types.Operator):
    bl_idname = "uvdrag.drag_island"
    bl_label = "快捷 移动 UV孤岛"
    bl_description = "Quick drag Move island"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        if context.scene.tool_settings.use_uv_select_sync is True:
            current_mode = tuple(context.tool_settings.mesh_select_mode)
            context.tool_settings.mesh_select_mode = (False, False, True)  # Face
            bpy.ops.uv.select_all(action="DESELECT")
            bpy.ops.uv.select_linked_pick("INVOKE_DEFAULT")
            bpy.ops.transform.translate("INVOKE_DEFAULT")
            context.tool_settings.mesh_select_mode = current_mode
            return {"FINISHED"}
        else:
            bpy.ops.uv.select_all(action="DESELECT")
            bpy.ops.uv.select_linked_pick("INVOKE_DEFAULT")
            bpy.ops.transform.translate("INVOKE_DEFAULT")
            return {"FINISHED"}


class UVDRAG_OT_uv_Rotate(bpy.types.Operator):
    bl_idname = "uvdrag.drag_rotate_island"
    bl_label = "快捷 旋转 UV孤岛"
    bl_description = "Quick drag Rotate island"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        if context.scene.tool_settings.use_uv_select_sync is True:
            current_mode = tuple(context.tool_settings.mesh_select_mode)
            context.tool_settings.mesh_select_mode = (False, False, True)  # Face
            bpy.ops.uv.select_all(action="DESELECT")
            bpy.ops.uv.select_linked_pick("INVOKE_DEFAULT")
            bpy.ops.transform.rotate("INVOKE_DEFAULT")
            context.tool_settings.mesh_select_mode = current_mode
            return {"FINISHED"}
        else:
            bpy.ops.uv.select_all(action="DESELECT")
            bpy.ops.uv.select_linked_pick("INVOKE_DEFAULT")
            bpy.ops.transform.rotate("INVOKE_DEFAULT")
            return {"FINISHED"}


classes = (
    UVDRAG_OT_uv_Drag,
    UVDRAG_OT_uv_Rotate,
)

addon_keymaps = []


def add_hotkey():
    kc = bpy.context.window_manager.keyconfigs.addon

    km = kc.keymaps.new(name="UV Editor", space_type="EMPTY")
    kmi = km.keymap_items.new("uvdrag.drag_island", "LEFTMOUSE", "ANY", alt=True, shift=True)
    kmi.active = True
    addon_keymaps.append((km, kmi))

    km = kc.keymaps.new(name="UV Editor", space_type="EMPTY")
    kmi = km.keymap_items.new("uvdrag.drag_rotate_island", "LEFTMOUSE", "ANY", ctrl=True, alt=True)
    kmi.active = True
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(classes)
    add_hotkey()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(classes)
