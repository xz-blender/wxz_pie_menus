import bpy
from bpy.app.handlers import persistent

from ..utils import get_prefs, manage_app_handlers

bl_info = {
    "name": "Auto Active Camera Switcher",
    "blender": (4, 2, 0),
    "version": (1, 0, 2),
    "author": "Yamato3D-3dnchu.com",
    "description": "Automatically sets selected camera as active when selected.",
    "location": "View3D > Sidebar",
    "category": "3D View",
}


@persistent
def switch_to_active_camera(scene=None):
    obj = bpy.context.view_layer.objects.active
    if obj and obj.type == "CAMERA":
        if get_prefs().AutoSwitch_ActiveCam_Default:
            bpy.context.scene.camera = obj


def register():
    manage_app_handlers(["depsgraph_update_post"], switch_to_active_camera)


def unregister():
    manage_app_handlers(["depsgraph_update_post"], switch_to_active_camera, remove=True)
