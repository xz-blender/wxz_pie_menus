from pathlib import Path

import bpy
import bpy.utils.previews
from bpy.types import Menu, Operator

from ..utils import ADDON_ID, safe_register_class, safe_unregister_class
from .utils import *

preview_collections = {}
pview_pcoll_name = ADDON_ID.split(".")[-1]


def load_custom_icon():
    icons_directory = Path(__file__).parent / "icons"
    pcoll = bpy.utils.previews.new()
    for path in icons_directory.glob("*.png"):
        name = path.stem.upper()  # 使用文件名（不含扩展名）作为键名
        pcoll.load(name, str(path), "IMAGE")
    preview_collections[pview_pcoll_name] = pcoll


def get_icon_id(pic_name):
    return preview_collections[pview_pcoll_name][pic_name.upper()].icon_id


class VIEW3D_PIE_MT_Bottom_Q(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ui = get_area_ui_type(context)
        # print("UI:", ui)
        if ui == "VIEW_3D":
            # 4 - LEFT
            pie.operator("view3d.view_axis", text="左", icon_value=get_icon_id("a4")).type = "LEFT"
            # 6 - RIGHT
            pie.operator("view3d.view_axis", text="右", icon_value=get_icon_id("a6")).type = "RIGHT"
            # 2 - BOTTOM
            pie.operator("view3d.view_camera", text="摄像机", icon="VIEW_CAMERA")
            # 8 - TOP
            pie.operator("view3d.view_axis", text="顶", icon_value=get_icon_id("a8")).type = "TOP"
            # 7 - TOP - LEFT
            pie.operator("view3d.view_axis", text="后", icon_value=get_icon_id("a7")).type = "BACK"
            # 9 - TOP - RIGHT
            pie.operator("view3d.view_axis", text="前", icon_value=get_icon_id("a9")).type = "FRONT"
            # 1 - BOTTOM - LEFT
            pie.operator("view3d.view_all", text="全部", icon_value=get_icon_id("a1"))
            # 3 - BOTTOM - RIGHT
            pie.operator("view3d.view_selected", text="所选", icon_value=get_icon_id("a3"))
        elif ui == "UV":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.operator("image.view_all", text="全部")
            # 3 - BOTTOM - RIGHT
            pie.operator("image.view_selected", text="所选")
        elif ui == "FCURVES":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator("graph.view_frame", text="当前帧")
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.operator("graph.view_all", text="全部")
            # 3 - BOTTOM - RIGHT
            pie.operator("graph.view_selected", text="所选")

        elif ui == "ShaderNodeTree":
            # 4 - LEFT # 6 - RIGHT
            if context.active_object.active_material.node_tree.nodes.active != None:
                if context.active_object.active_material.node_tree.nodes.active.type == "TEX_IMAGE":
                    pie.operator(Node_Change_Image_ColorSpace.bl_idname, text="图像-sRGB").colorspace = "sRGB"
                    pie.operator(Node_Change_Image_ColorSpace.bl_idname, text="图像-非彩色").colorspace = "Non-Color"
                else:
                    pie.operator("node.nw_reset_nodes", text="重置所选")
                    pie.separator()
            else:
                pie.separator()
                pie.separator()

            # 2 - BOTTOM
            pie.operator("node.mute_toggle", text="停用")
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            if context.active_object.active_material.node_tree.nodes.active != None:
                if context.active_object.active_material.node_tree.nodes.active.type == "TEX_IMAGE":
                    new = pie.split()
                    sp1 = new.split().box().column()
                    sp1.label(text="纹理插值")
                    sp1.operator(Node_Change_Image_Interpolation.bl_idname, text="线性").interpolation = "Linear"
                    sp1.operator(Node_Change_Image_Interpolation.bl_idname, text="智能").interpolation = "Smart"
                    sp2 = new.split().box().column()
                    sp2.label(text="投射方法")
                    sp2.operator(Node_Change_Image_Projection.bl_idname, text="平直").projection = "FLAT"
                    sp2.operator(Node_Change_Image_Projection.bl_idname, text="立方体").projection = "BOX"
                else:
                    pie.separator()
            else:
                pie.separator()
            # 9 - TOP - RIGHT
            box = pie.box()
            box.props_enum(context.object.active_material, "blend_method")
            # 1 - BOTTOM - LEFT
            pie.operator("node.view_all", text="全部")
            # 3 - BOTTOM - RIGHT
            pie.operator("node.view_selected", text="所选")

        elif ui == "GeometryNodeTree":
            # 4 - LEFT
            pie.operator("node.nw_reset_nodes", text="重置所选")
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator("node.mute_toggle", text="停用")
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.operator("node.view_all", text="全部")
            # 3 - BOTTOM - RIGHT
            pie.operator("node.view_selected", text="所选")

        elif ui == "CompositorNodeTree":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator("node.mute_toggle", text="停用")
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.operator("node.view_all", text="全部")
            # 3 - BOTTOM - RIGHT
            pie.operator("node.view_selected", text="所选")


class VIEW3D_PIE_MT_Bottom_Ctrl_Alt_Q(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ui = get_area_ui_type(context)
        # print(ui)

        if ui == "VIEW_3D":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.separator()


class Node_Change_Image_ColorSpace(Operator):
    bl_idname = "pie.node_change_image_colorspace"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    colorspace: bpy.props.StringProperty(name="colorspace")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        nodes = context.active_object.active_material.node_tree.nodes
        selected_nodes = [x for x in nodes if x.select and x.type == "TEX_IMAGE"]
        for node in selected_nodes:
            node.image.colorspace_settings.name = self.colorspace
        return {"FINISHED"}


class Node_Change_Image_Projection(Operator):
    bl_idname = "pie.node_change_image_projection"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    projection: bpy.props.StringProperty(name="projection")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        nodes = context.active_object.active_material.node_tree.nodes
        selected_nodes = [x for x in nodes if x.select and x.type == "TEX_IMAGE"]
        for node in selected_nodes:
            node.projection = self.projection
        return {"FINISHED"}


class Node_Change_Image_Interpolation(Operator):
    bl_idname = "pie.node_change_image_interpolation"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    interpolation: bpy.props.StringProperty(name="interpolation")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        nodes = context.active_object.active_material.node_tree.nodes
        selected_nodes = [x for x in nodes if x.select and x.type == "TEX_IMAGE"]
        for node in selected_nodes:
            node.interpolation = self.interpolation
        return {"FINISHED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_Q,
    Node_Change_Image_ColorSpace,
    Node_Change_Image_Projection,
    Node_Change_Image_Interpolation,
    VIEW3D_PIE_MT_Bottom_Ctrl_Alt_Q,
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
        kmi = km.keymap_items.new("wm.call_menu_pie", "Q", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Q"
        addon_keymaps.append(km)

    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(
        idname="wm.call_menu_pie", type="Q", value="CLICK_DRAG", shift=False, ctrl=True, alt=True, oskey=False
    )
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_Ctrl_Alt_Q"
    addon_keymaps.append(km)


def register():
    load_custom_icon()
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    bpy.utils.previews.remove(preview_collections[pview_pcoll_name])
    preview_collections.clear()
    safe_unregister_class(CLASSES)
