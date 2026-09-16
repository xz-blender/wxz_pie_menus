"""Exercise pip helpers, operators and preference drawing without installing packages."""

import importlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "_wxz_pip_test"


class OutputLines(list):
    def add(self):
        item = SimpleNamespace(line="")
        self.append(item)
        return item


class Operator:
    def report(self, level, message):
        self.reports.append((level, message))


class Layout:
    def __init__(self):
        self.labels = []
        self.properties = []
        self.operators = []
        self.grids = []

    def row(self, **kwargs):
        return self

    column = box = split = row

    def grid_flow(self, **kwargs):
        self.grids.append(kwargs)
        return self

    def label(self, **kwargs):
        self.labels.append(kwargs)

    def prop(self, owner, name, **kwargs):
        getattr(owner, name)
        self.properties.append(name)

    def operator(self, name, **kwargs):
        self.operators.append(name)


class PipPackageTests(unittest.TestCase):
    def setUp(self):
        self.output = SimpleNamespace(RETRUNCODE_OUTPUT="old", TEXT_OUTPUT=OutputLines(), ERROR_OUTPUT=OutputLines())
        self.context = SimpleNamespace(scene=SimpleNamespace(PIE_pip_output=self.output))
        self.prefs = SimpleNamespace(use_china_mirror=True, install_custom_pip_packages="  pillow  requests\tshapely ", debug=False)
        package = ModuleType(PACKAGE)
        package.__path__ = [str(ROOT)]
        utils = ModuleType(f"{PACKAGE}.utils")
        utils.get_prefs = lambda: self.prefs
        bpy = ModuleType("bpy")
        bpy.context = self.context
        bpy.utils = SimpleNamespace(system_resource=lambda name: "missing-python")
        bpy.types = ModuleType("bpy.types")
        bpy.types.Operator = Operator
        self.addCleanup(patch.stopall)
        patch.dict(sys.modules, {PACKAGE: package, f"{PACKAGE}.utils": utils, "bpy": bpy, "bpy.types": bpy.types}).start()
        # Import must work with a host console that cannot be reconfigured.
        with patch("site.addsitedir"), patch("sys.stdout", io.StringIO()):
            self.helper = importlib.import_module(f"{PACKAGE}.module.pip_helper")
            self.commands = importlib.import_module(f"{PACKAGE}.module.pip_helper.commands")
            self.ops = importlib.import_module(f"{PACKAGE}.module.pip_helper.operators")

    def run_operator(self, name):
        operator = getattr(self.ops, name)()
        operator.reports = []
        result = operator.execute(self.context)
        return result, operator.reports

    def test_manifest_drives_packages_and_import_names(self):
        manifest = tomllib.loads((ROOT / "blender_manifest.toml").read_text(encoding="utf-8"))
        distributions = {Path(wheel).name.split("-")[0] for wheel in manifest["wheels"]}
        self.assertEqual(set(self.helper.PIP_Packeges_Dict), distributions)
        self.assertEqual(self.helper.PIP_Packeges_Dict["pillow"], "PIL")
        self.assertIn("requests", self.helper.PIP_Packeges_Dict)

    def test_commands_match_mirror_and_bootstrap_settings(self):
        command = self.helper.build_pip_command("install", None, "pillow", use_china_mirror=True)
        self.assertEqual(command[:5], [sys.executable, "-m", "pip", "install", "--no-warn-script-location"])
        self.assertEqual(command[-3:], ["pillow", "-i", "https://mirrors.aliyun.com/pypi/simple/"])
        command = self.helper.build_pip_command("install", "--no-warn-script-location", "pillow")
        self.assertEqual(command.count("--no-warn-script-location"), 1)
        self.assertNotIn("-i", command)
        self.assertEqual(
            self.helper.build_pip_command("--default-pip", run_module="ensurepip", use_china_mirror=True),
            [sys.executable, "-m", "ensurepip", "--default-pip"],
        )

    def test_resolves_blender_python_before_host_executable(self):
        with tempfile.TemporaryDirectory() as directory:
            python = Path(directory) / "bin" / "python.exe"
            python.parent.mkdir()
            python.touch()
            with patch.object(self.commands.bpy.utils, "system_resource", return_value=directory):
                self.assertEqual(self.commands._resolve_python_bin(), str(python))
            python.unlink()
            with patch.object(self.commands.bpy.utils, "system_resource", return_value=directory):
                self.assertEqual(self.commands._resolve_python_bin(), sys.executable)

    def test_package_probe_does_not_import_package(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "wxz_probe_package.py").write_text("raise RuntimeError('must not import')", encoding="utf-8")
            with patch.object(sys, "path", [directory, *sys.path]):
                self.assertTrue(self.helper.check_package_is_installed("wxz_probe_package"))
                self.assertNotIn("wxz_probe_package", sys.modules)
                self.assertFalse(self.helper.check_package_is_installed("wxz_missing_dependency_package"))

    def test_output_clearing_append_and_failure_status(self):
        self.output.TEXT_OUTPUT.add().line = "stale stdout"
        self.output.ERROR_OUTPUT.add().line = "stale stderr"
        result = subprocess.CompletedProcess([], 1, "first\n\nsecond\n", "problem\n \n")
        with patch.object(self.commands.subprocess, "run", return_value=result):
            self.assertEqual(self.helper.run_pip_command("install", "pillow"), 1)
            self.assertEqual(self.output.RETRUNCODE_OUTPUT, "通用错误")
            self.assertEqual([line.line for line in self.output.TEXT_OUTPUT], ["first", "second"])
            self.assertEqual([line.line for line in self.output.ERROR_OUTPUT], ["problem"])
            self.helper.run_pip_command("list", clear_output=False)
            self.assertEqual(len(self.output.TEXT_OUTPUT), 4)

    def test_default_install_uses_manifest_and_reports_failure_honestly(self):
        with patch.object(self.ops, "run_pip_command", return_value=0) as run:
            result, reports = self.run_operator("PIE_OT_PIPInstall_Default")
            self.assertEqual(result, {"FINISHED"})
            self.assertEqual(list(run.call_args.args), ["install", *self.helper.PIP_Packeges_Dict])
            self.assertTrue(run.call_args.kwargs["use_china_mirror"])
            self.assertEqual(reports[0][0], {"INFO"})
        with patch.object(self.ops, "run_pip_command", return_value=1):
            result, reports = self.run_operator("PIE_OT_PIPInstall_Default")
            self.assertEqual(result, {"CANCELLED"})
            self.assertEqual(reports[0][0], {"ERROR"})

    def test_custom_install_and_uninstall_are_noninteractive(self):
        with patch.object(self.commands.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
            self.assertEqual(self.run_operator("PIE_OT_PIPInstall")[0], {"FINISHED"})
            command = run.call_args.args[0]
            self.assertIn("-i", command)
            self.assertEqual(command[5:8], ["pillow", "requests", "shapely"])
            self.assertNotIn("--user", command)
            self.assertEqual(self.run_operator("PIE_OT_PIPRemove")[0], {"FINISHED"})
            self.assertEqual(run.call_args.args[0][3:], ["uninstall", "pillow", "requests", "shapely", "-y"])
            self.assertTrue(self.prefs.use_china_mirror)

    def test_list_bootstrap_upgrade_and_clear_output(self):
        with patch.object(self.commands.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "packages", "")) as run:
            self.run_operator("PIE_OT_PIPList")
            self.assertEqual(run.call_args.args[0][1:], ["-m", "pip", "list"])
            self.run_operator("PIE_OT_EnsurePIP")
            self.assertEqual(run.call_args.args[0][1:], ["-m", "ensurepip", "--default-pip"])
            self.run_operator("PIE_OT_UpgradePIP")
            self.assertIn("-i", run.call_args.args[0])
            self.prefs.use_china_mirror = False
            self.run_operator("PIE_OT_UpgradePIP")
            self.assertNotIn("-i", run.call_args.args[0])
        self.run_operator("PIE_OT_ClearText")
        self.assertEqual(self.output.RETRUNCODE_OUTPUT, "")
        self.assertFalse(self.output.TEXT_OUTPUT or self.output.ERROR_OUTPUT)

    def test_dependency_panel_layout_and_errors_without_debug(self):
        panel = importlib.import_module(f"{PACKAGE}.module.pip_helper.panel")
        patch.object(panel, "check_package_is_installed", side_effect=lambda name: name == "PIL").start()
        self.output.TEXT_OUTPUT.add().line = "installed"
        self.output.ERROR_OUTPUT.add().line = "visible error"
        for native_multiline in (False, True):
            with self.subTest(native_multiline=native_multiline):
                layout = Layout()
                if native_multiline:
                    layout.label_multiline = layout.label
                self.prefs.layout = layout
                panel.draw_dependencies(self.prefs, self.context, layout)
                self.assertEqual(layout.properties, ["use_china_mirror", "install_custom_pip_packages"])
                self.assertEqual(layout.grids[0]["columns"], 4)
                package_labels = {item["text"]: item["icon"] for item in layout.labels if item.get("icon") in {"CHECKMARK", "PANEL_CLOSE"}}
                self.assertEqual(set(package_labels), set(self.helper.PIP_Packeges_Dict))
                self.assertEqual(package_labels["pillow"], "CHECKMARK")
                self.assertEqual(package_labels["requests"], "PANEL_CLOSE")
                self.assertIn({"text": "visible error"}, layout.labels)
                self.assertEqual(set(layout.operators), {cls.bl_idname for cls in self.ops.CLASSES})

    def test_command_capture_and_result_output(self):
        with patch("sys.stdout", io.StringIO()):
            result = self.helper.run_command_capture([sys.executable, "-c", "print('captured'); raise SystemExit(2)"])
        self.assertEqual(result["returncode"], 2)
        self.assertEqual(result["stdout"].strip(), "captured")
        self.assertFalse(result["cancelled"])
        self.helper.write_command_results_to_pip_output([self.helper.internal_command_result("prepare", stdout="ready"), result])
        self.assertEqual(self.output.RETRUNCODE_OUTPUT, "误用 shell 命令")
        self.assertEqual([line.line for line in self.output.TEXT_OUTPUT], [">>> prepare", "ready", ">>> pip", "captured"])
        self.assertEqual([line.line for line in self.output.ERROR_OUTPUT], ["captured"])


if __name__ == "__main__":
    unittest.main()
