from math import cos, pi, sin
from pprint import pprint
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as view3d_tools
import blf
import bpy
import gpu
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar
from bpy_extras.view3d_utils import location_3d_to_region_2d ,region_2d_to_location_3d
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Quaternion, Vector

modal_hud_scale = 1
def get_prefs():
    return bpy.context.preferences.addons[__package__].preferences

red = (1, 0.25, 0.25)
green = (0.25, 1, 0.25)
blue = (0.2, 0.6, 1)
white = (1, 1, 1)
yellow = (1, 0.9, 0.2)
axis_items = [("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")]
axis_index_mapping = {"X": 0, "Y": 1, "Z": 2}
def get_addon(addon, debug=False):
    import addon_utils

    for mod in addon_utils.modules():
        name = mod.bl_info["name"]
        version = mod.bl_info.get("version", None)
        foldername = mod.__name__
        path = mod.__file__
        enabled = addon_utils.check(foldername)[1]

        if name == addon:
            if debug:
                print(name)
                print("  enabled:", enabled)
                print("  folder name:", foldername)
                print("  version:", version)
                print("  path:", path)
                print()

            return enabled, foldername, version, path
    return False, None, None, None
def get_active_tool(context):
    return view3d_tools.tool_active_from_context(context)
def move_mod(mod, index=0):
    obj = mod.id_data
    current_index = list(obj.modifiers).index(mod)

    if current_index != index:
        obj.modifiers.move(current_index, index)
def get_loc_2d(context, loc):
    loc_2d = location_3d_to_region_2d(context.region, context.region_data, loc)
    return loc_2d if loc_2d else Vector((-1000, -1000))


def step_list(current, list, step, loop=True):
    item_idx = list.index(current)

    step_idx = item_idx + step

    if step_idx >= len(list):
        if loop:
            step_idx = 0
        else:
            step_idx = len(list) - 1

    elif step_idx < 0:
        if loop:
            step_idx = len(list) - 1
        else:
            step_idx = 0

    return list[step_idx]


def printd(d, name=""):
    print(f"\n{name}")
    pprint(d, sort_dicts=False)


