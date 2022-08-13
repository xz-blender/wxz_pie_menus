import bpy
import addon_utils


rely_addons = [
    ('Edit Mesh Tools', 'mesh_tools'),  # 0
    ('Straight Skeleton', 'straight_skeleton'),  # 1
    ('LoopTools', 'mesh_looptools'),  # 2
    ('Modifier Tools', 'space_view3d_modifier_tools'),  # 3
    ('DPFR Distribute Objects', 'distributeobjects'),  # 4
    ('SketchUp Importer', 'sketchup_importer'),  # 5
    ('Atomic Data Manager', 'atomic_data_manager'),  # 6
    ('EdgeFlow', 'slide_edge'),  # 7
    ('Bend Face', 'bend_face'),  # 8
    ('Face Cutter', 'face_cutter'),  # 9
    ('Curve Tools', 'curve_tools'),  # 10
]

# rely_addons.sort(key=lambda name: name[0])

addon_lists = []
for mod in addon_utils.modules():
    addon_lists.append(mod.bl_info.get('name'))


def check_rely_addon(a_name, p_name):  # addon name & path name
    if a_name in addon_lists:
        if addon_utils.check(p_name)[0] == False:
            # return: (loaded_default, loaded_state) 元组
            return '0'  # 安装未启用
        else:
            return '1'  # 安装已启用
    else:
        return '2'  # 未安装


def set_pie_ridius(context, radius=100):
    context.preferences.view.pie_menu_radius = radius


def pie_op_check(pie, check_op, op_text):
    if check_op == '2':
        pie.operator('pie.empty_operator', text='未安装%s插件' % (op_text))
        return False
    elif check_op == '0':
        pie.operator('pie.empty_operator', text='未启用%s插件' % (op_text))
        return False
    elif check_op == '1':
        return True
