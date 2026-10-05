"""Run with Blender --background --factory-startup --python-exit-code 1 --python this_file."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import bmesh
import bpy


ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / "pie" / "A_pie.py"
source = ast.parse(source_path.read_text(encoding="utf-8"))
menu = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "PIE_MT_Bottom_A")
draw = next(node for node in menu.body if isinstance(node, ast.FunctionDef) and node.name == "draw")
scope = {
    "bpy": bpy,
    "Operator": bpy.types.Operator,
    "add_operator": lambda layout, *args, **kwargs: layout.separator(),
    "set_pie_ridius": lambda: None,
    "get_ob_type": lambda context: context.object.type,
    "get_ob_mode": lambda context: context.object.mode,
    "get_area_ui_type": lambda context: "VIEW_3D",
}
exec(compile(ast.Module(body=[draw], type_ignores=[]), str(source_path), "exec"), scope)
selection_operator = next(
    node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "PIE_Select_Same_Mesh_Count"
)
exec(compile(ast.Module(body=[selection_operator], type_ignores=[]), str(source_path), "exec"), scope)
utils_path = ROOT / "pie" / "utils.py"
utils_source = ast.parse(utils_path.read_text(encoding="utf-8"))
operator_exists = next(
    node for node in utils_source.body if isinstance(node, ast.FunctionDef) and node.name == "operator_exists"
)
exec(compile(ast.Module(body=[operator_exists], type_ignores=[]), str(utils_path), "exec"), scope)


class RegistryLayout:
    """Record buttons, using the running Blender's real operator/property registry."""

    def __init__(self):
        self.buttons = []
        self.missing = []
        self.entries = []

    def menu_pie(self):
        return self

    def split(self):
        return self

    def box(self):
        return self

    def column(self, **kwargs):
        return self

    def row(self, **kwargs):
        return self

    def separator(self, **kwargs):
        self.entries.append(None)

    def label(self, **kwargs):
        pass

    def menu(self, identifier, **kwargs):
        self.entries.append(identifier)

    def operator(self, operator_id, **kwargs):
        self.entries.append(operator_id)
        category, name = operator_id.split(".")
        try:
            getattr(getattr(bpy.ops, category), name).get_rna_type()
        except (KeyError, AttributeError):
            # UILayout.operator returns None when an operator is unregistered.
            self.missing.append(operator_id)
            return None
        properties = SimpleNamespace()
        self.buttons.append((operator_id, kwargs, properties))
        return properties


class SameMeshCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.operator = scope["PIE_Select_Same_Mesh_Count"]
        bpy.utils.register_class(cls.operator)

    @classmethod
    def tearDownClass(cls):
        bpy.utils.unregister_class(cls.operator)

    def setUp(self):
        self.area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        self.region = next(region for region in self.area.regions if region.type == "WINDOW")
        for obj in bpy.context.view_layer.objects:
            obj.select_set(False)
        self.reference = self.new_mesh("Reference", 4, faces=[(0, 1, 2, 3)])
        self.same_vertices = self.new_mesh("Same vertices", 4, faces=[(0, 1, 2)])
        self.same_edges = self.new_mesh("Same edges", 5, edges=[(0, 1), (1, 2), (2, 3), (3, 4)])
        self.same_faces = self.new_mesh("Same faces", 3, faces=[(0, 1, 2)])
        self.different = self.new_mesh("Different", 2, edges=[(0, 1)])
        self.empty = bpy.data.objects.new("Non-mesh", None)
        self.addCleanup(bpy.data.objects.remove, self.empty, do_unlink=True)
        bpy.context.scene.collection.objects.link(self.empty)
        self.empty.select_set(True)
        bpy.context.view_layer.objects.active = self.reference

    def new_mesh(self, name, vertex_count, edges=(), faces=()):
        mesh = bpy.data.meshes.new(name)
        self.addCleanup(bpy.data.meshes.remove, mesh)
        mesh.from_pydata([(index, index % 2, 0) for index in range(vertex_count)], edges, faces)
        obj = bpy.data.objects.new(name, mesh)
        self.addCleanup(bpy.data.objects.remove, obj, do_unlink=True)
        bpy.context.scene.collection.objects.link(obj)
        obj.select_set(True)
        return obj

    def viewport(self):
        return bpy.context.temp_override(area=self.area, region=self.region)

    def assert_selection(self, expected):
        self.assertEqual(set(bpy.context.selected_objects), set(expected))
        self.assertIs(bpy.context.view_layer.objects.active, self.reference)

    def test_counts_match_independently_and_keep_active_object(self):
        expected = {
            "VERTICES": [self.reference, self.same_vertices],
            "EDGES": [self.reference, self.same_edges],
            "FACES": [self.reference, self.same_vertices, self.same_faces],
        }
        with self.viewport():
            for count_type, objects in expected.items():
                with self.subTest(count_type=count_type):
                    self.assertEqual(bpy.ops.pie.select_same_mesh_count(count_type=count_type), {"FINISHED"})
                    self.assert_selection(objects)

    def test_default_uses_original_vertex_count_before_modifiers(self):
        self.reference.modifiers.new("Count before subdivision", "SUBSURF")
        with self.viewport():
            self.assertEqual(bpy.ops.pie.select_same_mesh_count(), {"FINISHED"})
            self.assert_selection([self.reference, self.same_vertices])

    def test_hidden_unselectable_and_other_scene_objects_are_ignored(self):
        hidden = self.new_mesh("Hidden", 4)
        hidden.hide_set(True)
        disabled = self.new_mesh("Disabled in viewport", 4)
        disabled.hide_viewport = True
        locked = self.new_mesh("Selection locked", 4)
        locked.hide_select = True
        other_scene = bpy.data.scenes.new("Other scene")
        self.addCleanup(bpy.data.scenes.remove, other_scene)
        outside = self.new_mesh("Other scene object", 4)
        other_scene.collection.objects.link(outside)
        bpy.context.scene.collection.objects.unlink(outside)
        bpy.context.view_layer.update()
        ignored = [hidden, disabled, locked]
        before = [obj.select_get() for obj in ignored]
        with self.viewport():
            self.assertEqual(bpy.ops.pie.select_same_mesh_count(), {"FINISHED"})
            self.assertTrue(self.reference.select_get())
            self.assertTrue(self.same_vertices.select_get())
            self.assertFalse(self.different.select_get())
        self.assertEqual([obj.select_get() for obj in ignored], before)
        self.assertNotIn(outside, bpy.context.view_layer.objects[:])

    def test_local_view_does_not_change_selection_outside_view(self):
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        self.reference.select_set(True)
        self.different.select_set(True)
        with self.viewport():
            bpy.ops.view3d.localview(frame_selected=False)
            try:
                # Selected objects outside local view must retain their state.
                self.same_faces.select_set(True)
                bpy.ops.pie.select_same_mesh_count()
                self.assertTrue(self.reference.select_get())
                self.assertFalse(self.different.select_get())
                self.assertFalse(self.same_vertices.select_get())
                self.assertTrue(self.same_faces.select_get())
            finally:
                bpy.ops.view3d.localview(frame_selected=False)

    def test_menu_right_slot_defaults_to_vertices(self):
        layout = RegistryLayout()
        with self.viewport():
            scope["draw"](SimpleNamespace(layout=layout), bpy.context)
        self.assertEqual(layout.entries[1], self.operator.bl_idname)
        properties = next(props for identifier, _, props in layout.buttons if identifier == self.operator.bl_idname)
        self.assertEqual(properties.count_type, "VERTICES")
        self.assertNotIn(self.operator.bl_idname, layout.missing)

    def test_poll_requires_mesh_in_object_mode_and_3d_view(self):
        with self.viewport():
            self.assertTrue(bpy.ops.pie.select_same_mesh_count.poll())
            bpy.context.view_layer.objects.active = self.empty
            self.assertFalse(bpy.ops.pie.select_same_mesh_count.poll())
            bpy.context.view_layer.objects.active = None
            self.assertFalse(bpy.ops.pie.select_same_mesh_count.poll())
            bpy.context.view_layer.objects.active = self.reference
            bpy.ops.object.mode_set(mode="EDIT")
            try:
                self.assertFalse(bpy.ops.pie.select_same_mesh_count.poll())
            finally:
                bpy.ops.object.mode_set(mode="OBJECT")
        other_area = next(area for area in bpy.context.screen.areas if area.type != "VIEW_3D")
        with bpy.context.temp_override(area=other_area):
            self.assertFalse(bpy.ops.pie.select_same_mesh_count.poll())

    def test_invoke_opens_dialog_without_changing_selection(self):
        calls = []
        context = SimpleNamespace(
            window_manager=SimpleNamespace(
                invoke_props_dialog=lambda operator, **kwargs: calls.append((operator, kwargs)) or {"RUNNING_MODAL"}
            )
        )
        operator = SimpleNamespace()
        before = set(bpy.context.selected_objects)
        self.assertEqual(self.operator.invoke(operator, context, None), {"RUNNING_MODAL"})
        self.assertEqual(calls, [(operator, {"width": 360})])
        self.assertEqual(set(bpy.context.selected_objects), before)


