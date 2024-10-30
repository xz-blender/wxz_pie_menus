import bpy
from bpy.types import Operator, Panel

from ..utils import safe_register_class, safe_unregister_class
from .utils import keymap_safe_unregister


class Window_Lock_View(Operator):
    bl_idname = "window.lock_view"
    bl_label = "Lock Window"
    bl_description = "Lock References Board window"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        for area in context.window.screen.areas:
            if area.type == "VIEW_3D":
                if (area.x <= event.mouse_x < area.x + area.width) and (area.y <= event.mouse_y < area.y + area.height):
                    if area != None:
                        area.spaces.active.region_3d.lock_rotation = not area.spaces.active.region_3d.lock_rotation

        return {"FINISHED"}


CLASSES = [
    Window_Lock_View,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(
        idname=Window_Lock_View.bl_idname,
        type="P",
        value="CLICK",
        shift=True,
        alt=True,
    )
    addon_keymaps.append(km)


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
