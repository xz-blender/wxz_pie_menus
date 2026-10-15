"""Platform path defaults and import-time consumers, without Blender installed."""

import ast
import importlib
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "platform_paths_addon_under_test"


class PlatformPathTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(TemporaryDirectory())
        self.home = Path(temporary) / "home"
        self.home.mkdir()
        self.enterContext(patch.dict(os.environ, {"HOME": str(self.home)}, clear=True))
        self.system = self.enterContext(patch("platform.system", return_value="Linux"))

        package = ModuleType(PACKAGE)
        package.__package__ = PACKAGE
        package.__path__ = [str(ROOT)]
        bpy = ModuleType("bpy")
        bpy_types = ModuleType("bpy.types")
        bpy_types.PointerProperty = object
        bpy_types.PropertyGroup = object
        handlers = ModuleType("bpy.app.handlers")
        handlers.persistent = lambda function: function
        mathutils = ModuleType("mathutils")
        for name in ("Euler", "Matrix", "Vector"):
            setattr(mathutils, name, type(name, (), {}))
        self.enterContext(patch.dict(sys.modules, {
            PACKAGE: package,
            "bpy": bpy,
            "bpy.types": bpy_types,
            "bpy.app.handlers": handlers,
            "mathutils": mathutils,
        }))
        self.utils = importlib.import_module(PACKAGE + ".utils")

    def write_user_dirs(self, content, config_home=None):
        config_home = config_home or self.home / ".config"
        config_home.mkdir(parents=True, exist_ok=True)
        (config_home / "user-dirs.dirs").write_text(content, encoding="utf-8")

    def test_linux_asset_defaults_are_absolute_strings_without_creating_directories(self):
        base = self.home / ".local/share/wxz_pie_menus/assets"
        self.assertEqual(self.utils.get_sync_path(), str(base / "sync"))
        self.assertEqual(self.utils.get_local_path(), str(base / "local"))
        self.assertFalse(base.exists())

    def test_linux_asset_paths_respect_xdg_data_home(self):
        data = self.home / "Application Data"
        os.environ["XDG_DATA_HOME"] = str(data)
        self.assertEqual(self.utils.get_sync_path(), str(data / "wxz_pie_menus/assets/sync"))
        self.assertEqual(self.utils.get_local_path(), str(data / "wxz_pie_menus/assets/local"))
        self.assertFalse(data.exists())

    def test_empty_or_relative_xdg_data_home_uses_default(self):
        for value in ("", "relative/data", "~/data", "$HOME/data"):
            with self.subTest(value=value):
                os.environ["XDG_DATA_HOME"] = value
                base = self.home / ".local/share/wxz_pie_menus/assets"
                self.assertEqual(self.utils.get_sync_path(), str(base / "sync"))
                self.assertEqual(self.utils.get_local_path(), str(base / "local"))

    def test_linux_desktop_falls_back_when_config_is_missing(self):
        self.assertEqual(self.utils.get_desktop_path(), str(self.home / "Desktop"))
        self.assertFalse((self.home / "Desktop").exists())

    def test_linux_desktop_supports_localized_home_path_and_comments(self):
        self.write_user_dirs('# Comment\nXDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
                             ' XDG_DESKTOP_DIR="$HOME/桌面 with spaces" # Localized desktop\n')
        self.assertEqual(self.utils.get_desktop_path(), str(self.home / "桌面 with spaces"))

    def test_linux_desktop_respects_custom_config_home_and_absolute_path(self):
        config_home = self.home / "config"
        desktop = self.home.parent / "Shared Desktop"
        os.environ["XDG_CONFIG_HOME"] = str(config_home)
        self.write_user_dirs(f'XDG_DESKTOP_DIR="{desktop}"\n', config_home)
        self.assertEqual(self.utils.get_desktop_path(), str(desktop))

    def test_empty_or_relative_xdg_config_home_uses_default(self):
        self.write_user_dirs('XDG_DESKTOP_DIR="$HOME/Work Desktop"\n')
        for value in ("", "relative/config"):
            with self.subTest(value=value):
                os.environ["XDG_CONFIG_HOME"] = value
                self.assertEqual(self.utils.get_desktop_path(), str(self.home / "Work Desktop"))

    def test_linux_desktop_handles_escaped_characters_without_expanding_other_variables(self):
        self.write_user_dirs(r'XDG_DESKTOP_DIR="$HOME/Desk \"quoted\" \\ \$HOME"' + "\n")
        self.assertEqual(self.utils.get_desktop_path(), str(self.home / 'Desk "quoted" \\ $HOME'))

    def test_linux_disabled_desktop_can_point_to_home(self):
        for value in ("$HOME", "${HOME}"):
            with self.subTest(value=value):
                self.write_user_dirs(f'XDG_DESKTOP_DIR="{value}"\n')
                self.assertEqual(self.utils.get_desktop_path(), str(self.home))

    def test_linux_desktop_ignores_invalid_or_unreadable_config(self):
        for content in ('XDG_DESKTOP_DIR="relative/path"', 'XDG_DESKTOP_DIR=""',
                        'XDG_DESKTOP_DIR="unterminated', 'XDG_DESKTOP_DIR="\\$HOME/Desktop"',
                        'XDG_DESKTOP_DIR="$(touch unexpected-file)"', 'XDG_DESKTOP_DIR="/bad\0path"'):
            with self.subTest(content=content):
                self.write_user_dirs(content)
                self.assertEqual(self.utils.get_desktop_path(), str(self.home / "Desktop"))
        for error in (PermissionError, UnicodeError):
            with self.subTest(error=error), patch.object(Path, "read_text", side_effect=error):
                self.assertEqual(self.utils.get_desktop_path(), str(self.home / "Desktop"))

    def test_windows_existing_asset_defaults_and_registry_desktop_are_preserved(self):
        self.system.return_value = "Windows"
        registry = MagicMock()
        registry.QueryValueEx.return_value = ("D:/Redirected Desktop", 1)
        with patch.dict(sys.modules, {"winreg": registry}):
            self.assertEqual(self.utils.get_sync_path(), "D:/BaiduSyncdisk/Blender Assets")
            self.assertEqual(self.utils.get_local_path(), "F:/Blender Assets")
            self.assertEqual(self.utils.get_desktop_path(), "D:/Redirected Desktop")
        registry.QueryValueEx.assert_called_once_with(registry.OpenKey.return_value.__enter__.return_value, "Desktop")

    def test_macos_existing_defaults_are_preserved(self):
        self.system.return_value = "Darwin"
        self.assertEqual(self.utils.get_sync_path(),
                         "/Users/wangxianzhi/Library/CloudStorage/OneDrive-个人/Sync/Blender/Assets Sync")
        self.assertEqual(self.utils.get_local_path(), "/Users/wangxianzhi/Blender Lib")
        self.assertEqual(self.utils.get_desktop_path(), str(self.home / "Desktop"))

    def test_linux_extension_settings_import_accepts_asset_defaults(self):
        settings = importlib.import_module(PACKAGE + ".operator.extensions_setting")
        search_path = settings.blender_org_extensions["node_presets"][0][0][1]
        self.assertEqual(search_path, str(Path(self.utils.get_sync_path()) / "Nodes Presets"))
        hdri_path = settings.addons_officials_list["hdri_maker"][0][0][1]
        self.assertEqual(hdri_path, str(Path(self.utils.get_local_path()) /
                                       "HDRI MAKER LIBRARY/HDRI_MAKER_DEFAULT_LIB"))

    def test_linux_asset_preference_declarations_receive_strings(self):
        source = ROOT / "prefs/props.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        fields = {"assets_library_path_sync", "assets_library_path_local"}
        declarations = [node for node in ast.walk(tree) if isinstance(node, ast.AnnAssign)
                        and isinstance(node.target, ast.Name) and node.target.id in fields]

        def string_property(**options):
            self.assertIsInstance(options["default"], str)
            self.assertTrue(Path(options["default"]).is_absolute())
            return options["default"]

        namespace = {"StringProperty": string_property, "get_sync_path": self.utils.get_sync_path,
                     "get_local_path": self.utils.get_local_path}
        exec(compile(ast.Module(body=declarations, type_ignores=[]), str(source), "exec"), namespace)
        self.assertEqual(set(namespace["__annotations__"]), fields)


if __name__ == "__main__":
    unittest.main()
