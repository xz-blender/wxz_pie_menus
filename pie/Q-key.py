import os
import bpy
from bpy.types import Menu, Operator

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Interface",
}


class PIE_MT_Bottom_Q_favorite(Menu):
    bl_idname = 'PIE_MT_Bottom_Q_favorite'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.alignment = 'CENTER'
        layout.use_property_decorate = True
        layout.use_property_split = True

        split = layout.split()
        col = split.column()

        col.menu_contents("SCREEN_MT_user_menu")

        col.separator()

        split = layout.split()
        col = split.column()
        # col.label(text="自定工具集")
        col.operator('text.run_script', text='运行脚本', icon='PLAY')

        # col.separator()

        # col.label(text="工具集二")
        # col.operator("view3d.view_axis", text="2").type = 'FRONT'


class PIE_Q_key(Operator):
    bl_idname = "pie.q_key"
    bl_label = submoduname
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob_mode = context.object.mode
        ob_type = context.object.type
        area_type = context.area.type

        if area_type == 'VIEW_3D':
            if ob_mode == 'OBJECT':
                bpy.ops.wm.call_menu(name='PIE_MT_Bottom_Q_favorite')
            elif ob_mode == 'EDIT':
                if ob_type == 'MESH':
                    bpy.ops.mesh.select_linked_pick('INVOKE_DEFAULT')
                elif ob_type == 'CURVE':
                    bpy.ops.curve.select_linked_pick('INVOKE_DEFAULT')
                elif ob_type == 'ARMATURE':
                    bpy.ops.armature.select_linked_pick('INVOKE_DEFAULT')
            elif ob_mode == 'EDIT_GPENCIL':
                bpy.ops.gpencil.select_linked('INVOKE_DEFAULT')
                #     bpy.ops.gpencil.select_alternate('INVOKE_DEFAULT')   shift
        elif area_type == 'IMAGE_EDITOR':
            bpy.ops.uv.select_linked_pick('INVOKE_DEFAULT', extend=True)

        return {"FINISHED"}


class PIE_Q_key_shift(Operator):
    bl_idname = "pie.q_key_shift"
    bl_label = submoduname
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob_mode = context.object.mode
        ob_type = context.object.type
        area_type = context.area.type

        if area_type == 'VIEW_3D':
            if ob_mode == 'OBJECT':
                bpy.ops.object.select_linked('INVOKE_DEFAULT')
            if ob_mode == 'EDIT':
                if ob_type == 'MESH':
                    bpy.ops.mesh.select_linked_pick('INVOKE_DEFAULT', deselect=True)
                elif ob_type == 'CURVE':
                    bpy.ops.curve.select_linked_pick('INVOKE_DEFAULT', deselect=True)
                elif ob_type == 'ARMATURE':
                    bpy.ops.armature.select_linked_pick('INVOKE_DEFAULT', deselect=True)
            elif ob_mode == 'SCULPT':
                # 当您尝试调用它时，执行上下文是 EXEC_DEFAULT，但它只支持 INVOKE_DEFAULT。
                bpy.ops.object.transfer_mode('INVOKE_DEFAULT')
            elif ob_mode == 'EDIT_GPENCIL':
                if self.gpencil_seselect_linkes_toggle == True:
                    bpy.ops.gpencil.select_alternate('INVOKE_DEFAULT')
        elif area_type == 'IMAGE_EDITOR':
            print('UVyes')
            bpy.ops.uv.select_linked_pick('INVOKE_DEFAULT', extend=True, deselect=True)

        return {"FINISHED"}


class PIE_Q_key_ctrl(Operator):
    bl_idname = "pie.q_key_shift"
    bl_label = submoduname
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ob_mode = context.object.mode
        ob_type = context.object.type
        area_type = context.area.type
        if area_type == 'VIEW_3D':
            if ob_mode == 'OBJECT':
                bpy.ops.wm.call_menu(name='VIEW3D_MT_make_links')

        return {"FINISHED"}


classes = [
    PIE_MT_Bottom_Q_favorite,
    PIE_Q_key,
    PIE_Q_key_shift,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("pie.q_key", 'Q', 'CLICK')
    kmi = km.keymap_items.new("pie.q_key_shift", 'Q', 'CLICK', shift=True)
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.q_key", 'Q', 'CLICK')
    kmi = km.keymap_items.new("pie.q_key_shift", 'Q', 'CLICK', shift=True)
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("wm.call_menu", 'Q', 'CLICK', ctrl=True)
    kmi.properties.name = 'VIEW3D_MT_make_links'
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="UV Editor")
    kmi = km.keymap_items.new("pie.q_key", 'Q', 'CLICK')
    kmi = km.keymap_items.new("pie.q_key_shift", 'Q', 'CLICK', shift=True)
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()

#     bpy.ops.wm.call_menu(name="PIE_MT_Bottom_Q_favorite")
