"""Run with Blender --background --factory-startup --python-exit-code 1 --python this_file.

Exercise the actual menu draw and modifier invoke methods against Blender RNA,
without enabling the full add-on or modifying user preferences.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

import bmesh
import bpy


ROOT = Path(__file__).resolve().parents[1]


def load_definitions(relative_path, names, namespace):
    path = ROOT / relative_path
    source = ast.parse(path.read_text(encoding="utf-8"))
    body = [
        node
        for node in source.body
        if (
            isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names
            or isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id in names for target in node.targets)
        )
    ]
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


scope = {
    "bpy": bpy,
    "Menu": bpy.types.Menu,
    "Operator": bpy.types.Operator,
    "get_pyfilename": lambda: "A",
    "set_pie_ridius": lambda: None,
    "get_ob_type": lambda context: context.object.type,
    "get_ob_mode": lambda context: context.object.mode,
    "get_area_ui_type": lambda context: "VIEW_3D",
}
load_definitions("pie/utils.py", {"operator_exists"}, scope)
load_definitions("pie/A_pie.py", {"PIE_MT_Bottom_A"}, scope)
load_definitions(
    "pie/Modifier_bar.py",
    {"BOOLEAN_FAST_SOLVER", "numbers", "modifier_props", "add_custom_boolean", "PIE_PT_Bar_AddCustomModifier"},
    scope,
)


class RNAProperties:
    def __init__(self, rna):
        object.__setattr__(self, "rna", rna)

    def __setattr__(self, name, value):
        if name not in self.rna.properties:
            raise AttributeError(f"{self.rna.identifier} has no property {name!r}")
        object.__setattr__(self, name, value)


class MenuLayout:
    """Mirror UILayout.operator's missing-operator behavior using real RNA."""

    def __init__(self):
        self.buttons = []

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

    def operator(self, identifier, **kwargs):
        category, name = identifier.split(".")
        try:
            rna = getattr(getattr(bpy.ops, category), name).get_rna_type()
        except (AttributeError, KeyError, RuntimeError):
            self.buttons.append((identifier, kwargs, None))
            return None
        props = RNAProperties(rna)
        self.buttons.append((identifier, kwargs, props))
        return props


class PieCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.created_objects = []
        self.original_collections = set(bpy.data.collections)
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        self.active = self.new_mesh("CompatibilityTarget")
        bpy.context.view_layer.objects.active = self.active

    def new_mesh(self, name):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.select_set(True)
        self.created_objects.append(obj)
        return obj

    def tearDown(self):
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        for obj in self.created_objects:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
        for collection in set(bpy.data.collections) - self.original_collections:
            bpy.data.collections.remove(collection)

    def test_edit_mesh_menu_draw(self):
        # A regular quad grid distinguishes a connected edge loop from a ring
        # of parallel edges, so the test also checks each button's behavior.
        vertices = [(x, y, 0) for y in range(5) for x in range(5)]
        faces = [
            (y * 5 + x, y * 5 + x + 1, (y + 1) * 5 + x + 1, (y + 1) * 5 + x)
            for y in range(4)
            for x in range(4)
        ]
        self.active.data.from_pydata(vertices, [], faces)
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        bpy.ops.object.mode_set(mode="EDIT")
        layout = MenuLayout()
        scope["PIE_MT_Bottom_A"].draw(SimpleNamespace(layout=layout), bpy.context)
        missing = [identifier for identifier, _, props in layout.buttons if props is None]
        self.assertEqual(missing, [], "Menu buttons must reference registered operators")
        buttons = [
            (identifier, props)
            for identifier, options, props in layout.buttons
            if options.get("text") in ("循环边", "并排边")
        ]
        self.assertEqual(len(buttons), 2)
        if "select_edge_loop_multi" in dir(bpy.ops.mesh):
            self.assertEqual(
                [identifier for identifier, _ in buttons],
                ["mesh.select_edge_loop_multi", "mesh.select_edge_ring_multi"],
            )
        else:
            self.assertEqual([identifier for identifier, _ in buttons], ["mesh.loop_multi_select"] * 2)
            self.assertEqual([props.ring for _, props in buttons], [False, True])

        expected_edges = [
            {frozenset(((x, 2, 0), (x + 1, 2, 0))) for x in range(4)},
            {frozenset(((2, y, 0), (3, y, 0))) for y in range(5)},
        ]
        for (identifier, props), expected in zip(buttons, expected_edges):
            with self.subTest(operator=identifier):
                bpy.ops.mesh.select_all(action="DESELECT")
                bm = bmesh.from_edit_mesh(self.active.data)
                seed = next(
                    edge for edge in bm.edges
                    if {tuple(vertex.co) for vertex in edge.verts} == {(2, 2, 0), (3, 2, 0)}
                )
                seed.select_set(True)
                bmesh.update_edit_mesh(self.active.data)
                category, name = identifier.split(".")
                options = {name: value for name, value in vars(props).items() if name != "rna"}
                self.assertEqual(getattr(getattr(bpy.ops, category), name)(**options), {"FINISHED"})
                selected = {
                    frozenset(tuple(vertex.co) for vertex in edge.verts)
                    for edge in bmesh.from_edit_mesh(self.active.data).edges if edge.select
                }
                self.assertEqual(selected, expected)

    def assert_boolean(self, operand_count, *, shift=False, ctrl=False):
        operands = [self.new_mesh(f"Operand{index}") for index in range(operand_count)]
        event = SimpleNamespace(type_prev="NONE", shift=shift, ctrl=ctrl, alt=False)
        result = scope["PIE_PT_Bar_AddCustomModifier"].invoke(
            SimpleNamespace(type="BOOLEAN"), bpy.context, event
        )
        self.assertEqual(result, {"FINISHED"})
        self.assertEqual(len(self.active.modifiers), 1)
        modifier = self.active.modifiers[0]
        solvers = modifier.bl_rna.properties["solver"].enum_items.keys()
        self.assertEqual(modifier.solver, "FLOAT" if "FLOAT" in solvers else "FAST")
        self.assertEqual(modifier.operation, "INTERSECT" if ctrl else "UNION" if shift else "DIFFERENCE")
        if operand_count == 1:
            self.assertEqual(modifier.object, operands[0])
        elif operand_count > 1:
            self.assertEqual(modifier.operand_type, "COLLECTION")
            self.assertEqual(set(modifier.collection.objects), set(operands))
        for obj in operands:
            self.assertEqual(obj.display_type, "WIRE")

    def test_boolean_without_operands(self):
        self.assert_boolean(0)

    def test_boolean_object_operand(self):
        self.assert_boolean(1)

    def test_boolean_collection_operands(self):
        self.assert_boolean(2)

    def test_boolean_shift_union(self):
        self.assert_boolean(1, shift=True)

    def test_boolean_ctrl_intersect(self):
        self.assert_boolean(1, ctrl=True)


if __name__ == "__main__":
    print(f"Testing Blender {bpy.app.version_string}", flush=True)
    result = unittest.main(argv=[__file__], exit=False, verbosity=2).result
    if not result.wasSuccessful():
        raise RuntimeError("Pie compatibility regression tests failed")
