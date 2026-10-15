"""Read-only keymap diagnostics, native editor targeting, and real RNA mapping.

Run standard tests with unittest; run this file through scripts/blender_dev.py
for the additional Blender tests in an isolated factory profile.
"""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

try:
    import bpy
except ImportError:
    bpy = None

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "wxz_keymaps_ui_test"
package = ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
module_package = ModuleType(f"{PACKAGE}.module")
module_package.__path__ = [str(ROOT / "module")]
sys.modules[module_package.__name__] = module_package
spec = importlib.util.spec_from_file_location(f"{PACKAGE}.module.keymaps_ui", ROOT / "module/keymaps_ui.py")
ui = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ui
spec.loader.exec_module(ui)


class Items(list):
    def from_id(self, identifier):
        return next((item for item in self if item.id == identifier), None)


def item(identifier=1, **kwargs):
    values = dict(id=identifier, idname="wm.call_menu_pie", type="F", value="PRESS", active=True,
                  any=False, shift=0, ctrl=0, alt=0, oskey=0, key_modifier="NONE", direction="ANY",
                  properties={"name": "PIE_MT_test"}, is_user_modified=False, is_user_defined=False)
    values.update(kwargs)
    return SimpleNamespace(**values)


def keymap(name="Mesh", entries=(), space="EMPTY", region="WINDOW", modal=False):
    return SimpleNamespace(name=name, keymap_items=Items(entries), space_type=space, region_type=region,
                           is_modal=modal)


def config(*maps):
    return SimpleNamespace(keymaps=list(maps))


class KeymapIdentityTests(unittest.TestCase):
    def setUp(self):
        self.templates = [item(7), item(25, properties={"name": "PIE_MT_second"})]
        self.addon = keymap(entries=self.templates)
        self.base = keymap(entries=[item(1, idname="mesh.select_all"), item(9, idname="mesh.edge_face_add")])
        self.customized = item(10, type="G", value="CLICK_DRAG", ctrl=1, active=False, is_user_modified=True)
        self.second = item(11, properties={"name": "PIE_MT_second"})
        self.user = keymap(entries=[self.second, self.customized, *self.base.keymap_items])
        self.kcs = SimpleNamespace(user=config(self.user), active=config(self.base), default=config(self.base))

    def test_merged_id_not_template_id_or_original_event(self):
        self.assertEqual(ui.resolve_user_item(self.kcs, self.addon, self.templates[0]),
                         (self.user, self.customized))
        self.customized.properties = {"name": "USER_EDITED_MENU"}
        self.customized.idname = "wm.call_menu"
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[0])[1], self.customized)

    def test_hidden_preset_counter_is_not_maximum_remaining_id(self):
        # The preset deleted its highest-id items; native kmi_id remains 13.
        self.customized.id, self.second.id = 14, 15
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[0])[1], self.customized)
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[1])[1], self.second)

    def test_ambiguous_modified_identity_is_never_exposed(self):
        self.addon.keymap_items.append(item(30))
        self.customized.id = 12
        self.user.keymap_items = Items([self.customized, *self.base.keymap_items])
        self.assertIsNone(ui.resolve_user_item(self.kcs, self.addon, self.templates[0]))

    def test_same_operator_different_menu_maps_to_own_identity(self):
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[1])[1], self.second)

    def test_removed_item_is_not_recreated_or_replaced_by_template(self):
        self.user.keymap_items.remove(self.customized)
        self.assertIsNone(ui.resolve_user_item(self.kcs, self.addon, self.templates[0]))
        self.assertEqual(len(self.user.keymap_items), 3)

    def test_wrong_unmodified_identity_fails_closed(self):
        self.customized.is_user_modified = False
        self.customized.idname = "mesh.unrelated"
        self.assertIsNone(ui.resolve_user_item(self.kcs, self.addon, self.templates[0]))

    def test_native_find_match_is_preferred(self):
        calls = []
        self.user.keymap_items.find_match = lambda km, kmi: calls.append((km, kmi)) or self.customized
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[0])[1], self.customized)
        self.assertEqual(calls, [(self.addon, self.templates[0])])

    def test_keymap_space_and_region_are_part_of_identity(self):
        wrong = keymap(entries=[item(10)], space="VIEW_3D")
        self.kcs.user.keymaps.insert(0, wrong)
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[0])[0], self.user)
        self.kcs.user = config(wrong)
        self.assertIsNone(ui.resolve_user_item(self.kcs, self.addon, self.templates[0]))

    def test_active_preset_ids_take_precedence_and_default_fallback_works(self):
        self.kcs.active = config()
        self.assertIs(ui.resolve_user_item(self.kcs, self.addon, self.templates[0])[1], self.customized)


