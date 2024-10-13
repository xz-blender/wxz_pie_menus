from collections import defaultdict
from typing import List, Dict, Union

import bpy
from bpy.types import Object, Material, Collection


# def group_obj_by_collection(objects):
#     grouped = defaultdict(list)
#     for obj in objects:
#         first_collection = obj.users_collection[0]
#         grouped[first_collection.name].append(obj)
#     return grouped


def group_by_material(targets: List[bpy.types.Object]) -> Dict[Material, List[Object]]:
    """Group objects in a dict of {Material: [obj, ...]"""
    groups = defaultdict(list)
    for target in targets:
        materials = [slot.material for slot in target.material_slots if slot.material]
        for material in materials:
            groups[material].append(target)
    return groups


def group_by_collection(
    targets: List[bpy.types.Object],
) -> Dict[Collection, List[Object]]:
    """Group objects in a dict of {Collection: [obj, ...]"""
    groups = defaultdict(list)
    for target in targets:
        for collection in target.users_collection:
            groups[collection].append(target)
    return groups
