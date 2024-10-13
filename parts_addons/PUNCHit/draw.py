import blf
import bpy

if not bpy.app.background:
    import gpu
    from gpu_extras.batch import batch_for_shader

from mathutils import Matrix, Vector

from ...utils import get_prefs


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


def draw_points(
    coords, indices=None, mx=Matrix(), color=(1, 1, 1), size=6, alpha=1, xray=True, modal=True, screen=False
):
    def draw():
        shader = gpu.shader.from_builtin(get_builtin_shader_name("UNIFORM_COLOR"))
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA" if alpha < 1 else "NONE")
        gpu.state.point_size_set(size)

        if indices:
            if mx != Matrix():
                batch = batch_for_shader(shader, "POINTS", {"pos": [mx @ co for co in coords]}, indices=indices)
            else:
                batch = batch_for_shader(shader, "POINTS", {"pos": coords}, indices=indices)

        else:
            if mx != Matrix():
                batch = batch_for_shader(shader, "POINTS", {"pos": [mx @ co for co in coords]})
            else:
                batch = batch_for_shader(shader, "POINTS", {"pos": coords})

        batch.draw(shader)

    if modal:
        draw()

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_PIXEL")

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def draw_line(
    coords, indices=None, mx=Matrix(), color=(1, 1, 1), alpha=1, width=1, xray=True, modal=True, screen=False
):

    def draw():
        nonlocal indices

        if indices is None:
            indices = [(i, i + 1) for i in range(0, len(coords)) if i < len(coords) - 1]

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

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_PIXEL")

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def draw_lines(
    coords, indices=None, mx=Matrix(), color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True, screen=False
):

    def draw():
        nonlocal indices

        if not indices:
            indices = [(i, i + 1) for i in range(0, len(coords), 2)]

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

    elif screen:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_PIXEL")

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


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


def draw_tris(coords, indices=None, mx=Matrix(), color=(1, 1, 1), alpha=1, xray=True, modal=True):

    def draw():

        shader = gpu.shader.from_builtin(get_builtin_shader_name("UNIFORM_COLOR"))
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set("NONE" if xray else "LESS_EQUAL")
        gpu.state.blend_set("ALPHA" if alpha < 1 else "NONE")

        if mx != Matrix():
            batch = batch_for_shader(shader, "TRIS", {"pos": [mx @ co for co in coords]}, indices=indices)

        else:
            batch = batch_for_shader(shader, "TRIS", {"pos": coords}, indices=indices)

        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), "WINDOW", "POST_VIEW")


def draw_init(self):
    self.font_id = 1
    self.offset = 0


def draw_label(context, title="", coords=None, offset=0, center=True, size=12, color=(1, 1, 1), alpha=1):

    if not coords:
        region = context.region
        width = region.width / 2
        height = region.height / 2
    else:
        width, height = coords

    scale = context.preferences.system.ui_scale * get_prefs().modal_hud_scale

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


def draw_split_row(
    self,
    layout,
    prop="prop",
    text="",
    label="Label",
    factor=0.2,
    align=True,
    toggle=True,
    expand=True,
    info=None,
    warning=None,
):

    row = layout.row(align=align)
    split = row.split(factor=factor, align=align)

    text = text if text else str(getattr(self, prop)) if str(getattr(self, prop)) in ["True", "False"] else ""
    split.prop(self, prop, text=text, toggle=toggle, expand=expand)

    if label:
        split.label(text=label)

    if info:
        split.label(text=info, icon="INFO")

    if warning:
        split.label(text=warning, icon="ERROR")
    return row
