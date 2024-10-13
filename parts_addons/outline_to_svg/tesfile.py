import bpy
import bmesh
import mathutils
import time

context = bpy.context
ob = context.object
me = ob.data
bm = bmesh.new()
bm.from_mesh(me)

uv_layer = bm.loops.layers.uv.verify()
for face in bm.faces:
    fverts = []
    for loop in face.loops:
        uv = loop[uv_layer].uv
        uv.xy = mathutils.noise.random_unit_vector(size=2)

bm.to_mesh(me)