import bpy
import addon_utils
from pathlib import Path
import sys, os, time
from bpy.types import Operator

def change_addon_key_value(change_dir):
    bpy.context.preferences.view.use_translate_interface = False
    for dir_list in change_dir:
        keymaps = bpy.context.window_manager.keyconfigs['Blender addon'].keymaps
        for ks_name , ks_data in keymaps.items():
            if ks_name == dir_list[0][0]:
                list_keymaps = []
                for id_name , id_data in ks_data.keymap_items.items():
                    if id_name == dir_list[0][1] and id_data.name == dir_list[0][2]:
                            list_keymaps.append(id_data)
                for data in list_keymaps:
                    for value in dir_list[1]:
                        setattr(data, value[0], value[1]) 
                        # print(value[0], value[1])
                    if dir_list[2] != None:
                        for prop in dir_list[2]:
                                setattr(data.properties,prop[0],prop[1])
                list_keymaps.clear()
    bpy.context.preferences.view.use_translate_interface = True


if sys.platform == "win32":
    sync_path = r'D:/OneDrive/Sync/Blender/Assets Sync'
    local_path = r'F:/Blender Assets'
    addon_path = Path(bpy.utils.user_resource("SCRIPTS"))/'addons'
elif sys.platform == 'darwin':
    sync_path = r'/Users/wangxianzhi/Library/CloudStorage/OneDrive-个人/Sync/Blender/Assets Sync'
    local_path = r'/Users/wangxianzhi/Blender Lib'
    addon_path = Path(bpy.utils.user_resource("SCRIPTS"))/'addons'
    
