import bpy


class OBJECT_OT_orient_and_origin_to_selection(bpy.types.Operator):
    bl_label = "Orient Origin to Selected"
    bl_idname = "pie.orient_origin_to_selection"
    bl_description = "在编辑模式下将对象的原点捕捉到选定的组件"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        cursor = bpy.context.scene.cursor.location
        cursor_location = [cursor[0], cursor[1], cursor[2]]

        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.scene.cursor.location = cursor_location
        # ----------------------
        obj = bpy.context.edit_object
        orientation = bpy.context.scene.transform_orientation_slots[0].type
        edit_origin = bpy.context.scene.tool_settings.use_transform_data_origin
        affect_children = bpy.context.scene.tool_settings.use_transform_skip_children
        auto_keying = bpy.context.scene.tool_settings.use_keyframe_insert_auto

        bpy.context.scene.transform_orientation_slots[0].type = "NORMAL"
        try:
            bpy.ops.transform.create_orientation(name="SELECTION", use=True)
        except:
            bpy.context.scene.transform_orientation_slots[0].type = orientation
            self.report(
                {"WARNING"},
                "无法创建方向，因为所选项目的法线完全相互抵消",
            )
            return {"CANCELLED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.scene.tool_settings.use_transform_skip_children = True
        bpy.context.scene.tool_settings.use_transform_data_origin = True
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

        bpy.context.view_layer.objects.active = obj
        bpy.ops.transform.transform(mode="ALIGN", orient_type="SELECTION", orient_matrix_type="SELECTION")

        bpy.context.scene.tool_settings.use_transform_skip_children = affect_children
        bpy.context.scene.tool_settings.use_transform_data_origin = edit_origin
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = auto_keying
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.transform.delete_orientation()
        bpy.context.scene.transform_orientation_slots[0].type = orientation

        if obj.animation_data:
            self.report(
                {"WARNING"},
                "此对象具有关键帧。更改局部方向将改变任何动画旋转",
            )
        return {"FINISHED"}


def draw_orient_and_origin_to_selection_menu(self, context):
    if bpy.context.edit_object:
        self.layout.separator()
        self.layout.operator(OBJECT_OT_orient_and_origin_to_selection.bl_idname, icon="ORIENTATION_NORMAL")


def register():
    bpy.utils.register_class(OBJECT_OT_orient_and_origin_to_selection)
    bpy.types.VIEW3D_MT_snap.append(draw_orient_and_origin_to_selection_menu)


def unregister():
    bpy.types.VIEW3D_MT_snap.remove(draw_orient_and_origin_to_selection_menu)
    bpy.utils.unregister_class(OBJECT_OT_orient_and_origin_to_selection)
