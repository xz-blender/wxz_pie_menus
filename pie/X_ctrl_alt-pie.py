import os

import bpy
import numpy as np
from bpy.types import Menu, Operator, Panel
from mathutils import Matrix, Vector

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_X_ctrl_shift(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "OBJECT":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            TR_op = pie.operator("object.origin_set", text="原点 -> 游标")
            TR_op.type = "ORIGIN_CURSOR"
            TR_op.center = "BOUNDS"
            # # 2 - BOTTOM
            pie.operator(PIE_Origin_TO_Bottom_No_Apply.bl_idname, text="原点 -> 底部(不应用)")
            # # 8 - TOP
            pie.operator(PIE_Origin_To_Selection_Object.bl_idname, text="原点 -> 选择")
            # # 7 - TOP - LEFT
            TL_op = pie.operator("object.origin_set", text="几何中心 -> 原点")
            TL_op.type = "GEOMETRY_ORIGIN"
            TL_op.center = "BOUNDS"
            # # 9 - TOP - RIGHT
            # pie.separator()
            TR_op = pie.operator("object.origin_set", text="原点 -> 几何中心")
            TR_op.type = "ORIGIN_GEOMETRY"
            TR_op.center = "BOUNDS"
            # # 1 - BOTTOM - LEFT
            col = pie.split().box().column(align=True)
            col.scale_y = 1.2
            row = col.row()
            L_op = row.operator("object.origin_set", text="原点 -> 质心(表面)")
            L_op.type = "ORIGIN_CENTER_OF_MASS"
            L_op.center = "MEDIAN"
            col.separator(factor=0.2)
            row = col.row()
            L_op = row.operator("object.origin_set", text="原点 -> 质心(体积)")
            L_op.type = "ORIGIN_CENTER_OF_VOLUME"
            L_op.center = "MEDIAN"
            # # 3 - BOTTOM - RIGHT
            pie.operator(PIE_Origin_TO_Bottom_Apply_Object.bl_idname, text="原点 -> 底部")

        elif ob_mode == "EDIT":
            # 4 - LEFT
            pie.operator("pie.orient_origin_to_selection", text="旋转原点 -> 选择")
            # 6 - RIGHT
            pie.operator(PIE_Origin_To_Cursor_Edit.bl_idname, text="原点 -> 游标")
            # 2 - BOTTOM
            pie.operator(PIE_Origin_TO_Bottom_No_Apply.bl_idname, text="原点 -> 底部(不应用)")
            # 8 - TOP
            pie.operator(PIE_Origin_To_Selection_Edit.bl_idname, text="原点 -> 选择")
            # 7 - TOP - LEFT
            pie.operator(PIE_Geometry_To_Origin_Edit.bl_idname, text="几何中心 -> 原点")
            # 9 - TOP - RIGHT
            pie.operator(PIE_Origin_To_Geometry_Edit.bl_idname, text="原点 -> 几何中心")
            # 1 - BOTTOM - LEFT
            col = pie.split().box().column(align=True)
            col.scale_y = 1.2
            row = col.row()
            L_op = row.operator(PIE_Origin_To_Mass_Edit.bl_idname, text="原点 -> 质心(表面)")
            L_op.mass_type = "ORIGIN_CENTER_OF_MASS"
            col.separator(factor=0.2)
            row = col.row()
            L_op = row.operator(PIE_Origin_To_Mass_Edit.bl_idname, text="原点 -> 质心(体积)")
            L_op.mass_type = "ORIGIN_CENTER_OF_VOLUME"
            # 3 - BOTTOM - RIGHT
            pie.operator(PIE_Origin_TO_Bottom_Apply_Edit.bl_idname, text="原点 -> 底部")


# --------Operator---------


def origin_to_bottom(ob, matrix=Matrix(), use_verts=False):
    me = ob.data
    mw = ob.matrix_world

    if use_verts:
        data = (v.co for v in me.vertices)
    else:
        data = (Vector(v) for v in ob.bound_box)

    coords = np.array([matrix @ v for v in data])
    z = coords.T[2]
    mins = np.take(coords, np.where(z == z.min())[0], axis=0)

    o = Vector(np.mean(mins, axis=0))
    o = matrix.inverted() @ o
    me.transform(Matrix.Translation(-o))

    mw.translation = mw @ o


# 原点到底部-不应用变换
class PIE_Origin_TO_Bottom_No_Apply(Operator):
    bl_idname = "pie.origin_to_no_apply"
    bl_label = __qualname__
    bl_descritpion = ""
    bl_options = {"REGISTER", "UNDO"}

    all_selected: bpy.props.BoolProperty(name="All selected", default=True)  # type: ignore
    global_transform: bpy.props.BoolProperty(name="Global Transform", default=False)  # type: ignore

    @classmethod
    def poll(self, context):
        if context.object:
            return True

    def execute(self, context):
        selected = context.selected_objects

        if self.all_selected == False:
            ob = context.object
            if self.global_transform == False:
                origin_to_bottom(ob)
            else:
                origin_to_bottom(ob, matrix=ob.matrix_world)

        elif self.all_selected == True:
            for ob in selected:
                if self.global_transform == False:
                    origin_to_bottom(ob)
                else:
                    origin_to_bottom(ob, matrix=ob.matrix_world)
        return {"FINISHED"}


def get_collection(name):
    if not [c.name for c in bpy.data.collections if bpy.context.scene.user_of_id(c) and name in c.name]:
        col = bpy.data.collections.new(name)
        # col = bpy.data.collections[name]
        bpy.context.scene.collection.children.link(col)
        return col.name
    return [c.name for c in bpy.data.collections if bpy.context.scene.user_of_id(c) and name in c.name][0]


def duplicate_object(obj, col=None):
    new_obj = None
    to_copy = bpy.data.objects[obj.name]
    if not col:
        col = bpy.context.view_layer.active_layer_collection.collection
    else:
        col = get_collection(col)
        col = bpy.data.collections[col]
    new_obj = to_copy.copy()
    if new_obj.data is not None:
        new_obj.data = to_copy.data.copy()
    new_obj.animation_data_clear()
    if col:
        col.objects.link(new_obj)
    return new_obj


def delete_object_with_data(obj):
    if obj and obj.name in bpy.data.objects:
        data = obj.data
        isMesh = obj.type == "MESH"
        bpy.data.objects.remove(obj, do_unlink=True)
        if isMesh:
            bpy.data.meshes.remove(data)


# 原点到底部-应用变换
class PIE_Origin_TO_Bottom_Apply_Object(Operator):
    bl_idname = "pie.origin_to_bottom_apply_object"
    bl_label = __qualname__
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        active = context.active_object
        for obj in context.selected_objects:
            dup = duplicate_object(obj)
            mw = dup.matrix_world.copy()
            dup.parent = None
            dup.matrix_world = mw
            # bbverts =
            lowest_pt = min([(dup.matrix_world @ Vector(corner)).z for corner in dup.bound_box])

            cursorLocBackUp = bpy.context.scene.cursor.location.copy()
            bpy.context.scene.cursor.location = (dup.location[0], dup.location[1], lowest_pt)
            delete_object_with_data(dup)
            override = context.copy()
            override.update(
                {
                    "selected_objects": [
                        obj,
                    ],
                    "acitve_object": obj,
                    "object": obj,
                    "selected_editable_objects": [
                        obj,
                    ],
                }
            )
            with bpy.context.temp_override(**override):
                bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
            bpy.context.scene.cursor.location = cursorLocBackUp
        return {"FINISHED"}


class PIE_Origin_TO_Bottom_Apply_Edit(Operator):
    bl_idname = "pie.origin_to_bottom_apply_edit"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")

        bpy.ops.pie.origin_to_bottom_apply_object()

        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


# 原点到选择-物体模式
class PIE_Origin_To_Selection_Object(Operator):
    bl_idname = "pie.origin_to_selection_object"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        saved_location = context.scene.cursor.location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        context.scene.cursor.location = saved_location

        return {"FINISHED"}


# 原点到选择-编辑模式
def CheckOrigin(context):
    try:
        cursorPositionX = context.scene.cursor.location[0]
        cursorPositionY = context.scene.cursor.location[1]
        cursorPositionZ = context.scene.cursor.location[2]
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set()
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
        bpy.ops.object.mode_set(mode="EDIT")
        context.scene.cursor.location[0] = cursorPositionX
        context.scene.cursor.location[1] = cursorPositionY
        context.scene.cursor.location[2] = cursorPositionZ
        return True
    except:
        return False


class PIE_Origin_To_Selection_Edit(Operator):
    bl_idname = "pie.origin_to_selection_edit"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D" and context.active_object is not None

    def execute(self, context):
        check = CheckOrigin(context)
        if not check:
            self.report({"ERROR"}, "Set Origin to Selected could not be performed")
            return {"CANCELLED"}

        return {"FINISHED"}


# 原点到游标-编辑模式
class PIE_Origin_To_Cursor_Edit(Operator):
    bl_idname = "pie.origin_to_cursor_edit"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


# 原点到质心-编辑模式
class PIE_Origin_To_Mass_Edit(Operator):
    bl_idname = "pie.origin_to_mass_edit"
    bl_label = __qualname__
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    mass_type: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type=self.mass_type, center="MEDIAN")
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


