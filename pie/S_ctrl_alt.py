import bpy
import bmesh
import math
from math import radians
from math import pi
from bpy.props import IntProperty, FloatProperty
from bpy.types import Menu, Operator
from mathutils import Quaternion
from mathutils import Matrix
from mathutils import Vector
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

class Mesh_UVScaleModalOperator(Operator):
    """通过鼠标左右移动来调整UV缩放的大小"""
    bl_idname = "pie.uv_modal_scale_operator"
    bl_label = "调整 UV 缩放"

    initial_mouse_x: IntProperty()
    scale_factor: FloatProperty(default=1.0, min=0.0, max=2.0)
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = self.initial_mouse_x - event.mouse_x
            self.scale_factor = max(0.0, min(2.0, self.scale_factor - delta * 0.0002))
            self.scale_uv(context, self.scale_factor)
            self.initial_mouse_x = event.mouse_x
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.object:
            self.initial_mouse_x = event.mouse_x
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "没有激活的对象")
            return {'CANCELLED'}
    
    def scale_uv(self, context, scale_factor):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        # 计算选中UV的中心点
        uv_center = [0, 0]
        selected_uv_count = 0
        for face in bm.faces:
            if face.select:  # 检查面是否被选中
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv_center[0] += uv[0]
                    uv_center[1] += uv[1]
                    selected_uv_count += 1
                    
        if selected_uv_count == 0:  # 如果没有选中的UV，直接返回
            return
        
        uv_center[0] /= selected_uv_count
        uv_center[1] /= selected_uv_count

        # 使用计算出的UV中心进行缩放
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop_uv = loop[uv_layer]
                    loop_uv.uv = ((loop_uv.uv[0] - uv_center[0]) * scale_factor + uv_center[0], 
                                (loop_uv.uv[1] - uv_center[1]) * scale_factor + uv_center[1])
        
        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)


def uv_menu_func(self, context):
    self.layout.operator(Mesh_UVScaleModalOperator.bl_idname)

classes = [
    Mesh_UVScaleModalOperator,
]
addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    
    km = addon.keymaps.new(name='Mesh')
    kmi = km.keymap_items.new(
    idname='pie.uv_modal_scale_operator', type="S", value="CLICK",ctrl = True,alt = True)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    bpy.types.VIEW3D_MT_uv_map.append(uv_menu_func)
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()

def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_uv_map.remove(uv_menu_func)