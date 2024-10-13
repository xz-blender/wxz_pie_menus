from typing import List, Union, Tuple
import sys

import bpy
import bmesh
from bpy.types import Material, Context
from bpy_extras.view3d_utils import (
    location_3d_to_region_2d,
    region_2d_to_location_3d,
    region_2d_to_origin_3d,
    region_2d_to_vector_3d,
)
from mathutils import Vector, Matrix, bvhtree
from mathutils.bvhtree import BVHTree
import numpy as np

from shapely.geometry import Polygon
from bmesh.types import BMFace
from . import context_poll
from .obj_info import get_material_index


def is_point_obscurred(bvh: BVHTree, co: Vector, view: Vector):
    """Ray from co to view and and return True if no hit"""
    distance = (view - co).length
    direction = (view - co).normalized()
    result = bvh.ray_cast(co, direction, distance)
    return None in result


def is_backface(
    viewpoint: Vector,
    view_normal: Vector,
    face: BMFace,
    bvh: BVHTree,
    check_obscured: bool = False,
    ortho: bool = False,
):
    if ortho:
        return view_normal.dot(face.normal) < 0.0

    origin = face.verts[0].co
    ray = viewpoint - origin
    ray_dir = ray.normalized()
    distance = ray.length
    ray_result = bvh.ray_cast(origin, ray_dir, distance)
    dot = face.normal.dot(view_normal)
    is_facing = dot < 0.0

    if check_obscured:
        return all((None not in ray_result, is_facing))
    return is_facing


def get_flattened_faces(
    ctx: Context,
    targets: Union[List[bpy.types.Object], bpy.types.Object],
    xform: Matrix = Matrix(),
    screenspace: bool = False,
    material_mask: Union[Material, None] = None,
    only_visible: bool = False,
) -> List[List[Vector]]:
    if not isinstance(targets, list):
        targets = [targets]

    dg = ctx.evaluated_depsgraph_get()
    bm = bmesh.new()

    # Add all targeted objects to current bm
    for obj in targets:
        add_evaled_mesh(bm, dg, obj, True, material_mask)

    bm.normal_update()

    faces = []

    if only_visible:
        bvh = BVHTree.FromBMesh(bm)
        is_ortho = context_poll.view3d_is_orthographic(ctx)

        if context_poll.view3d_is_camera(ctx):
            cam = ctx.scene.camera
            cam_loc = cam.matrix_world.translation
            cam_normal = (cam.matrix_world @ Vector((0, 0, -1))).normalized()
        else:
            area = ctx.area
            rv3d = area.spaces[0].region_3d
            cam_loc = rv3d.view_location
            cam_normal = (rv3d.view_rotation @ Vector((0, 0, -1))).normalized()

    for face in bm.faces:
        if only_visible:
            if is_backface(cam_loc, cam_normal, face, bvh, ortho=is_ortho):
                bm.faces.remove(face)
                continue

        if screenspace:
            face_points = (get_point_in_screenspace(v.co, ctx) for v in face.verts)
        else:
            face_points = (xform @ vert.co for vert in face.verts)
        face_points = [point.to_2d() for point in face_points]

        # Correct flip
        for p in face_points:
            p.y *= -1

        faces.append(face_points)
    bm.free()

    return faces


def faces_to_polygons(face_set: List[List[Vector]]):
    """Convert list of face points to shapely polyon"""
    polygons = []
    for face in face_set:

        pts = []
        for point in face:
            # TODO: Hacky fix, find actual source of problem
            # point.y *= -1
            pts.append(point.to_tuple())
        # pts.append(face[-1])

        polygon = Polygon(pts)
        polygons.append(polygon)

    return polygons


def add_evaled_mesh(
    bm: bmesh.types.BMesh,
    dg: bpy.types.Depsgraph,
    obj: bpy.types.Object,
    to_world: bool = True,
    material_mask: Union[Material, None] = None,
):
    object_eval = obj.evaluated_get(dg)
    mesh_from_eval = object_eval.to_mesh()
    if to_world:
        for v in mesh_from_eval.vertices:
            v.co = object_eval.matrix_world @ v.co

    if material_mask:
        material_index = get_material_index(obj, material_mask)
        # print("foesn", material_mask, material_index)

        mask_bm = bmesh.new()
        mask_bm.from_mesh(mesh_from_eval)
        for f in mask_bm.faces:
            if f.material_index != material_index:
                mask_bm.faces.remove(f)
        mask_bm.to_mesh(mesh_from_eval)
        mask_bm.free()

    bm.from_mesh(mesh_from_eval)

    # Remove temporary mesh.
    object_eval.to_mesh_clear()
    return None


