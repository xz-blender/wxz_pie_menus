import bpy
import os
import bmesh
from bpy.types import PropertyGroup, Panel, Operator, Menu
from .utils import check_rely_addon, rely_addons, set_pie_ridius
from .utils import change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "PIE",
}


class VIEW3D_PIE_MT_Bottom_E(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        # "EdgeFlow"addon
        ef_name, ef_path = rely_addons[7][0], rely_addons[7][1]
        ef_check = check_rely_addon(ef_name, ef_path)
        # "Bend Face"addon
        bf_name, bf_path = rely_addons[8][0], rely_addons[8][1]
        bf_check = check_rely_addon(bf_name, bf_path)
        # "Face Cutter"addon
        fc_name, fc_path = rely_addons[9][0], rely_addons[9][1]
        fc_check = check_rely_addon(fc_name, fc_path)

        if ob_mode == 'EDIT' and ob_type == 'MESH':
            # 4 - LEFT
            pie.operator("mesh.flip_normals")
            # 6 - RIGHT
            col = pie.split().box().column()
            if ef_check == '2':
                row = col.row()
                row.operator('pie.empty_operator',
                             text='未安装"%s"插件' % (ef_name))
            elif ef_check == '0':
                row = col.row()
                row.operator('pie.empty_operator',
                             text='未启用"%s"插件' % (ef_name))
            elif ef_check == '1':
                row = col.row()
                row.operator('mesh.set_edge_flow')
                row = col.row()
                row.operator('mesh.set_edge_linear')

            # 2 - BOTTOM
            pie.operator("mesh.normals_make_consistent")
            # 8 - TOP
            pie.operator('mesh.extrude_manifold', text='挤出流形')
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.operator('mesh.bridge_edge_loops', text='桥接循环边')
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            col = pie.split().box().column()
            if bf_check == '2':
                row = col.row()
                row.operator('pie.empty_operator',
                             text='未安装"%s"插件' % (bf_name))
            elif bf_check == '0':
                row = col.row()
                row.operator('pie.empty_operator',
                             text='未启用"%s"插件' % (bf_name))
            elif bf_check == '1':
                row = col.row()
                row.operator('mesh.bend_face_operator')

            if fc_check == '2':
                row = col.row()
                row.operator('pie.empty_operator',
                             text='未安装"%s"插件' % (fc_name))
            elif fc_check == '0':
                row = col.row()
                row.operator('pie.empty_operator',
                             text='未启用"%s"插件' % (fc_name))
            elif fc_check == '1':
                row = col.row()
                row.operator('mesh.face_cutter_operator')

class PIE_Shift_E_KEY(Operator):
    bl_idname = "pie.shift_e"
    bl_label = "设置折痕"
    bl_description = "在不同网格选择模式下设置不同的折痕"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def execute(self, context):
        active_ob_data = context.active_object.data
        for edge in active_ob_data.edges:
            if edge.select == True:
                edge.crease = 1
        
        
        return {'FINISHED'}

class PIE_Ctrl_Shift_E_KEY(Operator):
    bl_idname = "pie.ctrl_shift_e"
    bl_label = "设置权重"
    bl_description = "在不同网格选择模式下设置不同的权重"
    bl_options = {"REGISTER","UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def execute(self, context):
        
        return {"FINISHED"}

'''
class CAB_PG_Prop(PropertyGroup):
    ## Update functions
    def update_edge_bevelWeight(self, context):

        o  = bpy.context.object
        d  = o.data
        bm = bmesh.from_edit_mesh(d)

        bevelWeightLayer = bm.edges.layers.bevel_weight.verify()

        if self.whoToInfluence == 'Selected Elements':
            selectedEdges = [e for e in bm.edges if e.select]
            for e in selectedEdges: e[bevelWeightLayer] = self.edge_bevelWeight
        else:
            for e in bm.edges: e[bevelWeightLayer] = self.edge_bevelWeight

        bmesh.update_edit_mesh(d)

    def update_vert_bevelWeight(self, context):

        o  = bpy.context.object
        d  = o.data
        bm = bmesh.from_edit_mesh(d)

        bevelWeightLayer = bm.verts.layers.bevel_weight.verify()

        if self.whoToInfluence == 'Selected Elements':
            selectedVerts = [v for v in bm.verts if v.select]
            for v in selectedVerts: v[bevelWeightLayer] = self.vert_bevelWeight
        else:
            for v in bm.edges: v[bevelWeightLayer] = self.vert_bevelWeight

        bmesh.update_edit_mesh(d)

    def update_edge_Crease(self, context):

        o  = bpy.context.object
        d  = o.data
        bm = bmesh.from_edit_mesh(d)

        creaseLayer = bm.edges.layers.crease.verify()

        if self.whoToInfluence == 'Selected Elements':
            selectedEdges = [e for e in bm.edges if e.select]
            for e in selectedEdges: e[creaseLayer] = self.edge_Crease
        else:
            for e in bm.edges: e[creaseLayer] = self.edge_Crease

        bmesh.update_edit_mesh(d)

    def update_vert_Crease(self, context):

        o  = bpy.context.object
        d  = o.data
        bm = bmesh.from_edit_mesh(d)

        creaseLayer = bm.verts.layers.crease.verify()

        if self.whoToInfluence == 'Selected Elements':
            selectedVerts = [v for v in bm.verts if v.select]
            for v in selectedVerts: v[creaseLayer] = self.vert_Crease
        else:
            for v in bm.verts: v[creaseLayer] = self.vert_Crease

        bmesh.update_edit_mesh(d)

    ## Properties
    items = [
        ('All', 'All', ''),
        ('Selected Elements', 'Selected Elements', '')
    ]

    whoToInfluence: bpy.props.EnumProperty(
        description = "Influence all / selection",
        name        = "whoToInfluence",
        items       = items,
        default     = 'Selected Elements'
    )

    edge_bevelWeight: bpy.props.FloatProperty(
        description = "Edge Bevel Weight",
        name        = "Set bevel Weight",
        min         = 0.0,
        max         = 1.0,
        step        = 0.1,
        default     = 0,
        update      = update_edge_bevelWeight
    )

    vert_bevelWeight: bpy.props.FloatProperty(
        description = "Vertex Bevel Weight",
        name        = "Set bevel Weight",
        min         = 0.0,
        max         = 1.0,
        step        = 0.1,
        default     = 0,
        update      = update_vert_bevelWeight
    )

    edge_Crease: bpy.props.FloatProperty(
        description = "Edge Crease",
        name        = "Set edge Crease",
        min         = 0.0,
        max         = 1.0,
        step        = 0.1,
        default     = 0,
        update      = update_edge_Crease
    )    

    vert_Crease: bpy.props.FloatProperty(
        description = "Vertex Crease",
        name        = "Set vertex Crease",
        min         = 0.0,
        max         = 1.0,
        step        = 0.1,
        default     = 0,
        update      = update_vert_Crease
    )


def get_edge_crease_selected():
    o  = bpy.context.object
    d  = o.data
    bm = bmesh.from_edit_mesh(d)

    creaseLayer = bm.edges.layers.crease.verify()

    selectedEdges = ""
    for e in bm.edges:
        if e.select:
            selectedEdges += (str(round(e[creaseLayer], 2)) + ' ')
    return selectedEdges

def get_edge_bevelWeight_selected():
    o  = bpy.context.object
    d  = o.data
    bm = bmesh.from_edit_mesh(d)

    bevelWeightLayer = bm.edges.layers.bevel_weight.verify()

    selectedEdges = ""
    for e in bm.edges:
        if e.select:
            selectedEdges += (str(round(e[bevelWeightLayer], 2)) + ' ')
    return selectedEdges

def get_vert_crease_selected():
    o  = bpy.context.object
    d  = o.data
    bm = bmesh.from_edit_mesh(d)

    creaseLayer = bm.verts.layers.crease.verify()

    selectedVerts = ""
    for v in bm.verts:
        if v.select:
            selectedVerts += (str(round(v[creaseLayer], 2)) + ' ')
    return selectedVerts

def get_vert_bevelWeight_selected():
    o  = bpy.context.object
    d  = o.data
    bm = bmesh.from_edit_mesh(d)

    bevelWeightLayer = bm.verts.layers.bevel_weight.verify()

    selectedVerts = ""
    for v in bm.verts:
        if v.select:
            selectedVerts += (str(round(v[bevelWeightLayer], 2)) + ' ')
    return selectedVerts

###########################################################################################
###################################### UI #################################################
###########################################################################################

class CAB_PT_Panel(Panel):
    bl_label = "Crease and Bevel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CaB'
 
    def draw(self, context):
        layout = self.layout
        props  = context.scene.CAB_PG_Prop # Create reference to property group
        
        # sel_mode[0] or sel_mode[1] or sel_mode[2]
        sel_mode = context.tool_settings.mesh_select_mode[:]
        
        col = layout.column(align = True)

        # if Vertex edit mode
        if context.active_object.mode == 'EDIT' and sel_mode[0] and len(get_vert_crease_selected()) != 0:
            col.label(text='Vertex edit mode:', icon='VERTEXSEL')
            bcol = col.box()
            bcol.label(text='Weight value: ' + get_vert_bevelWeight_selected())
            bcol.label(text='Crese value: ' + get_vert_crease_selected()) 
                       
            bcol.prop(props, "vert_bevelWeight")          
            bcol.prop(props, "vert_Crease")
        
        # if Edge edit mode
        elif context.active_object.mode == 'EDIT' and sel_mode[1] and len(get_edge_crease_selected()) != 0:
            col.label(text='Edge edit mode:', icon='EDGESEL')
            bcol = col.box()
            bcol.label(text='Weight value: ' + get_edge_bevelWeight_selected())
            bcol.label(text='Crese value: ' + get_edge_crease_selected())  
                      
            bcol.prop(props, "edge_bevelWeight")
            bcol.prop(props, "edge_Crease")
        
        # if other mode
        else:
            col.label(text='Need to select elements')
            col.label(text='in Vertex or Edge mode')
                              
###########################################################################################
##################################### Register ############################################
########################################################################################### 
 
classes = (
            CAB_PG_Prop,
            CAB_PT_Panel,
)

    
    bpy.types.Scene.CAB_PG_Prop = bpy.props.PointerProperty(type = CAB_PG_Prop)
    
'''
'''
import bpy
import bgl
import blf

def draw_callback_px(self, context):
    font_id = 0
    # 获取鼠标位置
    mouse_x, mouse_y = context.window_manager.mouse_pos
    # 设置文字大小
    blf.size(font_id, 20, 72)
    # 设置文字显示位置，稍微偏离鼠标位置以避免遮挡
    blf.position(font_id, mouse_x + 20, mouse_y - 20, 0)
    # 显示当前的Z轴移动值，限制显示的小数点后两位
    blf.draw(font_id, "Z-Axis Movement: %.2f" % self.mouse_dx)

class ModalOperator(bpy.types.Operator):
    bl_idname = "pie.modal_operator"
    bl_label = "Simple Modal Object Operator"
    
    # Declare properties as annotations
    mouse_dx: bpy.props.FloatProperty(default=0.0)  # Difference in mouse X position
    init_mouse_x: bpy.props.IntProperty(default=0)  # Initial mouse X position
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply movement based on mouse X movement
            delta = event.mouse_x - self.init_mouse_x
            # 计算新的Z轴移动值，并限制在0到1之间
            new_mouse_dx = self.mouse_dx + delta * 0.01  # Sensitivity factor
            self.mouse_dx = max(0.0, min(1.0, new_mouse_dx))
            # 应用新的Z轴位置
            context.object.location.z = self.mouse_dx
            self.init_mouse_x = event.mouse_x
            context.area.tag_redraw()  # Redraw the 3D view

        elif event.type == 'LEFTMOUSE':  # Confirm
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            context.object.location.z = 0.0  # Reset the location to initial value
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.init_mouse_x = event.mouse_x
            context.window_manager.modal_handler_add(self)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(ModalOperator)

def unregister():
    bpy.utils.unregister_class(ModalOperator)

if __name__ == "__main__":
    register()

    # test call
#    bpy.ops.object.modal_operator('INVOKE_DEFAULT')
'''


classes = [
    VIEW3D_PIE_MT_Bottom_E,
    PIE_Shift_E_KEY,
    PIE_Ctrl_Shift_E_KEY,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", 'E', 'CLICK_DRAG')
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_E"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", 'E', 'PRESS', shift = True)
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.ctrl_shift_e", 'E', 'PRESS',ctrl = True, shift = True)
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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_E")
