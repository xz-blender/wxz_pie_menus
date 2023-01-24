import bpy
import os
from pathlib import *
from bpy.types import Menu, Operator, AddonPreferences
from .utils import set_pie_ridius, change_default_keymap, restored_default_keymap


submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "PIE",
}
def del_wspace(d_name):
    # 删除原始工作空间                                           
    for i_index, i_data in enumerate(bpy.data.workspaces): 
        if i_data.name == d_name:
            w = bpy.data.workspaces[d_name]
            bpy.ops.workspace.delete({"workspace": w})
            return i_index

class VIEW3D_PIE_MT_Ctrl_Tab(Menu):
    bl_label = "Tab-ctrl"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        # print(context.area.type, context.area.ui_type)

        # 4 - LEFT
        L = pie.operator('pie.workspaceswapper', text='UV', icon='UV_DATA')
        L.target_workspace = '3-UV'
        L.default_workspace = 'UV Editing'
        # 6 - RIGHT
        R = pie.operator('pie.workspaceswapper', text='MOD', icon='CUBE')
        R.target_workspace = '1-MOD'
        R.default_workspace = 'Modeling'
        # 2 - BOTTOM
        B = pie.operator('pie.workspaceswapper', text='MAT', icon='MATERIAL')
        B.target_workspace = '4-MAT'
        B.default_workspace = 'Shading'
        # 8 - TOP
        box = pie.column(align=True)
        row = box.row()
        row.scale_y = 1.3
        T1 = row.operator(
            'pie.workspaceswapper', text='SETTING', icon='SETTINGS'
        )
        T1.target_workspace = '8-SETTING'
        T1.default_workspace = 'Scripting'

        row = box.row(align=True)
        row.scale_y = 1.1
        split = row.split()
        T2_1 = split.operator(
            'pie.workspaceswapper', text='LIB', icon='BOOKMARKS'
        )
        T2_1.target_workspace = '0-LIB'
        T2_1.default_workspace = 'Layout'
        split = row.split()
        T2_2 = split.operator(
            'pie.workspaceswapper', text='COMPO', icon='NODE_COMPOSITING'
        )
        T2_2.target_workspace = '7-COMPO'
        T2_2.default_workspace = 'Compositing'

        row = box.row(align=True)
        row.scale_y = 1.1
        split = row.split()
        T3_1 = split.operator(
            'pie.workspaceswapper', text='MOTION', icon='MOD_INSTANCE'
        )
        T3_1.target_workspace = '5-MOTION'
        T3_1.default_workspace = 'Animation'
        split = row.split()
        T3_2 = split.operator(
            'pie.workspaceswapper', text='RENDER', icon='RENDER_STILL'
        )
        T3_2.target_workspace = '6-RENDER'
        T3_2.default_workspace = 'Rendering'
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        BR = pie.operator('pie.workspaceswapper', text='GN', icon='CUBE')
        BR.target_workspace = '2-GN'
        BR.default_workspace = 'Geometry Nodes'


class PIE_WorkspaceSwapOperator(Operator):
    """Swap workspaces with this operator"""
    bl_idname = "pie.workspaceswapper"
    bl_label = "Swap Workspace"
    bl_options = {'REGISTER','UNDO'}

    target_workspace: bpy.props.StringProperty(name='Target Workspace')
    default_workspace: bpy.props.StringProperty(
        name='Default Workspcae', default='Layout'
    )

    def execute(self, context):
        t_name = self.target_workspace
        d_name = self.default_workspace
        # don't need to swap if already on there
        if context.workspace.name == t_name:
            self.report({'INFO'}, '已经为该工作空间！')
            return {'CANCELLED'}

        if t_name in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces[t_name]
            self.report({'INFO'}, '已切换工作空间:"%s"' % (t_name))
            return {'FINISHED'}

        # Try local workspace swapping first
        # Last resort: try to import from the blender templates

        # old path:
        # path = bpy.utils.user_resource('CONFIG') + os.sep + "startup.blend"
        
        # new path: ('startup.blend' in addon files)
        # path = os.path.join(os.path.dirname(__file__), "startup.blend")
        path = str(Path(__file__).parent.parent / 'workspace.blend')
        if t_name not in bpy.data.workspaces:
            # try:
                # 删除原始工作空间, 并获取所在index
                index = del_wspace(d_name)
                print(index)

                bpy.ops.workspace.append_activate(idname=t_name, filepath=path)
                # context.window.workspace = bpy.data.workspaces[t_name]
                # 重新排序
                bpy.ops.workspace.reorder_to_front({"workspace": bpy.data.workspaces[t_name]})


                self.report({'INFO'}, '已添加工作空间:"%s",并切换' % (t_name))
                return {'FINISHED'}

            # except:
            #     context.window.workspace = bpy.data.workspaces[d_name]
            #     self.report(
            #         {'INFO'}, '没找到"{}"工作空间,已切换默认:"{}"'.format(t_name, d_name)
            #     )
                # return {'FINISHED'}


# class PIE_Change_Active_WorkSpace(Operator):
#     bl_idname = "pie.workspaces_active"
#     bl_label = "Change Workspace"
#     bl_options = {'REGISTER','UNDO'}

#     ws_name : bpy.props.StringProperty(name='Active Workspace')

#     def execute(self, context):
#         context.workspace = bpy.data.workspaces[self.ws_name]
#         return {'FINISHED'}

classes = [
    VIEW3D_PIE_MT_Ctrl_Tab,
    PIE_WorkspaceSwapOperator,
]


addon_keymaps = []

def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    keymap_items = {
        '3D View': 'VIEW_3D',
        'Node Editor': 'NODE_EDITOR',
        'Image': 'IMAGE_EDITOR',
    }
    for name, space in keymap_items.items():
        km = addon.keymaps.new(name=name, space_type=space)
        kmi = km.keymap_items.new(
            idname='wm.call_menu_pie',
            type="TAB",
            value="CLICK_DRAG",
            ctrl=True,
            shift=False,
            alt=False,
        )
        kmi.properties.name = "VIEW3D_PIE_MT_Ctrl_Tab"
        addon_keymaps.append(km)
    
    wspace_names = ['0-LIB','1-MOD','2-GN','3-UV','4-MAT','5-MOTION','6-RENDER','7-COMPO','8-SETTING']
    for name in wspace_names:
        km = addon.keymaps.new(name='Screen', space_type='EMPTY')
        kmi = km.keymap_items.new(
            idname=PIE_WorkspaceSwapOperator.bl_idname,
            type="NUMPAD_%s"%(name[0]),
            value="CLICK",
            ctrl=False,
            shift=False,
            alt=True,
        )
        kmi.properties.target_workspace = name
        addon_keymaps.append(km)





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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Ctrl_Tab")
