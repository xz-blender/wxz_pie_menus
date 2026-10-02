# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty

from . import keymaps

ADDON_ID = __package__.rsplit(".", 2)[0]


def get_preferences(context):
    addon = context.preferences.addons.get(ADDON_ID)
    return getattr(addon.preferences, "quick_crease_weight", None) if addon else None


class WXZ_PG_QuickCreaseWeight(bpy.types.PropertyGroup):

    sensitivity: FloatProperty(
        name="鼠标灵敏度", description="每移动一个像素调整的数值", default=0.005,
        min=0.0001, max=0.1, precision=4,
    )
    show_hud: BoolProperty(name="显示 HUD", default=True)
    hud_anchor: EnumProperty(name="位置", items=(
        ("BOTTOM", "视口底部", "固定在视口底部居中"),
        ("TOP", "视口顶部", "固定在视口顶部居中"),
        ("CURSOR", "跟随鼠标", "显示在鼠标旁边"),
    ), default="BOTTOM")
    hud_offset_x: IntProperty(name="水平偏移", default=0, min=-2000, max=2000)
    hud_offset_y: IntProperty(name="垂直偏移", default=60, min=-2000, max=2000)
    hud_font_size: IntProperty(name="数值字号", default=38, min=12, max=96)
    hud_corner_radius: IntProperty(name="圆角半径", description="卡片圆角大小，0 为直角", default=16, min=0, max=32)
    hud_panel_shadow: BoolProperty(name="卡片阴影", default=True)
    hud_text_color: FloatVectorProperty(name="文字颜色", subtype="COLOR", size=4,
                                       default=(0.84, 0.88, 0.95, 1.0), min=0.0, max=1.0)
    hud_crease_color: FloatVectorProperty(name="折痕主题色", subtype="COLOR", size=4,
                                         default=(1.0, 0.5, 0.15, 1.0), min=0.0, max=1.0)
    hud_bevel_color: FloatVectorProperty(name="倒角权重主题色", subtype="COLOR", size=4,
                                        default=(0.25, 0.75, 1.0, 1.0), min=0.0, max=1.0)
    hud_background: BoolProperty(name="显示背景", default=True)
    hud_background_color: FloatVectorProperty(name="背景颜色与透明度", subtype="COLOR", size=4,
                                             default=(0.022, 0.029, 0.043, 0.94), min=0.0, max=1.0)
    hud_shadow: BoolProperty(name="文字阴影", default=False)
    hud_show_help: BoolProperty(name="显示右侧按键列表", description="工具操作期间，在数值 HUD 右侧持续显示独立的悬浮操作列表", default=True)
    hud_show_bar: BoolProperty(name="显示数值进度条", default=True)

    def draw_settings(self, layout, context):
        layout.label(text="网格编辑模式：点模式作用于顶点，边/面模式作用于边。")
        layout.label(text="快捷键", icon="KEYINGSET")
        keymaps.draw(layout, context)
        layout.prop(self, "sensitivity")
        box = layout.box()
        box.prop(self, "show_hud")
        column = box.column()
        column.enabled = self.show_hud
        column.use_property_split = True
        for name in ("hud_anchor", "hud_offset_x", "hud_offset_y", "hud_font_size", "hud_corner_radius",
                     "hud_text_color", "hud_crease_color", "hud_bevel_color", "hud_background"):
            column.prop(self, name)
        row = column.row()
        row.enabled = self.hud_background
        row.prop(self, "hud_background_color")
        row = column.row()
        row.enabled = self.hud_background
        row.prop(self, "hud_panel_shadow")
        for name in ("hud_shadow", "hud_show_help", "hud_show_bar"):
            column.prop(self, name)
        layout.label(text="左键/Enter 确认；右键/Esc 还原；Shift 吸附 0.1；Ctrl=1；Alt=0。")
        layout.label(text="调用快捷键后，先松开修饰键，再按下即可使用上述控制。")
        layout.label(text="快捷键和 HUD 设置随 Blender 偏好设置保存。", icon="INFO")
