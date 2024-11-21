import re

import bpy
from bpy.types import Menu, Operator, Panel

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_Z_Overlay(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        # 4 - LEFT
        if context.active_object:
            col = pie.column()

            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_y = 1.4
            row.scale_x = 2
            row.prop(context.object, "show_bounds", icon="SHADING_BBOX", icon_only=True)
            row.prop(context.object, "show_wire", icon="CUBE", icon_only=True)

            row = col.row(align=True)
            row.scale_x = 0.9
            row.scale_y = 1.4
            row.prop(context.object, "display_type", expand=True, invert_checkbox=True)
        else:
            pie.separator()

        # 6 - RIGHT
        pie.operator("view3d.toggle_shading", text="实体", icon="SHADING_SOLID").type = "SOLID"
        # 2 - BOTTOM
        pie.operator("view3d.toggle_shading", text="预览", icon="SHADING_TEXTURE").type = "MATERIAL"
        # 8 - TOP
        if context.active_object:
            if context.object.type == "MESH" or "CURVE":
                pie.operator("pie.gn_autosmooth", icon="RADIOBUT_ON")
                # auto_smooth = pie.operator('wm.call_panel', text='自动光滑', icon='RADIOBUT_ON', emboss=True)
                # auto_smooth.name = VIEW_PIE_PT_AutoSmooth.bl_idname
                # auto_smooth.keep_open = True
        # pie.operator("pie.gn_autosmooth",icon="RADIOBUT_ON")
        else:
            pie.separator()
        # 7 - TOP - LEFT    &     9 - TOP - RIGHT
        if context.active_object:
            if context.object.mode == "OBJECT" and context.object.type == "MESH":
                pie.operator("OBJECT_OT_shade_smooth", icon="ANTIALIASED")
                pie.operator("OBJECT_OT_shade_flat", icon="ALIASED")
            elif context.object.mode == "EDIT" and context.object.type == "MESH":
                pie.operator("MESH_OT_faces_shade_smooth", icon="ANTIALIASED")
                pie.operator("MESH_OT_faces_shade_flat", icon="ALIASED")
            else:
                pie.separator()
                pie.separator()
        else:
            pie.separator()
            pie.separator()
        # 1 - BOTTOM - LEFT
        pie.prop(
            context.space_data.overlay,
            "show_wireframes",
            text="所有线框",
            icon="SHADING_WIRE",
            toggle=False,
        )
        # 3 - BOTTOM - RIGHT
        pie.prop(
            context.space_data.overlay,
            "show_face_orientation",
            icon="NORMALS_FACE",
            toggle=False,
        )


class VIEW_PIE_PT_AutoSmooth(Panel):
    bl_idname = __qualname__
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"

    def draw(self, context):
        layout = self.layout

        # 创建界面元素以调整属性
        row = layout.row()
        row.scale_y = 1.4
        op = row.operator("pie.gn_autosmooth", icon="RADIOBUT_ON")
        # 显示操作符的属性供编辑
        layout.prop(op, "angle", emboss=True, event=True)
        layout.prop(op, "ignore")


def add_sm():
    bpy.ops.object.modifier_add_node_group(
        asset_library_type="ESSENTIALS",
        asset_library_identifier="",
        relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\Smooth by Angle",
    )


class PIE_GN_AutoSmooth(Operator):
    bl_idname = "pie.gn_autosmooth"
    bl_label = "按角度光滑"
    bl_description = "添加自动光滑几何节点"
    bl_options = {"REGISTER", "UNDO"}

    angle: bpy.props.FloatProperty(default=0.52359, name="Angle", min=0, soft_max=3.14159, subtype="ANGLE")  # type: ignore
    ignore: bpy.props.BoolProperty(default=False, name="Ignore Sharpness")  # type: ignore
    only_one: bpy.props.BoolProperty(default=True, name="Only One")  # type: ignore

    @classmethod
    def poll(cls, context):
        if bpy.ops.selected_objects:
            return True

    def execute(self, context):
        # 编译一个正则表达式来匹配以“Smooth by Angle”开头的所有修改器名称
        pattern = re.compile(r"^Smooth by Angle(\.\d+)?$")
        s_name = "Smooth by Angle"
        ob_mode = get_ob_mode(context)
        ob_type = get_ob_type(context)

        if ob_mode == "OBJECT":
            for obj in context.selected_objects:
                modifiers = obj.modifiers  # 获取该物体修改器属性
                # 遍历每个选定物体的修改器
                if modifiers:
                    # 初始化变量以保留找到的第一个“Smooth by Angle”修改器
                    primary_modifier = None
                    # 遍历所有修改器的副本列表（使用列表副本以避免在遍历时修改列表）
                    for modifier in modifiers:
                        # 检查修改器名称是否完全匹配“Smooth by Angle”
                        if modifier.type == "NODES":
                            if modifier.node_group == None:
                                modifiers.remove(modifier)
                            elif modifier.node_group.name == s_name:
                                if primary_modifier is None:
                                    # 如果找到第一个“Smooth by Angle”修改器，保留它
                                    primary_modifier = modifier
                                else:
                                    if self.only_one:
                                        # 如果已经找到一个“Smooth by Angle”，则删除当前这个
                                        modifiers.remove(modifier)
                            # 对于其他匹配正则表达式的修改器（即以“Smooth by Angle.”开头的）
                            elif pattern.match(modifier.node_group.name):
                                modifiers.remove(modifier)
                    # 如果找到了“Smooth by Angle”修改器，将其移动到堆栈底部
                    if primary_modifier:
                        primary_modifier["Input_1"] = self.angle
                        primary_modifier["Socket_1"] = self.ignore
                    else:
                        bpy.ops.object.shade_auto_smooth(angle=self.angle)
        elif ob_mode == "EDIT" and ob_type == "MESH":
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.shade_auto_smooth(angle=self.angle)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.context.view_layer.update()
        return {"FINISHED"}


class PIE_Update_AutoSmooth_Angle(bpy.types.Operator):
    """更新选定物体的'Smooth by Angle'修改器中的角度参数"""

    bl_idname = "pie.update_smooth_angle"
    bl_label = "Update AutoSmooth Angle"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        return {"FINISHED"}


class VIEW3D_PIE_MT_Bottom_Z_Shift(Menu):
    bl_label = "Shift-Z"

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        # 4 - LEFT
        pie.prop(bpy.context.space_data, "show_gizmo", text="控件层")
        # 6 - RIGHT
        pie.prop(bpy.context.space_data.overlay, "show_overlays", text="叠加层")
        # 2 - BOTTOM
        split = pie.split()
        col = split.column(align=True)
        col.row(align=True).prop(context.space_data.shading, "color_type", expand=True)
        # 8 - TOP
        pie.operator("wm.window_fullscreen_toggle")
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


CLASSES = [
    VIEW3D_PIE_MT_Bottom_Z_Overlay,
    VIEW_PIE_PT_AutoSmooth,
    PIE_GN_AutoSmooth,
    PIE_Update_AutoSmooth_Angle,
    VIEW3D_PIE_MT_Bottom_Z_Shift,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "Z", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Z_Overlay"

    kmi = km.keymap_items.new("wm.call_menu_pie", "Z", "CLICK_DRAG", shift=True)
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Z_Shift"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    bpy.types.Scene.pie_smooth_prop = bpy.props.FloatProperty(name="angle")
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    del bpy.types.Scene.pie_smooth_prop
    safe_unregister_class(CLASSES)
