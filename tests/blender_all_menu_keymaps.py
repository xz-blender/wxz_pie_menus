"""Full feature toggles: exact ownership and trigger-preserving reload cycles."""

import importlib
import sys
from pathlib import Path
import addon_utils
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
errors = []
addon = addon_utils.enable(ROOT.name, default_set=True, handle_error=lambda: errors.append(sys.exc_info()))
assert addon and not errors, errors
kc = bpy.context.window_manager.keyconfigs


def signature(config):
    return [
        (
            km.name,
            km.space_type,
            km.region_type,
            [
                (k.idname, k.type, k.value, k.any, k.shift, k.ctrl, k.alt, k.oskey, k.key_modifier, k.active)
                for k in km.keymap_items
            ],
        )
        for km in config.keymaps
    ]


from bl_keymap_utils.keymap_hierarchy import generate

contexts = {}


def visit(rows):
    for name, space, region, children in rows:
        contexts.setdefault(name, set()).add((space, region))
        visit(children)


visit(generate())
before = signature(kc.default)
menus = [mod for mod in addon.all_modules_dir["pie_modules"] if hasattr(mod, "register_keymaps")]
items = importlib.import_module(f"{ROOT.name}.items")
try:
    for module in menus:
        name = module.__name__.rsplit(".", 1)[-1]
        addon._lifecycle.set_enabled(name, True)
        status = addon._lifecycle.status(name)
        assert not status.errors, (name, status)
        for km, kmi in module.addon_keymaps:
            assert km.name in contexts, (name, "unknown keymap", km.name)
            assert (km.space_type, km.region_type) in contexts[km.name], (
                name,
                km.name,
                km.space_type,
                contexts[km.name],
            )
        first = tuple((km.as_pointer(), kmi.as_pointer()) for km, kmi in module.addon_keymaps)
        assert first, name
        module.register_keymaps()
        assert first == tuple((km.as_pointer(), kmi.as_pointer()) for km, kmi in module.addon_keymaps), name
        assert signature(kc.default) == before, name
        addon._lifecycle.set_enabled(name, False)
        assert not module.addon_keymaps, name
        assert not addon._lifecycle.status(name).errors, addon._lifecycle.status(name)
        addon._lifecycle.set_enabled(name, True)
        assert not addon._lifecycle.status(name).errors, addon._lifecycle.status(name)
        addon._lifecycle.set_enabled(name, False)
        assert signature(kc.default) == before, name
        print("PASS:", name, "owned keymaps enable/repeat/disable/re-enable/disable")
    assert not items.All_Pie_keymaps, items.All_Pie_keymaps
    print("PASS: all", len(menus), "menu modules, no registry leftovers")
finally:
    addon_utils.disable(ROOT.name, default_set=True)
