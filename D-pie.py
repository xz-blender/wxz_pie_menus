import bpy
from bpy.types import Menu, Operator
from .utils import set_pie_ridius  # check_rely_addon, rely_addons,

bl_info = {
    "name": "D-PIE",
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "Interface",
}


class VIEW3D_PIE_MT_Bottom_D(Menu):
    bl_label = "D"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context)

        # 4 - LEFT
        sp = pie.split()
        sp.scale_x = 1.1

        sp = sp.split(factor=0.18)
        col_l = sp.column()
        row_l = col_l.row()
        row_l.label(text='坐')
        row_l = col_l.row()
        row_l.label(text='标')
        row_l = col_l.row()
        row_l.label(text='系')

        col = sp.box().column()
        row = col.row()
        row.operator(
            "pie.transform_orientation", text="万象", icon='ORIENTATION_GIMBAL'
        ).axis = 'GIMBAL'
        row = col.row()
        row.operator(
            "pie.transform_orientation", text="视图", icon='ORIENTATION_VIEW'
        ).axis = 'VIEW'
        row = col.row()
        row.operator(
            "pie.transform_orientation", text="游标", icon='ORIENTATION_CURSOR'
        ).axis = 'CURSOR'
        # 6 - RIGHT
        sp = pie.split()

        sp = sp.split(factor=0.8)
        col = sp.box().column()
        row = col.row()
        row.operator(
            "pie.transform_pivot", text="质心点", icon='PIVOT_MEDIAN'
        ).pivot = 'MEDIAN_POINT'
        row = col.row()
        row.operator(
            "pie.transform_pivot", text="活动项", icon='PIVOT_ACTIVE'
        ).pivot = 'ACTIVE_ELEMENT'

        col_r = sp.column()
        row = col_r.row()
        row.label(text='轴')
        row = col_r.row()
        row.label(text='心')
        row = col_r.row()
        row.label(text='点')
        # 2 - BOTTOM
        pie.operator(
            "pie.transform_pivot", text="各自原点", icon='PIVOT_INDIVIDUAL'
        ).pivot = 'INDIVIDUAL_ORIGINS'
        # 8 - TOP
        pie.operator(
            "pie.transform_orientation", text="法向", icon='ORIENTATION_NORMAL'
        ).axis = 'NORMAL'
        # 7 - TOP - LEFT
        pie.operator(
            "pie.transform_orientation", text="全局", icon='ORIENTATION_GLOBAL'
        ).axis = 'GLOBAL'
        # 9 - TOP - RIGHT
        pie.operator(
            "pie.transform_orientation", text="局部", icon='ORIENTATION_LOCAL'
        ).axis = 'LOCAL'
        # 1 - BOTTOM - LEFT
        pie.operator(
            "pie.transform_pivot", text="边界框", icon='PIVOT_BOUNDBOX'
        ).pivot = 'BOUNDING_BOX_CENTER'
        # 3 - BOTTOM - RIGHT
        pie.operator(
            "pie.transform_pivot", text="游标", icon='PIVOT_CURSOR'
        ).pivot = 'CURSOR'


class VIEW3D_PIE_MT_Transform_Orientation(Operator):
    bl_idname = "pie.transform_orientation"
    bl_label = ""

    axis: bpy.props.StringProperty(name="Axis", default='GLOBAL')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.transform_orientation_slots[0].type = '%s' % (
            self.axis
        )
        return {"FINISHED"}


class VIEW3D_PIE_MT_Transform_Pivot(Operator):
    bl_idname = "pie.transform_pivot"
    bl_label = ""

    pivot: bpy.props.StringProperty(name="Pivot", default='BOUNDING_BOX_CENTER')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.transform_pivot_point = '%s' % (
            self.pivot
        )
        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_D,
    VIEW3D_PIE_MT_Transform_Orientation,
    VIEW3D_PIE_MT_Transform_Pivot,
]


addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'D', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_D"
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_D")
