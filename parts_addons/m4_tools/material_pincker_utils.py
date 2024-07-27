import os
import sys
from pprint import pprint

import bmesh
import bpy
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
from mathutils.bvhtree import BVHTree as BVH


def get_asset_details_from_space(context, space, debug=False):

    lib_reference = get_asset_library_reference(space.params)
    catalog_id = space.params.catalog_id
    libname = "" if lib_reference == "ALL" else lib_reference
    libpath = space.params.directory.decode("utf-8")
    filename = space.params.filename
    import_method = get_asset_import_method(space.params)

    if debug:
        print()
        print("get_asset_details_from_space()")
        print(" asset_library_reference:", lib_reference)
        print(" catalog_id:", catalog_id)
        print(" libname:", libname)
        print(" libpath:", libpath)
        print(" filename:", filename)
        print(" import_method:", import_method)
        print()

    if libname == "ESSENTIALS":
        return None, None, "", None

    elif libname == "LOCAL":
        if "Object/" in filename:
            return libname, libpath, filename, import_method

    elif not ".blend" in filename:
        if debug:
            print(" WARNING: LOCAL library, but ALL or library is chosen (instead of current file)!")

        if "Object/" in filename:
            return "LOCAL", "", filename, import_method

    elif not libname and not libpath:
        if debug:
            print(" WARNING: EXTERNAL library, but library ref is ALL and directory is not set!")

        catalogs = get_catalogs_from_asset_libraries(context, debug=False)

        for uuid, catdata in catalogs.items():
            if catalog_id == uuid:
                catalog = catdata["catalog"]
                libname = catdata["libname"]
                libpath = catdata["libpath"]

                if debug:
                    print(
                        f" INFO: found catalog {catalog}'s libname and libpath via asset catalogs:",
                        libname,
                        "at",
                        libpath,
                    )

                break

    if debug:
        print()

    if libpath:
        return libname, libpath, filename, import_method

    else:
        return None, None, "", None


def get_asset_library_reference(params):
    if bpy.app.version >= (4, 0, 0):
        return params.asset_library_reference
    else:
        return params.asset_library_ref


def get_asset_import_method(params):
    if bpy.app.version >= (4, 0, 0):
        return params.import_method
    else:
        return params.import_type


def get_catalogs_from_asset_libraries(context, debug=False):
    asset_libraries = context.preferences.filepaths.asset_libraries
    all_catalogs = []

    for lib in asset_libraries:
        libname = lib.name
        libpath = lib.path

        cat_path = os.path.join(libpath, "blender_assets.cats.txt")

        if os.path.exists(cat_path):
            if debug:
                print(libname, cat_path)

            with open(cat_path) as f:
                lines = f.readlines()

            for line in lines:
                if (
                    line != "\n"
                    and not any([line.startswith(skip) for skip in ["#", "VERSION"]])
                    and len(line.split(":")) == 3
                ):
                    all_catalogs.append(line[:-1].split(":") + [libname, libpath])

    catalogs = {}

    for uuid, catalog, simple_name, libname, libpath in all_catalogs:
        if uuid not in catalogs:
            catalogs[uuid] = {"catalog": catalog, "simple_name": simple_name, "libname": libname, "libpath": libpath}

    return catalogs


def init_cursor(self, event, offsetx=0, offsety=20):
    self.last_mouse_x = event.mouse_x
    self.last_mouse_y = event.mouse_y

    self.region_offset_x = event.mouse_x - event.mouse_region_x
    self.region_offset_y = event.mouse_y - event.mouse_region_y

    self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
    self.HUD_y = event.mouse_y - self.region_offset_y + offsety


def wrap_cursor(self, context, event, x=False, y=False):
    if x:

        if event.mouse_region_x <= 0:
            context.window.cursor_warp(context.region.width + self.region_offset_x - 10, event.mouse_y)

        if (
            event.mouse_region_x >= context.region.width - 1
        ):  # the -1 is required for full screen, where the max region width is never passed
            context.window.cursor_warp(self.region_offset_x + 10, event.mouse_y)

    if y:
        if event.mouse_region_y <= 0:
            context.window.cursor_warp(event.mouse_x, context.region.height + self.region_offset_y - 10)

        if event.mouse_region_y >= context.region.height - 1:
            context.window.cursor_warp(event.mouse_x, self.region_offset_y + 100)


