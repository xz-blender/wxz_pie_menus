import importlib.util

from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from .operators import EXPORT_OT_Export_Outline_SVG


def dependencies_installed() -> bool:
    """return True if required module, shapely, is installed"""
    return importlib.util.find_spec("shapely") is not None


class VIEW3D_PT_Outline_To_SVG(Panel):
    bl_label = "Outline to SVG"
    bl_idname = "VIEW3D_PT_outline_to_svg"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "XZ"

    def draw(self, context):
        addon_props = context.scene.outline_to_svg_props
        layout = self.layout
        col = layout.column(align=True)

        if dependencies_installed():
            # row = col.row(align=True)
            # row.label(text="Export")
            row = col.row(align=True)
            # row.prop(addon_props, "group_by_collection", text="Collection")
            # row.prop(addon_props, "group_by_material", text="Material")
            row.label(text="Group:")
            row.prop(addon_props, "grouping", text="Group by:", expand=True)
            row = col.row(align=True)
            row.prop(addon_props, "unique_colors", text="Unique Colors")
            row.prop(addon_props, "holes_as_group", text="Holes as Group")
            if addon_props.holes_as_group:
                row = col.row()
                row.prop(addon_props, "hole_exclusion", text="Except")

            # row = col.row(align=True)
            # row.prop(addon_props, "only_visible", text="Limit to Visible")
            row = col.row(align=True)
            row.prop(addon_props, "filepath", text="")
            row = col.row(align=True)
            btn = row.operator(EXPORT_OT_Export_Outline_SVG.bl_idname, text="Export SVG")
            btn.filepath = addon_props.filepath
            btn.grouping = addon_props.grouping
            btn.unique_colors = addon_props.unique_colors
            btn.holes_as_group = addon_props.holes_as_group
            btn.hole_exclusion = addon_props.hole_exclusion
            # btn.append_mode = addon_props.append_mode
            # row = col.row(align=True)
            # row.prop(addon_props, "append_mode", text="Append Last")
        else:
            col.label(text="Missing dependency, please try restarting Blender")


def register():
    register_class(VIEW3D_PT_Outline_To_SVG)


def unregister():
    unregister_class(VIEW3D_PT_Outline_To_SVG)
