import bpy
from bpy.types import Operator


class PIE_Custom_Scripts_EmptyToCollection(bpy.types.Operator):
    bl_idname = "pie.empty_to_collection"
    bl_label = "选择父子级到集合"
    bl_description = "将选择的空物体绑定的父子级创建到集合"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            name  = ob.name
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            bpy.data.objects[name].select_set(True)
            bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name=name)
        return {"FINISHED"}

class PIE_Custom_Scripts_CleanSameMatTex(bpy.types.Operator):
    bl_idname = "pie.clean_same_material_texture"
    bl_label = "清理同名材质槽贴图"
    bl_description = "清理.001类似的材质和贴图.注意使用！"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        # return self.execute(context)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text="仅适用于导入模型！", icon="ERROR")

    def execute(self, context):
        import re
        selected_objects = bpy.context.selected_objects
        def change_mat(active_mat_name):
            if "." in active_mat_name:
                orgin_mat = active_mat_name.split('.',1)[0]
                bpy.ops.view3d.materialutilities_replace_material(
                matorg= active_mat_name,
                matrep=orgin_mat, all_objects=True, update_selection=False)
        # 遍历每个选中的物体
        for obj in selected_objects:
            # 将当前物体设置为激活物体
            bpy.context.view_layer.objects.active = obj
            active_object = bpy.context.active_object
            if active_object is not None and active_object.material_slots:
                print("Active object's material names:")
                # 遍历每个材质槽
                for slot in active_object.material_slots:
                    # 打印材质名称
                    if slot.material:  # 确保材质槽不为空
                        active_mat_name = slot.material.name
                        change_mat(active_mat_name)
        # 正则表达式，用于匹配以点号开头，后跟三个数字的模式
        pattern = re.compile(r"\.\d{3}$")
        # 遍历所有的贴图
        for image in bpy.data.images:
            # 使用正则表达式搜索后缀
            new_name = re.sub(pattern, '', image.name)
            # 如果名称被修改，则更新贴图名称
            if new_name != image.name:
                image.name = new_name

        return {"FINISHED"}

class PIE_Quick_RedHaloM2B(bpy.types.Operator):
    bl_idname = "pie.quick_redhalom2b"
    bl_label = "导入Max导出物体"
    bl_description = "快速通过RedHaloM2B插件导入再MAX中已选择导出的物体"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            bpy.ops.redhalo.maxfilebrower(onlyImport = True)
        except:
            pass
        return {"FINISHED"}


classes = [
    PIE_Custom_Scripts_EmptyToCollection,
    PIE_Custom_Scripts_CleanSameMatTex,
    PIE_Quick_RedHaloM2B,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()