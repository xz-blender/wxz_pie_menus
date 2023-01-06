import bpy
import addon_utils
from bpy.types import Operator
from.change_keys import change_key_value_base

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
            addons_list.append(mod.__name__)

        addons_officials_list ={
            # 官方&社区      #  addon_name : [[addon_settings],[addon_keys]]
            'curve_tools' : [],
            'add_curve_extra_objects':[],
            'curve_simplify':[],
            'add_mesh_BoltFactory':[],
            'add_mesh_extra_objects':[],
            'development_edit_operator':[],
            'development_icon_get':[],
            'amaranth':[[('use_frame_current',False),
                        ('use_scene_refresh',False),
                        ('use_file_save_reload',False),
                        ('use_timeline_extra_info',False),
                        ('use_layers_for_render',False),
                        ],[]], 
            'space_view3d_copy_attributes':[],
            'materials_utils':[[],
                        (['3D View','wm.call_menu','Material Utilities'],[('value','CLICK'),('ctrl',True)],[])
                        ],  # key
            'object_print3d_utils':[],
            'mesh_f2':[], #key
            'mesh_looptools':[],
            'mesh_snap_utilities_line':[],
            'mesh_tiny_cad':[],
            'node_presets':[], # addon path
            'node_wrangler':[],
            'object_boolean_tools':[], # key
            'magic_uv':[],
            'io_import_images_as_planes':[]
        }
        addons_thirds_list =[
            # 第三方
            'Bagapie', # key alt N
            'slcad_transform',
        ]
        for addon_name ,addon_change in addons_officials_list:
            if addon_name in addons_list:
            # if addon_utils.check(addon_name)[0] == True: # check addon is enabled
                try:
                    bpy.ops.preferences.addon_enable(module = addon_name)
                except:
                    print(addon_name,'is enable error')
                if addon_change[1]:
                    try:
                        change_key_value_base(addon_change[1])
                    except:
                        None
                # print('%s is already enabled'% addon_o)
                # print('enabled addon:',addon_o)

        return {"FINISHED"}

def register():
    bpy.utils.register_class(Enable_Pie_Menu_Relay_Addons)

def unregister():
    bpy.utils.unregister_class(Enable_Pie_Menu_Relay_Addons)

if __name__ == "__main__":
    register()