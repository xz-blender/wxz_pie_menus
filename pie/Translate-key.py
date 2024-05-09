import re

import bpy
from bpy.types import Menu, Operator, Panel

bl_info = {
    "name": "Translate",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "KEY",
}


class VIEW3D_PIE_MT_Translate_Interface_Key(Operator):
    bl_idname = "pie.translate_interface"
    bl_label = "Translate Interface Hot Key"
    bl_description = ""
    bl_options = {"REGISTER"}

    lang_en: bpy.props.StringProperty(default="en_US")  # type: ignore
    lang_ch: bpy.props.StringProperty(default="zh_CN")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # # 设置切换语言为中文
        lang = ["zh_CN", "zh_HANS"]
        language = bpy.context.preferences.view.language
        if language in lang:
            bpy.context.preferences.view.language = "en_US"
            self.report({"INFO"}, "英文")
        else:
            try:
                bpy.context.preferences.view.language = ""
            except TypeError as e:
                # 解析错误信息来获取所有可用的语言
                match = re.search(r"enum \"(.*)\" not found in \('(.*)'\)", str(e))
                if match:
                    all_languages = match.group(2).split("', '")

            zh_lang = [item for item in lang if item in all_languages]
            bpy.context.preferences.view.language = zh_lang[0]
            context.preferences.view.use_translate_interface = True
            self.report({"INFO"}, "中文")
        # # 新建数据不翻译
        bpy.context.preferences.view.use_translate_new_dataname = False

        return {"FINISHED"}


class VIEW3D_PIE_MT_Translate_Tooltips_Key(Operator):
    bl_idname = "pie.ranslate_tooltips"
    bl_label = "Translate Tooltips Hot Key"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if context.preferences.view.language != "en_US":
            return True

    def execute(self, context):
        tip = context.preferences.view.use_translate_tooltips
        if tip == True:
            # 必须访问原始数据
            context.preferences.view.use_translate_tooltips = False
            self.report({"INFO"}, " Translate Tooltips Is Closed!")
        else:
            context.preferences.view.use_translate_tooltips = True
            self.report({"INFO"}, "工具提示翻译打开！")
        return {"FINISHED"}


classes = [VIEW3D_PIE_MT_Translate_Interface_Key, VIEW3D_PIE_MT_Translate_Tooltips_Key]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    km.keymap_items.new(
        idname=VIEW3D_PIE_MT_Translate_Interface_Key.bl_idname,
        type="T",
        value="CLICK",
        shift=True,
        alt=True,
    )
    km.keymap_items.new(
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
