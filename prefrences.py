import bpy
from bpy.types import AddonPreferences, Menu, Operator, Panel, Preferences


class PIE_Preferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.box().row()
        row.lable("123145")


# classes = (PIE_Preferences,)


# def register():
#     for cls in classes:
#         bpy.utils.register_class(cls)


# def unregister():
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
