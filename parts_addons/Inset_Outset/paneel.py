import bpy

class TM_PT_paneel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Edit'
    bl_label = "Inset/Outset/Bool2D"
    bl_context = "mesh_edit"

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5 
        row.operator("mesh.outset_clipper", text = 'Outset/Inset')

        layout = self.layout
        col = layout.column(align=True)

        box =  layout.box()               
        box.label(text='2D布尔:') 
        row = box.row(align =False)
        col = box.column(align =False)
        row.operator('mesh.tiem_bools',icon="SELECT_EXTEND",text="并集").keuze = 'opl_1'
        row.operator('mesh.tiem_bools',icon="SELECT_SUBTRACT",text="差集").keuze = 'opl_2'
        row.operator('mesh.tiem_bools',icon="SELECT_DIFFERENCE",text="外集").keuze = 'opl_3'
        row.operator('mesh.tiem_bools',icon="SELECT_INTERSECT",text="交集").keuze = 'opl_4'