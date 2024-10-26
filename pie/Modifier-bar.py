import bpy
from bpy.types import Context, Event, Menu, Operator

from ..utils import get_prefs
from .pie_utils import *

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
        "NUMBERS": ("segments", 1),
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
    "DECIMATE": {
        "DEFAULT_PROP": [("ratio", 0.5)],
        "ctrl": [("decimate_type", "UNSUBDIV"), ("iterations", 2)],
        "shift": [("decimate_type", "DISSOLVE"), ("angle_limit", 0.0174533)],
        "NUMBERS": ("ratio", 0.1),
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
    if active_object in objs:
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
                    setattr(new_mod, item_data[0], numbers.index(event.type_prev) * item_data[1])

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
    bl_label = get_pyfilename()
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


class PIE_Modifier_Profiling_Panel(bpy.types.Panel):
    """ """

    bl_label = "修改器-耗时统计"
    bl_idname = "SCENE_PT_modifier_profiling_PIE"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
    bl_options = {"DEFAULT_CLOSED", "HIDE_HEADER"}

    def draw(self, context):
        if get_prefs().modifier_profiling:
            draw_modifier_times(self, context)


def time_to_string(t):
    """Formats time in seconds to the nearest sensible unit."""
    units = {3600.0: "h", 60.0: "m", 1.0: "s", 0.001: "ms"}
    for factor in units.keys():
        if t >= factor:
            return f"{t/factor:.3g} {units[factor]}"
    if t >= 1e-4:
        return f"{t/factor:.3g} {units[factor]}"
    else:
        return f"<0.1 ms"


def draw_modifier_times(self, context):
    depsgraph = context.view_layer.depsgraph

    ob = context.object
    ob_eval = ob.evaluated_get(depsgraph)

    box = self.layout.box()
    times = []
    total = 0
    for mod_eval in ob_eval.modifiers:
        t = mod_eval.execution_time
        times += [t]
        total += t

    col_fl = box.column_flow(columns=2)
    col = col_fl.column(align=True)
    for mod_eval in ob_eval.modifiers:
        row = col.row()
        row.enabled = mod_eval.show_viewport
        row.label(text=f"{mod_eval.name}:")

    col = col_fl.column(align=True)
    for i, t in enumerate(times):
        row = col.row()
        row.enabled = ob_eval.modifiers[i].show_viewport
        row.alert = t >= 0.8 * max(times)
        row.label(text=time_to_string(t))

    row = box.column_flow()
    row.column().label(text=f"总计:")
    row.column().label(text=time_to_string(sum(times)))


# Modifier Bar
def costom_modifier_bar(self, context):
    col = self.layout.column(align=True)
    col.alignment = "CENTER"
    col.scale_y = 0.9

    # ---------------------------- 0 Level --------------------------------
    # row = col.row(align=True)
    # nodes = row.operator(id, icon="GEOMETRY_NODES", text="节点")
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

    # ------------------------------4 Level-------------------------------
    row = col.row(align=True)
    decimate = row.operator(id, icon="MOD_DECIM", text="精简")
    decimate.type = "DECIMATE"
    edge_split = row.operator(id, icon="MOD_EDGESPLIT", text="拆边")
    edge_split.type = "EDGE_SPLIT"
    triangulate = row.operator(id, icon="MOD_TRIANGULATE", text="三角化")
    triangulate.type = "TRIANGULATE"
    # lattice = row.operator(id, icon="MOD_LATTICE", text="晶格")
    # lattice.type = "LATTICE"


classes = [
    Bar_Quick_Decimate,
    Bar_Add_New_Modifier,
    PIE_PT_Bar_AddCustomModifier,
    PIE_Modifier_Profiling_Panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.DATA_PT_modifiers.prepend(costom_modifier_bar)
    # bpy.types.DATA_PT_modifiers.append(menu)  # 区别 prepend 和 append


def unregister():
    bpy.types.DATA_PT_modifiers.remove(costom_modifier_bar)
    # bpy.types.DATA_PT_modifiers.remove(menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
