from mathutils.geometry import intersect_line_line, intersect_line_plane, intersect_point_line, interpolate_bezier, normal
import bmesh
import bpy
from math import degrees # type: ignore
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d
from .ui import *

def change_width(bm, sweeps, width, taper=False, debug=False):
    if taper:
        totallen1 = sum([s["rail_lengths"][0] for s in sweeps])
        totallen2 = sum([s["rail_lengths"][1] for s in sweeps])

        if debug:
            print("total length 1:", totallen1)
            print("total length 2:", totallen2)

    v1 = sweeps[0]["verts"][0]
    v1_next = sweeps[1]["verts"][0]

    v2 = sweeps[0]["verts"][1]
    v2_next = sweeps[1]["verts"][1]

    loop1 = sweeps[0]["loops"][0]
    loop1_next = sweeps[1]["loops"][0]

    loop2 = sweeps[0]["loops"][1]
    loop2_next = sweeps[1]["loops"][1]

    loop1_dir = v1.co + (loop1[1] - v1.co).normalized() * width
    loop2_dir = v2.co + (loop2[1] - v2.co).normalized() * width

    rail1_dir = v1_next.co - v1.co
    rail2_dir = v2_next.co - v2.co

    h1 = intersect_line_line(loop1_dir, loop1_dir + rail1_dir, v1_next.co, loop1_next[1])
    h2 = intersect_line_line(loop2_dir, loop2_dir + rail2_dir, v2_next.co, loop2_next[1])

    if taper:
        rlen1 = 0
        rlen2 = 0

    if h1 and h2:
        if not taper:
            v1.co = loop1_dir
            v2.co = loop2_dir

        loop1_ends = []
        loop1_ends.append(h1[0])  # maybe average h[0] and h[1] instead of taking just the first?, they should be the same, but you never know?

        loop2_ends = []
        loop2_ends.append(h2[0])

        for idx, sweep in enumerate(sweeps):
            if idx == 0:  # skip first index, its done above
                continue
            if idx == len(sweeps) - 1:
                v1_next.co = h1[0]
                v2_next.co = h2[0]
                break

            v1 = sweep["verts"][0]
            v1_next = sweeps[idx + 1]["verts"][0]

            v2 = sweep["verts"][1]
            v2_next = sweeps[idx + 1]["verts"][1]

            loop1 = sweep["loops"][0]
            loop1_next = sweeps[idx + 1]["loops"][0]

            loop2 = sweep["loops"][1]
            loop2_next = sweeps[idx + 1]["loops"][1]

            loop1_end = loop1_ends[-1]
            loop1_end_next = loop1_next[1]

            loop2_end = loop2_ends[-1]
            loop2_end_next = loop2_next[1]

            loop1_dir = v1.co + (loop1_end - v1.co)
            sweep1_dir = v1_next.co - v1.co

            loop2_dir = v2.co + (loop2_end - v2.co)
            sweep2_dir = v2_next.co - v2.co

            if taper:
                rlen1 += sweep["rail_lengths"][0]
                rlen2 += sweep["rail_lengths"][1]

                r1 = rlen1 / totallen1
                r2 = rlen2 / totallen2

                if debug:
                    print("accumulated 1:", rlen1)
                    print("accumulated 2:", rlen2)

                    print("factor 1:", r1)
                    print("factor 2:", r2)

                taper1_dir = v1.co + (loop1_end - v1.co) * r1
                taper2_dir = v2.co + (loop2_end - v2.co) * r2

                v1.co = taper1_dir
                v2.co = taper2_dir

            else:
                v1.co = loop1_dir
                v2.co = loop2_dir

            h1 = intersect_line_line(loop1_dir, loop1_dir + sweep1_dir, v1_next.co, loop1_end_next)
            h2 = intersect_line_line(loop2_dir, loop2_dir + sweep2_dir, v2_next.co, loop2_end_next)

            if h1 and h2:
                loop1_ends.append(h1[0])
                loop2_ends.append(h2[0])
            else:
                return False
    else:
        return False

    return True
