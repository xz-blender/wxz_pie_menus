# coding=utf-8
import bpy
from typing import List
from mathutils import Matrix
from mathutils import Vector

class NbSphereLatticeOperator(bpy.types.Operator):
    """编辑模式选择骨骼 添加球形范围控制"""
    bl_idname = "object.nbspherelatticeoperator"
    bl_label = "NB Sphere Lattice Ctrl"

    @classmethod
    def poll(cls, context):
        a=0
        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'EDIT_ARMATURE':
                    if len(context.selected_bones)>0:
                        a=1
        return a



    




    def execute(self, context):    
        def clamp(val, _min=0, _max=1) -> float or int:
            if val < _min:
                return _min
            if val > _max:
                return _max
            return val
    
    
        def adv_rename(string,insertname):
            suffixes = ["left", "right", "_l", "_r", ".l", ".r", "-l", "-r", " l", " r"]
            # 检查字符串是否以指定的后缀结尾
            if any(string.lower().endswith(suffix) for suffix in suffixes):
                # 找到后缀的位置
                suffix_index = len(string)
                for suffix in suffixes:
                    if string.lower().endswith(suffix):
                        suffix_index -= len(suffix)
                        break
                # 在后缀前插入"_mingcheng"
                newName = string[:suffix_index] + insertname + string[suffix_index:]             
            else:
                newName=string+ insertname 
            return newName
        
        def get_lattice_vertex_index(lattice: bpy.types.Lattice, xyz: List[int], do_clamp=True) -> int:
            """Get the index of a lattice vertex based on its position on the XYZ axes."""

            # The lattice vertex indicies start in the -Y, -X, -Z corner,
            # increase on X+, then moves to the next row on Y+, then moves up on Z+.
            res_x, res_y, res_z = lattice.points_u, lattice.points_v, lattice.points_w
            x, y, z = xyz[:]
            if do_clamp:
                x = clamp(x, 0, res_x)
                y = clamp(y, 0, res_y)
                z = clamp(z, 0, res_z)

            assert x < res_x and y < res_y and z < res_z, "Error: Lattice vertex xyz index out of bounds"

            index = (z * res_y*res_x) + (y * res_x) + x
            return index
        def ensure_falloff_vgroup(
                lattice_ob: bpy.types.Object,
                vg_name="Group", multiplier=1) -> bpy.types.VertexGroup:
            lattice = lattice_ob.data
            res_x, res_y, res_z = lattice.points_u, lattice.points_v, lattice.points_w

            vg = lattice_ob.vertex_groups.get(vg_name)

            center = Vector((res_x-1, res_y-1, res_z-1))/2
            max_res = max(res_x, res_y, res_z)

            if not vg:
                vg = lattice_ob.vertex_groups.new(name=vg_name)
            for x in range(res_x-4):
                for y in range(res_y-4):
                    for z in range(res_z-4):
                        index = get_lattice_vertex_index(lattice, (x+2, y+2, z+2))

                        coord = Vector((x+2, y+2, z+2))
                        distance_from_center = (coord-center).length
                        influence = 1 - distance_from_center / max_res * 2

                        vg.add([index], influence * multiplier, 'REPLACE')
            return vg
        
        
        
        
        MESH_s=[]
        for i in bpy.context.selected_objects:
            if i.type == 'MESH':
                MESH_s.append(i)


        cbs_sphere=bpy.data.objects.new("NB_sphere",None)
        cbs_sphere.empty_display_type = 'SPHERE'

        cbs_cube=bpy.data.objects.new("NB_cube",None)
        cbs_cube.empty_display_type = 'CUBE'





        obj =bpy.context.object
        arm =bpy.context.object.data
        bone_root =bpy.context.selected_bones[0]
        bon_dir=(bone_root.head-bone_root.tail).normalized()
        bon_len=(bone_root.head-bone_root.tail).length
        bone_root_name =bone_root.name



        bone_C_name =adv_rename(bone_root.name,"_NB_lattice_Ctrl")
        bone_C =arm.edit_bones.new(bone_C_name)
        bone_C.head =bone_root.head
        bone_C.tail =bone_root.tail
        bone_C.use_deform = False
        bone_C.roll=bone_root.roll
        bone_C.parent =bone_root

        lattice_name = bone_root.name
        lattice = bpy.data.lattices.new(lattice_name)
        lattice_ob = bpy.data.objects.new(lattice_name, lattice)
#        bpy.context.scene.collection.objects.link(lattice_ob)
        obj.users_collection[0].objects.link(lattice_ob)

        resolution = 10
        # Set resolution
        lattice_ob.data.points_u, lattice_ob.data.points_v, lattice_ob.data.points_w = 1, 1, 1
        lattice_ob.data.points_u, lattice_ob.data.points_v, lattice_ob.data.points_w = [resolution]*3

        # Create a falloff vertex group
        vg = ensure_falloff_vgroup(lattice_ob, vg_name="Hook", multiplier=1.5)

        # Parent lattice to the generated rig
        lattice_ob.parent = obj
        # Bone-parent lattice to root bone
        lattice_ob.parent_type = 'BONE'
        lattice_ob.parent_bone = bone_root.name
#        lattice_ob.matrix_world = bone_root.matrix
        lattice_ob.matrix_world = lattice_ob.matrix_world @ Matrix.Scale(bon_len*2*obj.scale[2], 4)
        lattice_ob.location[1] = -bon_len
        lattice_ob.location[0] =0
        lattice_ob.location[2] =0
        lattice_ob.rotation_euler[0] = 0
        lattice_ob.rotation_euler[1] = 0
        lattice_ob.rotation_euler[2] = 0


        lattice_ob.lock_location[0] = True
        lattice_ob.lock_location[1] = True
        lattice_ob.lock_location[2] = True
        lattice_ob.lock_rotation[0] = True
        lattice_ob.lock_rotation[1] = True
        lattice_ob.lock_rotation[2] = True
        lattice_ob.lock_scale[0] = True
        lattice_ob.lock_scale[1] = True
        lattice_ob.lock_scale[2] = True



        #self.lock_transforms(lattice_ob)

        

        bpy.ops.object.mode_set(mode='POSE')

        obj.pose.bones.get(bone_root_name).custom_shape = cbs_cube
        obj.pose.bones.get(bone_C_name).custom_shape = cbs_sphere

        # Add Hook modifier to the lattice
        hook_mod = lattice_ob.modifiers.new(name="Hook", type='HOOK')
        hook_mod.object = obj
        hook_mod.vertex_group = vg.name
        hook_mod.subtarget = bone_C_name

        

        if len(MESH_s)>0:
            for i in MESH_s:
                haslattice=0
                for j in i.modifiers[:]:
                    if j.type =='LATTICE':
                        if j.object==lattice_ob:
                            haslattice =1
                if haslattice==0: 
                    mod_lattice = i.modifiers.new(lattice_ob.name, 'LATTICE')
                    mod_lattice.object = lattice_ob    
                
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}











classes=(
NbSphereLatticeOperator,
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