class Enable_Pie_Menu_Relay_Addons(Operator):
    bl_idname = "pie.enable_relay_addons"
    bl_label = "一次性打开多个常用插件,会非常耗时!"
    bl_description = "一键打开常用内置插件"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        # return self.execute(context)
        
    # def draw(self, context):
    #     layout = self.layout
    #     layout.label(text="一次性打开多个常用插件,会非常耗时!", icon="ERROR")

    def execute(self, context):
        addon_utils.modules_refresh()
        addons_list =[]
        for mod in addon_utils.modules():
            addons_list.append(mod.__name__)

        user_path = bpy.utils.resource_path('USER') 
        config_path = os.path.join(user_path, "config")

        join = os.path.join

        addons_officials_list ={
        # 官方&社区      #  addon_name : [[addon_settings],[addon_keys]]
            'curve_tools' : [[],[]],
            'add_curve_extra_objects':[[],[]],
            'curve_simplify':[[],[]],
            'add_mesh_BoltFactory':[[],[]],
            'add_mesh_extra_objects':[[],[]],
            'development_edit_operator':[[],[]],
            'development_icon_get':[[],[]],
            # 'amaranth':[[('use_frame_current',False),
            #             ('use_scene_refresh',False),
            #             ('use_file_save_reload',False),
            #             ('use_timeline_extra_info',False),
            #             ('use_layers_for_render',False),
            #             ],[]], 
            'space_view3d_copy_attributes':[[],[]],
            'materials_utils':[[],[(['3D View','wm.call_menu','Material Utilities'],[('value','CLICK'),('ctrl',True)],[])]],
            'object_print3d_utils':[[],[]],
            'mesh_f2':[[('ajustuv',True)],
                       [(['Mesh','mesh.f2','Make Edge/Face'],[('value','CLICK')],[])]],
            'mesh_looptools':[[],[]],
            'mesh_snap_utilities_line':[[],[]],
            'mesh_tiny_cad':[[],[]],
            'node_presets':[[('search_path',join(sync_path,'Nodes Presets'))],[]], # addon path
            'node_wrangler':[[],[]],
            'object_boolean_tools':[[],[(['Object Mode','wm.call_menu','Bool Tool'],[('value','CLICK')],[])]], # key
            'magic_uv':[[],[]],
            # 'io_import_images_as_planes':[[],[]],
            'space_view3d_modifier_tools':[[],[]],
            'sun_position':[[],[]],
            'object_edit_linked':[[],[]],
            'mesh_tools':[[],[]],
            'mesh_inset':[[],[]],
            'io_import_dxf':[[],[]],
            'io_export_dxf':[[],[]],


        # 第三方
            'Bagapie': [[],[(['3D View','bagapie.duplicatelinkedgroup','Duplicate Linked Group'],[('active',False)],[]),
                            (['3D View','bagapie.duplicategroup','Duplicate Group'],[('active',False)],[]),
                            (['3D View','wm.call_menu_pie','BagaPie GeoPack'],[('active',False)],[]),
                            ]], # key alt N
            'slcad_transform': [[],[]],
            # EsayLight
            'EasyLight': [[('ies_library_path',str(Path(sync_path)/'IES'))],[]], # ies lib path
            # HDRI
            'hdri_maker': [[
                            ('addon_default_library',str(Path(local_path)/'HDRI MAKER LIBRARY'/'HDRI_MAKER_DEFAULT_LIB')),
                            ('addon_user_library',str(Path(local_path)/'HDRI MAKER LIBRARY'/'HDRI_MAKER_USER_LIB'))
                            ],[]],
            # QuickSnap
            'quicksnap': [[('auto_check_update',False)],[
                (['3D View','object.quicksnap','QuickSnap Tool'],[('value','CLICK'),('type','G'),('shift',False)],[])]],
            # Simple Tabs
            'simple-tabs': [[('startup_delay',1)],[]], # 导入json设置
            'slcad_transform': [[],[]],
            'extra_lights': [[],[]],
            # Photographer
            'photographer': [[
                            #('hdri_lib_path',str(Path(sync_path)/'Custom HDRI'))
                              ],
                            [(['3D View','wm.call_menu_pie','Photographer Camera Pie'],[('value','CLICK_DRAG')],[])]],
            # Object Asset Wizard
            'object_asset_wizard': [[('root',str(Path(sync_path)/'Blender Assets Wizard'))],[]],
            'BMAX_Connector': [[],[]],
            'sketchup_importer': [[],[]],
            # Super IO
            'super_io': [[('force_unicode',True),('cpp_obj_importer',True),
                            ('cpp_obj_exporter',True),('extend_export_menu',True)],
                        [
                        (['3D View','wm.super_import','Super Import'],[('value','CLICK')],[]),
                        (['3D View','wm.super_export','Super Export'],[('value','CLICK'),('type','E')],[]),
                        (['Node Editor','wm.super_import','Super Import'],[('value','CLICK')],[]),
                        (['Node Editor','wm.super_export','Super Export'],[('value','CLICK'),('type','E')],[]),
                        (['Image Generic','wm.super_export','Super Export'],[('value','CLICK'),('type','E')],[]),
                        (['File Browser','wm.super_import','Super Import'],[('value','CLICK')],[]),
                        (['File Browser','wm.super_export','Super EXport'],[('value','CLICK'),('type','E')],[]),
                        ]],
            'Synchronize Workspaces': [[],[]],
            'EasyPBR': [[],[]], # keys 未更改 ('lib_path',join(sync_path,'Easy_PBR_library'))
            'EdgeFlow': [[],[]],
            'slide_edge': [[],[]],
            'straight_skeleton': [[],[]],
            'face_cutter': [[],[]],
            'bend_face': [[],[]],
            'simple_bend': [[],[]],
            # Niche Loops
            'niche-loops': [[],[]],
            'round_inset': [[],[]],
            'Seer Adjacent Selection': [[],[]],
            # Smart Fill
            'smart_fill': [[('mouse_wheel',False)],[
                (['Mesh','mesh.mesh.smart_fill_popup','Smart Fill Popup'],[('value','CLICK')],[]),
                (['Mesh','mesh.edge_face_add','Make Edge/Face'],[('value','CLICK')],[]),
                ]],
            'smart_loops_toolkit': [[],[]],
            #----Nodes----
            'BB_Nodes': [[],[]],
            'colormate': [[],[]],
            'ETK_core': [[],[]],
            'Node Kit': [[('nodes_path',str(Path(sync_path)/'NodeKit'))],[]],
            'node_pie': [[],[(['Node Editor','wm.call_menu_pie','Node pie'],[('value','CLICK_DRAG')],[])]],
            'uber_compositor': [[],[]],
            'b3dsdf': [[],[]],
            'wxz_nodes_presets': [[],[]],
            # Drop It
            'drop_it': [[],[
                (['3D View','object.drop_it','Drop It'],[('value','CLICK')],[])
                ]],
            'NGon Loop Select': [[],[
                # (['Mesh','ls.select','Loop Select'],[('value','CLICK')],[]),
                ]],
            'OCD': [[],[]],
            # IQ lib
            'botaniq_full': [[('botaniq_path',str(Path(local_path)/'botaniq_full'))],[]],
            # 'aquatiq_full': [[('aquatiq_path',str(Path(local_path)/'aquatiq_full'))],[]],
            'materialiq_full': [[('materialiq5_path',str(Path(local_path)/'materialiq_full'))],[]],
            'traffiq_full': [[('traffiq_path',str(Path(local_path)/'traffiq_full'))],[]],
            # Vegtation
            'Vegetation': [[('assets_path',str(Path(local_path)/'vegetation'))],[]],
            # Leafig
            'leafig': [[],[]],
            'Text_input': [[],[]],
            'atomic_data_manager': [[('enable_missing_file_warning',False),('enable_support_me_popup',False),
                                        ('enable_pie_menu_ui',False),('auto_check_update',False),],[]],
            'QOL_Select_Contiguous': [[],[]],
            # TexTools
            'TexTools': [[],[]],
            'UvSquares': [[],[]],
            'distributeobjects': [[],[]],
            # Friendly Povit
            ''''
                scpo': [[],[
                (['3D View','friendly.pivot','Friendly:SCPO'],[('value','CLICK'),('ctrl',True)],[]),
                (['Image','friendly.pivot2d','Friendly:SCPO2D'],[('value','CLICK'),('ctrl',True)],[])]],
                '''
            # 辣椒酱
            'lattice_helper': [[],[]],
            'popoti_align_helper': [[],[]],
            'PlaceHelper': [[],[]],
            # 时间线
            'viewport_timeline_scrub': [[],[]],
            'autoMaterial': [[],[]],
            'Inset_Outset': [[],[]],
            'camera_shakify': [[],[]],
            'rotate_face': [[],[]],
            #Kushiro Addons
            'cut_corner': [[],[]],
            'safe_ngon': [[],[]],
            'select_sim': [[],[]],
            'VoronoiLinker': [[],
                              [(['Node Editor','node.voronoi_preview','Voronoi Preview'],[('active',False)],
                                ['Node Editor','node.voronoi_mixer','Voronoi Mixer'],[('active',False)],
                                ['Node Editor','node.voronoi_swaper','Voronoi Swaper'],[('active',False)],
                                )]],
            # True Assets
            'True-Assets': [[('ta_directory',str(Path(sync_path)/'True Assets'))],
                            [(['3D View','ta.saveassetsfromthisfile','Mark Assets and Quit'],[('active',False)],[])]],
        }

        addon_disable_list = [
            'io_anim_bvh',
            'io_mesh_ply',
            # 'mesh_f2',
        ]

        # ads_lis_dir = addons_officials_list.update(addons_thirds_list)
        # 打开插件并设置
        for addon_name ,addon_change in addons_officials_list.items():
            if addon_name in addons_list:
                if addon_utils.check(addon_name)[0] == False:
            #  # check addon is enabled
                    try:
                        bpy.ops.preferences.addon_enable(module = addon_name)
                        time.sleep(0.1)
                        bpy.ops.preferences.addon_refresh()
                        print(addon_name,'is enabled')
                    except:
                        print(addon_name,'is enable error')
                if addon_change[0]:
                    for pref_change in addon_change[0]:
                        setattr(context.preferences.addons[addon_name].preferences, pref_change[0], pref_change[1])
                if addon_change[1]:
                    change_addon_key_value(addon_change[1])
        # 关闭插件
        for disable in addon_disable_list:
            if disable in addons_list and addon_utils.check(disable)[0] == True:
                bpy.ops.preferences.addon_disable(module = disable)

        # 部分插件其他设置
        self.report({'INFO'}, '已开启预设插件')
        return {"FINISHED"}
        

