"""Exercise isolated preset copy, with synthetic default data in background mode."""

import importlib
import sys
from pathlib import Path
from types import ModuleType
import bpy

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "wxz_preset_test"
pkg = ModuleType(PACKAGE)
pkg.__package__ = PACKAGE
pkg.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = pkg
mod = importlib.import_module(PACKAGE + ".operator.change_keys")
kc = bpy.context.window_manager.keyconfigs
# Background Blender has no initialized default maps; seed this disposable test
# process only. The actual preset operation must leave them byte-for-byte intact.
mesh = kc.default.keymaps.new(name="Mesh")
k = mesh.keymap_items.new("mesh.edge_face_add", "F", "PRESS")
modal = kc.default.keymaps.new(name="Test Modal", modal=True)
modal.keymap_items.new_modal("CONFIRM", "RET", "PRESS")


def snapshot(config):
    return [
        (
            km.name,
            km.space_type,
            km.region_type,
            km.is_modal,
            [(k.idname, k.type, k.value, k.active) for k in km.keymap_items],
        )
        for km in config.keymaps
    ]


before_default = snapshot(kc.default)
before_user = snapshot(kc.user)
active = kc.active
handlers = {
    name: tuple(getattr(bpy.app.handlers, name)) for name in ("load_pre", "load_post", "load_factory_startup_post")
}


def legacy(_):
    raise AssertionError("legacy keymap writer should never run")


legacy.__module__ = mod.__name__
legacy.__name__ = "run_set_load_xz_keys_presets"
bpy.app.handlers.load_post.append(legacy)
mod.register()
assert legacy not in bpy.app.handlers.load_post

try:
    assert bpy.ops.pie.load_xz_keys_presets() == {"FINISHED"}
    preset = kc.get("XZ Pie (Independent)")
    assert preset and len(preset.keymaps) == len(kc.default.keymaps)
    assert snapshot(kc.default) == before_default
    assert snapshot(kc.user) == before_user
    assert kc.active == active
    assert preset.keymaps["Mesh"].keymap_items[0].value == "CLICK"
    assert bpy.ops.pie.load_xz_keys_presets() == {"CANCELLED"}, "never overwrite existing preset"
    assert {name: tuple(getattr(bpy.app.handlers, name)) for name in handlers} == handlers
    print("PASS: separate manual XZ keyconfig, modal copy, no default/user/active/handler changes, no overwrite")
finally:
    mod.unregister()
