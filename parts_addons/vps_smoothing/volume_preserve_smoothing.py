import time
from math import pow

import bmesh
import bpy
import numpy as np
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from mathutils import Vector, kdtree


def three_d_bincount_add(out, e_k, weights):
    out[:, 0] += np.bincount(e_k, weights[:, 0], out.shape[0])
    out[:, 1] += np.bincount(e_k, weights[:, 1], out.shape[0])
    out[:, 2] += np.bincount(e_k, weights[:, 2], out.shape[0])


def new_bincount(out, e_k, weights=None):
    out += np.bincount(e_k, weights, out.shape[0])


def get_mirrored_axis(source):
    x = y = z = False
    merge_threshold = 0.001
    use_m = bpy.context.object.data
    x, y, z = use_m.use_mirror_x, use_m.use_mirror_y, use_m.use_mirror_z
    if not (x and y and z):
        for mod in source.modifiers:
            if mod.type == "MIRROR" and mod.mirror_object == None:  #  and mod.show_viewport use first visible
                x = mod.use_axis[0] or x
                y = mod.use_axis[1] or y
                z = mod.use_axis[2] or z
                merge_threshold = mod.merge_threshold
    mirror_axes = []
    if x:
        mirror_axes.append(0)
    if y:
        mirror_axes.append(1)
    if z:
        mirror_axes.append(1)
    return mirror_axes, merge_threshold


def get_mirrored_verts(mesh):
    kd = kdtree.KDTree(len(mesh.vertices))
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)
    kd.balance()

    mirror_map = []
    for vert in mesh.vertices:
        co, mirror_vert_index, dist = kd.find(Vector((-vert.co[0], vert.co[1], vert.co[2])))
        if mirror_vert_index == vert.index:
            mirror_map.append(-1)
        elif dist < 0.0001:  # delta
            mirror_map.append(mirror_vert_index)
        else:
            mirror_map.append(-2)
    return tuple(mirror_map)


def close_bmesh(context, bm, source):
    bm.normal_update()
    if context.object.mode == "EDIT":
        bmesh.update_edit_mesh(source, loop_triangles=False, destructive=False)
    else:
        bm.to_mesh(source)
        bm.free()
        # source.update()


def get_bmesh(context, mesh):
    bm = bmesh.new()
    if context.active_object.mode == "OBJECT":
        bm.from_mesh(mesh)
    elif context.active_object.mode == "EDIT":
        bm = bmesh.from_edit_mesh(mesh)
    return bm


