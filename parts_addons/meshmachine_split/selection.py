from .utils import *
from .ui import *
from .tools import *
def get_2_rails_from_chamfer(bm, mg, verts, faces, reverse=False, debug=False):
    length_mode = False

    ngons = [f for f in faces if len(f.verts) > 4]
    tris = [f for f in faces if len(f.verts) < 4]

    if ngons:
        popup_message("Selection includes ngons, aborting", title="Illegal Selection")
        return
    elif tris:
        popup_message("Selection includes tris, aborting", title="Illegal Selection")
        return

    if len(faces) == 0:
        popup_message("Selection does not include faces, aborting", title="Illegal Selection")
        return
    elif len(faces) == 1:
        if debug:
            print("Selection is a single quad, determining direction via edge length")
        length_mode = True
    else:
        if debug:
            print("Determining direction via vert hops")

    corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

    if len(corners) == 0:
        cyclic = True

        f = faces[0]
        f.select_set(False)

        if debug:
            print("Selection is cyclic")
            print("cyclic deselect of face:", f.index)

        mg = build_mesh_graph(bm)
        corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

        if not corners:
            popup_message("Selection is not a chamfer, aborting", title="Illegal Selection")
            return
    else:
        cyclic = False

    if debug:
        print("corner verts:", [c.index for c in corners])

    c1 = corners[0]
    corners.remove(c1)

    c2_candidates = [c for c in corners if c.index in [idx for idx, vselect, eselect in mg[c1.index] if eselect]]

    if not c2_candidates:
        popup_message("Selection is not a chamfer, aborting", title="Illegal Selection")
        return
    elif length_mode:
        c2 = c2_candidates[0]
        c3 = c2_candidates[1]

        corners.remove(c2)
        corners.remove(c3)

        c4 = corners[-1]

        edgeA1 = bm.edges.get([c1, c3])
        edgeA2 = bm.edges.get([c2, c4])

        edgeB1 = bm.edges.get([c1, c2])
        edgeB2 = bm.edges.get([c3, c4])

        averageA = (edgeA1.calc_length() + edgeA2.calc_length()) / 2
        averageB = (edgeB1.calc_length() + edgeB2.calc_length()) / 2

        if averageA >= averageB:
            rail1 = [c1, c3]
            rail2 = [c2, c4]
        else:
            rail1 = [c1, c2]
            rail2 = [c3, c4]

        if reverse:
            rail1, rail2 = [rail1[0], rail2[0]], [rail1[1], rail2[1]]
    else:
        c2 = c2_candidates[0]
        corners.remove(c2)

        rail1 = [c1]
        rail2 = [c2]

        if debug:
            print("rail1 start:", rail1[-1].index)
            print("rail2 start:", rail2[-1].index)

        not_yet_walked = [f for f in faces]
        while not_yet_walked:
            v1 = rail1[-1]
            v2 = rail2[-1]
            sweep = bm.edges.get([v1, v2])
            if debug:
                print("sweep:", sweep.index)

            current_face = [f for f in sweep.link_faces if f.select and f in not_yet_walked]

            if current_face:
                cf = current_face[0]
                if debug:
                    print("current face:", cf.index)
                not_yet_walked.remove(cf)

                next_verts = [v for v in cf.verts if v not in rail1 + rail2]
                if debug:
                    print("next verts:", [v.index for v in next_verts])

                rail1_next_vert = [e.other_vert(v1) for e in v1.link_edges if e.other_vert(v1) in next_verts][0]
                if debug:
                    print("next vert 1:", rail1_next_vert.index)

                rail2_next_vert = [e.other_vert(v2) for e in v2.link_edges if e.other_vert(v2) in next_verts][0]
                if debug:
                    print("next vert 2:", rail2_next_vert.index)
                    print()

                rail1.append(rail1_next_vert)
                rail2.append(rail2_next_vert)
            else:
                break

        if cyclic:
            f.select_set(True)

    if debug:
        rail1ids = [str(v.index) for v in rail1]
        rail2ids = [str(v.index) for v in rail2]
        print(" • ".join(rail1ids))
        print(" • ".join(rail2ids))

    return (rail1, rail2), cyclic

