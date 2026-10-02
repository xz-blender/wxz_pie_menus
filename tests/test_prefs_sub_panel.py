"""Exercise preference panel drawing without importing Blender's full add-on."""

import ast
from pathlib import Path
import unittest

try:
    import bpy
except ImportError:
    bpy = None


ROOT = Path(__file__).resolve().parents[1]
source = ast.parse((ROOT / "prefs/panels.py").read_text(encoding="utf-8"))
helper = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "prefs_show_sub_panel")
namespace = {}
exec(compile(ast.Module(body=[helper], type_ignores=[]), str(ROOT / "prefs/panels.py"), "exec"), namespace)
prefs_show_sub_panel = namespace["prefs_show_sub_panel"]
panels = source
panel_flags = {
    node.args[2].value
    for node in ast.walk(panels)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "prefs_show_sub_panel"
}


class PreferencesWithoutIDProperties:
    show_other_module_prop = False

    def keys(self):
        raise TypeError("bpy_struct.keys(): this type doesn't support IDProperties")


class Layout:
    def __init__(self):
        self.properties = []

    def box(self):
        return self

    def column(self):
        return self

    def prop(self, owner, property_name, **kwargs):
        # RNA properties must be accessible through the same name used by the UI.
        getattr(owner, property_name)
        self.properties.append((owner, property_name, kwargs))


class PreferenceSubPanelTests(unittest.TestCase):
    def test_draw_and_toggle_without_idproperties(self):
        prefs = PreferencesWithoutIDProperties()
        for expanded in (False, True, False):
            with self.subTest(expanded=expanded):
                prefs.show_other_module_prop = expanded
                layout = Layout()
                state, column = prefs_show_sub_panel(prefs, layout, "show_other_module_prop", "Other tools")
                self.assertEqual(state, expanded)
                self.assertIs(column, layout)
                owner, name, options = layout.properties[0]
                self.assertIs(owner, prefs)
                self.assertEqual(name, "show_other_module_prop")
                self.assertEqual(options["text"], "Other tools")
                self.assertEqual(options["icon"], "TRIA_DOWN" if expanded else "TRIA_RIGHT")


@unittest.skipIf(bpy is None, "Run with Blender --background --factory-startup --python")
class BlenderPreferenceSubPanelTests(unittest.TestCase):
    def test_registered_panel_defaults_and_toggles(self):
        # Use the actual panel property declarations and the add-on's mixin pattern,
        # without enabling unrelated modules, handlers, or user preference presets.
        props = ast.parse((ROOT / "prefs/props.py").read_text(encoding="utf-8"))
        mixin = next(node for node in props.body if isinstance(node, ast.ClassDef) and node.name == "WXZ_PIE_Prefs_Props")
        mixin.body = [
            node
            for node in mixin.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in panel_flags
        ] or [ast.Pass()]
        module = ast.fix_missing_locations(ast.Module(body=[mixin], type_ignores=[]))
        scope = {"BoolProperty": bpy.props.BoolProperty}
        exec(compile(module, str(ROOT / "prefs/props.py"), "exec"), scope)

        class ProbePreferences(bpy.types.AddonPreferences, scope["WXZ_PIE_Prefs_Props"]):
            bl_idname = "wxz_prefs_sub_panel_regression"

        bpy.utils.register_class(ProbePreferences)
        self.addCleanup(bpy.utils.unregister_class, ProbePreferences)
        addon = bpy.context.preferences.addons.new()
        self.addCleanup(bpy.context.preferences.addons.remove, addon)
        addon.module = ProbePreferences.bl_idname
        prefs = addon.preferences

        self.assertTrue(panel_flags)
        for flag in sorted(panel_flags):
            with self.subTest(flag=flag):
                self.assertFalse(getattr(prefs, flag))
                for expanded in (False, True, False):
                    setattr(prefs, flag, expanded)
                    layout = Layout()
                    state, _ = prefs_show_sub_panel(prefs, layout, flag)
                    self.assertEqual(state, expanded)
                    self.assertEqual(layout.properties[0][1], flag)
                    self.assertEqual(layout.properties[0][2]["text"], flag)


if __name__ == "__main__":
    # Blender leaves its own command-line arguments in sys.argv.
    result = unittest.main(argv=[__file__], exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("Preference sub-panel regression tests failed")
