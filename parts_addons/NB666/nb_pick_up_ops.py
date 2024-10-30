import bpy


class NB_Pick_Up_Operator(bpy.types.Operator):
    bl_idname = "object.pick_up"
    bl_label = "标记拿起(1)"
    bl_description = "标记拿起(1)"
    bl_options = {"REGISTER", "UNDO"}

    #    @classmethod
    #    def poll(cls, context):
    #        return context.area.type == 'DOPESHEET_EDITOR' and context.area.spaces.active.mode == 'TIMELINE'
    #
    def execute(self, context):
        # 获取当前场景
        scene = bpy.context.scene

        # 获取当前帧
        current_frame = scene.frame_current

        # 在当前帧创建一个名为"0"的标记
        scene.timeline_markers.new(name="1", frame=current_frame)
        bpy.ops.ed.undo_push(message="NB")
        return {"FINISHED"}


classes = (NB_Pick_Up_Operator,)

addon_keymaps = []


## 注册插件
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add keymap entry
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Dopesheet", space_type="DOPESHEET_EDITOR")
        kmi = km.keymap_items.new(NB_Pick_Up_Operator.bl_idname, type="ONE", value="PRESS", ctrl=False, shift=False)
        addon_keymaps.append((km, kmi))


## 注销插件
def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    try:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    except:
        pass
    addon_keymaps.clear()


## 在启动时注册插件
if __name__ == "__main__":
    register()
