import bpy
from bpy.types import Operator, Menu
from .utils import set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "Properties > Modifiers",
    "category": "BAR",
}


class Bar_Quick_Decimate(Operator):
    bl_idname = "bar.quick_decimate"
    bl_label = submoduname
    bl_options = {"REGISTER", "UNDO"}

    ratio: bpy.props.FloatProperty(name='decimate', min=0, max=1)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ratio = self.ratio

        if context.selected_objects:
            for obj in context.selected_objects:
                context.view_layer.objects.active = obj

                md_name = "精简-%.3s" % ratio

                obj.modifiers.new(name=md_name, type='DECIMATE')
                obj.modifiers[md_name].ratio = ratio

            self.report({"INFO"}, md_name)
            return {"FINISHED"}
        else:
            self.report({"INFO"}, "没有选择物体")
            return {"FINISHED"}


# Menus #
def menu(self, context):
    col = self.layout.column(align=True)
    col.alignment = 'CENTER'
    col.scale_y = 0.9

    row = col.row(align=True)
    row.operator('object.modifier_add', icon='MOD_TRIANGULATE',
                 text='三角化').type = 'TRIANGULATE'

    row.operator(Bar_Quick_Decimate.bl_idname, text="精简0.1").ratio = 0.1

    row.operator(Bar_Quick_Decimate.bl_idname, text="精简0.3").ratio = 0.3

    row.operator(Bar_Quick_Decimate.bl_idname, text="精简0.5").ratio = 0.5


# Modifier Bar
def costom_modifier_bar(self, context):
    col = self.layout.column(align=True)
    col.alignment = 'CENTER'
    col.scale_y = 0.9
    # ----------------------------------------------------------------------
    row = col.row(align=True)
    row.operator('object.modifier_add', icon='GEOMETRY_NODES',
                 text='节点').type = 'NODES'
    row.operator('object.modifier_add', icon='MOD_SUBSURF',
                 text='细分').type = 'SUBSURF'

    row.operator('object.modifier_add', icon='MOD_SHRINKWRAP',
                 text='缩裹').type = 'SHRINKWRAP'
    # ----------------------------------------------------------------------
    row = col.row(align=True)
    bevel = row.operator('object.modifier_add', icon='MOD_BEVEL', text='倒角')
    bevel.type = 'BEVEL'
    # context.object.modifiers["Bevel"].harden_normals = True
    # bevel.segments = 2
    row.operator('object.modifier_add',
                 icon='MOD_ARRAY', text='阵列').type = 'ARRAY'
    if context.active_object.type == 'MESH':
        row.operator('object.modifier_add', icon='MOD_DISPLACE',
                     text='置换').type = 'DISPLACE'
    else:
        row.operator('pie.empty_operator', icon='ERROR', text='置换')
    # ----------------------------------------------------------------------
    row = col.row(align=True)
    mirror = row.operator('object.modifier_add', icon='MOD_MIRROR', text='镜像')
    mirror.type = 'MIRROR'
    # mirror.use_clip = True
    if context.active_object.type == 'MESH':
        row.operator('object.modifier_add',
                     icon='MOD_BOOLEAN', text='布尔').type = 'BOOLEAN'
    else:
        row.operator('pie.empty_operator', icon='ERROR', text='布尔')

    # boolean.solver = 'FAST'
    row.operator('object.modifier_add', icon='MOD_SIMPLEDEFORM',
                 text='形变').type = 'SIMPLE_DEFORM'

    # ----------------------------------------------------------------------
    row = col.row(align=True)
    row.operator('object.modifier_add', icon='MOD_SOLIDIFY',
                 text='厚度').type = 'SOLIDIFY'
    row.operator('object.modifier_add', icon='AUTOMERGE_OFF',
                 text='焊接').type = 'WELD'
    row.operator('object.modifier_add', icon='MOD_SCREW',
                 text='螺旋').type = 'SCREW'


classes = [
    Bar_Quick_Decimate,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.DATA_PT_modifiers.prepend(costom_modifier_bar)
    bpy.types.DATA_PT_modifiers.append(menu)  # 区别 prepend 和 append


def unregister():
    bpy.types.DATA_PT_modifiers.remove(menu)
    bpy.types.DATA_PT_modifiers.remove(costom_modifier_bar)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
