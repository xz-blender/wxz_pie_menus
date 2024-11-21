import threading

import bpy

from ..pie.utils import keymap_safe_unregister
from ..utils import extend_keymaps_list, safe_register_class, safe_unregister_class


def main_test(context):
    for ob in context.scene.objects:
        print(ob)


class PIE_Simple_Test_Operator(bpy.types.Operator):
    bl_idname = "pie.test_operator"
    bl_label = "Test Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # 获取参数
        repo_directory = context.preferences.extensions.repos["blender4.com"].directory
        repo_index = context.preferences.extensions.repos.find("blender4.com")
        pkg_id = "engon"

        # 创建并启动子线程
        thread = threading.Thread(
            target=self.background_task,
            args=(repo_directory, repo_index, pkg_id),
        )
        thread.start()

        return {"FINISHED"}

    def background_task(self, repo_directory, repo_index, pkg_id):
        bpy.ops.extensions.package_install(
            "INVOKE_DEFAULT",
            repo_directory=repo_directory,
            repo_index=repo_index,
            pkg_id=pkg_id,
            enable_on_install=True,
            do_legacy_replace=False,
        )


CLASSES = [
    PIE_Simple_Test_Operator,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "F", "CLICK_DRAG")
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    # register_keymaps()
    extend_keymaps_list(addon_keymaps)


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
