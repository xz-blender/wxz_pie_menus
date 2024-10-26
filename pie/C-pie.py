import tempfile
from datetime import datetime
from pathlib import Path

import bpy
from bpy.types import Menu, Operator

from .pie_utils import *


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
        pie.separator()
        # 6 - RIGHT
        pie.operator("view3d.walk", text="行走漫游", icon="MOD_DYNAMICPAINT")
        # 2 - BOTTOM
        if ob_type == "CAMERA" or region == "CAMERA":
            pie.prop(context.space_data, "lock_camera", text="锁定相机视图")
        else:
            pie.operator("pie.material_pincker")
        # 8 - TOP
        pie.operator("mesh.select_mode", text="边").type = "EDGE"
        # 7 - TOP - LEFT
        pie.operator("mesh.select_mode", text="点").type = "VERT"
        # 9 - TOP - RIGHT
        pie.operator("mesh.select_mode", text="面").type = "FACE"
        # 1 - BOTTOM - LEFT
        pie.operator("view3d.camera_to_view", text="对齐相机至视图")
        # 3 - BOTTOM - RIGHT
        if ob_type == "CAMERA":
            pie.operator("view3d.object_as_camera", text="激活选择相机")
        else:
            col = pie.split().column()
            col.scale_y = 1.7
            col.operator(
                "pie.paste_clipboard_as_image_plane", text="剪切板 - 参考图", icon="IMAGE_REFERENCE"
            ).is_ref = True
            col.operator("pie.paste_clipboard_as_image_plane", text="剪切板 - 平面", icon="MESH_PLANE").is_ref = False


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
            file_paths = None
            temp_dir = tempfile.gettempdir()
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                # 保存图像到临时文件夹并返回路径
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_name = f"clipboard_image_{current_time}.png"
                image_path = str(Path(temp_dir) / image_name)
                image.save(image_path)
                print(f"Image saved to: {image_path}")
            elif isinstance(image, list):
                # 如果剪贴板包含文件，则打印其绝对路径
                file_paths = [str(Path(file).absolute) for file in image]
                for file_path in file_paths:
                    print(f"File path: {file_path}")
            else:
                self.report({"ERROR"}, "剪贴板不包含图像或文件")
                return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"访问剪贴板时出错:{e}")
            return {"CANCELLED"}

        def add_plane(file_path, image_name, dir):
            bpy.ops.image.import_as_mesh_planes(
                relative=False, filepath=file_path, files=[{"name": image_name, "name": image_name}], directory=dir
            )

        def add_ref(file_path):
            bpy.ops.object.empty_image_add(filepath=file_path, align="VIEW")

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

        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_C,
    PIE_Paste_ClipBord_as_Image_Plane,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    # km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    # kmi = km.keymap_items.new("pie.paste_clipboard_as_image_plane", "R", "PRESS", ctrl=True, shift=True)

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "C", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_C"
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


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_C")
