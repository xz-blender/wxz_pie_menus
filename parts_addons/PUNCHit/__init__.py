old_bl_info = {
    "name": "PUNCHit",
    "author": "MACHIN3",
    "version": (1, 2, 0),
    "blender": (3, 6, 0),
    "location": "",
    "description": "Manifold Extrude that works.",
    "warning": "",
    "doc_url": "https://machin3.io/PUNCHit/docs",
    "category": "Mesh",
}


import bpy

from .extrude import PunchIt


def register():
    bpy.utils.register_class(PunchIt)


def unregister():
    bpy.utils.unregister_class(PunchIt)
