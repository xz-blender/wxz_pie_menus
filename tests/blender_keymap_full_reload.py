"""Preserve native user shortcuts through complete add-on disable/re-enable.

Run with scripts/blender_dev.py --test tests/blender_keymap_full_reload.py. The
launcher supplies a disposable profile. No desktop or user profile is touched.
"""

import importlib
from pathlib import Path
import sys

import addon_utils
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
# Background Blender starts without the full standard keymap.
preset = next(Path(path) / "Blender.py" for path in bpy.utils.preset_paths("keyconfig")
              if (Path(path) / "Blender.py").is_file())
bpy.utils.execfile(str(preset))
kc = bpy.context.window_manager.keyconfigs


def enable():
    errors = []
    addon = addon_utils.enable(ROOT.name, default_set=True, handle_error=lambda: errors.append(sys.exc_info()))
    assert addon is not None and not errors, errors
    addon._lifecycle.set_enabled("F_pie", True)
    statuses = [addon._lifecycle.status(module.__name__.rsplit(".", 1)[-1]) for module in addon.all_modules]
    assert all(not status.errors for status in statuses), statuses
    assert bpy.types.Operator.bl_rna_get_subclass_py("WXZ_INTERNAL_OT_keymap_type_refresh", None) is None
    kc.update()
    return addon


def binding():
    matches = [item for item in kc.user.keymaps["Mesh"].keymap_items if item.idname == "pie.mesh_f_gesture"]
    assert len(matches) == 1, [(item.id, item.type) for item in matches]
    return matches[0]


def event_signature(item):
    return (item.type, item.value, item.any, item.shift, item.ctrl, item.alt, item.oskey,
            item.key_modifier, item.active, item.repeat)


def config_snapshot(config):
    return [(km.name, km.space_type, km.region_type, [(item.id, item.idname, event_signature(item))
             for item in km.keymap_items]) for km in config.keymaps]


addon = enable()
try:
    default_before = config_snapshot(kc.default)
    custom = binding()
    custom.type, custom.value, custom.ctrl, custom.alt = "J", "CLICK_DRAG", 1, 1
    expected = event_signature(custom)
    kc.update()
    # Repeated operator-type cleanup while F is dormant used to convert the
    # saved diff's RNA to generic properties on Blender 4.3, even with no second
    # keymap removal. This catches the bug independently of full teardown order.
    addon._lifecycle.set_enabled("F_pie", False)
    addon._lifecycle.set_enabled("test_operators", False)
    addon._lifecycle.set_enabled("F_pie", True)
    kc.update()
    assert event_signature(binding()) == expected, ("dormant feature", event_signature(binding()), expected)
    addon._lifecycle.set_enabled("test_operators", True)
    print("PASS: dormant F customization survives unrelated operator cleanup", flush=True)

    for cycle in range(3):
        # The enabled preference entry remains during an in-session reload.
        addon_utils.disable(ROOT.name, default_set=False)
        kc.update()
        assert not addon_utils.check(ROOT.name)[1]
        addon = enable()
        assert event_signature(binding()) == expected, ("full reload", cycle, event_signature(binding()), expected)
        assert config_snapshot(kc.default) == default_before
        print(f"PASS: full addon_utils.disable/enable preserves native user shortcut, cycle {cycle + 1}", flush=True)

    # addon_utils itself unregisters an already-enabled add-on before enabling.
    for cycle in range(2):
        addon = enable()
        assert event_signature(binding()) == expected, ("repeated enable", cycle, event_signature(binding()), expected)
        assert config_snapshot(kc.default) == default_before
        print(f"PASS: repeated addon_utils.enable preserves native user shortcut, cycle {cycle + 1}", flush=True)

    # The ordinary preferences disable path removes the add-on preference entry.
    addon_utils.disable(ROOT.name, default_set=True)
    kc.update()
    addon = enable()
    assert event_signature(binding()) == expected, ("preference disable/re-enable", event_signature(binding()), expected)
    assert config_snapshot(kc.default) == default_before
    ui = importlib.import_module(f"{ROOT.name}.module.keymaps_ui")
    f_menu = importlib.import_module(f"{ROOT.name}.pie.F_pie")
    template_map, template = next((km, kmi) for km, kmi in f_menu.addon_keymaps
                                  if kmi.idname == "pie.mesh_f_gesture")
    resolved = ui.resolve_user_item(kc, template_map, template)
    assert resolved is not None and resolved[1].id == binding().id
    assert template.type == "F" and not template.ctrl and not template.alt
    print("PASS: preferences disable/re-enable, safe native UI lookup, unchanged default and add-on template", flush=True)
finally:
    addon_utils.disable(ROOT.name, default_set=True)
    assert bpy.types.Operator.bl_rna_get_subclass_py("WXZ_INTERNAL_OT_keymap_type_refresh", None) is None
