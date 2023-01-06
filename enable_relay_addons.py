import bpy
from bpy.types import Operator

class Enable_Pie_Menu_Relay_Addons(Operator):
    bl_idname = "pie.enable_relay_addons"
    bl_label = "Enable Addons"
    bl_description = "一键打开常用内置插件"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        
        return {"FINISHED"}

