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
from .align_helper_panel import PanelM4A1tools
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
    # PanelM4A1tools,
    PIE_MaterialPicker,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()
    icon.register()
    delay_execution(manage_focus_HUD)
    # register_keymaps()


def unregister():
    class_unregister()
    # unregister_keymaps()
    icon.unregister()


if __name__ == "__main__":
    register()
