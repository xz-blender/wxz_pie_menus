import bpy
from bpy.types import Operator, Menu
from .utils import set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "Properties > Modifiers",
    "category": "BAR",
}


class Bar_Quick_Decimate(Operator):
    bl_idname = "bar.quick_decimate"
    bl_label = submoduname
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        return {"FINISHED"}


# Menus #
def menu(self, context):
    if context.active_object:
        if len(context.active_object.modifiers):
            col = self.layout.column(align=True)

            row = col.row(align=True)
            row.operator(ApplyAllModifiers.bl_idname, icon='IMPORT', text="Apply All")
            row.operator(DeleteAllModifiers.bl_idname, icon='X', text="Delete All")

            row = col.row(align=True)
            row.operator(
                ToggleApplyModifiersView.bl_idname, icon='RESTRICT_VIEW_OFF', text="Viewport Vis"
            )
            row.operator(
                ToggleAllShowExpanded.bl_idname, icon='FULLSCREEN_ENTER', text="Toggle Stack"
            )


classes = [
    Bar_Quick_Decimate,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.DATA_PT_modifiers.append(menu)  # 区别 prepend 和 append


def unregister():
    bpy.types.DATA_PT_modifiers.remove(menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
