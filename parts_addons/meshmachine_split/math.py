from math import degrees, sqrt, pi, sin, cos, radians
from mathutils import Vector, Matrix, geometry
from random import choice
from .vars import *
from .utils import *


def remap(value, srcMin, srcMax, resMin, resMax):
    srcRange = srcMax - srcMin
    if srcRange == 0:
        return resMin
    else:
        resRange = resMax - resMin
        return (((value - srcMin) * resRange) / srcRange) + resMin

def flatten_matrix(mx):
    dimension = len(mx)
    return [mx[j][i] for i in range(dimension) for j in range(dimension)]

def get_loc_matrix(location):
    return Matrix.Translation(location)

def get_rot_matrix(rotation):
    return rotation.to_matrix().to_4x4()

def get_sca_matrix(scale):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = scale[i]
    return scale_mx

def get_center_between_verts(vert1, vert2, center=0.5):
    return get_center_between_points(vert1.co, vert2.co, center=center)

def get_center_between_points(point1, point2, center=0.5):
    return point1 + (point2 - point1) * center

def get_angle_between_edges(edge1, edge2, radians=True):
    if not all([edge1.calc_length(), edge2.calc_length()]):

        angle = pi

    else:
        centervert = None

        for vert in edge1.verts:
            if vert in edge2.verts:
                centervert = vert

        if centervert:
            vector1 = centervert.co - edge1.other_vert(centervert).co
            vector2 = centervert.co - edge2.other_vert(centervert).co
        else:
            vector1 = edge1.verts[0].co - edge1.verts[1].co
            vector2 = edge2.verts[0].co - edge2.verts[1].co

        angle = vector1.angle(vector2)

    return angle if radians else degrees(vector1.angle(vector2))

def get_distance_between_points(point1, point2):
    return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)

def get_distance_between_verts(vert1, vert2, getvectorlength=True):
    if getvectorlength:
        vector = vert1.co - vert2.co
        return vector.length
    else:
        return get_distance_between_points(vert1.co, vert2.co)

def get_edge_normal(edge):
    return average_normals([f.normal for f in edge.link_faces])

def check_angle(edges):
    angle = get_angle_between_edges(edges[0], edges[1], radians=False)
    return angle

def check_ngon(edge):
    for f in edge.link_faces:
        if len(f.verts) > 4:
            return f
    return False

def average_locations(locationslist):
    avg = Vector()

    for n in locationslist:
        avg += n

    return avg / len(locationslist)

def average_normals(normalslist):
    avg = Vector()

    for n in normalslist:
        avg += n

    return avg.normalized()

def create_rotation_matrix_from_normal(obj, normal, location=Vector((0, 0, 0)), debug=False):
    objup = Vector((0, 0, 1)) @ obj.matrix_world.inverted_safe()

    dot = normal.dot(objup)
    if abs(round(dot, 6)) == 1:
        objup = Vector((1, 0, 0)) @ obj.matrix_world.inverted_safe()

    tangent = objup.cross(normal)
    binormal = tangent.cross(-normal)

    if debug:
        objloc, _, _ = obj.matrix_world.decompose()
        draw_vector(objup, objloc, color=(1, 0, 0))

        draw_vector(normal, location)
        draw_vector(tangent, location, color=(0, 1, 0))
        draw_vector(binormal, location, color=(0, 0, 1))

    rotmx = Matrix()
    rotmx[0].xyz = tangent.normalized()
    rotmx[1].xyz = binormal.normalized()
    rotmx[2].xyz = normal.normalized()

    return rotmx.transposed()

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

def create_circle_coords(radius, count, tilt, calc_normals=False, debug=False):
    coords = []

    rotmx = Matrix.Rotation(radians(tilt), 4, 'Z')

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

def resample_coords(coords, cyclic, segments=None, shift=0, mx=None, debug=False):
    if not segments:
        segments = len(coords) - 1

    if len(coords) < 2:
        return coords

    if not cyclic and shift != 0:  # not PEP but it shows that we want shift = 0
        print('Not shifting because this is not a cyclic vert chain')
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

        extra = desired_length - cumulative_lengths[j- 1]

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

def get_irregular_circle_center(verts, mx=None, debug=False):
    if len(verts) >= 3:
        v1 = choice(verts)

        diameter = max([(v.co - v1.co).length for v in verts if v != v1])

        d = 0
        while d < diameter * 0.6:
            v2 = choice([v for v in verts if v != v1])
            d = (v2.co - v1.co).length

        d = 0
        d2 = 0
        while d < diameter * 0.6 or d2 < diameter * 0.6:
            v3 = choice([v for v in verts if v not in [v1, v2]])
            d = (v3.co - v1.co).length
            d2 = (v3.co - v2.co).length

        v2v1 = v1.co - v2.co
        v3v1 = v1.co - v3.co

        if debug and mx:
            draw_line([v1.co, v2.co], mx=mx, modal=False)
            draw_line([v1.co, v3.co], mx=mx, modal=False)

        normal = v2v1.cross(v3v1).normalized()

        if debug and mx:
            draw_vector(normal, origin=v1.co, mx=mx, color=blue, modal=False)

        v2v1_perp = v2v1.cross(normal).normalized()
        v3v1_perp = v3v1.cross(-normal).normalized()

        v2v1_mid = v2.co + v2v1 * 0.5
        v3v1_mid = v3.co + v3v1 * 0.5

        if debug and mx:
            draw_vector(v2v1_perp, origin=v2v1_mid, mx=mx, color=red, modal=False)
            draw_vector(v3v1_perp, origin=v3v1_mid, mx=mx, color=red, modal=False)

        i = geometry.intersect_line_line(v2v1_mid, v2v1_mid + v2v1_perp, v3v1_mid, v3v1_mid + v3v1_perp)

        if i:
            if debug and mx:
                draw_point(i[0], mx=mx, color=red, modal=False)

            return i[0], normal
    return None, None

def average_normals(normalslist):
    avg = Vector()

    for n in normalslist:
        avg += n

    return avg.normalized()