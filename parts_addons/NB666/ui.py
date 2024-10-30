import gettext
import os

import bpy

from .nb_actionctrl_ops import NB_actionctrl_Operator
from .nb_add_bbone2_ctrl_ops import Nb2BboneOperator
from .nb_add_bbone_ctrl_ops import NbBboneOperator
from .nb_add_bbone_ctrl_plus_ops import NbBbonePlusOperator
from .nb_add_ik_ctrl_ops import NbIKBoneOperator
from .nb_add_lattice_bbone2_ctrl_ops import Nb2LatticeBoneOperator
from .nb_add_lattice_bbone_ctrl_ops import NbLatticeBoneOperator
from .nb_add_lattice_bbone_ctrl_plus_ops import NbLatticeBonePlusOperator
from .nb_add_lattice_bbone_ctrl_squash_stretch_ops import NbLatticeBoneSquashStretchOperator
from .nb_add_lattice_bbone_ctrl_wave_ops import NbLatticeBoneWaveOperator
from .nb_add_lattice_ctrl_ops import NbLatticeAndBoneOperator
from .nb_bboxlattice_ops import NbLatticeAAOperator
from .nb_curve_lattice_ctrl_ops import NbCurveLatticeOperator
from .nb_face_bonechain_ops import NB_FaceToBoneChain_Operator
from .nb_fibonacci_bone_ops import fibonacciBoneOperator
from .nb_grease_pencil_to_bbone_ctrl_ops import OBJECT_OT_grease_pencil_to_bbone_ctrl
from .nb_grease_pencil_to_bonechain_ops import OBJECT_OT_grease_pencil_to_armature
from .nb_location_offset_ops import NB_LoctionOffset_Operator
from .nb_obj_bone_ctrl_ops import NbObjectBoneOperator
from .nb_obj_mirror_copy_ops import NbObjectMirrorCopyOperator
from .nb_overshoot_ops import NB_AN_overshoot
from .nb_pick_put_bake_action_ops import NB_Pick_Put_Bake_Action_Operator
from .nb_pick_put_clear_ops import NB_Pick_Put_Clear_Operator
from .nb_pick_up_ops import NB_Pick_Up_Operator
from .nb_put_down_ops import NB_Put_Down_Operator
from .nb_removelattice_ops import NbLatticeRemoveOperator
from .nb_rotation_offset_ops import NB_RotationOffset_Operator
from .nb_sel_update_driver_ops import NB_selall_update_driver_Operator
from .nb_simpleparent_ops import NB_simpleparent_Operator
from .nb_sphere_lattice_ctrl_ops import NbSphereLatticeOperator
from .nb_subdivision_bottom import NbSubdivisionBottomOperator
from .nb_track_offset_bonechain_ops import NB_TrackOffset_BoneChain_Operator
from .nb_track_offset_ops import NB_TrackOffset_Operator

# bpy.utils.user_resource('SCRIPTS', path="addons")#插件的位置


