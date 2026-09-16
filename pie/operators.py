from ..module.reg import register_classes, unregister_classes
import bpy
from bpy.types import Operator



class Empty_Operator(Operator):
    bl_idname = "pie.empty_operator"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return {"CANCELLED"}


CLASSES = [
    Empty_Operator,
]


@register_classes(CLASSES)
def register():
    pass


@unregister_classes(CLASSES)
def unregister():
    pass