def init_status(self, context, title="", func=None):
    self.bar_orig = statusbar.draw

    if func:
        statusbar.draw = func
    else:
        statusbar.draw = draw_basic_status(self, context, title)


def draw_basic_status(self, context, title):
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text=title)

        row.label(text="", icon="MOUSE_LMB")
        row.label(text="Finish")

        if context.window_manager.keyconfigs.active.name.startswith("blender"):
            row.label(text="", icon="MOUSE_MMB")
            row.label(text="Viewport")

        row.label(text="", icon="MOUSE_RMB")
        row.label(text="Cancel")

    return draw


def finish_status(self):
    statusbar.draw = self.bar_orig


def printd(d, name=""):
    print(f"\n{name}")
    pprint(d, sort_dicts=False)


def update_HUD_location(self, event, offsetx=20, offsety=20):
    self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
    self.HUD_y = event.mouse_y - self.region_offset_y + offsety


def draw_init(self, event):
    self.font_id = 1
    self.offset = 0


def cast_obj_ray_from_mouse(mousepos, depsgraph=None, candidates=None, objtypes=["MESH"], debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    if not candidates:
        candidates = bpy.context.visible_objects

    objects = [obj for obj in candidates if obj.type in objtypes]

    hitobj = None
    hitobj_eval = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    for obj in objects:
        mx = obj.matrix_world
        mxi = mx.inverted_safe()

        ray_origin = mxi @ origin_3d
        ray_direction = mxi.to_3x3() @ vector_3d

        success, location, normal, index = obj.ray_cast(origin=ray_origin, direction=ray_direction, depsgraph=depsgraph)
        distance = (mx @ location - origin_3d).length

        if debug:
            print("candidate:", success, obj.name, location, normal, index, distance)

        if success and distance < hitdistance:
            hitobj, hitobj_eval, hitlocation, hitnormal, hitindex, hitdistance = (
                obj,
                obj.evaluated_get(depsgraph) if depsgraph else None,
                mx @ location,
                mx.to_3x3() @ normal,
                index,
                distance,
            )

    if debug:
        print(
            "best hit:",
            hitobj.name if hitobj else None,
            hitlocation,
            hitnormal,
            hitindex,
            hitdistance if hitobj else None,
        )
        print()

    if hitobj:
        return hitobj, hitobj_eval, hitlocation, hitnormal, hitindex, hitdistance

    return None, None, None, None, None, None


def cast_bvh_ray_from_mouse(mousepos, candidates=None, bmeshes={}, bvhs={}, debug=False):
    region = bpy.context.region
    region_data = bpy.context.region_data

    origin_3d = region_2d_to_origin_3d(region, region_data, mousepos)
    vector_3d = region_2d_to_vector_3d(region, region_data, mousepos)

    objects = [(obj, None) for obj in candidates if obj.type == "MESH"]

    hitobj = None
    hitlocation = None
    hitnormal = None
    hitindex = None
    hitdistance = sys.maxsize

    cache = {"bmesh": {}, "bvh": {}}

    for obj, src in objects:
        mx = obj.matrix_world
        mxi = mx.inverted_safe()

        ray_origin = mxi @ origin_3d
        ray_direction = mxi.to_3x3() @ vector_3d

        if obj.name in bmeshes:
            bm = bmeshes[obj.name]
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            cache["bmesh"][obj.name] = bm

        if obj.name in bvhs:
            bvh = bvhs[obj.name]
        else:
            bvh = BVH.FromBMesh(bm)
            cache["bvh"][obj.name] = bvh

        location, normal, index, distance = bvh.ray_cast(ray_origin, ray_direction)

        if distance:
            distance = (mx @ location - origin_3d).length

        if debug:
            print("candidate:", obj.name, location, normal, index, distance)

        if distance and distance < hitdistance:
            hitobj, hitlocation, hitnormal, hitindex, hitdistance = (
                obj,
                mx @ location,
                mx.to_3x3() @ normal,
                index,
                distance,
            )

    if debug:
        print(
            "best hit:",
            hitobj.name if hitobj else None,
            hitlocation,
            hitnormal,
            hitindex,
            hitdistance if hitobj else None,
        )
        print()

    if hitobj:
        return hitobj, hitlocation, hitnormal, hitindex, hitdistance, cache

    return None, None, None, None, None, cache