class KeymapConflictTests(unittest.TestCase):
    def test_same_key_different_modes_do_not_conflict(self):
        self.assertFalse(ui.keymaps_overlap(keymap("Mesh"), keymap("Object Mode")))
        self.assertFalse(ui.keymaps_overlap(keymap("Mesh"), keymap("Curve")))
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), keymap("3D View", space="VIEW_3D")))
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), keymap("3D View Generic", space="VIEW_3D")))
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), keymap("Object Non-modal")))
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), keymap("Window")))

    def test_editor_region_modal_and_unknown_contexts(self):
        self.assertFalse(ui.keymaps_overlap(keymap("Mesh"), keymap("UV Editor")))
        self.assertFalse(ui.keymaps_overlap(keymap("Mesh"), keymap("Mesh", region="UI")))
        self.assertFalse(ui.keymaps_overlap(keymap("Mesh"), keymap("Transform Modal Map", modal=True)))
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), keymap("Unknown EMPTY map")))
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), keymap("Screen Editing")))
        self.assertTrue(ui.keymaps_overlap(keymap("UV Editor"), keymap("Image", space="IMAGE_EDITOR")))
        self.assertFalse(ui.keymaps_overlap(keymap("UV Editor"), keymap("Image Paint")))

    def test_tools_are_mode_specific(self):
        mesh_tool = keymap("3D View Tool: Edit Mesh, Extrude", space="VIEW_3D")
        object_tool = keymap("3D View Tool: Object, Move", space="VIEW_3D")
        self.assertTrue(ui.keymaps_overlap(keymap("Mesh"), mesh_tool))
        self.assertFalse(ui.keymaps_overlap(keymap("Mesh"), object_tool))
        self.assertFalse(ui.keymaps_overlap(mesh_tool, object_tool))

    def test_event_values_and_press_blocking_are_distinguished(self):
        self.assertEqual(ui.event_relation(item(), item()), "SAME_EVENT")
        self.assertEqual(ui.event_relation(item(value="ANY"), item(value="CLICK_DRAG")), "SAME_EVENT")
        self.assertEqual(ui.event_relation(item(), item(value="CLICK_DRAG")), "PRESS_BLOCKS_GESTURE")
        self.assertEqual(ui.event_relation(item(value="CLICK"), item()), "GESTURE_BLOCKED_BY_PRESS")
        self.assertIsNone(ui.event_relation(item(value="CLICK"), item(value="CLICK_DRAG")))
        self.assertIsNone(ui.event_relation(item(type="G"), item()))
        self.assertIsNone(ui.event_relation(item(active=False), item()))

    def test_modifier_wildcards_and_key_modifier(self):
        self.assertIsNone(ui.event_relation(item(ctrl=1), item()))
        self.assertEqual(ui.event_relation(item(ctrl=-1), item(ctrl=1)), "SAME_EVENT")
        self.assertEqual(ui.event_relation(item(any=True), item(ctrl=1, alt=1, shift=1)), "SAME_EVENT")
        self.assertIsNone(ui.event_relation(item(any=True, key_modifier="D"), item(key_modifier="NONE")))
        self.assertEqual(ui.event_relation(item(key_modifier="D"), item(key_modifier="D")), "SAME_EVENT")
        self.assertIsNone(ui.event_relation(item(hyper=1), item(hyper=0)))

    def test_drag_directions(self):
        self.assertIsNone(ui.event_relation(item(value="CLICK_DRAG", direction="NORTH"),
                                            item(value="CLICK_DRAG", direction="SOUTH")))
        self.assertEqual(ui.event_relation(item(value="CLICK_DRAG", direction="ANY"),
                                           item(value="CLICK_DRAG", direction="SOUTH")), "SAME_EVENT")

    def test_operator_and_menu_properties_are_distinct(self):
        a, b = item(), item(properties={"name": "PIE_MT_other"})
        self.assertNotEqual(ui.operator_signature(a), ui.operator_signature(b))
        own = keymap(entries=[a, b])
        b.id = 2
        kc = SimpleNamespace(user=config(own), default=config())
        found = ui.find_conflicts(kc, own, a)
        self.assertEqual(len(found), 1)
        self.assertFalse(found[0].same_action)
        b.properties = dict(a.properties)
        self.assertTrue(ui.find_conflicts(kc, own, a)[0].same_action)

    def test_mesh_default_is_expected_fallback_and_f2_is_real_conflict(self):
        dispatcher = item(5, idname="pie.mesh_f_gesture", properties={})
        face = item(2, idname="mesh.edge_face_add", properties={})
        f2 = item(8, idname="mesh.f2", properties={})
        km = keymap(entries=[dispatcher, face, f2])
        defaults = keymap(entries=[item(2, idname="mesh.edge_face_add", properties={})])
        kc = SimpleNamespace(user=config(km), default=config(defaults))
        found = ui.find_conflicts(kc, km, dispatcher)
        self.assertEqual([(c.item.idname, c.kind) for c in found],
                         [("mesh.edge_face_add", "EXPECTED_FALLBACK"), ("mesh.f2", "SAME_EVENT")])
        face.is_user_modified = True
        self.assertEqual(ui.find_conflicts(kc, km, dispatcher)[0].kind, "SAME_EVENT")

    def test_unknown_context_is_reported_as_uncertain(self):
        own = item(1)
        km = keymap(entries=[own])
        unknown = keymap("Third Party Context", entries=[item(2)])
        kc = SimpleNamespace(user=config(km, unknown), default=config())
        found = ui.find_conflicts(kc, km, own)
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].context_uncertain)

    def test_duplicate_default_addon_copies_are_not_reported(self):
        own = item()
        km = keymap(entries=[own])
        kc = SimpleNamespace(user=config(km), default=config(km), addon=config(km))
        self.assertEqual(ui.find_conflicts(kc, km, own), [])

    def test_reads_do_not_mutate_either_configuration(self):
        own, peer = item(1), item(2, idname="mesh.f2")
        km = keymap(entries=[own, peer])
        kc = SimpleNamespace(user=config(km), default=config(keymap(entries=[item(3)])))
        before = repr(kc)
        ui.find_conflicts(kc, km, own)
        ui.event_label(peer)
        self.assertEqual(repr(kc), before)


