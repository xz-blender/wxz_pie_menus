import importlib.util
import json
import os
from pathlib import Path
import tempfile
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
            with patch.object(dev.subprocess, "check_output", return_value=json.dumps(data)):
                self.assertEqual(dev.dependency_path(root, {"python": [3, 13, 5], "machine": "x86_64"}), "test-site")
                for info in ({"python": [3, 11, 9], "machine": "x86_64"},
                             {"python": [3, 13, 5], "machine": "aarch64"}):
                    with self.assertRaisesRegex(RuntimeError, "ABI mismatch"):
                        dev.dependency_path(root, info)


if __name__ == "__main__":
    unittest.main()