class CommonSmoothMethods:
    # @cache    # gives infinite boost
    def numpy_smooth_init(self, context, method="LC", from_brush=False, tension="UNIFORM"):

        beta = 1 - self.smooth_amount * (
            0.6 - (self.iteration_amount / 20 * 0.1)
        )  # map smooth ammount from <0,1> to beta <0,7; 1>

        mirror_axes, delta = get_mirrored_axis(context.active_object)
        bm = get_bmesh(context, context.active_object.data)
        # source = context.active_object.data
        # mode = context.active_object.mode
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.index_update()
        bm.edges.index_update()

        if from_brush and not self.only_selected:  # smooth all verts

            sel_v = tuple(v for v in bm.verts if not v.hide)
            if len(sel_v) == 0:
                self.report(
                    {"ERROR"},
                    "No vertices were selected!\nDisable 'Only Selected' option (or select vertices).\nCancelling",
                )
                return "CANCELLED"
            sel_adj_verts_ids = [v.index for v in sel_v]
            sel_adj_verts_ids.extend(
                [e.other_vert(s_vert).index for s_vert in sel_v for e in s_vert.link_edges if e.hide]
            )
            sel_e = tuple(e for e in bm.edges if not e.hide)
            sel_adj_verts_ids_unique = np.unique(sel_adj_verts_ids)  # remove duplis
            sel_verts = np.array(
                tuple(not bm.verts[old_index].hide for old_index in sel_adj_verts_ids_unique), dtype="?"
            )  # bool
        else:  # N: automatically hidden mesh is assumed to be non selected.
            sel_v = tuple(v for v in bm.verts if v.select)
            if len(sel_v) == 0:
                self.report(
                    {"ERROR"},
                    "No vertices were selected!\nDisable 'Only Selected' option (or select vertices).\nCancelling",
                )
                return "CANCELLED"
            sel_adj_verts_ids = [v.index for v in sel_v]
            sel_adj_verts_ids.extend(
                [e.other_vert(s_vert).index for s_vert in sel_v for e in s_vert.link_edges if not e.select]
            )
            sel_e = tuple(e for e in bm.edges if e.select)
            sel_adj_verts_ids_unique = np.unique(sel_adj_verts_ids)  # remove duplis
            sel_verts = np.array(tuple(bm.verts[old_index].select for old_index in sel_adj_verts_ids_unique), dtype="?")

        o_normal = np.array([bm.verts[old_index].normal for old_index in sel_adj_verts_ids_unique])
        o_co = np.array([bm.verts[old_index].co for old_index in sel_adj_verts_ids_unique])

        on_axis_vmask = {}
        for axis_id in mirror_axes:  # adjust normals for center verts
            on_axis_vmask[axis_id] = np.abs(o_co[:, axis_id]) < delta  # True for verts on mirror axis
            o_normal[on_axis_vmask[axis_id], axis_id] = 0

            # normalize on axis normals
            normals_mag = np.sqrt(
                np.einsum("...i,...i", o_normal[on_axis_vmask[axis_id]], o_normal[on_axis_vmask[axis_id]])
            )
            o_normal[on_axis_vmask[axis_id]] /= normals_mag[:, None]  # total_normal.normalize()

        vert_count = sel_adj_verts_ids_unique.shape[0]
        orig_to_new_idx = dict(zip(sel_adj_verts_ids_unique, range(sel_adj_verts_ids_unique.shape[0])))

        edge_keys = []
        border_vert_ek_mask = (
            []
        )  # list of (e.v1, e.v2)   - 1 everywere where vert will pull neibors.  Only 0 for border verts on non border edges
        sharp_edges = []
        sharp_verts = []

        for edge in sel_e:  # N: file border_vert_ek_mask, etc.
            v1_id = orig_to_new_idx[edge.verts[0].index]
            v2_id = orig_to_new_idx[edge.verts[1].index]
            if edge.is_boundary:  # boundary edges have  100% influence for  adjacent verts
                border_vert_ek_mask.append([True, True])
            else:  # find all inner mesh edges. And partially weights edges connected to border verts
                v1_is_on_axis = False  # does v1 belongs to center mirror of any axis?
                v2_is_on_axis = False  # does vs belongs to center mirror  of any axis?

                # XXX: does it event work for y, z  mirror symmetry?
                for (
                    axis_id,
                    mirror_mask,
                ) in on_axis_vmask.items():  # we dont care about which axis it lays on (x, y or z)
                    v1_is_on_axis = True if mirror_mask[v1_id] else v1_is_on_axis
                    v2_is_on_axis = True if mirror_mask[v2_id] else v2_is_on_axis

                if (
                    v1_is_on_axis and v2_is_on_axis
                ):  # special condition - else these 2verts would always pull - but we do not want to pull on axis border verts though
                    border_vert_ek_mask.append([not edge.verts[0].is_boundary, not edge.verts[1].is_boundary])
                else:  # vert pulls if non_boundary or  (boundary but on axis)
                    border_vert_ek_mask.append(
                        [not edge.verts[0].is_boundary or v1_is_on_axis, not edge.verts[1].is_boundary or v2_is_on_axis]
                    )

                # DONE: need to add mirror_axis touching edge second time
                if (
                    v1_is_on_axis ^ v2_is_on_axis
                ):  # add non border edges, when one of (e.v1 xor e.v2) is on mirror axis.
                    border_vert_ek_mask.append(
                        [v1_is_on_axis, v2_is_on_axis]
                    )  # add fake edge for negative mirror side (actually can be same edge 2x. cos we ignore x component (x=0))
                    sharp_edges.append(not edge.smooth)  # add same twice to sharp_edges
                    edge_keys.append([v1_id, v2_id])

            edge_keys.append([v1_id, v2_id])
            sharp_edges.append(not edge.smooth)
            if not edge.smooth:
                sharp_verts.append((orig_to_new_idx[edge.verts[0].index], orig_to_new_idx[edge.verts[1].index]))

        sel_border_verts = [False] * len(sel_adj_verts_ids_unique)
        for s_vert in sel_v:  # N: get non selected edges, but connected to sel_v - as additional smoothing inluencers
            # if drawing by brush (old was not_sel_edges_adj = [] - cos no adjacent non selected edges when all is selected)
            # if smoothing whole mesh then pick hidden edges if any exist
            not_sel_edges_adj = (
                [e for e in s_vert.link_edges if e.hide]
                if from_brush and not self.only_selected
                else [e for e in s_vert.link_edges if not e.select]
            )
            if self.freeze_border and ((from_brush and self.only_selected) or not from_brush):
                not_sel_faces_adj = [f for f in s_vert.link_faces if not f.select]
                sel_border_verts[orig_to_new_idx[s_vert.index]] = len(not_sel_faces_adj) != 0

            for nsel_e in not_sel_edges_adj:
                edge_keys.append([orig_to_new_idx[nsel_e.verts[0].index], orig_to_new_idx[nsel_e.verts[1].index]])
                # border_vert_ek_mask.append( [not nsel_e.verts[0].is_boundary or nsel_e.is_boundary, not nsel_e.verts[1].is_boundary or nsel_e.is_boundary] )
                border_vert_ek_mask.append(
                    [
                        not nsel_e.verts[0].is_boundary or nsel_e.is_boundary,
                        not nsel_e.verts[1].is_boundary or nsel_e.is_boundary,
                    ]
                )

                sharp_edges.append(not nsel_e.smooth)
                if not nsel_e.smooth:
                    sharp_verts.extend(
                        [(orig_to_new_idx[nsel_e.verts[0].index], orig_to_new_idx[nsel_e.verts[1].index])]
                    )
        edge_keys = np.array(edge_keys)
        border_vert_ek_mask = np.array(border_vert_ek_mask)
        sharp_edges = np.array(sharp_edges)  # search for vert that are belonging to sharp edges
        sharp_verts = np.unique(sharp_verts)

        # sharp_edge_neighbors_mask = np.isin(edge_keys, list(sharp_verts)) #find sharp_verts in edge_keys, create mask
        sharp_edge_neighbors_mask = np.in1d(edge_keys, list(sharp_verts))  # find sharp_verts in edge_keys, create mask
        sharp_edge_neighbors_mask.shape = edge_keys.shape
        v_linked_edges = np.zeros(vert_count, dtype=np.float32)
        new_bincount(v_linked_edges, edge_keys[:, 1])
        new_bincount(v_linked_edges, edge_keys[:, 0])

        # count sharp connected edges to vert (==connected edges that are sharp)
        v_sharp_connections = np.zeros(vert_count, dtype=np.float32)
        new_bincount(v_sharp_connections, edge_keys[:, 1], sharp_edges)
        new_bincount(v_sharp_connections, edge_keys[:, 0], sharp_edges)

        freeze_verts = ~sel_verts
        freeze_verts |= v_linked_edges <= 2  # freeze verts with only two edges connected
        freeze_verts |= v_sharp_connections > 2  # freeze verts idf 3 or more sharp edges connected
        freeze_verts |= np.logical_and(
            v_sharp_connections == 2, v_linked_edges == 3
        )  # freeze verts with 3 edges if 2 are sharp
        freeze_verts |= v_sharp_connections == 1  # freeze verts if one one sharp edge is connected
        if self.freeze_border:
            freeze_verts |= np.array([bm.verts[old_index].is_boundary for old_index in sel_adj_verts_ids_unique])
            if (from_brush and self.only_selected) or not from_brush:
                freeze_verts |= np.array(sel_border_verts, "bool")

        # remove sharp edges, so we are left only with neighbors mask
        sharp_edge_neighbors_mask[sharp_edges] = [False, False]  # change double [True,True] to false
        slide_ek_mask = np.logical_and(border_vert_ek_mask, ~sharp_edge_neighbors_mask)

        p_co = np.copy(o_co)  # current new vertex position
        p_normal = np.copy(o_normal)
        b_co = np.zeros(shape=(vert_count, 3), dtype=np.float32)  # offset in iteration x, of vert i

        b_co_sum_neighbors = np.copy(b_co)  # offset in iteration x, of vert i

        v_boundary_mirrored_edges = np.zeros(vert_count, dtype=np.float32)
        # ~border_vert_ek_mask[:,0]+1 - ones everywhere, exept 0 where border vert and non border edge.
        new_bincount(
            v_boundary_mirrored_edges, edge_keys[:, 1], -1 * ~border_vert_ek_mask[:, 1] + 1
        )  # numb of vert connected to Vert[ek[0]]
        new_bincount(
            v_boundary_mirrored_edges, edge_keys[:, 0], -1 * ~border_vert_ek_mask[:, 0] + 1
        )  # numb of vert connected to Vert[ek[1]]

        sum_edge_len_per_vert = np.zeros(vert_count, dtype=np.float32)
        edge_weights = np.ones(edge_keys.shape[0])

        # when suming neibhors border_edge_m add additional weigths on boder verts
        border_edge_multiplier_1 = (
            ~border_vert_ek_mask[:, 1] + 1 + self.sharp_edge_weight * sharp_edge_neighbors_mask[:, 1]
        )
        border_edge_multiplier_2 = (
            ~border_vert_ek_mask[:, 0] + 1 + self.sharp_edge_weight * sharp_edge_neighbors_mask[:, 0]
        )
        if method == "INFlATE":
            v_connections = np.zeros(vert_count, dtype=np.float32)
            # sum edges that have vert X  and either end of edge (Va, Vb)
            # ~border_vert_ek_mask[:,0]+1 - ones everywhere, exept 2 where border vert and non border edge.
            new_bincount(
                v_connections,
                edge_keys[:, 1],
                (4 * ~border_vert_ek_mask[:, 1] + 1) + self.sharp_edge_weight * sharp_edge_neighbors_mask[:, 1],
            )
            new_bincount(
                v_connections,
                edge_keys[:, 0],
                (4 * ~border_vert_ek_mask[:, 0] + 1) + self.sharp_edge_weight * sharp_edge_neighbors_mask[:, 0],
            )

        #! ############
        def calc_lc_numpy_smooth():
            nonlocal p_co, b_co, edge_weights, b_co_sum_neighbors, sum_edge_len_per_vert
            for _ in range(self.iteration_amount):
                q_co = np.copy(p_co)  # prevoius iteration vert position
                p_co.fill(0)
                b_co.fill(0)
                b_co_sum_neighbors.fill(0)
                sum_edge_len_per_vert.fill(0)
                # for ek in edge_keys:
                diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
                if tension == "PROPORTIONAL":
                    edge_weights = np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)
                elif tension == "INVERSE":  # cos strength in inverse prop to len (maybe should be squared?)
                    edge_weights = 1 / np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)
                # calculate sum of adjacent edge weights to vert
                # np.add.at(sum_edge_len_per_vert, edge_keys[:,1],edge_weights*border_edge_multiplier_1 )  #numb of vert connected to Vert[ek[0]]
                # np.add.at(sum_edge_len_per_vert, edge_keys[:,0],edge_weights*border_edge_multiplier_2 )
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 1], edge_weights * border_edge_multiplier_1)
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 0], edge_weights * border_edge_multiplier_2)

                # p_co[ek[0]] += q_co[ek[1]] #sum all verts for ek[0] in data[ek_vert][0]
                # p_co[ek[1]] += q_co[ek[0]] #sum all verts for ek[1] in data[ek_vert][0]
                # np.add.at(p_co, edge_keys[:,1], -1*diff*edge_weights[:,None]*slide_ek_mask[:,1,None])
                # np.add.at(p_co, edge_keys[:,0], diff*edge_weights[:,None]*slide_ek_mask[:,0,None])
                three_d_bincount_add(
                    p_co, edge_keys[:, 1], -1 * diff * edge_weights[:, None] * slide_ek_mask[:, 1, None]
                )
                three_d_bincount_add(p_co, edge_keys[:, 0], diff * edge_weights[:, None] * slide_ek_mask[:, 0, None])

                # this vont work with proportional version
                # p_co = p_co / sum_edge_len_per_vert[:,None]  # /v_connections[:,None]   #new aver posision
                p_co = q_co + p_co / sum_edge_len_per_vert[:, None]  # new aver posision

                where_are_NaNs = np.isnan(
                    p_co
                )  # nan on corner case - where border and shapr edges meet vert. Just use old co there
                p_co[where_are_NaNs] = q_co[where_are_NaNs]

                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co
                b_co = p_co - (self.alpha * o_co + (1 - self.alpha) * q_co)  # difference

                # average of neibors vert differences
                three_d_bincount_add(
                    b_co_sum_neighbors, edge_keys[:, 1], b_co[edge_keys[:, 0]] * slide_ek_mask[:, 1, None]
                )
                three_d_bincount_add(
                    b_co_sum_neighbors, edge_keys[:, 0], b_co[edge_keys[:, 1]] * slide_ek_mask[:, 0, None]
                )

                # project p_normal* p_normal.dot(b_sum)  # u(u dot v)  - projection of v on u
                # TO prevent border vert slide ahead of loop (caused by sum_b being to big.., so reduce it by projecting on vert normal)
                # projected b_sum on normal  - helps also stabilize noise...
                b_sum_projected_to_normal = np.einsum(
                    "ij,i->ij",
                    o_normal,
                    np.einsum("ij,ij->i", o_normal, b_co_sum_neighbors / v_boundary_mirrored_edges[:, None]),
                )
                p_co = p_co - (beta * b_co + (1 - beta) * b_sum_projected_to_normal)
                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co

                for axis_id, mirror_mask in on_axis_vmask.items():
                    p_co[mirror_mask, axis_id] = 0

        def vol_numpy_smooth():
            nonlocal p_co, b_co, edge_weights, b_co_sum_neighbors, sum_edge_len_per_vert
            for _ in range(self.iteration_amount):
                # q_normal = np.copy(p_normal) #prevoius iteration vert position
                # p_normal.fill(0)
                q_co = np.copy(p_co)  # prevoius iteration vert position
                p_co.fill(0)
                b_co.fill(0)
                b_co_sum_neighbors.fill(0)
                sum_edge_len_per_vert.fill(0)
                # for ek in edge_keys:
                diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
                if tension == "PROPORTIONAL":
                    edge_weights = np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)
                elif tension == "INVERSE":  # cos strength in inverse prop to len (maybe should be squared?)
                    edge_weights = 1 / np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)
                # calculate sum of adjacent edge weights to vert
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 1], edge_weights * border_edge_multiplier_1)
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 0], edge_weights * border_edge_multiplier_2)

                # p_co[ek[0]] += q_co[ek[1]] #sum all verts for ek[0] in data[ek_vert][0]
                # p_co[ek[1]] += q_co[ek[0]] #sum all verts for ek[1] in data[ek_vert][0]
                three_d_bincount_add(
                    p_co, edge_keys[:, 1], -1 * diff * edge_weights[:, None] * slide_ek_mask[:, 1, None]
                )
                three_d_bincount_add(p_co, edge_keys[:, 0], diff * edge_weights[:, None] * slide_ek_mask[:, 0, None])

                # this vont work with proportional version
                # p_co = p_co / sum_edge_len_per_vert[:,None]  # /v_connections[:,None]   #new aver posision
                b_co = p_co / sum_edge_len_per_vert[:, None]  # new aver posision

                b_co[freeze_verts] = 0  # not selected ver - reset to original pos o_co

                three_d_bincount_add(
                    b_co_sum_neighbors, edge_keys[:, 1], b_co[edge_keys[:, 0]] * slide_ek_mask[:, 1, None]
                )
                three_d_bincount_add(
                    b_co_sum_neighbors, edge_keys[:, 0], b_co[edge_keys[:, 1]] * slide_ek_mask[:, 0, None]
                )

                # TO prevent border vert slide ahead of loop (caused by sum_b being to big.., so reduce it by projecting on vert normal)
                #  projected b_sum on normal
                b_sum_projected_to_normal = np.einsum(
                    "ij,i->ij",
                    o_normal,
                    np.einsum("ij,ij->i", o_normal, b_co_sum_neighbors / v_boundary_mirrored_edges[:, None]),
                )

                # new_co_dif = b_co - beta*b_co - (1-beta)*b_sum_projected_to_normal #   == line below
                new_co_dif = (1 - beta) * (b_co - b_sum_projected_to_normal)

                where_are_NaNs = np.isnan(
                    new_co_dif
                )  # nan on corner case - where border and shapr edges meet vert. Just use old co there
                new_co_dif[where_are_NaNs] = 0

                # average normals an normalize
                # np.add.at(p_normal, edge_keys[:,1], q_normal[edge_keys[:,1]])
                # np.add.at(p_normal, edge_keys[:,0], q_normal[edge_keys[:,0]])

                # p_normal_magnitudes = np.sqrt(np.einsum('...i,...i', p_normal, p_normal))
                # p_normal /= p_normal_magnitudes[:,None] # total_normal.normalize()

                # p_normal[i].dot(new_co_dif[i])
                diff_projected_on_normal_scalar_li = np.einsum(
                    "ij,ij->i", o_normal, new_co_dif
                )  # normal has to be normlized
                aver_normal_scalar = np.sum(diff_projected_on_normal_scalar_li[sel_verts]) / np.sum(sel_verts)

                # projected_diff_on_normal = total_normal* total_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                projected_diff_on_normal = np.einsum(
                    "ij,i->ij",
                    o_normal,
                    diff_projected_on_normal_scalar_li * (1 - self.normal_smooth)
                    + self.normal_smooth * aver_normal_scalar,
                )

                p_co = q_co + new_co_dif - projected_diff_on_normal * self.Inflate  # new aver normal
                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co

                for axis_id, mirror_mask in on_axis_vmask.items():
                    p_co[mirror_mask, axis_id] = 0
                    # q_normal[mirror_center_verts,0] = 0

        def inflate_numpy_smooth():
            nonlocal p_co, b_co, edge_weights, b_co_sum_neighbors, sum_edge_len_per_vert, p_normal, v_connections
            for _ in range(self.iteration_amount):
                q_normal = np.copy(p_normal)  # prevoius iteration vert position
                p_normal.fill(0)

                q_co = np.copy(p_co)  # prevoius iteration vert position
                p_co.fill(0)
                sum_edge_len_per_vert.fill(0)

                if tension == "PROPORTIONAL":
                    diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
                    # edge_weights = np.sqrt(np.maximum(np.einsum('ij,ij->i', diff, diff) ,0.0001))
                    edge_weights = np.maximum(np.einsum("ij,ij->i", diff, diff), 0.0001)
                elif tension == "INVERSE":  # cos strength in inverse prop to len (maybe should be squared?)
                    diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
                    edge_weights = 1 / np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)

                # calculate sum of adjacent edge weights to vert
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 0], edge_weights * slide_ek_mask[:, 0])
                new_bincount(sum_edge_len_per_vert, edge_keys[:, 1], edge_weights * slide_ek_mask[:, 1])
                # calculate sum of adjacent edge weights to vert

                # calc average position weighted...
                three_d_bincount_add(
                    p_co, edge_keys[:, 1], q_co[edge_keys[:, 0]] * edge_weights[:, None] * slide_ek_mask[:, 1, None]
                )
                three_d_bincount_add(
                    p_co, edge_keys[:, 0], q_co[edge_keys[:, 1]] * edge_weights[:, None] * slide_ek_mask[:, 0, None]
                )

                p_co = (
                    q_co + (p_co / sum_edge_len_per_vert[:, None] - q_co) / v_connections[:, None]
                )  # new aver posision
                where_are_NaNs = np.isnan(
                    p_co
                )  # nan on corner case - where border and shapr edges meet vert. Just use old co there
                p_co[where_are_NaNs] = q_co[where_are_NaNs]

                # average normals an normalize
                three_d_bincount_add(p_normal, edge_keys[:, 1], q_normal[edge_keys[:, 1]])
                three_d_bincount_add(p_normal, edge_keys[:, 0], q_normal[edge_keys[:, 0]])

                p_normal_magnitudes = np.sqrt(np.einsum("...i,...i", p_normal, p_normal))
                p_normal /= p_normal_magnitudes[:, None]  # total_normal.normalize()
                # npy dot product:  np.einsum('ij,ij->i',p_normal,new_co_dif)
                # vec list * scalar list => np.einsum('ij,i->ij',p_normal,scalarList)
                new_co_dif = (
                    p_co - q_co
                )  # to get diff between new and old position -> we will use it to determine size of vert movement along normal

                # p_normal[i].dot(new_co_dif[i])
                diff_projected_on_normal_scalar_li = np.einsum(
                    "ij,ij->i", p_normal, new_co_dif
                )  # normal has to be normlized
                aver_normal_scalar = np.sum(diff_projected_on_normal_scalar_li[sel_verts]) / np.sum(sel_verts)

                # projected_diff_on_normal = total_normal* total_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                projected_diff_on_normal = np.einsum(
                    "ij,i->ij",
                    p_normal,
                    diff_projected_on_normal_scalar_li * (1 - self.normal_smooth)
                    + self.normal_smooth * aver_normal_scalar,
                )

                p_co = p_co - projected_diff_on_normal * self.Inflate  # new aver normal
                # p_co =  p_co  + p_normal * self.Inflate   #new aver normal
                p_co[freeze_verts] = q_co[freeze_verts]  # not selected ver - reset to original pos o_co

                for axis_id, mirror_mask in on_axis_vmask.items():
                    p_co[mirror_mask, axis_id] = 0
                    p_normal[mirror_mask, axis_id] = 0

            if self.smooth_amount < 1:
                p_co = self.smooth_amount * p_co + (1 - self.smooth_amount) * o_co

        if method == "LC":
            calc_lc_numpy_smooth()
        elif method == "INFlATE":
            inflate_numpy_smooth()
        elif method == "VOL":
            vol_numpy_smooth()

        # source.vertices.foreach_set('co', p_co.ravel())
        if from_brush:
            self.bm = bm
            new_co = np.array([p_co[orig_to_new_idx[v.index]] for v in sel_v], "f")
            orig_co = np.array([o_co[orig_to_new_idx[v.index]] for v in sel_v], "f")
            self.o_normal = np.array(
                [o_normal[orig_to_new_idx[v.index]] for v in sel_v], "f"
            )  # for sliding only in brush mode
            self.o_normal = np.array(
                [o_normal[orig_to_new_idx[v.index]] for v in sel_v], "f"
            )  # for sliding only in brush mode
            self.freeze_verts = np.array(
                [freeze_verts[orig_to_new_idx[v.index]] for v in sel_v], "bool"
            )  # for sliding only in brush mode freeze_verts

            self.p_co = new_co
            self.o_co = orig_co
            self.sel_v = sel_v
            self.orig_to_new_idx = orig_to_new_idx

            remapped_mirror_v_mask = (
                {}
            )  # from sub sel vert group + adj geo verts,  to original verts (only selected) ids
            for axis_id, mirror_mask in on_axis_vmask.items():
                remapped_mirror_v_mask[axis_id] = np.array(
                    [mirror_mask[orig_to_new_idx[v.index]] for v in sel_v], "bool"
                )
            self.on_axis_vmask = remapped_mirror_v_mask
        else:
            for v in sel_v:
                if bpy.context.object.data.use_mirror_x:
                    mirror_vert_idx = self.mirror_map[v.index]
                    if mirror_vert_idx >= 0:
                        bm.verts[mirror_vert_idx].co = p_co[orig_to_new_idx[v.index]]
                        bm.verts[mirror_vert_idx].co.x *= -1
                v.co = p_co[orig_to_new_idx[v.index]]
            # source.update()
            close_bmesh(context, bm, context.active_object.data)
        # print('Laplacian numpy smooth took: '+ str(time.time()-startTime)+' sec')
        # bpy.ops.object.mode_set(mode = mode)

    def calc_numpy_smooth(self, context):
        pass


