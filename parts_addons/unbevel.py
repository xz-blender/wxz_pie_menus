import bmesh
import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty
from bpy.types import Operator
from mathutils import Vector
from mathutils.geometry import intersect_line_line

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}


def flatten(nested):
    for item in nested:
        try:
            yield from flatten(item)
        except TypeError:
            yield item


def flattened(nested):
    return list(flatten(nested))


def walk_island(vert, sedges=None):
    vert.tag = True
    yield vert
    if sedges:
        linked_verts = []
        for e in vert.link_edges:
            if e in sedges:
                ov = e.other_vert(vert)
                if not ov.tag:
                    linked_verts.append(ov)
    else:
        linked_verts = [e.other_vert(vert) for e in vert.link_edges if not e.other_vert(vert).tag]
    for v in linked_verts:
        if v.tag:
            continue
        yield from walk_island(v, sedges=sedges)


def get_islands(bm, verts, same_part_edges=None):
    def tag(vs, switch):
        for i in vs:
            i.tag = switch

    if not same_part_edges:
        tag(bm.verts, True)
    tag(verts, False)
    islands = []
    verts = set(verts)
    while verts:
        v = verts.pop()
        verts.add(v)
        island = set(walk_island(v, sedges=same_part_edges))
        islands.append(list(island))
        tag(island, False)
        verts -= island
    return islands


def get_face_islands(bm, sel_verts=None, sel_edges=None, sel_faces=None):
    # Not super optimal, but convenient
    if not sel_verts:
        sel_verts = [v for v in bm.verts if v.select]
    if not sel_edges:
        sel_edges = [e for e in bm.edges if e.select]
    if not sel_faces:
        sel_faces = [f for f in bm.faces if f.select]
    v_islands = get_islands(bm, verts=sel_verts, same_part_edges=sel_edges)
    f_islands = []
    for vi in v_islands:
        f_island = [f for f in sel_faces if f.verts[0] in vi]
        f_islands.append(f_island)
    return f_islands


def vertloops(vertpairs):
    """Sort verts from list of vert pairs"""
    loop_vp = [i for i in vertpairs]
    loops = []
    while len(loop_vp) > 0:
        vpsort = [loop_vp[0][0], loop_vp[0][1]]
        loop_vp.pop(0)
        loops.append(vpsort)
        for n in range(0, len(vertpairs)):
            i = 0
            for e in loop_vp:
                if vpsort[0] == e[0]:
                    vpsort.insert(0, e[1])
                    loop_vp.pop(i)
                    break
                elif vpsort[0] == e[1]:
                    vpsort.insert(0, e[0])
                    loop_vp.pop(i)
                    break
                elif vpsort[-1] == e[0]:
                    vpsort.append(e[1])
                    loop_vp.pop(i)
                    break
                elif vpsort[-1] == e[1]:
                    vpsort.append(e[0])
                    loop_vp.pop(i)
                    break
                else:
                    i += 1
    return loops


def get_endpoints(vert, exclude_faces, vec_check, se):
    vert_linkfaces = [i for i in vert.link_faces if i not in exclude_faces]
    ce = [None, -9]
    ngon = False
    # unconnected tri, ngon cyl caps etc
    if vert_linkfaces:
        ngon = all(len(f.verts) != 4 for f in vert_linkfaces)
        if len(vert_linkfaces) == 1 and len(vert_linkfaces[0].verts) != 4:
            ngon = True
    if ngon:
        return vert.co, vert_linkfaces[0].calc_center_median_weighted(), True
    else:
        for f in vert_linkfaces:
            edge_candidates = [e for e in f.edges if e not in se]
            if edge_candidates:
                for e in edge_candidates:
                    if vert in e.verts:
                        vec = Vector(e.verts[0].co - e.verts[1].co).normalized()
                        cv = abs(vec.dot(vec_check)) - 1
                        if cv > ce[1]:
                            ce = [e, cv]
        if ce[0] is not None:
            return vert.co, ce[0].other_vert(vert).co, False
    return None, None, False


