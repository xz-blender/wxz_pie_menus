import mathutils
import bpy
import math # type: ignore
import mathutils
from .utils import *
from .draw import *
from .math import *

def create_loop_intersection_handles(bm, sweeps, tension, debug=False):
    for idx, sweep in enumerate(sweeps):
        edge = sweep["edges"][0]
        edgelen = edge.calc_length()

        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        loop1 = sweep["loops"][0]
        loop1_dir = v1.co - loop1[1]

        loop2 = sweep["loops"][1]
        loop2_dir = v2.co - loop2[1]

        if debug:
            print()
            print("sweep:", idx)
            print(" • edge:", edge.index, "length:", edgelen)
            print(" • vert 1:", v1.index)
            print("   • loop type", loop1[0])
            print("     • loop end", loop1[1])
            print("     • loop index", loop1[2])
            print("     • direction", loop1_dir)
            print()
            print(" • vert 2:", v2.index)
            print("   • loop type", loop2[0])
            print("     • loop end", loop2[1])
            print("     • loop index", loop2[2])
            print("     • direction", loop2_dir)
            print()

        loop_angle = math.degrees(loop1_dir.angle(loop2_dir))

        if debug:
            print("loop angle:", loop_angle)

        h = mathutils.geometry.intersect_line_line(v1.co, loop1[1], v2.co, loop2[1])

        if debug:
            mx = bpy.context.active_object.matrix_world

            if h:
                draw_point(h[0], mx=mx, color=(1, 0, 0), modal=False)
                draw_point(h[1], mx=mx, color=(1, 0, 0), modal=False)

        if h is None and 178 <= loop_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
            if debug:
                print(" • handles could not be determined via line-line instersection")
                print(" • falling back to closest point to handle vector")

            h1_full = mathutils.geometry.intersect_point_line(v2.co, v1.co, loop1[1])[0]
            h2_full = mathutils.geometry.intersect_point_line(v1.co, v2.co, loop2[1])[0]

            h1 = v1.co + (h1_full - v1.co)
            h2 = v2.co + (h2_full - v2.co)

            if debug:
                draw_point(h1, mx=mx, color=(1, 1, 0), modal=False)
                draw_point(h2, mx=mx, color=(1, 1, 0), modal=False)

            h = (h1, h2)

        elif h is None and -2 <= loop_angle <= 2:  # if loops on both sides are parallel, this should not happen in a valid chamfer as its 90 degrees on both sides |._.|
            if debug:
                print(" • loops on both sides are parallel and go in the same direction")
                print(" • falling back to handle creation from loop edge")
            h1 = v1.co + (loop1[1] - v1.co).normalized()
            h2 = v2.co + (loop2[1] - v2.co).normalized()

            if debug:
                draw_point(h1, mx=mx, color=(0, 0, 1), modal=False)
                draw_point(h2, mx=mx, color=(0, 0, 1), modal=False)

            h = (h1, h2)

        if v1.co == h[0] or v2.co == h[1]:

            if debug:
                print(" • handle position lies on end point")
                print(" • falling back to handle creation from loop edge")

            h1 = v1.co + (loop1[1] - v1.co).normalized()
            h2 = v2.co + (loop2[1] - v2.co).normalized()

            h = (h1, h2)

        handle1co = v1.co + ((h[0] - v1.co) * tension)
        handle2co = v2.co + ((h[1] - v2.co) * tension)

        if debug:
            draw_point(handle1co, mx=mx, color=(0, 1, 0), modal=False)
            draw_point(handle2co, mx=mx, color=(0, 1, 0), modal=False)

        handle1_dir = handle1co - v1.co
        handle2_dir = handle2co - v2.co

        dot1 = loop1_dir.dot(handle1_dir)
        dot2 = loop2_dir.dot(handle2_dir)

        if dot1 < 0:
            handle1co = v1.co + loop1_dir.normalized() * handle1_dir.length
            handle1_dir = handle1co - v1.co

            if debug:
                print(" • flipped handle 1 direction")
                draw_point(handle1co, mx=mx, color=(1, 0, 0), modal=False)

        if dot2 < 0:
            handle2co = v2.co + loop2_dir.normalized() * handle2_dir.length
            handle2_dir = handle2co - v2.co

            if debug:
                print(" • flipped handle 2 direction")
                draw_point(handle2co, mx=mx, color=(1, 0, 0), modal=False)

        handle1_v1_dist = get_distance_between_points(v1.co, handle1co)
        handle2_v2_dist = get_distance_between_points(v2.co, handle2co)

        handle1_edge_ratio = handle1_v1_dist / edgelen
        handle2_edge_ratio = handle2_v2_dist / edgelen

        handle_dir_angle = handle1_dir.angle(handle2_dir) + 0.0001  # adding in a tiny amount to prevetn edge case where angle is 0

        ideal_ratio = tension / handle_dir_angle
        max_ratio = tension + ideal_ratio

        if handle1_edge_ratio > max_ratio or handle2_edge_ratio > max_ratio:
            if debug:
                print(" • surface angle:", math.degrees(handle_dir_angle), handle_dir_angle)
                print(" • ideal ratio:", ideal_ratio, "max ratio:", max_ratio)

            if handle1_edge_ratio > max_ratio:
                if debug:
                    print(" • handle overshoot! handle 1 to edge length ratio:", handle1_edge_ratio)
                    print(" • falling back to closest point to handle vector")

                h1_full = mathutils.geometry.intersect_point_line(v2.co, v1.co, loop1[1])[0]

                handle1co = v1.co + (h1_full - v1.co) * tension

                if debug:
                    draw_point(handle1co, mx=mx, color=(0, 1, 1), modal=False)

            if handle2_edge_ratio > max_ratio:
                if debug:
                    print(" • handle overshoot! handle 2 to edge length  ratio:", handle2_edge_ratio)
                    print(" • falling back to closest point to handle vector")

                h2_full = mathutils.geometry.intersect_point_line(v1.co, v2.co, loop2[1])[0]

                handle2co = v2.co + (h2_full - v2.co) * tension

                if debug:
                    draw_point(handle2co, mx=mx, color=(0, 1, 1), modal=False)

        sweep["handles"] = [handle1co, handle2co]

        if debug:
            draw_line([handle1co, v1.co.copy()], mx=mx, color=(1, 1, 1), modal=False)
            draw_line([handle2co, v2.co.copy()], mx=mx, color=(1, 1, 1), modal=False)
