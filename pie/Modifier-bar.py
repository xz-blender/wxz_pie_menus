import bpy
from bpy.types import Context, Event, Menu, Operator

from .utils import set_pie_ridius

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "Properties > Modifiers",
    "category": "BAR",
}

numbers = ("ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE")
modifier_props = {
    "SOLIDIFY": {
        "DEFAULT_PROP": [("use_even_offset", True)],
        "shift": [("offset", 0)],
        "alt": [("offset", -1)],
        "ctrl": [("offset", 1)],
    },
    "BEVEL": {
        "DEFAULT_PROP": [("segments", 1), ("use_clamp_overlap", False), ("harden_normals", True)],
        "shift": [("harden_normals", False), ("use_clamp_overlap", True)],
        "NUMBERS": ("segments"),
    },
    "ARRAY": {
        "DEFAULT_PROP": [("use_merge_vertices_cap", True)],
        "shift": [("use_constant_offset", True), ("use_relative_offset", False)],
        "X": [("relative_offset_displace", (1, 0, 0)), ("constant_offset_displace", (1, 0, 0))],
        "Y": [("relative_offset_displace", (0, 1, 0)), ("constant_offset_displace", (0, 1, 0))],
        "Z": [("relative_offset_displace", (0, 0, 1)), ("constant_offset_displace", (0, 0, 1))],
    },
    "MIRROR": {
        "DEFAULT_PROP": [("use_clip", True)],
        "X": [("use_axis", (True, False, False))],
        "Y": [("use_axis", (False, True, False))],
        "Z": [("use_axis", (False, False, True))],
    },
    "SIMPLE_DEFORM": {
        "DEFAULT_PROP": [("deform_method", "BEND")],
        "shift": [("deform_method", "TWIST")],
        "X": [("deform_axis", "X")],
        "Y": [("deform_axis", "Y")],
        "Z": [("deform_axis", "Z")],
    },
    "SCREW": {
        "DEFAULT_PROP": [("use_normal_calculate", True), ("use_merge_vertices", True)],
        "shift": [("angle", 0), ("steps", 1), ("render_steps", 1)],
        "X": [("axis", "X")],
        "Y": [("axis", "Y")],
        "Z": [("axis", "Z")],
    },
    "BOOLEAN": {
        "DEFAULT_PROP": [("solver", "FAST")],
        "shift": [("operation", "UNION")],
        "ctrl": [("operation", "INTERSECT")],
    },
}


def add_set_modifier_prop(self, context, add_modifier):
    prop_bool = self.prop_bool
    prop_float = self.prop_float
    prop_int = self.prop_int
    prop_string = self.prop_string
    # 转化自定义修改器参数
    if prop_bool != "":
        prop_bool_list = prop_bool.split(",")
        for prop in prop_bool_list:
            split = prop.split("=")
            prop_name = split[0]
            prop_value = split[1] == "True"
            # 设置自定义参数，布尔类型
            setattr(add_modifier, prop_name, prop_value)
    elif prop_float != "":
        prop_float_list = prop_float.split(",")
        for prop in prop_float_list:
            split = prop.split("=")
            prop_name = split[0]
            prop_value = float(split[1])
            # 设置自定义参数，浮点类型
            setattr(add_modifier, prop_name, prop_value)
    elif prop_int != "":
        prop_int_list = prop_int.split(",")
        for prop in prop_int_list:
            split = prop.split("=")
            prop_name = split[0]
            prop_value = int(split[1])
            # 设置自定义参数，浮点类型
            setattr(add_modifier, prop_name, prop_value)
    elif prop_string != "":
        prop_string_list = prop_string.split(",")
        for prop in prop_string_list:
            split = prop.split("=")
            prop_name = split[0]
            prop_value = split[1]
            # 设置自定义参数,文本类型
            setattr(add_modifier, prop_name, prop_value)


def set_default_props(self):
    self.prop_bool = ""
    self.prop_float = ""
    self.prop_int = ""
    self.prop_string = ""


