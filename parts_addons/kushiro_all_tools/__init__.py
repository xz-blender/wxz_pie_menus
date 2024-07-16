# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Kushiro
import bpy


from bpy.props import (
        FloatProperty,
        IntProperty,
        BoolProperty,
        EnumProperty,
        )


#from . import helper

import importlib

# from .connect_face import connect_face
# from .cut_corner import cut_corner
# from .quad_swords import quad_swords
# from .quick_bridge import quick_bridge
# from .select_sim import select_sim
# from .surface_inflate import surface_inflate
# from .visual_axis import visual_axis

# from .connect_face import connect_face
from . import pref

from . import attach_align
from . import connect_face
from . import cut_corner
from . import even_triangulation
from . import face_regulator
from . import quad_swords
from . import quick_bridge
from . import safe_inset
from . import shatter_cut
from . import select_sim
from . import surface_inflate
from . import soft_bevel
from . import visual_axis

from . import curve_face_color
from . import edge_extrude
from . import light_pattern
from . import padding_inset
from . import safe_ngon
from . import slow_bevel

from . import face_cutter
from . import beta_quad
from . import bend_face
from . import hard_bevel
from . import loop_copier
from . import mesh_copier
from . import round_inset
from . import slide_edge
from . import simple_bend

from .translation.translate import GetTranslationDict

bl_info = {
    "name": "Kushiro Tools",
    "description": "Kushiro Tools",
    "author": "Kushiro",
    "version": (1, 5, 13),
    "blender": (2, 83, 0),
    "location": "View3D > Edit > Context Menu (right click)",
    "category": "Mesh",
}


class VIEW3D_MT_my_addon_submenu(bpy.types.Menu):
    bl_label = "Kushiro Tool Others"

    def draw(self, context):
        layout = self.layout
        layout.operator('mesh.attach_align_operator')
        layout.operator('mesh.connectface_operator')
        layout.operator('mesh.cut_corner_operator')
        layout.operator('mesh.even_triangulation_operator')
        layout.operator('mesh.face_regulator_operator')
        layout.operator('mesh.quad_swords_operator')
        layout.operator('mesh.quick_bridge_operator')
        layout.operator('mesh.safe_inset_operator')
        layout.operator('mesh.shatter_cut_operator')
        layout.operator('mesh.select_sim_operator')
        layout.operator('mesh.surface_inflate_operator')
        layout.operator('mesh.soft_bevel_operator')
        layout.operator('mesh.visual_axis_operator')
        layout.operator('mesh.curve_face_color_operator')
        layout.operator('mesh.edge_extrude_operator')
        layout.operator('mesh.light_pattern')
        layout.operator('mesh.safe_ngon_operator')
        layout.operator('mesh.slow_bevel_operator')
        

class VIEW3D_MT_my_addon_submenu_new(bpy.types.Menu):
    bl_label = "Kushiro Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator('mesh.bend_face_operator')
        layout.operator('mesh.face_cutter_operator')
        layout.operator('mesh.beta_quad_operator')
        layout.operator('mesh.hard_bevel_operator')
        layout.operator('mesh.loop_copier_operator')
        layout.operator('mesh.mesh_copier_operator')
        layout.operator('mesh.padding_inset_operator')
        layout.operator('mesh.round_inset_operator')
        layout.operator('mesh.slide_edge_operator')
        layout.operator('mesh.simple_bend_operator')
        
def menu_func(self, context):
    layout = self.layout
    layout.menu("VIEW3D_MT_my_addon_submenu_new")
    layout.menu("VIEW3D_MT_my_addon_submenu")

classes = [
    attach_align.AttachAlignOperator,
    connect_face.CONNECTFACE_OT_operator,
    cut_corner.CutCornerOperator,
    even_triangulation.EvenTriangulationOperator,
    face_regulator.FaceRegulatorOperator,
    quad_swords.QuadSwordsOperator,
    quick_bridge.QuickBridgeOperator,
    safe_inset.SafeInsetOperator,
    shatter_cut.ShatterCutOperator,
    select_sim.SelectSimOperator,
    soft_bevel.SoftBevelOperator,
    surface_inflate.SurfaceInflateOperator,
    visual_axis.VisualAxisOperator,
    even_triangulation.InstallScipyOperator,
    safe_ngon.SafeNgonOperator,

    curve_face_color.CurveFaceColorOperator,
    edge_extrude.EdgeExtrudeOperator,
    light_pattern.LightPatternOperator,
    padding_inset.PaddingInsetOperator,
    slow_bevel.SlowBevelOperator,
    
    face_cutter.FaceCutterOperator,
    beta_quad.BetaQuadOperator,
    bend_face.BendFaceOperator,
    hard_bevel.HardBevelOperator,
    loop_copier.LoopCopierOperator,
    mesh_copier.MeshCopierOperator,
    round_inset.RoundInsetOperator,
    slide_edge.SlideEdgeOperator,
    simple_bend.SimpleBendOperator,

    VIEW3D_MT_my_addon_submenu,
    VIEW3D_MT_my_addon_submenu_new,
    pref.BendFacePreferences,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)

def register():
    try:
        for cls in classes:
            importlib.reload(cls)
    except:
        pass
    
    class_register()
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)

    try:
	    bpy.app.translations.register(__package__, GetTranslationDict())
    except Exception as e: print(e)  


def unregister():
    class_unregister()

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)

    try:
	    bpy.app.translations.unregister(__package__)
    except Exception as e: print(e)


if __name__ == "__main__":    
    register()