def create_face_intersection_handles(bm, sweeps, tension, average=False, debug=False):
    for idx, sweep in enumerate(sweeps):
        edge = sweep["edges"][0]
        edgelen = edge.calc_length()

        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        loop1 = sweep["loops"][0]
        loop1_dir = v1.co - loop1[1]

        loop2 = sweep["loops"][1]
        loop2_dir = v2.co - loop2[1]

        ino1 = sweep["avg_face_normals"][0]
        ino2 = sweep["avg_face_normals"][1]

        if debug:
            mx = bpy.context.active_object.matrix_world
            draw_vector(ino1 * 0.1, origin=v1.co.copy(), mx=mx, color=(0.5, 0.5, 1), modal=False)
            draw_vector(ino2 * 0.1, origin=v2.co.copy(), mx=mx, color=(0.5, 0.5, 1), modal=False)

            print()
            print("sweep:", idx)
            print(" • edge:", edge.index, "length:", edgelen)
            print(" • vert 1:", v1.index)
            print("   • loop type", loop1[0])
            print("     • loop end", loop1[1])
            print("     • loop index", loop1[2])
            print("     • direction", loop1_dir)
            print("   • intersection_normal", ino1)
            print()
            print(" • vert 2:", v2.index)
            print("   • loop type", loop2[0])
            print("     • loop end", loop2[1])
            print("     • loop index", loop2[2])
            print("     • direction", loop2_dir)
            print("   • intersection_normal", ino2)
            print()

        ico1 = mathutils.geometry.intersect_line_plane(v1.co, loop1[1], v2.co, ino2)
        ico2 = mathutils.geometry.intersect_line_plane(v2.co, loop2[1], v1.co, ino1)

        if not all([ico1, ico2]):
            if debug:
                print("WARNING: falling back to the old handle creation method")
            create_loop_intersection_handles(bm, [sweeps[idx]], tension, debug=debug)
        else:
            if debug:
                draw_point(ico1, mx=mx, color=(1, 0, 0), modal=False)
                draw_point(ico2, mx=mx, color=(1, 0, 0), modal=False)

            handle1co = v1.co + ((ico1 - v1.co) * tension)
            handle2co = v2.co + ((ico2 - v2.co) * tension)

            handle1_dir = handle1co - v1.co
            handle2_dir = handle2co - v2.co

            dot1 = loop1_dir.dot(handle1_dir)
            dot2 = loop2_dir.dot(handle2_dir)

            if dot1 < 0:
                handle1co = v1.co + loop1_dir.normalized() * handle1_dir.length
                handle1_dir = handle1co - v1.co

                if debug:
                    print(" • flipped handle 1 direction")

            if dot2 < 0:
                handle2co = v2.co + loop2_dir.normalized() * handle2_dir.length
                handle2_dir = handle2co - v2.co
                if debug:
                    print(" • flipped handle 2 direction")

            if average:
                handle1co = v1.co + handle1_dir.normalized() * (handle1_dir.length + handle2_dir.length) / 2
                handle2co = v2.co + handle2_dir.normalized() * (handle2_dir.length + handle1_dir.length) / 2

            sweep["handles"] = [handle1co, handle2co]

            if debug:
                draw_point(handle1co, mx=mx, color=(1, 1, 1), modal=False)
                draw_point(handle2co, mx=mx, color=(1, 1, 1), modal=False)

                draw_line([handle1co, v1.co.copy()], mx=mx, color=(1, 1, 1), modal=False)
                draw_line([handle2co, v2.co.copy()], mx=mx, color=(1, 1, 1), modal=False)
def create_tri_corner_handles(bm, sweeps, tension, debug=False):
    for sweep in sweeps:
        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        loop1 = sweep["loops"][0]
        loop1_dir = v1.co - loop1[1]

        loop2 = sweep["loops"][1]
        loop2_dir = v2.co - loop2[1]

        if debug:
            print(" • vert 1:", v1.index)
            print("   • loop type", loop1[0])
            print("     • loop end", loop1[1])
            print("     • direction", loop1_dir)
            print()
            print(" • vert 2:", v2.index)
            print("   • loop type", loop2[0])
            print("     • loop end", loop2[1])
            print("     • direction", loop2_dir)
            print()

        h = mathutils.geometry.intersect_line_line(v1.co, loop1[1], v2.co, loop2[1])

        handle1co = v1.co + ((h[0] - v1.co) * tension)
        handle2co = v2.co + ((h[1] - v2.co) * tension)

        sweep["handles"] = [handle1co, handle2co]

        if debug:
            handle1 = bm.verts.new()
            handle1.co = handle1co

            handle2 = bm.verts.new()
            handle2.co = handle2co

            bm.edges.new((v1, handle1))
            bm.edges.new((v2, handle2))
