import bpy
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
import bmesh
from mathutils.bvhtree import BVHTree as BVH
import sys




def cast_bvh_ray_from_point(origin, direction, cache, candidates=None, debug=False):
    objects = [obj for obj in candidates if obj.type == "MESH"]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    if not cache:
        cache = {'bmesh': {},
                 'bvh': {}}

    for obj in objects:
        if obj.name in cache['bmesh']:
            bm = cache['bmesh'][obj.name]

            if obj.name not in cache['bmesh']:
                cache['bmesh'][obj.name] = bm

        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            cache['bmesh'][obj.name] = bm

        if obj.name in cache['bvh']:
            bvh = cache['bvh'][obj.name]

            if obj.name not in cache['bvh']:
                cache['bvh'][obj.name] = bvh
        else:
            bvh = BVH.FromBMesh(bm)
            cache['bvh'][obj.name] = bvh

        location, normal, index, distance = bvh.ray_cast(origin, direction)

        if distance:
            distance = (location - origin).length

        if debug:
            print("candidate:", obj.name, location, normal, index, distance)

        if distance and distance < hitdistance:
            hitobj, hitlocation, hitnormal, hitindex, hitdistance = obj, location, normal, index, distance


    if debug:
        print("best hit:", hitobj.name if hitobj else None, hitlocation, hitnormal, hitindex, hitdistance if hitobj else None)
        print()

    if hitobj:
        return hitobj, hitlocation, hitnormal, hitindex, hitdistance, cache

    return None, None, None, None, None, cache



def cast_scene_ray_from_mouse(mousepos, depsgraph, exclude=[], exclude_wire=False, unhide=[], debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    view_origin = region_2d_to_origin_3d(region, region_data, mousepos)
    view_dir = region_2d_to_vector_3d(region, region_data, mousepos)

    scene = bpy.context.scene

    for ob in unhide:
        ob.hide_set(False)

    hit, location, normal, index, obj, mx = scene.ray_cast(depsgraph=depsgraph, origin=view_origin, direction=view_dir)


    hidden = []

    if hit:
        if obj in exclude or (exclude_wire and obj.display_type == 'WIRE'):
            ignore = True

            while ignore:
                if debug:
                    print(" Ignoring object", obj.name)

                obj.hide_set(True)
                hidden.append(obj)

                hit, location, normal, index, obj, mx = scene.ray_cast(depsgraph=depsgraph, origin=view_origin, direction=view_dir)

                if hit:
                    ignore = obj in exclude or (exclude_wire and obj.display_type == 'WIRE')
                else:
                    break

    for ob in unhide:
        ob.hide_set(True)

    for ob in hidden:
        ob.hide_set(False)

    if hit:
        if debug:
            print(obj.name, index, location, normal)

        return hit, obj, index, location, normal, mx

    else:
        if debug:
            print(None)

        return None, None, None, None, None, None
