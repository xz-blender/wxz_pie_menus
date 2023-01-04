import bpy
from .pie.utils import change_default_keymap
from bpy.app.handlers import persistent

#### def ####
def change_key_value(A_dir,value):
    for space_type in A_dir:
        s_idname = space_type.lower().replace(' ','_').replace('_editor','').replace('_mode','')+'.select_all'

        keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
        for ks_name , ks_data in keymaps.items():
            if ks_name == space_type:
                list_keymaps = []
                for id_name , id_data in ks_data.keymap_items.items():
                    if id_name == s_idname and id_data.value != 'DOUBLE_CLICK':
                        list_keymaps.append(id_data)
                for data in list_keymaps:
                    data.value = value
                list_keymaps.clear()

def change_key_value_2(change_dir):
    stored_value_list = {}
    stored_prop_list = {}
    for dir_list in change_dir:
        keymaps = bpy.context.window_manager.keyconfigs.default.keymaps
        for ks_name , ks_data in keymaps.items():
            if ks_name == dir_list[0][0]:
                list_keymaps = []
                for id_name , id_data in ks_data.keymap_items.items():
                    if id_name == dir_list[0][1] and id_data.name == dir_list[0][2]:
                        list_keymaps.append(id_data)
                            # print('error_name----',dir_list[0][0],'---',dir_list[0][1],'-->',dir_list[0][2])
                for data in list_keymaps:
                    for value in dir_list[1]:
                        stored_value_list[data] = [value[0],getattr(data, value[0])]
                        setattr(data, value[0], value[1]) 
                    if dir_list[2] != None:
                        for prop in dir_list[2]:
                            stored_prop_list[data] = [prop[0],getattr(data.properties, prop[0])]
                            try:
                                setattr(data.properties,prop[0],prop[1])
                            except:
                                print(data.name,'--keys_prop_error-->',prop[0],':',prop[1])
                list_keymaps.clear()
    return (stored_value_list, stored_prop_list)

A_select_dir = [
    'Pose','Object Mode','Curve','Mesh','UV Editor','NLA Editor','Outliner'
    'Clip Editor','Node Editor','Graph Editor','Sequencer',
    'Armature','Metaball','Lattice','Particle','Sculpt Curves'
    ]