class Layout:
    def __init__(self):
        self.labels = []
        self.pointers = []

    def box(self):
        return self

    def row(self):
        return self

    def column(self):
        return self

    def prop(self, *_args, **_kwargs):
        pass

    def label(self, **kwargs):
        self.labels.append(kwargs)

    def context_pointer_set(self, key, value):
        self.pointers.append((key, value))


class NativeDrawingTests(unittest.TestCase):
    setUp = KeymapIdentityTests.setUp

    def test_native_ui_receives_user_config_and_customized_item(self):
        calls = []
        items_module = ModuleType(f"{PACKAGE}.items")
        items_module.All_Pie_keymaps = [(self.addon, self.templates[0])]
        renderer = ModuleType("rna_keymap_ui")
        renderer.draw_kmi = lambda *args: calls.append(args)
        prefs = SimpleNamespace(show_pie_keymaps=True, show_pie_keymap_conflicts=True, pie_keymap_filter="")
        context = SimpleNamespace(window_manager=SimpleNamespace(keyconfigs=self.kcs))
        layout = Layout()
        with patch.dict(sys.modules, {items_module.__name__: items_module, "rna_keymap_ui": renderer}):
            ui.draw_keymaps(prefs, context, layout)
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0][1], self.kcs.user)
        self.assertIs(calls[0][2], self.user)
        self.assertIs(calls[0][3], self.customized)
        self.assertIn(("keymap", self.user), layout.pointers)
        self.assertIn(("keyconfig", self.kcs.user), layout.pointers)


