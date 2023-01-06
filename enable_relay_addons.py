import bpy
from bpy.types import Operator
import addon_utils

class Enable_Pie_Menu_Relay_Addons(Operator):
    bl_idname = "pie.enable_relay_addons"
    bl_label = "Enable Addons"
    bl_description = "一键打开常用内置插件"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        addon_utils.modules_refresh()
        addons_list =[]
        for mod in addon_utils.modules():
            addon_lists.append(mod.bl_info.get('name'))

        addons_officials_list =[
            # 官方&社区
            'curve_tools',
            'add_curve_extra_objects',
            'curve_simplify',
            'add_mesh_BoltFactory',
            'add_mesh_extra_objects',
            'development_edit_operator',
            'development_icon_get',
            'amaranth', # addon prop
            'space_view3d_copy_attributes',
            'materials_utils',  # key
            'object_print3d_utils',
            'mesh_f2', #key
            'mesh_looptools',
            'mesh_snap_utilities_line',
            'mesh_tiny_cad',
            'node_presets', # addon path
            'node_wrangler',
            'object_boolean_tools', # key
            'majic_uv',
            'io_import_images_as_planes'
        ]
        addons_thirds_list =[
            # 第三方
            'Bagapie',
            
        ]
        addon_utils.enable(module_name = '')
        return {"FINISHED"}

def register():
    bpy.utils.register_module(Enable_Pie_Menu_Relay_Addons)

def unregister():
    bpy.utils.unregister_module(Enable_Pie_Menu_Relay_Addons)

if __name__ == "__main__":
    register()