def create_splines(bm, sweeps, segments, debug=False):
    spline_sweeps = []
    for idx, sweep in enumerate(sweeps):
        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        handle1co = sweep["handles"][0]
        handle2co = sweep["handles"][1]

        bezier_verts = interpolate_bezier(v1.co, handle1co, handle2co, v2.co, segments + 2)[1:-1]

        spline_verts = []
        spline_verts.append(v1)

        for vco in bezier_verts:
            v = bm.verts.new()
            v.co = vco
            spline_verts.append(v)

        spline_verts.append(v2)

        if debug:
            bm.verts.index_update()
            print("sweep:", idx)
            print(" • spline verts:", [v.index for v in spline_verts])
            print()
            for vert in spline_verts:
                vert.select = True

        spline_sweeps.append(spline_verts)

    return spline_sweeps

def fuse_surface(bm, spline_sweeps, smooth, capholes=True, capdissolveangle=10, cyclic=False, select=True, debug=False):
    faces = []

    for sweepidx, sweep in enumerate(spline_sweeps):
        for railidx, vert in enumerate(sweep):
            fc1 = vert  # sweep[railidx]
            fc2 = sweep[railidx + 1]

            fc3 = spline_sweeps[sweepidx + 1][railidx + 1]
            fc4 = spline_sweeps[sweepidx + 1][railidx]

            face_corners = [fc1, fc2, fc3, fc4]
            face = bm.faces.new(face_corners)
            if smooth:
                face.smooth = True
            faces.append(face)

            if debug:
                bm.faces.index_update()
                print("face:", face.index, "verts:", [fc.index for fc in face_corners])

            if railidx + 2 == len(sweep):
                break

        if sweepidx + 2 == len(spline_sweeps):
            break

    bmesh.ops.recalc_face_normals(bm, faces=faces)

    no_caps_selected = True
    caps = []
    if capholes or cyclic:
        border1 = spline_sweeps[0]
        border2 = spline_sweeps[-1]

        if debug:
            border1_ids = [v.index for v in border1]
            border2_ids = [v.index for v in border2]

            print("border1:", border1_ids)
            print("border2:", border2_ids)

        if cyclic:
            cyclic_faces = []
            for idx, (sweep1_vert, sweep2_vert) in enumerate(zip(border1, border2)):
                fc1 = sweep1_vert  # border1[idx]
                fc2 = border1[idx + 1]
                fc3 = border2[idx + 1]
                fc4 = sweep2_vert  # border2[idx]

                face_corners = [fc1, fc2, fc3, fc4]
                face = bm.faces.new(face_corners)
                if smooth:
                    face.smooth = True
                cyclic_faces.append(face)

                if idx + 2 == len(border1):
                    bmesh.ops.recalc_face_normals(bm, faces=cyclic_faces)
                    break

            if select:
                for f in faces + cyclic_faces:
                    f.select = True

            return faces + cyclic_faces, None

        caps.extend([bm.faces.new(b) for b in [border1, border2]])
        bmesh.ops.recalc_face_normals(bm, faces=caps)

        cap1_edge = bm.edges.get([border1[0], border1[-1]])
        cap2_edge = bm.edges.get([border2[0], border2[-1]])

        if cap1_edge.is_manifold:
            cap1_angle = degrees(cap1_edge.calc_face_angle())

            if debug:
                print("cap1 angle:", cap1_angle)

            if cap1_angle < capdissolveangle or cap1_angle > 181 - capdissolveangle:
                bmesh.ops.dissolve_edges(bm, edges=[cap1_edge])

                if smooth:
                    border1vert = border1[1]
                    cap1face = [f for f in border1vert.link_faces if f not in faces][0]
                    cap1face.smooth = True

        if cap2_edge.is_manifold:
            cap2_angle = degrees(cap2_edge.calc_face_angle())

            if debug:
                print("cap2 angle:", cap2_angle)

            if cap2_angle < capdissolveangle or cap2_angle > 181 - capdissolveangle:
                bmesh.ops.dissolve_edges(bm, edges=[cap2_edge])

                if smooth:
                    border2vert = border2[1]
                    cap2face = [f for f in border2vert.link_faces if f not in faces][0]
                    cap2face.smooth = True

        if cap1_edge.is_valid:
            caps[0].select = True
            no_caps_selected = False
            bm.select_history.add(caps[0])

        if cap2_edge.is_valid:
            caps[1].select = True
            no_caps_selected = False
            bm.select_history.add(caps[1])

    if select:
        if no_caps_selected or not caps or cyclic:
            for f in faces:
                f.select = True

    return faces, caps

