from bpy.types import PropertyGroup, AddonPreferences, Operator
from bpy.props import BoolProperty, PointerProperty
import bpy
import os
from .pie.utils import check_rely_addon, rely_addons


bl_info = {
    "name": "WXZ Pie Menus Addon",
    "author": "wxz",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "description": "Pie Menu",
    "category": "3D View",
}

sub_modules_names = [
    "X-key",
    "X-pie",
    "Q-pie",
    "A-pie",
    "Z-pie",
    "D-pie",
    "F-pie",
    "R-pie",
    "W-pie",
    "Tab_ctrl-pie",
    "T-pie",
    "E-pie",
    "Translate-key",
    "Space-key",
    "Space_shift-pie",
    "C-pie",
    "C-key",
    "S_ctrl-pie",
    "S-pie",
    "Q_alt-key",
    "Q-key",
    "V-pie",
    "X_ctrl_alt-pie",
    "Outliner-pie",
    "U-pie",
    "Modifier-bar",
    "W_alt-key",
    "A_shift-pie",
]
sub_modules_names.sort()

sub_modules = [
    __import__(__package__ + "." + "pie" + "." + submod, {}, {}, submod)
    for submod in sub_modules_names
]
sub_modules.sort(key=lambda mod: (
    mod.bl_info['name'], mod.bl_info['category']))


def _get_pref_class(mod):
    import inspect

    for obj in vars(mod).values():
        if inspect.isclass(obj) and issubclass(obj, PropertyGroup):
            if hasattr(obj, 'bl_idname') and obj.bl_idname == mod.__name__:
                return obj


def get_addon_preferences(name=''):
    """Acquisition and registration"""
    addons = bpy.context.preferences.addons
    if __name__ not in addons:  # wm.read_factory_settings()
        return None
    addon_prefs = addons[__name__].preferences
    if name:
        if not hasattr(addon_prefs, name):
            for mod in sub_modules:
                if mod.__name__.split('.')[-1] == name:
                    cls = _get_pref_class(mod)
                    if cls:
                        prop = PointerProperty(type=cls)
                        create_property(WXZ_PIE_Preferences, name, prop)
                        bpy.utils.unregister_class(WXZ_PIE_Preferences)
                        bpy.utils.register_class(WXZ_PIE_Preferences)
        return getattr(addon_prefs, name, None)
    else:
        return addon_prefs


def create_property(cls, name, prop):
    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = dict()
    cls.__annotations__[name] = prop


def register_submodule(mod):
    mod.register()
    mod.__addon_enabled__ = True


def unregister_submodule(mod):
    if mod.__addon_enabled__:
        mod.unregister()
        mod.__addon_enabled__ = False

        prefs = get_addon_preferences()
        name = mod.__name__.split('.')[-1]
        if hasattr(WXZ_PIE_Preferences, name):
            delattr(WXZ_PIE_Preferences, name)
            if prefs:
                bpy.utils.unregister_class(WXZ_PIE_Preferences)
                bpy.utils.register_class(WXZ_PIE_Preferences)
                if name in prefs:
                    del prefs[name]


def get_dirpath():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "keymap_presets")


class Empty_Operator(Operator):
    bl_idname = "pie.empty_operator"
    bl_label = ""

    def execute(self, context):
        return {'CANCELLED'}


class Apply_My_Keymap(Operator):
    bl_idname = "pie.apply_my_keymap"
    bl_label = "应用快捷键表"
    bl_description = ""
    bl_options = {"REGISTER"}

    path: bpy.props.StringProperty(name="apply_name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if os.path.exists(self.path):
            bpy.ops.preferences.keyconfig_import(filepath=self.path)
            self.report({'INFO'}, '已应用快捷键配置:"%s"' %
                        (os.path.basename(self.path)))
            return {"FINISHED"}
        else:
            self.report({'INFO'}, '未应用快捷键表:"%s"' % (slef.path))
            return {"FINISHED"}


class Restore_My_Keymap(Operator):
    bl_idname = "pie.restore_my_keymap"
    bl_label = "备份当前快捷键表"
    bl_description = ""
    bl_options = {"REGISTER"}

    path: bpy.props.StringProperty(name="backup_name")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if os.path.exists(self.path) == True:
            return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="已有备份!是否覆盖？", icon="QUESTION")

    def execute(self, context):
        bpy.ops.preferences.keyconfig_export(filepath=self.path)
        bpy.ops.wm.save_userpref()
        self.report({'INFO'}, '已备份配置到: "%s"' % (self.path))
        return {"FINISHED"}


