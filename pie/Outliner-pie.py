import bpy
import os
from bpy.types import Menu, Panel, Operator
from .utils import set_pie_ridius, change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class OUTLINER_PIE_MT_Bottom_A(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        set_pie_ridius(context, 20)

        pie.operator(
            'outliner.show_one_level', icon='REMOVE', text=''
        ).open = False
        # 6 - RIGHT
        pie.operator('outliner.show_one_level', icon='ADD', text='')
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()

class Collection_Enable_Toggle(Operator):
    bl_idname = "pie.toggle_collection"
    bl_label = submoduname
    bl_options = {"REGISTER",'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        active = context.view_layer.active_layer_collection.exclude
        if active:
            bpy.ops.outliner.collection_exclude_set('INVOKE_DEFAULT')
        else:
            bpy.ops.outliner.collection_exclude_clear('INVOKE_DEFAULT')
        return {"FINISHED"}

classes = [
    OUTLINER_PIE_MT_Bottom_A,
    Collection_Enable_Toggle,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Outliner", space_type='OUTLINER')
    kmi = km.keymap_items.new("wm.call_menu_pie", 'A', 'CLICK_DRAG')
    kmi.properties.name = "OUTLINER_PIE_MT_Bottom_A"
    kmi = km.keymap_items.new("outliner.show_active", 'F', 'CLICK')
    # kmi = km.keymap_items.new("pie.toggle_collection", 'E', 'CLICK')
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()

    # global key2
    # key2 = change_default_keymap(
    #     'Outliner','outliner.collection_exclude_set',
    #     [('active',False)],
    #     )
    # global key3
    # key3 = change_default_keymap(
    #     'Outliner','collection_exclude_clear',
    #     [('active',False)],
    #     )

def unregister():

    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="OUTLINER_PIE_MT_Bottom_A")