def set_sweep_sharps_and_bweights(bm, bw, sweeps, spline_sweeps, vg=None):
    for sweep, verts in zip(sweeps, spline_sweeps):
        loops = sweep["loops"]

        sharp = not all([loop[4] for loop in loops])
        bweight = max([loop[5] for loop in loops])

        sweep_edges = [bm.edges.get([vert, verts[idx + 1]]) for idx, vert in enumerate(verts) if idx < len(verts) - 1]

        for se in sweep_edges:
            if sharp:
                se.smooth = False

            if bweight > 0:
                se[bw] = bweight

        if vg and dict(verts[0][vg]) == dict(verts[-1][vg]):
            for v in verts[1:-1]:
                for idx, weight in verts[0][vg].items():
                    v[vg][idx] = weight
def clear_rail_sharps_and_bweights(bm, bw, rails, cyclic, select=False):
    if cyclic:
        rails[0].append(rails[0][0])
        rails[1].append(rails[1][0])

    for rail in rails:
        rail_edges = [bm.edges.get([vert, rail[idx + 1]]) for idx, vert in enumerate(rail) if idx < len(rail) - 1]

        for re in rail_edges:
            re.smooth = True
            re[bw] = 0

            re.select = select

def unfuse(bm, faces, sweeps, debug=False):
    edgeloops = []
    edgeloopverts = []

    for sweep in sweeps[1:-1]:
        e = bm.edges.get(sweep)
        edgeloops.append(e)
        edgeloopverts.extend([v for v in sweep])

        for loop in e.link_loops:
            while len(loop.vert.link_edges) == 4:
                loop = loop.link_loop_prev.link_loop_radial_prev.link_loop_prev

                next_e = loop.edge
                if next_e in edgeloops:  # cyclicity
                    break
                else:
                    edgeloops.append(next_e)
                    edgeloopverts.extend([v for v in next_e.verts if v not in edgeloopverts])

    removedgeloops = []
    edgeloopfaces = []
    for e in edgeloops:
        for f in e.link_faces:
            if f not in edgeloopfaces:
                if len(f.verts) == 4:  # some edges may go further than desired, see 065_unfuse_fail, this is just aimple check to only include quads, it may still contain undesired polys however
                    edgeloopfaces.append(f)
                    f.select = True
                else:
                    removedgeloops.append(e)

    for e in removedgeloops:
        if e in edgeloops:
            edgeloops.remove(e)
        for v in e.verts:
            if v in edgeloopverts:
                edgeloopverts.remove(v)

    otherfaces = [f for f in bm.faces if f not in edgeloopfaces]

    try:
        bmesh.ops.dissolve_edges(bm, edges=edgeloops)
        bmesh.ops.dissolve_verts(bm, verts=edgeloopverts)
        bm.verts.ensure_lookup_table()

        bm.select_flush(True)

        for f in otherfaces:
            if f.is_valid:
                f.select = False

        return [f for f in bm.faces if f.select]
    except:
        popup_message(["You can't unfuse bevels with triangular coners", "Turn them into Quad Corners first!"], title="Illegal Selection")
        return