def get_sweeps_from_fillet(bm, mg, verts, faces, debug=False):
    ngons = [f for f in faces if len(f.verts) > 4]
    tris = [f for f in faces if len(f.verts) < 4]

    if ngons:
        popup_message("Selection includes ngons, aborting", title="Illegal Selection")
        return
    elif tris:
        popup_message("Selection includes tris, aborting", title="Illegal Selection")
        return

    if len(faces) < 2:
        popup_message("Selection has less than 2 faces, aborting", title="Illegal Selection")
        return
    elif len(verts) < 6:
        popup_message("Selection has less than 6 verts, aborting", title="Illegal Selection")
        return
    else:
        if debug:
            print("Determining rail direction via vert hops")

    corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

    if len(corners) == 0:  # < 0 ?
        popup_message("Cyclic selections are not supported, aborting", title="Illegal Selection")
        return

    c1 = corners[0]
    corners.remove(c1)

    c2 = [c for c in corners if c.index in [idx for idx, _, eselect in mg[c1.index] if eselect]]

    if not c2:
        popup_message("Selection is not a poly strip, aborting", title="Illegal Selection")
        return
    else:
        c2 = c2[0]
        corners.remove(c2)

        rail1 = [c1]
        rail2 = [c2]

        sweeps = [(c1, c2)]

        if debug:
            print("rail1 start:", rail1[-1].index)
            print("rail2 start:", rail2[-1].index)

        not_yet_walked = [f for f in faces]
        while not_yet_walked:
            v1 = rail1[-1]
            v2 = rail2[-1]
            sweep = bm.edges.get([v1, v2])

            if debug:
                print("sweep:", sweep.index)

            current_face = [f for f in sweep.link_faces if f.select and f in not_yet_walked]

            if current_face:
                cf = current_face[0]
                if debug:
                    print("current face:", cf.index)
                not_yet_walked.remove(cf)

                next_verts = [v for v in cf.verts if v not in rail1 + rail2]
                if debug:
                    print("next verts:", [v.index for v in next_verts])

                rail1_next_vert = [e.other_vert(v1) for e in v1.link_edges if e.other_vert(v1) in next_verts][0]
                if debug:
                    print("next vert 1:", rail1_next_vert.index)

                rail2_next_vert = [e.other_vert(v2) for e in v2.link_edges if e.other_vert(v2) in next_verts][0]
                if debug:
                    print("next vert 2:", rail2_next_vert.index)
                    print()

                rail1.append(rail1_next_vert)
                rail2.append(rail2_next_vert)
                sweeps.append((rail1_next_vert, rail2_next_vert))
            else:
                break

    if debug:
        print("rails:")
        rail1ids = [str(v.index) for v in rail1]
        rail2ids = [str(v.index) for v in rail2]
        print(" • ".join(rail1ids))
        print(" • ".join(rail2ids))

        print()
        print("sweeps:")
        sweepids = [(str(v1.index), str(v2.index)) for v1, v2 in sweeps]
        print(sweepids)

    return sweeps

def get_vert_sequence(bm, mg, verts, debug=False):
    seq = []
    if len(verts) > 3:
        ends = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[bm.verts[idx].index] if eselect]) == 1]

        if not ends:  # cyclic selection
            popup_message("Selection is cyclic, aborting", title="Illegal Selection")
            return
        else:
            end1 = ends[0]
            seq.append(end1)
            ends.remove(end1)

            while ends:
                nextvs = [bm.verts[idx] for idx, vselect, eselect in mg[seq[-1].index] if vselect and eselect and bm.verts[idx] not in seq]
                if nextvs:
                    nextv = nextvs[0]

                    seq.append(nextv)
                    if nextv in ends:
                        ends.remove(nextv)
                else:
                    popup_message("Selection need to be at least 3 loop edges, aborting", title="Illegal Selection")
                    return

    if debug:
        print(" • ".join([str(v.index) for v in seq]))

    return seq

