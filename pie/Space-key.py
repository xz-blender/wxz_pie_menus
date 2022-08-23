import bpy
from bpy.types import Operator, Menu
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


class PIE_Space_KEY(Operator):
    bl_idname = "pie.key_space"
    bl_label = submoduname
    bl_options = {"REGISTER"}

    def execute(self, context):
        print(context.area.ui_type)
        if context.area.ui_type == 'VIEW_3D':
            mode = context.object.mode
            if mode in ['OBJECT', 'EDIT']:
                bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
            elif mode in ['SCULPT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'VERTEX_PAINT']:
                bpy.ops.wm.tool_set_by_index(index=1)
        elif context.area.ui_type == 'IMAGE_EDITOR':
            bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
        elif context.area.ui_type in [
            'SEQUENCE_EDITOR',
            'CLIP_EDITOR',
            'DOPESHEET',
            'TIMELINE',
            'FCURVES',
            'DRIVERS',
            'NLA_EDITOR',
        ]:
            bpy.ops.screen.animation_play()
        return {"FINISHED"}


classes = [
    PIE_Space_KEY,
]


addon_keymaps = []

keymap_areas = [
    ('3D View', 'VIEW_3D'),
    ('SequencerCommon', 'SEQUENCE_EDITOR'),
    ('NLA Editor', 'NLA_EDITOR'),
    ('Graph Editor', 'GRAPH_EDITOR'),
    ('Dopesheet', 'DOPESHEET_EDITOR'),
    ('UV Editor', 'EMPTY'),
]


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    # KEY:
    for area in keymap_areas:
        km = addon.keymaps.new(name=area[0], space_type=area[1])  # ----视频序列播放器
        kmi = km.keymap_items.new(PIE_Space_KEY.bl_idname, 'SPACE', 'CLICK')  # space
        if area[0] == '3D View':  # shift-space
            kmi = km.keymap_items.new('screen.animation_play', 'SPACE', 'CLICK', shift=True)
        else:
            kmi = km.keymap_items.new(
                'screen.animation_play', 'SPACE', 'CLICK', shift=True
            ).properties.reverse = True  # shift-space
        addon_keymaps.append(km)


'''
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    # KEY:
    for area in keymap_areas:
        km = addon.keymaps.new(name=area[0], space_type=area[1])  # ----视频序列播放器
        kmi = km.keymap_items.new(PIE_Space_KEY.bl_idname, 'SPACE', 'CLICK')  # space
        if area[0] == '3D View':  # shift-space
            kmi = km.keymap_items.new('screen.animation_play', 'SPACE', 'CLICK', shift=True)
        else:
            kmi = km.keymap_items.new(
                'screen.animation_play', 'SPACE', 'CLICK', shift=True
            ).properties.reverse = True  # shift-space
        kmi = km.keymap_items.new('wm.call_menu_pie', 'SPACE', 'CLICK_DRAG', shift=True)  # 拖拽
        kmi.properties.name = "VIEW3D_PIE_MT_Space_KEY_shift"
        addon_keymaps.append(km)
'''


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
