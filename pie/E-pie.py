import blf
import bmesh
import bpy
import numpy as np
from bpy.types import Context, Menu, Operator, Panel, PropertyGroup

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_E(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "EDIT" and ob_type == "MESH":
            # 4 - LEFT
            pie.operator("mesh.flip_normals")
            # 6 - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_y = 1.1
            col.operator("pie.mm_fuse")
            col.operator("pie.mm_change_width")
            col.operator("pie.mm_unchamfer")
            col.operator("pie.mm_turn_corner")
            col.operator("pie.mm_quad_corner")
            col.separator(factor=0.1)
            col.operator("pie.mm_unfuse")
            col.operator("pie.mm_refuse")
            col.operator("pie.mm_unbevel")
            col.separator(factor=0.1)
            col.operator("pie.mm_offset_cut")
            col.operator("pie.mm_unfuck")
            col.operator("pie.mm_boolean_cleanup")
            col.separator(factor=0.1)
            col.operator("pie.mm_symmetrize")
            # 2 - BOTTOM
            pie.operator("mesh.normals_make_consistent")
            # 8 - TOP
            col = pie.split().box().column(align=True)
            col.scale_y = 1.4
            col.operator("mesh.extrude_manifold", text="挤出流形")
            col.operator("pie.punchit", text="负向流形")
            # 7 - TOP - LEFT
            pie.operator("mesh.bridge_edge_loops", text="桥接循环边")
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            col = pie.split().box().column()
            add_operator(col, "mesh.set_edge_flow")
            add_operator(col, "mesh.set_edge_linear")
            # 3 - BOTTOM - RIGHT
            pie.separator()

        if ob_mode == "OBJECT" and ob_type == "MESH":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.operator("pie.ke_lineararray")
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("pie.ke_radial_instances")
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


class PIE_Shift_E_KEY(Operator):
    bl_idname = "pie.shift_e"
    bl_label = "设置折痕"
    bl_description = "在不同网格选择模式下设置不同的折痕"
    bl_options = {"REGISTER", "UNDO"}

    first_mouse_x: bpy.props.IntProperty()  # type: ignore
    set_value: bpy.props.FloatProperty(min=0, max=1)  # type: ignore
    attr_name: bpy.props.StringProperty()  # type: ignore

    ctrl_held: bool = False
    alt_held: bool = False

    attr_name_item = {
        "bevel_weight_edge": "边 - 倒角权重",
        "bevel_weight_vert": "顶点 - 倒角权重",
        "crease_vert": "顶点 - 折痕",
        "crease_edge": "边 - 折痕",
    }
    key_help_text = "ESC/右键: 退出 |  Shift: 吸附到0.1倍  |  Ctrl = 1  |  Alt = 0"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def get_suffix_name(self, context):
        mode = context.tool_settings.mesh_select_mode
        if mode[0]:
            return "_vert"
        elif mode[1] or mode[2]:
            return "_edge"

    def get_mode_name(self, context):
        mode = context.tool_settings.mesh_select_mode
        if mode[0]:
            return "POINT"
        elif mode[1] or mode[2]:
            return "EDGE"

    def get_mode_bmesh_layer(self, bm):
        mode = bpy.context.tool_settings.mesh_select_mode
        if mode[0]:
            return bm.verts.layers.float
        elif mode[1] or mode[2]:
            return bm.edges.layers.float

    def get_selected_elements(self, bm):
        mode = bpy.context.tool_settings.mesh_select_mode
        if mode[0]:
            return [v for v in bm.verts if v.select]
        elif mode[1] or mode[2]:
            return [e for e in bm.edges if e.select]

    def get_or_create_bmesh_layer(self, bm, attr_name):
        layer_collection = self.get_mode_bmesh_layer(bm)
        # 获取或创建 BMesh 层
        if attr_name not in layer_collection.keys():
            layer = layer_collection.new(attr_name)
        else:
            layer = layer_collection.get(attr_name)
        return layer

    def update_bmesh(self, obj):
        bmesh.update_edit_mesh(obj.data)

    def set_bmesh_layer_value(self, value):
        self.set_value = value
        attr_name = self.attr_name + self.get_suffix_name(bpy.context)
        layer = self.get_or_create_bmesh_layer(self.bm, attr_name)
        elements = self.get_selected_elements(self.bm)
        for elem in elements:
            elem[layer] = self.set_value
        self.update_bmesh(bpy.context.active_object)
        # self.update_screen_display(bpy.context)

    # def update_screen_display(self, context):
    #     context.area.tag_redraw()

    def modal(self, context, event):
        # 处理 Ctrl 键事件
        if event.type in {"LEFT_CTRL", "RIGHT_CTRL"}:
            if event.value == "PRESS":
                self.ctrl_held = True
                # 设置值为 1.0
                self.set_bmesh_layer_value(1.0)
                # 更新状态栏提示
                self.set_status_text(context)
            elif event.value == "RELEASE":
                self.ctrl_held = False
                # 更新状态栏提示
                self.set_status_text(context)

        # 处理 Alt 键事件
        elif event.type in {"LEFT_ALT", "RIGHT_ALT"}:
            if event.value == "PRESS":
                self.alt_held = True
                # 设置值为 0.0
                self.set_bmesh_layer_value(0.0)
                # 更新状态栏提示
                self.set_status_text(context)
            elif event.value == "RELEASE":
                self.alt_held = False
                # 更新状态栏提示
                self.set_status_text(context)

        elif event.type == "MOUSEMOVE":
            # 如果按下了 Ctrl 或 Alt 键，鼠标移动不调整值
            if self.ctrl_held or self.alt_held:
                pass  # 不做任何操作
            else:
                delta = event.mouse_x - self.first_mouse_x
                if event.shift:
                    # 未按下 Shift 键，值以 0.1 为步长调整
                    self.set_value = max(0.0, min(1.0, delta * 0.005))
                else:
                    # Shift 键按下，值平滑调整
                    self.set_value = max(0.0, min(1.0, round(delta * 0.005 / 0.1) * 0.1))
                # 更新 BMesh 层值
                self.set_bmesh_layer_value(self.set_value)

        elif event.type == "LEFTMOUSE" and event.value == "PRESS":
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            self.finish(context)
            # 清除状态栏提示
            context.workspace.status_text_set("")
            return {"FINISHED"}

        elif event.type == "MIDDLEMOUSE":
            return {"PASS_THROUGH"}

        elif event.type in {"RIGHTMOUSE", "ESC"}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            self.cancel(context)
            # 清除状态栏提示
            context.workspace.status_text_set("")
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_x = event.mouse_x

            obj = context.active_object
            me = obj.data
            self.bm = bmesh.from_edit_mesh(me)

            context.window_manager.modal_handler_add(self)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback, (context,), "WINDOW", "POST_PIXEL"
            )
            self.set_status_text(context)
            # context.area.header_text_set(self.key_help_text)
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

    def finish(self, context):
        # 释放 BMesh
        del self.bm
        context.workspace.status_text_set("")

    def cancel(self, context):
        # 释放 BMesh
        del self.bm
        context.workspace.status_text_set("")

    def set_status_text(self, context):
        status_text = "左键确认  |  右键/ESC取消"
        ctrl_t = "按住Ctrl为 1"
        shift_t = "按住Shift以0.1倍调整"
        alt_t = "按住Alt为 0"

        def join_t(list):
            return "  |  ".join(list)

        if self.ctrl_held:
            status_text = join_t([status_text, ctrl_t])
        elif self.alt_held:
            status_text = join_t([status_text, alt_t])
        else:
            status_text = join_t([status_text, shift_t, ctrl_t, alt_t])

        context.workspace.status_text_set(status_text)

    def draw_callback(self, context):
        region = context.region
        mid_x = region.width / 2 - 200
        mid_y = region.height * 0.1

        font_id = 0
        blf.position(font_id, mid_x, mid_y, 0)
        blf.size(font_id, 50)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
        text = f"{self.attr_name_item[self.attr_name+self.get_suffix_name(context)]} : {self.set_value:.2f}"
        blf.draw(font_id, text)


CLASSES = [
    VIEW3D_PIE_MT_Bottom_E,
    PIE_Shift_E_KEY,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "E", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_E"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", shift=True)
    kmi.properties.attr_name = "crease"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", ctrl=True, shift=True)
    kmi.properties.attr_name = "bevel_weight"
    addon_keymaps.append(km)


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
