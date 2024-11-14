import tempfile
from datetime import datetime
from pathlib import Path

import bpy
from bpy.types import Menu, Operator

from ..utils import get_prefs, safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_C(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)
        set_pie_ridius()

        region = context.space_data.region_3d.view_perspective

        # 4 - LEFT
        pie.prop(get_prefs(), "AutoSwitch_ActiveCam_Default", text="自动激活相机")
        # 6 - RIGHT
        pie.operator("view3d.walk", text="行走漫游", icon="MOD_DYNAMICPAINT")
        # 2 - BOTTOM
        if ob_type == "CAMERA" or region == "CAMERA":
            pie.prop(context.space_data, "lock_camera", text="锁定相机视图")
        else:
            pie.operator("pie.material_pincker")
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.operator("view3d.camera_to_view", text="对齐相机至视图")
        # 3 - BOTTOM - RIGHT
        if ob_type == "CAMERA":
            pie.operator("view3d.object_as_camera", text="激活选择相机")
        else:
            pie.separator()


class PIE_Paste_ClipBord_as_Image_Plane(bpy.types.Operator):
    bl_idname = "pie.paste_clipboard_as_image_plane"
    bl_label = "导入剪切板图像"
    bl_description = "导入剪切板图像"
    bl_options = {"REGISTER", "UNDO"}

    is_ref: bpy.props.BoolProperty(default=True)  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:

            from PIL import Image, ImageGrab
        except ImportError:
            self.report({"ERROR"}, "pyperclip或pillow库未安装，请在偏好设置安装库。")
            return {"CANCELLED"}

        try:
            image_path = None
            file_paths = []
            temp_dir = tempfile.gettempdir()
            clopboard = ImageGrab.grabclipboard()
            if isinstance(clopboard, Image.Image):
                # 保存图像到临时文件夹并返回路径
                current_time = datetime.now().strftime("%m%d_%H%M")
                image_name = f"xz_clipboard_image_{current_time}.png"
                image_path = str(Path(temp_dir) / image_name)
                clopboard.save(image_path)
                print(f"剪切板图像缓存到: {image_path}")
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
                        file_paths.append(Path(file))
                        print(f"文件路径: {file}")
            else:
                self.report({"ERROR"}, "剪贴板不包含图像或文件")
                return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"访问剪贴板时出错:{e}")
            return {"CANCELLED"}

        def add_plane(file_path, image_name, dir):
            bpy.ops.image.import_as_mesh_planes(
                relative=False, filepath=str(file_path), files=[{"name": image_name, "name": image_name}], directory=dir
            )

        def add_ref(file_path):
            bpy.ops.object.empty_image_add(filepath=str(file_path), align="VIEW")

        if self.is_ref:
            if image_path:
                add_ref(image_path)
            elif file_paths:
                for file_path in file_paths:
                    add_ref(file_path)
        else:
            if image_path:
                add_plane(image_path, image_name, temp_dir)
            elif file_paths:
                for file_path in file_paths:
                    dir = str(Path(file_path).parent)
                    image_name = Path(file_path).name
                    add_plane(file_path, image_name, dir)

        file_paths.clear()
        image_path = None
        file_paths = []
        return {"FINISHED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_C,
    PIE_Paste_ClipBord_as_Image_Plane,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "C", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_C"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