def draw_cross_3d(co, mx=Matrix(), color=(1, 1, 1), width=1, length=1, alpha=1, xray=True, modal=True):
    def draw():
        x = Vector((1, 0, 0))
        y = Vector((0, 1, 0))
        z = Vector((0, 0, 1))

        coords = [
            (co - x) * length,
            (co + x) * length,
            (co - y) * length,
            (co + y) * length,
            (co - z) * length,
            (co + z) * length,
        ]

        indices = [(0, 1), (2, 3), (4, 5)]

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA")

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.uniform_float("color", (*color, alpha))
        shader.uniform_float("lineWidth", width)
        shader.uniform_float("viewportSize", gpu.state.scissor_get()[2:])
        shader.bind()

        batch = batch_for_shader(shader, "LINES", {"pos": [mx @ co for co in coords]}, indices=indices)
        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def draw_bbox(bbox, mx=Matrix(), color=(1, 1, 1), corners=0, width=1, alpha=1, xray=True, modal=True):
    def draw():
        if corners:
            length = corners

            coords = [
                bbox[0],
                bbox[0] + (bbox[1] - bbox[0]) * length,
                bbox[0] + (bbox[3] - bbox[0]) * length,
                bbox[0] + (bbox[4] - bbox[0]) * length,
                bbox[1],
                bbox[1] + (bbox[0] - bbox[1]) * length,
                bbox[1] + (bbox[2] - bbox[1]) * length,
                bbox[1] + (bbox[5] - bbox[1]) * length,
                bbox[2],
                bbox[2] + (bbox[1] - bbox[2]) * length,
                bbox[2] + (bbox[3] - bbox[2]) * length,
                bbox[2] + (bbox[6] - bbox[2]) * length,
                bbox[3],
                bbox[3] + (bbox[0] - bbox[3]) * length,
                bbox[3] + (bbox[2] - bbox[3]) * length,
                bbox[3] + (bbox[7] - bbox[3]) * length,
                bbox[4],
                bbox[4] + (bbox[0] - bbox[4]) * length,
                bbox[4] + (bbox[5] - bbox[4]) * length,
                bbox[4] + (bbox[7] - bbox[4]) * length,
                bbox[5],
                bbox[5] + (bbox[1] - bbox[5]) * length,
                bbox[5] + (bbox[4] - bbox[5]) * length,
                bbox[5] + (bbox[6] - bbox[5]) * length,
                bbox[6],
                bbox[6] + (bbox[2] - bbox[6]) * length,
                bbox[6] + (bbox[5] - bbox[6]) * length,
                bbox[6] + (bbox[7] - bbox[6]) * length,
                bbox[7],
                bbox[7] + (bbox[3] - bbox[7]) * length,
                bbox[7] + (bbox[4] - bbox[7]) * length,
                bbox[7] + (bbox[6] - bbox[7]) * length,
            ]

            indices = [
                (0, 1),
                (0, 2),
                (0, 3),
                (4, 5),
                (4, 6),
                (4, 7),
                (8, 9),
                (8, 10),
                (8, 11),
                (12, 13),
                (12, 14),
                (12, 15),
                (16, 17),
                (16, 18),
                (16, 19),
                (20, 21),
                (20, 22),
                (20, 23),
                (24, 25),
                (24, 26),
                (24, 27),
                (28, 29),
                (28, 30),
                (28, 31),
            ]

        else:
            coords = bbox
            indices = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA")

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.uniform_float("color", (*color, alpha))
        shader.uniform_float("lineWidth", width)
        shader.uniform_float("viewportSize", gpu.state.scissor_get()[2:])
        shader.bind()

        batch = batch_for_shader(shader, "LINES", {"pos": [mx @ co for co in coords]}, indices=indices)
        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def draw_label(context, title="", coords=None, offset=0, center=True, size=12, color=(1, 1, 1), alpha=1):
    if not coords:
        region = context.region
        width = region.width / 2
        height = region.height / 2
    else:
        width, height = coords

    scale = context.preferences.system.ui_scale * modal_hud_scale

    font = 1
    fontsize = int(size * scale)

    blf.size(font, fontsize)
    blf.color(font, *color, alpha)

    if center:
        dims = blf.dimensions(font, title)
        blf.position(font, width - (dims[0] / 2), height - (offset * scale), 1)

    else:
        blf.position(font, width, height - (offset * scale), 1)

    blf.draw(font, title)

    return blf.dimensions(font, title)


def get_builtin_shader_name(name, prefix="3D"):
    if bpy.app.version >= (4, 0, 0):
        return name
    else:
        return f"{prefix}_{name}"


def draw_point(co, mx=Matrix(), color=(1, 1, 1), size=6, alpha=1, xray=True, modal=True, screen=False):
    def draw():
        shader = gpu.shader.from_builtin(get_builtin_shader_name("UNIFORM_COLOR"))
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA" if alpha < 1 else "NONE")
        gpu.state.point_size_set(size)

        batch = batch_for_shader(shader, "POINTS", {"pos": [mx @ co]})
        batch.draw(shader)

    if modal:
        draw()

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_PIXEL")

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def draw_circle(
    loc=Vector(),
    rot=Quaternion(),
    radius=100,
    segments="AUTO",
    width=1,
    color=(1, 1, 1),
    alpha=1,
    xray=True,
    modal=True,
    screen=False,
):
    def draw():
        nonlocal segments

        if segments == "AUTO":
            segments = max(int(radius), 16)

        else:
            segments = max(segments, 16)

        indices = [(i, i + 1) if i < segments - 1 else (i, 0) for i in range(segments)]

        coords = []

        for i in range(segments):

            theta = 2 * pi * i / segments

            x = radius * cos(theta)
            y = radius * sin(theta)

            coords.append(Vector((x, y, 0)))

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA")

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.uniform_float("color", (*color, alpha))
        shader.uniform_float("lineWidth", width)
        shader.uniform_float("viewportSize", gpu.state.scissor_get()[2:])
        shader.bind()

        if len(loc) == 2:
            mx = Matrix()
            mx.col[3] = loc.resized(4)
            batch = batch_for_shader(shader, "LINES", {"pos": [mx @ co for co in coords]}, indices=indices)

        else:
            mx = Matrix.LocRotScale(loc, rot, Vector.Fill(3, 1))
            batch = batch_for_shader(shader, "LINES", {"pos": [mx @ co for co in coords]}, indices=indices)

        batch.draw(shader)

    if modal:
        draw()

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_PIXEL")

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def get_world_space_normal(normal, mx):
    return (mx.inverted_safe().transposed().to_3x3() @ normal).normalized()


