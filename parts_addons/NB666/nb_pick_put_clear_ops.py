import bpy



class NB_Pick_Put_Clear_Operator(bpy.types.Operator):
    bl_idname = "object.pick_put_clear"
    bl_label = "清除标记"
    bl_description = "清除标记"
    bl_options ={"REGISTER","UNDO"}
    


        
    def execute(self, context):

        # 获取当前场景
        scene = bpy.context.scene

        # 要删除的标记名称列表
        names_to_remove = ["0", "1"]

        # 遍历所有标记并删除名为"0"或"1"的标记
        markers_to_remove = [marker for marker in scene.timeline_markers if marker.name in names_to_remove]
        for marker in markers_to_remove:
            scene.timeline_markers.remove(marker)

        print(f"已删除 {len(markers_to_remove)} 个名为'0'或'1'的标记。")
        bpy.ops.ed.undo_push(message="NB")
        return {"FINISHED"}








classes=(
NB_Pick_Put_Clear_Operator,
)

## 注册插件
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

## 注销插件
def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

## 在启动时注册插件
if __name__ == "__main__":
    register()






