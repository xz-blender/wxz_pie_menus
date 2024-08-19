import datetime
import os
import webbrowser

import bpy

# License Information
"""
Quicklapse Lite Addon
Copyright (c) 2024 KING ZEN STUDIOS

This software is licensed under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.

1. Grant of License:
You are free to use this software for personal, educational, or commercial projects. You may not modify, redistribute, or sell the source code or binary code of the software.

2. Restrictions:
You may not:
- Sell, redistribute, or sublicense the source code or binary code of the software.
- Modify or create derivative works based on the software.
- Use the software for any commercial purpose beyond personal or internal use.

3. Ownership:
The software remains the property of KING ZEN STUDIOS. This license does not grant any ownership rights to the software or its source code.

4. No Warranty:
The software is provided "as is" without any warranties. KING ZEN STUDIOS disclaims all warranties, including implied warranties of merchantability or fitness for a particular purpose.

5. Termination:
This license will terminate automatically if you fail to comply with any terms of this agreement.

By using this software, you agree to the terms and conditions set forth in this license agreement.
"""

bl_info = {
    "name": "Quicklapse Lite",
    "description": "Repeatedly takes screenshots of a 3D View. Useful for creating timelapses.",
    "author": "KING ZEN STUDIOS",
    "location": "View3D > Sidebar > Quicklapse",
    "blender": (4, 2, 0),
    "version": (0, 1, 0),
}

i = 0
frame = 1
ctx = {}
destination = ""
last_screenshot_time = datetime.datetime.now()
increment = 0.025


class auto_timelapse_settings(bpy.types.PropertyGroup):
    recording: bpy.props.BoolProperty(name="Recording", default=False)
    file_type: bpy.props.EnumProperty(
        name="File type", items=[("jpg", "JPEG", "", 1), ("png", "PNG", "", 2)], default=1
    )
    file_path: bpy.props.StringProperty(name="File Path", default="//", subtype="DIR_PATH")
    use_pivot_object: bpy.props.BoolProperty(
        name="Use Pivot Object", default=False, description="Rotate a pivot object every X actions"
    )
    pivot_object: bpy.props.StringProperty(name="Pivot Object", description="Pivot object to rotate")
    pivot_object_increment: bpy.props.FloatProperty(
        name="Pivot Increment", description="World Z rotation per screenshot", unit="ROTATION", default=0.025
    )
    steps: bpy.props.IntProperty(
        name="Action Steps",
        description="Capture every X actions. For paint/sculpt, one stroke = one action. For edit/object mode, each mouse movement = one action",
        default=10,
        min=1,
    )
    minimum_time_between_screenshots: bpy.props.FloatProperty(
        name="Minimum time",
        description="Minimum time between screenshots in seconds",
        default=0.500,
        min=0.1000,
        soft_max=2.0,
        precision=3,
    )
    custom_prefix: bpy.props.StringProperty(
        name="Custom Prefix", default="Timelapse", description="Custom prefix for screenshot filenames"
    )


class VIEW3D_OT_auto_timelapse_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_label = "Quicklapse Lite"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column(align=True)

        settings = context.scene.auto_timelapse_settings

        col.prop(settings, "file_path")
        col.prop(settings, "file_type")
        col.prop(settings, "custom_prefix")

        if not settings.recording:
            col.prop(settings, "use_pivot_object")
            if settings.use_pivot_object:
                col.prop_search(settings, "pivot_object", context.scene, "objects")
                col.prop(settings, "pivot_object_increment")

            col = layout.column(align=True)
            subcol = col.column(align=True)
            subcol.prop(settings, "steps", text="Steps")
            subcol.prop(settings, "minimum_time_between_screenshots", text="Minimum Time")

            layout.separator()
            col = self.layout.column()
            col.operator("autotimelapse.auto_timelapse_viewport_start", text="Record", icon="RECORD_ON")

        else:
            col.alert = True
            col.operator("autotimelapse.auto_timelapse_viewport_end", text="Done", icon="CHECKMARK")

        layout.separator()
        col = layout.column(align=True)
        col.operator("quicklapse.visit_facebook", text="Visit Facebook Page", icon="URL").url = (
            "https://web.facebook.com/kingzen0000"
        )
        col.operator("quicklapse.visit_blendermarket", text="Visit Blender Market", icon="URL").url = (
            "https://blendermarket.com/creators/kingzen"
        )