def add_custom_boolean(context):
    objs = context.selected_objects
    active_object = context.active_object
    active_modifier = active_object.modifiers.active
    if len(objs) > 1:
        # 获取当前激活的物体
        # 创建一个新的列表，排除激活的物体
        filtered_objects = [obj for obj in objs if obj != active_object]
        if len(filtered_objects) > 1:
            # 获取当前激活物体所在的集合
            if active_object.users_collection:
                active_collection = active_object.users_collection[0]
            # 创建一个新的集合
            new_collection_name = active_object.name + "_Boolean"
            new_collection = bpy.data.collections.new(name=new_collection_name)
            # 将新的集合链接到当前场景
            if active_object.users_collection:
                active_collection.children.link(new_collection)
            else:
                context.scene.collection.children.link(new_collection)
            # 将排除激活物体后的选择物体移动到新的集合
            for obj in filtered_objects:
                obj.display_type = "WIRE"
                # 将物体从原来的集合中移除
                for collection in obj.users_collection:
                    collection.objects.unlink(obj)
                # 将物体添加到新的集合
                new_collection.objects.link(obj)

            active_modifier.solver = "FAST"
            active_modifier.operand_type = "COLLECTION"
            active_modifier.collection = new_collection
        elif len(filtered_objects) == 1:
            object = filtered_objects[0]
            object.display_type = "WIRE"
            active_modifier.solver = "FAST"
            active_modifier.object = object


class PIE_PT_Bar_AddCustomModifier(Operator):
    bl_idname = "bar.add_custom_prop_modifier"
    bl_label = "测试修改器"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        ob_modifiers = context.active_object.modifiers
        active_modifier = ob_modifiers.active

        new_mod = bpy.context.active_object.modifiers.new(name="", type=self.type)
        # print([d for d in dir(event.type)])
        # print(event.type_prev)
        # print(event.type_recast)
        if self.type in modifier_props:
            for item_name, item_data in modifier_props[self.type].items():
                if item_name == "DEFAULT_PROP":
                    for props in item_data:
                        setattr(new_mod, props[0], props[1])
                elif event.type_prev == item_name:
                    for props in item_data:
                        setattr(new_mod, props[0], props[1])
                elif item_name not in ["X", "Y", "Z", "NUMBERS"]:
                    if getattr(event, item_name):
                        for props in item_data:
                            setattr(new_mod, props[0], props[1])
                elif item_name == "NUMBERS" and event.type_prev in numbers:
                    setattr(new_mod, item_data, numbers.index(event.type_prev))

        if self.type == "BOOLEAN":
            add_custom_boolean(context)

        if active_modifier is not None:
            modifier_list = [md.name for md in ob_modifiers]
            # 移动修改器到激活位置+1
            bpy.ops.object.modifier_move_to_index(
                modifier=new_mod.name, index=modifier_list.index(active_modifier.name) + 1
            )
            modifier_list.clear()

        return {"FINISHED"}


id = PIE_PT_Bar_AddCustomModifier.bl_idname


class Bar_Add_New_Modifier(Operator):
    bl_idname = "bar.add_new_modifier"
    bl_label = "Add New Modifier"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    name: bpy.props.StringProperty()  # type: ignore
    prop_bool: bpy.props.StringProperty()  # type: ignore
    prop_float: bpy.props.StringProperty()  # type: ignore
    prop_int: bpy.props.StringProperty()  # type: ignore
    prop_string: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context: Context) -> bool:
        return super().poll(context)

    def execute(self, context):
        name = self.name
        ob_modifiers = context.active_object.modifiers
        active_modifier = ob_modifiers.active

        if active_modifier is not None:
            # 获取当前激活修改器位置
            active_modifier_name = active_modifier.name

            modifier_list = []
            for md in ob_modifiers:
                modifier_list.append(md.name)
            # 添加修改器
            add = bpy.context.active_object.modifiers.new(name="", type=name)
            add_name = add.name

            add_set_modifier_prop(self, context, add)
            set_default_props(self)

            # 移动修改器到激活位置+1
            bpy.ops.object.modifier_move_to_index(
                modifier=add_name, index=modifier_list.index(active_modifier_name) + 1
            )
            modifier_list.clear()
        else:
            add = bpy.context.active_object.modifiers.new(name="", type=name)

            add_set_modifier_prop(self, context, add)
            set_default_props(self)

        return {"FINISHED"}

    # def invoke(self, context, event):
    #     if event.ctrl:
    #         print("!!!!!!")
    #     return self.execute(context)


