"""Reconstructed regression tests for deferred M4 HUD lifecycle cleanup."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class FocusHandlerTests(unittest.TestCase):
    def setUp(self):
        self.pending = set()
        timers = SimpleNamespace(
            is_registered=lambda fn: fn in self.pending,
            register=lambda fn, **kwargs: self.pending.add(fn),
            unregister=lambda fn: self.pending.remove(fn),
        )
        self.add = Mock(side_effect=lambda *args: object())
        self.remove = Mock()
        bpy = SimpleNamespace(
            app=SimpleNamespace(background=True, timers=timers, version=(4, 3, 2)),
            context=SimpleNamespace(scene=object()),
            types=SimpleNamespace(SpaceView3D=SimpleNamespace(
                draw_handler_add=self.add, draw_handler_remove=self.remove,
            )),
        )
        spec = importlib.util.spec_from_file_location(
            "test_focus_impl", Path(__file__).resolve().parents[1] / "parts_addons/m4_tools/focus_handler.py",
        )
        self.focus = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"bpy": bpy}):
            spec.loader.exec_module(self.focus)

    def test_disable_before_timer_fires_cancels_setup(self):
        f = self.focus
        f.delay_execution(f.manage_focus_HUD)
        self.assertIn(f.manage_focus_HUD, self.pending)
        f.remove_focus_hud()
        for callback in tuple(self.pending):
            callback()
        self.assertIsNone(f.focusHUD)
        self.add.assert_not_called()
        self.assertFalse(self.pending)

    def test_repeated_setup_and_cleanup_are_idempotent(self):
        f = self.focus
        f.manage_focus_HUD()
        handle = f.focusHUD
        f.manage_focus_HUD()
        self.assertIs(f.focusHUD, handle)
        self.add.assert_called_once()
        f.remove_focus_hud()
        f.remove_focus_hud()
        self.remove.assert_called_once_with(handle, "WINDOW")
        self.assertIsNone(f.focusHUD)

    def test_reenable_uses_one_new_handle(self):
        f = self.focus
        for _ in range(3):
            f.delay_execution(f.manage_focus_HUD)
            self.pending.remove(f.manage_focus_HUD)
            f.manage_focus_HUD()
            self.assertIsNotNone(f.focusHUD)
            f.remove_focus_hud()
            self.assertIsNone(f.focusHUD)
            self.assertFalse(self.pending)
        self.assertEqual(self.add.call_count, 3)
        self.assertEqual(self.remove.call_count, 3)


if __name__ == "__main__":
    unittest.main()
