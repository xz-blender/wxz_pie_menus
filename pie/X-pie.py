import bmesh
import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


def verties_lenth(context):
    lenth = 0
    for vertex in context.active_object.data.vertices:
        if vertex.select == True:
            lenth += 1
    return lenth


class VIEW3D_PIE_MT_Bottom_X(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        main_ap_fac = 1.2

        if ob_mode == "EDIT":
            if ob_type == "MESH":
                ed_mode = context.tool_settings.mesh_select_mode
                col = pie.split().box().column(align=True)

                row = col.row(align=True)
                row.scale_y = main_ap_fac
                if ed_mode[0] == True:
                    try:
                        row.operator("mesh.merge", text="首点", icon="DOT").type = "FIRST"
                        row.separator(factor=0.1)
                        row.operator("mesh.merge", text="中心").type = "CENTER"
                        row.separator(factor=0.1)
                        row.operator("mesh.merge", text="末点", icon="DOT").type = "LAST"
                    except TypeError:
                        row.operator("mesh.merge", text="中心").type = "CENTER"
                else:
                    sub = row.row()
                    # sub.alignment = 'CENTER'
                    sub.operator("mesh.merge", text="中心").type = "CENTER"

                col.separator(factor=0.4)
                row = col.row()
                row.operator("mesh.merge", text="游标").type = "CURSOR"
                op = row.operator("mesh.merge", text="塌陷")
                op.type = "COLLAPSE"
                col.separator(factor=0.4)
                row = col.row()
                row.scale_y = main_ap_fac
                row.operator("mesh.remove_doubles", text="按间距合并")
                # 6 - RIGHT
                col = pie.split().box().column(align=True)
                col.scale_x = 0.8

                row = col.row()
                row.operator("mesh.delete_loose")

                col.separator(factor=0.4)
                row = col.row()
                row.operator("mesh.decimate", text="精简几何体")
                row.operator("mesh.dissolve_degenerate", text="简并融并")
                row.operator("mesh.face_make_planar", text="平整表面")

                col.separator(factor=0.4)
                row = col.row()
                row.operator("mesh.vert_connect_nonplanar", text="拆分非平面")
                row.operator("mesh.vert_connect_concave", text="拆分凹面")
                row.operator("mesh.fill_holes", text="填充洞面")

                col.separator(factor=0.4)
                row = col.row()
                row.operator("mesh.dissolve_limited", text="有限融并")

                # 2 - BOTTOM
                pie.operator("mesh.edge_collapse", text="塌陷边面")
                # 8 - TOP
                box = pie.split().box()
                box.scale_x = 1.2
                box.scale_y = main_ap_fac
                col = box.column(align=True)
                row = col.row()
                row.operator("mesh.delete", text="仅面", icon="SNAP_FACE_CENTER").type = "ONLY_FACE"
                row = col.row()
                row.operator("mesh.delete", text="仅边", icon="MOD_EDGESPLIT").type = "EDGE_FACE"
                # 7 - TOP - LEFT
                col = pie.split()
                box = col.box().column(align=True)
                box.scale_x = 0.7
                box.scale_y = main_ap_fac
                row = box.row(align=True)
                id = PIE_Clean_Mesh_Edge_Atributes.bl_idname
                row.operator(id, text="清除", emboss=False).del_all = True
                row.operator(id, text="锐边").del_sharp = True
                row.operator(id, text="style").del_seam = True
                row.operator(id, text="权重").del_freestyle = True
                row.operator(id, text="折痕").del_crease = True
                row.operator(id, text="权重").del_weight = True

                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()

            if ob_type == "CURVE":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.operator("curve.decimate")
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
        elif ob_mode == "OBJECT":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator("object.move_to_collection")
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


class PIE_Clean_Mesh_Edge_Atributes(Operator):
    bl_idname = "pie.clean_mesh_edge_atributes"
    bl_label = "清除全部边线属性"
    bl_description = "清理网格全部边线属性"
    bl_options = {"REGISTER", "UNDO"}

    del_sharp: bpy.props.BoolProperty(default=False, name="清除锐边")  # type: ignore
    del_seam: bpy.props.BoolProperty(default=False, name="清除缝合边")  # type: ignore
    del_freestyle: bpy.props.BoolProperty(default=False, name="清除Freestyle")  # type: ignore
    del_crease: bpy.props.BoolProperty(default=False, name="清除点边折痕")  # type: ignore
    del_weight: bpy.props.BoolProperty(default=False, name="清除点边倒角权重")  # type: ignore
    del_all: bpy.props.BoolProperty(default=False, name="清除全部边线属性")  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout
        row = layout.row().box()
        row.prop(self, "del_all")
        row = layout.row().box().column(align=True)
        row.prop(self, "del_sharp")
        row.prop(self, "del_seam")
        row.prop(self, "del_freestyle")
        row.prop(self, "del_crease")
        row.prop(self, "del_weight")

    def remove_attributes(self, context, names: list):
        attr = context.active_object.data.attributes
        try:
            for name in names:
                attr.remove(attr.get(name))
        except:
            pass

    def execute(self, context):
        if self.del_all:
            self.del_sharp = True
            self.del_seam = True
            self.del_freestyle = True
            self.del_crease = True
            self.del_weight = True
        else:
            self.del_sharp = False
            self.del_seam = False
            self.del_freestyle = False
            self.del_crease = False
            self.del_weight = False

        obj = context.active_object
        if obj and obj.type == "MESH":
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            # 保存选择
            saved_vert_indices = {v.index for v in bm.verts if v.select}
            saved_edge_indices = {e.index for e in bm.edges if e.select}
            saved_face_indices = {f.index for f in bm.faces if f.select}

            bpy.ops.mesh.select_all(action="SELECT")
            if self.del_sharp:
                bpy.ops.mesh.mark_sharp(clear=True)
            if self.del_seam:
                bpy.ops.mesh.mark_seam(clear=True)
            if self.del_freestyle:
                bpy.ops.mesh.mark_freestyle_edge(clear=True)
            if self.del_weight:
                self.remove_attributes(context, ["bevel_weight_edge", "bevel_weight_vert"])
            if self.del_crease:
                self.remove_attributes(context, ["crease_edge", "crease_vert"])
            # 恢复选择
            for v in bm.verts:
                v.select = v.index in saved_vert_indices
            for e in bm.edges:
                e.select = e.index in saved_edge_indices
            for f in bm.faces:
                f.select = f.index in saved_face_indices

            bmesh.update_edit_mesh(me)
            saved_vert_indices.clear()
            saved_edge_indices.clear()
            saved_face_indices.clear()

            return {"FINISHED"}
        else:
            self.report({"ERROR"}, "激活物体不是网格!")
            return {"CANCELLED"}


CLASSES = [
    VIEW3D_PIE_MT_Bottom_X,
    PIE_Clean_Mesh_Edge_Atributes,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "X", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_X"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
