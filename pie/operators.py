import bpy
from bpy.types import Operator

from ..utils import safe_register_class, safe_unregister_class


class Empty_Operator(Operator):
    bl_idname = "pie.empty_operator"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return {"CANCELLED"}


CLASSES = [
    Empty_Operator,
]


def register():
    safe_register_class(CLASSES)


def unregister():
    safe_unregister_class(CLASSES)
