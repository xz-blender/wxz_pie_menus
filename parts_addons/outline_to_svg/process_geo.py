from typing import List, Tuple
from mathutils import Matrix, Vector

try:
    from shapely.geometry import Point, Polygon, MultiPolygon
    from shapely.ops import unary_union
except ImportError as e:
    print(e)
    pass

def poly_union(polygons: List[Polygon], buffer: float) -> List[Polygon]:
    """ Perform union on list of polygons with buffer for cleaning incorrect alignments """
    # Buffer to increase overlay
    polygons = [poly.buffer(buffer) for poly in polygons]

    # Perform merge
    merged = unary_union(polygons)

    # Account for multipolygon output
    if isinstance(merged, MultiPolygon):
        polygons = [g for g in merged.geoms]
    else:
        polygons = [merged]

    # Remove buffer
    polygons = [poly.buffer(-buffer) for poly in polygons]

    return polygons


def get_bbox(polygons: List[Polygon]) -> Tuple[Vector, Vector]:
    convex_hulls = MultiPolygon([p.convex_hull for p in polygons])
    return convex_hulls.bounds


def translate_face_set(face_set: List[List[Vector]], xy):
    """ 2d translation of faces """
    translated = []
    for face in face_set:
        translated.append([v + xy for v in face])

    return translated


def flip_faces(face_set: List[List[Vector]], origin: Vector):
    translated = []
    scaler = Matrix.Scale(-1, 3, Vector((0, 1, 0)))

    for face in face_set:
        translated.append([scaler @ v for v in face])

    return translated
