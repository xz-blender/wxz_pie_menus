import math # type: ignore
import mathutils
from .math import *
from .utils import *
from .draw import  *
def biggest_angle_loop(vert, edge, loop_candidates, bw, debug=False):
    angles = []
    for e in loop_candidates:
        a = int(get_angle_between_edges(edge, e, radians=False))
        angles.append((a, e))

    angles = sorted(angles, key=lambda a: a[0], reverse=True)

    a1 = angles[0][0]
    a2 = angles[1][0]

    if abs(a1 - a2) < 10:
        if debug:
            print("angles (almost) the same")
        return

    angle, loop_edge = angles[0]
    remote_co = loop_edge.other_vert(vert).co.copy()

    if debug:
        mx = bpy.context.active_object.matrix_world
        if type(debug) is list:
            if vert.index in debug:
                print("biggest angle loop:", loop_edge.index)
                draw_line([vert.co.copy(), remote_co], mx=mx, color=(1, 1, 1), modal=False)

        else:
            print("biggest angle loop:", loop_edge.index)
            draw_line([vert.co.copy(), remote_co], mx=mx, color=(1, 1, 1), modal=False)

    return "BIGGEST_ANGLE", remote_co, loop_edge.index, angle, loop_edge.smooth, loop_edge[bw] if bw else 0
def topo_loop(vert, loop_candidates, bw, debug=False):

    loop_edge = loop_candidates[0]
    remote_co = loop_edge.other_vert(vert).co.copy()

    if debug:
        mx = bpy.context.active_object.matrix_world
        if type(debug) is list:
            if vert.index in debug:
                print("topo loop:", loop_edge.index)
                draw_line([vert.co.copy(), remote_co], mx=mx, color=(1, 1, 1), modal=False)
        else:
            print("topo loop:", loop_edge.index)
            draw_line([vert.co.copy(), remote_co], mx=mx, color=(1, 1, 1), modal=False)

    return "TOPO", remote_co, loop_edge.index, None, loop_edge.smooth, loop_edge[bw] if bw else 0
def projected_loop(vert, edge, debug=False):

    face = [f for f in vert.link_faces if not f.select and f not in edge.link_faces][0]

    v1 = vert
    v2 = edge.other_vert(v1)

    normals = [f.normal.normalized() for f in edge.link_faces if f.select]

    avg_edge_normal = average_normals(normals) * 0.1

    if debug:
        mx = bpy.context.active_object.matrix_world
        draw_vector(avg_edge_normal, origin=v1.co.copy(), mx=mx, color=(0.5, 0.5, 1), modal=False)

    avg_edge_face_normals = average_normals([avg_edge_normal, face.normal])
    v1_v2_dir = v2.co - v1.co

    dot = v1_v2_dir.dot(avg_edge_face_normals)

    if dot < 0:
        v1co_offset = v1.co - avg_edge_normal
        if debug:
            print("Offsetting in a negative direction")
            draw_point(v1co_offset, mx=mx, color=(1, 0, 0), modal=False)
    else:
        v1co_offset = v1.co + avg_edge_normal
        if debug:
            print("Offsetting in a positive direction")
            draw_point(v1co_offset, mx=mx, color=(1, 0, 0), modal=False)

    edge_dir = v1.co - v2.co
    ext_edgeco = v1co_offset + edge_dir

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                draw_line([v1co_offset, ext_edgeco], mx=mx, color=(0, 1, 0), modal=False)
        else:
            draw_line([v1co_offset, ext_edgeco], mx=mx, color=(0, 1, 0), modal=False)

    perpco = ext_edgeco - face.normal

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                draw_line([ext_edgeco, perpco], mx=mx, color=(0, 0, 1), modal=False)
        else:
            draw_line([ext_edgeco, perpco], mx=mx, color=(0, 0, 1), modal=False)

    ico = mathutils.geometry.intersect_line_plane(ext_edgeco, perpco, v1.co, face.normal)

    if debug:
        draw_point(ico, mx=mx, color=(1, 1, 1), modal=False)

    if debug:
        if type(debug) is list:
            if vert.index in debug:
                draw_line([vert.co.copy(), ico], mx=mx, color=(1, 1, 1), modal=False)
        else:
            draw_line([vert.co.copy(), ico], mx=mx, color=(1, 1, 1), modal=False)

    return "PROJECTED", ico, None, None, True, 0
