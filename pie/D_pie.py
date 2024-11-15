import bpy
from bpy.types import Menu, Operator

from ..utils import extend_keymaps_list, safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_D(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ui = get_area_ui_type(context)

        if ui == "VIEW_3D":

            # 4 - LEFT
            sp = pie.split()
            sp.scale_x = 1.1

            sp = sp.split(factor=0.18)
            col_l = sp.column()
            row_l = col_l.row()
            row_l.label(text="坐")
            row_l = col_l.row()
            row_l.label(text="标")
            row_l = col_l.row()
            row_l.label(text="系")

            col = sp.box().column()
            row = col.row()
            row.operator("pie.transform_orientation", text="万象", icon="ORIENTATION_GIMBAL").axis = "GIMBAL"
            row = col.row()
            row.operator("pie.transform_orientation", text="视图", icon="ORIENTATION_VIEW").axis = "VIEW"
            row = col.row()
            row.operator("pie.transform_orientation", text="游标", icon="ORIENTATION_CURSOR").axis = "CURSOR"
            # 6 - RIGHT
            sp = pie.split()

            sp = sp.split(factor=0.8)
            col = sp.box().column()
            row = col.row()
            row.operator("pie.transform_pivot", text="质心点", icon="PIVOT_MEDIAN").pivot = "MEDIAN_POINT"
            row = col.row()
            row.operator("pie.transform_pivot", text="活动项", icon="PIVOT_ACTIVE").pivot = "ACTIVE_ELEMENT"

            col_r = sp.column()
            row = col_r.row()
            row.label(text="轴")
            row = col_r.row()
            row.label(text="心")
            row = col_r.row()
            row.label(text="点")
            # 2 - BOTTOM
            pie.operator("pie.transform_pivot", text="各自原点", icon="PIVOT_INDIVIDUAL").pivot = "INDIVIDUAL_ORIGINS"
            # 8 - TOP
            pie.operator("pie.transform_orientation", text="法向", icon="ORIENTATION_NORMAL").axis = "NORMAL"
            # 7 - TOP - LEFT
            pie.operator("pie.transform_orientation", text="全局", icon="ORIENTATION_GLOBAL").axis = "GLOBAL"
            # 9 - TOP - RIGHT
            pie.operator("pie.transform_orientation", text="局部", icon="ORIENTATION_LOCAL").axis = "LOCAL"
            # 1 - BOTTOM - LEFT
            pie.operator("pie.transform_pivot", text="边界框", icon="PIVOT_BOUNDBOX").pivot = "BOUNDING_BOX_CENTER"
            # 3 - BOTTOM - RIGHT
            pie.operator("pie.transform_pivot", text="游标", icon="PIVOT_CURSOR").pivot = "CURSOR"
        elif ui == "UV":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator(VIEW3D_PIE_MT_Transform_Pivot_UV.bl_idname, text="各自中心", icon="PIVOT_INDIVIDUAL").pivot = (
                "INDIVIDUAL_ORIGINS"
            )
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.operator(VIEW3D_PIE_MT_Transform_Pivot_UV.bl_idname, text="边界框", icon="PIVOT_BOUNDBOX").pivot = (
                "CENTER"
            )
            # 3 - BOTTOM - RIGHT
            pie.operator(VIEW3D_PIE_MT_Transform_Pivot_UV.bl_idname, text="游标", icon="PIVOT_CURSOR").pivot = "CURSOR"


class VIEW3D_PIE_MT_Transform_Orientation(Operator):
    bl_idname = "pie.transform_orientation"
    bl_label = ""
    bl_options = {"REGISTER"}

    axis: bpy.props.StringProperty(name="Axis", default="GLOBAL")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.transform_orientation_slots[0].type = "%s" % (self.axis)
        return {"FINISHED"}


class VIEW3D_PIE_MT_Transform_Pivot(Operator):
    bl_idname = "pie.transform_pivot"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    pivot: bpy.props.StringProperty(name="Pivot", default="BOUNDING_BOX_CENTER")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.transform_pivot_point = "%s" % (self.pivot)
        return {"FINISHED"}


class VIEW3D_PIE_MT_Transform_Pivot_UV(Operator):
    bl_idname = "pie.transform_pivot_uv"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    pivot: bpy.props.StringProperty(name="Pivot", default="CENTER")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.space_data.pivot_point = "%s" % (self.pivot)
        return {"FINISHED"}


class PIE_Mesh_OriginToGeometry(Operator):
    bl_idname = "pie.mesh_origin_to_geometry"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_D,
    VIEW3D_PIE_MT_Transform_Orientation,
    VIEW3D_PIE_MT_Transform_Pivot,
    VIEW3D_PIE_MT_Transform_Pivot_UV,
    PIE_Mesh_OriginToGeometry,
]


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        ("3D View", "VIEW_3D"),
        ("UV Editor", "EMPTY"),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("wm.call_menu_pie", "D", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_D"
        addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("mesh.snap_utilities_line", "D", "CLICK")
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.mesh_origin_to_geometry", "D", "DOUBLE_CLICK")
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("object.origin_set", "D", "DOUBLE_CLICK")
    kmi.properties.type = "ORIGIN_GEOMETRY"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()
    extend_keymaps_list(addon_keymaps)


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