class PIE_MT_Unbevel(Operator):
    bl_idname = "pie.unbevel"
    bl_label = "Unbevel"
    bl_description = "选择循环边进行重倒角\n" "重倒角:设置在重做面板中"
    bl_options = {"REGISTER", "UNDO"}

    rebevel: BoolProperty(name="重新倒角", default=False)  # type: ignore
    keep_width: BoolProperty(name="保持宽度", default=True)  # type: ignore
    offset: FloatProperty(name="偏移量", min=0, max=100, default=0.01, subtype="DISTANCE")  # type: ignore
    segments: IntProperty(name="重倒角数量", min=0, max=999, soft_max=99, default=0)  # type: ignore
    profile: FloatProperty(name="重倒角形状", min=0, max=1, default=0.5)  # type: ignore
    merge_uvs: BoolProperty(default=False, name="重倒角-合并UVs", description="You rarely want this")  # type: ignore

    unbevel_autoring: BoolProperty(
        name="Unbevel Auto-EdgeRing", default=False, description="Runs Edge-Ring selection before Unbevel"
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH" and context.object.data.is_editmode

    def draw(self, context):
        # k = bpy.context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "unbevel_autoring", text="自动选择循环", toggle=True)
        row = layout.row(align=True)
        row.prop(self, "rebevel", toggle=True)
        if self.rebevel:
            row.prop(self, "keep_width", toggle=True)
            if not self.keep_width:
                layout.prop(self, "offset", toggle=True)
            layout.prop(self, "segments")
            layout.prop(self, "profile")
            layout.prop(self, "merge_uvs", toggle=True)
        layout.separator()

    def execute(self, context):
        # k = bpy.context.preferences.addons[__package__].preferences
        sel_mode = context.tool_settings.mesh_select_mode[:]
        obj = context.active_object
        od = obj.data
        bm = bmesh.from_edit_mesh(od)
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        sel_faces = [i for i in bm.faces if i.select]

        if sel_mode[2]:
            edge_rings = []

            face_island = get_face_islands(bm, sel_faces=sel_faces)

            for island in face_island:
                # sort for edge rings
                outer_edges = []
                inner_edges = []

                for f in island:
                    for of in island:
                        if of != f:
                            for e in f.edges:
                                if e in of.edges:
                                    inner_edges.append(e)
                                else:
                                    outer_edges.append(e)

                outer_edges = list(set(outer_edges))
                inner_edges = list(set(inner_edges))
                inner_verts = flattened([e.verts for e in inner_edges])
                for e in outer_edges:
                    if any(v for v in e.verts if v in inner_verts) and e not in inner_edges:
                        edge_rings.append(e)

            if edge_rings:
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
                bpy.ops.mesh.select_all(action="DESELECT")
                for e in edge_rings:
                    e.select_set(True)
                bmesh.update_edit_mesh(od)

        # if k.unbevel_autoring:
        if self.unbevel_autoring:
            bpy.ops.mesh.loop_multi_select(ring=True)

        sel_edges = [i for i in bm.edges if i.select]

        if not sel_edges:
            self.report({"INFO"}, "Invalid selection")
            return {"CANCELLED"}

        # compensation for rebevel clamp-filling up old bevel width
        seg_count = self.segments + 1

        post_sel = []
        post_merge = []

        vert_pairs = [e.verts for e in sel_edges]
        loops = vertloops(vert_pairs)

        if len(sel_edges) == len(loops) and self.rebevel:
            # Chamfer special, needs a center cut
            geo = bmesh.ops.bisect_edges(bm, edges=sel_edges, cuts=2)
            sel_verts = [i for i in geo["geom_split"] if isinstance(i, bmesh.types.BMVert)]
            sel_edges = [i for i in geo["geom_split"] if isinstance(i, bmesh.types.BMEdge)]
            bmesh.ops.connect_verts(bm, verts=sel_verts)
            vert_pairs = [e.verts for e in sel_edges]
            loops = vertloops(vert_pairs)

        exclude = []
        for e in sel_edges:
            exclude.extend(e.link_faces[:])
        exclude = list(set(exclude))

        mvs = []
        for vloop in loops:
            # create in-loop end vectors to test for closest
            vc1 = Vector(vloop[0].co - vloop[1].co).normalized()
            vc2 = Vector(vloop[-1].co - vloop[-2].co).normalized()

            v1, v2, ngon1_2 = get_endpoints(vert=vloop[0], exclude_faces=exclude, vec_check=vc1, se=sel_edges)
            v3, v4, ngon3_4 = get_endpoints(vert=vloop[-1], exclude_faces=exclude, vec_check=vc2, se=sel_edges)

            if any(i is None for i in [v1, v2, v3, v4]):
                self.report({"INFO"}, "Aborted: Invalid Selection")
                return {"CANCELLED"}

            linepoints = intersect_line_line(v1, v2, v3, v4)

            if linepoints is None:
                self.report({"INFO"}, "Aborted: Invalid Selection")
                return {"CANCELLED"}

            if ngon1_2 and ngon3_4:
                xpoint = linepoints[0].lerp(linepoints[-1], 0.5)
            elif ngon1_2:
                xpoint = linepoints[-1]
            elif ngon3_4:
                xpoint = linepoints[0]
            else:
                p1 = vc1.dot(Vector(vloop[0].co - linepoints[0]).normalized())
                p2 = vc1.dot(Vector(vloop[0].co - linepoints[-1]).normalized())
                if p1 > p2:
                    xpoint = linepoints[0]
                else:
                    xpoint = linepoints[-1]

            if self.rebevel and self.keep_width:
                merge_verts = vloop[1:-1]
            else:
                merge_verts = vloop

            mvs.append(merge_verts + [xpoint])
            post_merge.extend([vloop[0], vloop[-1]])

        for mv in mvs:
            post_sel.append(mv[0])
            bmesh.ops.pointmerge(bm, verts=mv[:-1], merge_co=mv[-1])

        bm.normal_update()
        bmesh.update_edit_mesh(od)

        bpy.ops.mesh.select_all(action="DESELECT")
        for v in post_sel:
            v.select_set(True)
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_mode(type="EDGE")

        if self.rebevel:
            new_edges = [e for e in bm.edges if e.select]
            if new_edges:
                if self.keep_width:
                    o = 100
                    t = "PERCENT"
                else:
                    o = self.offset
                    t = "WIDTH"
                result = bmesh.ops.bevel(
                    bm,
                    geom=new_edges,
                    offset_type=t,
                    offset=o,
                    affect="EDGES",
                    clamp_overlap=True,
                    loop_slide=True,
                    segments=seg_count,
                    profile=self.profile,
                )
                if self.keep_width:
                    merge = result["verts"] + post_merge
                    bmesh.ops.remove_doubles(bm, verts=merge, dist=0.0003)
                bmesh.update_edit_mesh(od)
            else:
                self.report({"INFO"}, "Aborted Rebevel: Ops Selection Error")

        if sel_mode[2]:
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")

        return {"FINISHED"}


classes = [
    PIE_MT_Unbevel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