class VPS_OT_VolSmooth(bpy.types.Operator, CommonSmoothMethods):
    bl_idname = "mesh.vol_smooth"
    bl_label = "Volume Smoothing (slower)"
    bl_description = "Accurate but slower that Laplacian Smooting"
    bl_options = {"REGISTER", "UNDO"}

    smooth_amount: FloatProperty(
        name="Smooth amount", description="Smooth amount", default=1, min=0, max=1, step=1, precision=2
    )
    iteration_amount: IntProperty(
        name="Iterations", description="Number of times to repeat the smoothing", default=5, min=1, soft_max=20
    )
    tension: bpy.props.EnumProperty(
        items=(
            ("UNIFORM", "Uniform", "", "", 0),
            ("INVERSE", "Inverse to edge length", "", "", 1),
            ("PROPORTIONAL", "Proportional to edge length", "", "", 2),
        ),
        name="Tension",
        default="UNIFORM",
    )
    sharp_edge_weight: IntProperty(
        name="Sharp edge weight", description="sharp edge weight", default=1, min=0, max=100, step=1
    )
    freeze_border: BoolProperty(name="Freeze border", description="Freeze border verts", default=False)
    normal_smooth: FloatProperty(
        name="Normal Smooth",
        description="Amount of smoothing to normals",
        default=0.5,
        min=0,
        max=1,
        step=10,
        precision=2,
    )
    Inflate: FloatProperty(name="Inflate", description="Inflate", default=0.85, min=0, max=2, step=10, precision=2)

    # force_numpy: BoolProperty( name="Force Numpy", description="Force algorithm to use Numpy", default=False)

    def vol_smooth_mesh(self, context):
        # beta = 1-self.smooth_amount*0.6 #map smooth ammount from <0,1> to beta <0,7; 1>
        beta = 1 - self.smooth_amount * (
            0.6 - (self.iteration_amount / 20 * 0.1)
        )  # map smooth ammount from <0,1> to beta <0,7; 1>
        source = context.active_object.data
        bm = bmesh.from_edit_mesh(source)
        bm.verts.ensure_lookup_table()
        (x_axis_mirror, y_axis_mirror, z_axis_mirror), delta = get_mirrored_axis(context.active_object)
        selected_vertices = [v for v in bm.verts if v.select and not (self.freeze_border and v.is_boundary)]
        if len(selected_vertices) == 0:
            selected_vertices = [v for v in bm.verts if not (self.freeze_border and v.is_boundary)]
        # Go through each vertex and compute their smoothed position.

        startTime = time.time()

        vert_connections = []
        for vertex in selected_vertices:
            edges_count = len(vertex.link_edges)
            boundary_mirrored_edges = 0
            for edge in vertex.link_edges:
                if vertex.is_boundary and not edge.is_boundary:
                    boundary_mirrored_edges += 1
            vert_connections.append([edges_count + boundary_mirrored_edges, edges_count - boundary_mirrored_edges])
        for i in range(self.iteration_amount):
            edge_weights = [0] * len(bm.edges)
            new_co_diff = [Vector((0, 0, 0))] * len(bm.verts)

            for vertex, v_links in zip(selected_vertices, vert_connections):
                if v_links[0] == 0:
                    continue
                total_sum = Vector((0, 0, 0))
                edges_weight_total = 0
                for edge in vertex.link_edges:
                    neighbor_vert = edge.other_vert(vertex)
                    if edge_weights[edge.index] == 0:
                        edge_len = edge.calc_length()
                        if edge_len == 0:
                            edge_len = 0.001
                        if self.tension == "UNIFORM":
                            edge_weights[edge.index] = pow(edge_len, 2)
                        else:  # cos strength in inverse prop to len (maybe should be squared?)
                            edge_weights[edge.index] = 1 / edge_len
                    edge_weight = edge_weights[edge.index]
                    edges_weight_total += edge_weight
                    to_neighbor_vert_dir = bm.verts[neighbor_vert.index].co - vertex.co
                    if not vertex.is_boundary or edge.is_boundary:
                        total_sum += to_neighbor_vert_dir * edge_weight

                new_co_diff[vertex.index] = total_sum / edges_weight_total / v_links[0]
            for vertex, v_links in zip(selected_vertices, vert_connections):
                if v_links[0] == 0:
                    continue
                beta_x = Vector((0, 0, 0))
                for edge in vertex.link_edges:
                    if not vertex.is_boundary or edge.is_boundary:
                        neighbor_vert = edge.other_vert(vertex)
                        beta_x += new_co_diff[neighbor_vert.index]
                beta_sum = beta_x / v_links[1]
                vert_offset = new_co_diff[vertex.index] - (beta * new_co_diff[vertex.index] + (1 - beta) * beta_sum)
                if x_axis_mirror and vertex.co[0] <= delta:  # preserve mirrored vert splitting
                    vertex.normal[0] = 0
                if y_axis_mirror and vertex.co[1] <= delta:
                    vertex.normal[1] = 0
                if z_axis_mirror and vertex.co[2] <= delta:
                    vertex.normal[2] = 0

                projected_diff_on_normal = vertex.normal * vertex.normal.dot(
                    vert_offset
                )  # u(u dot v)  - projection of v on u
                vertex.co = vertex.co + vert_offset - projected_diff_on_normal * self.Inflate
        # Update the user mesh.
        # print('Volume smooth took: '+ str(time.time()-startTime)+' sec')
        bm.normal_update()
        bmesh.update_edit_mesh(source, loop_triangles=False, destructive=False)
        # bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode == "EDIT" and obj.type == "MESH"

    def invoke(self, context, event):
        context.active_object.update_from_editmode()
        self.mirror_map = get_mirrored_verts(context.active_object.data)
        return self.execute(context)

    def execute(self, context):
        self.numpy_smooth_init(context, method="VOL", tension=self.tension)
        return {"FINISHED"}


