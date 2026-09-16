"""Validate the shipped libraries without running the add-on or rewriting blends.

Run with blender --background --factory-startup --disable-autoexec
--python-exit-code 1 --python tests/blender_node_assets.py.
"""

from pathlib import Path
from uuid import UUID

import bpy

LIBRARY = Path(__file__).resolve().parents[1] / "assets" / "blends" / "nodes" / "wxz_nodes"
# Blender's native node asset filter compares AssetMetaData["type"] to the editor's tree type.
LIBRARIES = (
    ("CN_Nodes", "CompositorNodeTree", "CompositorNodeGroup", 1, 18),
    ("GN_Nodes", "GeometryNodeTree", "GeometryNodeGroup", 3, 23),
    ("SN_Nodes", "ShaderNodeTree", "ShaderNodeGroup", 0, 11),
)


def read_catalogs():
    lines = [
        line.strip()
        for line in (LIBRARY / "blender_assets.cats.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert lines.pop(0) == "VERSION 1"
    catalogs = {}
    for line in lines:
        catalog_id, path, simple_name = line.split(":", 2)
        assert UUID(catalog_id).int != 0, line
        assert catalog_id not in catalogs, f"Duplicate catalog UUID: {catalog_id}"
        assert path and simple_name and "\\" not in path, line
        catalogs[catalog_id] = path
    return catalogs


catalogs = read_catalogs()
for filename, tree_type, group_type, metadata_type, expected_count in LIBRARIES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Discover assets through Blender's library reader, including only marked assets.
    with bpy.data.libraries.load(str(LIBRARY / f"{filename}.blend"), assets_only=True) as (source, loaded):
        names = list(source.node_groups)
        assert len(names) == expected_count, (filename, names)
        loaded.node_groups = names

    editor_tree = bpy.data.node_groups.new("Asset placement test", tree_type)
    for group in loaded.node_groups:
        assert group is not None, filename
        assert group.bl_idname == tree_type, (filename, group.name, group.bl_idname)
        asset = group.asset_data
        assert asset is not None, (filename, group.name)
        assert asset.get("type") == metadata_type, (filename, group.name, asset.get("type"))
        assert asset.catalog_id in catalogs, (filename, group.name, "Missing catalog", asset.catalog_id)
        catalog_path = catalogs[asset.catalog_id]
        assert catalog_path == filename or catalog_path.startswith(filename + "/"), (group.name, catalog_path)

        node = editor_tree.nodes.new(group_type)
        node.node_tree = group
        assert node.node_tree == group, (filename, group.name)
        editor_tree.nodes.remove(node)

    print(f"PASS: {filename}: {len(names)} assets, catalogs, native type metadata, and {tree_type} placement")