class Enable_Addon(Operator):
    bl_idname = "pie.enable_addon"
    bl_label = ""

    module: bpy.props.StringProperty(name="module_name")

    def execute(self, context):
        try:
            bpy.ops.preferences.addon_enable(module=self.module)
        except:
            self.report({'INFO', "插件已经开启！"})
        return {'FINISHED'}


class WXZ_PIE_Preferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        row = layout.box().row()

        box = row.box()
        sub = box.row(align=True)
        sub.label(text='自定义快捷键表:', icon='EVENT_SPACEKEY')

        sub.operator(Apply_My_Keymap.bl_idname, text='应用--"预设表"').path = os.path.join(
            get_dirpath(), 'My_Keymaps.py'
        )
        sub.operator(Apply_My_Keymap.bl_idname, text='应用--"备份表"').path = os.path.join(
            get_dirpath(), 'Stored_Keymaps.py'
        )

        row = row.box()
        row.alignment = "RIGHT"
        row.operator(Restore_My_Keymap.bl_idname, text="备份当前快捷键表").path = os.path.join(
            get_dirpath(), 'Stored_Keymaps.py'
        )

        split = layout.split()

        column = split.column()
        box = column.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label(text='检查-饼菜单依赖三方插件 :')

        for name in rely_addons:
            box = column.box()
            row = box.row()
            sub = row.row()
            sub.label(text=name[0], icon="DOT")
            sub = row.row()
            sub.alignment = 'RIGHT'
            if check_rely_addon(name[0], name[1]) == '1':
                sub.label(text='', icon="CHECKMARK")
            elif check_rely_addon(name[0], name[1]) == '0':
                sub.label(text='点此图标开启插件--->')
                sub.operator(
                    Enable_Addon.bl_idname,
                    text='',
                    icon="CHECKBOX_HLT",
                    emboss=True,
                ).module = name[1]
            else:
                sub.label(text='未安装此插件', icon="ERROR")

        column = split.column()
        box = column.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label(text='已安装并启用Pie插件 :')

        for mod in sub_modules:
            mod_name = mod.__name__.split('.')[-1]
            info = mod.bl_info
            box = column.box()
            row = box.row()
            sub = row.row()
            sub.context_pointer_set('addon_prefs', self)
            sub.label(
                icon="DOT",
                # text='{} ———— {}'.format(info['name'], info['category']),
                text='%s' % (info['name']),
            )
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(self, 'use_' + mod_name, text='')

        row = layout.box().row()
        row.alignment = "CENTER"
        row.label(text="End of Pie Menu Activations", icon="FILE_PARENT")


for mod in sub_modules:
    info = mod.bl_info
    mod_name = mod.__name__.split('.')[-1]

    def gen_update(mod):
        def update(self, context):
            enabled = getattr(self, 'use_' + mod.__name__.split('.')[-1])
            if enabled:
                register_submodule(mod)
            else:
                unregister_submodule(mod)
            mod.__addon_enabled__ = enabled

        return update

    create_property(
        WXZ_PIE_Preferences,
        'use_' + mod_name,
        BoolProperty(
            name=info['name'],
            description=info.get('description', ''),
            update=gen_update(mod),
            default=True,
        ),
    )

    create_property(WXZ_PIE_Preferences, 'show_expanded_' +
                    mod_name, BoolProperty())


classes = (
    WXZ_PIE_Preferences,
    Apply_My_Keymap,
    Restore_My_Keymap,
    Empty_Operator,
    Enable_Addon,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = get_addon_preferences()
    for mod in sub_modules:
        if not hasattr(mod, '__addon_enabled__'):
            mod.__addon_enabled__ = False
        name = mod.__name__.split('.')[-1]
        if getattr(prefs, 'use_' + name):
            register_submodule(mod)


def unregister():
    for mod in sub_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
