import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, PointerProperty
from bpy.types import AddonPreferences, Operator, Panel, PropertyGroup

from ..utils import get_prefs

bl_info = {
    "name": "Auto Active Camera Switcher",
    "blender": (4, 2, 0),
    "version": (1, 0, 2),
    "author": "Yamato3D-3dnchu.com",
    "description": "Automatically sets selected camera as active when selected.",
    "location": "View3D > Sidebar",
    "category": "3D View",
}


class AutoActiveCameraProps(PropertyGroup):
    enable_auto_switch: BoolProperty(
        name="自动激活相机", description="自动将所选相机设置为活动项", default=False
    )  # type: ignore


def switch_to_active_camera(scene=None):
    obj = bpy.context.view_layer.objects.active
    if obj and obj.type == "CAMERA":
        if bpy.context.scene.pie_auto_active_camera_props.enable_auto_switch:
            bpy.context.scene.camera = obj


@persistent
def on_scene_load_post(dummy=None):
    print("场景已加载，正在初始化自动相机开关...")

    if bpy.context.scene:
        prefs = get_prefs()
        bpy.context.scene.pie_auto_active_camera_props.enable_auto_switch = prefs.default_enable

    if switch_to_active_camera not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(switch_to_active_camera)


class VIEW3D_PT_auto_active_camera(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "View"
    bl_label = "启用自动相机切换器"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.pie_auto_active_camera_props, "enable_auto_switch")


def register():
    bpy.utils.register_class(AutoActiveCameraProps)
    bpy.types.Scene.pie_auto_active_camera_props = PointerProperty(type=AutoActiveCameraProps)
    bpy.utils.register_class(VIEW3D_PT_auto_active_camera)

    # Add persistent handlers for scene load and camera change
    bpy.app.handlers.load_post.append(on_scene_load_post)


def unregister():
    bpy.utils.unregister_class(AutoActiveCameraProps)
    if hasattr(bpy.types.Scene, "pie_auto_active_camera_props"):
        del bpy.types.Scene.pie_auto_active_camera_props
    bpy.utils.unregister_class(VIEW3D_PT_auto_active_camera)

    # Remove handlers
    if switch_to_active_camera in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(switch_to_active_camera)

    if on_scene_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_scene_load_post)


if __name__ == "__main__":
    register()
