import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "blender_dev", Path(__file__).resolve().parents[1] / "scripts" / "blender_dev.py"
)
dev = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dev)


class BlenderDevelopmentTests(unittest.TestCase):
    def test_info_ignores_blender_banner(self):
        info = {"python": [3, 13, 5], "machine": "x86_64", "executable": "/usr/bin/python3.13"}
        with patch.object(dev.subprocess, "check_output", return_value="Banner\n" + dev.MARKER + json.dumps(info) + "\n"):
            self.assertEqual(dev.blender_info("blender"), info)

    def make_executable(self, directory, name="blender tool"):
        executable = Path(directory) / (name + (".exe" if os.name == "nt" else ""))
        executable.touch()
        executable.chmod(0o700)
        return executable

    def test_resolve_absolute_and_relative_paths_with_spaces(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_executable(directory)
            for candidate in (str(executable), os.path.relpath(executable)):
                with self.subTest(candidate=candidate):
                    self.assertEqual(dev.resolve_blender(candidate), str(executable.resolve()))

    def test_resolve_name_from_path(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_executable(directory)
            with patch.dict(os.environ, {"PATH": directory}):
                self.assertEqual(dev.resolve_blender(executable.name), str(executable.resolve()))

    def test_missing_executable_and_directory_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            for candidate in (str(Path(directory) / "missing"), directory):
                with self.subTest(candidate=candidate):
                    with self.assertRaisesRegex(RuntimeError, "not found or not executable"):
                        dev.resolve_blender(candidate)

    @unittest.skipIf(os.name == "nt", "POSIX executable permission check")
    def test_non_executable_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_executable(directory)
            executable.chmod(0o600)
            with self.assertRaisesRegex(RuntimeError, "not executable"):
                dev.resolve_blender(str(executable))

    def test_main_keeps_metacharacters_literal_and_uses_same_executable(self):
        info = {"python": [3, 13, 5], "machine": "x86_64"}
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_executable(directory, "blender ;$ tool")
            test = Path(directory) / "outside repo ;$ test.py"
            test.touch()
            argv = ["blender_dev.py", "--blender", os.path.relpath(executable), "--test", str(test)]
            with patch("sys.argv", argv), patch("sys.stdout", io.StringIO()), \
                    patch.object(dev, "dependency_path", return_value="test-site"), \
                    patch.object(dev.subprocess, "check_output", return_value=dev.MARKER + json.dumps(info)) as probe, \
                    patch.object(dev.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
                self.assertEqual(dev.main(), 0)
            expected = str(executable.resolve())
            self.assertEqual(probe.call_args.args[0][0], expected)
            self.assertIs(probe.call_args.kwargs["shell"], False)
            command = run.call_args.args[0]
            self.assertEqual(command[0], expected)
            self.assertEqual(command[-2:], ["--python", str(test.resolve())])
            self.assertIn("--background", command)
            self.assertEqual(run.call_args.kwargs["cwd"], dev.ROOT)
            self.assertIs(run.call_args.kwargs["shell"], False)

    def test_info_does_not_require_venv_or_launch_session(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = self.make_executable(directory)
            argv = ["blender_dev.py", "--blender", str(executable), "--info"]
            with patch("sys.argv", argv), patch("sys.stdout", io.StringIO()), \
                    patch.object(dev, "blender_info", return_value={}) as probe, \
                    patch.object(dev, "dependency_path") as dependency, \
                    patch.object(dev.subprocess, "run") as run:
                self.assertEqual(dev.main(), 0)
            probe.assert_called_once_with(str(executable.resolve()))
            dependency.assert_not_called()
            run.assert_not_called()

    def test_missing_executable_reports_cli_error_before_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            argv = ["blender_dev.py", "--blender", str(Path(directory) / "missing"), "--info"]
            with patch("sys.argv", argv), patch("sys.stderr", io.StringIO()) as stderr, \
                    patch.object(dev, "blender_info") as probe:
                with self.assertRaises(SystemExit) as error:
                    dev.main()
            self.assertEqual(error.exception.code, 2)
            self.assertIn("not found or not executable", stderr.getvalue())
            probe.assert_not_called()

    def test_test_all_is_sorted_and_excludes_ui_scripts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tests = root / "tests"
            tests.mkdir()
            for name in ("blender_z.py", "blender_a.py", "blender_demo_ui.py", "test_unit.py"):
                (tests / name).touch()
            with patch.object(dev, "ROOT", root):
                actual = dev.integration_tests(SimpleNamespace(test_all=True))
            self.assertEqual(actual, [tests / "blender_a.py", tests / "blender_z.py"])
        self.assertEqual(dev.integration_tests(SimpleNamespace(test_all=False, test=None)), [None])

    def test_ui_session_command_enables_addon_without_background(self):
        command = dev.blender_command("trusted-blender", None, True)
        self.assertEqual(command[0], "trusted-blender")
        self.assertIn("--enable-event-simulate", command)
        self.assertNotIn("--background", command)
        self.assertEqual(command[-2], "--python-expr")
        self.assertIn(f"addon_utils.enable({dev.ROOT.name!r}, default_set=True)", command[-1])
        self.assertIn("--disable-autoexec", command)

    def test_isolated_environment_does_not_mutate_parent_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"PYTHONPATH": "original", "BLENDER_USER_CONFIG": "original"}):
                env = dev.isolated_environment(directory, "test-site")
                self.assertEqual(os.environ["PYTHONPATH"], "original")
                self.assertEqual(os.environ["BLENDER_USER_CONFIG"], "original")
            self.assertEqual(env["PYTHONPATH"], "test-site")
            self.assertEqual(env["PYTHONNOUSERSITE"], "1")
            for kind in ("CONFIG", "SCRIPTS", "DATAFILES", "EXTENSIONS"):
                expected = Path(directory) / kind.lower()
                self.assertEqual(env["BLENDER_USER_" + kind], str(expected))
                self.assertTrue(expected.is_dir())

    def test_failed_session_returns_failure_and_reports_session(self):
        args = SimpleNamespace(blender="trusted-blender", info=False, venv=dev.ROOT / ".venv",
                               test_all=False, test=None, ui=True)
        with patch.object(dev, "parse_arguments", return_value=args), \
                patch.object(dev, "blender_info", return_value={}), \
                patch.object(dev, "dependency_path", return_value="test-site"), \
                patch.object(dev.subprocess, "run", return_value=SimpleNamespace(returncode=1)), \
                patch("sys.stdout", io.StringIO()), patch("sys.stderr", io.StringIO()) as stderr:
            self.assertEqual(dev.main(), 1)
        self.assertEqual(stderr.getvalue(), "FAILED: session\n")

    def test_failed_test_does_not_stop_remaining_tests(self):
        args = SimpleNamespace(blender="trusted-blender", info=False, venv=dev.ROOT / ".venv", ui=False)
        tests = [Path("first.py"), Path("second.py")]
        results = [SimpleNamespace(returncode=1), SimpleNamespace(returncode=0)]
        with patch.object(dev, "parse_arguments", return_value=args), \
                patch.object(dev, "blender_info", return_value={}), \
                patch.object(dev, "dependency_path", return_value="test-site"), \
                patch.object(dev, "integration_tests", return_value=tests), \
                patch.object(dev.subprocess, "run", side_effect=results) as run, \
                patch("sys.stdout", io.StringIO()), patch("sys.stderr", io.StringIO()) as stderr:
            self.assertEqual(dev.main(), 1)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(stderr.getvalue(), "FAILED: first.py\n")
        profiles = [call.kwargs["env"]["BLENDER_USER_CONFIG"] for call in run.call_args_list]
        self.assertNotEqual(profiles[0], profiles[1])
        self.assertTrue(all(not Path(profile).exists() for profile in profiles))

    def test_missing_interpreter_fails_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "Missing"):
                dev.dependency_path(Path(directory), {})

    def test_mismatched_minor_or_machine_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            executable.parent.mkdir()
            executable.touch()
            data = {"python": [3, 13], "machine": "x86_64", "site": "test-site"}
            with patch.object(dev.subprocess, "check_output", return_value=json.dumps(data)) as run:
                self.assertEqual(dev.dependency_path(root, {"python": [3, 13, 5], "machine": "x86_64"}), "test-site")
                self.assertIs(run.call_args.kwargs["shell"], False)
                for info in ({"python": [3, 11, 9], "machine": "x86_64"},
                             {"python": [3, 13, 5], "machine": "aarch64"}):
                    with self.assertRaisesRegex(RuntimeError, "ABI mismatch"):
                        dev.dependency_path(root, info)


if __name__ == "__main__":
    unittest.main()
