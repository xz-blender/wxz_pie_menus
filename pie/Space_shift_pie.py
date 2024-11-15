import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Space_KEY_shift(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        pie = self.layout.menu_pie()
        set_pie_ridius()
        scene = context.scene

        # 4 - LEFT
        pie.operator("screen.frame_jump", text="首帧", icon="REW").end = False
        # 6 - RIGHT
        pie.operator("screen.frame_jump", text="末帧", icon="FF").end = True
        # 2 - BOTTOM
        pie.operator("screen.keyframe_jump", text="下一关键帧", icon="NEXT_KEYFRAME").next = True
        # 8 - TOP
        pie.operator("screen.keyframe_jump", text="上一关键帧", icon="PREV_KEYFRAME").next = False
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        asfmytool = scene.asfmy_tool
        pie.prop(asfmytool, "asfmy_bool", text="仅播放一次")


CLASSES = [
    VIEW3D_PIE_MT_Space_KEY_shift,
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
]


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        "3D View",
        "Graph Editor",
        "Dopesheet",
        "NLA Editor",
        "Clip",
        "Node Editor",
        "Sequencer",
        "Screen",
    ]
    for area in space_name:
        km = addon.keymaps.new(name=area)
        kmi = km.keymap_items.new("wm.call_menu_pie", "SPACE", "CLICK_DRAG", shift=True)
        kmi.properties.name = "VIEW3D_PIE_MT_Space_KEY_shift"
        addon_keymaps.append((km, kmi))


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
