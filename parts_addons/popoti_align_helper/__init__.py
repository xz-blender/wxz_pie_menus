from . import ops, res, ui

bl_info = {
    "name": "POPOTI Align Helper",
    "description": "More friendly alignment based on observation perspective",
    "author": "AIGODLIKE Community(小萌新)",
    "version": (1, 2, 4),
    "blender": (3, 0, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "辣椒出品",
}

mod_tuple = (
    ops,
    res,
    ui,
)


def register():
    for mod in mod_tuple:
        mod.register()


def unregister():
    for mod in mod_tuple:
        mod.unregister()
