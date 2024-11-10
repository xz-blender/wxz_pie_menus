import tempfile
from datetime import datetime
from pathlib import Path

import bpy
from bpy.types import Menu, Operator

from ..utils import get_prefs, safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_V(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)
        ui_type = get_area_ui_type(context)

        if ui_type == "VIEW_3D":
            if ob_mode == "OBJECT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                col = pie.split().column()
                col.scale_y = 1.7
                col.operator(
                    "pie.paste_clipboard_as_image_plane", text="剪切板 -> 参考图", icon="IMAGE_REFERENCE"
                ).is_ref = True
                col.operator("pie.paste_clipboard_as_image_plane", text="剪切板 -> 平面", icon="MESH_PLANE").is_ref = (
                    False
                )
                # 8 - TOP
                pie.separator()
                # 7 - TOP - LEFT
                pie.separator()
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT

            elif ob_mode == "EDIT":
                if ob_type == "CURVE":
                    # 4 - LEFT
                    pie.operator("curve.handle_type_set", text="矢量", icon="HANDLE_VECTOR").type = "VECTOR"
                    # 6 - RIGHT
                    pie.operator("curve.handle_type_set", text="对齐", icon="HANDLE_ALIGNED").type = "ALIGNED"
                    # 2 - BOTTOM
                    pie.separator()
                    # 8 - TOP
                    pie.operator(
                        "curve.handle_type_set",
                        text="自由/对齐",
                        icon="HANDLE_AUTOCLAMPED",
                    ).type = "TOGGLE_FREE_ALIGN"
                    # 7 - TOP - LEFT
                    pie.operator("curve.handle_type_set", text="自由", icon="HANDLE_FREE").type = "FREE_ALIGN"
                    # 9 - TOP - RIGHT
                    pie.operator("curve.handle_type_set", text="自动", icon="HANDLE_AUTO").type = "AUTOMATIC"
                    # 1 - BOTTOM - LEFT
                    pie.separator()
                    # 3 - BOTTOM - RIGHT
                    pie.separator()

                elif ob_type == "MESH":
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
        elif ui_type in ["GeometryNodeTree", "ShaderNodeTree", "CompositorNodeTree"]:
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator("pie.paste_clipboard_images_as_nodes", text="剪切板 -> 节点")


