"""Static lifecycle contract complements real-RNA and GUI gesture tests."""

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class KeymapContract(unittest.TestCase):
    def test_all_pie_registration_is_owned(self):
        count = 0
        for path in (ROOT / "pie").glob("*.py"):
            tree = ast.parse(path.read_text())
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == "register_keymaps":
                    count += 1
                    self.assertIn("owned_keymaps", [ast.unparse(d) for d in node.decorator_list], str(path))
        self.assertEqual(count, 37)  # Includes opt-out legacy Brush_key.

    def test_pie_never_edits_default_or_user_config(self):
        for path in (ROOT / "pie").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Attribute) and node.attr in {"default", "user"}:
                    if isinstance(node.value, ast.Attribute) and node.value.attr == "keyconfigs":
                        self.fail(f"{path}: direct external key configuration access")

    def test_preset_has_no_automatic_handlers(self):
        tree = ast.parse((ROOT / "operator/change_keys.py").read_text())
        calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertNotIn("manage_app_handlers", calls)
        self.assertNotIn("handlers.append", calls)
        register = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "register")
        self.assertEqual(
            [ast.unparse(n.func) for n in ast.walk(register) if isinstance(n, ast.Call)],
            ["_remove_legacy_handlers", "bpy.utils.register_class"],
        )

    def test_f_uses_no_hold_timer_and_explicit_undo(self):
        tree = ast.parse((ROOT / "pie/F_pie.py").read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PieMeshFGesture")
        calls = [n for n in ast.walk(cls) if isinstance(n, ast.Call)]
        self.assertFalse(any("timer" in ast.unparse(n.func) for n in calls))
        fills = [n for n in calls if ast.unparse(n.func) == "bpy.ops.mesh.edge_face_add"]
        self.assertEqual(len(fills), 2)
        for call in fills:
            self.assertTrue(ast.literal_eval(call.args[1]))


if __name__ == "__main__":
    unittest.main()
