# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.props import FloatProperty, StringProperty

from . import hud
from .mesh_data import WeightEdit
from .preferences import get_preferences

ACTIVE = []
MODIFIER_KEYS = {
    "LEFT_CTRL": "ctrl", "RIGHT_CTRL": "ctrl",
    "LEFT_ALT": "alt", "RIGHT_ALT": "alt",
    "LEFT_SHIFT": "shift", "RIGHT_SHIFT": "shift",
}


class WeightOperator:
    @classmethod
    def poll(cls, context):
        return (context.mode == "EDIT_MESH" and context.active_object is not None
                and context.area is not None and context.area.type == "VIEW_3D")

    def execute(self, context):
        edit = None
        try:
            edit = WeightEdit(context, self.attribute_kind)
            edit.apply(self.value)
        except (ValueError, RuntimeError, ReferenceError) as error:
            if edit is not None:
                edit.restore()
            self.report({"WARNING"}, str(error))
            return {"CANCELLED"}
        return {"FINISHED"}

    def invoke(self, context, event):
        if context.region is None or context.region.type != "WINDOW":
            self.report({"WARNING"}, "请在 3D 视口内调用")
            return {"CANCELLED"}
        if ACTIVE:
            return {"CANCELLED"}
        try:
            self._edit = WeightEdit(context, self.attribute_kind)
        except ValueError as error:
            self.report({"WARNING"}, str(error))
            return {"CANCELLED"}
        self.value = self._edit.initial_value
        self._area, self._region, self._workspace = context.area, context.region, context.workspace
        self._mouse_region = (event.mouse_region_x, event.mouse_region_y)
        self._origin_x = event.mouse_x
        self._origin_value = self.value
        # The modifiers used to invoke the tool are not adjustment commands.
        self._blocked_modifiers = {key for key in ("shift", "ctrl", "alt") if getattr(event, key)}
        self._navigating = False
        self._closed = False
        self._handle = None
        self._hud = None
        prefs = get_preferences(context)
        self._sensitivity = prefs.sensitivity if prefs else 0.005
        try:
            self._handle = bpy.types.SpaceView3D.draw_handler_add(hud.draw, (self,), "WINDOW", "POST_PIXEL")
            context.window_manager.modal_handler_add(self)
            ACTIVE.append(self)
            self._workspace.status_text_set(
                f"{self.display_name} | 左键/Enter 确认 | 右键/Esc 还原 | Shift 吸附 0.1 | Ctrl=1 | Alt=0"
            )
            self._area.tag_redraw()
        except Exception:
            self._cleanup()
            raise
        return {"RUNNING_MODAL"}

    def _cleanup(self):
        if getattr(self, "_closed", True):
            return
        self._closed = True
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            self._handle = None
        self._hud = None
        self._edit = None
        try:
            self._workspace.status_text_set(None)
            self._area.tag_redraw()
        except ReferenceError:
            pass
        if self in ACTIVE:
            ACTIVE.remove(self)

    def cancel(self, context):
        if getattr(self, "_closed", True):
            return
        try:
            self._edit.restore()
        finally:
            self._cleanup()

    def _rebase(self, event):
        self._origin_x = event.mouse_x
        self._origin_value = self.value

    def _set_value(self, value):
        self.value = max(0.0, min(1.0, value))
        if self._edit.apply(self.value):
            self._area.tag_redraw()
            return True
        return False

    def modal(self, context, event):
        if self._closed:
            return {"CANCELLED"}
        if context.mode != "EDIT_MESH" or not self._edit.valid() or context.area != self._area:
            self.cancel(context)
            return {"CANCELLED"}
        try:
            return self._modal(context, event)
        except (RuntimeError, ReferenceError, ValueError) as error:
            self.cancel(context)
            self.report({"WARNING"}, str(error))
            return {"CANCELLED"}

    def _modal(self, context, event):
        mouse = (event.mouse_region_x, event.mouse_region_y)
        moved = mouse != getattr(self, "_mouse_region", None)
        self._mouse_region = mouse
        if event.type in {"RIGHTMOUSE", "ESC"} and event.value == "PRESS":
            self.cancel(context)
            return {"CANCELLED"}
        if event.type in {"LEFTMOUSE", "RET", "NUMPAD_ENTER"} and event.value == "PRESS":
            self._cleanup()
            return {"FINISHED"}
        if event.type == "MIDDLEMOUSE":
            self._navigating = event.value == "PRESS"
            self._rebase(event)
            return {"PASS_THROUGH"}
        if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE", "TRACKPADPAN", "TRACKPADZOOM"}:
            self._rebase(event)
            return {"PASS_THROUGH"}
        if self._navigating:
            self._rebase(event)
            return {"PASS_THROUGH"}
        modifier = MODIFIER_KEYS.get(event.type)
        if modifier:
            if event.value == "RELEASE":
                self._blocked_modifiers.discard(modifier)
                self._rebase(event)
            elif event.value == "PRESS" and modifier not in self._blocked_modifiers:
                if modifier == "ctrl":
                    self._set_value(1.0)
                elif modifier == "alt":
                    self._set_value(0.0)
                self._rebase(event)
            return {"RUNNING_MODAL"}
        if event.type == "MOUSEMOVE":
            updated = False
            ctrl = event.ctrl and "ctrl" not in self._blocked_modifiers
            alt = event.alt and "alt" not in self._blocked_modifiers
            if not (ctrl or alt):
                value = self._origin_value + (event.mouse_x - self._origin_x) * self._sensitivity
                if event.shift and "shift" not in self._blocked_modifiers:
                    value = round(value * 10) / 10
                value = max(0.0, min(1.0, value))
                # A stationary/vertical mouse event must not flatten mixed values.
                if value != self.value:
                    updated = self._set_value(value)
            if moved and not updated:
                prefs = get_preferences(context)
                if prefs and prefs.show_hud and prefs.hud_anchor == "CURSOR":
                    self._area.tag_redraw()
        return {"RUNNING_MODAL"}


class PIE_Shift_E_KEY(WeightOperator, bpy.types.Operator):
    """Keep the host operator and RNA properties used by existing keymaps."""

    bl_idname = "pie.shift_e"
    bl_label = "快速折痕 / 倒角权重"
    bl_description = "按网格选择模式调整顶点或边的折痕、倒角权重"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}
    attr_name: StringProperty(name="属性", default="crease", options={"HIDDEN"})
    set_value: FloatProperty(name="权重", default=0.0, min=0.0, max=1.0)

    @property
    def attribute_kind(self):
        return self.attr_name

    @property
    def display_name(self):
        return "倒角权重" if self.attr_name == "bevel_weight" else "折痕"

    @property
    def value(self):
        return self.set_value

    @value.setter
    def value(self, value):
        self.set_value = value


CLASSES = (PIE_Shift_E_KEY,)


def cancel_active():
    for operator in tuple(ACTIVE):
        operator.cancel(bpy.context)