class StartAutoTimelapseViewport(bpy.types.Operator):
    """This starts the timelapse process. The images are saved in the specified file path."""

    bl_idname = "autotimelapse.auto_timelapse_viewport_start"
    bl_label = "Start Auto Timelapse"

    def execute(self, context):
        global ctx
        global foldername
        global destination
        global i
        global frame

        settings = context.scene.auto_timelapse_settings

        if settings.use_pivot_object and settings.pivot_object == "":
            self.report({"ERROR"}, "Must have a pivot")
            return {"CANCELLED"}

        destination = bpy.path.abspath(settings.file_path)
        i = 0
        frame = 0

        ctx = {"window": bpy.context.window, "area": bpy.context.area, "region": bpy.context.region}

        settings.recording = True

        foldername = datetime.datetime.now().strftime("%Y-%b-%d-%H%M")

        if not os.path.exists(destination):
            os.makedirs(destination)

        bpy.app.handlers.depsgraph_update_post.append(auto_timelapse_on_depsgraph_update)
        print("Started timelapse")
        return {"FINISHED"}


class EndAutoTimelapseViewport(bpy.types.Operator):
    bl_idname = "autotimelapse.auto_timelapse_viewport_end"
    bl_label = "End Auto Timelapse"

    def execute(self, context):
        context.scene.auto_timelapse_settings.recording = False

        try:
            bpy.app.handlers.depsgraph_update_post.remove(auto_timelapse_on_depsgraph_update)
        except:
            pass

        print("Ended timelapse")
        return {"FINISHED"}


class VisitFacebookPageOperator(bpy.types.Operator):
    bl_idname = "quicklapse.visit_facebook"
    bl_label = "Visit Facebook Page"

    url: bpy.props.StringProperty()

    def execute(self, context):
        webbrowser.open(self.url)
        return {"FINISHED"}


class VisitBlenderMarketOperator(bpy.types.Operator):
    bl_idname = "quicklapse.visit_blendermarket"
    bl_label = "Visit Blender Market"

    url: bpy.props.StringProperty()

    def execute(self, context):
        webbrowser.open(self.url)
        return {"FINISHED"}


def auto_timelapse_on_depsgraph_update(scene):
    global i
    global ctx
    global last_screenshot_time
    global foldername
    global increment
    global frame

    i += 1

    if i % scene.auto_timelapse_settings.steps == 0:
        seconds_since_last_screenshot = (datetime.datetime.now() - last_screenshot_time).total_seconds()
        if seconds_since_last_screenshot > scene.auto_timelapse_settings.minimum_time_between_screenshots:
            frame += 1
            if scene.auto_timelapse_settings.use_pivot_object:
                scene.auto_timelapse_settings.pivot_object.rotation_euler[2] += increment
            last_screenshot_time = datetime.datetime.now()

            with bpy.context.temp_override(**ctx):
                prefix = scene.auto_timelapse_settings.custom_prefix
                filename = f"{prefix}-{foldername}-{str(frame).zfill(6)}.{scene.auto_timelapse_settings.file_type}"
                bpy.ops.screen.screenshot_area(filepath=os.path.join(destination, filename))
    return {"FINISHED"}


classes = [
    auto_timelapse_settings,
    # VIEW3D_OT_auto_timelapse_panel,
    StartAutoTimelapseViewport,
    EndAutoTimelapseViewport,
    VisitFacebookPageOperator,
    VisitBlenderMarketOperator,
]

class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()
    bpy.types.Scene.auto_timelapse_settings = bpy.props.PointerProperty(type=auto_timelapse_settings)


def unregister():
    class_unregister()
    del bpy.types.Scene.auto_timelapse_settings


if __name__ == "__main__":
    register()
