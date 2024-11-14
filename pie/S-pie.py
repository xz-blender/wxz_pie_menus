import bpy
from bpy.types import Context, Menu, Operator, Panel

from ..parts_addons.m4_tools.align_helper_npanel import *
from ..parts_addons.m4_tools.align_helper_utils import *
from ..utils import safe_register_class, safe_unregister_class
from .utils import *


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


class VIEW3D_PIE_MT_Bottom_S(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        m4 = context.scene.M4_split
        active = context.active_object
        sel = [obj for obj in context.selected_objects if obj != active]

        ui = context.area.ui_type
        if ui == "VIEW_3D":
            if context.object:
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
                    col.scale_x = 1.5
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
            if m4.align_mode == "AXES":
                draw_align_with_axes_uv(pie, m4)
            elif m4.align_mode == "VIEW":
                draw_align_with_view_uv(pie, m4)

        elif ui == "ShaderNodeTree" or "GeometryNodeTree" or "CompositorNodeTree":
            # 4 - LEFT
            pie.operator("pie.s_flat_nodes", text="对齐到 X 轴").value = (0, 1, 1)
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("pie.s_flat_nodes", text="对齐到 Y 轴").value = (1, 0, 1)
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            try:
                pie.operator("node_relax.arrange")
            except:
                pie.separator()


class PIE_S_Flat_NOdes(Operator):
    bl_idname = "pie.s_flat_nodes"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    value: bpy.props.IntVectorProperty()  # type: ignore

    @classmethod
    def poll(cls, context: Context):
        return True

    def execute(self, context):
        value = self.value
        bpy.ops.transform.resize(value=value)
        return {"FINISHED"}


class PIE_S_Flat_Mesh(Operator):
    bl_idname = "pie.view_s_flat_mesh"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    X: bpy.props.BoolProperty(name="X")  # type: ignore
    Y: bpy.props.BoolProperty(name="Y")  # type: ignore
    Z: bpy.props.BoolProperty(name="Z")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        X = self.X
        Y = self.Y
        Z = self.Z
        if X:
            bpy.ops.transform.resize(value=(0, 1, 1))
        elif Y:
            bpy.ops.transform.resize(value=(1, 0, 1))
        elif Z:
            bpy.ops.transform.resize(value=(1, 1, 0))
        return {"FINISHED"}


class PIE_S_Flat_Object(Operator):
    bl_idname = "pie.view_s_flat_object"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    X: bpy.props.BoolProperty(name="X")  # type: ignore
    Y: bpy.props.BoolProperty(name="Y")  # type: ignore
    Z: bpy.props.BoolProperty(name="Z")  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.selected_objects:
            if context.object.mode == "OBJECT":
                return True
        else:
            return False

    def execute(self, context):
        X = self.X
        Y = self.Y
        Z = self.Z
        if context.scene.tool_settings.use_transform_pivot_point_align == False:
            context.scene.tool_settings.use_transform_pivot_point_align = True
            if X:
                bpy.ops.transform.resize(value=(0, 1, 1))
            elif Y:
                bpy.ops.transform.resize(value=(1, 0, 1))
            elif Z:
                bpy.ops.transform.resize(value=(1, 1, 0))
            context.scene.tool_settings.use_transform_pivot_point_align = False
        else:
            if X:
                bpy.ops.transform.resize(value=(0, 1, 1))
            elif Y:
                bpy.ops.transform.resize(value=(1, 0, 1))
            elif Z:
                bpy.ops.transform.resize(value=(1, 1, 0))
        return {"FINISHED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_S,
    PIE_S_Flat_Mesh,
    PIE_S_Flat_Object,
    PIE_S_Flat_NOdes,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        ("3D View", "VIEW_3D"),
        ("UV Editor", "EMPTY"),
        ("Node Editor", "NODE_EDITOR"),
        ("Graph Editor", "GRAPH_EDITOR"),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("wm.call_menu_pie", "S", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_S"
        addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
