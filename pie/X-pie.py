import bpy
from bpy.types import Menu
from .utils import set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "KEY",
}


def verties_lenth(context):
    lenth = 0
    for vertex in context.active_object.data.vertices:
        if vertex.select == True:
            lenth += 1
    return lenth


class VIEW3D_PIE_MT_Bottom_X(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        if ob_mode == 'EDIT':
            ed_mode = context.tool_settings.mesh_select_mode
            col = pie.split().box().column(align=True)

            row = col.row(align=True)
            if ed_mode[0] == True:
                try:
                    row.operator(
                        'mesh.merge', text='首点', icon='DOT'
                    ).type = 'FIRST'
                    row.separator(factor=0.1)
                    row.operator('mesh.merge', text='中心').type = 'CENTER'
                    row.separator(factor=0.1)
                    row.operator(
                        'mesh.merge', text='末点', icon='DOT'
                    ).type = 'LAST'
                except TypeError:
                    row.operator('mesh.merge', text='中心').type = 'CENTER'
            else:
                sub = row.row()
                # sub.alignment = 'CENTER'
                sub.operator('mesh.merge', text='中心').type = 'CENTER'

            col.separator(factor=0.4)
            row = col.row()
            row.operator('mesh.merge', text='游标').type = 'CURSOR'
            row.operator('mesh.merge', text='塌陷').type = 'COLLAPSE'

            col.separator(factor=0.4)
            row = col.row()
            row.operator('mesh.remove_doubles', text='按间距合并')
            # 6 - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_x = 0.8

            row = col.row()
            row.operator('mesh.delete_loose')

            col.separator(factor=0.4)
            row = col.row()
            row.operator('mesh.decimate', text='精简几何体')
            row.operator('mesh.dissolve_degenerate', text='简并融并')
            row.operator('mesh.face_make_planar', text='平整表面')

            col.separator(factor=0.4)
            row = col.row()
            row.operator('mesh.vert_connect_nonplanar', text='拆分非平面')
            row.operator('mesh.vert_connect_concave', text='拆分凹面')
            row.operator('mesh.fill_holes', text='填充洞面')

            col.separator(factor=0.4)
            row = col.row()
            row.operator('mesh.dissolve_limited', text='有限融并')

            # 2 - BOTTOM
            pie.operator('mesh.edge_collapse', text='塌陷边面')
            # 8 - TOP
            pie.operator(
                'mesh.delete', text='仅面', icon='SNAP_FACE_CENTER'
            ).type = 'ONLY_FACE'
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.separator()
        elif ob_mode == 'EDIT':
                # 4 - LEFT
                pie.operator('object.move_to_collection')
                # 6 - RIGHT
                pie.separator()
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                pie.separator()
                # 7 - TOP - LEFT
                pie.separator()
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()

classes = [
    VIEW3D_PIE_MT_Bottom_X,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'X', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_X"
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
