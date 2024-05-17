import json
import os
import re
import uuid
from pathlib import Path

import bpy

txt_prefix = """
# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"\n
VERSION 1\n
"""
assets_cats_text_path = Path(__file__).parent / "blender_assets_cats.txt"
cwf_name = Path(bpy.data.filepath).stem
text = ""


def add_line(text, cat_path) -> str:
    text += "%s:%s:%s\n" % (uuid.uuid4(), cat_path, str(cat_path).replace("\\", "/").replace("/", "-"))
    return text


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


def test1():
    for node in modifier_node_tree.nodes:
        if node.type == "FRAME":
            print("Frame:", node.node_tree.name)
            pass
        if node.type == "GROUP":
            print("Group:", node.node_tree.name)

    if assets_cats_text_path.exists():
        with open(assets_cats_text_path, "w") as f:
            data = json.load(f)
            json.dump(data, f)


def set_cat_uuid(ob, cat_name):
    ob.asset_mark()
    ob.asset_generate_preview()
    with assets_cats_text_path.open() as f:
        for line in f.readlines():
            if line.startswith(("#", "VERSION", "\n")):
                continue
            name = line.split(":")[2].split("\n")[0]
            if name == cat_name:
                uuid = line.split(":")[0]
                # Object name, case-sensitive !
                asset_data = ob.asset_data
                asset_data.catalog_id = uuid


def write_file(path, text):
    with open(path, "w") as f:
        f.write(text)


if cwf_name == "GN_Nodes":
    print("______________GNYes!\n")
    text = txt_prefix
    all_nodes = bpy.data.node_groups["GN_ALL_NODES"]
    all_nodes_name = all_nodes.name
    text = add_line(text, all_nodes_name)

    for node in all_nodes.nodes:
        if node.type == "FRAME":
            text = add_line(text, Path(all_nodes_name) / node.label)


elif cwf_name == "SN_Nodes":
    all_nodes = bpy.data.materials["SN_ALL_NODES"]

elif cwf_name == "CN_Nodes":
    all_nodes = bpy.data.node_groups

write_file(assets_cats_text_path, text)

bpy.ops.wm.save_mainfile()
