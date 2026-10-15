"""Deliberate failures must not become successful Blender timer test runs."""

import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
reports = importlib.import_module("blender_test_report")
read_report, write_report = reports.read_report, reports.write_report

# A distinct module name avoids unittest discovery's test_* name collision.
SPEC = importlib.util.spec_from_file_location("persistence_launcher", SCRIPTS / "test_keymap_persistence.py")
launcher = importlib.util.module_from_spec(SPEC)
# Executed in setUpClass after blender_dev has its executable resolver.


class ReportFixture:

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.profile = Path(temporary.name)
        self.report = self.profile / "config" / "keymap-write.json"


class ReportTests(ReportFixture, unittest.TestCase):
    def test_success_round_trip(self):
        write_report(lambda: {"key": "J", "ctrl": True}, self.report, "write")
        self.assertEqual(read_report(self.report, "write", 0),
                         {"passed": True, "stage": "write", "key": "J", "ctrl": True})

    def test_deliberate_assertion_is_reported_and_rejected_even_with_zero_exit(self):
        def deliberately_fail():
            raise AssertionError("deliberate regression failure")

        with patch("sys.stderr", new=io.StringIO()):
            write_report(deliberately_fail, self.report, "write")
        data = json.loads(self.report.read_text())
        self.assertIs(data["passed"], False)
        self.assertIn("AssertionError: deliberate regression failure", data["error"])
        with self.assertRaisesRegex(RuntimeError, "validation failed"):
            read_report(self.report, "write", 0)

    def test_missing_report_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "missing or invalid"):
            read_report(self.report, "write", 0)

    def test_nonzero_exit_rejected_even_with_success_report(self):
        write_report(lambda: {}, self.report, "write")
        with self.assertRaisesRegex(RuntimeError, "status 7"):
            read_report(self.report, "write", 7)

    def test_malformed_and_non_success_reports_rejected(self):
        self.report.parent.mkdir()
        for value in ("", "{", "null", "[]", "true", "{}", '{"passed": false}',
                      '{"passed": "true", "stage": "write"}',
                      '{"passed": 1, "stage": "write"}',
                      '{"passed": true, "stage": "read"}', '{"passed": true}'):
            with self.subTest(value=value):
                self.report.write_text(value)
                with self.assertRaises(RuntimeError):
                    read_report(self.report, "write", 0)

    def test_report_write_error_is_not_swallowed(self):
        self.report.parent.write_text("not a directory")
        with self.assertRaises(OSError):
            write_report(lambda: {}, self.report, "write")


class ProcessBoundaryTests(ReportFixture, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SPEC.loader.exec_module(launcher)

    def launch_fixture(self, source):
        command = [sys.executable, "-c", source]
        with patch("sys.stdout", new=io.StringIO()):
            return launcher.run_stage(command, os.environ.copy(), self.profile, "write")

    def report_source(self, passed=True):
        return (f"from pathlib import Path; p=Path({str(self.report)!r}); "
                "p.parent.mkdir(parents=True, exist_ok=True); "
                f"p.write_text({json.dumps({'passed': passed, 'stage': 'write'})!r}); ")

    def test_real_process_success_is_accepted(self):
        self.assertIs(self.launch_fixture(self.report_source())["passed"], True)

    def test_real_process_false_report_is_rejected(self):
        source = self.report_source(False)
        with self.assertRaisesRegex(RuntimeError, "validation failed"):
            self.launch_fixture(source)

    def test_real_process_missing_report_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "missing or invalid"):
            self.launch_fixture("pass")

    def test_real_process_nonzero_exit_is_rejected(self):
        source = self.report_source() + "raise SystemExit(7)"
        with self.assertRaisesRegex(RuntimeError, "status 7"):
            self.launch_fixture(source)

    def test_stale_success_report_cannot_mask_missing_new_report(self):
        write_report(lambda: {}, self.report, "write")
        with self.assertRaisesRegex(RuntimeError, "missing or invalid"):
            self.launch_fixture("pass")

    def test_real_process_deliberate_assertion_round_trip(self):
        source = (f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); "
                  "from pathlib import Path; from blender_test_report import write_report\n"
                  "def check():\n    raise AssertionError('deliberate child-process failure')\n"
                  f"write_report(check, Path({str(self.report)!r}), 'write')\n")
        with self.assertRaisesRegex(RuntimeError, "validation failed"):
            self.launch_fixture(source)
        self.assertIn("deliberate child-process failure", (self.profile / "write.log").read_text())


if __name__ == "__main__":
    unittest.main()
