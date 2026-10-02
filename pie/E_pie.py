from ..module.reg import register_classes, unregister_classes
import bpy
from bpy.types import Menu

from ..items import All_Pie_keymaps
from ..module.quick_crease_weight.operators import PIE_Shift_E_KEY, cancel_active
from ..utils import extend_keymaps_list
from .utils import *


class VIEW3D_PIE_MT_Bottom_E(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "EDIT" and ob_type == "MESH":
            # 4 - LEFT
            pie.operator("mesh.flip_normals")
            # 6 - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_y = 1.1
            col.operator("pie.mm_fuse")
            col.operator("pie.mm_change_width")
            col.operator("pie.mm_unchamfer")
            col.operator("pie.mm_turn_corner")
            col.operator("pie.mm_quad_corner")
            col.separator(factor=0.1)
            col.operator("pie.mm_unfuse")
            col.operator("pie.mm_refuse")
            col.operator("pie.mm_unbevel")
            col.separator(factor=0.1)
            col.operator("pie.mm_offset_cut")
            col.operator("pie.mm_unfuck")
            col.operator("pie.mm_boolean_cleanup")
            col.separator(factor=0.1)
            col.operator("pie.mm_symmetrize")
            # 2 - BOTTOM
            pie.operator("mesh.normals_make_consistent")
            # 8 - TOP
            col = pie.split().box().column(align=True)
            col.scale_y = 1.4
            col.operator("mesh.extrude_manifold", text="挤出流形")
            col.operator("pie.punchit", text="负向流形")
            # 7 - TOP - LEFT
            pie.operator("mesh.bridge_edge_loops", text="桥接循环边")
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            col = pie.split().box().column()
            add_operator(col, "mesh.set_edge_flow")
            add_operator(col, "mesh.set_edge_linear")
            # 3 - BOTTOM - RIGHT
            pie.separator()

        if ob_mode == "OBJECT" and ob_type == "MESH":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.operator("pie.ke_lineararray")
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("pie.ke_radial_instances")
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


CLASSES = [
    VIEW3D_PIE_MT_Bottom_E,
    PIE_Shift_E_KEY,
]

addon_keymaps = []


def register_keymaps():
    unregister_keymaps()
    addon = bpy.context.window_manager.keyconfigs.addon
    if addon is None:
        return

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "E", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_E"
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", shift=True)
    kmi.properties.attr_name = "crease"
    addon_keymaps.append((km, kmi))

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", ctrl=True, shift=True)
    kmi.properties.attr_name = "bevel_weight"
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    # Remove the shared UI registry entries while the RNA items are still valid.
    All_Pie_keymaps[:] = [entry for entry in All_Pie_keymaps if entry not in addon_keymaps]
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    addon_keymaps.clear()


@register_classes(CLASSES)
def register():
    cancel_active()
    register_keymaps()
    extend_keymaps_list(addon_keymaps)


@unregister_classes(CLASSES)
def unregister():
    cancel_active()
    unregister_keymaps()