@unittest.skipIf(bpy is None, "Requires Blender; use scripts/blender_dev.py --test tests/test_keymaps_ui.py")
class BlenderKeymapUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Background Blender does not initialize its full standard keymap.
        paths = bpy.utils.preset_paths("keyconfig")
        preset = next(Path(path) / "Blender.py" for path in paths if (Path(path) / "Blender.py").is_file())
        bpy.utils.execfile(str(preset))
        cls.kc = bpy.context.window_manager.keyconfigs

    def test_native_private_counter_after_highest_preset_id_deleted(self):
        kc = self.kc
        previous = kc.active
        preset = kc.new("WXZ keymap identity probe")
        base = preset.keymaps.new(name="Mesh")
        for key in ("ONE", "TWO", "THREE"):
            last = base.keymap_items.new("mesh.select_all", key, "PRESS")
        base.keymap_items.remove(last)  # max visible id=2, native counter=3.
        km = kc.addon.keymaps.new(name="Mesh")
        first = km.keymap_items.new("wm.call_menu_pie", "F11", "PRESS")
        first.properties.name = "WXZ_MT_private_counter_first"
        second = km.keymap_items.new("wm.call_menu_pie", "F12", "PRESS")
        second.properties.name = "WXZ_MT_private_counter_second"
        try:
            kc.active = preset
            kc.update()
            user_map, custom = ui.resolve_user_item(kc, km, first)
            self.assertEqual(custom.id, 4)
            custom.type, custom.ctrl = "J", 1
            kc.update()
            self.assertEqual(ui.resolve_user_item(kc, km, first)[1].id, 4)
            self.assertEqual(ui.resolve_user_item(kc, km, first)[1].type, "J")
            self.assertEqual(ui.resolve_user_item(kc, km, second)[1].id, 5)
        finally:
            km.keymap_items.remove(first)
            km.keymap_items.remove(second)
            kc.update()
            kc.active = previous
            kc.remove(preset)
            kc.update()

    def test_real_rna_fallback_f2_and_read_only_diagnostics(self):
        class Dispatcher(bpy.types.Operator):
            bl_idname = "pie.mesh_f_gesture"
            bl_label = "Test F dispatcher"

            def execute(self, context):
                return {"CANCELLED"}

        class F2(bpy.types.Operator):
            bl_idname = "mesh.f2"
            bl_label = "Test F2 peer"

            def execute(self, context):
                return {"CANCELLED"}

        kc = self.kc
        bpy.utils.register_class(Dispatcher)
        bpy.utils.register_class(F2)
        km = kc.addon.keymaps.new(name="Mesh")
        own = km.keymap_items.new(Dispatcher.bl_idname, "F", "PRESS")
        peer = km.keymap_items.new(F2.bl_idname, "F", "PRESS")
        try:
            kc.update()
            user_map, effective = ui.resolve_user_item(kc, km, own)
            def snapshot():
                return [(c.name, m.name, k.id, ui.event_label(k), ui.operator_signature(k), k.active)
                        for c in (kc.default, kc.addon, kc.user) for m in c.keymaps for k in m.keymap_items]
            before = snapshot()
            found = ui.find_conflicts(kc, user_map, effective)
            by_operator = {conflict.item.idname: conflict for conflict in found}
            self.assertEqual(by_operator["mesh.edge_face_add"].kind, "EXPECTED_FALLBACK")
            self.assertEqual(by_operator["mesh.f2"].kind, "SAME_EVENT")
            self.assertNotIn(Dispatcher.bl_idname, by_operator)
            self.assertEqual(snapshot(), before)
        finally:
            km.keymap_items.remove(own)
            km.keymap_items.remove(peer)
            kc.update()
            bpy.utils.unregister_class(F2)
            bpy.utils.unregister_class(Dispatcher)

    def test_real_user_remap_survives_lookup_draw_and_native_restore(self):
        kc = self.kc
        km = kc.addon.keymaps.new(name="Mesh")
        templates = []
        for index, key in enumerate(("F10", "F11", "F12")):
            entry = km.keymap_items.new("wm.call_menu_pie", key, "PRESS")
            entry.properties.name = "WXZ_MT_native_probe" if index != 1 else "WXZ_MT_other_probe"
            templates.append(entry)
        try:
            kc.update()
            default_before = [(k.id, k.idname, ui.event_label(k), ui.operator_signature(k))
                              for k in kc.default.keymaps["Mesh"].keymap_items]
            resolved = [ui.resolve_user_item(kc, km, template) for template in templates]
            self.assertTrue(all(resolved))
            self.assertEqual(len({entry.id for _map, entry in resolved}), 3)
            user_map, custom = resolved[0]
            custom_id = custom.id
            self.assertNotEqual(custom_id, templates[0].id)
            custom.type, custom.value, custom.ctrl = "G", "CLICK_DRAG", 1
            custom.active = False
            custom.properties.name = "WXZ_MT_user_changed_menu"
            kc.update()
            user_map, custom = ui.resolve_user_item(kc, km, templates[0])
            self.assertEqual((custom.id, custom.type, custom.value, custom.ctrl, custom.active),
                             (custom_id, "G", "CLICK_DRAG", 1, False))
            self.assertEqual(custom.properties.name, "WXZ_MT_user_changed_menu")
            self.assertEqual(templates[0].type, "F10")
            for _ in range(3):
                self.assertEqual(ui.resolve_user_item(kc, km, templates[0])[1].id, custom_id)
                ui.find_conflicts(kc, user_map, custom)
            self.assertEqual([(k.id, k.idname, ui.event_label(k), ui.operator_signature(k))
                              for k in kc.default.keymaps["Mesh"].keymap_items], default_before)
            # Native restore preserves the same native id and restores only this user item.
            user_map.restore_item_to_default(custom)
            kc.update()
            user_map, custom = ui.resolve_user_item(kc, km, templates[0])
            self.assertEqual((custom.id, custom.type, custom.value, custom.ctrl, custom.active),
                             (custom_id, "F10", "PRESS", 0, True))
            self.assertEqual(custom.properties.name, "WXZ_MT_native_probe")
            user_map.keymap_items.remove(custom)
            kc.update()
            self.assertIsNone(ui.resolve_user_item(kc, km, templates[0]))
            self.assertIsNotNone(ui.resolve_user_item(kc, km, templates[2]))
        finally:
            for template in templates:
                km.keymap_items.remove(template)
            kc.update()


if __name__ == "__main__":
    result = unittest.main(argv=[__file__], exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("Keymap UI regressions failed")
