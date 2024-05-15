import os

import bpy
import bpy.utils.previews
from bpy.types import Menu, Operator

from .utils import change_default_keymap, restored_default_keymap, set_pie_ridius

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Interface",
}

preview_dict = None


def load_previews():
    global preview_dict
    preview_dict = bpy.utils.previews.new()
    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
    for file in os.scandir(dir):
        if file.name.endswith(".png"):
            name = os.path.splitext(file.name)[0].upper()
            preview_dict.load(name, file.path, "IMAGE")


class VIEW3D_PIE_MT_Bottom_Q(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        set_pie_ridius(context, 100)

        ui = context.area.ui_type
        # print(ui)
        if preview_dict is not None:
            if ui == "VIEW_3D":
                # 4 - LEFT
                pie.operator("view3d.view_axis", text="左", icon_value=preview_dict["A4"].icon_id).type = "LEFT"
                # 6 - RIGHT
                pie.operator("view3d.view_axis", text="右", icon_value=preview_dict["A6"].icon_id).type = "RIGHT"
                # 2 - BOTTOM
                pie.operator("view3d.view_camera", text="摄像机", icon="VIEW_CAMERA")
                # 8 - TOP
                pie.operator("view3d.view_axis", text="顶", icon_value=preview_dict["A8"].icon_id).type = "TOP"
                # 7 - TOP - LEFT
                pie.operator("view3d.view_axis", text="后", icon_value=preview_dict["A7"].icon_id).type = "BACK"
                # 9 - TOP - RIGHT
                pie.operator("view3d.view_axis", text="前", icon_value=preview_dict["A9"].icon_id).type = "FRONT"
                # 1 - BOTTOM - LEFT
                pie.operator("view3d.view_all", text="全部", icon_value=preview_dict["A1"].icon_id)
                # 3 - BOTTOM - RIGHT
                pie.operator("view3d.view_selected", text="所选", icon_value=preview_dict["A3"].icon_id)
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
                        pie.operator(Node_Change_Image_ColorSpace.bl_idname, text="图像-非彩色").colorspace = (
                            "Non-Color"
                        )
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
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        set_pie_ridius(context, 100)

        ui = context.area.ui_type
        print(ui)
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


E = ["VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR"]
B = [
    # General
    ("3D_VIEW", "3D视图", ""),  # 0
    ("IMAGE_EDITOR", "图像编辑器", ""),  # 1
    ("UV", "UV编辑器", ""),  # 2
    ("CompositorNodeTree", "合成器", ""),  # 3
    ("TextureNodeTree", "纹理节点编辑器", ""),  # 4
    ("GeometryNodeTree", "几何节点编辑器", ""),  # 5
    ("ShaderNodeTree", "着色器编辑器", ""),  # 6
    ("SEQUENCE_EDITOR", "视频序列编辑器", ""),  # 7
    ("CLIP_EDITOR", "影片剪辑编辑器", ""),  # 8
    # Animation
    ("DOPESHEET", "动画摄影表", ""),  # 9
    ("TIMELINE", "时间线", ""),  # 10
    ("FCURVES", "曲线编辑器", ""),  # 11
    ("DRIVERS", "驱动器", ""),  # 12
    ("NLA_EDITOR", "非线性动画", ""),  # 13
    # Scripting
    ("TEXT_EDITOR", "文本编辑器", ""),  # 14
    ("CONSOLE", "Python 控制台", ""),  # 15
    ("INFO", "信息", ""),
    # Scripting
    ("OUTLINER", "大纲视图", ""),  # 16
    ("PROPERTIES", "属性", ""),  # 17
    ("FILES", "文件浏览器", ""),  # 18
    ("ASSETS", "资产浏览器", ""),  # 19
    ("SPREADSHEET", "电子表格", ""),  # 20
    ("PREFERENCES", "偏好设置", ""),  # 21
]


classes = [
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
    load_previews()


def unregister():
    global preview_dict
    bpy.utils.previews.remove(preview_dict)
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()

#     bpy.ops.wm.call_menu(name="PIE_MT_Bottom_Q_favorite")
