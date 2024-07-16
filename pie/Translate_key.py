import re

import bpy
from bpy.app import translations
from bpy.types import Menu, Operator, Panel

from .. import __package__ as base_package
from ..utils import get_prefs

bl_info = {
    "name": "Translate",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "KEY",
}
enum_languages = (
    ("zh_HANS", "Simplified Chinese (简体中文)", "zh_HANS", 1),
    ("zh_HANT", "Traditional Chinese (繁體中文)", "zh_HANT", 2),
    ("en_US", "English (English)", "en_US", 3),
    ("ca_AD", "Catalan (Català)", "ca_AD", 4),
    ("es", "Spanish (Español)", "es", 5),
    ("fr_FR", "French (Français)", "fr_FR", 6),
    ("ja_JP", "Japanese (日本語)", "ja_JP", 7),
    ("sk_SK", "Slovak (Slovenčina)", "sk_SK", 8),
    ("cs_CZ", "Czech (Čeština)", "cs_CZ", 9),
    ("de_DE", "German (Deutsch)", "de_DE", 10),
    ("it_IT", "Italian (Italiano)", "it_IT", 11),
    ("ka", "Georgian (ქართული)", "ka", 12),
    ("ko_KR", "Korean (한국어)", "ko_KR", 13),
    ("pt_BR", "Brazilian Portuguese (Português do Brasil)", "pt_BR", 14),
    ("pt_PT", "Portuguese (Português)", "pt_PT", 15),
    ("ru_RU", "Russian (Русский)", "ru_RU", 16),
    ("uk_UA", "Ukrainian (Українська)", "uk_UA", 17),
    ("vi_VN", "Vietnamese (Tiếng Việt)", "vi_VN", 18),
)


def update_translate_new_dataname_state(self, context):
    userpref = context.preferences
    scene = context.scene
    lang = translations.locale
    if lang != "en_US":
        userpref.view.use_translate_new_dataname = scene.pie_switch_language.translate_new_dataname


class PIE_ToggleLanguageSettings(bpy.types.PropertyGroup):
    translate_new_dataname: bpy.props.BoolProperty(
        name="翻译新数据块的名称",
        description="启用或禁用新数据块名称的转换",
        default=False,
        update=update_translate_new_dataname_state,
    )  # type: ignore


def message_box(title="消息", message="", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=translations.pgettext(title), icon=icon)


class PIE_OT_toggle_language(Operator):
    bl_idname = "pie.toggle_language"
    bl_label = "切换语言"

    def execute(self, context):
        userpref = context.preferences
        addonpref = get_prefs()
        lang = translations.locale

        if addonpref.first_lang != addonpref.second_lang:
            if lang == addonpref.first_lang:
                userpref.view.language = addonpref.second_lang
            else:
                userpref.view.language = addonpref.first_lang
        else:
            message_box(
                title="切换语言失败",
                message="两种语言是一样的!请为在偏好设置选择两种不同的语言",
                icon="ERROR",
            )

        # 检测并修正 use_translate_new_dataname 选项值。
        scene = context.scene
        lang = bpy.app.translations.locale
        if lang != "en_US":
            if userpref.view.use_translate_new_dataname != scene.pie_switch_language.translate_new_dataname:
                userpref.view.use_translate_new_dataname = scene.pie_switch_language.translate_new_dataname

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


classes = [
    PIE_OT_toggle_language,
    VIEW3D_PIE_MT_Translate_Tooltips_Key,
    PIE_ToggleLanguageSettings,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)

addon_keymaps = []


def draw_ui(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.operator("pie.toggle_language")


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    km.keymap_items.new(
        idname=PIE_OT_toggle_language.bl_idname,
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
    class_register()
    bpy.types.Scene.pie_switch_language = bpy.props.PointerProperty(type=PIE_ToggleLanguageSettings)
    # bpy.types.TOPBAR_MT_editor_menus.append(draw_ui)
    register_keymaps()


def unregister():
    unregister_keymaps()
    class_unregister()
    del bpy.types.Scene.pie_switch_language
    # bpy.types.TOPBAR_MT_editor_menus.remove(draw_ui)
