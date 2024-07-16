import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty

from .utils import *


class PIE_OffsetCut(bpy.types.Operator):
    bl_idname = "pie.mm_offset_cut"
    bl_label = "重构无法倒角的边"
    bl_description = "选择需要倒角的循环边(Ngon)，自动向两侧偏移重构四边面"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="宽度", default=0.1, min=0.002, step=0.1)  # type: ignore
    resample: BoolProperty(name="重新采样", default=True)  # type: ignore
    factor: FloatProperty(name="Factor", default=1, min=0.5)  # type: ignore
    smooth: BoolProperty(name="平滑", default=False)  # type: ignore
    iterations: IntProperty(name="迭代次数", default=1, min=1)  # type: ignore
    optimize: BoolProperty(name="优化", default=True)  # type: ignore
    angle: FloatProperty(name="Angle", default=180, min=0, max=180)  # type: ignore
    extend: FloatProperty(name="Extend", default=0.2, min=0)  # type: ignore
    override: BoolProperty(name="Spread", default=False)  # type: ignore
    rails: IntProperty(name="精度", default=18, min=7)  # type: ignore
    tilt: FloatProperty(name="摆动种子", default=1)  # type: ignore
    shift: BoolProperty(name="Shift", default=True)  # type: ignore
    solver: EnumProperty(name="Solver", items=boolean_solver_items, default="FAST")  # type: ignore

    shade_smooth: BoolProperty(default=False)  # type: ignore
    mark_sharp: BoolProperty(default=False)  # type: ignore
    all_cyclic: BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return len([f for f in bm.edges if f.select]) >= 1

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)

        column.prop(self, "width")

        if not self.all_cyclic:
            split = column.split(factor=0.7, align=True)
            split.prop(self, "extend")
            split.prop(self, "override", toggle=True)

        column.separator()

        row = column.row(align=True)

        row.prop(self, "resample", toggle=True)
        r = row.split(align=True)
        r.active = self.resample
        r.prop(self, "factor")

        row = column.row(align=True)
        row.prop(self, "smooth", toggle=True)
        r = row.split(align=True)
        r.active = self.smooth
        r.prop(self, "iterations")

        row = column.row(align=True)
        row.prop(self, "optimize", toggle=True)
        r = row.split(align=True)
        r.active = self.optimize
        # r.prop(self, "angle")

        row = column.row(align=True)
        row.prop(self, "solver", expand=True)

        column.separator()

        row = column.row(align=True)
        row.prop(self, "rails")
        row.prop(self, "tilt")
        # row.prop(self, "shift", toggle=True)

    def execute(self, context):
        active = context.active_object
        mxw = active.matrix_world

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        edge_layer, face_layer = self.get_data_layers(bm, force_new=True)

        verts = [v for v in bm.verts if v.select]

        sequences = get_selected_vert_sequences(verts, debug=False)

        edge = bm.edges.get((sequences[0][0][0], sequences[0][0][1]))
        face = edge.link_faces[0]
        self.mark_sharp = not edge.smooth
        self.shade_smooth = face.smooth
        self.all_cyclic = all(cyclic for _, cyclic in sequences)

        circle_coords, circle_normals = create_circle_coords(
            self.width, self.rails, self.tilt, calc_normals=True, debug=False
        )

        pipes = []
        all_pipe_faces = []
        face_maps = []

        for idx, (seq, cyclic) in enumerate(sequences):
            coords = create_pipe_coords(
                seq,
                cyclic,
                self.resample,
                self.factor,
                self.smooth,
                self.iterations,
                self.optimize,
                self.angle,
                mxw,
                debug=False,
            )

            ext_coords = self.extend_coords(coords, cyclic, self.extend)

            ring_coords = create_pipe_ring_coords(
                ext_coords, cyclic, circle_coords, circle_normals, mx=mxw, debug=False
            )

            vert_rings = self.create_pipe_verts(bm, ring_coords, cyclic, mx=mxw, debug=False)

            pipe_faces = self.create_pipe_faces(
                bm, vert_rings, cyclic, edge_layer, face_layer, idx, self.shift, self.shade_smooth
            )
            all_pipe_faces.extend(pipe_faces)

            pipes.append((coords, cyclic))

        bmesh.ops.recalc_face_normals(bm, faces=all_pipe_faces)
        bmesh.update_edit_mesh(active.data)

        for idx in range(len(pipes)):
            self.boolean_pipe(bm, face_layer, idx)

        bpy.ops.mesh.select_all(action="DESELECT")

        merge_verts = []
        junk_edges = []

        for pipe_idx, (coords, cyclic) in enumerate(pipes):
            faces = [f for f in bm.faces if f[face_layer] == pipe_idx + 1]
            edges = {e for f in faces for e in f.edges}
            verts = {v for f in faces for v in f.verts}

            geom = bmesh.ops.region_extend(bm, geom=faces, use_faces=True)
            border_faces = geom["geom"]
            border_edges = {e for f in border_faces for e in f.edges}
            border_verts = {v for f in border_faces for v in f.verts}

            sweeps, non_sweep_edges, has_caps = self.get_sorted_sweep_edges(len(coords), edges, edge_layer, pipe_idx)

            end_rail_edges = (
                self.set_end_sweeps(sweeps, border_verts, border_edges) if not cyclic and len(sweeps) > 2 else set()
            )

            junk = self.collect_junk_edges(non_sweep_edges, border_edges, border_verts, end_rail_edges)
            junk_edges.extend(junk)

            merge = self.recreate_hard_edges(sweeps, cyclic, coords, border_verts, self.override)
            merge_verts.extend(merge)

            self.mark_end_sweep_edges_sharp(self.mark_sharp, cyclic, has_caps, border_edges, merge_verts)

        bmesh.ops.dissolve_edges(bm, edges=junk_edges, use_verts=True)
        bmesh.ops.remove_doubles(bm, verts=[v for v in merge_verts if v.is_valid], dist=0.00001)

        bm.select_flush(True)

        self.mark_selected_sharp(bm, self.mark_sharp)

        bm.edges.layers.string.remove(edge_layer)
        bm.faces.layers.int.remove(face_layer)

        bmesh.update_edit_mesh(active.data)
        return {"FINISHED"}

    def get_data_layers(self, bm, force_new=False):
        edge_layer = bm.edges.layers.string.get("OffsetCutEdges")
        face_layer = bm.faces.layers.int.get("OffsetCutFaces")

        if force_new:
            if edge_layer:
                bm.edges.layers.string.remove(edge_layer)

            if face_layer:
                bm.faces.layers.int.remove(face_layer)

        edge_layer = bm.edges.layers.string.new("OffsetCutEdges")
        face_layer = bm.faces.layers.int.new("OffsetCutFaces")

        return edge_layer, face_layer

    def extend_coords(self, coords, cyclic, extend):
        if not cyclic and extend:
            ext_coords = coords.copy()

            start_dir = (coords[0] - coords[1]).normalized()
            ext_coords[0] = coords[0] + start_dir * extend

            end_dir = (coords[-1] - coords[-2]).normalized()
            ext_coords[-1] = coords[-1] + end_dir * extend

        else:
            ext_coords = coords

        return ext_coords

    def create_pipe_verts(self, bm, ring_coords, cyclic, mx=None, debug=False):
        vert_rings = []

        for ridx, ring in enumerate(ring_coords):
            if ridx == len(ring_coords) - 1:
                if cyclic:
                    next_ring = ring_coords[0]
                else:
                    verts = []
                    for co, _ in ring:
                        v = bm.verts.new(co)
                        verts.append(v)

                    vert_rings.append((verts, 0))
                    continue
            else:
                next_ring = ring_coords[ridx + 1]

            first_co, first_nrm = ring[0]

            dots = [(idx, co, first_nrm.dot(nrm)) for idx, (co, nrm) in enumerate(next_ring)]
            maxdot = max(dots, key=lambda x: x[2])

            shift_amount = maxdot[0]

            if debug and mx:
                draw_line([first_co, maxdot[1]], mx=mx, color=(1, 1, 0), alpha=0.5, modal=False)

            verts = []
            for co, _ in ring:
                v = bm.verts.new(co)
                verts.append(v)

            vert_rings.append((verts, shift_amount))

        return vert_rings

    def create_pipe_faces(self, bm, vert_rings, cyclic, edge_layer, face_layer, pipe_idx, shift, smooth):
        pipe_faces = []

        for ridx, ring in enumerate(vert_rings):
            if cyclic:
                if ridx == len(vert_rings) - 1:
                    next_verts = vert_rings[0][0]

                else:
                    next_verts = vert_rings[ridx + 1][0]

            else:
                if ridx in [0, len(vert_rings) - 1]:
                    f = bm.faces.new(ring[0])

                    f[face_layer] = pipe_idx + 1
                    pipe_faces.append(f)

                    for e in f.edges:
                        d = {pipe_idx: ridx}
                        e[edge_layer] = str(d).encode()

                    if ridx == len(vert_rings) - 1:
                        continue

                next_verts = vert_rings[ridx + 1][0]

            verts, shift_amount = ring

            if shift and shift_amount:
                next_verts = next_verts.copy()
                rotate_list(next_verts, shift_amount)

            for vidx, (v, vn) in enumerate(zip(verts, next_verts)):

                if vidx < self.rails - 1:
                    f = bm.faces.new([v, verts[vidx + 1], next_verts[vidx + 1], vn])

                else:
                    f = bm.faces.new([v, verts[0], next_verts[0], vn])

                f.smooth = smooth

                if cyclic or ridx > 0:
                    e = f.edges[0]

                    d = {pipe_idx: ridx}
                    e[edge_layer] = str(d).encode()

                f[face_layer] = pipe_idx + 1

                pipe_faces.append(f)

        return pipe_faces

    def boolean_pipe(self, bm, face_layer, pipe_idx):

        bpy.ops.mesh.select_all(action="DESELECT")

        for f in bm.faces:
            if f[face_layer] == pipe_idx + 1:
                f.select_set(True)

        bpy.ops.mesh.intersect_boolean(operation="DIFFERENCE", solver=self.solver)

    def mark_selected_sharp(self, bm, mark_sharp):
        if mark_sharp:
            for e in bm.edges:
                if e.select:
                    e.smooth = False

    def mark_end_sweep_edges_sharp(self, mark_sharp, cyclic, has_caps, border_edges, merge_verts):
        if cyclic or has_caps or not mark_sharp:
            return

        else:
            for e in [e for e in border_edges if any([v in merge_verts for v in e.verts])]:
                e.smooth = False

    def collect_junk_edges(self, non_sweep_edges, border_edges, border_verts, end_rail_edges):
        junk = set()

        for e in non_sweep_edges - border_edges - end_rail_edges:
            if any(v in border_verts for v in e.verts):
                junk.add(e)

        return list(junk)

    def recreate_hard_edges(self, sweeps, cyclic, coords, border_verts, override):
        merge = set()

        for idx, (sweep, co) in enumerate(zip(sweeps, coords)):
            if sweep:
                sweep_verts = {v for e in sweep for v in e.verts}

                if cyclic or 0 < idx < len(sweeps) - 1 or override:
                    sweep_verts -= border_verts

                for v in sweep_verts:
                    v.co = co

                    merge.add(v)

                    v.select_set(True)

        return merge

    def set_end_sweeps(self, sweeps, border_verts, border_edges):
        end_rails = set()

        if sweeps[1]:
            for e in sweeps[1]:
                if not any([v in border_verts for v in e.verts]):
                    sweep = []

                    for loop in e.link_loops:
                        start_loop = loop

                        while True:
                            loop = loop.link_loop_next

                            if loop.edge in border_edges:
                                sweep.append(loop.edge)

                            else:
                                end_rails.add(loop.edge)

                            if loop == start_loop:
                                break

                    if sweeps[0] is None:
                        sweeps[0] = sweep

                    else:
                        sweeps[0].extend(sweep)

        if sweeps[-2]:
            for e in sweeps[-2]:
                if not any([v in border_verts for v in e.verts]):
                    sweep = []

                    for loop in e.link_loops:
                        start_loop = loop

                        while True:
                            loop = loop.link_loop_next

                            if loop.edge in border_edges:
                                sweep.append(loop.edge)

                            else:
                                end_rails.add(loop.edge)

                            if loop == start_loop:
                                break

                            if sweeps[-1] is None:
                                sweeps[-1] = sweep

                            else:
                                sweeps[-1].extend(sweep)

        return end_rails

    def get_sorted_sweep_edges(self, sweep_count, edges, layer, pipe_idx):
        sweeps = [None] * sweep_count
        non_sweep_edges = set()

        for e in edges:
            edge_string = e[layer].decode()

            if edge_string:
                edge_dict = eval(edge_string)

                sweep_idx = edge_dict.get(pipe_idx)

                sweep = sweeps[sweep_idx]

                if sweep:
                    sweeps[sweep_idx].append(e)

                else:
                    sweeps[sweep_idx] = [e]

            else:
                non_sweep_edges.add(e)

        return sweeps, non_sweep_edges, True if sweeps[0] and sweeps[-1] else False
