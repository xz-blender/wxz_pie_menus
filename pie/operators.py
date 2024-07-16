submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D",
    "category": "3D View",
}

import bpy
from bpy.types import Operator


class Empty_Operator(Operator):
    bl_idname = "pie.empty_operator"
    bl_label = ""

    def execute(self, context):
        return {"CANCELLED"}


classes = (Empty_Operator,)
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()


def unregister():
    class_unregister()
