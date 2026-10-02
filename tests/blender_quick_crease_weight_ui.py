# SPDX-License-Identifier: GPL-3.0-or-later
"""Run in factory-startup Blender with --enable-event-simulate.

Adapted from Quick Crease Weight 1.2.1; output goes to WXZ_QCW_TEST_OUTPUT
or the temporary wxz-qcw-ui directory. Never saves user preferences.
"""
import json
import os
from pathlib import Path
import sys
import traceback

import tempfile
import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quick_crease_weight_support import e_pie, hud, operators, preferences, register, unregister

OUTPUT = Path(os.environ.get("WXZ_QCW_TEST_OUTPUT", str(Path(tempfile.gettempdir()) / "wxz-qcw-ui")))
OUTPUT.mkdir(parents=True, exist_ok=True)
register()

window = bpy.context.window
area = next(item for item in window.screen.areas if item.type == "VIEW_3D")
region = next(item for item in area.regions if item.type == "WINDOW")
center = (region.x + region.width // 2, region.y + region.height // 2)
prefs = preferences.get_preferences(bpy.context)
draw_errors = []
draw_count = 0
pref_draw_count = 0
original_draw = hud.draw


def checked_draw(operator):
    global draw_count
    try:
        original_draw(operator)
        draw_count += 1
    except Exception:
        draw_errors.append(traceback.format_exc())


hud.draw = checked_draw


class QCW_PT_smoke_preferences(bpy.types.Panel):
    bl_idname = "QCW_PT_smoke_preferences"
    bl_label = "Quick Crease Weight · Preferences"
    bl_space_type = "PREFERENCES"
    bl_region_type = "WINDOW"

    def draw(self, context):
        global pref_draw_count
        try:
            # Use the real preference draw method and real RNA UILayout.
            prefs.draw_settings(self.layout, context)
            pref_draw_count += 1
        except Exception:
            draw_errors.append(traceback.format_exc())


def send(kind, value="PRESS", dx=0, **modifiers):
    window.event_simulate(type=kind, value=value, x=center[0] + dx, y=center[1], **modifiers)


def screenshot(name):
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / name))


def active():
    assert len(operators.ACTIVE) == 1, f"Expected one active operator, found {operators.ACTIVE}"
    return operators.ACTIVE[0]


def values(attribute, edge=False):
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    elements = bm.edges if edge else bm.verts
    layer = elements.layers.float.get(attribute)
    return None if layer is None else [element[layer] for element in elements]


def setup():
    for obj in bpy.context.scene.objects:
        if obj.type in {"CAMERA", "LIGHT"}:
            obj.hide_set(True)
    view = area.spaces.active
    view.region_3d.view_distance = 6.5
    view.overlay.show_floor = False
    view.overlay.show_axis_x = False
    view.overlay.show_axis_y = False
    view.overlay.show_cursor = False
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.ed.undo_push(message="Quick Crease Weight test baseline")
    send("MOUSEMOVE", "NOTHING")


def start_crease():
    screenshot("before-shortcut.png")
    keymap = bpy.context.window_manager.keyconfigs.user.keymaps["Mesh"]
    print([(item.idname, item.type, item.shift, item.ctrl, item.active) for item in keymap.keymap_items
           if item.type == "E"], flush=True)
    send("E", shift=True)


def adjust_crease():
    assert active().attribute_kind == "crease"
    send("E", "RELEASE", shift=True)
    send("LEFT_SHIFT", "RELEASE")
    send("LEFT_CTRL", ctrl=True)


def move_crease():
    assert active().value == 1
    send("LEFT_CTRL", "RELEASE")
    send("MOUSEMOVE", "NOTHING", dx=-70)


def capture_crease():
    assert abs(active().value - 0.65) < 0.001, active().value
    assert all(abs(value - 0.65) < 0.001 for value in values("crease_vert"))
    screenshot("hud-default.png")
    send("ESC")


def start_bevel():
    assert not operators.ACTIVE
    assert values("crease_vert") is None
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    send("E", ctrl=True, shift=True)