class APieTests(unittest.TestCase):
    def setUp(self):
        mesh = bpy.data.meshes.new("A pie selection regression")
        self.addCleanup(bpy.data.meshes.remove, mesh)
        mesh.from_pydata(
            [(x, y, 0) for y in range(5) for x in range(5)],
            [],
            [(y * 5 + x, y * 5 + x + 1, (y + 1) * 5 + x + 1, (y + 1) * 5 + x)
             for y in range(4) for x in range(4)],
        )
        obj = bpy.data.objects.new("A pie selection regression", mesh)
        self.addCleanup(bpy.data.objects.remove, obj, do_unlink=True)
        bpy.context.collection.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        self.addCleanup(bpy.ops.object.mode_set, mode="OBJECT")
        bpy.ops.mesh.select_mode(type="EDGE")
        self.mesh = mesh

    def draw_menu(self):
        layout = RegistryLayout()
        scope["draw"](SimpleNamespace(layout=layout), bpy.context)
        self.assertEqual(layout.missing, [])
        for operator_id, _, properties in layout.buttons:
            rna_properties = bpy.context.window_manager.operator_properties_last(operator_id)
            for name, value in vars(properties).items():
                setattr(rna_properties, name, value)
        return layout

    def test_mesh_edit_menu_uses_registered_operators(self):
        layout = self.draw_menu()
        for label in ("循环边", "并排边"):
            self.assertEqual(sum(options.get("text") == label for _, options, _ in layout.buttons), 1)

    def test_loop_and_ring_buttons_select_expected_edges(self):
        layout = self.draw_menu()

        def edge_key(edge):
            return frozenset(tuple(vertex.co) for vertex in edge.verts)

        expected = {
            "循环边": {frozenset(((x, 2, 0), (x + 1, 2, 0))) for x in range(4)},
            "并排边": {frozenset(((2, y, 0), (3, y, 0))) for y in range(5)},
        }
        for label, edges in expected.items():
            with self.subTest(button=label):
                bpy.ops.mesh.select_all(action="DESELECT")
                bm = bmesh.from_edit_mesh(self.mesh)
                seed = next(edge for edge in bm.edges if edge_key(edge) == frozenset(((2, 2, 0), (3, 2, 0))))
                seed.select_set(True)
                bm.select_history.clear()
                bm.select_history.add(seed)
                bmesh.update_edit_mesh(self.mesh)
                operator_id, _, properties = next(
                    button for button in layout.buttons if button[1].get("text") == label
                )
                category, name = operator_id.split(".")
                result = getattr(getattr(bpy.ops, category), name)(**vars(properties))
                self.assertEqual(result, {"FINISHED"})
                bm = bmesh.from_edit_mesh(self.mesh)
                self.assertEqual({edge_key(edge) for edge in bm.edges if edge.select}, edges)


if __name__ == "__main__":
    print("Blender:", bpy.app.version_string)
    result = unittest.main(argv=[__file__], exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("A pie menu regression tests failed")
