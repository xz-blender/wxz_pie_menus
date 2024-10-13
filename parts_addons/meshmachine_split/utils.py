from math import cos, degrees, pi, radians, sin, sqrt  # type: ignore
from random import choice

import bmesh
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import Context, Operator, Panel
from mathutils import Matrix, Quaternion, Vector, geometry

if not bpy.app.background:
    import gpu
    from gpu_extras.batch import batch_for_shader

from ... import __package__ as base_package
from .items import *
from .math import *
from .vars import *


def get_prefs():
    return bpy.context.preferences.addons[base_package].preferences


def average_locations(locationslist):
    avg = Vector()

    for n in locationslist:
        avg += n

    return avg / len(locationslist)


def resample_coords(coords, cyclic, segments=None, shift=0, mx=None, debug=False):
    if not segments:
        segments = len(coords) - 1

    if len(coords) < 2:
        return coords

    if not cyclic and shift != 0:  # not PEP but it shows that we want shift = 0
        print("Not shifting because this is not a cyclic vert chain")
        shift = 0

    arch_len = 0
    cumulative_lengths = [0]  # TODO: make this the right size and dont append

    for i in range(0, len(coords) - 1):
        v0 = coords[i]
        v1 = coords[i + 1]
        V = v1 - v0
        arch_len += V.length
        cumulative_lengths.append(arch_len)

    if cyclic:
        v0 = coords[-1]
        v1 = coords[0]
        V = v1 - v0
        arch_len += V.length
        cumulative_lengths.append(arch_len)
        segments += 1

    if cyclic:
        new_coords = [[None]] * segments
    else:
        new_coords = [[None]] * (segments + 1)
        new_coords[0] = coords[0]
        new_coords[-1] = coords[-1]

    n = 0

    for i in range(0, segments - 1 + cyclic * 1):
        desired_length_raw = (i + 1 + cyclic * -1) / segments * arch_len + shift * arch_len / segments
        if desired_length_raw > arch_len:
            desired_length = desired_length_raw - arch_len
        elif desired_length_raw < 0:
            desired_length = arch_len + desired_length_raw  # this is the end, + a negative number
        else:
            desired_length = desired_length_raw

        for j in range(n, len(coords) + 1):

            if cumulative_lengths[j] > desired_length:
                break

        extra = desired_length - cumulative_lengths[j - 1]

        if j == len(coords):
            new_coords[i + 1 + cyclic * -1] = coords[j - 1] + extra * (coords[0] - coords[j - 1]).normalized()
        else:
            new_coords[i + 1 + cyclic * -1] = coords[j - 1] + extra * (coords[j] - coords[j - 1]).normalized()

    if debug:
        print(len(coords), len(new_coords))
        print(cumulative_lengths)
        print(arch_len)

        if mx:
            draw_points(new_coords, mx=mx, color=green if cyclic else yellow, xray=True, modal=False)

    return new_coords


def get_builtin_shader_name(name, prefix="3D"):
    if bpy.app.version >= (4, 0, 0):
        return name
    else:
        return f"{prefix}_{name}"


