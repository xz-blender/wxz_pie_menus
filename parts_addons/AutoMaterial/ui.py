import bpy


def Material_handle_Panel(self, context):
    """options for fast naming and setting materials color"""
    layout = self.layout.box()
    layout.use_property_split = False
    # layout.label(text="设置颜色:")

    split = layout.split(factor=0.5, align=True)
    split.operator(
        "materials.viewport_color_from_node", text="节点色 -> 视图色", icon="RESTRICT_VIEW_OFF"
    ).from_viewport = False
    split.operator("materials.viewport_color_from_node", text="视图色 -> 节点色", icon="NODE_SEL").from_viewport = True

    layout = self.layout.box()
    layout.use_property_split = False
    row = layout.row()
    row.label(text="自动重命名:")
    # row = layout.row()
    row.prop(context.scene, "mat_change_multiple", text="所有材质槽")
    row.prop(context.scene, "only_unnamed", text="仅未命名材质")
    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator("materials.auto_name_material", text="通过-视图色-重命名", icon="RESTRICT_COLOR_ON").viewport = True
    row.operator("materials.auto_name_material", text="通过-节点色-重命名", icon="NODETREE").viewport = False

    row = col.row()
    row.operator("materials.convert_clip_color_to_name", text="按名称替换剪贴板颜色", icon="COLOR")


def GP_Material_handle_Panel(self, context):
    layout = self.layout
    layout.use_property_split = True
    # split = layout.split(factor=0.5, align=False)
    split = layout.split(factor=0.25, align=False)
    split.label(text="自动重命名:")
    split.prop(context.scene, "mat_change_multiple", text="重命名所有槽")
    layout.operator("materials.auto_name_material", text="从颜色重命名", icon="RESTRICT_COLOR_ON").viewport = True


def register():
    bpy.types.MATERIAL_PT_viewport.append(Material_handle_Panel)
    if bpy.app.version >= (2, 93, 0):
        bpy.types.MATERIAL_PT_gpencil_settings.append(GP_Material_handle_Panel)
    else:
        bpy.types.MATERIAL_PT_gpencil_options.append(GP_Material_handle_Panel)


def unregister():
    bpy.types.MATERIAL_PT_viewport.remove(Material_handle_Panel)
    if bpy.app.version >= (2, 93, 0):
        bpy.types.MATERIAL_PT_gpencil_settings.remove(GP_Material_handle_Panel)
    else:
        bpy.types.MATERIAL_PT_gpencil_options.remove(GP_Material_handle_Panel)