# 定义中英文文本资源
translations = {
    "en": {
        "NB": "NB",
        "Location Offset": "Location Offset",
        "Rotation Offset": "Rotation Offset",
        "Track Offset": "Track Offset",
        "Track Offset(BoneChain)": "Track Offset(BoneChain)",
        "+1bbone": "+1bbone",
        "+1bbone+": "+1bbone+",
        "+2bbone": "+2bbone",
        "Lattice +1 ctrl": "Lattice +1 ctrl",
        "Lattice +1 ctrl+": "Lattice +1 ctrl+",
        "Lattice ss ctrl": "Lattice ss ctrl",
        "Lattice Wave ctrl": "Lattice Wave ctrl",
        "Lattice +2 ctrl": "Lattice +2 ctrl",
        "Lattice +B": "Lattice +B",
        "NBIK": "NBIK",
        "fibonacci": "fibonacci",
        "Lattice+": "Lattice+",
        "Lattice-": "Lattice-",
        "select update driver": "select update driver",
        "Lattice Curve": "Lattice Curve",
        "Subdivision Bottom": "Subdivision Bottom",
        "Sphere Lattice": "Sphere Lattice",
        "Action Ctrl": "Action Ctrl",
        "Face To Bone Chain": "Face To Bone Chain",
        "nb simple parent": "nb simple parent",
        "velocity weight": "velocity weight",
        "Overshoot": "Overshoot",
        "Object Bone": "Object Bone",
        "Mirror Copy": "Mirror Copy",
        "Pick Up(1)": "Pick Up(1)",
        "Put Down(0)": "Put Down(0)",
        "Clear Mark": "Clear Mark",
        "Pick Put Animation Bake": "Pick Put Animation Bake",
        "grease pencil To Bone Chain": "grease pencil To Bone Chain",
        "grease pencil To +1bbone": "grease pencil To +1bbone",
    },
    "zh": {
        "NB": "牛逼",
        "Location Offset": "位置错帧",
        "Rotation Offset": "旋转错帧",
        "Track Offset": "跟随错帧",
        "Track Offset(BoneChain)": "骨骼链跟随错帧",
        "+1bbone": "+1柔骨控",
        "+1bbone+": "+1柔骨控+",
        "+2bbone": "+2柔骨控",
        "Lattice +1 ctrl": "晶格+1控",
        "Lattice +1 ctrl+": "晶格+1控+",
        "Lattice ss ctrl": "晶格+SS控",
        "Lattice Wave ctrl": "晶格+Wave控",
        "Lattice +2 ctrl": "晶格+2控",
        "Lattice +B": "晶格+B",
        "NBIK": "牛逼IK",
        "fibonacci": "斐波那契",
        "Lattice+": "晶格+",
        "Lattice-": "晶格-",
        "select update driver": "选择更新驱动",
        "Lattice Curve": "晶格曲线",
        "Subdivision Bottom": "细分移至底部",
        "Sphere Lattice": "球晶",
        "Action Ctrl": "+动作控制器",
        "Face To Bone Chain": "模型面转骨骼链",
        "nb simple parent": "简单父级",
        "velocity weight": "速度权重",
        "Overshoot": "过冲",
        "Object Bone": "物体骨骼",
        "Mirror Copy": "镜像复制",
        "Pick Up(1)": "拿起(1)",
        "Put Down(0)": "放下(0)",
        "Clear Mark": "清除标记",
        "Pick Put Animation Bake": "拿放动画烘焙",
        "grease pencil To Bone Chain": "蜡笔转骨骼链",
        "grease pencil To +1bbone": "蜡笔转 +1柔骨控",
    },
}


# 获取当前语言
def get_language():
    #    return bpy.context.preferences.view.language
    return bpy.app.translations.locale


# 获取对应语言的文本资源
def get_translation(key):
    language = get_language()
    if "zh" in get_language():
        language = "zh"
    if language in translations:
        if key in translations[language] and bpy.context.preferences.view.use_translate_interface:
            return translations[language][key]
    # 如果未找到对应语言的文本资源，则默认使用英文
    return translations["en"][key]


class Prop_nb_666(bpy.types.PropertyGroup):
    cuoFrame: bpy.props.IntProperty(default=1, name="Frame", min=-10, max=10)
    cInfluence: bpy.props.FloatProperty(default=1.0, name="Influence", min=0, max=1)
    velocity_weight: bpy.props.FloatProperty(default=0.666, name="velocity weight", min=0, max=1)

    LOC: bpy.props.BoolProperty(default=True, name="LOC")
    ROT: bpy.props.BoolProperty(default=True, name="ROT")
    SIZE: bpy.props.BoolProperty(default=True, name="SIZE")
    gap_frame: bpy.props.IntProperty(default=2, name="Frame", min=1, max=10)
    cycle_index: bpy.props.IntProperty(default=6, name="index", min=1, max=10)
    factor: bpy.props.FloatProperty(default=1.0, name="factor", min=0, max=1)


