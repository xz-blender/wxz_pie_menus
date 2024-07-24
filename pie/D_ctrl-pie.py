import bpy
from bpy.types import Menu, Operator

from .utils import *
from ..parts_addons.m4_tools.align_helper_utils import screen_relevant_direction_3d_axis
from ..parts_addons.m4_tools.align_helper_npanels import *

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Interface",
}


def draw_align_with_axes_uv(pie, m4):
    op = pie.operator("m4a1.align_uv", text="V min")
    op.axis = "V"
    op.type = "MIN"

    op = pie.operator("m4a1.align_uv", text="V max")
    op.axis = "V"
    op.type = "MAX"

    pie.separator()

    box = pie.split()
    column = box.column()

    row = column.row(align=True)
    row.prop(m4, "align_mode", expand=True)

    column.separator()
    column.separator()

    op = pie.operator("m4a1.align_uv", text="U min")
    op.axis = "U"
    op.type = "MIN"

    op = pie.operator("m4a1.align_uv", text="U max")
    op.axis = "U"
    op.type = "MAX"

    op = pie.operator("m4a1.align_uv", text="U Cursor")
    op.axis = "U"
    op.type = "CURSOR"

    op = pie.operator("m4a1.align_uv", text="V Cursor")
    op.axis = "V"
    op.type = "CURSOR"


def draw_align_with_view_uv(pie, m4):
    op = pie.operator("m4a1.align_uv", text="Left")
    op.axis = "U"
    op.type = "MIN"

    op = pie.operator("m4a1.align_uv", text="Right")
    op.axis = "U"
    op.type = "MAX"

    op = pie.operator("m4a1.align_uv", text="Bottom")
    op.axis = "V"
    op.type = "MIN"

    op = pie.operator("m4a1.align_uv", text="Top")
    op.axis = "V"
    op.type = "MAX"

    pie.separator()

    box = pie.split()
    column = box.column()

    row = column.row(align=True)
    row.prop(m4, "align_mode", expand=True)

    pie.separator()

    box = pie.split()
    column = box.column()

    row = column.split(factor=0.2)

    row.label(icon="PIVOT_CURSOR")

    r = row.row(align=True)
    row.scale_y = 1.2
    op = r.operator("m4a1.align_uv", text="Horizontal")
    op.type = "CURSOR"
    op.axis = "U"
    op = r.operator("m4a1.align_uv", text="Vertical")
    op.type = "CURSOR"
    op.axis = "V"


def draw_align_with_axes_edit(pie, m3, sel):
    op = pie.operator("m4a1.align_editmesh", text="Y min")
    op.mode = "AXES"
    op.axis = "Y"
    op.type = "MIN"

    op = pie.operator("m4a1.align_editmesh", text="Y max")
    op.mode = "AXES"
    op.axis = "Y"
    op.type = "MAX"

    box = pie.split()
    column = box.column(align=True)

    column.separator()

    row = column.split(factor=0.2, align=True)
    row.separator()
    row.label(text="Center")

    row = column.row(align=True)
    row.scale_y = 1.2
    row.operator("m4a1.center_editmesh", text="X").axis = "X"
    row.operator("m4a1.center_editmesh", text="Y").axis = "Y"
    row.operator("m4a1.center_editmesh", text="Z").axis = "Z"

    column.separator()

    row = column.row(align=True)
    row.scale_y = 1.2
    row.operator("m4a1.straighten", text="Straighten")

    if sel:
        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("m4a1.align_object_to_vert", text="Align Object to Vert")

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("m4a1.align_object_to_edge", text="Align Object to Edge")

    box = pie.split()
    column = box.column()

    row = column.split(factor=0.2)
    row.label(icon="ARROW_LEFTRIGHT")
    r = row.row(align=True)
    r.scale_y = 1.2
    op = r.operator("m4a1.align_editmesh", text="X")
    op.mode = "AXES"
    op.axis = "X"
    op.type = "AVERAGE"
    op = r.operator("m4a1.align_editmesh", text="Y")
    op.mode = "AXES"
    op.axis = "Y"
    op.type = "AVERAGE"
    op = r.operator("m4a1.align_editmesh", text="Z")
    op.mode = "AXES"
    op.axis = "Z"
    op.type = "AVERAGE"

    row = column.split(factor=0.2)
    row.label(icon="FREEZE")
    r = row.row(align=True)
    r.scale_y = 1.2
    op = r.operator("m4a1.align_editmesh", text="X")
    op.mode = "AXES"
    op.axis = "X"
    op.type = "ZERO"
    op = r.operator("m4a1.align_editmesh", text="Y")
    op.mode = "AXES"
    op.axis = "Y"
    op.type = "ZERO"
    op = r.operator("m4a1.align_editmesh", text="Z")
    op.mode = "AXES"
    op.axis = "Z"
    op.type = "ZERO"

    row = column.split(factor=0.2)
    row.label(icon="PIVOT_CURSOR")
    r = row.row(align=True)
    r.scale_y = 1.2
    op = r.operator("m4a1.align_editmesh", text="X")
    op.mode = "AXES"
    op.axis = "X"
    op.type = "CURSOR"
    op = r.operator("m4a1.align_editmesh", text="Y")
    op.mode = "AXES"
    op.axis = "Y"
    op.type = "CURSOR"
    op = r.operator("m4a1.align_editmesh", text="Z")
    op.mode = "AXES"
    op.axis = "Z"
    op.type = "CURSOR"

    column.separator()

    row = column.split(factor=0.15)
    row.separator()
    r = row.split(factor=0.8)
    rr = r.row(align=True)
    rr.prop(m3, "align_mode", expand=True)

    column.separator()

    op = pie.operator("m4a1.align_editmesh", text="X min")
    op.mode = "AXES"
    op.axis = "X"
    op.type = "MIN"

    op = pie.operator("m4a1.align_editmesh", text="X max")
    op.mode = "AXES"
    op.axis = "X"
    op.type = "MAX"

    op = pie.operator("m4a1.align_editmesh", text="Z min")
    op.mode = "AXES"
    op.axis = "Z"
    op.type = "MIN"

    op = pie.operator("m4a1.align_editmesh", text="Z max")
    op.mode = "AXES"
    op.axis = "Z"
    op.type = "MAX"


