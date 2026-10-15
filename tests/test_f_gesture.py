"""Deterministic F gesture state-machine tests; real input is tested separately."""

import ast
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GestureTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

        def op(name):
            def run(*args, **kwargs):
                self.calls.append((name, args, kwargs))
                return {"FINISHED"}

            return run

        bpy = NS(ops=NS(mesh=NS(edge_face_add=op("fill")), wm=NS(call_menu_pie=op("pie"))))
        names = {
            "_ACTIVE_F_GESTURES",
            "cancel_f_gestures",
            "_event_modifiers_match",
            "_has_custom_press",
            "PIE_Mesh_F_Gesture",
        }
        tree = ast.parse((ROOT / "pie/F_pie.py").read_text())
        tree.body = [
            n
            for n in tree.body
            if getattr(n, "name", None) in names
            or isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)
        ]
        self.ns = {"bpy": bpy, "Operator": object}
        exec(compile(tree, "F_pie.py", "exec"), self.ns)
        self.gesture = self.ns["PIE_Mesh_F_Gesture"]()
        self.context = NS(
            area=NS(type="VIEW_3D", as_pointer=lambda: 1),
            region=NS(type="WINDOW"),
            mode="EDIT_MESH",
            window=NS(as_pointer=lambda: 2),
            preferences=NS(inputs=NS(drag_threshold=30)),
            window_manager=NS(
                keyconfigs=NS(user=NS(keymaps={}), addon=NS(keymaps={})), modal_handler_add=lambda _: None
            ),
        )

    def event(self, type="F", value="PRESS", **kwargs):
        data = dict(
            type=type,
            value=value,
            is_repeat=False,
            mouse_x=100,
            mouse_y=100,
            shift=False,
            ctrl=False,
            alt=False,
            oskey=False,
        )
        data.update(kwargs)
        return NS(**data)

    def start(self):
        self.assertEqual(self.gesture.invoke(self.context, self.event()), {"RUNNING_MODAL"})

    def test_tap_and_undo(self):
        self.start()
        self.gesture.modal(self.context, self.event(value="RELEASE"))
        self.assertEqual(self.calls, [("fill", ("EXEC_DEFAULT", True), {})])

    def test_drag_only(self):
        self.start()
        self.gesture.modal(self.context, self.event(type="MOUSEMOVE", value="NOTHING", mouse_x=131))
        self.assertEqual([c[0] for c in self.calls], ["pie"])
        self.assertFalse(self.ns["_ACTIVE_F_GESTURES"])

    def test_below_threshold_is_tap(self):
        self.start()
        self.gesture.modal(self.context, self.event(type="MOUSEMOVE", value="NOTHING", mouse_x=129))
        self.assertFalse(self.calls)
        self.gesture.modal(self.context, self.event(value="RELEASE"))
        self.assertEqual(self.calls[0][0], "fill")

    def test_repeat_does_not_trigger(self):
        self.start()
        for _ in range(10):
            self.gesture.modal(self.context, self.event(is_repeat=True))
        self.assertFalse(self.calls)
        self.gesture.modal(self.context, self.event(value="RELEASE"))
        self.assertEqual(len(self.calls), 1)

    def test_escape_focus_and_unregister_cancel(self):
        for type in ("ESC", "WINDOW_DEACTIVATE"):
            self.start()
            self.assertEqual(self.gesture.modal(self.context, self.event(type=type)), {"CANCELLED"})
        self.start()
        self.ns["cancel_f_gestures"]()
        self.assertEqual(self.gesture.modal(self.context, self.event(value="RELEASE")), {"CANCELLED"})
        self.assertFalse(self.calls)

    def test_modifier_change_and_unrelated_key_pass(self):
        self.start()
        self.assertIn("PASS_THROUGH", self.gesture.modal(self.context, self.event(type="LEFT_SHIFT", shift=True)))
        self.start()
        self.assertIn("PASS_THROUGH", self.gesture.modal(self.context, self.event(type="F2")))
        self.assertFalse(self.calls)

    def test_f2_addon_custom_binding_wins(self):
        peer = NS(
            active=True,
            idname="mesh.f2",
            type="F",
            value="PRESS",
            key_modifier="NONE",
            any=False,
            shift=False,
            ctrl=False,
            alt=False,
            oskey=False,
            is_user_modified=False,
            is_user_defined=False,
        )
        self.context.window_manager.keyconfigs.addon.keymaps["Mesh"] = NS(keymap_items=[peer])
        self.assertEqual(self.gesture.invoke(self.context, self.event()), {"PASS_THROUGH"})
        self.assertFalse(self.calls)


if __name__ == "__main__":
    unittest.main()
