import bpy
from bpy.types import Operator, Panel


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


classes = [
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


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
