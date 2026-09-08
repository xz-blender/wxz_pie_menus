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
    "set_pie_ridius": lambda: None,
    "get_ob_type": lambda context: context.object.type,
    "get_ob_mode": lambda context: context.object.mode,
    "get_area_ui_type": lambda context: "VIEW_3D",
}
exec(compile(ast.Module(body=[draw], type_ignores=[]), str(source_path), "exec"), scope)
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
        pass

    def operator(self, operator_id, **kwargs):
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
