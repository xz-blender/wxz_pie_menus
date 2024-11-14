import os

import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class PIE_MT_Bottom_Q_favorite(Menu):
    bl_idname = "PIE_MT_Bottom_Q_favorite"
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.alignment = "CENTER"
        layout.use_property_decorate = True
        layout.use_property_split = True

        split = layout.split()
        col = split.column()

        col.menu_contents("SCREEN_MT_user_menu")

        col.separator()

        split = layout.split()
        col = split.column()

        col.label(text="自定工具集")
        col.operator("pie.q_render_viewport")
        col.operator("pie.quick_redhalom2b")

        col.separator()

        # col.label(text="自定脚本集")
        col.operator("pie.empty_to_collection")
        col.operator("pie.parents_to_file")
        col.operator("pie.origin_to_parent")
        col.operator("pie.clean_same_material_texture")
        col.operator("pie.clean_to_link_data")
        col.operator("pie.linksameobjectdata_byselects")
        col.operator("pie.selectsamevertexobject")
        col.operator("pie.context_translate", icon="FILE_TEXT")


class Render_Viewport_OpenGL(Operator):
    bl_idname = "pie.q_render_viewport"
    bl_label = "视图渲染图像"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.render.opengl("INVOKE_DEFAULT")
        return {"CANCELLED"}


class PIE_Q_key(Operator):
    bl_idname = "pie.q_key"
    bl_label = get_pyfilename()
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.object != None:
            ob_mode = context.object.mode
            ob_type = context.object.type
            area_type = context.area.type

            if area_type == "VIEW_3D":
                if ob_mode == "OBJECT":
                    bpy.ops.wm.call_menu(name="PIE_MT_Bottom_Q_favorite")
                elif ob_mode == "EDIT":
                    if ob_type == "MESH":
                        bpy.ops.mesh.select_linked_pick("INVOKE_DEFAULT")
                    elif ob_type == "CURVE":
                        bpy.ops.curve.select_linked_pick("INVOKE_DEFAULT")
                    elif ob_type == "ARMATURE":
                        bpy.ops.armature.select_linked_pick("INVOKE_DEFAULT")
                elif ob_mode == "EDIT_GPENCIL":
                    bpy.ops.gpencil.select_linked("INVOKE_DEFAULT")
                    #     bpy.ops.gpencil.select_alternate('INVOKE_DEFAULT')   shift
            elif area_type == "IMAGE_EDITOR":
                bpy.ops.uv.select_linked_pick("INVOKE_DEFAULT", extend=True)
            elif area_type == "NODE_EDITOR":
                bpy.ops.pie.translate_nodes("INVOKE_DEFAULT")
        else:
            bpy.ops.wm.call_menu(name="PIE_MT_Bottom_Q_favorite")

        return {"FINISHED"}


class PIE_Q_key_shift(Operator):
    bl_idname = "pie.q_key_shift"
    bl_label = get_pyfilename()
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob_mode = context.object.mode
        ob_type = context.object.type
        area_type = context.area.type

        if area_type == "VIEW_3D":
            if ob_mode == "OBJECT":
                bpy.ops.object.select_linked("INVOKE_DEFAULT")
            if ob_mode == "EDIT":
                if ob_type == "MESH":
                    bpy.ops.mesh.select_linked_pick("INVOKE_DEFAULT", deselect=True)
                elif ob_type == "CURVE":
                    bpy.ops.curve.select_linked_pick("INVOKE_DEFAULT", deselect=True)
                elif ob_type == "ARMATURE":
                    bpy.ops.armature.select_linked_pick("INVOKE_DEFAULT", deselect=True)
            elif ob_mode == "SCULPT":
                # 当您尝试调用它时，执行上下文是 EXEC_DEFAULT，但它只支持 INVOKE_DEFAULT。
                bpy.ops.object.transfer_mode("INVOKE_DEFAULT")
            elif ob_mode == "EDIT_GPENCIL":
                if self.gpencil_seselect_linkes_toggle == True:
                    bpy.ops.gpencil.select_alternate("INVOKE_DEFAULT")
        elif area_type == "IMAGE_EDITOR":
            # print("UVyes")
            bpy.ops.uv.select_linked_pick("INVOKE_DEFAULT", extend=True, deselect=True)

        return {"FINISHED"}


class PIE_Q_key_ctrl(Operator):
    bl_idname = "pie.q_key_shift"
    bl_label = get_pyfilename()
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob_mode = get_ob_mode(context)
        area_type = context.area.type
        if area_type == "VIEW_3D" and ob_mode == "OBJECT":
            bpy.ops.wm.call_menu(name="VIEW3D_MT_make_links")

        return {"FINISHED"}


class PIE_Translate_Nodes(Operator):
    bl_idname = "pie.translate_nodes"
    bl_label = "翻译节点名称="
    bl_description = "翻译选择的节点或节点组的接口名称"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        return {"FINISHED"}


CLASSES = [
    PIE_MT_Bottom_Q_favorite,
    PIE_Q_key,
    PIE_Q_key_shift,
    Render_Viewport_OpenGL,
    PIE_Translate_Nodes,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        ("3D View", "VIEW_3D"),
        ("UV Editor", "EMPTY"),
        ("Node Editor", "NODE_EDITOR"),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("pie.q_key", "Q", "CLICK")
        kmi = km.keymap_items.new("pie.q_key_shift", "Q", "CLICK", shift=True)
        addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("wm.call_menu", "Q", "CLICK", ctrl=True)
    kmi.properties.name = "VIEW3D_MT_make_links"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
