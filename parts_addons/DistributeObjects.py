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

bl_info = {
    "name": "DPFR Distribute Objects",
    "author": "Duarte Farrajota Ramos",
    "version": (1, 0),
    "blender": (2, 82, 0),
    "location": "View3D > Object > Transform > Distribute",
    "description": "Distribute selected objects in a grid-like array",
    "warning": "",
    "wiki_url": "https://blendermarket.com/products/distribute-objects-addon/docs",
    "category": "Usability",
}

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty

############################################################################################################################
# Operators


class OBJECT_OT_DistributeObjects(bpy.types.Operator):
    """Distributes selected objects in a grid array"""  # Blender will use this as a tooltip for menu items and buttons.

    bl_idname = "object.distribute"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Distribute Objects"  # Display name in the interface.
    bl_options = {"REGISTER", "UNDO"}  # Enable undo for the operator.

    # Define Spacing for each axis
    spacingX: FloatProperty(
        name="Spacing X",
        description="Distance increment for the X axis",
        subtype="DISTANCE",
        min=-100000.0,
        max=100000.0,
        default=0.1,
    )

    spacingY: FloatProperty(
        name="Spacing Y",
        description="Distance increment for the Y axis",
        subtype="DISTANCE",
        min=-100000.0,
        max=100000.0,
        default=0.1,
    )

    spacingZ: FloatProperty(
        name="Spacing Z",
        description="Distance increment for the Z axis",
        subtype="DISTANCE",
        min=-100000.0,
        max=100000.0,
        default=0.1,
    )

    # Define max distance for each axis
    maxX: FloatProperty(
        name="Maximum X",
        description="Maximum distance in the X axis",
        subtype="DISTANCE",
        min=0.0,
        max=100000.0,
        default=0.0,
    )

    maxY: FloatProperty(
        name="Maximum Y",
        description="Maximum distance in the Y axis",
        subtype="DISTANCE",
        min=0.0,
        max=100000.0,
        default=0.0,
    )

    # Define count limit for each axis
    countX: IntProperty(
        name="Count X",
        description="Number of Items in X",
        min=0,
        max=100000,
        default=0,
    )

    countY: IntProperty(
        name="Count Y",
        description="Number of Items in Y",
        min=0,
        max=100000,
        default=0,
    )

    # Defines origin point for array
    origin: EnumProperty(
        name="Start Point",
        description="Start Point for Array",
        items=[
            ("CURSOR", "3D Cursor", ""),
            ("ACTIVE", "Active Object", ""),
            ("WORLD", "World Origin", ""),
        ],
        default="ACTIVE",
    )

    # Defines sorting order for objects
    sort: EnumProperty(
        name="Sort",
        description="Sort objects",
        items=[
            ("NONE", "No Sorting", ""),
            ("NAME", "By Name", ""),
            ("X", "By X Coordinate", ""),
            ("Y", "By Y Coordinate", ""),
            ("Z", "By Z Coordinate", ""),
        ],
        default="NONE",
    )

    def distribute(self, context):

        if self.sort == "NONE":
            selection = bpy.context.selected_objects
        elif self.sort == "NAME":
            selection = bpy.context.selected_objects
            selection.sort(key=lambda o: o.name)
        elif self.sort == "X":
            selection = bpy.context.selected_objects
            selection.sort(key=lambda o: o.matrix_world.translation[0])
        elif self.sort == "Y":
            selection = bpy.context.selected_objects
            selection.sort(key=lambda o: o.matrix_world.translation[1])
        elif self.sort == "Z":
            selection = bpy.context.selected_objects
            selection.sort(key=lambda o: o.matrix_world.translation[2])

        if self.origin == "CURSOR":
            start_position = (bpy.context.scene.cursor.location,)
        elif self.origin == "ACTIVE" and bpy.context.active_object == None:
            start_position = [[0, 0, 0]]
        elif self.origin == "ACTIVE":
            start_position = (bpy.context.active_object.matrix_world.translation,)
        elif self.origin == "WORLD":
            start_position = [[0, 0, 0]]

        offsetX = 0
        offsetY = 0
        offsetZ = 0
        iterationX = 0
        iterationY = 0
        iterationZ = 0

        for object in selection:
            object.location = (
                start_position[0][0] + self.spacingX * iterationX,
                start_position[0][1] + self.spacingY * iterationY,
                start_position[0][2] + self.spacingZ * iterationZ,
            )
            iterationX += 1
            if (
                self.maxX != 0.0
                and abs(self.spacingX * iterationX) >= self.maxX
                or self.countX != 0
                and iterationX >= self.countX
            ):
                iterationX = 0
                iterationY += 1
            if (
                self.maxY != 0.0
                and abs(self.spacingY * iterationY) >= self.maxY
                or self.countY != 0
                and iterationY >= self.countY
            ):
                iterationY = 0
                iterationZ += 1

    def execute(self, context):  # execute() is called by Blender when running the operator.
        self.distribute(context)
        return {"FINISHED"}  # This lets Blender know the operator finished successfully.

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, "origin")
        row = layout.row(align=True)
        row.prop(self, "sort")

        col = layout.column(align=True)
        col.prop(self, "spacingX")
        col.prop(self, "spacingY")
        col.prop(self, "spacingZ")

        split = layout.split()
        col = split.column(align=True)
        col.prop(self, "countX")
        col.prop(self, "countY")
        col = split.column(align=True)
        col.prop(self, "maxX", text="Max X")
        col.prop(self, "maxY", text="Max Y")


############################################################################################################################
# UI


def VIEW3D_MT_transform_object_distribute(self, context):
    self.layout.operator("object.distribute", icon="MOD_ARRAY")


############################################################################################################################
# Class registration

classes = (OBJECT_OT_DistributeObjects,)


def register():
    for cla in classes:
        bpy.utils.register_class(cla)
    bpy.types.VIEW3D_MT_transform_object.append(VIEW3D_MT_transform_object_distribute)


def unregister():
    for cla in reversed(classes):
        bpy.utils.unregister_class(cla)
    bpy.types.VIEW3D_MT_transform_object.remove(VIEW3D_MT_transform_object_distribute)


if __name__ == "__main__":
    register()
