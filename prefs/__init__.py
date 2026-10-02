"""Add-on preferences, property types, and preference panels."""

from ..module.reg import safe_register_class, safe_unregister_class

if "bpy" in locals():
    import importlib

    for core_name in ("props", "panels", "pip_props", "pip_panel"):
        importlib.reload(globals()[core_name])
else:
    import bpy
    from bpy.types import AddonPreferences

    from ..module.pip_helper import panel as pip_panel
    from ..module.pip_helper import props as pip_props
    from . import panels, props


MODULE_PATH_NAMES = {"pie": "pie_modules", "parts_addons": "other_modules", "operator": "setting_modules"}


class WXZ_PIE_Preferences(AddonPreferences, props.WXZ_PIE_Prefs_Props, pip_props.PIP_Prefs_Props):
    # Blender stores preferences under the host add-on, including extension namespaces.
    bl_idname = __package__.rsplit(".", 1)[0]

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        row.alignment = "CENTER"

        if self.tabs == "DEPENDENCIES":
            pip_panel.draw_dependencies(self, context, layout)
        elif self.tabs == "ADDON_MENUS":
            panels.draw_addon_menus(self, layout, context, MODULE_PATH_NAMES)
        elif self.tabs == "RESOURCE_CONFIG":
            panels.draw_resource_config(self, layout)
        elif self.tabs == "Other_Addons_Setting":
            panels.draw_other_addons_setting(self, layout)


def register():
    # Property groups must exist before the preferences and panels that use them.
    props.register()
    pip_props.register()
    safe_register_class([WXZ_PIE_Preferences])
    panels.register()


def unregister():
    panels.unregister()
    safe_unregister_class([WXZ_PIE_Preferences])
    pip_props.unregister()
    props.unregister()
