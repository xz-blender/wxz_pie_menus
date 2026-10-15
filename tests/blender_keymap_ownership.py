"""Real RNA ownership regression; run in an isolated Blender profile."""

import importlib
import sys
from pathlib import Path
from types import ModuleType
import bpy

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "wxz_keymap_test"
package = ModuleType(PACKAGE)
package.__package__ = PACKAGE
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
helper = importlib.import_module(f"{PACKAGE}.module.keymaps")
items = importlib.import_module(f"{PACKAGE}.items")
F = importlib.import_module(f"{PACKAGE}.pie.F_pie")


def snapshot(config):
    return [
        (
            km.name,
            km.space_type,
            km.region_type,
            [
                (k.id, k.idname, k.type, k.value, k.any, k.shift, k.ctrl, k.alt, k.oskey, k.key_modifier, k.active)
                for k in km.keymap_items
            ],
        )
        for km in config.keymaps
    ]


kc = bpy.context.window_manager.keyconfigs
before = snapshot(kc.default)
peer_map = kc.addon.keymaps.new(name="Mesh")
peer = peer_map.keymap_items.new("mesh.select_all", "F12", "PRESS")
for cycle in range(3):
    F.register()
    count = sum(len(km.keymap_items) for km in kc.addon.keymaps)
    own = tuple(F.addon_keymaps)
    F.register_keymaps()
    assert tuple(F.addon_keymaps) == own
    assert sum(len(km.keymap_items) for km in kc.addon.keymaps) == count
    assert len({k.as_pointer() for km, k in items.All_Pie_keymaps}) == len(items.All_Pie_keymaps)
    assert any(k.idname == "pie.mesh_f_gesture" and k.type == "F" and k.value == "PRESS" for km, k in F.addon_keymaps)
    assert snapshot(kc.default) == before
    # Simulate a missing RNA item: cleanup must continue for every other item.
    km, kmi = F.addon_keymaps[0]
    km.keymap_items.remove(kmi)
    F.unregister()
    assert not F.addon_keymaps and not items.All_Pie_keymaps
    assert peer_map.keymap_items.from_id(peer.id) == peer
    assert snapshot(kc.default) == before
peer_map.keymap_items.remove(peer)
print("PASS: owned F lifecycle, idempotence, stale item cleanup, peer preservation, unchanged default")

# All menu registrations must be covered and no default/user mutations may return.
import ast

for path in (ROOT / "pie").glob("*.py"):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "register_keymaps":
            assert any(isinstance(d, ast.Name) and d.id == "owned_keymaps" for d in node.decorator_list), path
print("PASS: every menu register_keymaps uses shared ownership")