user_lib_names = []
for lib in bpy.context.preferences.filepaths.asset_libraries:
    user_lib_names.append(lib.name)

setting_lib = {
    'Rig_Car' : (str(Path(local_path)/'rig_cars'), 'LINK'),
    'Poly Haven' : (str(Path(local_path)/'Poly Haven'), 'LINK'),
    '旧公司资产' : (str(Path(local_path)/'company_old_lib'), 'APPEND_REUSE'),
    'Simple Cloth' : (str(Path(sync_path)/'Blender Assets Browser'/'Simply Basic Cloth Library'), 'APPEND'),
    'GN' : (str(Path(sync_path)/'Blender Assets Browser'/'GN'), 'APPEND_REUSE'),
    'Material' : (str(Path(sync_path)/'Blender Assets Browser'/'Material'), 'APPEND_REUSE'),
    'Lights' : (str(Path(sync_path)/'Blender Assets Browser'/'Lights'), 'APPEND_REUSE'),
    '马路标志' : (str(Path(sync_path)/'Blender Assets Browser'/'马路标志'), 'LINK'),
    'Abionic' : (str(Path(local_path)/'Abionic'), 'LINK'),
    'BagaPie Assets' : (str(Path(local_path)/'BagaPie Assets'), 'LINK'),
    '室内家具模型' : (str(Path(local_path)/'室内家具模型'), 'LINK'),
    'Geo-Scatter_library' : (str(Path(local_path)/'Geo-Scatter_library'), 'LINK'),
    'Trash_kit' : (str(Path(local_path)/'Trash_kit'), 'LINK'),
    'kit_bash' : (str(Path(local_path)/'kit_bash'), 'LINK'),
    'kit_building' : (str(Path(local_path)/'kit_building'), 'LINK'),
    'Tree Assets' : (str(Path(local_path)/'Tree Assets'), 'LINK'),
    'Motion Animate' : (str(Path(local_path)/'Motion Animate'), 'APPEND'),
    '图案光阴影贴图' : (str(Path(local_path)/'图案光阴影贴图'), 'LINK'),
    '其他' : (str(Path(local_path)/'其他'), 'LINK'),
    'HIG_Nodes' : (str(Path(addon_path)/'Higgsas_Groups'), 'APPEND'),
}

