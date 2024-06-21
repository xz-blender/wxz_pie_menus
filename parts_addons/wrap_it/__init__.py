# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	'name': 'Wrap It',
	'author': 'Ian Lloyd Dela Cruz',
	'version': (1, 0, 0),
	'blender': (4, 1, 0),
	'location': '3d View > Shift A Mesh Menu',
	'description': 'More free stuff for Blender: https://t.me/cgplugin',
	'warning': '',
	'wiki_url': '',
	'doc_url': 'https://www.blenderguppy.com/add-ons/wrap-it',
	'tracker_url': 'https://www.blenderguppy.com/add-ons/help-and-support',
	'category': 'Mesh'}

import bpy
import bmesh
from math import *
from mathutils import *
from bpy.props import *
from bpy.types import (
		AddonPreferences,
		PropertyGroup,
		Operator,
		Menu,
		Panel,
		)

def get_eval_mesh(obj):

	depsgraph = bpy.context.evaluated_depsgraph_get()
	obj_eval = obj.evaluated_get(depsgraph)

	return obj_eval.to_mesh()

def duplicate_obj(name, copy_obj, get_eval=True, link=True):

	new_mesh = bpy.data.meshes.new(name)
	new_obj = bpy.data.objects.new(name, new_mesh)
	new_obj.data = get_eval_mesh(copy_obj).copy() \
		if (copy_obj.type != 'MESH' or get_eval) else copy_obj.data.copy()
	new_obj.scale = copy_obj.scale
	new_obj.rotation_euler = copy_obj.rotation_euler
	new_obj.location = copy_obj.location

	if link:
		bpy.context.scene.collection.objects.link(new_obj)
		new_obj.select_set(True)

	return new_obj

def remove_obj(obj, clear_data=True):

	sce = bpy.context.scene
	in_master = True

	for c in bpy.data.collections:
		if obj.name in c.objects:
			c.objects.unlink(obj)
			in_master = False
			break

	if in_master:
		if obj.name in sce.collection.objects:
			sce.collection.objects.unlink(obj)

	if clear_data: bpy.data.objects.remove(obj)

def new_object(obj, data, name):

	new_obj = bpy.data.objects.new(name, data)
	new_obj.data.shade_smooth()

	return new_obj

def origin_to_geo(obj):

	mesh = obj.data
	mat_world = obj.matrix_world

	origin = sum((v.co for v in mesh.vertices), Vector()) / len(mesh.vertices)

	mesh.transform(Matrix.Translation(-origin))
	mat_world.translation = mat_world @ origin

