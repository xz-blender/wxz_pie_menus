import os
import bpy
import bpy.utils.previews
from bpy.types import Menu
from .utils import set_pie_ridius  # check_rely_addon, rely_addons,

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Interface",
}

preview_collections = {}
dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
pcoll = bpy.utils.previews.new()
for entry in os.scandir(dir):
    if entry.name.endswith(".png"):
        name = os.path.splitext(entry.name)[0].upper()
        pcoll.load(name, entry.path, "IMAGE")


class VIEW3D_PIE_MT_Bottom_Q(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        set_pie_ridius(context)

        # 4 - LEFT
        pie.operator(
            "view3d.view_axis", text="左", icon_value=pcoll["A4"].icon_id
        ).type = 'LEFT'
        # 6 - RIGHT
        pie.operator(
            "view3d.view_axis", text="右", icon_value=pcoll["A6"].icon_id
        ).type = 'RIGHT'
        # 2 - BOTTOM
        pie.operator("view3d.view_camera", text="摄像机", icon="VIEW_CAMERA")
        # 8 - TOP
        pie.operator(
            "view3d.view_axis", text="顶", icon_value=pcoll["A8"].icon_id
        ).type = 'TOP'
        # 7 - TOP - LEFT
        pie.operator(
            "view3d.view_axis", text="后", icon_value=pcoll["A7"].icon_id
        ).type = 'BACK'
        # 9 - TOP - RIGHT
        pie.operator(
            "view3d.view_axis", text="前", icon_value=pcoll["A9"].icon_id
        ).type = 'FRONT'
        # 1 - BOTTOM - LEFT
        pie.operator("view3d.view_all", text="全部")
        # 3 - BOTTOM - RIGHT
        pie.operator("view3d.view_selected", text="所选")


classes = [VIEW3D_PIE_MT_Bottom_Q]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'Q', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Q"
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

#     bpy.ops.wm.call_menu(name="PIE_MT_Bottom_Q_favorite")
