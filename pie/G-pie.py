import bpy
from bpy.types import Menu, Operator
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


class VIEW3D_PIE_MT_Bottom_G(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        if context.area.ui_type == 'VIEW_3D':

            ob_type = context.object.type
            ob_mode = context.object.mode

            set_pie_ridius(context, 100)

            get_orient = context.scene.transform_orientation_slots[0].type
            
            if ob_mode == 'OBJECT':
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                rotate_Y = pie.operator('transform.translate', text='Y',icon='EVENT_Y')
                rotate_Y.orient_type = get_orient
                rotate_Y.constraint_axis = (False,True,False)
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT
            elif ob_mode == 'EDIT':
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                # 2 - BOTTOM 
                # 8 - TOP
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT

        elif context.area.ui_type == 'UV':

            set_pie_ridius(context, 100)
            # 4 - LEFT
            # 6 - RIGHT
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT

            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


classes = [
    VIEW3D_PIE_MT_Bottom_G,
]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    
    space_name = [
        ('3D View', 'VIEW_3D'),
        ('UV Editor', 'IMAGE_EDITOR'),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new(
            idname='wm.call_menu_pie', type="G", value="CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_G"
        addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()

def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_G")
