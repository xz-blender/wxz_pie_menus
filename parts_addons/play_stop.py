bl_info = {
    "name": "Auto Stop - Free",
    "description": "Option to auto stop playback at last scene frame",
    "author": "Coby Randal",
    "version": (1, 1, 0),
    "blender": (3, 60, 0),
    "location": "View3D > N-Panel> ASF",
    "doc_url": "https://blendermarket.com/creators/coby-randal-media",
    "category": "Animation",
}

import bpy


# Assuming AutoStopFree is defined elsewhere
# class AutoStopFree:
#     pass


# class ASF_PT_MainPanel(AutoStopFree, bpy.types.Panel):
#     bl_idname = "ASF_PT_Animation_Helpers"
#     bl_label = "Auto Stop - Free"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "ASF"

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene
#         asfmytool = scene.asfmy_tool

#         layout.prop(asfmytool, "asfmy_bool", text="Auto Stop")
#         layout.separator()


class ASF_PT_Properties(bpy.types.PropertyGroup):
    asfmy_bool: bpy.props.BoolProperty(
        name="Auto Stop Playback",
        description="Automatically stops recording / animation playback at the last scene frame",
        default=False,
        update=lambda self, context: asfmy_bool_updated(context),
    )  # type: ignore


def asfmy_bool_updated(context):
    scene = context.scene
    asfmytool = scene.asfmy_tool

    if asfmytool.asfmy_bool:
        asf_add_animation_end_callback()
        asf_auto_stop_on()
    else:
        asf_remove_animation_end_callback()
        asf_auto_stop_off()


def asf_auto_stop_on():
    print("Auto stop playback turned on")


def asf_auto_stop_off():
    print("Auto stop playback turned off")


def asf_check_animation_end(scene):
    if scene.frame_current == scene.frame_end:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False


def asf_remove_animation_end_callback():
    for handler in bpy.app.handlers.frame_change_pre:
        if handler.__name__ == "asf_check_animation_end":
            bpy.app.handlers.frame_change_pre.remove(handler)
            break


def asf_add_animation_end_callback():
    bpy.app.handlers.frame_change_pre.append(asf_check_animation_end)


classes = (
    # ASF_PT_MainPanel,
    ASF_PT_Properties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.asfmy_tool = bpy.props.PointerProperty(type=ASF_PT_Properties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.asfmy_tool


if __name__ == "__main__":
    register()
