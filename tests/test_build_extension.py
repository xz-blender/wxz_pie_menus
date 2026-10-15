"""Check isolated platform packaging without running Blender or changing source."""

import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import call, patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_extension.py"
spec = importlib.util.spec_from_file_location("build_extension", SCRIPT)
build_extension = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_extension)

WINDOWS_WHEEL = "example-1.0-cp313-cp313-win_amd64.whl"
LINUX_WHEEL = "example-1.0-cp313-cp313-manylinux_2_28_x86_64.whl"
PURE_WHEEL = "another-1.0-py3-none-any.whl"
MANIFEST = f'''# Keep unrelated values and comments.
id = "example"
version = "1.0.0"
name = "示例"
wheels = [
  "wheels/{WINDOWS_WHEEL}",  # A Windows dependency.
]

[build]
paths_exclude_pattern = [".*", "/dist/"]
'''


class ManifestTests(unittest.TestCase):
    def test_replaces_only_root_wheels(self):
        paths = [f"wheels/{LINUX_WHEEL}"]
        updated = build_extension.replace_manifest_wheels(MANIFEST, paths)
        original = tomllib.loads(MANIFEST)
        self.assertEqual(tomllib.loads(updated), {**original, "wheels": paths})
        self.assertEqual(updated.split("wheels =")[0], MANIFEST.split("wheels =")[0])
        self.assertEqual(updated.split("[build]")[1], MANIFEST.split("[build]")[1])

    def test_handles_single_line_array(self):
        updated = build_extension.replace_manifest_wheels('id = "example"\nwheels = []', ["wheels/test.whl"])
        self.assertEqual(tomllib.loads(updated), {"id": "example", "wheels": ["wheels/test.whl"]})

    def test_handles_brackets_in_comments_and_paths(self):
        text = 'wheels = [\n# ]\n"wheels/odd]name.whl",\n]\n[build]\nsetting = true\n'
        updated = build_extension.replace_manifest_wheels(text, ["wheels/test.whl"])
        self.assertEqual(tomllib.loads(updated), {"wheels": ["wheels/test.whl"], "build": {"setting": True}})

    def test_rejects_missing_root_wheels(self):
        with self.assertRaisesRegex(ValueError, "must contain a wheels list"):
            build_extension.replace_manifest_wheels('[build]\nwheels = []\n', ["wheels/test.whl"])


class BuildExtensionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / "checkout"
        self.root.mkdir()
        (self.root / "blender_manifest.toml").write_text(MANIFEST, encoding="utf-8")
        (self.root / "__init__.py").write_text("# extension\n", encoding="utf-8")
        (self.root / "wheels").mkdir()
        (self.root / "wheels" / WINDOWS_WHEEL).write_bytes(b"tracked Windows wheel")
        (self.root / "wheels" / "_update_wheels.py").write_text("# wheel helper\n", encoding="utf-8")
        self.wheel_dir = self.directory / "prepared-wheels"
        self.wheel_dir.mkdir()
        (self.wheel_dir / LINUX_WHEEL).write_bytes(b"prepared Linux wheel")
        (self.wheel_dir / PURE_WHEEL).write_bytes(b"prepared pure Python wheel")
        (self.wheel_dir / "README.txt").write_text("Not a wheel", encoding="utf-8")
        self.destination = self.directory / "staged"
        self.dist = self.root / "dist"
        self.addCleanup(patch.stopall)
        patch.object(build_extension, "ROOT", self.root).start()
        patch.object(build_extension, "DIST", self.dist).start()

    def snapshot_source(self):
        return {path.relative_to(self.root): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def test_stage_excludes_generated_files_and_preserves_checkout(self):
        for relative in (
            ".git/config", ".venv/bin/python", "dist/old.zip", "__pycache__/cached.pyc", ".cache/result",
            ".pytest_cache/result", ".ruff_cache/result", ".mypy_cache/result", "package/__pycache__/cached.pyc",
            "package/orphan.pyc", "package/orphan.pyo",
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"exclude this")
        before = self.snapshot_source()

        build_extension.stage_source(self.root, self.destination, self.wheel_dir)

        self.assertEqual(self.snapshot_source(), before)
        self.assertEqual(
            sorted(path.name for path in (self.destination / "wheels").glob("*.whl")),
            sorted([LINUX_WHEEL, PURE_WHEEL]),
        )
        self.assertEqual((self.destination / "wheels" / LINUX_WHEEL).read_bytes(), b"prepared Linux wheel")
        self.assertTrue((self.destination / "wheels" / "_update_wheels.py").is_file())
        self.assertEqual((self.destination / "__init__.py").read_bytes(), before[Path("__init__.py")])
        for relative in before:
            if relative.parts[0] not in {"wheels", "__init__.py", "blender_manifest.toml"}:
                self.assertFalse((self.destination / relative).exists(), relative)
        manifest = tomllib.loads((self.destination / "blender_manifest.toml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["wheels"], [f"wheels/{name}" for name in sorted([LINUX_WHEEL, PURE_WHEEL])])
        self.assertEqual({**manifest, "wheels": tomllib.loads(MANIFEST)["wheels"]}, tomllib.loads(MANIFEST))
        self.assertFalse((self.destination / "wheels" / "README.txt").exists())

    def test_prepared_wheels_inside_checkout_are_not_copied_twice(self):
        prepared = self.root / "local-wheels"
        prepared.mkdir()
        (prepared / LINUX_WHEEL).write_bytes(b"Linux wheel")
        build_extension.stage_source(self.root, self.destination, prepared)
        self.assertFalse((self.destination / "local-wheels").exists())
        self.assertTrue((self.destination / "wheels" / LINUX_WHEEL).is_file())
        self.assertTrue((prepared / LINUX_WHEEL).is_file())

    def test_can_stage_existing_wheels_directory(self):
        build_extension.stage_source(self.root, self.destination, self.root / "wheels")
        self.assertEqual(
            (self.destination / "wheels" / WINDOWS_WHEEL).read_bytes(), b"tracked Windows wheel",
        )

    def test_empty_or_missing_wheel_directory_fails_before_copying(self):
        empty = self.directory / "empty"
        empty.mkdir()
        (empty / "directory.whl").mkdir()
        before = self.snapshot_source()
        for directory, message in ((empty, "No wheel files"), (self.directory / "missing", "does not exist")):
            with self.subTest(directory=directory), self.assertRaisesRegex(ValueError, message):
                build_extension.stage_source(self.root, self.destination, directory)
            self.assertFalse(self.destination.exists())
            self.assertEqual(self.snapshot_source(), before)

    def test_default_build_uses_original_source_and_validates_archive(self):
        before = self.snapshot_source()
        with patch.object(build_extension.subprocess, "run") as run, patch("sys.stdout", io.StringIO()):
            build_extension.main(["--blender", "custom-blender"])
        command = ["custom-blender", "--background", "--factory-startup", "--command", "extension"]
        self.assertEqual(run.call_args_list, [
            call([*command, "build", "--source-dir", str(self.root), "--output-dir", str(self.dist)],
                 cwd=self.root, check=True),
            call([*command, "validate", str(self.dist / "example-1.0.0.zip")], cwd=self.root, check=True),
        ])
        self.assertEqual(self.snapshot_source(), before)

    def test_isolated_build_cleans_up_and_can_use_separate_output_directory(self):
        before = self.snapshot_source()
        staged_sources = []
        output = self.dist / "linux"

        def fake_run(command, **kwargs):
            if "build" in command:
                source = Path(command[command.index("--source-dir") + 1])
                staged_sources.append(source)
                self.assertNotEqual(source, self.root)
                self.assertTrue((source / "wheels" / LINUX_WHEEL).is_file())
                self.assertFalse((source / "wheels" / WINDOWS_WHEEL).exists())
                self.assertEqual(command[command.index("--output-dir") + 1], str(output))
            else:
                self.assertEqual(command[-2:], ["validate", str(output / "example-1.0.0.zip")])
                self.assertTrue(staged_sources[0].is_dir())

        with patch.object(build_extension.subprocess, "run", side_effect=fake_run) as run:
            with patch("sys.stdout", io.StringIO()):
                build_extension.main(["--wheel-dir", str(self.wheel_dir), "--output-dir", str(output)])
        self.assertEqual(run.call_count, 2)
        self.assertTrue(output.is_dir())
        self.assertFalse(staged_sources[0].exists())
        self.assertEqual(self.snapshot_source(), before)

    def test_failure_preserves_checkout_and_cleans_staged_files(self):
        before = self.snapshot_source()
        for fail_on in ("build", "validate"):
            staged_sources = []

            def fake_run(command, **kwargs):
                if "build" in command:
                    staged_sources.append(Path(command[command.index("--source-dir") + 1]))
                if fail_on in command:
                    raise subprocess.CalledProcessError(1, command)

            with self.subTest(fail_on=fail_on), patch.object(build_extension.subprocess, "run", side_effect=fake_run):
                with self.assertRaises(subprocess.CalledProcessError):
                    build_extension.main(["--wheel-dir", str(self.wheel_dir)])
                self.assertFalse(staged_sources[0].exists())
                self.assertEqual(self.snapshot_source(), before)

    def test_empty_directory_reports_cli_error_without_running_blender(self):
        empty = self.directory / "empty"
        empty.mkdir()
        with patch.object(build_extension.subprocess, "run") as run, patch("sys.stderr", io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as error:
                build_extension.main(["--wheel-dir", str(empty)])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("No wheel files", stderr.getvalue())
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