def get_loops(bm, bw, faces, sweeps, force_projected=False, debug=False):

    for sweep in sweeps:
        for idx, v in enumerate(sweep["verts"]):
            vert_debug_print(debug, v, "\n" + str(v.index), end=" • ")

            ccount = len(sweep["loop_candidates"][idx])
            vert_debug_print(debug, v, "\nloop count: " + str(ccount))

            if ccount == 0 or force_projected:
                loop_tuple = projected_loop(v, sweep["edges"][0], debug=debug)
                sweep["loops"].append(loop_tuple)

            elif ccount == 1:
                loop_candidate = sweep["loop_candidates"][idx][0]
                edge = sweep["edges"][0]
                link_edges = [e for e in v.link_edges]

                if not edge.is_manifold:
                        vert_debug_print(debug, v, "topo loop next to an open boundary")
                elif check_ngon(edge):
                    if check_ngon(loop_candidate):
                        vert_debug_print(debug, v, "topo loop next to an ngon")
                elif check_ngon(loop_candidate) and len(link_edges) == 3:
                    if 89 < math.degrees(edge.calc_face_angle()) < 91:
                        vert_debug_print(debug, v, "topo loop next to face angled at 90 degrees")
                    else:
                        vert_debug_print(debug, v, "projected loop redirect")
                        loop_tuple = projected_loop(v, sweep["edges"][0], debug=debug)
                        sweep["loops"].append(loop_tuple)
                        continue
                else:
                    vert_debug_print(debug, v, "normal topo loop")

                loop_tuple = topo_loop(v, sweep["loop_candidates"][idx], bw, debug=debug)
                sweep["loops"].append(loop_tuple)

            else:
                loop_tuple = biggest_angle_loop(v, sweep["edges"][0], sweep["loop_candidates"][idx], bw, debug=debug)

                if loop_tuple:
                    loop_type, _, loop_edge_idx, angle, _, _ = loop_tuple
                    vert_debug_print(debug, v, "angle: " + str(angle))

                    if 89 <= angle <= 91:  # NOTE: this may need to be dialed in
                        vert_debug_print(debug, v, "topo loop redirect after biggest angle returned a 90 degrees angle")
                        loop2_tuple = topo_loop(v, sweep["loop_candidates"][idx], bw, debug=debug)
                        loop2_type, _, loop2_edge_idx, _, _, _ = loop2_tuple

                        if loop_edge_idx == loop2_edge_idx:
                            vert_debug_print(debug, v, "projected loop redirect after topo loop returned the same loop as the biggest angle loop")

                            loop_tuple = projected_loop(v, sweep["edges"][0], debug=debug)
                            sweep["loops"].append(loop_tuple)

                        else:
                            sweep["loops"].append(loop2_tuple)
                    else:
                        sweep["loops"].append(loop_tuple)
                else:
                    vert_debug_print(debug, v, "projected loop after biggest angle loop found no definitive result")
                    loop_tuple = projected_loop(v, sweep["edges"][0], debug=debug)
                    sweep["loops"].append(loop_tuple)

def get_tri_corner_loops(bm, bw, faces, sweeps, debug=False):
    if debug:
        print()

    for sweep in sweeps:
        for idx, v in enumerate(sweep["verts"]):
            vert_debug_print(debug, v, "\n" + str(v.index), end=" • ")

            ccount = len(sweep["loop_candidates"][idx])
            vert_debug_print(debug, v, "\nloop count: " + str(ccount))

            loop_tuple = topo_loop(v, sweep["loop_candidates"][idx], bw, debug=debug)
            sweep["loops"].append(loop_tuple)
