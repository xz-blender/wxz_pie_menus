bl_info = {
    "name": "MeshMachine-剥离版",
    "author": "wxz",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Mesh > Edit Mode",
    "description": "关于倒角的实用增强工具",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
}

import bpy

from .op_boolean_cleanup import PIE_BooleanCleanup
from .op_change_width import PIE_ChangeWidth
from .op_fuse import PIE_Fuse
from .op_offset_cut import PIE_OffsetCut
from .op_quad_corner import PIE_QuadCorner
from .op_refuse import PIE_Refuse
from .op_symmetrize import PIE_Symmetrize
from .op_turn_corner import PIE_TurnCorner
from .op_unbevel import PIE_Unbevel
from .op_unchamfer import PIE_Unchamfer
from .op_unfuck import PIE_Unfuck
from .op_unfuse import PIE_Unfuse


class MM_PT_SplitVersion(bpy.types.Panel):
    bl_idname = __qualname__
    bl_label = "MeshMachine-剥离版"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "mesh"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(PIE_OffsetCut.bl_idname)
        row = layout.row()
        row.operator(PIE_Unfuck.bl_idname)
        row = layout.row()
        row.operator(PIE_Fuse.bl_idname)
        row = layout.row()
        row.operator(PIE_ChangeWidth.bl_idname)
        row = layout.row()
        row.operator(PIE_Unfuse.bl_idname)
        row = layout.row()
        row.operator(PIE_Refuse.bl_idname)
        row = layout.row()
        row.operator(PIE_Unchamfer.bl_idname)
        row = layout.row()
        row.operator(PIE_Unbevel.bl_idname)
        row = layout.row()
        row.operator(PIE_TurnCorner.bl_idname)
        row = layout.row()
        row.operator(PIE_QuadCorner.bl_idname)
        row = layout.row()
        row.operator(PIE_BooleanCleanup.bl_idname)
        layout.separator()
        row = layout.row()
        row.operator(PIE_Symmetrize.bl_idname)


classes = [
    PIE_OffsetCut,
    PIE_Fuse,
    PIE_ChangeWidth,
    PIE_Unfuse,
    PIE_Refuse,
    PIE_Unchamfer,
    PIE_Unbevel,
    PIE_Unfuck,
    PIE_TurnCorner,
    PIE_QuadCorner,
    PIE_BooleanCleanup,
    PIE_Symmetrize,
    MM_PT_SplitVersion,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()


def unregister():
    class_unregister()


if __name__ == "__main__":
    register()