def draw_vectors(
    vectors,
    origins,
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
        coords = []
        colors = []

        for v, o in zip(vectors, origins):
            coords.append(mx @ o)

            if normal:
                coords.append(mx @ o + get_world_space_normal(v, mx))  # type: ignore
            else:
                coords.append(mx @ o + mx.to_3x3() @ v)

            colors.extend([(*color, alpha), (*color, alpha / 10 if fade else alpha)])

        indices = [(i, i + 1) for i in range(0, len(coords), 2)]

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


def get_loc_matrix(location):
    return Matrix.Translation(location)


def create_rotation_matrix_from_vector(vec):
    vec.normalize()

    if vec == Vector((0, 0, 1)):
        tangent = Vector((1, 0, 0))
        binormal = Vector((0, 1, 0))

    elif vec == Vector((0, 0, -1)):
        tangent = Vector((-1, 0, 0))
        binormal = Vector((0, 1, 0))

    else:
        tangent = Vector((0, 0, 1)).cross(vec).normalized()
        binormal = tangent.cross(-vec).normalized()

    rotmx = Matrix()
    rotmx[0].xyz = tangent
    rotmx[1].xyz = binormal
    rotmx[2].xyz = vec

    return rotmx.transposed()


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
            coords = [mx @ origin, mx @ origin + get_world_space_normal(vector, mx)]  # type: ignore
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


def create_pipe_ring_coords(coords, cyclic, circle_coords, circle_normals=None, mx=None, debug=False):
    ring_coords = []

    for idx, co in enumerate(coords):
        ring = []

        prevco = coords[-1] if idx == 0 else coords[idx - 1]
        nextco = coords[0] if idx == len(coords) - 1 else coords[idx + 1]

        if cyclic or idx not in [0, len(coords) - 1]:
            vec_next = (nextco - co).normalized()
            vec_prev = (co - prevco).normalized()

            direction = vec_prev + vec_next

        else:
            if idx == 0:
                direction = (nextco - co).normalized()

            elif idx == len(coords) - 1:
                direction = (co - prevco).normalized()

        if debug and mx:
            draw_vector(direction * 0.05, origin=co, mx=mx, color=(1, 1, 1), modal=False)

        rotmx = create_rotation_matrix_from_vector(direction)

        locmx = get_loc_matrix(co)

        for cidx, cco in enumerate(circle_coords):
            if circle_normals:
                normal = circle_normals[cidx]
                ring.append((locmx @ rotmx @ cco, rotmx @ normal))

            else:
                ring.append(locmx @ rotmx @ cco)

        if debug and mx:
            if circle_normals:
                dcoords = [co for co, _ in ring]
                draw_points(dcoords[1:], mx=mx, color=(1, 1, 1), size=4, alpha=0.5, modal=False)
                draw_point(dcoords[0], mx=mx, color=(1, 0, 0), size=4, alpha=1, modal=False)

                normals = [nrm for _, nrm in ring]
                draw_vectors(normals, dcoords, mx=mx, color=(1, 0, 0), alpha=0.5, modal=False)

            else:
                draw_points(ring[1:], mx=mx, color=(1, 1, 1), size=4, alpha=0.5, modal=False)
                draw_point(ring[0], mx=mx, color=(1, 0, 0), size=4, alpha=1, modal=False)

        ring_coords.append(ring)

    return ring_coords


def create_pipe_coords(seq, cyclic, resample, factor, smooth, iterations, optimize, angle, mx, debug=False):
    def smooth_coords(coords, cyclic, iterations, mx, debug=False):
        while iterations:
            iterations -= 1

            smoothed = []

            for idx, co in enumerate(coords):
                if idx in [0, len(coords) - 1]:
                    if cyclic:
                        if idx == 0:
                            smoothed.append(average_locations([coords[-1], coords[1]]))

                        elif idx == len(coords) - 1:
                            smoothed.append(average_locations([coords[-2], coords[0]]))
                    else:
                        smoothed.append(co)
                else:
                    co_prev = coords[idx - 1]
                    co_next = coords[idx + 1]

                    smoothed.append(average_locations([co_prev, co_next]))

            coords = smoothed

        if debug:
            draw_points(coords, mx=mx, color=red, xray=True, modal=False)

        return coords

    def optimize_straights(coords, cyclic, angle, mx, debug=False):
        optimized = []
        removed = []

        for idx, co in enumerate(coords):
            if idx in [0, len(coords) - 1]:
                if cyclic:
                    if idx == 0:
                        co_prev = coords[-1]
                        co_next = coords[1]

                    elif idx == len(coords) - 1:
                        co_prev = coords[-2]
                        co_next = coords[0]
                else:
                    optimized.append(co)
                    continue
            else:
                co_prev = coords[idx - 1]
                co_next = coords[idx + 1]

            vec1 = co_prev - co
            vec2 = co_next - co
            a = round(degrees(vec1.angle(vec2)), 3)

            if a >= angle:
                removed.append(co)

            else:
                optimized.append(co)

        if debug:
            draw_points(removed, mx=mx, color=black, modal=False)

        return optimized

    coords = [v.co.copy() for v in seq]

    if resample:
        coords = resample_coords(coords, cyclic, segments=int(len(coords) * factor), mx=mx, debug=False)

    if smooth:
        coords = smooth_coords(coords, cyclic, iterations, mx, debug=False)

    if optimize:
        coords = optimize_straights(coords, cyclic, angle, mx, debug=False)

    if debug:
        draw_points(coords, mx=mx, color=white, xray=True, modal=False)

    return coords


def rotate_list(list, amount):
    for i in range(abs(amount)):
        if amount > 0:
            list.append(list.pop(0))
        else:
            list.insert(0, list.pop(-1))

    return list


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


def create_circle_coords(radius, count, tilt, calc_normals=False, debug=False):
    coords = []

    rotmx = Matrix.Rotation(radians(tilt), 4, "Z")

    for idx in range(count):
        vert_angle = idx * (2.0 * pi / count)

        x = sin(vert_angle) * radius
        y = cos(vert_angle) * radius
        coords.append(rotmx @ Vector((x, y, 0)))

        if debug:
            draw_points(coords, alpha=0.5, modal=False)

    if calc_normals:
        normals = [(co - Vector()).normalized() * 0.05 for co in coords]

        if debug:
            draw_vectors(normals, origins=coords, color=(1, 0, 0), modal=False)

        return coords, normals

    return coords


def get_selected_vert_sequences(verts, debug=False):
    sequences = []

    noncyclicstartverts = [v for v in verts if len([e for e in v.link_edges if e.select]) == 1]

    if noncyclicstartverts:
        v = noncyclicstartverts[0]

    else:
        v = verts[0]

    seq = []

    while verts:
        seq.append(v)

        verts.remove(v)
        if v in noncyclicstartverts:
            noncyclicstartverts.remove(v)

        nextv = [e.other_vert(v) for e in v.link_edges if e.select and e.other_vert(v) not in seq]

        if nextv:
            v = nextv[0]

        else:
            cyclic = True if len([e for e in v.link_edges if e.select]) == 2 else False

            sequences.append((seq, cyclic))

            if verts:
                if noncyclicstartverts:
                    v = noncyclicstartverts[0]
                else:
                    v = verts[0]

                seq = []

    if debug:
        for seq, cyclic in sequences:
            print(cyclic, [v.index for v in seq])

    return sequences


def output_traceback(self, e):
    import traceback

    print()
    traceback.print_exc()
    self.report({"ERROR"}, str(e))


def ensure_custom_data_layers(bm, vertex_groups=True, bevel_weights=True, crease=True):

    vert_vg_layer = bm.verts.layers.deform.verify() if vertex_groups else None
    if bpy.app.version >= (4, 0, 0):

        if bevel_weights:
            edge_bw_layer = bm.edges.layers.float.get("bevel_weight_edge")

            if not edge_bw_layer:
                edge_bw_layer = bm.edges.layers.float.new("bevel_weight_edge")
        else:
            edge_bw_layer = None

        if crease:
            edge_crease_layer = bm.edges.layers.float.get("crease_edge")

            if not edge_crease_layer:
                edge_crease_layer = bm.edges.layers.float.new("crease_edge")
        else:
            edge_crease_layer = None
    else:
        edge_bw_layer = bm.edges.layers.bevel_weight.verify() if bevel_weights else None
        edge_crease_layer = bm.edges.layers.crease.verify() if crease else None

    return [layer for layer in [vert_vg_layer, edge_bw_layer, edge_crease_layer] if layer is not None]


def loop_index_update(bm, debug=False):
    lidx = 0
    for f in bm.faces:
        if debug:
            print(f)
        for l in f.loops:
            l.index = lidx
            lidx += 1
            if debug:
                print(" •", l)


def build_mesh_graph(bm, debug=False):
    mesh_graph = {}
    for v in bm.verts:
        mesh_graph[v.index] = []

    for edge in bm.edges:
        mesh_graph[edge.verts[0].index].append((edge.verts[1].index, edge.verts[1].select, edge.select))
        mesh_graph[edge.verts[1].index].append((edge.verts[0].index, edge.verts[0].select, edge.select))

    if debug:
        for idx in mesh_graph:
            print(idx, mesh_graph[idx])

    return mesh_graph


def build_edge_graph(verts, edges, debug=False):
    mg = {}
    for v in verts:
        mg[v.index] = {"fixed": v.tag, "connected": [], "children": []}

    for e in edges:
        v1 = e.verts[0]
        v2 = e.verts[1]

        mg[v1.index]["connected"].append((v2.index, v2.tag, e.calc_length()))
        mg[v2.index]["connected"].append((v1.index, v1.tag, e.calc_length()))

    if debug:
        for idx in mg:
            print(idx, mg[idx])

    return mg


def init_sweeps(
    bm,
    active,
    rails,
    verts=True,
    edges=True,
    loop_candidates=True,
    freestyle=True,
    loops=True,
    handles=True,
    avg_face_normals=True,
    rail_lengths=True,
    debug=False,
):
    sweeps = []
    for idx, vertpair in enumerate(zip(rails[0], rails[1])):
        sweep = {}
        if verts:
            sweep["verts"] = vertpair
        if edges:
            sweep["edges"] = [bm.edges.get(vertpair)]
        if loop_candidates:

            candidates = []
            for v in sweep["verts"]:
                side = []
                for e in v.link_edges:
                    if not e.select:
                        if e.calc_length() != 0:
                            side.append(e)
                        elif debug:
                            print("Zero length edge detected, ignoring edge %d. Results may be unexpected!" % (e.index))

                if freestyle:
                    fsloopcount = sum([active.data.edges[e.index].use_freestyle_mark for e in side])

                    if fsloopcount > 0:
                        if fsloopcount == 1 and len(side) != 1:
                            side = [e for e in side if active.data.edges[e.index].use_freestyle_mark]
                            if debug:
                                print("Using freestyle edge %d as the only loop candidate." % (side[0].index))
                        else:
                            exclude = [e for e in side if active.data.edges[e.index].use_freestyle_mark]
                            if debug:
                                for e in exclude:
                                    print("Excluding freestyle edge %d from loop edge candidates" % (e.index))
                            side = [e for e in side if e not in exclude]

                candidates.append(side)
            sweep["loop_candidates"] = candidates
        if loops:
            sweep["loops"] = []
        if handles:
            sweep["handles"] = []
        if avg_face_normals:
            inos = []
            for v in sweep["verts"]:
                inos.append(
                    average_normals(
                        [
                            f.normal.normalized()
                            for f in v.link_faces
                            if not f.select and f not in sweep["edges"][0].link_faces
                        ]
                    )
                )
            sweep["avg_face_normals"] = inos
        if rail_lengths:
            rlens = []

            if idx == 0:
                rlens.extend([0, 0])
            else:
                vA = vertpair[0]
                priorvA = rails[0][idx - 1]

                vB = vertpair[1]
                priorvB = rails[1][idx - 1]

                distA = get_distance_between_verts(vA, priorvA)
                distB = get_distance_between_verts(vB, priorvB)

                rlens.extend([distA, distB])

            sweep["rail_lengths"] = rlens

        sweeps.append(sweep)
        if debug:
            debug_sweeps(
                [sweeps[-1]],
                index=idx,
                verts=verts,
                edges=edges,
                loop_candidates=loop_candidates,
                loops=loops,
                handles=handles,
                avg_face_normals=avg_face_normals,
                rail_lengths=rail_lengths,
            )

    return sweeps


def debug_sweeps(
    sweeps,
    index=None,
    cyclic=False,
    verts=True,
    edges=True,
    loop_candidates=True,
    loops=True,
    loop_types=True,
    handles=True,
    avg_face_normals=True,
    rail_lengths=True,
):
    for idx, sweep in enumerate(sweeps):
        if index:
            idx = index
        print("sweep:", idx)
        if verts:
            print("  • verts:", sweep["verts"][0].index, " - ", sweep["verts"][1].index)
        if edges:
            print("  • edges:", sweep["edges"][0].index)
        if loop_candidates:
            print("  • loop_candidates:", [[l.index for l in lcs] for lcs in sweep["loop_candidates"]])
        if loops:
            print("  • loops:")
            for idx, loop_tuple in enumerate(sweep["loops"]):
                loop_type, remote_co, loop_edge_idx, angle, smooth, bevel_weight = loop_tuple
                print(
                    "    %d." % idx,
                    "type:",
                    loop_type,
                    "remote co:",
                    remote_co,
                    "edge index:",
                    loop_edge_idx,
                    "angle:",
                    angle,
                    "smooth:",
                    smooth,
                    "bevel weight:",
                    bevel_weight,
                )
        if handles:
            print("  • handles:", [hco for hco in sweep["handles"]])
        if avg_face_normals:
            print("  • avg_face_normals:", [ino for ino in sweep["avg_face_normals"]])
        if rail_lengths:
            print("  • rail lengths:", [length for length in sweep["rail_lengths"]])
        print()

    if cyclic:
        print("Selection is cyclic!")


def negate_string(floatstring):
    if floatstring.startswith("-"):
        return floatstring[1:]
    else:
        return "-" + floatstring


def normal_clear(active, limit=False):
    bpy.ops.object.mode_set(mode="OBJECT")

    mesh = active.data

    if bpy.app.version < (4, 1, 0):
        mesh.calc_normals_split()

    loop_normals = []
    for loop in mesh.loops:
        loop_normals.append(loop.normal)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    verts = [v for v in bm.verts if v.select]
    faces = [f for f in bm.faces if f.select]

    for v in verts:
        for l in v.link_loops:
            if not limit or l.face in faces:
                loop_normals[l.index] = Vector()

    mesh.normals_split_custom_set(loop_normals)

    if bpy.app.version < (4, 1, 0):
        mesh.use_auto_smooth = True

    bpy.ops.object.mode_set(mode="EDIT")

    return True


def normal_transfer_from_obj(active, nrmsrc, vertids=False, vgroup=False, remove_vgroup=False):
    bpy.ops.object.mode_set(mode="OBJECT")

    if vertids:
        vgroup = add_vgroup(active, "NormalTransfer", vertids)
        vgname = vgroup.name

    if vgroup:
        data_transfer = add_normal_transfer_mod(active, nrmsrc, vgname, vgroup)
        apply_mod(data_transfer.name)

        if remove_vgroup and (vg := active.vertex_groups.get(vgname)):
            active.vertex_groups.remove(vg)

    bpy.ops.object.mode_set(mode="EDIT")


def add_vgroup(obj, name="", ids=[], weight=1):
    vgroup = obj.vertex_groups.new(name=name)
    if ids:
        vgroup.add(ids, weight, "ADD")

    else:
        obj.vertex_groups.active_index = vgroup.index
        bpy.ops.object.vertex_group_assign()


def add_normal_transfer_mod(obj, nrmsrc, name, vgroup, mapping=None):
    data_transfer = obj.modifiers.new(name, "DATA_TRANSFER")
    data_transfer.object = nrmsrc
    data_transfer.use_loop_data = True

    if mapping:
        data_transfer.loop_mapping = loop_mapping_dict[mapping]
    else:
        data_transfer.loop_mapping = loop_mapping_dict["NEAREST FACE"]

    data_transfer.vertex_group = vgroup.name

    data_transfer.data_types_loops = {"CUSTOM_NORMAL"}
    data_transfer.show_expanded = False
    data_transfer.show_in_editmode = True

    data_transfer.use_object_transform = False

    if bpy.app.version < (4, 1, 0):
        obj.data.use_auto_smooth = True

    return data_transfer


def apply_mod(modname):
    bpy.ops.object.modifier_apply(modifier=modname)