class NB_PT_666_3dview(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_idname = "VIEW_PT_EG1"
    bl_region_type = "UI"
    bl_category = "XZ"
    bl_label = "绑定工具"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)
        row.prop(bpy.context.scene.Prop_nb_666, "gap_frame", toggle=True)
        row.prop(bpy.context.scene.Prop_nb_666, "cycle_index", toggle=True)
        row.prop(bpy.context.scene.Prop_nb_666, "factor", toggle=True)
        row = box.row(align=True)
        row.prop(bpy.context.scene.Prop_nb_666, "LOC", text="Location", toggle=True)
        row.prop(bpy.context.scene.Prop_nb_666, "ROT", text="Rotation", toggle=True)
        row.prop(bpy.context.scene.Prop_nb_666, "SIZE", text="Scale", toggle=True)
        row = box.row(align=True)
        row.operator(NB_AN_overshoot.bl_idname, icon="IPO_ELASTIC", text=get_translation("Overshoot"))

        row = layout.row(align=True)
        row.prop(bpy.context.scene.Prop_nb_666, "cuoFrame", toggle=True)
        row.prop(bpy.context.scene.Prop_nb_666, "cInfluence", toggle=True)
        row.prop(bpy.context.scene.Prop_nb_666, "velocity_weight", toggle=True, text=get_translation("velocity weight"))
        row = layout.row(align=True)
        row.operator(NB_LoctionOffset_Operator.bl_idname, text=get_translation("Location Offset"))
        row.operator(NB_RotationOffset_Operator.bl_idname, text=get_translation("Rotation Offset"))
        row = layout.row(align=True)
        row.operator(NB_TrackOffset_Operator.bl_idname, text=get_translation("Track Offset"))
        row.operator(NB_TrackOffset_BoneChain_Operator.bl_idname, text=get_translation("Track Offset(BoneChain)"))
        row = layout.row(align=True)
        row.operator(NbBboneOperator.bl_idname, text=get_translation("+1bbone"))
        row.operator(NbBbonePlusOperator.bl_idname, text=get_translation("+1bbone+"))
        row.operator(Nb2BboneOperator.bl_idname, text=get_translation("+2bbone"))
        row = layout.row(align=True)
        row.operator(NbLatticeBoneOperator.bl_idname, text=get_translation("Lattice +1 ctrl"))
        row.operator(NbLatticeBonePlusOperator.bl_idname, text=get_translation("Lattice +1 ctrl+"))
        row.operator(Nb2LatticeBoneOperator.bl_idname, text=get_translation("Lattice +2 ctrl"))

        row = layout.row(align=True)
        row.operator(NbLatticeBoneSquashStretchOperator.bl_idname, text=get_translation("Lattice ss ctrl"))
        row.operator(NbLatticeBoneWaveOperator.bl_idname, text=get_translation("Lattice Wave ctrl"))
        row = layout.row(align=True)
        row.operator(NbLatticeAndBoneOperator.bl_idname, text=get_translation("Lattice +B"))

        layout.operator(NbIKBoneOperator.bl_idname, text=get_translation("NBIK"))
        layout.operator(fibonacciBoneOperator.bl_idname, text=get_translation("fibonacci"))

        layout.operator(NbLatticeAAOperator.bl_idname, text=get_translation("Lattice+"))
        layout.operator(NbLatticeRemoveOperator.bl_idname, text=get_translation("Lattice-"))
        row = layout.row(align=True)
        row.operator(NbCurveLatticeOperator.bl_idname, text=get_translation("Lattice Curve"))
        row.operator(NbSphereLatticeOperator.bl_idname, text=get_translation("Sphere Lattice"))
        box = layout.box()
        row = box.row(align=True)
        row.operator(NB_selall_update_driver_Operator.bl_idname, text=get_translation("select update driver"))
        row.operator(NbSubdivisionBottomOperator.bl_idname, text=get_translation("Subdivision Bottom"))
        row = layout.row(align=True)
        row.operator(NB_actionctrl_Operator.bl_idname, text=get_translation("Action Ctrl"))
        row = layout.row(align=True)
        row.operator(NB_FaceToBoneChain_Operator.bl_idname, text=get_translation("Face To Bone Chain"))
        row.operator(NbObjectMirrorCopyOperator.bl_idname, text=get_translation("Mirror Copy"))
        row = layout.row(align=True)
        row.operator(OBJECT_OT_grease_pencil_to_armature.bl_idname, text=get_translation("grease pencil To Bone Chain"))
        row.operator(OBJECT_OT_grease_pencil_to_bbone_ctrl.bl_idname, text=get_translation("grease pencil To +1bbone"))
        row = layout.row(align=True)
        row.operator(NB_simpleparent_Operator.bl_idname, text=get_translation("nb simple parent"))
        row.operator(NbObjectBoneOperator.bl_idname, text=get_translation("Object Bone"))
        box = layout.box()
        row = box.row(align=True)
        row.operator(NB_Pick_Up_Operator.bl_idname, text=get_translation("Pick Up(1)"))
        row.operator(NB_Put_Down_Operator.bl_idname, text=get_translation("Put Down(0)"))
        row.operator(NB_Pick_Put_Clear_Operator.bl_idname, text=get_translation("Clear Mark"))
        row = box.row(align=True)
        row.operator(NB_Pick_Put_Bake_Action_Operator.bl_idname, text=get_translation("Pick Put Animation Bake"))