class PIE_Paste_ClipBord_Images_As_Nodes(bpy.types.Operator):
    bl_idname = "pie.paste_clipboard_images_as_nodes"
    bl_label = "剪切板图像到节点"
    bl_description = "导入剪切板图像到节点"
    bl_options = {"REGISTER", "UNDO"}

    single_image: None
    file_paths: list = []

    @classmethod
    def poll(cls, context):
        return True

    def __init__(self):
        self.single_image = None
        self.file_paths = []

    def init_clipboard(self, context):
        try:
            from PIL import Image, ImageGrab
        except ImportError:
            self.report({"ERROR"}, "pyperclip或pillow库未安装，请在偏好设置安装库。")
            return {"CANCELLED"}
        try:
            temp_dir = tempfile.gettempdir()
            clopboard = ImageGrab.grabclipboard()
            if isinstance(clopboard, Image.Image):
                # 保存图像到临时文件夹并返回路径
                current_time = datetime.now().strftime("%Y%m%d,%H%M%S")
                image_name = f"xz_clipboard_image_{current_time}.png"
                self.single_image = str(Path(temp_dir) / image_name)
                clopboard.save(self.single_image)
                print(f"剪切板图像已缓存到: {self.single_image}")
            elif isinstance(clopboard, list):
                # 如果剪贴板包含文件，则打印其绝对路径
                for file in clopboard:
                    file = Path(file)
                    if file.suffix.lower() in [
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".bmp",
                        ".gif",
                        ".webp",
                        ".tif",
                        ".exr",
                        ".hdri",
                    ]:
                        self.file_paths.append(Path(file))
                        # print(f"文件路径: {file}")
            else:
                self.report({"ERROR"}, "剪贴板不包含图像或文件")
                return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"访问剪贴板时出错:{e}")
            return {"CANCELLED"}

    def get_node_tree(self, context):
        space = context.area.spaces.active
        node_tree = space.node_tree
        if node_tree is not None:
            # print("当前节点树名称: ", node_tree.name)
            # print("节点树类型: ", node_tree.bl_idname)
            return node_tree
        else:
            self.report({"ERROR"}, "未找到节点树")
            return None

    def invoke(self, context, event):
        self.init_clipboard(context)

        node_tree = self.get_node_tree(context)
        if node_tree is None:
            return {"CANCELLED"}

        def get_location(self, context, event):
            # 获取节点编辑器的区域和视图
            area = context.area
            region = None
            for reg in area.regions:
                if reg.type == "WINDOW":
                    region = reg
                    break
            if not region:
                self.report({"WARNING"}, "未找到节点编辑器的视图区域")
                return 0, 0  # 或者其他默认值
            # 获取 View2D 对象
            view2d = region.view2d
            # 获取鼠标在区域内的坐标
            region_x = event.mouse_region_x
            region_y = event.mouse_region_y
            # 将区域坐标转换为视图坐标
            node_x, node_y = view2d.region_to_view(region_x, region_y)

            return node_x, node_y

        def get_inamge_node_type(node_tree):
            if node_tree.bl_idname == "ShaderNodeTree":
                return "ShaderNodeTexImage"
            elif node_tree.bl_idname == "GeometryNodeTree":
                return "GeometryNodeImageTexture"
            elif node_tree.bl_idname == "CompositorNodeTree":
                return "CompositorNodeImage"
            else:
                self.report({"ERROR"}, f"不支持的节点树类型: {node_tree.bl_idname}")
                return None

        def set_inamge_node_image(node_tree, image_node, image):
            if node_tree.bl_idname in ["ShaderNodeTree", "CompositorNodeTree"]:
                setattr(image_node, "image", image)
            elif node_tree.bl_idname == "GeometryNodeTree":
                setattr(image_node, "inputs['Image'].default_value", image)
            else:
                self.report({"ERROR"}, f"不支持的节点树类型: {node_tree.bl_idname}")
                return None

        def add_image_node(node_tree):
            node_type = get_inamge_node_type(node_tree)
            try:
                image_node = node_tree.nodes.new(type=node_type)
                return image_node
            except Exception as e:
                self.report({"ERROR"}, f"创建节点时出错: {e}")
                return None

        def node_load_image(image_node, image):
            if Path(image).name in bpy.data.images:
                image = bpy.data.images[image.name]
            else:
                image = bpy.data.images.load(str(image))

            set_inamge_node_image(node_tree, image_node, image)

        def select_nodes(node_tree, image_nodes, is_single_image=True):
            for node in node_tree.nodes:
                node.select = False
            if is_single_image:
                image_nodes.select = True
                node_tree.nodes.active = image_nodes
            else:
                for image_node in image_nodes:
                    image_node.select = True
                node_tree.nodes.active = image_nodes[-1]

        def move_node():
            return bpy.ops.node.translate_attach_remove_on_cancel("INVOKE_DEFAULT")

        def finish_add_node(self, node_tree):
            node = add_image_node(node_tree)
            if node is None:
                return {"CANCELLED"}
            node_x, node_y = get_location(self, context, event)
            node.location = (node_x, node_y)
            node_load_image(node, self.single_image)
            select_nodes(node_tree, node, is_single_image=True)
            move_node()

        def finish_images_nodes(self, node_tree):
            nodes = []
            offset = 30
            node_x, node_y = get_location(self, context, event)
            for iter, file_path in enumerate(self.file_paths):
                node = add_image_node(node_tree)
                node.location = (node_x + iter * offset, node_y + iter * offset)
                node_load_image(node, file_path)
                nodes.append(node)
            select_nodes(node_tree, nodes, is_single_image=False)
            move_node()

        if self.single_image:
            finish_add_node(self, node_tree)
        elif self.file_paths:
            finish_images_nodes(self, node_tree)
        return {"FINISHED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_V,
    PIE_Paste_ClipBord_Images_As_Nodes,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        ("3D View", "VIEW_3D"),
        # ("UV Editor", "EMPTY"),
        ("Node Editor", "NODE_EDITOR"),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new("wm.call_menu_pie", "V", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_V"
        addon_keymaps.append(km)

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    km.keymap_items.new("pie.drop_it", "V", "CLICK")
    addon_keymaps.append(km)


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
