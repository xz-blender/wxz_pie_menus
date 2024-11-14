import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_W(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):

        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)
        ui_type = get_area_ui_type(context)

        if ob_mode == "OBJECT":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.prop(context.scene.tool_settings, "use_transform_data_origin", text="仅原点")
            # 8 - TOP
            pie.prop(context.scene.tool_settings, "use_proportional_edit_objects", text="衰减编辑物体")
            # 7 - TOP - LEFT
            if bool(context.object.modifiers) == False:
                pie.operator("pie.empty_operator", text="没有任何修改器!")
            else:
                add_operator(pie, "object.toggle_apply_modifiers_view", text="显示/隐藏所有修改器", icon="MODIFIER")
            # 9 - TOP - RIGHT
            # ---------------
            col = pie.split().column(align=True)
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 1.3
            row.scale_y = 1.2
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="SMOOTHCURVE").mode = "SMOOTH"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="SPHERECURVE").mode = "SPHERE"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="ROOTCURVE").mode = "ROOT"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="INVERSESQUARECURVE").mode = "INVERSE_SQUARE"
            # ---------------
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 1.3
            row.scale_y = 1.2
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="SHARPCURVE").mode = "SHARP"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="LINCURVE").mode = "LINEAR"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="NOCURVE").mode = "CONSTANT"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="RNDCURVE").mode = "RANDOM"
            # 1 - BOTTOM - LEFT
            pie.prop(bpy.context.scene.tool_settings, "use_transform_pivot_point_align", text="仅位置")
            # 3 - BOTTOM - RIGHT
            pie.prop(bpy.context.scene.tool_settings, "use_transform_skip_children", text="仅父级")

        elif ob_mode == "EDIT":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.prop(context.scene.tool_settings, "use_mesh_automerge", text="自动合并")
            # 8 - TOP
            pie.prop(context.scene.tool_settings, "use_proportional_edit", text="衰减编辑网格")
            # 7 - TOP - LEFT
            if bool(context.object.modifiers) == False:
                pie.operator("pie.empty_operator", text="没有任何修改器!")
            else:
                add_operator(pie, "object.toggle_apply_modifiers_view", text="显示/隐藏所有修改器", icon="MODIFIER")
            # 9 - TOP - RIGHT
            col = pie.split().column(align=True)
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 2
            row.scale_y = 1.3
            row.prop(
                bpy.context.scene.tool_settings,
                "use_proportional_connected",
                icon="PROP_PROJECTED",
                icon_only=True,
            )
            row.separator(factor=0.1)
            row.prop(
                context.scene.tool_settings,
                "use_proportional_projected",
                icon="RESTRICT_VIEW_OFF",
                icon_only=True,
            )
            # -
            col.separator(factor=0.4)
            # ---------------
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 1.3
            row.scale_y = 1.2
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="SMOOTHCURVE").mode = "SMOOTH"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="SPHERECURVE").mode = "SPHERE"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="ROOTCURVE").mode = "ROOT"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="INVERSESQUARECURVE").mode = "INVERSE_SQUARE"
            # ---------------
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 1.3
            row.scale_y = 1.2
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="SHARPCURVE").mode = "SHARP"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="LINCURVE").mode = "LINEAR"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="NOCURVE").mode = "CONSTANT"
            row.operator(Proportional_Edit_Falloff.bl_idname, icon="RNDCURVE").mode = "RANDOM"

            # 1 - BOTTOM - LEFT
            col = pie.split().column(align=True)
            col.scale_y = 1.2
            row = col.row()
            row.prop(context.scene.tool_settings, "use_edge_path_live_unwrap")
            row = col.row()
            row.prop(context.scene.tool_settings, "use_mesh_automerge_and_split")

            # 3 - BOTTOM - RIGHT
            pie.prop(context.scene.tool_settings, "use_transform_correct_face_attributes")


class Proportional_Edit_Falloff(Operator):
    bl_idname = "pie.proportional_edit_falloff"
    bl_label = ""
    bl_description = ""
    bl_options = {"REGISTER"}

    mode: bpy.props.StringProperty(name="Mode")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.proportional_edit_falloff = "%s" % (self.mode)
        return {"FINISHED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_W,
    Proportional_Edit_Falloff,
]


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "W", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_W"
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("wm.call_menu", "W", "CLICK")
    kmi.properties.name = "PIE_MT_Bottom_Q_favorite"
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="UV Editor", space_type="IMAGE_EDITOR")
    kmi = km.keymap_items.new("wm.call_menu_pie", "W", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_W"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
