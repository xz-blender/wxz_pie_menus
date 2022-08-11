import bpy
import os
from bpy.types import Menu, Panel, Operator

bl_info = {
    "name": "Translate",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "KEY"}


# class VIEW3D_PIE_MT_Bottom_E(Menu):
#     bl_label = "Shift-Alt-T"

#     def draw(self, context):
#         layout = self.layout
#         layout.alignment = "CENTER"
#         pie = layout.menu_pie()

#         ob_type = context.object.type
#         ob_mode = context.object.mode

#         # addon1:"LoopTools"
#         addon1 = check_rely_addon(rely_addons[2][0], rely_addons[2][1])

#         # 4 - LEFT
#         # 6 - RIGHT
#         # 2 - BOTTOM
#         # 8 - TOP
#         # 7 - TOP - LEFT
#         # 9 - TOP - RIGHT
#         # 1 - BOTTOM - LEFT
#         # 3 - BOTTOM - RIGHT

class VIEW3D_PIE_MT_Translate_Interface_Key(Operator):
    bl_idname = "pie.translate_interface"
    bl_label = "Translate Interface Hot Key"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # # 设置切换语言为中文
        lang = context.preferences.view.language
        if lang != 'zh_CN':
            context.preferences.view.language = 'zh_CN'
        # # 新建数据不翻译
        context.preferences.view.use_translate_new_dataname = False

        inter = context.preferences.view.use_translate_interface
        if inter == True:
            # 操作必须访问原始数据
            context.preferences.view.use_translate_interface = False
            self.report({'INFO'}, "英文")
        else:
            context.preferences.view.use_translate_interface = True
            self.report({'INFO'}, "中文")
        return {"FINISHED"}


class VIEW3D_PIE_MT_Translate_Tooltips_Key(Operator):
    bl_idname = "pie.ranslate_tooltips"
    bl_label = "Translate Tooltips Hot Key"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if context.preferences.view.language != 'en_US':
            return True

    def execute(self, context):
        tip = context.preferences.view.use_translate_tooltips
        if tip == True:
            # 必须访问原始数据
            context.preferences.view.use_translate_tooltips = False
            self.report({'INFO'}, " Translate Tooltips Is Closed!")
        else:
            context.preferences.view.use_translate_tooltips = True
            self.report({'INFO'}, "工具提示翻译打开！")
        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Translate_Interface_Key,
    VIEW3D_PIE_MT_Translate_Tooltips_Key
]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(
        idname=VIEW3D_PIE_MT_Translate_Interface_Key.bl_idname,
        type="T",
        value="CLICK",
        shift=True,
        alt=True,
    )
    kmi = km.keymap_items.new(
        idname=VIEW3D_PIE_MT_Translate_Tooltips_Key.bl_idname,
        type="T",
        value="CLICK",
        ctrl=True,
        shift=True,
        alt=True,
    )
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


if __name__ == "__main__":
    register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_E")