# 原点到几何中心-编辑模式
class PIE_Origin_To_Geometry_Edit(Operator):
    bl_idname = "pie.origin_to_geometry_edit"
    bl_label = __qualname__
    bl_description = "Origin To Geometry Edit"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


# 几何中心到原点-编辑模式
class PIE_Geometry_To_Origin_Edit(Operator):
    bl_idname = "pie.geometry_to_origin_edit"
    bl_label = __qualname__
    bl_description = "Geometry To Origin Edit"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="MEDIAN")
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


CLASSES = (
    VIEW3D_PIE_MT_Bottom_X_ctrl_shift,
    PIE_Origin_TO_Bottom_No_Apply,
    PIE_Origin_TO_Bottom_Apply_Object,
    PIE_Origin_TO_Bottom_Apply_Edit,
    PIE_Origin_To_Selection_Object,
    PIE_Origin_To_Selection_Edit,
    PIE_Origin_To_Cursor_Edit,
    PIE_Origin_To_Mass_Edit,
    PIE_Origin_To_Geometry_Edit,
    PIE_Geometry_To_Origin_Edit,
)


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        "Object Mode",
        "Mesh",
        "Curve",
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", "X", "CLICK_DRAG", ctrl=True, alt=True)
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_X_ctrl_shift"
        addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
