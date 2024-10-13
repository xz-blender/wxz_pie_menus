import sys

import blf
import bpy

if not bpy.app.background:
    import gpu
    from gpu_extras.batch import batch_for_shader

from mathutils import Matrix, Vector

from ...utils import get_prefs


def get_loop_triangles(bm, faces=None):
    if faces:
        return [lt for lt in bm.calc_loop_triangles() if lt[0].face in faces]
    return bm.calc_loop_triangles()


def get_tri_coords_from_face(loop_triangles, f, mx=None):
    if mx:
        return [mx @ l.vert.co for lt in loop_triangles if lt[0].face == f for l in lt]
    else:
        return [l.vert.co for lt in loop_triangles if lt[0].face == f for l in lt]


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


def build_mesh_graph(verts, edges, topo=True):
    mg = {}
    for v in verts:
        mg[v] = []

    for e in edges:
        distance = 1 if topo else e.calc_length()

        mg[e.verts[0]].append((e.verts[1], distance))
        mg[e.verts[1]].append((e.verts[0], distance))

    return mg


def get_shortest_path(bm, vstart, vend, topo=False, ignore_selected=False, select=False):

    def dijkstra(mg, vstart, vend, topo=True):
        d = dict.fromkeys(mg.keys(), sys.maxsize)

        predecessor = dict.fromkeys(mg.keys())

        d[vstart] = 0

        unknownverts = [(0, vstart)]

        while unknownverts:

            dist, vcurrent = unknownverts[0]

            others = mg[vcurrent]

            if ignore_selected and vcurrent == vstart and vend in [v for v, _ in others]:
                others = [(v, d) for v, d in others if v != vend]

            for vother, distance in others:

                if ignore_selected and vother not in [vstart, vend] and vother.select:
                    continue

                if d[vother] > d[vcurrent] + distance:
                    d[vother] = d[vcurrent] + distance

                    unknownverts.append((d[vother], vother))
                    predecessor[vother] = vcurrent

            unknownverts.pop(0)

            if topo and vcurrent == vend:
                break

        path = []
        endvert = vend

        while endvert is not None:
            path.append(endvert)
            endvert = predecessor[endvert]

        return reversed(path)

    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    verts = [v for v in bm.verts]
    edges = [e for e in bm.edges]

    mg = build_mesh_graph(verts, edges, topo)

    path = dijkstra(mg, vstart, vend, topo)

    path = f7(path)

    if select:
        for v in path:
            v.select = True

    return path


def rotate_list(list, amount):
    for i in range(abs(amount)):
        if amount > 0:
            list.append(list.pop(0))
        else:
            list.insert(0, list.pop(-1))

    return list


def shorten_float_string(float_str, count=4):

    split = float_str.split(".")

    if len(split) == 2:
        return f"{split[0]}.{split[1][:count].rstrip('0').rstrip('.')}"
    else:
        return float_str
