import bpy

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": "kekit_op",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D",
    "category": "3D View",
}

from .ke_vp_step_rotate import PIE_KeStepRotate
from .pie_axis_move import KeMouseAxisMove
from .pie_linear_array import KeLinearArray
from .pie_radial_instances import KeRadialInstances


def draw_extras(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.operator("outliner.show_active", icon="VIEWZOOM", text="")
    row.operator("outliner.show_one_level", icon="ZOOM_IN", text="")
    row.operator("outliner.show_one_level", icon="ZOOM_OUT", text="").open = False


classes = [
    KeMouseAxisMove,
    KeLinearArray,
    KeRadialInstances,
    PIE_KeStepRotate,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()
    bpy.types.OUTLINER_HT_header.append(draw_extras)


def unregister():
    class_unregister()
    bpy.types.OUTLINER_HT_header.remove(draw_extras)
