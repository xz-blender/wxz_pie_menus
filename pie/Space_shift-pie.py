import bpy
from bpy.types import Operator, Menu
from .utils import set_pie_ridius, change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "KEY",
}


class VIEW3D_PIE_MT_Space_KEY_shift(Menu):
    bl_label = submoduname

    def draw(self, context):
        pie = self.layout.menu_pie()

        set_pie_ridius(context, 100)

        # print(context.area.type)
        # if context.area.type in [
        #     'VIEW_3D',
        #     'SEQUENCE_EDITOR',
        #     'CLIP_EDITOR',
        #     'DOPESHEET',
        #     'TIMELINE',
        #     'FCURVES',
        #     'DRIVERS',
        #     'NLA_EDITOR',
        #     'UV',
        #     'IMAGE_EDITOR',
        # ]:

        # 4 - LEFT
        pie.operator('screen.frame_jump', text='首帧',
                     icon='REW').end = False
        # 6 - RIGHT
        pie.operator('screen.frame_jump', text='末帧', icon='FF').end = True
        # 2 - BOTTOM
        pie.operator('screen.keyframe_jump', text='下一关键帧',
                     icon='NEXT_KEYFRAME').next = True
        # 8 - TOP
        pie.operator('screen.keyframe_jump', text='上一关键帧',
                     icon='PREV_KEYFRAME').next = False
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


classes = [
    VIEW3D_PIE_MT_Space_KEY_shift,
]


addon_keymaps = []

keymap_areas = [
    ('3D View', 'VIEW_3D'),
    ('SequencerCommon', 'SEQUENCE_EDITOR'),
    ('NLA Editor', 'NLA_EDITOR'),
    ('Graph Editor', 'GRAPH_EDITOR'),
    ('Dopesheet', 'DOPESHEET_EDITOR'),
    ('UV Editor', 'IMAGE_EDITOR'),
    ('Image', 'IMAGE_EDITOR'),
]


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        '3D View',
        'Graph Editor',
        'Dopesheet',
        'NLA Editor',
        'Clip',
        'Node Editor',
        'Sequencer',
        'Screen',
    ]
    for area in space_name:
        km = addon.keymaps.new(name=area)
        kmi = km.keymap_items.new(
            "wm.call_menu_pie", 'SPACE', 'CLICK_DRAG', shift=True)
        kmi.properties.name = "VIEW3D_PIE_MT_Space_KEY_shift"
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
