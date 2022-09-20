import bpy
import os
from bpy.types import Menu, Panel, Operator

# from . import check_rely_addon, rely_addons

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "PIE",
}


# class VIEW3D_PIE_MT_Bottom_Q_alt(Menu):
#     bl_label = __name__.split('.')[-1],

#     def draw(self, context):
#         layout = self.layout
#         layout.alignment = "CENTER"
#         pie = layout.menu_pie()

#         ob_type = context.object.type
#         ob_mode = context.object.mode

#         # addon1:"LoopTools"
#         addon1 = check_rely_addon(rely_addons[2][0], rely_addons[2][1])

#         # 4 - LEFT
#         # if addon1 == '1':
#         pie.separator()

#         # 6 - RIGHT

#         # 2 - BOTTOM

#         # 8 - TOP

#         # 7 - TOP - LEFT
#         # 9 - TOP - RIGHT
#         # 1 - BOTTOM - LEFT
#         # 3 - BOTTOM - RIGHT


class PIE_Bottom_Q_alt(Operator):
    bl_idname = "pie.q_alt_key"
    bl_label = submoduname
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.selected_objects:
            mode = context.object.mode
            if mode == 'OBJECT' or 'EDIT':
                bpy.ops.view3d.localview(frame_selected=False)
        else:
            self.report('INFO', '未选择物体')
        return {"FINISHED"}


classes = [
    PIE_Bottom_Q_alt,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(
        PIE_Bottom_Q_alt.bl_idname, 'Q', 'CLICK', alt=True
    )
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_E")
