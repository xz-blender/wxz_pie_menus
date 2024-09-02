bl_info = {
    "name": "NB 666",
    "author": "下前下前拳",
    "category": "NB",
    "blender": (4, 0, 0),
    "location": "Sidebar > 牛逼",
    "description": "牛逼插件 谁用谁牛逼",
    "wiki_url": "https://space.bilibili.com/67482199",
    "tracker_url": "https://space.bilibili.com/67482199",
    "version": (1, 0, 9),
}

from . import nb_obj_mirror_copy_ops
from . import nb_obj_bone_ctrl_ops
from . import nb_nla_ops
from . import nb_overshoot_ops
from . import nb_simpleparent_ops
from . import nb_bonecustomshape_ops
from . import nb_add_lattice_bbone_ctrl_squash_stretch_ops
from . import nb_face_bonechain_ops
from . import nb_actionctrl_ops
from . import nb_add_lattice_bbone_ctrl_plus_ops
from . import nb_add_bbone_ctrl_plus_ops
from . import nb_sphere_lattice_ctrl_ops
from . import nb_subdivision_bottom
from . import nb_curve_lattice_ctrl_ops
from . import nb_sel_update_driver_ops
from . import nb_removelattice_ops
from . import nb_bboxlattice_ops
from . import nb_autoweight2bone_ops
from . import nb_add_lattice_ctrl_ops
from . import nb_add_ik_ctrl_ops
from . import nb_fibonacci_bone_ops
from . import nb_add_bbone_ctrl_ops
from . import nb_add_bbone2_ctrl_ops
from . import nb_add_lattice_bbone_ctrl_ops
from . import nb_add_lattice_bbone2_ctrl_ops
from . import nb_track_offset_bonechain_ops
from . import nb_track_offset_ops
from . import nb_rotation_offset_ops
from . import nb_location_offset_ops
from . import ui


import bpy


mods = (
nb_obj_mirror_copy_ops,
nb_obj_bone_ctrl_ops,
nb_nla_ops,
nb_overshoot_ops,
nb_simpleparent_ops,
nb_bonecustomshape_ops,
nb_add_lattice_bbone_ctrl_squash_stretch_ops,
nb_face_bonechain_ops,
nb_actionctrl_ops,
nb_add_lattice_bbone_ctrl_plus_ops,
nb_add_bbone_ctrl_plus_ops,
nb_sphere_lattice_ctrl_ops,
nb_subdivision_bottom,
nb_curve_lattice_ctrl_ops,
nb_sel_update_driver_ops,
nb_removelattice_ops,
nb_bboxlattice_ops,
nb_autoweight2bone_ops,
nb_add_lattice_ctrl_ops,
nb_add_ik_ctrl_ops,
nb_fibonacci_bone_ops,
nb_add_bbone_ctrl_ops,
nb_add_bbone2_ctrl_ops,
nb_add_lattice_bbone_ctrl_ops,
nb_add_lattice_bbone2_ctrl_ops,
nb_track_offset_bonechain_ops,
nb_track_offset_ops,
nb_rotation_offset_ops,
nb_location_offset_ops,
ui,
)



def register():
    if bpy.app.background:
        return

    
    for m in mods:
        m.register()
        
        
def unregister():
    if bpy.app.background:
        return

    for m in reversed(mods):
        m.unregister()

if __name__ == "__main__":
    register()
