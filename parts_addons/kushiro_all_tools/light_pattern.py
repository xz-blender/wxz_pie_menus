bl_info = {
    "name": "Light Pattern",
    "description": "Create a light with masking plane",
    "author": "Kushiro",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Light",
    "category": "Mesh",
}
import bpy

class LightPatternOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.light_pattern"
    bl_label = "Add light pattern —— 添加灯光纹理"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"

    def create_light(self, context):
        print('add light')
        light_data = bpy.data.lights.new(name="light_texture", type='POINT')
        light_data.energy = 1000000
        light_data.shadow_soft_size = 0.7

        light_object = bpy.data.objects.new(name="light_texture", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object
        light_object.location = (0, 0, 70)

        bpy.ops.mesh.primitive_plane_add(size=40.0, calc_uvs=True, enter_editmode=False,
            align='WORLD', location=[0, 0, 50], 
            rotation=[0,0,0], scale=[1, 1, 1])

        plane = bpy.context.active_object
        plane.parent = light_object
        plane.matrix_parent_inverse = light_object.matrix_world.inverted()

        dg = bpy.context.evaluated_depsgraph_get() 
        dg.update()

        material = bpy.data.materials.new(name="light_texture_material")
        material.use_nodes = True

        # Remove default
        material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
        material_output = material.node_tree.nodes.get('Material Output')
        material_output.location = (1000,0)

        trans = material.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        trans.location = (800,0)

        ramp = material.node_tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = (0.5)
        ramp.color_ramp.elements[1].position = (1.0)
        ramp.location = (500,0)

        material.node_tree.links.new(trans.inputs[0], ramp.outputs[0])

        wave = material.node_tree.nodes.new("ShaderNodeTexWave")
        wave.inputs['Scale'].default_value = 10
        wave.location = (0,0)

        material.node_tree.links.new(ramp.inputs[0], wave.outputs[0])
        noise = material.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.location = (0,300)
        noise.inputs['Scale'].default_value = 30
        noise.inputs['Distortion'].default_value = 10
        #material.node_tree.links.new(ramp.inputs[0], noise.outputs[0])

        image = material.node_tree.nodes.new("ShaderNodeTexImage")
        image.location = (0,-400)

        mapping = material.node_tree.nodes.new("ShaderNodeMapping")
        mapping.location = (-200, 0)
        material.node_tree.links.new(noise.inputs[0], mapping.outputs[0])
        material.node_tree.links.new(wave.inputs[0], mapping.outputs[0])
        material.node_tree.links.new(image.inputs[0], mapping.outputs[0])

        cod = material.node_tree.nodes.new("ShaderNodeTexCoord")
        cod.location = (-400, 0)
        material.node_tree.links.new(mapping.inputs[0], cod.outputs[0])
        material.node_tree.links.new(material_output.inputs[0], trans.outputs[0])
        plane.active_material = material
            
    def __init__(self):
        pass

    def execute(self, context):
        # bpy.ops.object.mode_set(mode='OBJECT')
        #self.report({'INFO'}, self.toolmode)
        self.create_light(context)
        return {'FINISHED'}   