def set_rail_sharps_and_bweights(bm, bw, rails, cyclic, sharps=True, bweights=True, bweight=1):
    if cyclic:
        rails[0].append(rails[0][0])
        rails[1].append(rails[1][0])

    if sharps:
        bpy.context.space_data.overlay.show_edge_sharp = True
    if bweights:
        bpy.context.space_data.overlay.show_edge_bevel_weight = True

    for rail in rails:
        rail_edges = [bm.edges.get([vert, rail[idx + 1]]) for idx, vert in enumerate(rail) if idx < len(rail) - 1]

        for re in rail_edges:
            if sharps:
                re.smooth = False
            if bweights:
                re[bw] = bweight

def unchamfer_face_intersection(bm, sweeps, slide=0, debug=False):
    double_verts = []

    for face in bm.faces:
        face.select_set(False)

    for sweep in sweeps:
        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        h1co = sweep["handles"][0]
        h2co = sweep["handles"][1]

        remapped_avg = slide * 0.5 + 0.5
        slided_h = get_center_between_points(h1co, h2co, remapped_avg)

        if debug:
            mx = bpy.context.active_object.matrix_world
            draw_point(h1co, mx=mx, color=(0, 1, 0), modal=False)
            draw_point(h2co, mx=mx, color=(0, 1, 0), modal=False)
            draw_point(slided_h, mx=mx, color=(1, 1, 1), modal=False)

        v1.co = slided_h
        v2.co = slided_h

        v1.select = True
        v2.select = True
        bm.select_flush(True)

        double_verts.extend([v1, v2])

    return double_verts

def unchamfer_loop_intersection(bm, sweeps, debug=False):
    double_verts = []

    for face in bm.faces:
        face.select_set(False)

    for sweep in sweeps:
        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        h1co = sweep["handles"][0]
        h2co = sweep["handles"][1]

        h = intersect_line_line(v1.co, h1co, v2.co, h2co)

        if h:
            if debug:
                mx = bpy.context.active_object.matrix_world
                draw_point(h[0], mx=mx, color=(1, 1, 1), modal=False)

            v1.co = h[0]
            v2.co = h[0]

            v1.select = True
            v2.select = True
            bm.select_flush(True)

            double_verts.extend([v1, v2])
        else:
            return False

    return double_verts

def set_sharps_and_bweights(edges, bw=None, sharps=True, bweights=True, bweight=1):
    if any([sharps, bweights]):
        if sharps:
            bpy.context.space_data.overlay.show_edge_sharp = True

        if bweights:
            bpy.context.space_data.overlay.show_edge_bevel_weight = True

    for e in edges:
        e.smooth = not sharps

        if bweights:
            e[bw] = bweight

        else:
            e[bw] = 0

