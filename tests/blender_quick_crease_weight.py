# SPDX-License-Identifier: GPL-3.0-or-later
# Adapted from Quick Crease Weight 1.2.1 integration tests.
"""Run in factory-startup Blender; does not save or alter user preferences."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quick_crease_weight_support import addon, e_pie, operators, preferences, WeightEdit, register, unregister

register()


def event(kind, value="PRESS", x=100, shift=False, ctrl=False, alt=False):
    return SimpleNamespace(type=kind, value=value, mouse_x=x, mouse_region_x=x,
                           mouse_region_y=200, shift=shift, ctrl=ctrl, alt=alt)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        operators.cancel_active()
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        mesh = bpy.data.meshes.new("test_mesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
        self.obj = bpy.data.objects.new("test_object", mesh)
        bpy.context.collection.objects.link(self.obj)
        self.obj.select_set(True)
        bpy.context.view_layer.objects.active = self.obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        bpy.ops.mesh.select_all(action="SELECT")
        self.bm = bmesh.from_edit_mesh(mesh)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()

    def tearDown(self):
        operators.cancel_active()
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

    def values(self, name, domain="POINT", bm=None):
        bm = bm if bm is not None else self.bm
        elements = bm.verts if domain == "POINT" else bm.edges
        layer = elements.layers.float.get(name)
        self.assertIsNotNone(layer)
        return [element[layer] for element in elements]

    def test_all_four_attributes_and_face_domain(self):
        for kind in ("crease", "bevel_weight"):
            for mode, suffix, domain in (((True, False, False), "vert", "POINT"),
                                         ((False, True, False), "edge", "EDGE"),
                                         ((False, False, True), "edge", "EDGE")):
                with self.subTest(kind=kind, mode=mode):
                    bpy.context.tool_settings.mesh_select_mode = mode
                    edit = WeightEdit(bpy.context, kind)
                    edit.apply(0.625)
                    self.assertEqual(self.values(f"{kind}_{suffix}", domain), [0.625] * 4)
                    self.assertEqual(edit.domain, domain)
                    edit.restore()

    def test_cancel_restores_mixed_values_and_untouched_elements(self):
        layer = self.bm.verts.layers.float.new("crease_vert")
        original = [0.125, 0.25, 0.75, 1.0]
        for vertex, value in zip(self.bm.verts, original):
            vertex[layer] = value
        self.bm.verts[3].select_set(False)
        edit = WeightEdit(bpy.context, "crease")
        self.assertEqual(edit.initial_value, 0.375)
        edit.apply(0.5)
        self.assertEqual(self.values("crease_vert"), [0.5, 0.5, 0.5, 1.0])
        edit.restore()
        self.assertEqual(self.values("crease_vert"), original)

    def test_cancel_removes_new_layer_and_clamps(self):
        edit = WeightEdit(bpy.context, "bevel_weight")
        self.assertIsNone(self.bm.verts.layers.float.get("bevel_weight_vert"))
        edit.apply(20)
        self.assertEqual(self.values("bevel_weight_vert"), [1.0] * 4)
        edit.apply(-10)
        self.assertEqual(self.values("bevel_weight_vert"), [0.0] * 4)
        edit.restore()
        self.assertIsNone(self.bm.verts.layers.float.get("bevel_weight_vert"))

    def test_repeated_values_skip_updates_without_skipping_first_average(self):
        layer = self.bm.verts.layers.float.new("crease_vert")
        original = [0.25, 0.75, 0.25, 0.75]
        for element, value in zip(self.bm.verts, original):
            element[layer] = value
        edit = WeightEdit(bpy.context, "crease")
        with patch.object(WeightEdit, "_update", wraps=WeightEdit._update) as update:
            edit.apply(edit.initial_value)
            self.assertEqual(self.values("crease_vert"), [0.5] * 4)
            edit.apply(0.5)
            self.assertEqual(update.call_count, 1)
            edit.apply(3)
            edit.apply(2)
            self.assertEqual(update.call_count, 2)
            self.assertEqual(self.values("crease_vert"), [1] * 4)
        edit.restore()
        self.assertEqual(self.values("crease_vert"), original)
        edit.apply(0.5)
        self.assertEqual(self.values("crease_vert"), [0.5] * 4)
        edit.restore()

    def test_layer_creation_between_writes_preserves_targets_and_cancel(self):
        edit = WeightEdit(bpy.context, "crease")
        edit.apply(0.25)
        self.bm.verts.layers.float.new("unrelated_attribute")
        edit.apply(0.75)
        self.assertEqual(self.values("crease_vert"), [0.75] * 4)
        edit.restore()
        self.assertIsNone(self.bm.verts.layers.float.get("crease_vert"))
        self.assertIsNotNone(self.bm.verts.layers.float.get("unrelated_attribute"))

    def test_hidden_and_empty_selection(self):
        self.bm.verts[0].hide = True
        edit = WeightEdit(bpy.context, "crease")
        self.assertEqual(edit.count, 3)
        edit.apply(1)
        self.assertEqual(self.values("crease_vert"), [0, 1, 1, 1])
        bpy.ops.mesh.select_all(action="DESELECT")
        with self.assertRaisesRegex(ValueError, "请先选择"):
            WeightEdit(bpy.context, "crease")

    def test_wrong_attribute_type_does_not_mutate(self):
        self.bm.verts.layers.int.new("crease_vert")
        bmesh.update_edit_mesh(self.obj.data)
        with self.assertRaisesRegex(ValueError, "浮点属性"):
            WeightEdit(bpy.context, "crease")
        self.assertIsNone(self.bm.verts.layers.float.get("crease_vert"))

    def test_multi_object_and_shared_data(self):
        bpy.ops.object.mode_set(mode="OBJECT")
        other = self.obj.copy()
        other.data = self.obj.data.copy()
        bpy.context.collection.objects.link(other)
        other.select_set(True)
        linked = self.obj.copy()
        bpy.context.collection.objects.link(linked)
        linked.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        edit = WeightEdit(bpy.context, "crease")
        self.assertEqual(len(edit.snapshots), 2)
        self.assertEqual(edit.count, 8)
        edit.apply(0.75)
        for snapshot in edit.snapshots:
            self.assertEqual(self.values("crease_vert", bm=snapshot.bm), [0.75] * 4)
        edit.restore()
        for snapshot in edit.snapshots:
            self.assertIsNone(snapshot.bm.verts.layers.float.get("crease_vert"))

    def test_real_registered_execute_and_poll(self):
        for kind, attribute in (("crease", "crease_vert"), ("bevel_weight", "bevel_weight_vert")):
            # Exercise the existing public operator and its saved RNA arguments.
            result = bpy.ops.pie.shift_e(attr_name=kind, set_value=0.5)
            self.assertEqual(result, {"FINISHED"})
            self.assertEqual(self.values(attribute), [0.5] * 4)
        bpy.ops.object.mode_set(mode="OBJECT")
        self.assertFalse(bpy.ops.pie.shift_e.poll())

    def test_preferences_and_registration_cycle(self):
        prefs = preferences.get_preferences(bpy.context)
        self.assertIsNotNone(prefs)
        prefs.hud_font_size = 48
        prefs.hud_anchor = "CURSOR"
        parent = addon.get_addon_preferences()
        for _ in range(2):
            self.assertEqual(len(e_pie.addon_keymaps), 3)
            mesh_keys = [(km, item) for km, item in e_pie.addon_keymaps if item.idname == "pie.shift_e"]
            self.assertEqual(len(mesh_keys), 2)
            for _keymap, item in mesh_keys:
                self.assertEqual(item.type, "E")
                self.assertTrue(item.shift)
                self.assertEqual(item.ctrl, item.properties.attr_name == "bevel_weight")
            # Use the host's actual module checkbox, not just the helper methods.
            parent.use_E_pie = False
            self.assertEqual(e_pie.addon_keymaps, [])
            self.assertIsNone(bpy.types.Operator.bl_rna_get_subclass_py("PIE_Shift_E_KEY", None))
            parent.use_E_pie = True
            self.assertEqual(prefs.hud_font_size, 48)
            self.assertEqual(prefs.hud_anchor, "CURSOR")

    def test_module_disable_restores_active_edit_and_releases_caches(self):
        op = self.make_modal()
        op._hud = object()
        op._set_value(0.75)
        prefs = addon.get_addon_preferences()
        prefs.use_E_pie = False
        self.assertIsNone(self.bm.verts.layers.float.get("crease_vert"))
        self.assertEqual(operators.ACTIVE, [])
        self.assertIsNone(op._hud)
        self.assertIsNone(op._edit)
        self.assertEqual(op.modal(bpy.context, event("MOUSEMOVE")), {"CANCELLED"})
        prefs.use_E_pie = True

    def test_repeated_registration_does_not_duplicate_keys(self):
        from wxz_pie_menus.items import All_Pie_keymaps

        for _ in range(2):
            e_pie.register()
            self.assertEqual(len(e_pie.addon_keymaps), 3)
            self.assertEqual(len(All_Pie_keymaps), 3)
            for name in ("Mesh", "3D View"):
                km = bpy.context.window_manager.keyconfigs.addon.keymaps[name]
                entries = [item for item in km.keymap_items if item.idname == "pie.shift_e"
                           or item.idname == "wm.call_menu_pie"
                           and item.properties.name == "VIEW3D_PIE_MT_Bottom_E"]
                self.assertEqual(len(entries), 2 if name == "Mesh" else 1)
        e_pie.unregister()
        self.assertEqual(All_Pie_keymaps, [])
        e_pie.register()

    def test_shared_mesh_in_mixed_selection_mode(self):
        bpy.context.tool_settings.mesh_select_mode = (True, True, False)
        edit = WeightEdit(bpy.context, "bevel_weight")
        self.assertEqual(edit.domain, "POINT")
        edit.apply(0.25)
        self.assertEqual(self.values("bevel_weight_vert"), [0.25] * 4)
        self.assertIsNone(self.bm.edges.layers.float.get("bevel_weight_edge"))

    def make_modal(self, kind="crease", initial_event=None):
        # A plain harness executes the production modal methods without putting
        # synthetic operators into Blender's real window event queue.
        class Harness(operators.WeightOperator):
            attribute_kind = kind
            display_name = "测试"

        op = Harness()
        op._edit = WeightEdit(bpy.context, kind)
        op.value = op._edit.initial_value
        op._area, op._region, op._workspace = bpy.context.area, bpy.context.region, bpy.context.workspace
        op._origin_x, op._origin_value = 100, op.value
        op._blocked_modifiers = set()
        if initial_event:
            op._blocked_modifiers = {key for key in ("shift", "ctrl", "alt") if getattr(initial_event, key)}
        op._closed, op._navigating, op._handle = False, False, None
        op._sensitivity = 0.005
        operators.ACTIVE.append(op)
        return op

    def test_modal_shortcut_modifiers_snap_ctrl_alt_cancel(self):
        op = self.make_modal("bevel_weight", event("E", shift=True, ctrl=True))
        op.modal(bpy.context, event("MOUSEMOVE", x=150, shift=True, ctrl=True))
        self.assertAlmostEqual(op.value, 0.25)
        op.modal(bpy.context, event("LEFT_CTRL", "RELEASE", x=150, shift=True))
        op.modal(bpy.context, event("LEFT_SHIFT", "RELEASE", x=150))
        op.modal(bpy.context, event("LEFT_SHIFT", x=150, shift=True))
        op.modal(bpy.context, event("MOUSEMOVE", x=172, shift=True))
        self.assertAlmostEqual(op.value, 0.4)
        op.modal(bpy.context, event("LEFT_CTRL", x=172, ctrl=True))
        self.assertEqual(op.value, 1)
        op.modal(bpy.context, event("LEFT_CTRL", "RELEASE", x=172))
        op.modal(bpy.context, event("LEFT_ALT", x=172, alt=True))
        self.assertEqual(op.value, 0)
        op.modal(bpy.context, event("LEFT_ALT", "RELEASE", x=172))
        op.modal(bpy.context, event("MOUSEMOVE", x=192))
        self.assertAlmostEqual(op.value, 0.1)
        self.assertEqual(op.modal(bpy.context, event("ESC")), {"CANCELLED"})
        self.assertIsNone(self.bm.verts.layers.float.get("bevel_weight_vert"))
        self.assertEqual(operators.ACTIVE, [])

    def test_modal_confirm_navigation_and_disable(self):
        op = self.make_modal()
        op.modal(bpy.context, event("MIDDLEMOUSE"))
        op.modal(bpy.context, event("MOUSEMOVE", x=300))
        self.assertFalse(op._edit.changed)
        op.modal(bpy.context, event("MIDDLEMOUSE", "RELEASE", x=300))
        op.modal(bpy.context, event("MOUSEMOVE", x=350))
        self.assertEqual(op.value, 0.25)
        self.assertEqual(op.modal(bpy.context, event("RET")), {"FINISHED"})
        self.assertIsNone(op._edit)
        self.assertIsNone(op._hud)
        self.assertEqual(self.values("crease_vert"), [0.25] * 4)
        op = self.make_modal()
        op.modal(bpy.context, event("LEFT_CTRL", ctrl=True))
        operators.cancel_active()
        self.assertEqual(self.values("crease_vert"), [0.25] * 4)
        self.assertEqual(operators.ACTIVE, [])

    def test_stationary_mouse_preserves_mixed_values_and_repeat_snap_skips_update(self):
        layer = self.bm.verts.layers.float.new("crease_vert")
        original = [0.125, 0.25, 0.75, 0.875]
        for element, value in zip(self.bm.verts, original):
            element[layer] = value
        op = self.make_modal()
        op.modal(bpy.context, event("MOUSEMOVE", x=100))
        self.assertFalse(op._edit.changed)
        self.assertEqual(self.values("crease_vert"), original)
        with patch.object(WeightEdit, "_update", wraps=WeightEdit._update) as update:
            op.modal(bpy.context, event("MOUSEMOVE", x=120, shift=True))
            op.modal(bpy.context, event("MOUSEMOVE", x=121, shift=True))
            op.modal(bpy.context, event("MOUSEMOVE", x=122, shift=True))
            self.assertEqual(update.call_count, 1)
        op.modal(bpy.context, event("ESC"))
        self.assertEqual(self.values("crease_vert"), original)


area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
region = next(region for region in area.regions if region.type == "WINDOW")
with bpy.context.temp_override(area=area, region=region):
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTests))
unregister()
print(f"Blender {bpy.app.version_string}: {result.testsRun} checks; success={result.wasSuccessful()}")
if not result.wasSuccessful():
    raise SystemExit(1)
