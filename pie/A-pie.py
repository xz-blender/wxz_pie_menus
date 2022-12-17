import os
import bpy
from bpy.types import Menu, Operator
from .utils import check_rely_addon, rely_addons, set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class PIE_MT_Bottom_A(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        # set pie radius
        set_pie_ridius(context, 100)

        # addon1:"DPFR Distribute Objects"
        addon1 = check_rely_addon(rely_addons[4][0], rely_addons[4][1])

        if ob_mode == 'OBJECT':
            # 4 - LEFT
            if addon1 == '2':
                pie.operator('pie.empty_operator',
                             text='未找到"Distribute Objects"插件!')
            elif addon1 == '0':
                pie.operator('pie.empty_operator',
                             text='启用"Distribute Objects"插件!')
            elif addon1 == '1':
                pie.operator('object.distribute',
                             text='排列物体', icon='MOD_ARRAY')
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("object.select_all", text="反选",
                         icon='DECORATE_OVERRIDE').action = 'INVERT'
            # 7 - TOP - LEFT
            if ob_type == 'EMPTY':
                if context.active_object.data.type == 'IMAGE':
                    pie.operator(
                        PIE_Image_usefaker.bl_idname,
                        text='设置参考伪用户',
                        icon='FAKE_USER_ON',
                    )
                else:
                    pie.separator()
            else:
                pie.separator()
            # 9 - TOP - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_x = 1.3
            col.scale_y = 1.2
            row = col.row()
            row.operator("asset.mark", text="标记资产", icon="ASSET_MANAGER")
            row = col.row()
            row.operator('asset.clear', text='抹除资产',
                         icon='REMOVE').set_fake_user = False

            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            if ob_type in [
                'ARMATURE',
                'LIGHT',
                'EMPTY',
                'LATTICE',
                'GPENCIL',
                'LIGHT_PROBE',
                'EMPTY',
            ]:
                pie.separator()
            else:
                pie.menu("VIEW3D_MT_object_convert", text="转换物体")

        # 编辑模式
        if context.object.mode == 'EDIT':
            if ob_type == 'MESH':
                # 4 - LEFT
                pie.operator("mesh.select_less", text="缩减选择", icon='REMOVE')
                # 6 - RIGHT
                pie.operator("mesh.select_more", text="扩展选择", icon="ADD")
                # 2 - BOTTOM
                box = pie.split().box().column()
                box.scale_y = 1.2
                row = box.row(align=True)
                row.operator("mesh.edges_select_sharp", text="选择锐边")
                row.separator_spacer()
                row.operator("mesh.edges_select_sharp", text="选择相连")
                row = box.row(align=True)
                row.operator("mesh.select_face_by_sides", text="边数选面")
                row.separator_spacer()
                row.operator("mesh.select_axis", text="按轴选点")
                # 8 - TOP
                pie.operator(
                    "mesh.select_all", text="反选", icon='EMPTY_SINGLE_ARROW'
                ).action = 'INVERT'
                # 7 - TOP - LEFT
                pie.operator("mesh.select_prev_item",
                             text="上一个元素", icon="REMOVE")
                # 9 - TOP - RIGHT
                pie.operator("mesh.select_next_item", text="下一个元素", icon="ADD")
                # 1 - BOTTOM - LEFT
                box = pie.split().box().column()
                box.scale_y = 1.2
                row = box.row(align=True)
                row.operator("mesh.loop_multi_select", text="循环边").ring = False
                row.operator("mesh.loop_multi_select", text="并排边").ring = True
                row = box.row(align=True)
                row.operator("mesh.loop_to_region", text="选循环内侧")
                row.operator("mesh.region_to_loop", text="选区域轮廓")
                # 3 - BOTTOM - RIGHT
                box = pie.split().box().column()
                box.scale_y = 1.2
                row = box.row(align=True)
                row.operator("mesh.faces_select_linked_flat", text="相连平展面")
                row.operator("mesh.select_nth", text="间隔式弃选")
                row = box.row(align=True)
                row.operator("mesh.select_loose", text="选松散元素")
                row.operator("mesh.select_non_manifold", text="选择非流形")

            if ob_type in ['CURVE', 'SURFACE']:
                # 4 - LEFT
                pie.operator("curve.select_less", text="缩减选择", icon='REMOVE')
                # 6 - RIGHT
                pie.operator("curve.select_more", text="扩展选择", icon='ADD')
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                pie.operator(
                    "curve.select_all", text="反选", icon='EMPTY_SINGLE_ARROW'
                ).action = 'INVERT'
                # 7 - TOP - LEFT
                pie.operator("curve.de_select_last",
                             text="选首端点", icon='FORCE_CURVE')
                # 9 - TOP - RIGHT
                pie.operator("curve.de_select_last",
                             text="选尾端点", icon='FORCE_CURVE')
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.menu(
                    "VIEW3D_MT_object_convert",
                    text="转换物体",
                    icon='MOD_DATA_TRANSFER',
                )


class PIE_Image_usefaker(Operator):
    bl_idname = "pie.a_image_usefaker"
    bl_label = ""
    bl_description = ""
    bl_options = {"REGISTER"}

    toggle: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.toggle == True:
            for ob in context.selected_objects:
                if context.object.type == 'EMPTY':
                    if ob.data.type == "IMAGE":
                        ob.data.use_fake_user = True
            self.toggle = False
            return {"FINISHED"}
        else:
            for ob in context.selected_objects:
                if context.object.type == 'EMPTY':
                    if ob.data.type == "IMAGE":
                        ob.data.use_fake_user = False
            self.toggle = True


class PIE_MT_Bottom_A_Ctrl(Menu):
    bl_label = "Ctrl-A"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        set_pie_ridius(context, 100)

        if context.selected_objects != None:
            ob_type = context.object.type
            ob_mode = context.object.mode

            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            if ob_type in ['MESH', 'CURVE', 'SURFACE', 'FONT', 'GPENCIL', 'META']:
                pie.operator('object.convert', text='可视几何->网格').target = 'MESH'
            else:
                pie.separate()
            # 8 - TOP
            lrs1 = pie.operator('object.transform_apply', text='旋转&缩放')
            lrs1.location = False
            lrs1.rotation = True
            lrs1.scale = True
            # 7 - TOP - LEFT
            lrs2 = pie.operator('object.transform_apply', text='旋转')
            lrs2.location = False
            lrs2.rotation = True
            lrs2.scale = False
            # 9 - TOP - RIGHT
            lrs3 = pie.operator('object.transform_apply', text='缩放')
            lrs3.location = False
            lrs3.rotation = False
            lrs3.scale = True
            # 1 - BOTTOM - LEFT
            pie.operator('object.visual_transform_apply', text='可视变换')
            # 3 - BOTTOM - RIGHT
            pie.operator('object.duplicates_make_real', text='实例独立化')


classes = [
    PIE_MT_Bottom_A,
    PIE_MT_Bottom_A_Ctrl,
    PIE_Image_usefaker,
]


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'A', 'CLICK_DRAG')
    kmi.properties.name = "PIE_MT_Bottom_A"

    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG", ctrl=True)
    kmi.properties.name = "PIE_MT_Bottom_A_Ctrl"
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
        try:
            bpy.utils.register_class(cls)
        except:
            None
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="PIE_MT_Bottom_A")
