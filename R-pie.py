import bpy
from bpy.types import Menu, Operator
from math import pi


bl_info = {
    "name": "R-PIE",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View"}


class VIEW3D_PIE_MT_Bottom_R(Menu):
    bl_label = "R"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        if ob_mode == 'OBJECT':
            # 4 - LEFT
            pie.operator(PIE_Transform_Rotate_OP.bl_idname,
                         text='Z轴-90°', icon='TRIA_LEFT_BAR').degree = -pi/2
            # 6 - RIGHT
            pie.operator(PIE_Transform_Rotate_OP.bl_idname,
                         text='Z轴+90°', icon='TRIA_RIGHT_BAR').degree = pi/2
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT

        elif ob_mode == 'EDIT':
            # 4 - LEFT
            pie.operator(PIE_Transform_Rotate_OP.bl_idname,
                         text='Z轴-90°', icon='TRIA_LEFT_BAR').degree = -pi/2
            # 6 - RIGHT
            pie.operator(PIE_Transform_Rotate_OP.bl_idname,
                         text='Z轴+90°', icon='TRIA_RIGHT_BAR').degree = pi/2

            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT# 9 - TOP - RIGHT
            if ob_type == 'MESH':
                pie.operator('mesh.edge_rotate',
                             text='边-逆时针', icon='FRAME_PREV').use_ccw = True
                pie.operator('mesh.edge_rotate',
                             text='边-顺时针', icon='FRAME_NEXT').use_ccw = False
            else:
                pie.separator()
                pie.separator()
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


class UV_PIE_MT_Bottom_R(Menu):
    bl_label = "UV-R"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        ob_type = context.object.type
        ob_mode = context.object.mode

        # 4 - LEFT
        pie.operator(PIE_UV_Rotate_OP.bl_idname, text='Z轴-90°',
                     icon='TRIA_LEFT_BAR').degree = -pi/2
        # 6 - RIGHT
        pie.operator(PIE_UV_Rotate_OP.bl_idname, text='Z轴+90°',
                     icon='TRIA_RIGHT_BAR').degree = pi/2
        # 2 - BOTTOM
        # 8 - TOP
        # 7 - TOP - LEFT
        # 9 - TOP - RIGHT

        # 1 - BOTTOM - LEFT
        # 3 - BOTTOM - RIGHT


class PIE_Transform_Rotate_OP(Operator):
    bl_idname = "pie.tramsform_rotate"
    bl_label = "Pie R 物体网格"
    bl_description = ""
    bl_options = {"REGISTER"}

    degree: bpy.props.FloatProperty(name="Rotate_Dgree")

    def execute(self, context):
        bpy.ops.transform.rotate(value=self.degree,
                                 orient_axis='Z',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        return {"FINISHED"}


class PIE_UV_Rotate_OP(Operator):
    bl_idname = "pie.uv_rotate"
    bl_label = "Pie R 图像UV"
    bl_description = ""
    bl_options = {"REGISTER"}

    degree: bpy.props.FloatProperty(name="Rotate_Dgree")

    def execute(self, context):
        bpy.ops.transform.rotate(value=self.degree,
                                 orient_axis='Z',
                                 orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_R,
    UV_PIE_MT_Bottom_R,
    PIE_Transform_Rotate_OP,
    PIE_UV_Rotate_OP,
]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(
        idname='wm.call_menu_pie',
        type="R",
        value="CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_R"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Image", space_type="IMAGE_EDITOR")
    kmi = km.keymap_items.new(
        idname='wm.call_menu_pie',
        type="R",
        value="CLICK_DRAG")
    kmi.properties.name = "UV_PIE_MT_Bottom_R"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_R")
