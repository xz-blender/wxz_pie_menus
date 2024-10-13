from bpy.types import Context


def _get_region_perspective_type(context: Context):
    """return one of ["PERSP", "ORTHO", "CAMERA"]"""
    area = context.area
    rv3d = area.spaces[0].region_3d
    return rv3d.view_perspective


def view3d_is_orthographic(context: Context):
    region_perspective_type = _get_region_perspective_type(context)

    if region_perspective_type == "ORTHO":
        return True
    if region_perspective_type == "CAMERA":
        return context.scene.camera.data.type == "ORTHO"
    return False


def view3d_is_camera(context: Context):
    region_perspective_type = _get_region_perspective_type(context)
    return region_perspective_type == "CAMERA"