class Bar_Quick_Decimate(Operator):
    bl_idname = "bar.quick_decimate"
    bl_label = submoduname
    bl_options = {"REGISTER", "UNDO"}

    ratio: bpy.props.FloatProperty(name="Decimate Ratio", min=0, max=1, default=1)  # type: ignore
    iterations: bpy.props.IntProperty(name="Unsubdiv Iterations", default=2)  # type: ignore
    de_type: bpy.props.StringProperty(name="Decimate Type", default="COLLAPSE")  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ratio = self.ratio
        de_type = self.de_type
        iterations = self.iterations

        if context.selected_objects:
            for obj in context.selected_objects:
                context.view_layer.objects.active = obj

                md_name = "精简-%.3s" % ratio
                md = obj.modifiers.new(name=md_name, type="DECIMATE")
                md.decimate_type = de_type
                if de_type == "UNSUBDIV":
                    md.iterations = iterations
                else:
                    md.ratio = ratio

            self.report({"INFO"}, md_name)
        else:
            self.report({"INFO"}, "没有选择物体")

        return {"FINISHED"}


# Menus #
def menu(self, context):
    col = self.layout.column(align=True)
    col.alignment = "CENTER"
    col.scale_y = 0.9
    row = col.row(align=True)

    split = row.split(factor=0.2)

    split_1 = split.operator("object.modifier_add", icon="MOD_TRIANGULATE", text="三角化").type = "TRIANGULATE"
    # ------
    split_2 = split.row()

    L1 = split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.1")
    L1.de_type = "COLLAPSE"
    L1.ratio = 0.1

    L2 = split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.2")
    L2.de_type = "COLLAPSE"
    L2.ratio = 0.2

    L3 = split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.3")
    L3.de_type = "COLLAPSE"
    L3.ratio = 0.3

    L4 = split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.4")
    L4.de_type = "COLLAPSE"
    L4.ratio = 0.4

    L5 = split_2.operator(Bar_Quick_Decimate.bl_idname, text="0.5")
    L5.de_type = "COLLAPSE"
    L5.ratio = 0.5

    L0 = split_2.operator(Bar_Quick_Decimate.bl_idname, text="反细分")
    L0.de_type = "UNSUBDIV"
    L0.iterations = 2


# Modifier Bar
def costom_modifier_bar(self, context):
    col = self.layout.column(align=True)
    col.alignment = "CENTER"
    col.scale_y = 0.9

    # ---------------------------- 1 Level --------------------------------
    row = col.row(align=True)
    nodes = row.operator(id, icon="GEOMETRY_NODES", text="节点")
    nodes.type = "NODES"
    subs = row.operator(id, icon="MOD_SUBSURF", text="细分")
    subs.type = "SUBSURF"
    shirink = row.operator(id, icon="MOD_SHRINKWRAP", text="缩裹")
    shirink.type = "SHRINKWRAP"

    # ----------------------------- 2 Level --------------------------------
    row = col.row(align=True)
    bevel = row.operator(id, icon="MOD_BEVEL", text="倒角")
    bevel.type = "BEVEL"
    array = row.operator(id, icon="MOD_ARRAY", text="阵列")
    array.type = "ARRAY"
    if context.active_object.type == "MESH":
        displace = row.operator(id, icon="MOD_DISPLACE", text="置换")
        displace.type = "DISPLACE"
    else:
        row.operator("pie.empty_operator", icon="ERROR", text="置换")

    # ------------------------------3 Level--------------------------------
    row = col.row(align=True)
    mirror = row.operator(id, icon="MOD_MIRROR", text="镜像")
    mirror.type = "MIRROR"
    if context.active_object.type == "MESH":
        bool_mod = row.operator(id, icon="MOD_BOOLEAN", text="布尔")
        bool_mod.type = "BOOLEAN"
    else:
        row.operator("pie.empty_operator", icon="ERROR", text="布尔")
    deform = row.operator(id, icon="MOD_SIMPLEDEFORM", text="形变")
    deform.type = "SIMPLE_DEFORM"

    # ------------------------------4 Level-------------------------------
    row = col.row(align=True)
    solidfy = row.operator(id, icon="MOD_SOLIDIFY", text="厚度")
    solidfy.type = "SOLIDIFY"
    weld = row.operator(id, icon="AUTOMERGE_OFF", text="焊接")
    weld.type = "WELD"
    weld = row.operator(id, icon="MOD_SCREW", text="螺旋")
    weld.type = "SCREW"


classes = [
    Bar_Quick_Decimate,
    Bar_Add_New_Modifier,
    PIE_PT_Bar_AddCustomModifier,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.DATA_PT_modifiers.prepend(costom_modifier_bar)
    bpy.types.DATA_PT_modifiers.append(menu)  # 区别 prepend 和 append


def unregister():
    bpy.types.DATA_PT_modifiers.remove(costom_modifier_bar)
    bpy.types.DATA_PT_modifiers.remove(menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
