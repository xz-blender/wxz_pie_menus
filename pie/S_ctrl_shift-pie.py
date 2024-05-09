import bpy
import os
from pathlib import Path
from bpy.types import Menu, Panel, Operator
from .utils import set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D",
    "category": "3D View",
}

class PIE_MT_S_ctrl_Shift(Menu):
    bl_idname = __qualname__
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        set_pie_ridius(context, 100)

        temp_path = [path for path in Path(bpy.app.tempdir).resolve().parents][:-3]
        file_path = bpy.data.filepath
        
        # 4 - LEFT
        try:
            pie.operator('rf.callpanel', text='打开附近文件', icon='FILE_TICK', emboss=True)
            if file_path and not any(Path(file_path).resolve().is_relative_to(folder) for folder in temp_path):
                pp = Path(str(file_path)).parent
                context.preferences.addons['Quick Files'].preferences['blends_path'] = str(pp)
                bpy.ops.rf.refreshfiles()
            else:
                context.preferences.addons['Quick Files'].preferences['blends_path'] = "该文件在缓存文件夹中！"
        except Exception as e:
            print(f"Error: {e}")
        # 6 - RIGHT
        pie.separator()
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
       

classes = [
    PIE_MT_S_ctrl_Shift,
]

addon_keymaps = []

def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'S', 'CLICK_DRAG', ctrl=True,shift=True)
    kmi.properties.name = "PIE_MT_S_ctrl_Shift"
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
