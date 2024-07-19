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
from .model.node_relax_props import NodeRelaxProps
from .operators.node_relax_arrange import NodeRelaxArrange
from .operators.node_relax_brush import NodeRelaxBrush
from .panels.node_relax_arrange import NodeRelaxArrangePanel
from .panels.node_relax_brush import NodeRelaxBrushPanel

bl_info = {
    "name": "Node Relax",
    "author": "Shahzod Boyhonov (Specoolar)",
    "description": "Tool for arranging nodes easier",
    "blender": (2, 92, 0),
    "version": (1, 0, 0),
    "location": "Node Editor > Properties > Node Relax. Shortcut: Shift R",
    "category": "Node",
}

import bpy

classes = [NodeRelaxBrush, NodeRelaxBrushPanel, NodeRelaxArrange, NodeRelaxArrangePanel, NodeRelaxProps]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = []


def register_keymaps():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")
    kmi = km.keymap_items.new(NodeRelaxBrush.bl_idname, "R", "PRESS", shift=True)
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.NodeRelax_props = bpy.props.PointerProperty(type=NodeRelaxProps)
    register_keymaps()


def unregister():
    # unregister_keymaps()

    class_unregister()
    del bpy.types.Scene.NodeRelax_props


if __name__ == "__main__":
    register()
