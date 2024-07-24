import importlib

import bpy
from bpy.props import CollectionProperty, EnumProperty, PointerProperty, StringProperty


class PIE_HistoryObjectsCollection(bpy.types.PropertyGroup):
    name: StringProperty()  # type: ignore
    obj: PointerProperty(name="History Object", type=bpy.types.Object)  # type: ignore


class PIE_HistoryUnmirroredCollection(bpy.types.PropertyGroup):
    name: StringProperty()  # type: ignore
    obj: PointerProperty(name="History Unmirror", type=bpy.types.Object)  # type: ignore


class PIE_HistoryEpochCollection(bpy.types.PropertyGroup):
    name: StringProperty()  # type: ignore
    objects: CollectionProperty(type=PIE_HistoryObjectsCollection)  # type: ignore
    unmirrored: CollectionProperty(type=PIE_HistoryUnmirroredCollection)  # type: ignore


class M4_split_SceneProperties(bpy.types.PropertyGroup):
    align_mode: EnumProperty(
        name="Align Mode", items=[("VIEW", "View", ""), ("AXES", "Axes", "")], default="VIEW"
    )  # type: ignore
    focus_history: CollectionProperty(type=PIE_HistoryEpochCollection)  # type: ignore


classes = [
    PIE_HistoryObjectsCollection,
    PIE_HistoryUnmirroredCollection,
    PIE_HistoryEpochCollection,
    M4_split_SceneProperties,
]

class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def register():
    class_register()
    if "bpy" in locals():
        importlib.reload(M4_split_SceneProperties)

    bpy.types.Scene.M4_split = bpy.props.PointerProperty(type=M4_split_SceneProperties)


def unregister():
    class_unregister()
    del bpy.types.Scene.M4_split