class VPS_OT_InflateSmooth(bpy.types.Operator, CommonSmoothMethods):
    bl_idname = "mesh.smooth_inflate"
    bl_label = "Inflate Smoothing"
    bl_description = "Good for simple round shapes"
    bl_options = {"REGISTER", "UNDO"}

    smooth_amount: FloatProperty(
        name="Smooth Amount", description="Amount of smoothing to apply", default=1, min=0, max=1, step=10, precision=2
    )
    iteration_amount: IntProperty(
        name="Iterations", description="Number of times to repeat the smoothing", default=5, min=1, soft_max=20, step=1
    )
    Inflate: FloatProperty(name="Inflate", description="Inflate", default=1, min=-2, max=2, step=10, precision=2)
    normal_smooth: FloatProperty(
        name="Normal Smooth",
        description="Amount of smoothing to normals",
        default=0.5,
        min=0,
        max=1,
        step=10,
        precision=2,
    )

    tension: bpy.props.EnumProperty(
        items=(
            ("UNIFORM", "Uniform", "", "", 0),
            ("INVERSE", "Inverse to edge length", "", "", 1),
            ("PROPORTIONAL", "Proportional to edge length", "", "", 2),
        ),
        name="Tension",
        default="UNIFORM",
    )
    sharp_edge_weight: IntProperty(
        name="Sharp edge weight", description="sharp edge weight", default=1, min=0, max=100, step=1
    )
    freeze_border: BoolProperty(name="Freeze border", description="Freeze border verts", default=False)
    # force_numpy: BoolProperty( name="Force Numpy", description="Force algorithm to use Numpy", default=False)

    def inflate_smooth(self, context, bm):
        bm.verts.ensure_lookup_table()
        (x_axis_mirror, y_axis_mirror, z_axis_mirror), delta = get_mirrored_axis(context.active_object)
        selected_vertices = [v for v in bm.verts if v.select and not (self.freeze_border and v.is_boundary)]
        if len(selected_vertices) == 0:
            selected_vertices = selected_vertices = [v for v in bm.verts if not (self.freeze_border and v.is_boundary)]
        # Go through each vertex and compute their smoothed position.
        o_normal = [vert.normal.copy() for vert in bm.verts]

        edge_weights = [1] * len(bm.edges)

        o_co = [vert.co.copy() for vert in bm.verts]
        q_co = o_co[:]
        p_co = o_co[:]
        edge_weights = [1] * len(bm.edges)
        diff_projected_on_normal_scalar_li = [0] * len(bm.verts)

        p_normal = o_normal[:]
        for i in range(self.iteration_amount):
            if self.tension == "PROPORTIONAL":
                edge_weights = [pow(edge.calc_length(), 2) for edge in bm.edges]
            elif self.tension == "INVERSE":  # cos strength in inverse prop to len (maybe should be squared?)
                edge_weights = [1 / max(edge.calc_length(), 0.001) for edge in bm.edges]
            new_co_dif = [Vector((0, 0, 0))] * len(bm.verts)
            q_normal = p_normal[:]
            p_normal = [Vector((0, 0, 0))] * len(bm.verts)
            for vertex in selected_vertices:
                i = vertex.index
                temp_new_normal = Vector((0, 0, 0))  # cos stupid bug in blender if normalizing vector list element
                total_sum = Vector((0, 0, 0))
                edge_count = len(vertex.link_edges)
                if edge_count == 0:
                    continue
                edges_weight_total = 0
                for edge in vertex.link_edges:
                    neighbor_vert = edge.other_vert(vertex)
                    edge_weight = edge_weights[edge.index]
                    edges_weight_total += edge_weight
                    to_neighbor_vert_dir = bm.verts[neighbor_vert.index].co - vertex.co
                    if not vertex.is_boundary or edge.is_boundary:  # skip bounary vert and not boundary edges.
                        total_sum += to_neighbor_vert_dir * edge_weight
                        temp_new_normal += q_normal[neighbor_vert.index] * edge_weight
                new_co_dif[i] = total_sum / edges_weight_total / edge_count
                if x_axis_mirror and vertex.co[0] <= delta:  # preserve mirrored vert splitting
                    new_co_dif[i][0] = 0
                    temp_new_normal[0] = 0
                if y_axis_mirror and vertex.co[1] <= delta:
                    new_co_dif[i][1] = 0
                    temp_new_normal[1] = 0
                if z_axis_mirror and vertex.co[2] <= delta:
                    new_co_dif[i][2] = 0
                    temp_new_normal[2] = 0

                p_normal[i] = temp_new_normal.normalized()
                diff_projected_on_normal_scalar_li[i] = p_normal[i].dot(new_co_dif[i])
            # average offsett along normal if smoothed normal is used.
            aver_normal_scalar = sum(diff_projected_on_normal_scalar_li) / len(selected_vertices)
            for vertex in selected_vertices:
                i = vertex.index
                vertex.co = vertex.co + self.smooth_amount * new_co_dif[i]
                projected_diff_on_normal = p_normal[i] * (
                    diff_projected_on_normal_scalar_li[i] * (1 - self.normal_smooth)
                    + self.normal_smooth * aver_normal_scalar
                )  # u(u dot v)  - projection of v on u
                # projected_diff_on_normal = p_normal* p_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                vertex.co -= self.smooth_amount * projected_diff_on_normal * self.Inflate
        # print('Inflate smooth  took: '+ str(time.time()-startTime)+' sec')

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH"

    def invoke(self, context, event):
        context.active_object.update_from_editmode()
        self.mirror_map = get_mirrored_verts(context.active_object.data)
        return self.execute(context)

    def execute(self, context):
        # if  context.active_object.mode == 'OBJECT' or self.force_numpy or np.sum(sel_verts)> len(bm.verts)/5: #if we select more than 20% verts use numpy
        self.numpy_smooth_init(context, method="INFlATE", tension=self.tension)
        return {"FINISHED"}


