from ...module.reg import register_classes, unregister_classes
bl_info = {
    "name": "m4_tools_split",
    "author": "ah",
    "description": "ah",
    "blender": (4, 2, 0),
    "version": (1, 0, 0),
    "location": "3D View",
    "category": "Interface",
}

from pathlib import Path

import bpy

from .align import AlignEditMesh, AlignObjectToEdge, AlignObjectToVert, CenterEditMesh, Straighten
from .align_helper_npanel import ObjectAlignPanel
from .align_helper_op import AlignObject
from .align_helper_uv import AlignUV
from .focus_handler import delay_execution, manage_focus_HUD
from .icons import icon
from .material_pincker import PIE_MaterialPicker
from .mirror import Mirror

classes = [
    AlignUV,
    Mirror,
    AlignObject,
    CenterEditMesh,
    AlignObjectToEdge,
    AlignObjectToVert,
    Straighten,
    AlignEditMesh,
    ObjectAlignPanel,
    PIE_MaterialPicker,
]


@register_classes(classes)
def register():
    icon.register()
    delay_execution(manage_focus_HUD)


@unregister_classes(classes)
def unregister():
    icon.unregister()


if __name__ == "__main__":
    register()