def align_vert_sequence_to_spline(bm, seq, width, width2, tension, tension2, fade=0, merge=False, merge_verts=[], flipped=False, widthlinked=False, tensionlinked=False, advanced=False, debug=False):
    if merge:
        tension = tension2 = 1

    remote1 = seq[0]
    end1 = seq[1]

    remote2 = seq[-1]
    end2 = seq[-2]

    if debug:
        print("remote 1:", remote1.index, "end 1:", end1.index)
        print("remote 2:", remote2.index, "end 2:", end2.index)

        mx = bpy.context.active_object.matrix_world
        draw_point(end1.co.copy(), mx=mx, color=(1, 1, 0), modal=False)
        draw_point(end2.co.copy(), mx=mx, color=(1, 1, 0), modal=False)

    loop1_dir = remote1.co - end1.co
    loop2_dir = remote2.co - end2.co

    if widthlinked:
        width2 = width

    if flipped:
        start1co = end1.co + (remote1.co - end1.co).normalized() * width2
        start2co = end2.co + (remote2.co - end2.co).normalized() * width
    else:
        start1co = end1.co + (remote1.co - end1.co).normalized() * width
        start2co = end2.co + (remote2.co - end2.co).normalized() * width2

    if debug:
        draw_point(start1co, mx=mx, color=(1, 0, 0), modal=False)
        draw_point(start2co, mx=mx, color=(0, 1, 0), modal=False)

    if debug:
        s1 = bm.verts.new()
        s1.co = start1co

        s2 = bm.verts.new()
        s2.co = start2co

    h = intersect_line_line(end1.co, remote1.co, end2.co, remote2.co)

    loop_angle = degrees(loop1_dir.angle(loop2_dir))

    if debug:
        print("loop angle:", loop_angle)

    if h is None or 178 <= loop_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
        if debug:
            print(" • handles could not be determined via line-line instersection")
            print(" • falling back to closest point to handle vector")

        h1_full = intersect_point_line(end2.co, end1.co, remote1.co)[0]
        h2_full = intersect_point_line(end1.co, end2.co, remote2.co)[0]

        h1 = end1.co + (h1_full - end1.co)
        h2 = end2.co + (h2_full - end2.co)

        h = (h1, h2)

    if not advanced or tensionlinked:
        tension2 = tension

    if flipped:
        handle1co = start1co + (h[0] - start1co) * tension2
        handle2co = start2co + (h[1] - start2co) * tension

    else:
        handle1co = start1co + (h[0] - start1co) * tension
        handle2co = start2co + (h[1] - start2co) * tension2

    if debug:
        draw_point(handle1co, mx=mx, color=(1, 1, 1), modal=False)
        draw_point(handle2co, mx=mx, color=(1, 1, 1), modal=False)

    if merge:
        for idx, vert in enumerate(seq[1:-1]):
            vert.co = get_center_between_points(handle1co, handle2co)

        merge_verts.append(seq[1:-1])
    else:
        bezierverts = interpolate_bezier(start1co, handle1co, handle2co, start2co, len(seq) - 2)

        for idx, vert in enumerate(seq[1:-1]):
            vert.co = bezierverts[idx] + (vert.co - bezierverts[idx]) * fade

