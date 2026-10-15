from ..module.keymaps import owned_keymaps
from ..module.reg import register_classes, unregister_classes
import bpy
from bpy.types import Menu, Operator

from ..utils import extend_keymaps_list
from .utils import *


class VIEW3D_PIE_MT_Bottom_F(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "OBJECT":
            # 4 - LEFT
            op = pie.operator(PIE_Make_Sigle_User.bl_idname, text="单一化", icon="UNLINKED")
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator(Merge_Objects_WithoutActive.bl_idname, text="合并", icon="SELECT_EXTEND")
            # 8 - TOP
            add_operator(pie, "object.parent_to_empty")
            # 7 - TOP - LEFT
            if ob_type == "ARMATURE":
                pie.operator("armature.parent_clear")
            else:
                pie.operator("object.parent_clear").type = "CLEAR_KEEP_TRANSFORM"
            # 9 - TOP - RIGHT
            if ob_type == "ARMATURE":
                pie.operator("armature.parent_set")
            else:
                op = pie.operator("object.parent_set")
                op.type = "OBJECT"
                op.keep_transform = True
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.operator(Clean_Custom_Normal.bl_idname, text="批量删自定法线", icon="NORMALS_VERTEX_FACE")

        if ob_mode == "EDIT":
            if ob_type == "MESH":
                # 4 - LEFT
                pie.operator("mesh.inset", text="内插面")
                # 6 - RIGHT
                add_operator(pie, "mesh.offset_edges", text="偏移边线")
                # 2 - BOTTOM
                pie.operator("mesh.subdivide", text="细分")
                # 8 - TOP
                pie.operator("mesh.separate", text="分离选中").type = "SELECTED"
                # 7 - TOP - LEFT
                pie.operator("mesh.split", text="拆分")
                # 9 - TOP - RIGHT
                add_operator(pie, "mesh.edgetools_extend", text="延伸边")
                # 1 - BOTTOM - LEFT
                pie.operator("wm.tool_set_by_id", text="切刀工具").name = "builtin.knife"
                # 3 - BOTTOM - RIGHT
                add_operator(pie, "object.mesh_edge_length_set", text="设边长")
            if ob_type == "CURVE":
                # 4 - LEFT
                pie.operator("curve.smooth", text="光滑")
                # 6 - RIGHT
                pie.operator("curvetools.add_toolpath_offset_curve", text="曲线偏移")
                # 2 - BOTTOM
                pie.operator("curve.subdivide", text="细分")
                # 8 - TOP
                pie.operator("curve.separate", text="分离")
                # 7 - TOP - LEFT
                pie.operator("curve.switch_direction", text="切换方向")
                # 9 - TOP - RIGHT

                # 1 - BOTTOM - LEFT

                # 3 - BOTTOM - RIGHT


class Clean_Custom_Normal(Operator):
    bl_idname = "pie.clear_custom_normal"
    bl_label = "Clear Custom Data"
    bl_description = "Clear Custom Data"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.object is not None and context.object.type == "MESH":
            return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        for o in selection:
            bpy.context.view_layer.objects.active = o
            try:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            except:
                None
        return {"FINISHED"}


class PIE_Make_Sigle_User(Operator):
    bl_idname = "pie.make_sigle_user"
    bl_label = "Make_Sigle_User"
    bl_description = "Make_Sigle_User Only for selected"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.make_single_user(object=True, obdata=True)
        return {"FINISHED"}


class Merge_Objects_WithoutActive(Operator):
    bl_idname = "pie.merge_objects_without_active"
    bl_label = "Merge Objects"
    bl_description = "Merge Objects Without Active Objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.object is not None:
            if context.object.type in ["MESH", "CURVE", "SURFACE", "GPENCIL", "ARMATURE"]:
                return True

    def execute(self, context):
        selection_ob = context.selected_objects
        active_ob = context.active_object
        if active_ob in selection_ob:
            bpy.ops.object.join()
        else:
            context.view_layer.objects.active = selection_ob[0]
            bpy.ops.object.join()
        return {"FINISHED"}


F_GESTURE_IDNAME = "pie.mesh_f_gesture"
_ACTIVE_F_GESTURES = set()


def cancel_f_gestures():
    for operator in tuple(_ACTIVE_F_GESTURES):
        operator._cancelled = True
    _ACTIVE_F_GESTURES.clear()


def _event_modifiers_match(kmi, event):
    return kmi.any or all(
        getattr(kmi, name) in {-1, int(getattr(event, name))} for name in ("shift", "ctrl", "alt", "oskey")
    )


def _has_custom_press(context, event):
    """Yield to explicit user/F2 bindings instead of silently replacing them."""
    configs = context.window_manager.keyconfigs
    for config in (configs.user, configs.addon):
        if config is None:
            continue
        km = config.keymaps.get("Mesh")
        if km is None:
            continue
        for kmi in km.keymap_items:
            if (
                not kmi.active
                or kmi.idname == F_GESTURE_IDNAME
                or kmi.type != event.type
                or kmi.value not in {"PRESS", "ANY"}
                or kmi.key_modifier != "NONE"
                or not _event_modifiers_match(kmi, event)
            ):
                continue
            if config == configs.addon or kmi.is_user_modified or kmi.is_user_defined:
                return True
    return False


class PieMeshFGesture(Operator):
    bl_idname = F_GESTURE_IDNAME
    bl_label = "XZ F: Click Make Edge/Face, Drag Pie"
    bl_description = "Release without dragging: Make Edge/Face. Move while held: F pie. No hold timer"
    # The delegated mesh operation owns its undo entry; the dispatcher changes no data.
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        return (
            context.area is not None
            and context.area.type == "VIEW_3D"
            and context.region is not None
            and context.region.type == "WINDOW"
            and context.mode == "EDIT_MESH"
        )

    def _finish(self, result):
        _ACTIVE_F_GESTURES.discard(self)
        return result

    def invoke(self, context, event):
        if _has_custom_press(context, event):
            return {"PASS_THROUGH"}
        if event.value == "CLICK_DRAG":
            bpy.ops.wm.call_menu_pie("INVOKE_DEFAULT", name="VIEW3D_PIE_MT_Bottom_F")
            return {"FINISHED"}
        if event.value in {"CLICK", "RELEASE"}:
            return bpy.ops.mesh.edge_face_add("EXEC_DEFAULT", True)
        if event.value != "PRESS" or event.is_repeat:
            return {"CANCELLED"}
        self._key = event.type
        self._origin = (event.mouse_x, event.mouse_y)
        self._modifiers = tuple(getattr(event, name) for name in ("shift", "ctrl", "alt", "oskey"))
        self._window = context.window.as_pointer()
        self._area = context.area.as_pointer()
        self._cancelled = False
        inputs = context.preferences.inputs
        self._threshold = max(1, getattr(inputs, "drag_threshold_keyboard", inputs.drag_threshold))
        _ACTIVE_F_GESTURES.add(self)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if (
            self._cancelled
            or event.type in {"ESC", "WINDOW_DEACTIVATE"}
            or context.window is None
            or context.window.as_pointer() != self._window
            or context.area is None
            or context.area.as_pointer() != self._area
            or context.mode != "EDIT_MESH"
        ):
            return self._finish({"CANCELLED"})
        modifiers = tuple(getattr(event, name) for name in ("shift", "ctrl", "alt", "oskey"))
        if modifiers != self._modifiers:
            return self._finish({"CANCELLED", "PASS_THROUGH"})
        if event.type == self._key:
            if event.value == "RELEASE":
                self._finish({"FINISHED"})
                return bpy.ops.mesh.edge_face_add("EXEC_DEFAULT", True)
            return {"RUNNING_MODAL"}  # OS repeat must not fill or launch a second modal.
        if event.type in {"MOUSEMOVE", "INBETWEEN_MOUSEMOVE"}:
            dx, dy = event.mouse_x - self._origin[0], event.mouse_y - self._origin[1]
            if max(abs(dx), abs(dy)) >= self._threshold:
                self._finish({"FINISHED"})
                bpy.ops.wm.call_menu_pie("INVOKE_DEFAULT", name="VIEW3D_PIE_MT_Bottom_F")
                return {"FINISHED"}
            return {"RUNNING_MODAL"}
        if event.type in {"TIMER", "TIMER_REPORT", "TIMERREGION"}:
            return {"RUNNING_MODAL", "PASS_THROUGH"}
        # Do not swallow an unrelated shortcut (including the physical F2 key).
        return self._finish({"CANCELLED", "PASS_THROUGH"})

    def cancel(self, context):
        self._finish({"CANCELLED"})


CLASSES = [
    PieMeshFGesture,
    VIEW3D_PIE_MT_Bottom_F,
    Clean_Custom_Normal,
    Merge_Objects_WithoutActive,
    PIE_Make_Sigle_User,
]

addon_keymaps = []


@owned_keymaps
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        "Object Mode",
        "Curve",
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", "F", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_F"
        addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new(F_GESTURE_IDNAME, "F", "PRESS", repeat=False)
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")  # ,space_type ='VIEW_3D')
    kmi = km.keymap_items.new("mesh.vert_connect_path", "F", "CLICK", shift=True)
    addon_keymaps.append((km, kmi))


@register_classes(CLASSES)
def register():
    register_keymaps()


@unregister_classes(CLASSES)
def unregister():
    cancel_f_gestures()
    keymap_safe_unregister(addon_keymaps)