def propagate_edge_loops(bm, seq, propagate, width, width2, tension, tension2, fade=0, merge=False, merge_verts=[], widthlinked=False, tensionlinked=False, advanced=False, debug=False):
    for p in range(propagate):
        if debug:
            print("propagation:", p)

        new_seq = []

        if p == 0:
            e1 = bm.edges.get([seq[0], seq[1]])
            bmloop_start = [l for l in e1.link_loops if len(l.face.verts) == 4][0]
            flipped = False

            if bmloop_start.vert != seq[0]:
                if debug:
                    print("Taking start edge from the end of the sequence!")
                flipped = True
                e1 = bm.edges.get([seq[-1], seq[-2]])
                bmloop_start = [l for l in e1.link_loops if len(l.face.verts) == 4][0]

        else:
            bmloop_start = bmloop_start.link_loop_next.link_loop_next.link_loop_radial_next

        if debug:
            for e in bm.edges:
                e.select = False
            e1.select = True
            print("first edge of old sequence:", e1.index)

        bmloop = bmloop_start.link_loop_next.link_loop_next.link_loop_radial_next

        v = bmloop.vert
        new_seq.append(v)

        if debug:
            v.select = True
            print("vertex:", v.index)

        for i in range(len(seq) - 1):
            bmloop = bmloop.link_loop_next.link_loop_radial_next.link_loop_next
            v = bmloop.vert
            new_seq.append(v)

            if debug:
                v.select = True

        if debug:
            print(" • ".join([str(v.index) for v in seq]))

        fade_propagate = (p + 1) / (propagate + 1) * fade
        if debug:
            print("fade_propagate: ", fade_propagate)

        align_vert_sequence_to_spline(bm, new_seq, width, width2, tension, tension2, fade_propagate, merge, merge_verts, flipped, widthlinked, tensionlinked, advanced, debug=debug)

        seq = new_seq

def get_3_sides_from_tri_corner(bm, mg, verts, edges, faces, turn, debug=False):
    if len(faces) == 0:
        popup_message("Selection does not include faces, aborting", title="Illegal Selection")
        return
    elif len(verts) < 3:
        popup_message("Selection has less than 3 verts selected, aborting", title="Illegal Selection")
        return

    corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

    if len(corners) != 3:
        popup_message("Selection does not have 3 corners, it's not a triangular corner, aborting", title="Illegal Selection")
        return

    if turn == "2":
        first = corners.pop(0)
        corners.append(first)
    elif turn == "3":
        third = corners.pop(2)
        corners.insert(0, third)

    sides = [[corners[0]], [corners[1]], [corners[2]]]

    if debug:
        print("sides:", sides)

    for idx, c in enumerate(corners):
        if debug:
            print("corner:", c.index)

        loop = [l for l in c.link_loops if l.face.select][0]

        v = c
        side = [side for side in sides if side[0] == v][0]
        while loop.edge.other_vert(v) not in corners:
            side.append(loop.edge.other_vert(v))

            loop = loop.link_loop_next.link_loop_radial_next.link_loop_next
            v = loop.vert

            if debug:
                print("edge:", loop.edge.index, "vert:", v.index)

        if idx == 0:
            if loop.edge.other_vert(v) != sides[1][0]:
                if debug:
                    print("switched side 1 and 2")
                second = sides.pop(1)
                sides.append(second)

    if debug:
        for side in sides:
            print(" • ".join([str(v.index) for v in side]))

    return sides, corners

def get_2_rails_from_tri_corner(bm, faces, sides, width, debug=False):
    c1 = sides[0][0]

    c1_loop = [l for l in c1.link_loops if l.face.select][0]

    edge_A = c1_loop.link_loop_radial_next.link_loop_next.edge

    edge_B = c1_loop.link_loop_prev.link_loop_radial_prev.link_loop_prev.edge

    edge_A_other_v = edge_A.other_vert(c1)
    edge_B_other_v = edge_B.other_vert(c1)

    c1_A = bm.verts.new()
    c1_A.co = c1.co

    c1_B = bm.verts.new()
    c1_B.co = c1.co

    bm.verts.index_update()

    bm.edges.new([c1_A, edge_A_other_v])
    bm.edges.new([c1_B, edge_B_other_v])
    bm.edges.index_update()

    rail1 = [c1_A]
    rail2 = [c1_B]

    for v in sides[0][1:]:
        rail1.append(v)

    for v in reversed(sides[2][1:]):
        rail2.append(v)

    if debug:
        for v in rail1:
            v.select = True

        for v in rail2:
            v.select = True

    if debug:
        print("\nrails:")
        rail1ids = [str(v.index) for v in rail1]
        rail2ids = [str(v.index) for v in rail2]
        print(" • ".join(rail1ids))
        print(" • ".join(rail2ids))

    return (rail1, rail2), (edge_A_other_v, edge_B_other_v)

