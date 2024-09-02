import bpy

class Prop_nb_666_autoweight(bpy.types.PropertyGroup):
    
    Armature_Object: bpy.props.PointerProperty(type=bpy.types.Object, name="Object",poll=lambda self, object: object.type == 'ARMATURE')
#    n: bpy.props.BoolProperty(name="n")
#    cuoFrame: bpy.props.IntProperty(default=1, name="Frame", min=-10,max =10)
#    cInfluence: bpy.props.FloatProperty(default=1.0, name="Influence",min=0,max =1)
    switch_state: bpy.props.StringProperty(default='A')
#    arm_display_type: bpy.props.StringProperty(default='ShaYeBuShi')
    vertexSel: bpy.props.BoolProperty(name="vertexSel",default=False)
    
class NBSwitchOperator(bpy.types.Operator):
    """自动权重to bone"""
    bl_idname = "object.nb_rigswitch_operator"
    bl_label = "NB 自动权重Switch Operator"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        a=0

        if len(context.selected_objects)>0:
            for i in bpy.context.selected_objects:
                if i.type == 'ARMATURE' or 'MESH':
                    a=1
            
        return a
    
    def execute(self, context):
        
        MESH_s=[]
        ARMATURE_s=[]
        if bpy.context.mode =='EDIT_MESH':
            bpy.context.scene.Prop_nb_666_autoweight.vertexSel = True

        for i in bpy.context.selected_objects:
            if i.type == 'ARMATURE':
                ARMATURE_s.append(i)
            if i.type == 'MESH':
                MESH_s.append(i)
                
        if getattr(bpy.context.scene.Prop_nb_666_autoweight, 'switch_state', None) == 'A':
#            print("A")
            
            if len(ARMATURE_s)==1:  
                bpy.context.view_layer.objects.active=ARMATURE_s[0]
                bpy.context.scene.Prop_nb_666_autoweight.Armature_Object=ARMATURE_s[0]
                bpy.ops.object.mode_set(mode='POSE')
                bpy.context.object.show_in_front = True
                ARMATURE_s[0].data.display_type = 'OCTAHEDRAL'
                bpy.context.scene.Prop_nb_666_autoweight.switch_state = 'B'
                self.report({'INFO'}, "骨骼姿态")  
            armObj=bpy.context.scene.Prop_nb_666_autoweight.Armature_Object
            if len(ARMATURE_s)==0 and armObj: 
                if armObj in bpy.context.view_layer.objects[:]:
                    bpy.context.view_layer.objects.active=armObj
                    armObj.data.display_type = 'OCTAHEDRAL'
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.context.object.show_in_front = True
                    bpy.context.scene.Prop_nb_666_autoweight.switch_state = 'B'
                    self.report({'INFO'}, "骨骼姿态")  
            
            
            
        elif getattr(bpy.context.scene.Prop_nb_666_autoweight, 'switch_state', None) == 'B':
#            print("B")
            self.report({'INFO'}, "物体")  
            bpy.ops.object.mode_set(mode='OBJECT')
            armObj=bpy.context.scene.Prop_nb_666_autoweight.Armature_Object

            
            armObj.data.display_type = 'WIRE'  
            
            if len(context.selected_objects)==1 and len(ARMATURE_s)==1:
                for bone in ARMATURE_s[0].pose.bones[:]:
                    bone.rotation_mode = 'XYZ'

                if ARMATURE_s[0].data.display_type =='WIRE':
                    ARMATURE_s[0].data.display_type ='BBONE'
                else:
                    ARMATURE_s[0].data.display_type ='OCTAHEDRAL'

            
            
            bpy.ops.object.select_all(action='DESELECT')

            for i in MESH_s: 
                if i.find_armature() == armObj:
                    bpy.context.view_layer.objects.active=i      
                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                    i.data.use_paint_mask = False
                    i.data.use_paint_mask_vertex = False
                    if bpy.context.scene.Prop_nb_666_autoweight.vertexSel:
                        i.data.use_paint_mask_vertex = True
                        bpy.context.scene.Prop_nb_666_autoweight.vertexSel=False
                    bpy.ops.paint.weight_from_bones(type='AUTOMATIC')
                    bpy.ops.object.vertex_group_smooth(group_select_mode='ACTIVE', factor=0.01, repeat=1, expand=0)
                    self.report({'INFO'}, i.name+"牛逼_自动权重")           
                    
                if i.find_armature() != armObj:
                    if armObj in bpy.context.view_layer.objects[:]:         
                        bpy.context.view_layer.objects.active=armObj
                        i.select_set(1)
                        bpy.ops.object.parent_set(type='ARMATURE')
                        i.modifiers[:][len(i.modifiers[:])-1].use_deform_preserve_volume = True

                        if i.modifiers[:][len(i.modifiers[:])-2].type=='SUBSURF':
                            i.modifiers.move(len(i.modifiers[:])-1,len(i.modifiers[:])-2)
                        
                                
                        i.select_set(0)
                        self.report({'INFO'}, i.name+"牛逼_添加骨架变形(无权重)")
                 
           
                
            bpy.ops.object.mode_set(mode='OBJECT')

            
            bpy.context.scene.Prop_nb_666_autoweight.switch_state = 'A'
        else:
            bpy.context.scene.Prop_nb_666_autoweight.switch_state = 'A'
            
            
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}




addon_keymaps = []

classes=(
NBSwitchOperator,
Prop_nb_666_autoweight,
)

## 注册插件
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Prop_nb_666_autoweight = bpy.props.PointerProperty(type=Prop_nb_666_autoweight)

    
    
    # 添加快捷键
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')
    kmi = km.keymap_items.new(NBSwitchOperator.bl_idname, 'F5', 'PRESS', ctrl=False, shift=False,alt=False,)
    addon_keymaps.append((km, kmi))
    
## 注销插件
def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.Prop_nb_666_autoweight
    
    # 移除快捷键
    wm = bpy.context.window_manager
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
## 在启动时注册插件
if __name__ == "__main__":
    register()



