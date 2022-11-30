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

def add_set_modifier_prop(self,context,add_modifier):
    prop_bool = self.prop_bool
    prop_float = self.prop_float
    prop_int = self.prop_int
    prop_string = self.prop_string
    #转化自定义修改器参数
    if prop_bool != '':
        prop_bool_list = prop_bool.split(',')
        for prop in prop_bool_list:
            split = prop.split('=')
            prop_name = split[0]
            prop_value = split[1] == 'True'
            #设置自定义参数，布尔类型
            setattr(add_modifier, prop_name, prop_value)
    if prop_float != '':
        prop_float_list = prop_float.split(',')
        for prop in prop_float_list:
            split = prop.split('=')
            prop_name = split[0]
            prop_value = float(split[1])
            #设置自定义参数，浮点类型
            setattr(add_modifier, prop_name, prop_value)
    if prop_int != '':
        prop_int_list = prop_int.split(',')
        for prop in prop_int_list:
            split = prop.split('=')
            prop_name = split[0]
            prop_value = int(split[1])
            #设置自定义参数，浮点类型
            setattr(add_modifier, prop_name, prop_value)
    if prop_string != '':
        prop_string_list = prop_string.split(',')
        for prop in prop_string_list:
            split = prop.split('=')
            prop_name = split[0]
            prop_value = split[1]
            #设置自定义参数,文本类型
            setattr(add_modifier, prop_name, prop_value)


class Bar_Add_New_Modifier(Operator):
    bl_idname = "bar.add_new_modifier"
    bl_label = "Add New Modifier"
    bl_description = ""
    bl_options = {"REGISTER","UNDO"}

    name : bpy.props.StringProperty()
    prop_bool : bpy.props.StringProperty()
    prop_float : bpy.props.StringProperty()
    prop_int : bpy.props.StringProperty()
    prop_string : bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        name = self.name

        ob_modifiers = context.active_object.modifiers
        active_modifier = ob_modifiers.active
        
        if active_modifier is not None:
            #获取当前激活修改器位置
            active_modifier_name = active_modifier.name

            modifier_list = []
            for md in ob_modifiers:
                modifier_list.append(md.name)
            #添加修改器
            add = bpy.context.active_object.modifiers.new(name = '',type=name)
            add_name = add.name

            add_set_modifier_prop(self,context,add)

            #移动修改器到激活位置+1
            bpy.ops.object.modifier_move_to_index(
                modifier=add_name, 
                index=modifier_list.index(active_modifier_name)+1
                )
            modifier_list.clear()
        else:
            add = bpy.context.active_object.modifiers.new(name = '',type=name)

            add_set_modifier_prop(self,context,add)

        return {"FINISHED"}

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

    split = row.split(factor = 0.2)
    
    split_1 = split.operator('object.modifier_add', icon='MOD_TRIANGULATE',
                 text='三角化').type = 'TRIANGULATE'
    #------
    split_2 = split.row()

    split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.1").ratio = 0.1
    split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.3").ratio = 0.3
    split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.5").ratio = 0.5
    split_2.operator(Bar_Quick_Decimate.bl_idname, text="1").ratio = 1.0

# Modifier Bar
def costom_modifier_bar(self, context):
    col = self.layout.column(align=True)
    col.alignment = 'CENTER'
    col.scale_y = 0.9
    # ---------------------------- 1 Level --------------------------------
    row = col.row(align=True)
    row.operator('object.modifier_add', icon='GEOMETRY_NODES',
                 text='节点').type = 'NODES'
    row.operator('object.modifier_add', icon='MOD_SUBSURF',
                 text='细分').type = 'SUBSURF'

    row.operator('object.modifier_add', icon='MOD_SHRINKWRAP',
                 text='缩裹').type = 'SHRINKWRAP'

    # ----------------------------- 2 Level --------------------------------
    row = col.row(align=True)
    #倒角
    bevel = row.operator(Bar_Add_New_Modifier.bl_idname,icon = 'MOD_BEVEL', text='倒角')
    bevel.name = 'BEVEL'
    bevel.prop_bool = 'harden_normals=True,use_clamp_overlap=False'
    # bevel.prop_int = 'segments=2'
    #阵列
    row.operator('object.modifier_add',
                 icon='MOD_ARRAY', text='阵列').type = 'ARRAY'
    #置换
    if context.active_object.type == 'MESH':
        row.operator('object.modifier_add', icon='MOD_DISPLACE',
                     text='置换').type = 'DISPLACE'
    else:
        row.operator('pie.empty_operator', icon='ERROR', text='置换')

    # ------------------------------3 Level--------------------------------
    row = col.row(align=True)
    #镜像
    mirror = row.operator(Bar_Add_New_Modifier.bl_idname, icon='MOD_MIRROR', text='镜像')
    mirror.name = 'MIRROR'
    mirror.prop_bool = 'use_clip=True'
    #布尔
    if context.active_object.type == 'MESH':
        bool1 = row.operator(Bar_Add_New_Modifier.bl_idname,icon='MOD_BOOLEAN', text='布尔')
        bool1.name='BOOLEAN'
        bool1.prop_string = 'solver=FAST'
    else:
        row.operator('pie.empty_operator', icon='ERROR', text='布尔')
    #形变
    deform = row.operator(Bar_Add_New_Modifier.bl_idname, icon='MOD_SIMPLEDEFORM',text='形变')
    deform.name = 'SIMPLE_DEFORM'
    deform.prop_string = 'deform_method=BEND'

    # ------------------------------4 Level-------------------------------
    row = col.row(align=True)
    #厚度
    solidfy = row.operator(Bar_Add_New_Modifier.bl_idname, icon='MOD_SOLIDIFY',text='厚度')
    solidfy.name = 'SOLIDIFY'
    solidfy.prop_bool = 'use_even_offset=True'
    #焊接
    row.operator('object.modifier_add', icon='AUTOMERGE_OFF',text='焊接').type = 'WELD'
    #螺旋
    row.operator('object.modifier_add', icon='MOD_SCREW',
                 text='螺旋').type = 'SCREW'


classes = [
    Bar_Quick_Decimate,
    Bar_Add_New_Modifier,
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
