import bpy
from bpy.types import Operator

from .utils import get_prefs


class Empty_Operator(Operator):
    bl_idname = "pie.empty_operator"
    bl_label = ""

    def execute(self, context):
        return {"CANCELLED"}


operators_classes = (Empty_Operator,)
