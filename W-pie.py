import bpy
from bpy.types import Menu, Operator
from.utils import check_rely_addon, rely_addons

bl_info = {
    "name": "W-PIE",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Interface"}


class VIEW3D_PIE_MT_Bottom_W(Menu):
    bl_label = "W"

    def draw(self, context):

        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        # addon1: "Modifier Tools"
        adname = rely_addons[3][0]
        addon1 = check_rely_addon(adname, rely_addons[3][1])

        ob_type = context.object.type
        ob_mode = context.object.mode

        # 4 - LEFT
        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        if ob_mode == 'OBJECT':
            pie.prop(bpy.context.scene.tool_settings,
                     'use_transform_data_origin', text='仅原点')
        else:
            pie.separator()
        # 8 - TOP
        if ob_mode == 'EDIT':
            pie.prop(bpy.context.scene.tool_settings,
                     'use_proportional_edit', text='衰减编辑网格')
        elif ob_mode == 'OBJECT':
            pie.prop(bpy.context.scene.tool_settings,
                     'use_proportional_edit_objects', text='衰减编辑物体')
        else:
            pie.separator()
        # 7 - TOP - LEFT
        if addon1 == '2':
            pie.operator('pie.empty_operator', text='未找到"%s"插件!' % (adname))
        elif addon1 == '0':
            pie.operator('pie.empty_operator', text='启用"%s"插件!' % (adname))
        elif addon1 == '1':
            if bool(context.object.modifiers) == False:
                pie.operator('pie.empty_operator', text='没有任何修改器!')
            else:
                pie.operator('object.toggle_apply_modifiers_view',
                             text='显示/隐藏所有修改器', icon='MODIFIER')

        # 9 - TOP - RIGHT
        col = pie.column(align=True)
        if ob_mode == 'EDIT':
            row = col.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 2
            row.scale_y = 1.3
            row.prop(bpy.context.scene.tool_settings,
                     'use_proportional_connected', icon='PROP_PROJECTED', icon_only=True)
            row.separator(factor=0.1)
            row.prop(bpy.context.scene.tool_settings, 'use_proportional_projected',
                     icon='RESTRICT_VIEW_OFF', icon_only=True)
        # -
            col.separator(factor=0.4)
        # -
        row = col.row(align=True)
        row.alignment = "CENTER"
        row.scale_x = 1.3
        row.scale_y = 1.2
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='SMOOTHCURVE').mode = 'SMOOOTH'
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='SPHERECURVE').mode = 'SPHERE'
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='ROOTCURVE').mode = 'ROOT'
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='INVERSESQUARECURVE').mode = 'INVERSE_SQUARE'
        # -
        row = col.row(align=True)
        row.alignment = "CENTER"
        row.scale_x = 1.3
        row.scale_y = 1.2
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='SHARPCURVE').mode = 'SHARP'
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='LINCURVE').mode = 'LINEAR'
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='NOCURVE').mode = 'CONSTANT'
        row.operator(Proportional_Edit_Falloff.bl_idname,
                     icon='RNDCURVE').mode = 'RANDOM'

        # 1 - BOTTOM - LEFT
        if ob_mode == 'OBJECT':
            pie.prop(bpy.context.scene.tool_settings,
                     'use_transform_pivot_point_align', text='仅位置')
        else:
            pie.separator()
        # 3 - BOTTOM - RIGHT
        if ob_mode == 'OBJECT':
            pie.prop(bpy.context.scene.tool_settings,
                     'use_transform_skip_children', text='仅父级')
        else:
            pie.separator()


class Proportional_Edit_Falloff(Operator):
    bl_idname = "pie.proportional_edit_falloff"
    bl_label = ""
    bl_description = ""
    bl_options = {"REGISTER"}

    mode: bpy.props.StringProperty(name="Mode")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.proportional_edit_falloff = '%s' % (
            self.mode)
        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_W,
    Proportional_Edit_Falloff,

]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie",  'W', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_W"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_W")
