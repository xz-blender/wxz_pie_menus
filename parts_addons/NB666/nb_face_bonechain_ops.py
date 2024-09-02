import bpy
import math 
import bmesh
import mathutils 

class NB_FaceToBoneChain_Operator(bpy.types.Operator):
    """选择骨架 加选条带模型 进入编辑模式 选择模型一端的面 点击创建骨骼链"""
    bl_idname = "object.nbfacetobonevhainoperator"
    bl_label = "Face To Bone Chain"
    
    
    @classmethod
    def poll(cls, context):
        a=0

        if len(bpy.context.selected_objects)==2:
            if context.active_object.type == 'MESH':
                if bpy.context.mode =='EDIT_MESH':
                    for i in bpy.context.selected_objects:
                        if i.type =='ARMATURE':
                            a=1
                            break

        return a

    def execute(self, context):

        # 获取当前选择的对象
        obj = bpy.context.active_object
        for i in bpy.context.selected_objects:
            if i.type =='ARMATURE':
                armature_object = i
        bpy.ops.object.mode_set(mode='OBJECT')
        # 获取当前激活的面

        active_face = obj.data.polygons[obj.data.polygons.active]
        


        adjacent_edges_count =0
        for edge_key in active_face.edge_keys: 
            for face in obj.data.polygons:
                if edge_key in face.edge_keys and face != active_face and len(face.vertices) == 4:
                    adjacent_faces=face
                    adjacent_edges_count+=1
                    
        if adjacent_edges_count ==1:

            oedge_keys=[]
            useedge_keys=[]
            co_s=[]
            normals=[]
            face_s=[]
            def faceCreate_bone(rootface):
                adjacent_faces = None
                
                
                adjacent_edges_count =0
                for edge_key in rootface.edge_keys: 
                    for face in obj.data.polygons:
                        if edge_key in face.edge_keys and face != rootface and edge_key not in oedge_keys and len(face.vertices) == 4:
                            adjacent_faces=face
                            adjacent_edges_count+=1
                            useedge_keys.append(edge_key) 
                            co0=obj.data.vertices[edge_key[0]].co
                            co1=obj.data.vertices[edge_key[1]].co
                            co=(co0+co1)/2
                            co_s.append(co) 
                            face_s.append(face) 
                            normals.append(face.normal) 
                                                        
                    oedge_keys.append(edge_key)
            #    print(adjacent_edges_count)
                    
                if adjacent_faces == None or adjacent_edges_count !=1:
                    return
                else:
            #        adjacent_faces.select=1          
            #        print(adjacent_faces.index)
                    faceCreate_bone(adjacent_faces) 
                    
                    
            # 检查面是否为四边形
            if len(active_face.vertices) == 4:
                normals.append(active_face.normal)  
                faceCreate_bone(active_face)
            #print(useedge_keys)
            if face_s:
                for edge_key in active_face.edge_keys: 
                    if useedge_keys[0][0] not in edge_key and useedge_keys[0][1] not in edge_key:
                        useedge_keys.insert(0,edge_key) 
                        co0=obj.data.vertices[edge_key[0]].co
                        co1=obj.data.vertices[edge_key[1]].co
                        co=(co0+co1)/2
                        co_s.insert(0,co) 
                        break

                for edge_key in face_s[-1].edge_keys: 
                #    print(edge_key)
                    if useedge_keys[-1][0] not in edge_key and useedge_keys[-1][1] not in edge_key :
                        useedge_keys.append(edge_key) 
                        co0=obj.data.vertices[edge_key[0]].co
                        co1=obj.data.vertices[edge_key[1]].co
                        co=(co0+co1)/2
                        co_s.append(co) 
                        break


                #print(co_s)
                #print(face_s[-1].index)
                #print(normals)
                #print(useedge_keys)

                bpy.context.view_layer.objects.active = armature_object
                    

                bpy.ops.object.mode_set(mode='EDIT')
                bonelist =[]
                for i, normal in enumerate(normals):
                    # 获取顶点坐标

                    # 在骨骼下创建骨骼头
                    bone = armature_object.data.edit_bones.new(name="Bone")
                    bone.head = obj.matrix_world @ co_s[i]
                    bone.tail = obj.matrix_world @ co_s[i+1]

                    bone.align_roll(normal)
                    bonelist.append(bone)
                    
                for i, bone in enumerate(bonelist):
                    if i <len(bonelist)-1:
                        bonelist[i+1].parent = bone
                        bonelist[i+1].use_connect = True




                bpy.ops.object.mode_set(mode='OBJECT')

                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}




classes=(
NB_FaceToBoneChain_Operator,
)

## 注册插件
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

## 注销插件
def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

## 在启动时注册插件
if __name__ == "__main__":
    register()






