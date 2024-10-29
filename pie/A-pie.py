import os
import random
import tempfile
from collections import defaultdict

import bpy
from bpy.types import Context, Menu, Operator
from mathutils import Matrix

from .pie_utils import *


class PIE_MT_Bottom_A(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if context.area.ui_type == "VIEW_3D":
            if ob_mode == "OBJECT":
                # 4 - LEFT
                add_operator(pie, "object.distribute", text="排列物体", icon="MOD_ARRAY")
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                pie.operator("object.select_all", text="反选", icon="DECORATE_OVERRIDE").action = "INVERT"
                # 7 - TOP - LEFT
                if ob_type == "EMPTY":
                    if context.active_object.data.type == "IMAGE":
                        pie.operator(
                            PIE_Image_usefaker.bl_idname,
                            text="设置参考伪用户",
                            icon="FAKE_USER_ON",
                        )
                    else:
                        pie.separator()
                else:
                    pie.separator()
                # 9 - TOP - RIGHT
                col = pie.split().box().column(align=True)
                col.scale_x = 1
                col.scale_y = 1.2
                row = col.row()
                row.label(text="资产")
                row.operator("asset.mark", text="标记", icon="ASSET_MANAGER")
                row.operator("asset.clear", text="抹除", icon="REMOVE").set_fake_user = False
                row = col.row()

                row.operator("pie.creat_costom_asset_preview", text="创建视图预览", icon="IMAGE_PLANE")

                row.separator()

                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                if ob_type in [
                    "ARMATURE",
                    "LIGHT",
                    "EMPTY",
                    "LATTICE",
                    "GPENCIL",
                    "LIGHT_PROBE",
                    "EMPTY",
                ]:
                    pie.separator()
                else:
                    pie.menu("VIEW3D_MT_object_convert", text="转换物体")

            # 编辑模式
            if ob_mode == "EDIT":
                if ob_type == "MESH":
                    # 4 - LEFT
                    pie.operator("mesh.select_less", text="缩减选择", icon="REMOVE")
                    # 6 - RIGHT
                    pie.operator("mesh.select_more", text="扩展选择", icon="ADD")
                    # 2 - BOTTOM
                    col = pie.split().box().column()
                    col.scale_y = 1.2
                    col.scale_x = 0.8
                    row = col.row(align=True)
                    # row.scale_y = 1.2
                    row.operator("mesh.edges_select_sharp", text="选择锐边")
                    row.separator(factor=0.5)
                    row.operator("mesh.edges_select_sharp", text="选择相连")
                    row = col.row(align=True)
                    # row.scale_y = 1.2
                    row.operator("mesh.select_face_by_sides", text="边数选面")
                    row.separator(factor=0.5)
                    row.operator("mesh.select_axis", text="按轴选点")
                    # 8 - TOP
                    pie.operator("mesh.select_all", text="反选", icon="EMPTY_SINGLE_ARROW").action = "INVERT"
                    # 7 - TOP - LEFT
                    pie.operator("mesh.select_prev_item", text="上一个元素", icon="REMOVE")
                    # 9 - TOP - RIGHT
                    pie.operator("mesh.select_next_item", text="下一个元素", icon="ADD")
                    # 1 - BOTTOM - LEFT
                    box = pie.split().box().column()
                    col.scale_y = 1.2
                    col.scale_x = 0.8
                    row = box.row(align=True)
                    row.operator("mesh.loop_multi_select", text="循环边").ring = False
                    row.separator(factor=0.5)
                    row.operator("mesh.loop_multi_select", text="并排边").ring = True
                    row = box.row(align=True)
                    row.operator("mesh.loop_to_region", text="选循环内侧")
                    row.separator(factor=0.5)
                    row.operator("mesh.region_to_loop", text="选区域轮廓")
                    # 3 - BOTTOM - RIGHT
                    box = pie.split().box().column()
                    col.scale_y = 1.2
                    col.scale_x = 0.8
                    row = box.row(align=True)
                    row.scale_y = 1.2
                    row.operator("mesh.faces_select_linked_flat", text="相连平展面")
                    row.operator("mesh.select_nth", text="间隔式弃选")
                    row = box.row(align=True)
                    row.scale_y = 1.2
                    row.operator("mesh.select_loose", text="选松散元素")
                    row.operator("mesh.select_non_manifold", text="选择非流形")

                if ob_type in ["CURVE", "SURFACE"]:
                    # 4 - LEFT
                    pie.operator("curve.select_less", text="缩减选择", icon="REMOVE")
                    # 6 - RIGHT
                    pie.operator("curve.select_more", text="扩展选择", icon="ADD")
                    # 2 - BOTTOM
                    pie.separator()
                    # 8 - TOP
                    pie.operator("curve.select_all", text="反选", icon="EMPTY_SINGLE_ARROW").action = "INVERT"
                    # 7 - TOP - LEFT
                    pie.operator("curve.de_select_last", text="选首端点", icon="FORCE_CURVE")
                    # 9 - TOP - RIGHT
                    pie.operator("curve.de_select_last", text="选尾端点", icon="FORCE_CURVE")
                    # 1 - BOTTOM - LEFT
                    pie.separator()
                    # 3 - BOTTOM - RIGHT
                    pie.menu(
                        "VIEW3D_MT_object_convert",
                        text="转换物体",
                        icon="MOD_DATA_TRANSFER",
                    )

        elif get_area_ui_type(context) == "UV":
            # 4 - LEFT
            pie.operator("uv.select_less", text="缩减选择", icon="REMOVE")
            # 6 - RIGHT
            pie.operator("uv.select_more", text="扩展选择", icon="ADD")
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("uv.select_all", text="反选", icon="EMPTY_SINGLE_ARROW").action = "INVERT"
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


class PIE_Image_usefaker(Operator):
    bl_idname = "pie.a_image_usefaker"
    bl_label = ""
    bl_description = ""
    bl_options = {"REGISTER"}

    toggle: bpy.props.BoolProperty(default=True)  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.toggle == True:
            for ob in context.selected_objects:
                if context.object.type == "EMPTY":
                    if ob.data.type == "IMAGE":
                        ob.data.use_fake_user = True
            self.report({"INFO"}, "已设置伪用户")
            self.toggle = False

        else:
            for ob in context.selected_objects:
                if context.object.type == "EMPTY":
                    if ob.data.type == "IMAGE":
                        ob.data.use_fake_user = False
            self.report({"INFO"}, "清除伪用户")
            self.toggle = True
        return {"FINISHED"}


class PIE_Apply_MultiObjects_Scale(bpy.types.Operator):
    bl_idname = "pie.apply_multi_objects_scale"
    bl_label = "Apply Multi Objects Scale"
    bl_description = "Apply multi objects scale that skip links objects"
    bl_options = {"REGISTER", "UNDO"}

    scale: bpy.props.BoolProperty(default=False)  # type: ignore
    rotation: bpy.props.BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.selected_objects:
            return True

    def execute(self, context):
        scale = self.scale
        rotation = self.rotation
        # how to apply tramsform with bpy and without ops
        # https://blender.stackexchange.com/questions/159538/how-to-apply-all-transformations-to-an-object-at-low-level
        se_objects = context.selected_objects

        data_links = defaultdict(list)
        for ob in se_objects:
            # filter Mesh,Curve
            if ob.type == "MESH" or "CURVE":
                data_links[ob].append(ob)

        # filter is linked objects
        for data, ob_list in data_links.items():
            print(data, ob_list)
            # skip parents & linked objects
            if len(ob_list) == 1 and data.children_recursive == []:
                mw = data.matrix_world
                mb = data.matrix_basis

                loc, rot, scale = mb.decompose()

                # rotation
                T = Matrix.Translation(loc)
                R = rot.to_matrix().to_4x4()
                S = Matrix.Diagonal(scale).to_4x4()

                if hasattr(data.data, "transform"):
                    if scale:
                        data.data.transform(S)
                        data.matrix_basis = T @ R
                    if rotation:
                        data.data.transform(R)
                        data.matrix_basis = T @ S

                # for c in data.children:
                #     c.matrix_local = S @ c.matrix_local

        return {"FINISHED"}


class PIE_MT_Bottom_A_Ctrl(Menu):
    bl_label = "Ctrl-A"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        if context.selected_objects != None:
            ob_type = context.object.type
            ob_mode = context.object.mode

            # 4 - LEFT
            rotation = pie.operator(PIE_Apply_MultiObjects_Scale.bl_idname, text="旋转-跳过实例")
            rotation.rotation = True
            # 6 - RIGHT
            scale = pie.operator(PIE_Apply_MultiObjects_Scale.bl_idname, text="缩放-跳过实例")
            scale.scale = True
            # 2 - BOTTOM
            if ob_type in ["MESH", "CURVE", "SURFACE", "FONT", "GPENCIL", "META"]:
                pie.operator("object.convert", text="可视几何->网格").target = "MESH"
            else:
                pie.separator()
            # 8 - TOP
            lrs1 = pie.operator("object.transform_apply", text="旋转&缩放")
            lrs1.location = False
            lrs1.rotation = True
            lrs1.scale = True
            # 7 - TOP - LEFT
            lrs2 = pie.operator("object.transform_apply", text="旋转")
            lrs2.location = False
            lrs2.rotation = True
            lrs2.scale = False
            # 9 - TOP - RIGHT
            lrs3 = pie.operator("object.transform_apply", text="缩放")
            lrs3.location = False
            lrs3.rotation = False
            lrs3.scale = True
            # 1 - BOTTOM - LEFT
            pie.operator("object.visual_transform_apply", text="可视变换")
            # 3 - BOTTOM - RIGHT
            pie.operator("object.duplicates_make_real", text="实例独立化")


class Creat_Costom_Asset_Preview(Operator):
    """创建自定义预览图"""

    bl_idname = "pie.creat_costom_asset_preview"
    bl_label = "视图自定义资产预览"
    bl_options = {"REGISTER", "UNDO"}

    resolution: bpy.props.IntProperty(name="设置预览精度", min=64, soft_max=512, default=256, step=64)  # type: ignore
    show_overlays: bpy.props.BoolProperty(name="叠加层", default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.object is not None:
            if context.active_object.type != "CAMERA" and context.mode == "OBJECT":
                return True

    def execute(self, context):
        scene = context.scene
        act_obj = context.active_object
        space = bpy.context.space_data

        # 保存现有场景信息
        save_render_X = scene.render.resolution_x
        save_render_y = scene.render.resolution_y
        save_percentage = scene.render.resolution_percentage
        save_filepath = scene.render.filepath
        save_file_format = scene.render.image_settings.file_format
        save_file_color_mode = scene.render.image_settings.color_mode
        save_file_compression = scene.render.image_settings.compression
        save_overlay = context.space_data.overlay.show_overlays

        # 孤立模式
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces[0]
                if space.local_view == None:  # check if not using local view
                    bpy.ops.view3d.localview(frame_selected=False)
                    change_local = True
                else:
                    change_local = False

        # 更改预览大小
        scene.render.resolution_y = self.resolution
        scene.render.resolution_x = self.resolution
        scene.render.resolution_percentage = 100
        # 设置图像格式
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.compression = 50
        scene.render.image_settings.color_mode = "RGBA"
        context.space_data.overlay.show_overlays = self.show_overlays

        # 设置图像缓存位置

        # 创建临时文件夹
        temp_dir = tempfile.mkdtemp()
        # 在临时文件夹中创建一个示例文件
        temp_filepath = os.path.join(temp_dir, str(random.randint(0, 999999)) + ".png")
        print(temp_filepath)

        # temp_filename = str(random.randint(0,999999))+".png"
        # temp_filepath = os.path.join(str(os.getenv('LOCALAPPDATA')),'temp', temp_filename)

        bpy.context.scene.render.filepath = temp_filepath

        # 设置资产设置自定义图像
        bpy.ops.render.opengl(write_still=True)

        act_obj.asset_mark()
        override = bpy.context.copy()
        override["id"] = act_obj
        with context.temp_override(**override):
            bpy.ops.ed.lib_id_load_custom_preview(filepath=temp_filepath)

        # 设置叠加层

        # 返回原有场景信息
        if change_local:
            bpy.ops.view3d.localview(frame_selected=False)
        os.unlink(temp_filepath)
        bpy.context.scene.render.resolution_y = save_render_y
        bpy.context.scene.render.resolution_x = save_render_X
        scene.render.resolution_percentage = save_percentage
        bpy.context.scene.render.filepath = save_filepath
        scene.render.image_settings.file_format = save_file_format
        scene.render.image_settings.color_mode = save_file_color_mode
        scene.render.image_settings.compression = save_file_compression
        context.space_data.overlay.show_overlays = save_overlay

        return {"FINISHED"}


classes = [
    PIE_MT_Bottom_A,
    PIE_MT_Bottom_A_Ctrl,
    PIE_Image_usefaker,
    PIE_Apply_MultiObjects_Scale,
    Creat_Costom_Asset_Preview,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG")
    kmi.properties.name = "PIE_MT_Bottom_A"
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG", ctrl=True)
    kmi.properties.name = "PIE_MT_Bottom_A_Ctrl"
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="UV Editor")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG")
    kmi.properties.name = "PIE_MT_Bottom_A"
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    class_register()
    register_keymaps()


def unregister():
    class_unregister()
    # unregister_keymaps()


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_W")
