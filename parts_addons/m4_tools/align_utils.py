from time import time

import bpy
import rna_keymap_ui
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
from mathutils import Matrix, Vector

from ... import get_prefs


def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)

        if isinstance(message, list):
            print(" »", ", ".join(message))
        else:
            print(" »", message)


def get_right_and_up_axes(context, mx):
    r3d = context.space_data.region_3d

    view_right = r3d.view_rotation @ Vector((1, 0, 0))
    view_up = r3d.view_rotation @ Vector((0, 1, 0))

    axes_right = []
    axes_up = []

    for idx, axis in enumerate([Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]):
        dot = view_right.dot(mx.to_3x3() @ axis)
        axes_right.append((dot, idx))

        dot = view_up.dot(mx.to_3x3() @ axis)
        axes_up.append((dot, idx))

    axis_right = max(axes_right, key=lambda x: abs(x[0]))
    axis_up = max(axes_up, key=lambda x: abs(x[0]))

    flip_right = True if axis_right[0] < 0 else False
    flip_up = True if axis_up[0] < 0 else False

    return axis_right[1], axis_up[1], flip_right, flip_up


def get_selected_vert_sequences(verts, ensure_seq_len=False, debug=False):
    sequences = []

    noncyclicstartverts = [v for v in verts if len([e for e in v.link_edges if e.select]) == 1]

    if noncyclicstartverts:
        v = noncyclicstartverts[0]

    else:
        v = verts[0]

    seq = []

    while verts:
        seq.append(v)

        if v not in verts:
            break

        else:
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

    if ensure_seq_len:
        seqs = []

        for seq, cyclic in sequences:
            if len(seq) > 1:
                seqs.append((seq, cyclic))

        sequences = seqs

    if debug:
        for seq, cyclic in sequences:
            print(cyclic, [v.index for v in seq])

    return sequences


def get_selection_islands(faces, debug=False):
    if debug:
        print("selected:", [f.index for f in faces])

    face_islands = []

    while faces:
        island = [faces[0]]
        foundmore = [faces[0]]

        if debug:
            print("island:", [f.index for f in island])
            print("foundmore:", [f.index for f in foundmore])

        while foundmore:
            for e in foundmore[0].edges:
                bf = [f for f in e.link_faces if f.select and f not in island]
                if bf:
                    island.append(bf[0])
                    foundmore.append(bf[0])

            if debug:
                print("popping", foundmore[0].index)

            foundmore.pop(0)

        face_islands.append(island)

        for f in island:
            faces.remove(f)

    if debug:
        print()
        for idx, island in enumerate(face_islands):
            print("island:", idx)
            print(" » ", ", ".join([str(f.index) for f in island]))

    islands = []

    for fi in face_islands:
        vi = set()
        ei = set()

        for f in fi:
            vi.update(f.verts)
            ei.update(f.edges)

        islands.append((list(vi), list(ei), fi))

    return sorted(islands, key=lambda x: len(x[2]), reverse=True)


def get_center_between_points(point1, point2, center=0.5):
    return point1 + (point2 - point1) * center


def get_center_between_verts(vert1, vert2, center=0.5):
    return get_center_between_points(vert1.co, vert2.co, center=center)


def create_selection_bbox(coords):
    minx = min(coords, key=lambda x: x[0])
    maxx = max(coords, key=lambda x: x[0])

    miny = min(coords, key=lambda x: x[1])
    maxy = max(coords, key=lambda x: x[1])

    minz = min(coords, key=lambda x: x[2])
    maxz = max(coords, key=lambda x: x[2])

    midx = get_center_between_points(minx, maxx)
    midy = get_center_between_points(miny, maxy)
    midz = get_center_between_points(minz, maxz)

    mid = Vector((midx[0], midy[1], midz[2]))

    bbox = [
        Vector((minx.x, miny.y, minz.z)),
        Vector((maxx.x, miny.y, minz.z)),
        Vector((maxx.x, maxy.y, minz.z)),
        Vector((minx.x, maxy.y, minz.z)),
        Vector((minx.x, miny.y, maxz.z)),
        Vector((maxx.x, miny.y, maxz.z)),
        Vector((maxx.x, maxy.y, maxz.z)),
        Vector((minx.x, maxy.y, maxz.z)),
    ]

    return bbox, mid


def get_loc_matrix(location):
    return Matrix.Translation(location)


def create_rotation_difference_matrix(v1, v2):
    q = v1.rotation_difference(v2)
    return q.to_matrix().to_4x4()
