from ..module.reg import register_classes, unregister_classes
import bpy
from bpy.types import Menu

from ..module.workspace_presets import (
    WORKSPACE_NAMES,
    PIE_Workspace_Import_Online_Operator,
    PIE_WorkspaceSwapOperator,
)
from .utils import *


class VIEW3D_PIE_MT_Ctrl_Tab(Menu):
    bl_label = "Tab-ctrl"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        # 4 - LEFT
        L = pie.operator("pie.workspaceswapper", text="UV", icon="UV_DATA")
        L.target_workspace = "4-UV"
        L.default_workspace = "UV Editing"
        # 6 - RIGHT
        R = pie.operator("pie.workspaceswapper", text="MOD", icon="CUBE")
        R.target_workspace = "1-MOD"
        R.default_workspace = "Modeling"
        # 2 - BOTTOM
        B = pie.operator("pie.workspaceswapper", text="MAT", icon="MATERIAL")
        B.target_workspace = "3-MAT"
        B.default_workspace = "Shading"
        # 8 - TOP
        box = pie.column(align=True)
        row = box.row()
        row.scale_y = 1.3
        T1 = row.operator("pie.workspaceswapper", text="SETTING", icon="SETTINGS")
        T1.target_workspace = "8-SETTING"
        T1.default_workspace = "Scripting"

        row = box.row(align=True)
        row.scale_y = 1.1
        split = row.split()
        T2_1 = split.operator("pie.workspaceswapper", text="LIB", icon="BOOKMARKS")
        T2_1.target_workspace = "0-LIB"
        T2_1.default_workspace = "Layout"
        split = row.split()
        T2_2 = split.operator("pie.workspaceswapper", text="COMPO", icon="NODE_COMPOSITING")
        T2_2.target_workspace = "7-COMPO"
        T2_2.default_workspace = "Compositing"

        row = box.row(align=True)
        row.scale_y = 1.1
        split = row.split()
        T3_1 = split.operator("pie.workspaceswapper", text="MOTION", icon="MOD_INSTANCE")
        T3_1.target_workspace = "5-MOTION"
        T3_1.default_workspace = "Animation"
        split = row.split()
        T3_2 = split.operator("pie.workspaceswapper", text="RENDER", icon="RENDER_STILL")
        T3_2.target_workspace = "6-RENDER"
        T3_2.default_workspace = "Rendering"
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        BR = pie.operator("pie.workspaceswapper", text="GN", icon="CUBE")
        BR.target_workspace = "2-GN"
        BR.default_workspace = "Geometry Nodes"


CLASSES = [
    VIEW3D_PIE_MT_Ctrl_Tab,
    PIE_WorkspaceSwapOperator,
    PIE_Workspace_Import_Online_Operator,
]


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    keymap_items = {
        "3D View": "VIEW_3D",
        "Node Editor": "NODE_EDITOR",
        "Image": "IMAGE_EDITOR",
        "Graph Editor": "GRAPH_EDITOR",
        "Window": "EMPTY",
    }
    for name, space in keymap_items.items():
        km = addon.keymaps.new(name=name, space_type=space)
        kmi = km.keymap_items.new(
            idname="wm.call_menu_pie",
            type="TAB",
            value="CLICK_DRAG",
            ctrl=True,
            shift=False,
            alt=False,
        )
        kmi.properties.name = "VIEW3D_PIE_MT_Ctrl_Tab"
        addon_keymaps.append((km, kmi))

    number_keys = ("ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT")

    km = addon.keymaps.new(name="Window")  # , space_type='EMPTY'
    for name, number in zip(WORKSPACE_NAMES, number_keys):
        kmi = km.keymap_items.new(
            idname=PIE_WorkspaceSwapOperator.bl_idname,
            type=number,
            value="PRESS",
            ctrl=False,
            shift=False,
            alt=True,
        )
        kmi.properties.target_workspace = name
        addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Window")
    kmi = km.keymap_items.new(
        idname=PIE_Workspace_Import_Online_Operator.bl_idname,
        type="NINE",
        value="PRESS",
        ctrl=False,
        shift=False,
        alt=True,
    )

    addon_keymaps.append((km, kmi))


@register_classes(CLASSES)
def register():
    register_keymaps()


@unregister_classes(CLASSES)
def unregister():
    keymap_safe_unregister(addon_keymaps)