class MESH_OT_wrap_it(Operator):
	'''Simulates wrapping objects in plastic'''
	bl_idname = 'wrap_it.bga'
	bl_label = 'Wrap It'
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	mesh_offset : FloatProperty(
		name        = "Mesh Offset",
		description = "Offset of mesh vertices",
		default     = 0,
		min         = 0.0,
		soft_max    = 10.0,
		step        = 0.1,
		precision   = 4
		)
	sw_offset : FloatProperty(
		name        = "Shrinkwrap Offset",
		description = "Distance to keep from the target",
		default     = 0.0,
		min         = -100,
		max         = 100,
		step        = 0.1,
		precision   = 4
		)
	res_mode : EnumProperty(
		name = 'Resolution',
		description = "Use subdivision or remesh for increasing resolution",
		items = (
			('SUBDIV', 'Subdivision','Use subdivision modifier to increase resolution'),
			('REMESH', 'Remesh','Use remesh modifier to increase resolution')),
		default = 'SUBDIV'
		)
	wr_method : EnumProperty(
		name = 'Wrap Method',
		description = "Shrinkwrap method",
		items = (
			('NEAREST_SURFACEPOINT', 'Nearest Surface Point','Shrink the mesh to the nearest target surface'),
			('NEAREST_VERTEX', 'Nearest Vertex','Shrink the mesh to the nearest target vertex'),
			('TARGET_PROJECT', 'Target Normal Project','Shrink the mesh to the nearest target surface along the interpolated vertex normal of the target')),
		default = 'NEAREST_SURFACEPOINT'
		)
	sw_mode : EnumProperty(
		name = 'Wrap Mode',
		description = "Determines how vertices are constrained to the target surface",
		items = (
			('ON_SURFACE', 'On Surface','The point is constrained to the surface of the target object, with distance offset towards the original point location'),
			('INSIDE', 'Inside','The point is constrained to be inside the target object'),
			('OUTSIDE', 'Outside','The point is constrained to be outside the target object'),
			('OUTSIDE_SURFACE', 'Outside Surface','The point is constrained to the surface of the target object, with distance offset always to the outside, towards or away from the original location'),
			('ABOVE_SURFACE', 'Above Surface','The point is constrained to the surface of the target object, with distance offset applied exactly along the target normal')),
		default = 'ON_SURFACE'
		)
	subd_lvl : IntProperty(
		name        = "Subdivision",
		description = "Number of subdivisions to perform",
		default     = 0,
		min         = 0,
		soft_max    = 6,
		max         = 11,
		step        = 1
		)
	vox_size1 : FloatProperty(
		name        = "Voxel Size",
		description = "Size of the voxel in object space used for volume evaluation. Lover values preseve finer details",
		default     = 0.1,
		min         = 0.0001,
		soft_min    = 0.01,
		soft_max    = 2,
		step        = 0.1,
		precision   = 4
		)
	vox_size2 : FloatProperty(
		name        = "Voxel Size",
		description = "Size of the voxel in object space used for volume evaluation. Lover values preseve finer details",
		default     = 0.1,
		min         = 0.0001,
		soft_min    = 0.01,
		soft_max    = 2,
		step        = 0.1,
		precision   = 4
		)
	smooth_factor1 : FloatProperty(
		name        = "Smooth Factor",
		description = "Strength of smoothing",
		default     = 0.5,
		soft_min    = -10.0,
		soft_max    = 10.0,
		step        = 0.1,
		precision   = 3
		)
	smooth_iter1 : IntProperty(
		name        = "Smooth Repeat",
		description = "Smooth iteration",
		default     = 0,
		min         = 0,
		soft_max    = 100,
		step        = 1
		)
	smooth_factor2 : FloatProperty(
		name        = "Smooth",
		description = "Strength of smoothing",
		default     = 0.5,
		soft_min    = -10.0,
		soft_max    = 10.0,
		step        = 0.1,
		precision   = 3
		)
	smooth_iter2 : IntProperty(
		name        = "Repeat",
		description = "Smooth iteration",
		default     = 0,
		min         = 0,
		soft_max    = 100,
		step        = 1
		)
	wire_thickness : FloatProperty(
		name        = "Wire Thickness",
		description = "Thickness of the wireframe",
		default     = 0.02,
		min         = 0,
		soft_max    = 1.0,
		step        = 0.1,
		precision   = 3
		)
	limit_angle : FloatProperty(
		name        = "Simplify",
		description = "Limit dissolve angle to reduce the shrinkwrap target resolution, making the shrinkwrap faster",
		default     = radians(5),
		min         = 0,
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	use_material : BoolProperty(
		name        = "Add Shader",
		description = "Add simple see through shader",
		default     = True
		)
	post_remesh : BoolProperty(
		name        = "Post Remesh",
		description = "Add remesh modifier after resolution and shrinkwrap effects",
		default     = False
		)
	use_wire : BoolProperty(
		name        = "Wireframe",
		description = "Use wireframe modifier",
		default     = False
		)

	@classmethod
	def poll(cls, context):

		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def add_base_mods(self, obj, target):

		mod = obj.modifiers

		if self.res_mode == 'REMESH':
			md = mod.new('Remesh', 'REMESH')
			md.voxel_size = self.vox_size1
			md.use_smooth_shade = True
		else:
			md = mod.new('Subdivision', 'SUBSURF')
			md.subdivision_type = 'SIMPLE'
			md.levels = self.subd_lvl
			md.render_levels = self.subd_lvl

		md = obj.modifiers.new("Shrinkwrap", "SHRINKWRAP")
		md.target = target
		md.offset = self.sw_offset
		md.wrap_method = self.wr_method
		md.wrap_mode = self.sw_mode
        
		md = mod.new('Smooth', 'SMOOTH')
		md.factor = self.smooth_factor1
		md.iterations = self.smooth_iter1

		if self.post_remesh:
			md = mod.new('Remesh', 'REMESH')
			md.voxel_size = self.vox_size2
			md.use_smooth_shade = True

			md = mod.new('Smooth', 'SMOOTH')
			md.factor = self.smooth_factor2
			md.iterations = self.smooth_iter2

		if self.use_wire:
			md = mod.new('Wireframe', 'WIREFRAME')
			md.thickness = self.wire_thickness
			md.use_even_offset = False

	def clear_proxies(self):

		sw_objs = [o.name for o in bpy.data.objects if o.use_fake_user \
			and "target_obj" in o.name]

		for o in bpy.context.scene.objects:
			for m in o.modifiers:
				if m.type == 'SHRINKWRAP':
					if m.target:
						name = m.target.name
						if name in sw_objs:
							sw_objs.remove(name)

		if self.show_info:
			self.report({'INFO'}, "Removed " + str(len(sw_objs)) + " unused target proxy object(s).")
			self.show_info = False

		for n in sw_objs:
			if n in bpy.data.objects:
				bpy.data.objects.remove(bpy.data.objects[n])

	def create_proxy(self, obj):

		# target = duplicate_obj(obj.name + "_proxy", obj, get_eval=True)
		obj.data = get_eval_mesh(obj).copy()

		obj.modifiers.clear()
		obj.data.materials.clear()

		obj.use_fake_user = True
		remove_obj(obj, clear_data=False)

		return obj

	def add_material(self, obj):

		new_mat = bpy.data.materials.get("plastic_wrap") or bpy.data.materials.new(name="plastic_wrap")

		mat = obj.data.materials
		mat.clear()
		mat.append(new_mat)

		new_mat.use_nodes = True
		ntree = new_mat.node_tree

		for node in ntree.nodes:
			if node.type == "BSDF_PRINCIPLED":
				node.inputs[2].default_value = 0.2
				node.inputs[3].default_value = 1.2
				node.inputs[17].default_value = 1.0
				break

	def execute(self, context):

		obj = context.active_object

		bm = bmesh.new()
		wrap_mesh = bpy.data.meshes.new(".temp")

		bm_target = bmesh.new()
		target_mesh = bpy.data.meshes.new(".temp")

		for o in context.selected_objects:
			if o.type == 'MESH':
				eval_mesh = get_eval_mesh(o)
				eval_mesh.transform(o.matrix_world)
				bm.from_mesh(eval_mesh)
				bm_target.from_mesh(eval_mesh)

		bmesh.ops.dissolve_limit(bm_target, angle_limit=self.limit_angle,
			use_dissolve_boundaries=False, verts=bm_target.verts, edges=bm_target.edges, delimit={'NORMAL'})

		bm_target.to_mesh(target_mesh)
		bm_target.free()

		dup_obj = new_object(obj, target_mesh, "target_obj")

		ch = bmesh.ops.convex_hull(bm, input=bm.verts)

		bmesh.ops.delete(bm, geom=ch["geom_unused"] + ch["geom_interior"], context='VERTS')

		if self.mesh_offset:
			for v in bm.verts:
				v.co += v.normal * (v.calc_shell_factor() * self.mesh_offset)

		bm.to_mesh(wrap_mesh)
		bm.free()

		target_obj = self.create_proxy(dup_obj)

		wrap_obj = new_object(obj, wrap_mesh, "wrap_it")

		for col in obj.users_collection:
			if not wrap_obj.name in col.objects: col.objects.link(wrap_obj)

		origin_to_geo(wrap_obj)

		self.add_base_mods(wrap_obj, target_obj)

		if self.use_material:
			self.add_material(wrap_obj)

		self.clear_proxies()

		return {'FINISHED'}

	def draw(self, context):

		layout = self.layout
		col = layout.column()
		col.separator(factor=0.1)
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Mesh Offset:")
		row.row(align=True).prop(self, "mesh_offset", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="SWrap Offset:")
		row.row(align=True).prop(self, "sw_offset", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Wrap Method:")
		row.row(align=True).prop(self, "wr_method", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Wrap Mode:")
		row.row(align=True).prop(self, "sw_mode", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Resolution:")
		row.row(align=True).prop(self, "res_mode", expand=True)
		if self.res_mode == 'REMESH':
			row = col.row().split(factor=0.27, align=True)
			row.label(text="Voxel Size:")
			row.row(align=True).prop(self, "vox_size1", text="")
		else:
			row = col.row().split(factor=0.27, align=True)
			row.label(text="Subd Level:")
			row.row(align=True).prop(self, "subd_lvl", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Smooth:")
		row.row(align=True).prop(self, "smooth_factor1", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Repeat:")
		row.row(align=True).prop(self, "smooth_iter1", text="")
		row = col.row().split(factor=0.27, align=True)
		row.label(text="Simplify:")
		row.row(align=True).prop(self, "limit_angle", text="")
		col.separator(factor=0.5)
		col.prop(self, "use_material")
		col.prop(self, "post_remesh")
		if self.post_remesh:
			col.prop(self, "vox_size2")
			col.prop(self, "smooth_factor2")
			col.prop(self, "smooth_iter2")
		col.prop(self, "use_wire")
		if self.use_wire:
			col.prop(self, "wire_thickness")

	def invoke(self, context, event):

		self.show_info = True

		return context.window_manager.invoke_props_dialog(self)

def draw_wrap_it_menu(self, context):
	layout = self.layout
	layout.operator_context = 'INVOKE_REGION_WIN'
	layout.separator()
	layout.operator("wrap_it.bga", text="Wrap It", icon="MOD_SHRINKWRAP")
	layout.separator()

classes = (
	MESH_OT_wrap_it,
	)

def register():
	from bpy.utils import register_class

	for cls in classes:
		register_class(cls)

	bpy.types.VIEW3D_MT_mesh_add.prepend(draw_wrap_it_menu)

def unregister():
	from bpy.utils import unregister_class

	for cls in reversed(classes):
		unregister_class(cls)

	bpy.types.VIEW3D_MT_mesh_add.remove(draw_wrap_it_menu)