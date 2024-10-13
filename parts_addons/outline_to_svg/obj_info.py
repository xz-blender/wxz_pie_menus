from collections import defaultdict
from typing import List, Dict, Union

import bpy
from bpy.types import Object, Material, Collection


def get_material_index(obj: Object, material: Material) -> Union[int, None]:
    """Check object material slots for material and return index if found, else return None"""
    for indx, slot in enumerate(obj.material_slots):
        if slot.material == material:
            return indx
    return None
