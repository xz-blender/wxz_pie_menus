"""Run with Blender --background --factory-startup --offline-mode --python-exit-code 1 --python this_file."""

import importlib
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
relay = importlib.import_module(f"{ROOT.name}.operator.enable_relay_addons")
PRESETS = json.loads((ROOT / "operator" / "addons_lib_presets.json").read_text(encoding="utf-8"))
EXPECTED_OFFICIAL = {
    "simple_deform_helper",
    "bool_tool",
    "curve_tools",
    "extra_mesh_objects",
    "extra_curve_objectes",
    "simplify_curves_plus",
    "boltfactory",
    "edit_operator_source",
    "icon_viewer",
    "copy_attributes_menu",
    "print3d_toolbox",
    "looptools",
    "snap_utilities_line",
    "tinycad_mesh_tools",
    "node_presets",
    "magic_uv",
    "modifier_tools",
    "sun_position",
    "edit_linked_library",
    "edit_mesh_tools",
    "import_autocad_dxf_format_dxf",
    "export_autocad_dxf_format_dxf",
    "synchronize_workspaces",
    "NodePie",
    "improved_node_search",
    "material_utilities",
    "f2",
}


class OfficialInstallTests(unittest.TestCase):
    def setUp(self):
        self.installed = set()
        self.enabled = set()
        self.repo = SimpleNamespace(
            name="extensions.blender.org", module="blender_org", directory="official-repo", enabled=False
        )
        self.repos = Mock()
        self.repos.get.return_value = self.repo
        self.repos.find.return_value = 0
        self.context = object()
        self.operator = SimpleNamespace(ex_dirs="org_ex", report=Mock())
        self.sync = Mock(return_value={"FINISHED"})
        self.install = Mock(side_effect=self.install_package)
        self.enable = Mock(side_effect=self.enable_package)
        self.save = Mock()
        self.settings = Mock()
        self.fake_bpy = SimpleNamespace(
            ops=SimpleNamespace(
                extensions=SimpleNamespace(repo_sync=self.sync, package_install=self.install),
                preferences=SimpleNamespace(addon_enable=self.enable),
                wm=SimpleNamespace(save_userpref=self.save),
            )
        )
        patches = [
            patch.object(relay, "bpy", self.fake_bpy),
            patch.object(relay, "repos", self.repos),
            patch.object(relay, "set_online"),
            patch.object(relay, "is_BlenderVersion_gthan", return_value=True),
            patch.object(relay, "get_addon_list", side_effect=lambda: list(self.installed)),
            patch.object(relay, "set_ex_settings", self.settings),
            patch.object(
                relay, "addon_utils", SimpleNamespace(check=lambda name: (name in self.enabled, name in self.enabled))
            ),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def install_package(self, execution, **kwargs):
        self.assertEqual(execution, "EXEC_DEFAULT")
        self.sync.assert_called_once()
        self.assertEqual(kwargs["repo_directory"], self.repo.directory)
        self.assertEqual(kwargs["repo_index"], 0)
        self.assertTrue(kwargs["enable_on_install"])
        name = f"bl_ext.{self.repo.module}.{kwargs['pkg_id']}"
        self.installed.add(name)
        self.enabled.add(name)
        return {"FINISHED"}

    def enable_package(self, *, module):
        self.enabled.add(module)
        return {"FINISHED"}

    def execute(self):
        return relay.Enable_Pie_Menu_Relay_Addons.execute(self.operator, self.context)

    def test_complete_list_installs_from_official_source_and_keeps_presets(self):
        self.assertEqual(set(PRESETS["org_ex"]), EXPECTED_OFFICIAL)
        self.assertEqual(self.execute(), {"FINISHED"})
        self.assertTrue(self.repo.enabled)
        self.assertEqual({call.kwargs["pkg_id"] for call in self.install.call_args_list}, EXPECTED_OFFICIAL)
        self.assertEqual(self.settings.call_count, len(EXPECTED_OFFICIAL))
        self.settings.assert_any_call(self.context, "bl_ext.blender_org.f2", PRESETS["org_ex"]["f2"])
        self.save.assert_called_once()

    def test_existing_plugins_are_enabled_without_sync_or_download(self):
        self.installed.update(f"bl_ext.blender_org.{name}" for name in EXPECTED_OFFICIAL)
        self.assertEqual(self.execute(), {"FINISHED"})
        self.sync.assert_not_called()
        self.install.assert_not_called()
        self.assertEqual(self.enable.call_count, len(EXPECTED_OFFICIAL))

    def test_failed_package_does_not_block_later_packages_or_apply_its_presets(self):
        def fail_one(execution, **kwargs):
            if kwargs["pkg_id"] == "curve_tools":
                return {"CANCELLED"}
            return self.install_package(execution, **kwargs)

        self.install.side_effect = fail_one
        self.assertEqual(self.execute(), {"FINISHED"})
        self.assertEqual(self.install.call_count, len(EXPECTED_OFFICIAL))
        self.assertEqual(self.settings.call_count, len(EXPECTED_OFFICIAL) - 1)
        self.assertNotIn("bl_ext.blender_org.curve_tools", self.enabled)
        self.assertTrue(any("curve_tools" in call.args[1] for call in self.operator.report.call_args_list))

    def test_sync_failure_cancels_without_installing_or_saving(self):
        self.sync.return_value = {"CANCELLED"}
        self.assertEqual(self.execute(), {"CANCELLED"})
        self.install.assert_not_called()
        self.settings.assert_not_called()
        self.save.assert_not_called()

    def test_apply_all_presets_uses_extension_module_ids(self):
        with (
            patch.object(relay, "org_ext_id", "bl_ext.blender_org"),
            patch.object(relay, "third_ext_id", "bl_ext.blender4_com"),
        ):
            relay.set_all_addon_presets(self.operator, self.context)
        self.settings.assert_any_call(self.context, "bl_ext.blender_org.f2", PRESETS["org_ex"]["f2"])
        self.settings.assert_any_call(
            self.context, "bl_ext.blender4_com.simple_tabs", PRESETS["third_ex"]["simple_tabs"]
        )


suite = unittest.defaultTestLoader.loadTestsFromTestCase(OfficialInstallTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise AssertionError("Official repository installation regression tests failed")
