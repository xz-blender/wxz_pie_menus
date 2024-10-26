import bpy
from bpy.types import Menu, Operator, Panel

from .pie_utils import *


class OUTLINER_PIE_MT_Bottom_A(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius(20)

        pie.operator("outliner.show_one_level", icon="REMOVE", text="").open = False
        # 6 - RIGHT
        pie.operator("outliner.show_one_level", icon="ADD", text="")
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


class OUTLINER_PIE_MT_Bottom_X(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius(20)

        pie.separator()
        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.operator("pie.remove_empty_collection", icon="TRASH", text="空集合")
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


class Collection_Enable_Toggle(Operator):
    bl_idname = "pie.toggle_collection"
    bl_label = "打开/关闭选择的集合"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "OUTLINER"

    def execute(self, context):
        collection_selected_name_list = []
        area = next(area for area in bpy.context.window.screen.areas if area.type == "OUTLINER")
        with bpy.context.temp_override(
            window=bpy.context.window,
            area=area,
            region=next(region for region in area.regions if region.type == "WINDOW"),
            screen=bpy.context.window.screen,
        ):
            for collection in context.selected_ids:
                collection_selected_name_list.append(collection.name)

        def all_layer_collections(view_layer):
            stack = [view_layer.layer_collection]
            while stack:
                lc = stack.pop()
                yield lc
                stack.extend(lc.children)

        print("col_list:", collection_selected_name_list)
        if collection_selected_name_list != []:
            for collection_name in collection_selected_name_list:
                view_layer = bpy.context.scene.view_layers.get(bpy.context.view_layer.name, None)
                if view_layer:
                    for lc in all_layer_collections(view_layer):
                        if lc.collection.name == collection_name:
                            if lc.exclude == True:
                                lc.exclude = False
                                pass
                            elif lc.exclude == False:
                                lc.exclude = True
                        # for l in dir(lc):
                        #     print("dir______:", l)
        return {"FINISHED"}


class PIE_Collection_Remove_Empty(Operator):
    bl_idname = "pie.remove_empty_collection"
    bl_label = "删除空集合"
    bl_description = "删除空集合"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for eachCol in bpy.data.collections:
            if len(eachCol.all_objects) == 0:
                bpy.data.collections.remove(eachCol)
        return {"FINISHED"}


classes = [
    OUTLINER_PIE_MT_Bottom_A,
    Collection_Enable_Toggle,
    PIE_Collection_Remove_Empty,
    OUTLINER_PIE_MT_Bottom_X,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Outliner", space_type="OUTLINER")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG")
    kmi.properties.name = "OUTLINER_PIE_MT_Bottom_A"
    kmi = km.keymap_items.new("wm.call_menu_pie", "X", "CLICK_DRAG")
    kmi.properties.name = "OUTLINER_PIE_MT_Bottom_X"
    kmi = km.keymap_items.new("outliner.show_active", "F", "CLICK")
    kmi = km.keymap_items.new("pie.toggle_collection", "E", "CLICK")
    kmi = km.keymap_items.new("outliner.collection_new", "W", "CLICK")
    kmi.properties.nested = True
    kmi = km.keymap_items.new("outliner.collection_objects_select", "A", "CLICK")
    kmi = km.keymap_items.new("outliner.collection_duplicate", "D", "CLICK", shift=True)
    kmi = km.keymap_items.new("outliner.collection_duplicate_linked", "D", "CLICK", alt=True)

    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    class_register()
    register_keymaps()


def unregister():
    unregister_keymaps()
    class_unregister()
