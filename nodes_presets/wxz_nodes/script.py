# 只支持一层级子类别！
import json
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path

import bpy

txt_prefix = f"""
# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with `#` will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"

VERSION 1\n
"""

assets_catstext_path = Path(__file__).parent / "blender_assets.cats.txt"
blends_save_time_path = Path(__file__).parent / "blends_savetime.txt"
sep = os.path.sep
date_format = "%Y-%m-%d %H:%M:%S"
cwf_path = Path(bpy.data.filepath)
cwf_name = Path(bpy.data.filepath).stem


def creat_blens_savetime_file():
    with open(blends_save_time_path, "w") as file:
        json.dump(
            {
                "GN_Nodes_SaveTime": "",
                "SN_Nodes_SaveTime": "",
                "CN_Nodes_SaveTime": "",
            },
            file,
        )


def read_save_time(blend_name):
    with open(blends_save_time_path, "r", encoding="utf-8") as file:
        load = json.load(file)
        date_str = load[blend_name]
    return datetime.strptime(date_str, date_format)


def get_file_modification_time(file_path):
    mod_time_epoch = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mod_time_epoch)


def write_save_time(cwf_path, blend_name):
    with open(blends_save_time_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        # data[blend_name] = str(get_file_modification_time(cwf_path))

    mod_time = os.path.getmtime(cwf_path)
    # 格式化修改时间
    formatted_time = datetime.fromtimestamp(mod_time).strftime(date_format)
    # 更新字典中的时间
    data[blend_name] = formatted_time

    with open(blends_save_time_path, "w") as file:
        json.dump(data, file, indent=4)


def write_current_time(blend_name):
    with open(blends_save_time_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        # data[blend_name] = str(get_file_modification_time(cwf_path))

    current_time = datetime.now().strftime(date_format)
    # 更新字典中的时间
    data[blend_name] = current_time

    with open(blends_save_time_path, "w") as file:
        json.dump(data, file, indent=4)


def r_slash(input_string):
    return input_string.replace("\\", "/")


def r_slack(input_string):
    return input_string.replace("/", "-")


def add_line(cat_path):
    return "{a}:{b}:{c}\n".format(a=str(uuid.uuid4()), b=cat_path, c=r_slack(r_slash(cat_path)))


def set_cat_uuid(ob, cat_name):
    ob.asset_mark()
    ob.asset_generate_preview()
    with assets_catstext_path.open() as f:
        for line in f.readlines():
            if line.startswith(("#", "VERSION", "\n")):
                continue
            name = line.split(":")[2].split("\n")[0]
            if name == cat_name:
                uuid = line.split(":")[0]
                asset_data = ob.asset_data
                asset_data.catalog_id = uuid


def write_file(path, text):
    with open(path, "w") as f:
        f.write(text)


def change_default_cats_and_blends(all_nodes, cwf_name, cwf_path):

    nosign_name = "No Sign"
    others_cat = cwf_name + sep + nosign_name
    savetime_blend_key = cwf_name + "_SaveTime"
    if assets_catstext_path.exists() and blends_save_time_path.exists():

        save_time = read_save_time(savetime_blend_key)
        print("save_time:", save_time)
        last_time = get_file_modification_time(cwf_path)
        print("last_time:", last_time)
        print((last_time - save_time).total_seconds())
        if (last_time - save_time).total_seconds() > 30:
            for node in all_nodes.nodes:
                if node.type == "GROUP":
                    tree = node.node_tree
                    if node.parent == None:
                        set_cat_uuid(tree, f"{cwf_name}-{nosign_name}")
                    else:
                        set_cat_uuid(tree, f"{cwf_name}-{node.parent.label}")

            bpy.ops.wm.save_mainfile()
            # write_save_time(assets_catstext_path, savetime_blend_key)
            print(f"WXZ_Default_Nodes:'{cwf_name}'", "File And Cats File Saved Change!")
            write_save_time(cwf_path, savetime_blend_key)

    else:
        # 添加大类文件夹
        text = txt_prefix + add_line(cwf_name)
        # 添加 没分类的节点组,存放为other类
        text += add_line(others_cat)

        # 添加下一级子文件夹
        for node in all_nodes.nodes:
            if node.type == "FRAME":
                cat = cwf_name + sep + node.label
                text += add_line(cat)
        # 写入文件
        write_file(assets_catstext_path, r_slash(text))
        # 写入时间戳模板
        creat_blens_savetime_file()
        print("WXZ_Default_Nodes: Save Cats File")

        for node in all_nodes.nodes:
            if node.type == "GROUP":
                tree = node.node_tree
                if node.parent == None:
                    set_cat_uuid(tree, f"{cwf_name}-{nosign_name}")
                else:
                    set_cat_uuid(tree, f"{cwf_name}-{node.parent.label}")

        bpy.ops.wm.save_mainfile()
        write_save_time(cwf_path, savetime_blend_key)
        print(f"WXZ_Default_Nodes:'{cwf_name}'", "File And Cats File Saved Change!")

    # elif cwf_name == "SN_Nodes":
    #     all_nodes = bpy.data.materials["SN_ALL_NODES"]

    # elif cwf_name == "CN_Nodes":
    #     all_nodes = bpy.data.node_groups


if cwf_name == "GN_Nodes":
    all_nodes = bpy.data.node_groups["GN_ALL_NODES"]
    change_default_cats_and_blends(all_nodes, cwf_name, cwf_path)

# elif cwf_name == "SN_Nodes":
#     all_nodes = bpy.data.materials["SN_ALL_NODES"]
