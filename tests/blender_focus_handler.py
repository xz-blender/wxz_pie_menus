"""Check focus HUD timer/handle cleanup with Blender's real RNA API."""
import importlib.util
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wxz_focus_handler_test", ROOT / "parts_addons/m4_tools/focus_handler.py")
focus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(focus)
try:
    focus.delay_execution(focus.manage_focus_HUD)
    assert bpy.app.timers.is_registered(focus.manage_focus_HUD)
    focus.remove_focus_hud()
    assert not bpy.app.timers.is_registered(focus.manage_focus_HUD)
    assert focus.focusHUD is None
    for cycle in range(3):
        focus.manage_focus_HUD()
        handle = focus.focusHUD
        assert handle is not None
        focus.manage_focus_HUD()
        assert focus.focusHUD is handle
        focus.delay_execution(focus.manage_focus_HUD)
        focus.remove_focus_hud()
        focus.remove_focus_hud()
        assert focus.focusHUD is None
        assert not bpy.app.timers.is_registered(focus.manage_focus_HUD)
        print(f"PASS: focus HUD timer/handle cleanup, cycle {cycle + 1}")
finally:
    focus.remove_focus_hud()