def turn_corner(bm, verts, faces, width, debug=False):
    if debug:
        print()

    sel_face = faces[0]

    inner_verts = [v for v in verts if len(v.link_edges) == 3]

    c1 = inner_verts[0]
    c2 = inner_verts[1]

    c1_loop = [l for l in c1.link_loops if l in sel_face.loops][0]

    if debug:
        print("c1 next loop vert:", c1_loop.link_loop_next.vert.index)

    if not c1_loop.link_loop_next.vert == c2:
        c1, c2 = c2, c1
        if debug:
            print("switched c1 < > c2, to ensure clock-wise rotation")

    inner_edge = bm.edges.get([c1, c2])
    if debug:
        print("inner edge:", inner_edge.index)
        mx = bpy.context.active_object.matrix_world
        draw_line([v.co.copy() for v in inner_edge.verts], mx=mx, color=(0, 1, 0), modal=False)

    c1_edge = [e for e in c1.link_edges if e != inner_edge and e.select][0]
    c2_edge = [e for e in c2.link_edges if e != inner_edge and e.select][0]

    c3 = c1_edge.other_vert(c1)
    c4 = c2_edge.other_vert(c2)

    if debug:
        print("c1:", c1.index)
        print("c1_edge:", c1_edge.index)
        print("c3:", c3.index)

        print("c2:", c2.index)
        print("c2_edge:", c2_edge.index)
        print("c4:", c4.index)

    c3_edges = [e for e in c3.link_edges if not e.select]

    c3_edge1 = c3_edges[0]
    c3_edge2 = c3_edges[1]

    c3_c4_edge = bm.edges.get([c3, c4])

    if debug:
        print("c3 edge1:", c3_edge1.index)
        print("c3 edge2:", c3_edge2.index)
        print("c3 c4 edge:", c3_c4_edge.index)
        draw_line([v.co.copy() for v in c3_edge1.verts], mx=mx, color=(1, 0, 0), modal=False)
        draw_line([v.co.copy() for v in c3_edge2.verts], mx=mx, color=(0, 0, 1), modal=False)

    new_c1co = c3.co + (c3_edge1.other_vert(c3).co - c3.co).normalized() * width
    new_c2co = c3.co + (c3_edge2.other_vert(c3).co - c3.co).normalized() * width

    new_c1 = bm.verts.new()
    new_c1.co = new_c1co

    new_c2 = bm.verts.new()
    new_c2.co = new_c2co

    bm.verts.index_update()

    if debug:
        print("new_c1:", new_c1.index)
        print("new_c2:", new_c2.index)
        draw_point(new_c1.co.copy(), mx=mx, color=(1, 1, 1), modal=False)
        draw_point(new_c2.co.copy(), mx=mx, color=(1, 1, 1), modal=False)

    bm.edges.new([new_c1, new_c2])

    if get_distance_between_verts(c1, new_c1) < get_distance_between_verts(c1, new_c2):
        bm.edges.new([c1, new_c1])
        bm.edges.new([c4, new_c2])
    else:
        bm.edges.new([c1, new_c2])
        bm.edges.new([c4, new_c1])
        new_c1, new_c2 = new_c2, new_c1

    c1_remote_edge = [e for e in c1.link_edges if e != c1_edge and e != inner_edge][0]
    c2_remote_edge = [e for e in c2.link_edges if e != c2_edge and e != inner_edge][0]

    if debug:
        print("c1 remote edge:", c1_remote_edge.index)
        print("c2 remote edge:", c2_remote_edge.index)
        draw_line([v.co.copy() for v in c1_remote_edge.verts], mx=mx, color=(1, 1, 0), modal=False)
        draw_line([v.co.copy() for v in c2_remote_edge.verts], mx=mx, color=(1, 1, 0), modal=False)

    h = intersect_line_line(c1.co, c1_remote_edge.other_vert(c1).co, c2.co, c2_remote_edge.other_vert(c2).co)

    face_A = [f for f in c1_edge.link_faces if f != sel_face][0]
    face_B = [f for f in c3_c4_edge.link_faces if f != sel_face][0]
    face_N = [f for f in c3.link_faces if f not in [sel_face, face_A, face_B]][0]

    if debug:
        print("face_A face:", face_A.index)
        print("face_B face:", face_B.index)
        print("face_N:", face_N.index)

    new_sel_face_verts = [c1, new_c1, new_c2, c4]
    face_A_verts = [v for v in face_A.verts]
    face_B_verts = [v for v in face_B.verts]
    face_N_verts = [v for v in face_N.verts]

    if debug:
        print("old face A verts:", [v.index for v in face_A_verts])
        print("old face B verts:", [v.index for v in face_B_verts])
        print("old face N verts:", [v.index for v in face_N_verts])

    face_A_c3_index = face_A_verts.index(c3)

    face_A_verts.insert(face_A_c3_index, new_c1)
    face_A_verts.remove(c3)

    face_B_c3_index = face_B_verts.index(c3)

    face_B_verts.insert(face_B_c3_index, new_c2)
    face_B_verts.remove(c3)

    face_N_c3_index = face_N_verts.index(c3)

    face_N_verts[face_N_c3_index:face_N_c3_index] = [new_c1, new_c2]
    face_N_verts.remove(c3)

    if debug:
        print("new face A verts:", [v.index for v in face_A_verts])
        print("new face B verts:", [v.index for v in face_B_verts])
        print("new face N verts:", [v.index for v in face_N_verts])

    new_faces = []

    new_faces.append(bm.faces.new(new_sel_face_verts))
    new_faces.append(bm.faces.new(face_A_verts))
    new_faces.append(bm.faces.new(face_B_verts))
    new_faces.append(bm.faces.new(face_N_verts))

    for f in new_faces:
        f.smooth = sel_face.smooth

    bmesh.ops.delete(bm, geom=[sel_face, face_A, face_B, face_N], context='FACES')

    bmesh.ops.pointmerge(bm, verts=[c1, c2], merge_co=h[0])

    bmesh.ops.recalc_face_normals(bm, faces=new_faces)

    new_faces[0].select = True

    new_edges = [e for e in new_faces[0].edges]
    new_edges.extend([e for e in new_faces[1].edges if e in new_faces[-1].edges])
    new_edges.extend([e for e in new_faces[2].edges if e in new_faces[-1].edges])

    return new_edges