##        layout.operator(NbLatticeBoneOperator.bl_idname, text="晶格添加控制")


class NB_PT_666_TIMELINE(bpy.types.Panel):
    bl_label = "拿得起 放得下"
    bl_idname = "NB_PT_666_TIMELINE"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "XZ"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.operator(NB_Pick_Up_Operator.bl_idname, text=get_translation("Pick Up(1)"))
        box.operator(NB_Put_Down_Operator.bl_idname, text=get_translation("Put Down(0)"))
        box.operator(NB_Pick_Put_Clear_Operator.bl_idname, text=get_translation("Clear Mark"))
        box.operator(NB_Pick_Put_Bake_Action_Operator.bl_idname, text=get_translation("Pick Put Animation Bake"))


class nbnb_Prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        lay = self.layout
        row = lay.row()
        row.operator("wm.url_open", text="插件视频1", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV1KN41127y8"
        )
        row.operator("wm.url_open", text="插件视频2", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV12w4m1Z7UG"
        )
        row.operator("wm.url_open", text="插件视频3", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV17u4m1F7ia"
        )
        row = lay.row()
        row.operator("wm.url_open", text="插件视频4", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV1LH4y1g73M"
        )
        row.operator("wm.url_open", text="插件视频5", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV16T421a7Ri"
        )
        row.operator("wm.url_open", text="插件视频6", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV1bj421Q7HE"
        )
        row = lay.row()
        row.operator("wm.url_open", text="插件视频7", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV19kafecEQe"
        )
        row.operator("wm.url_open", text="听歌", icon="FILE_MOVIE").url = "https://www.bilibili.com/video/BV1XmsLepE8e"
        row.operator("wm.url_open", text="插件视频8", icon="FILE_MOVIE").url = (
            "https://www.bilibili.com/video/BV1kN4meFE16"
        )


def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(NB_Pick_Up_Operator.bl_idname)
    layout.operator(NB_Put_Down_Operator.bl_idname)
    layout.operator(NB_Pick_Put_Clear_Operator.bl_idname)


# ---------REGISTER ----------.

classes = (
    # nbnb_Prefs,
    NB_PT_666_3dview,
    Prop_nb_666,
    NB_PT_666_TIMELINE,
    # 添加其他需要注册的操作符类...
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Prop_nb_666 = bpy.props.PointerProperty(type=Prop_nb_666)
    bpy.types.TIME_MT_marker.append(draw_menu)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.Prop_nb_666
    bpy.types.TIME_MT_marker.remove(draw_menu)
