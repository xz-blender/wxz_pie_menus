import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "wheels" / "_update_wheels.py"
spec = importlib.util.spec_from_file_location("update_wheels", SCRIPT)
update_wheels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_wheels)


@unittest.skipUnless(os.name == "nt", "Windows temporary-directory ACL regression")
class WheelPermissionsTests(unittest.TestCase):
    def test_downloaded_wheel_inherits_destination_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            # Model a normal checkout, outside TemporaryDirectory's private ACL.
            subprocess.run(["icacls", directory, "/reset"], check=True, capture_output=True)
            destination = Path(directory) / "wheels"
            destination.mkdir()
            # A sibling created normally provides the destination's expected ACL.
            reference = destination / "reference.txt"
            reference.write_bytes(b"reference")

            def fake_download(command):
                download_dir = Path(command[command.index("--dest") + 1])
                (download_dir / "example-1.0-py3-none-any.whl").write_bytes(b"wheel")

            with patch.object(update_wheels, "WHEELS_DIR", destination), patch.object(
                update_wheels, "run", side_effect=fake_download
            ):
                update_wheels.download_wheels(("example",))

            wheel = destination / "example-1.0-py3-none-any.whl"
            self.assertEqual(wheel.read_bytes(), b"wheel")

            def acl_entries(path):
                result = subprocess.check_output(["icacls", str(path)], text=True)
                # Ignore the path and localized status footer; compare ACEs.
                return [line.strip() for line in result[len(str(path)):].splitlines() if ":(" in line]

            self.assertEqual(acl_entries(wheel), acl_entries(reference))


if __name__ == "__main__":
    unittest.main()
