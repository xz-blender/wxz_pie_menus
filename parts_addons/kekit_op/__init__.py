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

from .pie_axis_move import KeMouseAxisMove
from .pie_linear_array import KeLinearArray
from .pie_radial_instances import KeRadialInstances

classes = [
    KeMouseAxisMove,
    KeLinearArray,
    KeRadialInstances,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()


def unregister():
    class_unregister()