A_dir =[
    (['3D View','transform.skin_resize','Skin Resize'],[('value','CLICK')],[]), # ctrl A - mesh
    (['Object Mode','wm.call_menu','Apply'],[('value','CLICK')],[]), # ctrl A - object
    (['Object Mode','wm.call_menu','Add'],[('value','CLICK')],[]), # shift A - object
]
Brush_dir =[
    (['Sculpt','wm.call_menu_pie','Mask Edit'],[('value','CLICK_DRAG')],[]), # A
]
C_dir =[
    (['3D View','view3d.select_circle','Circle Select'],[('active',False)],[]), 
    (['UV Editor','uv.select_circle','Circle Select'],[('active',False)],[]),
    (['Graph Editor','graph.select_circle','Circle Select'],[('active',False)],[]),
    (['Node Editor','node.select_circle','Circle Select'],[('active',False)],[]),
    (['3D View','view3d.copybuffer','Copy Objects'],[('value','CLICK')],[]), # ctrl C
]
E_dir =[
    (['Curve','curve.extrude_move','Extrude Curve and Move'],[('value','CLICK')],[]), 
    (['Mesh','view3d.edit_mesh_extrude_move_normal','Extrude and Move on Normals'],[('value','CLICK')],[]), 
    (['Mesh','transform.edge_crease','Edge Crease'],[('value','CLICK')],[]), # shift E
    (['Graph Editor','transform.transform','Transform'],[('value','CLICK')],[]),
    (['Armature','armature.extrude_move','Extrude'],[('value','CLICK')],[]),
]
F_dir =[
    (['Curve','curve.make_segment','Make Segment'],[('value','CLICK')],[]), 
    (['Mesh','mesh.edge_face_add','Make Edge/Face'],[('value','CLICK')],[]), 
    (['Mesh','wm.call_menu','Face'],[('value','CLICK')],[]), # ctrl F
    (['Node Editor','node.link_make','Make Links'],[('value','CLICK')],[]), # ctrl F
]
Outliner_dir =[
    (['Outliner','outliner.select_all','Toggle Selected'],[('value','CLICK')],[]),  # A
    (['Outliner','outliner.collection_exclude_set','Disable from View Layer'],[('value','CLICK')],[]),  # E
    (['Outliner','outliner.collection_exclude_clear','Enable in View Layer'],[('value','CLICK')],[]),  # alt E
    (['Outliner','outliner.collection_new','New Collection'],[('value','CLICK')],[]),  # C
]
Q_dir =[
    (['Window','wm.call_menu','Quick Favorites'],[('active',False)],[]), # Q
    (['Window','wm.quit_blender','Quit Blender'],[('active',False)],[]), # ctrl Q
    (['Object Non-modal','object.transfer_mode','Transfer Mode'],[('active',False)],[]), # alt Q
]
R_dir =[
    (['3D View','transform.rotate','Rotate'],[('value','CLICK')],[]),
    (['UV Editor','transform.rotate','Rotate'],[('value','CLICK')],[]),
    (['Node Editor','transform.rotate','Rotate'],[('value','CLICK')],[]),
]
S_dir =[
    (['Window','wm.save_mainfile','Save Blender File'],[('value','CLICK')],[]), # ctrl S -- save file
    (['Window','wm.save_as_mainfile','Save As'],[('value','CLICK')],[]), # ctrl shift S -- save file
    (['3D View','transform.resize','Resize'],[('value','CLICK')],[]),
    (['UV Editor','transform.resize','Resize'],[('value','CLICK')],[]),
    (['Graph Editor','transform.resize','Resize'],[('value','CLICK')],[]),
    (['Node Editor','transform.resize','Resize'],[('value','CLICK')],[]),
]
SPACE_dir =[
    (['Window','wm.toolbar','Toolbar'],[('active',False)],[]),  # shift space
    (['Window','wm.search_menu','Search Menu'],[('type','SPACE'),('value','DOUBLE_CLICK')],[]),  # search
    (['Frames','screen.animation_play','Play Animation'],[('active',False)],[]),  # space
]
T_dir =[
    (['3D View Generic','wm.context_toggle','Context Toggle'],[('value','CLICK')],[]), 
    (['Image Generic','wm.context_toggle','Context Toggle'],[('value','CLICK')],[]), 
    (['Node Generic','wm.context_toggle','Context Toggle'],[('value','CLICK')],[]), 
]
TAB_dir =[
    (['Object Non-modal','object.mode_set','Set Object Mode'],[('value','CLICK')],[]), 
    (['Object Non-modal','view3d.object_mode_pie_or_toggle','Object Mode Menu'],[('value','CLICK_DRAG'),('type','TAB'),('ctrl',False)],[]), 
    (['Node Editor','wm.call_menu','Edit Group'],[('value','CLICK')],[]), 
]
U_dir =[
    (['Mesh','wm.call_menu','UV Mapping'],[('value','CLICK')],[]), 
    (['UV Editor','wm.call_menu','Unwrap'],[('value','CLICK')],[]), 
]
V_dir =[
    (['Curve','curve.handle_type_set','Set Handle Type'],[('value','CLICK')],[]), # V
    (['Mesh','mesh.rip_move','Rip'],[('value','CLICK')],[]), # V
    (['UV Editor','uv.stitch','Stitch'],[('value','CLICK')],[]), # alt V
    (['UV Editor','uv.rip_move','UV Rip Move'],[('value','CLICK')],[]), 
    (['3D View','view3d.pastebuffer','Paste Objects'],[('value','CLICK')],[]), # ctrl V
]
W_dir =[
    (['3D View','wm.tool_set_by_id','Set Tool by Name'],[('value','CLICK')],[]), # W
    (['Window','wm.toolbar_fallback_pie','Fallback Tool Pie Menu'],[('value','CLICK_DRAG')],[]), # alt W
]
X_dir =[
    (['Object Mode','object.delete','Delete'],[('value','CLICK')],[('use_global',False),('confirm',False)]),
    (['Mesh','wm.call_menu','Delete'],[('active',False)],[]),
    (['Curve','wm.call_menu','Delete'],[('value','CLICK')],[]),
    (['Outliner','outliner.delete','Delete'],[('value','CLICK')],[]),
    (['Graph Editor','wm.call_menu','Delete'],[('value','CLICK')],[]),
    (['Node Editor','node.delete','Delete'],[('value','CLICK')],[]),
]
Z_dir =[
    (['3D View','wm.call_menu_pie','Shading'],[('value','CLICK')],[]), # Z
    (['3D View','view3d.toggle_shading','Toggle Shading Type'],[('active',False)],[]), # shift Z
]

        
def changes_keys():

    change_key_value(A_select_dir, "CLICK")

    for _dir in [A_dir,Brush_dir,C_dir,E_dir,F_dir,Outliner_dir,Q_dir,R_dir,S_dir,SPACE_dir,T_dir,TAB_dir,U_dir,V_dir,W_dir,X_dir,Z_dir]:
        change_key_value_2(_dir)

    print('"WXZ_Pie_Menu" changed keys!')
    import os
    name = os.path.dirname(__file__)
    print(name)

def register():
    if not bpy.app.timers.is_registered(changes_keys):
        bpy.app.timers.register(changes_keys, first_interval=2)


def unregister(): 
    if bpy.app.timers.is_registered(changes_keys):
        bpy.app.timers.unregister(changes_keys)

if __name__ == "__main__":
    register()