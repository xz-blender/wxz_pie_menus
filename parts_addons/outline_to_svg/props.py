import bpy
from bpy.types import PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import (
    EnumProperty,
    StringProperty,
    PointerProperty,
    BoolProperty,
)
from . import consts


class Outlines_To_SVG_Properties(PropertyGroup):
    """Addon panel UI properties"""

    filepath: StringProperty(name="Output Path", subtype="FILE_PATH")
    # only_visible: BoolProperty(name="Only visible", default=True)
    unique_colors: BoolProperty(name="Unique Colors", default=False)
    holes_as_group: BoolProperty(name="Holes as Group", default=False)
    hole_exclusion: StringProperty(name="Hole Exclusion")
    grouping: EnumProperty(items=consts.OUTLINE_GROUPING_ENUM, default="NONE")
    append_mode: BoolProperty(name="Append Mode", default=False)


def register():
    register_class(Outlines_To_SVG_Properties)

    bpy.types.Scene.outline_to_svg_props = PointerProperty(
        type=Outlines_To_SVG_Properties
    )


def unregister():
    del bpy.types.Scene.outline_to_svg_props
    unregister_class(Outlines_To_SVG_Properties)
