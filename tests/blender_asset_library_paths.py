"""Run with Blender --background --factory-startup --python-exit-code 1 --python this_file.

Load only the preset operator and helper to avoid enabling the add-on and applying
unrelated user preferences. No preferences are saved.
"""

import ast
import json
from collections import OrderedDict
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "operator" / "change_assets_lib.py"
tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
tree.body = [
    node
    for node in tree.body
    if isinstance(node, (ast.ClassDef, ast.FunctionDef))
    and node.name in {"PIE_Change_Assets_library_Path", "change_assets_library_path"}
]

with TemporaryDirectory() as temporary:
    sync = Path(temporary) / "sync"
    local = Path(temporary) / "local"
    (sync / "GN").mkdir(parents=True)
    (local / "Poly Haven").mkdir(parents=True)
    preferences = SimpleNamespace(assets_library_path_sync=str(sync), assets_library_path_local=str(local))
    namespace = {
        "__name__": "asset_library_path_test",
        "__file__": str(SOURCE),
        "bpy": bpy,
        "json": json,
        "Path": Path,
        "OrderedDict": OrderedDict,
        "get_prefs": lambda: preferences,
        "addon_name": lambda: "Asset library path test",
    }
    exec(compile(tree, str(SOURCE), "exec"), namespace)
    execute = namespace["PIE_Change_Assets_library_Path"].execute
    libraries = bpy.context.preferences.filepaths.asset_libraries
    for library in list(libraries):
        libraries.remove(library)
    for name in ("Higssas", "wxz_nodes"):
        libraries.new(name=name, directory=str(ROOT / "nodes_presets" / name))
    libraries["Higssas"].import_method = "LINK"
    unrelated = libraries.new(name="Unrelated", directory=temporary)
    operator = SimpleNamespace(remove=False)

    assert execute(operator, bpy.context) == {"FINISHED"}
    for name in ("Higssas", "wxz_nodes"):
        assert Path(libraries[name].path) == ROOT / "assets" / "blends" / "nodes" / name
    assert libraries["Higssas"].import_method == "LINK"
    assert Path(libraries["GN"].path) == sync / "GN"
    assert libraries["GN"].import_method in {"APPEND_REUSE", "APPEND"}
    assert Path(libraries["Poly Haven"].path) == local / "Poly Haven"
    assert libraries["Poly Haven"].import_method == "LINK"
    count = len(libraries)
    execute(operator, bpy.context)
    assert len(libraries) == count, "Repeated addition must not duplicate libraries"
    assert libraries["Unrelated"] == unrelated

    operator.remove = True
    execute(operator, bpy.context)
    assert not operator.remove
    assert set(library.name for library in libraries) == {"Unrelated"}
    execute(operator, bpy.context)
    assert len(libraries) == count
    for name in ("Higssas", "wxz_nodes"):
        assert Path(libraries[name].path) == ROOT / "assets" / "blends" / "nodes" / name

print("PASS: preset add, old-path migration, missing external paths, repeated add, remove and re-add")
