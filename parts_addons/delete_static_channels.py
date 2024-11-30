import math

import bpy
from bpy.types import Operator

from ..pie.utils import keymap_safe_unregister


def refresh():
    # Updates all animation related UI
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "UI":
                    region.tag_redraw()
        elif area.type == "DOPESHEET_EDITOR":
            for region in area.regions:
                if region.type == "WINDOW":
                    region.tag_redraw()
                if region.type == "CHANNELS":
                    region.tag_redraw()
        elif area.type == "GRAPH_EDITOR":
            for region in area.regions:
                if region.type == "WINDOW":
                    region.tag_redraw()
                if region.type == "CHANNELS":
                    region.tag_redraw()
        elif area.type == "NLA_EDITOR":
            for region in area.regions:
                if region.type == "WINDOW":
                    region.tag_redraw()
                if region.type == "CHANNELS":
                    region.tag_redraw()
        elif area.type == "OUTLINER":
            for region in area.regions:
                if region.type == "WINDOW":
                    region.tag_redraw()
        elif area.type == "PROPERTIES":
            for region in area.regions:
                if region.type == "WINDOW":
                    region.tag_redraw()


def max_diff(a):
    maximum = max(a)
    minimum = min(a)
    return maximum - minimum


class GRAPH_OT_Delete_Static_Channels(Operator):
    """根据每个F曲线的关键帧数和""" """其关键帧值之间的差异"""

    bl_idname = "graph.delete_static_channels"
    bl_label = "删除未使用通道"
    bl_options = {"REGISTER", "UNDO"}

    filters: bpy.props.EnumProperty(
        name="通道过滤器",
        description="过滤哪些通道可以被删除.",
        default="ALL",
        items=[
            ("ALL", "All", "删除场景的所有静态通道."),
            ("SEL_OBJS", "选择的 物体/骨骼", "仅删除选定对象或姿势骨骼的静态通道."),
            ("SEL_FCURVE", "选择的 F-Curves", "仅删除选定的 F-Curves 的静态通道."),
            ("VIS_FCURVE", "可见的 F-Curves", "仅删除可见的 F-Curves 的静态通道."),
        ],
    )  # type: ignore

    keep_modifiers: bpy.props.BoolProperty(
        name="保留修改器通道", description="保存带有F曲线修改器的通道，使其不被删除", default=True
    )  # type: ignore

    min_key_count: bpy.props.IntProperty(
        name="最小. 帧计数", description="避免删除所需的最小关键帧数", default=2, soft_min=0, soft_max=20
    )  # type: ignore

    min_difference: bpy.props.FloatProperty(
        name="最小. 差别", description="F曲线关键帧值的最小差值", default=0.001, soft_min=0.0001, soft_max=10
    )  # type: ignore

    def delete_selected_channels(self, action, fcurve):
        rotations = ["rotation_euler", "rotation_quaternion", "delta_rotation_euler", "delta_rotation_quaternion"]

        if len(fcurve.keyframe_points) < self.min_key_count:
            if len(fcurve.modifiers.items()) == 0:
                action.fcurves.remove(fcurve)
            elif self.keep_modifiers == False:
                action.fcurves.remove(fcurve)
        else:
            values = list()
            for k in fcurve.keyframe_points:
                if fcurve.data_path in rotations:
                    values.append(math.degrees(k.co[1]))
                else:
                    values.append(k.co[1])
            if max_diff(values) < self.min_difference:
                action.fcurves.remove(fcurve)

    def execute(self, context):
        vis_curves = None

        if self.filters == "VIS_FCURVE":
            vis_curves = bpy.context.visible_fcurves[:]

        current_mode = bpy.context.object.mode
        if current_mode == "POSE" and self.filters == "SEL_OBJS":
            action = bpy.context.active_object.animation_data.action
            sel_bone_names = list()

            for pb in bpy.context.selected_pose_bones:
                sel_bone_names.append(pb.bone.name)

            for fcurve in action.fcurves:
                tmp = fcurve.data_path.split("[", maxsplit=1)[1].split("]", maxsplit=1)
                bone_name = tmp[0][1:-1]
                if bone_name in sel_bone_names:
                    self.delete_selected_channels(action, fcurve)
        else:
            for action in bpy.data.actions:
                if self.filters == "SEL_OBJS":
                    for action in bpy.data.actions:
                        for o in bpy.data.objects:
                            if o.animation_data and o.animation_data.action is action:
                                if o.select_get():
                                    for fcurve in action.fcurves:
                                        self.delete_selected_channels(action, fcurve)
                elif self.filters == "SEL_FCURVE":
                    for fcurve in action.fcurves:
                        if fcurve.select:
                            self.delete_selected_channels(action, fcurve)
                elif self.filters == "VIS_FCURVE":
                    for fcurve in action.fcurves:
                        if fcurve in vis_curves:
                            self.delete_selected_channels(action, fcurve)
                else:
                    for fcurve in action.fcurves:
                        self.delete_selected_channels(action, fcurve)

        refresh()
        return {"FINISHED"}


addon_keymaps = []


def register():
    bpy.utils.register_class(GRAPH_OT_Delete_Static_Channels)

    wm = bpy.context.window_manager
    key_conf = wm.keyconfigs.addon
    km = key_conf.keymaps.new(name="Graph Editor", space_type="GRAPH_EDITOR")
    kmi = km.keymap_items.new(GRAPH_OT_Delete_Static_Channels.bl_idname, "D", "PRESS")
    addon_keymaps.append((km, kmi))


def unregister():
    keymap_safe_unregister(addon_keymaps)
    bpy.utils.unregister_class(GRAPH_OT_Delete_Static_Channels)
