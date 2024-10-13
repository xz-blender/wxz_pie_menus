from collections import defaultdict
from typing import List, Dict, Union

import bpy
from bpy.types import Object, Material, Collection
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bmesh.types import BMFace


def group_by_material(targets: List[bpy.types.Object]) -> Dict[Material, List[Object]]:
    """ Group objects in a dict of {Material: [obj, ...]}"""
    groups = defaultdict(list)
    for target in targets:
        materials = [slot.material for slot in target.material_slots]
        for material in materials:
            groups[material].append(target)
    return groups


def group_by_collection(targets: List[bpy.types.Object]) -> Dict[Collection, List[Object]]:
    """ Group objects in a dict of {Collection: [obj, ...]}"""
    groups = defaultdict(list)
    for target in targets:
        for collection in target.users_collection:
            groups[collection].append(target)
    return groups


def get_material_index(obj: Object, material: Material) -> Union[int, None]:
    """ Check object material slots for material and return index if found, else return None """
    for indx, slot in enumerate(obj.material_slots):
        if slot.material == material:
            return indx
    return None

def is_backface(viewpoint: Vector, view_normal: Vector, face: BMFace, bvh: BVHTree, check_obscured: bool = True, ortho: bool = False):
    if ortho:
        return view_normal.dot(face.normal) < 0.0

    origin = face.verts[0]
    ray = viewpoint - origin
    ray_dir = ray.normalized()
    distance = ray.length
    ray_result = bvh.ray_cast(ray_dir, distance=distance)
    dot = face.normal.dot(view_normal)
    is_facing = dot < 0.0

    if check_obscured:
        return all((None not in ray_result, is_facing))
    return is_facing

