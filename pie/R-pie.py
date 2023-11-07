import bpy
from bpy.types import Menu, Operator
import math
from math import pi
from mathutils import Quaternion
from .utils import set_pie_ridius, change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_R(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        if context.area.ui_type == 'VIEW_3D':

            ob_type = context.object.type
            ob_mode = context.object.mode

            set_pie_ridius(context, 100)

            get_orient = context.scene.transform_orientation_slots[0].type

            if ob_mode == 'OBJECT':
                # 4 - LEFT
                pie.operator(
                    PIE_Transform_Rotate_Z.bl_idname, text='Z轴-90°').degree = (-pi / 2)
                # 6 - RIGHT
                pie.operator(
                    PIE_Transform_Rotate_Z.bl_idname, text='Z轴+90°').degree = (pi / 2)
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                rotate_Y = pie.operator('transform.rotate', text='Y',icon='EVENT_Y')
                rotate_Y.orient_type = get_orient
                rotate_Y.orient_axis = 'Y'
                # 7 - TOP - LEFT
                TL = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向后转')
                TL.x = True
                TL.y = False
                TL.degree = pi / 2
                # 9 - TOP - RIGHT
                TR = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向前转')
                TR.x = True
                TR.y = False
                TR.degree = -pi / 2
                # 1 - BOTTOM - LEFT
                TR = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向左转')
                TR.x = False
                TR.y = True
                TR.degree = pi / 2
                # 3 - BOTTOM - RIGHT
                TR = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向右转')
                TR.x = False
                TR.y = True
                TR.degree = -pi / 2

            elif ob_mode == 'EDIT':
                # 4 - LEFT
                pie.operator(
                    PIE_Transform_Rotate_Z.bl_idname, text='Z轴-90°').degree = (-pi / 2)
                # 6 - RIGHT
                pie.operator(
                    PIE_Transform_Rotate_Z.bl_idname, text='Z轴+90°').degree = (pi / 2)
                # 2 - BOTTOM
                pie.operator('mesh.sort_elements', text='顶点编号排序反转').type='REVERSE'
                # 8 - TOP
                rotate_Y = pie.operator('transform.rotate', text='Y',icon='EVENT_Y')
                rotate_Y.orient_type = get_orient
                rotate_Y.orient_axis = 'Y'
                pie.separator()
                # 7 - TOP - LEFT
                TR = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向前转')
                TR.x = True
                TR.y = False
                TR.degree = -pi / 2
                # 9 - TOP - RIGHT
                TL = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向后转')
                TL.x = True
                TL.y = False
                TL.degree = pi / 2
                # 1 - BOTTOM - LEFT
                TR = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向左转')
                TR.x = False
                TR.y = True
                TR.degree = pi / 2
                # 3 - BOTTOM - RIGHT
                TR = pie.operator(
                    PIE_Transform_Rotate_XY.bl_idname, text='向右转')
                TR.x = False
                TR.y = True
                TR.degree = -pi / 2

        elif context.area.ui_type == 'UV':

            set_pie_ridius(context, 100)
            # 4 - LEFT
            pie.operator(
                PIE_Transform_Rotate_Z.bl_idname, text='Z轴-90°', icon='TRIA_LEFT_BAR'
            ).degree = (-pi / 2)
            # 6 - RIGHT
            pie.operator(
                PIE_Transform_Rotate_Z.bl_idname, text='Z轴+90°', icon='TRIA_RIGHT_BAR'
            ).degree = (pi / 2)
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT

            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


class PIE_Transform_Rotate_Z(Operator):
    bl_idname = "pie.tramsform_rotate"
    bl_label = "Pie R 物体网格"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    
    degree: bpy.props.FloatProperty(name="Rotate_Dgree")

    @classmethod
    def rotation_ops():
        bpy.ops.transform.rotate(
            value=self.degree,
            orient_axis='Z',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1))
            )            
        
    def execute(self, context):
        is_pivot = context.scene.tool_settings.use_transform_pivot_point_align
        if is_pivot == True:
            is_pivot == False
            bpy.ops.transform.rotate(
            value=self.degree,
            orient_axis='Z',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1))
            )   
            is_pivot = True
        else:
            bpy.ops.transform.rotate(
            value=self.degree,
            orient_axis='Z',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1))
            )   
        return {"FINISHED"}


class PIE_Transform_Rotate_XY(Operator):
    bl_idname = "pie.uv_rotate_xy"
    bl_label = "旋转轴XY"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    x: bpy.props.BoolProperty(name='x', default=False)
    y: bpy.props.BoolProperty(name='y', default=False)
    degree: bpy.props.FloatProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        degree = self.degree
        use_x = self.x
        use_y = self.y
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                rotation = area.spaces.active.region_3d.view_rotation
                eul = Quaternion(rotation).to_euler()
                angle = math.degrees(eul.z)

        if -45 < angle < 45:
            if use_x:
                bpy.ops.transform.rotate(value=degree, orient_axis='X')
            elif use_y:
                bpy.ops.transform.rotate(value=degree, orient_axis='Y')
        elif 45 < angle < 135:
            if use_x:
                bpy.ops.transform.rotate(value=degree, orient_axis='Y')
            elif use_y:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis='X')
        elif 135 < angle < 180 or -180 < angle < -135:
            if use_x:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis='X')
            elif use_y:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis='Y')
        elif -135 < angle < -45:
            if use_x:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis='Y')
            elif use_y:
                bpy.ops.transform.rotate(value=degree, orient_axis='X')

        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_R,
    PIE_Transform_Rotate_Z,
    PIE_Transform_Rotate_XY,
]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    
    space_name = [
        ('3D View', 'VIEW_3D'),
        ('UV Editor', 'EMPTY'),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new(
            idname='wm.call_menu_pie', type="R", value="CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_R"
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
