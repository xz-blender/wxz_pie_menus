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
                    if id_name == dir_list[0][1]:
                        if id_data.name == dir_list[0][2]:
                            list_keymaps.append(id_data)
                        else:
                            print('error_name----',dir_list[0][0],'---',dir_list[0][1],'-->',dir_list[0][2])
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

A_dir = [
    'Pose','Object Mode','Curve','Mesh','UV Editor','NLA Editor','Clip Editor','Node Editor','Graph Editor','Sequencer'
    'Armature','Metaball','Lattice','Particle',
    'Sculpt Curves'
    ] 

U_dir =[
    (['Mesh','wm.call_menu','UV Mapping'],[('value','CLICK')],[]), 
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
    (['3D View','wm.toolbar_fallback_pie','Fallback Tool Pie Menu'],[('value','CLICK_DRAG')],[]), # alt W
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

    change_key_value(A_dir, "CLICK")

    for _dir in [V_dir, W_dir, X_dir, Z_dir]:
        change_key_value_2(_dir)

    print('"WXZ_Pie_Menu" changed keys!')

def register():
    if not bpy.app.timers.is_registered(changes_keys):
        bpy.app.timers.register(changes_keys, first_interval=5)


def unregister(): 
    if bpy.app.timers.is_registered(changes_keys):
        bpy.app.timers.unregister(changes_keys)

if __name__ == "__main__":
    register()