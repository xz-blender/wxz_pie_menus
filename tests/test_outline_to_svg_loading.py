import builtins
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / "parts_addons" / "outline_to_svg" / "__init__.py"
PACKAGE = "outline_loading_test"


class OutlineLoadingTests(unittest.TestCase):
    def load_addon(self, *, missing=False, error=None):
        spec = importlib.util.spec_from_file_location(PACKAGE, SOURCE)
        addon = importlib.util.module_from_spec(spec)
        installer = ModuleType(f"{PACKAGE}.install_packages")
        installer.module_has_loader = Mock(return_value=not missing)
        ui_helpers = ModuleType(f"{PACKAGE}.ui_helpers")
        ui_helpers.pop_message = Mock()
        modules = {
            PACKAGE: addon,
            "bpy": ModuleType("bpy"),
            installer.__name__: installer,
            ui_helpers.__name__: ui_helpers,
        }
        original_import = builtins.__import__

        def import_modules(name, globals=None, locals=None, fromlist=(), level=0):
            if level == 1 and "operators" in fromlist and error is not None:
                raise error
            return original_import(name, globals, locals, fromlist, level)

        with patch.dict(sys.modules, modules), patch("builtins.__import__", side_effect=import_modules):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                spec.loader.exec_module(addon)
                addon.register()
        return addon, ui_helpers.pop_message.call_args.args[0]

    def test_missing_dependency_is_named(self):
        addon, message = self.load_addon(missing=True)
        self.assertTrue(addon.restart_required)
        self.assertIn("shapely", message)
        self.assertIn("依赖未就绪", message)

    def test_dll_load_failure_preserves_actual_error(self):
        error = ImportError("DLL load failed while importing lib: 找不到指定的模块。")
        addon, message = self.load_addon(error=error)
        self.assertEqual(addon.MISSING_MODULES, [])
        self.assertTrue(addon.restart_required)
        self.assertIn(f"ImportError: {error}", message)
        self.assertNotIn("pip 软件包", message)
        self.assertNotIn("请安装后", message)

    def test_other_import_failure_is_not_reported_as_missing_dependency(self):
        _, message = self.load_addon(error=RuntimeError("Unsupported Blender API"))
        self.assertIn("RuntimeError: Unsupported Blender API", message)
        self.assertNotIn("依赖未就绪", message)


if __name__ == "__main__":
    unittest.main()