def change_assets_library_path():
    # for name in user_lib_names:
    #     df_name = 'User Library'
    #     if name == df_name:
    #         bpy.ops.preferences.asset_library_remove(index = user_lib_names.index(df_name))

    sort_setting_lib = dict(sorted(setting_lib.items(),key = lambda x : x[0]))

    for name, data in sort_setting_lib.items():
        if name not in user_lib_names:
            bpy.ops.preferences.asset_library_add(directory = data[0])
            bpy.context.preferences.filepaths.asset_libraries[-1].name = name

            version = bpy.app.version
            if version[0] >= 3 and version[1] >= 5 :
                bpy.context.preferences.filepaths.asset_libraries[-1].import_method = data[1]

def change_addons():
    bpy.context.preferences.filepaths.texture_directory = str(Path(sync_path).parent.parent/'Texture')
    bpy.context.preferences.filepaths.font_directory = str(Path(sync_path).parent.parent/'Fonts')

    bpy.ops.pie.enable_relay_addons()
    print('"WXZ_Pie_Menu" Enable Relay Addons!')
    change_assets_library_path()
    print('"WXZ_Pie_Menu" Change Assets Library Items!')

def register():
    # try:
    bpy.utils.register_class(Enable_Pie_Menu_Relay_Addons)
    # except:
    #     pass
    if not bpy.app.timers.is_registered(change_addons):
        bpy.app.timers.register(change_addons, first_interval=2)

def unregister():
    if bpy.app.timers.is_registered(change_addons):
        bpy.app.timers.unregister(change_addons)

    bpy.utils.unregister_class(Enable_Pie_Menu_Relay_Addons)
    
if __name__ == "__main__":
    register()