def get_side(verts, edges, startvert, startloop, endvert=None, flushedges=[], reverse=False, offset=None, debug=False):
    vert = startvert
    loop = startloop

    edges_travelled = [loop.edge]

    startedge = []
    if endvert:
        if startloop.link_loop_prev.edge not in edges:
            startedge.append(startloop.link_loop_prev.edge)

    d = {"vert": vert, "seledge": loop.edge, "edges": startedge, "faces": [loop.face]}
    side = [d]

    while True:
        if vert == endvert:
            d["seledge"] = edges_travelled[-1]
            break

        loop = loop.link_loop_next

        vert = loop.vert
        edge = loop.edge
        face = loop.face

        if not edge.is_manifold:
            return

        if edge in edges_travelled:
            break

        if vert in verts:
            if vert in [s["vert"] for s in side]:
                append = False
                d = [s for s in side if s["vert"] == vert][0]

            else:
                append = True
                d = {}
                d["vert"] = vert
                d["edges"] = []
                d["faces"] = []

            if edge in edges:
                edges_travelled.append(edge)
                d["seledge"] = edge
            else:
                d["edges"].append(edge)

            d["faces"].append(face)

            if append:
                side.append(d)

            if edge in flushedges:
                loop = loop.link_loop_radial_next

        else:
            loop = loop.link_loop_prev.link_loop_radial_next

    if reverse:
        side.reverse()

    if offset:
        side = side[-offset:] + side[:-offset]

    if debug:
        print()
        for d in side:
            print("vert:", d["vert"].index)
            print(" • seledge", d["seledge"].index)
            print(" • edges:", [e.index for e in d["edges"]])
            print(" • faces:", [f.index for f in d["faces"]])

    return side

def get_sides(bm, verts, edges, debug=False):
    if any([not e.is_manifold for e in edges]):
        errmsg = "Non-manifold edges are part of the selection. Failed to determine sides of the selection."
        errtitle = "Non-Manifold Geometry"
        return None, None, None, (errmsg, errtitle)

    bm.select_flush(True)
    flushedges = [e for e in bm.edges if e.select and e not in edges]

    for e in flushedges:
        e.select = False

    bm.select_flush(False)

    ends = []
    for v in verts:
        if sum([e.select for e in v.link_edges]) == 1:
            ends.append(v)

    endslen = len(ends)

    cyclic = False

    if endslen == 0:
        if debug:
            print("Cyclic edge loop selection")

        cyclic = True

        loops = [l for l in verts[0].link_loops if l.edge in edges]

        sideA = get_side(verts, edges, verts[0], loops[0], flushedges=flushedges, debug=debug)
        sideB = get_side(verts, edges, verts[0], loops[1], flushedges=flushedges, reverse=True, offset=1, debug=debug)

        if sideA and sideB:
            return sideA, sideB, cyclic, None
        else:
            errmsg = "There's a non-manifold edge closeby, failed to determine sides of the selection."
            errtitle = "Non-Manifold Geometry"

            return None, None, None, (errmsg, errtitle)

    elif endslen == 2:
        if debug:
            print("Non-Cyclic edge loop selection")

        loops = [l for v in ends for l in v.link_loops if l.edge in edges]

        sideA = get_side(verts, edges, ends[0], loops[0], endvert=ends[1], flushedges=flushedges, debug=debug)
        sideB = get_side(verts, edges, ends[1], loops[1], endvert=ends[0], flushedges=flushedges, reverse=True, debug=debug)

        if sideA and sideB:
            return sideA, sideB, cyclic, None
        else:
            errmsg = "There's a non-manifold edge closeby, failed to determine sides of the selection."
            errtitle = "Non-Manifold Geometry"

            return None, None, None, (errmsg, errtitle)

    else:
        if debug:
            print("Invalid selection.")

        errmsg = "Only single-island cyclic or non-cyclic edge loop selections are supproted."
        errtitle = "Illegal Selection"

        return None, None, None, (errmsg, errtitle)