def adjust_bevel():
    assert active().attribute_kind == "bevel_weight"
    assert active()._edit.domain == "EDGE"
    assert active().value == 0  # Invocation modifiers must not force a value.
    send("E", "RELEASE", ctrl=True, shift=True)
    send("LEFT_CTRL", "RELEASE", shift=True)
    send("LEFT_SHIFT", "RELEASE")
    send("MOUSEMOVE", "NOTHING", dx=140)
    prefs.hud_anchor = "TOP"
    prefs.hud_font_size = 44


def capture_bevel():
    assert abs(active().value - 0.7) < 0.001, active().value
    screenshot("hud-custom.png")
    send("RET")


def undo_and_change_shortcut():
    assert not operators.ACTIVE
    assert all(abs(value - 0.7) < 0.001 for value in values("bevel_weight_edge", edge=True))
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.ed.undo()
    assert values("bevel_weight_edge", edge=True) is None
    keymap = bpy.context.window_manager.keyconfigs.user.keymaps["Mesh"]
    item = next(item for item in keymap.keymap_items if item.idname == "pie.shift_e" and item.properties.attr_name == "crease")
    item.type = "Q"
    prefs.hud_anchor = "CURSOR"
    prefs.hud_background = False
    prefs.hud_show_help = False
    prefs.hud_show_bar = False
    send("Q", shift=True)


def capture_cursor():
    assert active().attribute_kind == "crease"
    screenshot("hud-cursor.png")


def extreme_style():
    prefs.hud_background = True
    prefs.hud_show_help = True
    prefs.hud_show_bar = True
    prefs.hud_font_size = 96
    prefs.hud_corner_radius = 32
    prefs.hud_offset_x = 2000
    prefs.hud_offset_y = 2000
    active()._set_value(1)


def capture_extreme():
    screenshot("hud-large-rounded.png")
    prefs.hud_corner_radius = 0
    active()._set_value(0)


def capture_square():
    screenshot("hud-square-zero.png")
    send("ESC")


def show_preferences():
    assert not operators.ACTIVE
    prefs.hud_anchor = "BOTTOM"
    prefs.hud_background = True
    prefs.hud_show_help = True
    prefs.hud_show_bar = True
    prefs.hud_font_size = 38
    prefs.hud_corner_radius = 16
    prefs.hud_offset_x = 0
    prefs.hud_offset_y = 60
    bpy.utils.register_class(QCW_PT_smoke_preferences)
    area.type = "PREFERENCES"
    bpy.context.preferences.active_section = "ADDONS"
    bpy.context.window_manager.addon_search = "Quick Crease Weight"
    area.tag_redraw()


def finish():
    assert draw_count > 0
    assert pref_draw_count > 0
    assert not draw_errors, "\n".join(draw_errors)
    screenshot("preferences.png")
    (OUTPUT / "ui-result.json").write_text(json.dumps({
        "success": True, "blender": bpy.app.version_string,
        "hud_draws": draw_count, "preference_draws": pref_draw_count,
        "checks": ["Shift+E vertex crease", "Ctrl+Shift+E edge bevel weight", "cancel restore",
                   "confirm and undo", "custom shortcut", "separate right-hand hints", "preferences layout",
                   "large font and corner radius", "square corners", "zero and full progress"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    bpy.utils.unregister_class(QCW_PT_smoke_preferences)
    unregister()
    bpy.ops.wm.quit_blender()


steps = iter((lambda: send("ESC"), setup, start_crease, adjust_crease, move_crease, capture_crease, start_bevel,
              adjust_bevel, capture_bevel, undo_and_change_shortcut, capture_cursor,
              extreme_style, capture_extreme, capture_square, show_preferences, finish))


def tick():
    try:
        next(steps)()
        return 1.0
    except StopIteration:
        return None
    except Exception:
        error = traceback.format_exc()
        screenshot("failure.png")
        (OUTPUT / "ui-result.json").write_text(json.dumps({
            "success": False, "error": error, "draw_errors": draw_errors,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(error, flush=True)
        os._exit(1)


bpy.app.timers.register(tick, first_interval=3.0)