def draw_align_with_view_edit(pie, m3, sel):
    op = pie.operator("m4a1.align_editmesh", text="Left")
    op.mode = "VIEW"
    op.direction = "LEFT"

    op = pie.operator("m4a1.align_editmesh", text="Right")
    op.mode = "VIEW"
    op.direction = "RIGHT"

    op = pie.operator("m4a1.align_editmesh", text="Bottom")
    op.mode = "VIEW"
    op.direction = "BOTTOM"

    op = pie.operator("m4a1.align_editmesh", text="Top")
    op.mode = "VIEW"
    op.direction = "TOP"

    pie.separator()

    box = pie.split()
    column = box.column()

    row = column.row(align=True)
    row.prop(m3, "align_mode", expand=True)

    box = pie.split()
    column = box.column(align=True)

    column.separator()

    row = column.split(factor=0.25)
    row.label(text="Center")

    r = row.row(align=True)
    r.scale_y = 1.2
    op = r.operator("m4a1.center_editmesh", text="Horizontal")
    op.direction = "HORIZONTAL"
    op = r.operator("m4a1.center_editmesh", text="Vertical")
    op.direction = "VERTICAL"

    column.separator()
    row = column.split(factor=0.25, align=True)
    row.scale_y = 1.2
    row.separator()
    row.operator("m4a1.straighten", text="Straighten")

    if sel:
        row = column.split(factor=0.25, align=True)
        row.scale_y = 1.2
        row.separator()
        row.operator("m4a1.align_object_to_vert", text="Align Object to Vert")

        row = column.split(factor=0.25, align=True)
        row.scale_y = 1.2
        row.separator()
        row.operator("m4a1.align_object_to_edge", text="Align Object to Edge")

    box = pie.split()
    column = box.column(align=True)

    row = column.split(factor=0.2, align=True)
    row.label(icon="ARROW_LEFTRIGHT")

    r = row.row(align=True)
    row.scale_y = 1.2
    op = r.operator("m4a1.align_editmesh", text="Horizontal")
    op.mode = "VIEW"
    op.type = "AVERAGE"
    op.direction = "HORIZONTAL"
    op = r.operator("m4a1.align_editmesh", text="Vertical")
    op.mode = "VIEW"
    op.type = "AVERAGE"
    op.direction = "VERTICAL"

    row = column.split(factor=0.2, align=True)
    row.label(icon="FREEZE")

    r = row.row(align=True)
    r.scale_y = 1.2
    op = r.operator("m4a1.align_editmesh", text="Horizontal")
    op.mode = "VIEW"
    op.type = "ZERO"
    op.direction = "HORIZONTAL"
    op = r.operator("m4a1.align_editmesh", text="Vertical")
    op.mode = "VIEW"
    op.type = "ZERO"
    op.direction = "VERTICAL"

    row = column.split(factor=0.2, align=True)
    row.label(icon="PIVOT_CURSOR")

    r = row.row(align=True)
    row.scale_y = 1.2
    op = r.operator("m4a1.align_editmesh", text="Horizontal")
    op.mode = "VIEW"
    op.type = "CURSOR"
    op.direction = "HORIZONTAL"
    op = r.operator("m4a1.align_editmesh", text="Vertical")
    op.mode = "VIEW"
    op.type = "CURSOR"
    op.direction = "VERTICAL"


class VIEW3D_PIE_MT_Bottom_D_Ctrl(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        m4 = context.scene.M4_split
        active = context.active_object
        sel = [obj for obj in context.selected_objects if obj != active]

        ui = context.area.ui_type
        if ui == "VIEW_3D":
            set_pie_ridius(context, 100)
            if context.object.mode == "OBJECT":
                direction = screen_relevant_direction_3d_axis(context)
                (x, x_), (y, y_) = direction
                set_axis(pie, {x_}, "Align_Left")
                set_axis(pie, {x}, "Align_Right")
                set_axis(pie, {y_}, "Align_Down")
                set_axis(pie, {y}, "Align_Up")

                draw_distribution_y(pie, y)

                col = pie.column(align=True)
                col.scale_y = 1.3
                draw_center_align(col, direction)

                draw_distribution_x(pie, x)

                col = pie.column(align=True)
                col.scale_y = 1.3
                draw_ground(col)
                draw_cursor_active_original(col)
            if context.object.mode == "EDIT":
                if m4.align_mode == "AXES":
                    draw_align_with_axes_edit(pie, m4, sel)
                elif m4.align_mode == "VIEW":
                    draw_align_with_view_edit(pie, m4, sel)

        elif ui == "UV":
            set_pie_ridius(context, 100)

            if m4.align_mode == "AXES":
                draw_align_with_axes_uv(pie, m4)
            elif m4.align_mode == "VIEW":
                draw_align_with_view_uv(pie, m4)


classes = [
    VIEW3D_PIE_MT_Bottom_D_Ctrl,
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
        kmi = km.keymap_items.new("wm.call_menu_pie", "D", "CLICK_DRAG", ctrl=True)
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_D_Ctrl"
        addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