class VPS_OT_lc_Smooth(bpy.types.Operator, CommonSmoothMethods):
    bl_idname = "mesh.lc_hc_smooth"
    bl_label = "Laplacian Smooth"
    bl_description = "Quite Accurate and quite fast"
    bl_options = {"REGISTER", "UNDO"}

    smooth_amount: FloatProperty(
        name="Smooth amount", description="Smooth amount", default=1, min=0, max=1, step=10, precision=2
    )
    # beta:= FloatProperty(name="beta", description="Beta i influence (vs neibors)", default=0.5, min=0, max=1, step=10, precision=2)
    # beta_inf:= FloatProperty(name="beta influence", description="Beta influence ", default=1, min=0, max=1, step=10, precision=2)
    iteration_amount: IntProperty(
        name="Iterations", description="Number of times to repeat the smoothing", default=5, min=0, soft_max=20
    )
    # preserveVol: FloatProperty(name="Maintain Volume", description="Maintain  Volume", default=0.0, min=0, max=1, step=0.5, precision=2)
    alpha: FloatProperty(
        name="Origin influence",
        description="Strength of original vertex position influence",
        default=0.5,
        min=0,
        max=1,
        step=10,
        precision=1,
    )
    tension: bpy.props.EnumProperty(
        items=(
            ("UNIFORM", "Uniform", "", "", 0),
            ("INVERSE", "Inverse to edge length", "", "", 1),
            ("PROPORTIONAL", "Proportional to edge length", "", "", 2),
        ),
        name="Tension",
        default="UNIFORM",
    )
    sharp_edge_weight: IntProperty(
        name="Sharp edge weight", description="sharp edge weight", default=1, min=0, max=100, step=1
    )
    freeze_border: BoolProperty(name="Freeze border", description="Freeze border verts", default=False)
    # force_numpy: BoolProperty( name="Force Numpy", description="Force algorithm to use Numpy", default=False)

    def lc_smooth_mesh(self, context):
        beta = 1 - self.smooth_amount * 0.5  # map smooth ammount from <0,1> to beta <0,7; 1>
        source = context.active_object.data
        delta = 0.0001
        startTime = time.time()
        bm = get_bmesh(context, context.active_object.data)
        bm.verts.ensure_lookup_table()
        (x_axis_mirror, y_axis_mirror, z_axis_mirror), delta = get_mirrored_axis(context.active_object)
        selected_vertices = [v for v in bm.verts if v.select and not (self.freeze_border and v.is_boundary)]
        if len(selected_vertices) == 0:
            selected_vertices = selected_vertices = [v for v in bm.verts if not (self.freeze_border and v.is_boundary)]
        o_co = np.array([vert.co.copy() for vert in bm.verts])
        p_co = np.copy(o_co)
        b_co = np.zeros(shape=(len(bm.verts), 3), dtype=np.float32)
        q_co = np.copy(o_co)

        edge_weights = [1] * len(bm.edges)
        sel_v_mask = np.array([v.select for v in bm.verts])
        edge_keys = np.array([[edge.verts[0].index, edge.verts[1].index] for edge in bm.edges])
        for x in range(self.iteration_amount):
            q_co[sel_v_mask] = np.copy(p_co[sel_v_mask])
            b_co.fill(0)
            p_co.fill(0)
            diff = q_co[edge_keys[:, 1]] - q_co[edge_keys[:, 0]]
            if self.tension == "PROPORTIONAL":
                edge_weights = np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)
            elif self.tension == "INVERSE":  # cos strength in inverse prop to len (maybe should be squared?)
                edge_weights = 1 / np.maximum(np.sqrt(np.einsum("ij,ij->i", diff, diff)), 0.0001)
            for vertex in selected_vertices:
                linked_edges = len(vertex.link_edges)
                if linked_edges == 0:
                    continue
                i = vertex.index
                edges_weight_total = 0
                boundary_mirrored_edges = 0
                for edge in vertex.link_edges:
                    if not vertex.is_boundary or edge.is_boundary:
                        i_other = edge.other_vert(vertex).index
                        edges_weight_total += edge_weights[edge.index]
                        p_co[i] += (q_co[i_other] - q_co[i]) * edge_weights[edge.index]
                    else:
                        edges_weight_total += 2 * edge_weights[edge.index]
                        # edges_weight_total += edge_weights[edge.index]
                        boundary_mirrored_edges += 1  # times 2 cos we count virulat boundary mirror edge....
                # p_co[i] = q_co[i] + (p_co[i] / edges_weight_total - q_co[i])/(linked_edges+2*boundary_mirrored_edges)
                p_co[i] = q_co[i] + p_co[i] / edges_weight_total
            p_co[~sel_v_mask] = o_co[~sel_v_mask]
            b_co = p_co - (self.alpha * o_co + (1 - self.alpha) * q_co)
            beta_sum = np.zeros(3, dtype=np.float32)
            for vertex in selected_vertices:
                if len(vertex.link_edges) == 0:
                    continue
                beta_sum.fill(0)
                i = vertex.index
                boundary_mirrored_edges = 0
                for edge in vertex.link_edges:
                    i_other = edge.other_vert(vertex).index
                    if not vertex.is_boundary or edge.is_boundary:
                        beta_sum += b_co[i_other]
                    else:  # for border vert and non border edge ignore
                        #     # i_other = edge.other_vert(vertex).index
                        # beta_sum += 2*b_co[i_other]
                        boundary_mirrored_edges += 1
                # if vertex.is_boundary and np.any(beta_sum): #to preserve movement with flow of diffs... > >  > < $ makes sure beta_sum is non zero
                # 1 - cosx = 1  - dot.prod(a,b)/ mag(a) / mag(b)
                # project p_normal* p_normal.dot(new_co_dif)  # u(u dot v)  - projection of v on u
                #  projected b_sum on normal
                b_sum_projected_to_normal = bm.verts[i].normal * np.dot(
                    bm.verts[i].normal, beta_sum / (len(vertex.link_edges) - boundary_mirrored_edges)
                )
                p_co[i] = p_co[i] - (beta * b_co[i] + (1 - beta) * b_sum_projected_to_normal) * self.beta_inf
                # else:
                #     p_co[i]  = p_co[i] - (beta*b_co[i] + (1-beta)*beta_sum/(len(vertex.link_edges)-boundary_mirrored_edges))*self.beta_inf
            # symmetry snap fix if mirror is used
        for i, vertex in enumerate(selected_vertices):
            vertex.co = Vector(p_co[vertex.index])  # - projected_diff_on_normal * self.preserveVol
        # print('Laplacian smooth took: '+ str(time.time()-startTime)+' sec')
        close_bmesh(context, bm, context.active_object.data)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH"

    def invoke(self, context, event):
        context.active_object.update_from_editmode()
        self.mirror_map = get_mirrored_verts(context.active_object.data)
        return self.execute(context)

    def execute(self, context):
        # if self.force_numpy:
        self.numpy_smooth_init(context, method="LC", tension=self.tension)
        # else:
        #     self.lc_smooth_mesh(context)
        return {"FINISHED"}


class VPS_MT_SmoothMenu(bpy.types.Menu):
    bl_label = "Mesh Smoothing"
    bl_idname = __qualname__

    def draw(self, context):
        layout = self.layout
        # self.layout.operator('mesh.vol_smooth')
        self.layout.operator("mesh.smooth_inflate")
        self.layout.operator("mesh.lc_hc_smooth")
        self.layout.operator("mesh.vol_smooth")
        # self.layout.operator('mesh.lc_numpy_smooth')
