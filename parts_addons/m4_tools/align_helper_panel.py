import bpy

from ...utils import get_prefs


class PanelM4A1tools(bpy.types.Panel):
    bl_idname = "M4A1_PT_m4a1_tools"
    bl_label = "M4A1tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"
    bl_order = 20

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        b = box.box()
        sp = b.split(factor=0.4, align=True)
        a = sp.row(align=True)
        b = sp.row(align=True)

        b.scale_y = a.scale_x = a.scale_y = 1.5
        from .align_helper_npanel import draw_left, draw_right

        pref = get_prefs()
        if not pref.ah_show_text:
            b.scale_x = 2
        if getattr(context.space_data, "region_3d", False):
            draw_left(a, context)
            draw_right(b, context)
