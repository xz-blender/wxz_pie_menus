"""Capture README media in a disposable Blender GUI session.

Run with --factory-startup --python this_file -- OUTPUT SCENE.
SCENE is crease, f-object, f-edit, a-edit, d-pie, or preferences.
Never saves a .blend file or user preferences. OUTPUT must be outside the repo.
"""

import importlib
import json
import sys
import traceback
from pathlib import Path

import bmesh
import bpy
from mathutils import Quaternion

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
SCENE = sys.argv[sys.argv.index("--") + 2]
if OUTPUT == ROOT or ROOT in OUTPUT.parents:
    raise ValueError("Use a temporary output directory outside the repository")
OUTPUT.mkdir(parents=True, exist_ok=True)
(OUTPUT / f"{SCENE}.json").write_text('{"success": false}', encoding="utf-8")
sys.path.insert(0, str(ROOT.parent))
addon = importlib.import_module(ROOT.name)
bpy.context.preferences.use_preferences_save = False
entry = bpy.context.preferences.addons.new()
entry.module = addon.__name__
addon.register()
prefs = entry.preferences
bpy.context.preferences.view.language = "zh_HANS"
bpy.context.preferences.view.use_translate_interface = True
bpy.context.preferences.view.use_translate_tooltips = True
bpy.context.preferences.view.ui_scale = 1.5
operators = importlib.import_module(f"{ROOT.name}.module.quick_crease_weight.operators")
window = bpy.context.window
area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")
frames = 0
steps = []
evidence = {"blender": bpy.app.version_string, "captures": [], "crease_values": []}


def capture(name):
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / name))
    evidence["captures"].append(name)


def context_call(function, **kwargs):
    with bpy.context.temp_override(window=window, area=area, region=region):
        return function(**kwargs)


def setup():
    global area, region
    context_call(bpy.ops.screen.screen_full_area, use_hide_panels=True)
    area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            obj.hide_set(True)
    view = area.spaces.active
    view.show_region_toolbar = False
    view.show_region_ui = False
    view.overlay.show_floor = False
    view.overlay.show_axis_x = False
    view.overlay.show_axis_y = False
    view.overlay.show_cursor = False
    view.overlay.show_extras = False
    view.region_3d.view_distance = 7.0
    view.region_3d.view_rotation = Quaternion((0.8205, 0.4247, 0.1759, 0.3399))
    view.region_3d.view_perspective = "ORTHO"
    view.shading.light = "STUDIO"
    view.shading.color_type = "SINGLE"
    view.shading.single_color = (0.42, 0.57, 0.72)
    view.shading.background_type = "WORLD"
    bpy.context.scene.world.color = (0.045, 0.045, 0.045)


def menu(name):
    context_call(bpy.ops.wm.call_menu_pie, name=name)


def edit_mode():
    context_call(bpy.ops.object.mode_set, mode="EDIT")
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    context_call(bpy.ops.mesh.select_all, action="SELECT")


def setup_crease():
    cube = bpy.context.object
    modifier = cube.modifiers.new("README · Subdivision preview", "SUBSURF")
    modifier.levels = 3
    modifier.show_in_editmode = True
    modifier.show_on_cage = False
    qcw = prefs.quick_crease_weight
    qcw.hud_anchor = "BOTTOM"
    qcw.hud_font_size = 32
    qcw.hud_offset_y = 76
    qcw.hud_show_help = True
    qcw.hud_show_bar = True


def crease_frame(expected):
    global frames
    op = operators.ACTIVE[0]
    assert abs(op.value - expected) < 0.001, (op.value, expected)
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    layer = bm.edges.layers.float.get("crease_edge")
    assert layer is not None
    assert all(abs(edge[layer] - expected) < 0.001 for edge in bm.edges if edge.select)
    capture(f"crease-{frames:03d}.png")
    frames += 1
    evidence["crease_values"].append(round(op.value, 2))


def verify_cancel():
    assert not operators.ACTIVE
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    assert bm.edges.layers.float.get("crease_edge") is None
    evidence["cancel_restored_attribute"] = True
    capture("crease-restored.png")


def show_preferences():
    context_call(bpy.ops.object.mode_set, mode="OBJECT")
    area.type = "PREFERENCES"
    bpy.context.preferences.active_section = "ADDONS"
    bpy.context.window_manager.addon_search = "XZ"
    import addon_utils

    addon_utils.modules_refresh()

    # Native AddonPreferences UI, without requiring an installed extension entry.
    class README_PT_preferences(bpy.types.Panel):
        bl_idname = "README_PT_preferences"
        bl_label = "XZ-Blender · 饼菜单与工具"
        bl_space_type = "PREFERENCES"
        bl_region_type = "WINDOW"

        def draw(self, context):
            self.layout.prop(prefs, "tabs", expand=True)
            addon.preferences.panels.draw_addon_menus(prefs, self.layout, context, addon.module_path_name_list)

    bpy.utils.register_class(README_PT_preferences)
    area.tag_redraw()


def finish():
    evidence["success"] = True
    (OUTPUT / f"{SCENE}.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print("README_CAPTURE_OK", json.dumps(evidence, ensure_ascii=False), flush=True)
    bpy.ops.wm.quit_blender()


def start_crease():
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.pie.shift_e("INVOKE_DEFAULT", attr_name="crease")
    assert len(operators.ACTIVE) == 1
    assert operators.ACTIVE[0].attribute_kind == "crease"


# Each menu gets a fresh process, so modal menus cannot overlap in captures.
steps.append(setup)
if SCENE == "crease":
    steps.extend([edit_mode, setup_crease, start_crease])
    for value in [
        0.0,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        0.9,
        0.8,
        0.7,
        0.6,
        0.5,
        0.4,
        0.3,
        0.2,
        0.1,
        0.0,
    ]:
        steps.append(lambda value=value: operators.ACTIVE[0]._set_value(value))
        steps.append(lambda value=value: crease_frame(value))
    steps.extend([operators.cancel_active, verify_cancel])
elif SCENE == "preferences":
    steps.extend([show_preferences, lambda: capture("preferences.png")])
else:
    if SCENE in {"f-edit", "a-edit"}:
        steps.append(edit_mode)
    menu_names = {
        "f-object": "VIEW3D_PIE_MT_Bottom_F",
        "f-edit": "VIEW3D_PIE_MT_Bottom_F",
        "a-edit": "PIE_MT_Bottom_A",
        "d-pie": "VIEW3D_PIE_MT_Bottom_D",
    }
    steps.extend([lambda: menu(menu_names[SCENE]), lambda: capture(f"{SCENE}.png")])
steps.append(finish)
iterator = iter(steps)


def tick():
    try:
        next(iterator)()
        return 0.3
    except StopIteration:
        return None
    except Exception:
        error = traceback.format_exc()
        print(error, flush=True)
        (OUTPUT / "failure.txt").write_text(error, encoding="utf-8")
        capture("failure.png")
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(tick, first_interval=3.0)