def draw_vector(
    vector,
    origin=Vector((0, 0, 0)),
    mx=Matrix(),
    color=(1, 1, 1),
    width=1,
    alpha=1,
    fade=False,
    normal=False,
    xray=True,
    modal=True,
    screen=False,
):
    def draw():
        if normal:
            coords = [mx @ origin, mx @ origin + get_world_space_normal(vector, mx)]
        else:
            coords = [mx @ origin, mx @ origin + mx.to_3x3() @ vector]

        colors = ((*color, alpha), (*color, alpha / 10 if fade else alpha))

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA")

        shader = gpu.shader.from_builtin("POLYLINE_SMOOTH_COLOR")
        shader.uniform_float("lineWidth", width)
        shader.uniform_float("viewportSize", gpu.state.scissor_get()[2:])
        shader.bind()

        batch = batch_for_shader(shader, "LINES", {"pos": coords, "color": colors})
        batch.draw(shader)

    if modal:
        draw()

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_PIXEL")

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


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


def init_status(self, context, title="", func=None):
    self.bar_orig = statusbar.draw

    if func:
        statusbar.draw = func
    else:
        statusbar.draw = draw_basic_status(self, context, title)


def get_flick_direction(context, mouse_loc_3d, flick_vector, axes):
    origin_2d = location_3d_to_region_2d(
        context.region,
        context.region_data,
        mouse_loc_3d,
        default=Vector((context.region.width / 2, context.region.height / 2)),
    )
    axes_2d = {}

    for direction, axis in axes.items():

        axis_2d = location_3d_to_region_2d(context.region, context.region_data, mouse_loc_3d + axis, default=origin_2d)
        if (axis_2d - origin_2d).length:
            axes_2d[direction] = (axis_2d - origin_2d).normalized()

    return min([(d, abs(flick_vector.xy.angle_signed(a))) for d, a in axes_2d.items()], key=lambda x: x[1])[0]


def get_zoom_factor(context, depth_location, scale=10, ignore_obj_scale=False):
    center = Vector((context.region.width / 2, context.region.height / 2))
    offset = center + Vector((scale, 0))

    try:
        center_3d = region_2d_to_location_3d(context.region, context.region_data, center, depth_location)
        offset_3d = region_2d_to_location_3d(context.region, context.region_data, offset, depth_location)
    except:
        print("exception!")
        return 1

    if not ignore_obj_scale and context.active_object:
        mx = context.active_object.matrix_world.to_3x3()
        zoom_vector = mx.inverted_safe() @ Vector(((center_3d - offset_3d).length, 0, 0))
        return zoom_vector.length
    return (center_3d - offset_3d).length


def remove_mod(mod):
    obj = mod.id_data

    if isinstance(mod, bpy.types.Modifier):
        obj.modifiers.remove(mod)

    elif isinstance(mod, bpy.types.GpencilModifier):
        obj.grease_pencil_modifiers.remove(mod)

    else:
        print(f"WARNING: Could not remove modiifer {mod.name} of type {mod.type}")


def get_mod_obj(mod):
    if mod.type in ["BOOLEAN", "HOOK", "LATTICE", "DATA_TRANSFER", "GP_MIRROR"]:
        return mod.object
    elif mod.type == "MIRROR":
        return mod.mirror_object
    elif mod.type == "ARRAY":
        return mod.offset_object


def flatten_matrix(mx):
    dimension = len(mx)
    return [mx[j][i] for i in range(dimension) for j in range(dimension)]


def compare_matrix(mx1, mx2, precision=4):
    round1 = [round(i, precision) for i in flatten_matrix(mx1)]
    round2 = [round(i, precision) for i in flatten_matrix(mx2)]
    return round1 == round2


def get_eval_bbox(obj):
    return [Vector(co) for co in obj.bound_box]
