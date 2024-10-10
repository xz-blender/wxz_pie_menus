bl_info = {
    "name": "Auto material",
    "description": "Some materials handling tools",
    "author": "Samuel Bernou",
    "version": (0, 3, 0),
    "blender": (2, 91, 0),
    "location": "Properties > Material > Settings",
    "warning": "",
    "doc_url": "https://github.com/Pullusb/autoMat",
    "tracker_url": "https://github.com/Pullusb/autoMat/issues",
    "category": "Material",
}

from . import auto_rename, clean_gp_slots, clean_slots, set_color, ui


def register():
    auto_rename.register()
    set_color.register()
    clean_slots.register()
    clean_gp_slots.register()
    ui.register()


def unregister():
    ui.unregister()
    auto_rename.unregister()
    clean_gp_slots.unregister()
    clean_slots.unregister()
    set_color.unregister()


if __name__ == "__main__":
    register()