def get_point_in_screenspace(co: Vector, context: Context):
    area = context.area

    # find window region
    window_region = next(region for region in area.regions if region.type == "WINDOW")
    rv3d = area.spaces[0].region_3d

    # TODO: Has this function changed is 4.0?
    location = location_3d_to_region_2d(window_region, rv3d, co, default=None)
    # print(co, location)
    return location


def vector_bbox(vectors: List[Vector]):
    # Get bounds x
    vectors.sort(key=lambda v: v.x)
    min_x, max_x = vectors[0].x, vectors[-1].x

    # Get bounds y
    vectors.sort(key=lambda v: v.y)
    min_y, max_y = vectors[0].y, vectors[-1].y

    min_xy = Vector((min_x, min_y))
    max_xy = Vector((max_x, max_y))
    return min_xy, max_xy


def get_camera_frame(
    context: Context, transform: Matrix = Matrix(), flatten: bool = True
) -> Polygon:
    # Apply camera crop
    camera = context.scene.camera
    cam_frame_local = camera.data.view_frame(scene=context.scene)

    # Apply frame aspect ratio
    width = context.scene.render.resolution_x
    height = context.scene.render.resolution_y

    # if width > height:
    #     aspect_correction = Vector((1.0, height / width, 1.0))
    # else:
    #     aspect_correction = Vector((width / height, 1.0, 1.0))
    # for v in cam_frame_local:
    #     v *= aspect_correction

    cam_frame_world = [camera.matrix_world @ v for v in cam_frame_local]
    cam_frame_world = [transform @ v for v in cam_frame_world]

    if flatten:
        cam_frame_world = [pt.to_2d() for pt in cam_frame_world]

    return cam_frame_world


def get_camera_normal(context: Context) -> Vector:
    area = context.area
    region = area.regions[5]
    rv3d = area.spaces[0].region_3d
    width = region.width
    height = region.height

    viewport_center = Vector((width / 2, height / 2))
    cam_normal = region_2d_to_vector_3d(region, rv3d, viewport_center)
    return cam_normal


def get_objects_centroid(objects: List[bpy.types.Object]) -> Vector:
    bound_maximums = get_bounds_of_objects(objects)
    bound_center = (bound_maximums[0] + bound_maximums[1]) * 0.5
    return bound_center


def get_bounds_of_objects(objects) -> Tuple[Vector, Vector]:
    """Return maximum bounding box of objects pair of vectors (vMin, vMax)"""
    bound_points_world = []
    for obj in objects:
        # Get each objects bounding box point in world space and append to bound_points_world
        bound_points_local = [Vector(point) for point in obj.bound_box]
        bound_points_world += [obj.matrix_world @ point for point in bound_points_local]

    # Convert to numpy array and get min, max values for each axis
    bound_points_world = np.array(bound_points_world)
    x_values = bound_points_world[:, 0]
    y_values = bound_points_world[:, 1]
    z_values = bound_points_world[:, 2]

    # Get extremes
    x_min, x_max = x_values.min(), x_values.max()
    y_min, y_max = y_values.min(), y_values.max()
    z_min, z_max = z_values.min(), z_values.max()

    # Generate output vectors
    v_min = Vector((x_min, y_min, z_min))
    v_max = Vector((x_max, y_max, z_max))

    return (v_min, v_max)


def get_face_sets_origin(face_sets):
    points = []
    for face_set in face_sets:
        for face in face_set:
            for v in face:
                points.append(v)

    return avg_vectors(points)


def avg_vectors(vectors: List[Vector]):
    nvectors = len(vectors)
    total = None
    for v in vectors:
        if total is None:
            total = v.copy()
            continue
        total += v

    return total / nvectors
