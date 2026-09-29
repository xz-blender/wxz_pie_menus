"""Blender preferences and presentation for the feature lifecycle.

This leaf module deliberately avoids importing the add-on entrypoint, props or
utils. The same RNA declarations are used by production and focused Blender tests.
"""

import sys
import traceback
from inspect import get_annotations

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import Operator, PropertyGroup

from .lifecycle import ModuleState

COLLECTION_NAMES = ("pie_modules", "other_modules", "setting_modules")
_lifecycle = None


class PIE_ModuleItem(PropertyGroup):
    name: StringProperty()  # type: ignore


def module_collection_properties():
    """Fresh declarations; callers merge them with their other annotations."""
    properties = {}
    for name in COLLECTION_NAMES:
        properties[name] = CollectionProperty(type=PIE_ModuleItem)
        properties[name + "_index"] = IntProperty()
    return properties


def bind_lifecycle(lifecycle):
    global _lifecycle
    _lifecycle = lifecycle


def bind_module_toggles(preferences_type, modules):
    def update_for(name):
        def update(preferences, context):
            if _lifecycle is not None:
                _lifecycle.set_enabled(name, getattr(preferences, "use_" + name))

        return update

    annotations = get_annotations(preferences_type)
    for module in modules:
        name = module.__name__.rsplit(".", 1)[-1]
        annotations["use_" + name] = BoolProperty(name=name, default=True, update=update_for(name))
    preferences_type.__annotations__ = annotations


class BlenderLifecycleHost:
    def __init__(self, addon_id, preferences_type):
        self.addon_id = addon_id
        self._preferences_type = preferences_type

    def preferences(self):
        addon = bpy.context.preferences.addons.get(self.addon_id)
        return addon.preferences if addon is not None else None

    def desired(self, name):
        preferences = self.preferences()
        return True if preferences is None else getattr(preferences, "use_" + name)

    def set_desired(self, name, desired):
        preferences = self.preferences()
        if preferences is not None and getattr(preferences, "use_" + name) != desired:
            setattr(preferences, "use_" + name, desired)

    def after_disable(self, name):
        # Preserve the old, optional named preference cleanup. Ordinary toggles
        # have no named PointerProperty and never rebuild the preferences class.
        preferences_type = self._preferences_type()
        if hasattr(preferences_type, name):
            delattr(preferences_type, name)
            if self.preferences() is not None:
                bpy.utils.unregister_class(preferences_type)
                bpy.utils.register_class(preferences_type)
                preferences = self.preferences()
                if name in preferences:
                    del preferences[name]

    def rebuild_collections(self, groups):
        preferences = self.preferences()
        if preferences is None:
            return
        for collection_name, modules in groups.items():
            collection = getattr(preferences, collection_name)
            collection.clear()
            for module in modules:
                collection.add().name = module.__name__.rsplit(".", 1)[-1]

    def report_error(self, name, stage, error):
        print(f"[{self.addon_id}] {name}: {stage} failed", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


_STATE_LABELS = {
    ModuleState.DISABLED: "未启用",
    ModuleState.ACTIVE: "已启用",
    ModuleState.ENABLE_FAILED: "启用失败",
    ModuleState.CLEANUP_FAILED: "清理失败",
}


def draw_module_item(layout, preferences, item):
    name = item.name
    row = layout.row()
    row.label(text=name)
    row.prop(preferences, "use_" + name, text="")
    if _lifecycle is None:
        return
    status = _lifecycle.status(name)
    if status.errors:
        row.label(text=_STATE_LABELS[status.state], icon="ERROR")
        summary = " / ".join(error.message for error in status.errors).replace("\n", " ")
        row.label(text=summary[:60])
        row.operator(PIE_Retry_Module.bl_idname, text="重试", icon="FILE_REFRESH").module_name = name
    else:
        row.label(text=_STATE_LABELS[status.state])


class PIE_Retry_Module(Operator):
    bl_idname = "pie.retry_module"
    bl_label = "重试模块启停"
    bl_description = "先重试未完成的清理，再按当前开关尝试启用"
    bl_options = {"INTERNAL"}

    module_name: StringProperty(options={"HIDDEN", "SKIP_SAVE"})  # type: ignore

    @classmethod
    def poll(cls, context):
        return _lifecycle is not None

    @classmethod
    def description(cls, context, properties):
        if _lifecycle is not None and properties.module_name:
            try:
                status = _lifecycle.status(properties.module_name)
            except KeyError:
                pass
            else:
                details = "\n".join(f"{error.stage}: {error.message}" for error in status.errors)
                if details:
                    return cls.bl_description + "\n" + details
        return cls.bl_description

    def execute(self, context):
        try:
            status = _lifecycle.retry(self.module_name)
        except KeyError:
            self.report({"ERROR"}, f"找不到模块: {self.module_name}")
            return {"CANCELLED"}
        if status.errors:
            self.report({"ERROR"}, " / ".join(error.message for error in status.errors))
            return {"CANCELLED"}
        self.report({"INFO"}, f"{self.module_name}: {_STATE_LABELS[status.state]}")
        return {"FINISHED"}
