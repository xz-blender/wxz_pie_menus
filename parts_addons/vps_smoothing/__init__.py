bl_info = {
    "name": "Volume Preserving Smoothing",
    "description": "Volume preserving Smoothing",
    "author": "Bartosz Styperek",
    "version": (2, 7, 0),
    "blender": (3, 6, 0),
    "location": "In Mesh Edit Mode: W-key -> Volume Smooth. Or use Volume Smooth tool from left tool sidebar ",
    "warning": "",
    "tracker_url": "https://discord.gg/cxZDbqH",
    "Category": "Mesh",
}

import bpy
import bpy.utils

from .smooth_tool import *
from .volume_preserve_smoothing import *


def smooth_menu_last(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VPS_MT_SmoothMenu")


classes = [
    VPS_OT_VolSmooth,
    VPS_OT_InflateSmooth,
    VPS_OT_lc_Smooth,
    VPS_MT_SmoothMenu,
    # ToolVpsSmooting,
    MyCustomShapeWidget,
    BrushCircleGizmoGroup,
    VPS_OT_DrawSmooth,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vps_gizmo_show = bpy.props.BoolProperty(default=True)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(smooth_menu_last)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(smooth_menu_last)
    try:
        bpy.utils.register_tool(ToolVpsSmooting, after={"builtin.smooth"}, separator=True, group=True)
    except:
        pass


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(smooth_menu_last)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(smooth_menu_last)
    del bpy.types.Scene.vps_gizmo_show

    try:
        bpy.utils.unregister_tool(ToolVpsSmooting)
    except:
        pass
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