def get_tri_corner_sharps_and_bweights(bm, bw, faces, sides, corners, debug=False):
    smooth = any([f.smooth for f in faces])

    sideedges = []
    for sidx, side in enumerate(sides):
        for vidx, v in enumerate(side):
            if vidx == len(side) - 1:
                if sidx == 0:
                    sideedges.append(bm.edges.get([v, sides[1][0]]))
                elif sidx == 1:
                    sideedges.append(bm.edges.get([v, sides[2][0]]))
                else:
                    sideedges.append(bm.edges.get([v, sides[0][0]]))
                break
            sideedges.append(bm.edges.get([v, side[vidx + 1]]))

    corneredges = []
    for v in corners:
        corneredges += [e for e in v.link_edges if e not in sideedges]

    sidesharps = False if all([e.smooth for e in sideedges]) else True
    cornersharps = False if all([e.smooth for e in corneredges]) else True

    sidebweights = True if any([e[bw] > 0 for e in sideedges]) else False
    cornerbweights = True if any([e[bw] > 0 for e in corneredges]) else False

    if debug:
        print("side sharps:", sidesharps)
        print("corner sharps:", cornersharps)

        print("side bweights:", sidebweights)
        print("corner bweights:", cornerbweights)

    return smooth, sidesharps, cornersharps, sidebweights, cornerbweights

def spread_tri_corner(sweeps, width, debug=False):
    sweeplen = len(sweeps)

    for idx, sweep in enumerate(sweeps):
        v1 = sweep["verts"][0]
        loop1 = sweep["loops"][0]

        dir1 = v1.co + (loop1[1] - v1.co).normalized() * width * (sweeplen - idx) / sweeplen
        v1.co = dir1

        v2 = sweep["verts"][1]
        loop2 = sweep["loops"][1]

        dir2 = v2.co + (loop2[1] - v2.co).normalized() * width * (sweeplen - idx) / sweeplen
        v2.co = dir2

        if debug:
            mx = bpy.context.active_object.matrix_world
            draw_point(dir1, mx=mx, color=(1, 0, 0), modal=False)
            draw_point(dir2, mx=mx, color=(0, 1, 0), modal=False)
def set_tri_corner_sharps_and_bweights(bm, bw, spline_sweeps, sidesharps, cornersharps, sidebweights, cornerbweights, fuse_faces):
    if any([sidesharps, cornersharps, sidebweights, cornerbweights]):
        for sweep in spline_sweeps:
            sweep[0].select = True
            sweep[-1].select = True

        for v in spline_sweeps[0]:
            v.select = True

        for v in spline_sweeps[-1]:
            v.select = True

        bm.select_flush(True)

        sideedges = [e for e in bm.edges if e.select]
        corneredges = [e for v in [spline_sweeps[0][0], spline_sweeps[0][-1]] for e in v.link_edges if e not in sideedges]

        for ssidx, v in enumerate(spline_sweeps[0]):
            if ssidx == len(spline_sweeps[0]) - 1:
                break
            corneredges.append(bm.edges.get([v, spline_sweeps[0][ssidx + 1]]))

        for e in sideedges:
            if sidesharps:
                e.smooth = False
            if sidebweights:
                e[bw] = 1

        for e in corneredges:
            if cornersharps:
                e.smooth = False
            if cornerbweights:
                e[bw] = 1

    for f in fuse_faces:
        f.select = True

