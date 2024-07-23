# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Inset Outset Bool2D",
    "author": "Tiemen Blankert",
    "description": "",
    "blender": (3, 3, 0),
    "version": (0, 0, 2),
    "location": "View3D",
    "warning": "",
    "category": "Object",
}
import bpy

from .booleans import MESH_OT_booleans
from .inset import MESH_OT_inset_cl
from .outset import MESH_OT_outset_cl
from .paneel import TM_PT_paneel

classes = (
    TM_PT_paneel,
    MESH_OT_inset_cl,
    MESH_OT_outset_cl,
    MESH_OT_booleans,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    ...