def rebuild_corner_faces(bm, sides, rails, spline_sweeps, single, smooth, debug=False):
    c1 = sides[0][0]
    if debug:
        print("c1 vert:", c1.index)
        mx = bpy.context.active_object.matrix_world
        draw_point(c1.co.copy(), mx=mx, color=(1, 1, 0), modal=False)

    c1_faces = [f for f in c1.link_faces]

    if single:   # if the selection is a single face, it has to be the following for the A edge
        c1_edge_A = bm.edges.get([c1, sides[1][0]])
    else:
        c1_edge_A = bm.edges.get([c1, sides[0][1]])

    c1_edge_B = bm.edges.get([c1, sides[2][-1]])

    c1_face_A = [f for f in c1_edge_A.link_faces if not f.select][0]
    c1_face_B = [f for f in c1_edge_B.link_faces if not f.select][0]

    c1_faces.remove(c1_face_A)
    c1_faces.remove(c1_face_B)
    c1_face_N = c1_faces[0]

    if debug:
        print("c1_face A:", c1_face_A.index)
        print("c1_face B:", c1_face_B.index)
        print("c1_face N:", c1_face_N.index)

    c1_face_A_verts = [v for v in c1_face_A.verts]
    c1_face_B_verts = [v for v in c1_face_B.verts]
    c1_face_N_verts = [v for v in c1_face_N.verts]

    if debug:
        print("old c1_face_A_verts:", [v.index for v in c1_face_A_verts])
        print("old c1_face_B_verts:", [v.index for v in c1_face_B_verts])
        print("old c1_face_N_verts:", [v.index for v in c1_face_N_verts])
        draw_points([v.co.copy() for v in c1_face_A_verts], mx=mx, color=[1, 0, 0], modal=False)
        draw_points([v.co.copy() for v in c1_face_B_verts], mx=mx, color=[0, 1, 0], modal=False)
        draw_points([v.co.copy() for v in c1_face_N_verts], mx=mx, color=[0, 0, 1], modal=False)

    A_vert_idx = c1_face_A_verts.index(c1)
    B_vert_idx = c1_face_B_verts.index(c1)
    N_vert_idx = c1_face_N_verts.index(c1)

    if debug:
        print("A_vert index:", A_vert_idx)
        print("B_vert index:", B_vert_idx)
        print("N_vert index:", N_vert_idx)

    c1_face_A_verts.insert(A_vert_idx, rails[0][0])
    c1_face_A_verts.remove(c1)

    c1_face_B_verts.insert(B_vert_idx, rails[1][0])
    c1_face_B_verts.remove(c1)

    c1_face_N_verts[N_vert_idx:N_vert_idx] = spline_sweeps[0]
    c1_face_N_verts.remove(c1)

    if debug:
        print("new c1_face_A_verts:", [v.index for v in c1_face_A_verts])
        print("new c1_face_B_verts:", [v.index for v in c1_face_B_verts])
        print("new c1_face_N_verts:", [v.index for v in c1_face_N_verts])

    new_faces = []

    new_faces.append(bm.faces.new(c1_face_A_verts))
    new_faces.append(bm.faces.new(c1_face_B_verts))
    new_faces.append(bm.faces.new(c1_face_N_verts))

    bmesh.ops.delete(bm, geom=[c1_face_A, c1_face_B, c1_face_N], context='FACES_KEEP_BOUNDARY')
    bmesh.ops.delete(bm, geom=[c1_edge_A, c1_edge_B], context='EDGES')

    bmesh.ops.recalc_face_normals(bm, faces=new_faces)

    if smooth:
        for f in new_faces:
            f.smooth = True
