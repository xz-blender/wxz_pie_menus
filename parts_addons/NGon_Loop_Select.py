import os

import bmesh
import bpy
import numpy as np  # type: ignore
import rna_keymap_ui
from bpy_extras import view3d_utils
from mathutils import Vector

bl_info = {
    "name": "NGon Loop Select",
    "author": "Amandeep",
    "description": "Selects all vertices in a loop",
    "blender": (2, 90, 0),
    "version": (3, 0, 0),
    "warning": "",
    "category": "Object",
}


kmaps_3dview = ["ls.select", "ls.selectfaceloop"]


def draw_hotkeys(col, km_name):
    kc = bpy.context.window_manager.keyconfigs.user
    for kmi in kmaps_3dview:
        km2 = kc.keymaps[km_name]
        kmi2 = []
        for a, b in km2.keymap_items.items():
            if a == kmi:
                kmi2.append(b)

        if kmi2:
            for a in kmi2:
                col.context_pointer_set("keymap", km2)
                rna_keymap_ui.draw_kmi([], kc, km2, a, col, 0)


class LSPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        draw_hotkeys(layout, "Mesh")


def deselect_all():
    if bpy.context.mode == "OBJECT":
        bpy.ops.object.select_all(action="DESELECT")
    elif "EDIT" in bpy.context.mode:
        bpy.ops.mesh.select_all(action="DESELECT")


def get_angle(e1, e2, vert):
    v1 = e1.other_vert(vert)
    v3 = e2.other_vert(vert)
    # print(v1.co,v3.co,vert.co)
    # print(math.degrees(v1.co.angle(vert.co)),math.degrees(vert.co.angle(v3.co)))
    a1 = (vert.co - v1.co).normalized()
    a2 = (v3.co - vert.co).normalized()
    # print(a1,a2)
    try:
        angle = a1.angle(a2)
        # print(math.degrees(angle))
    except:
        #  print("Invalid angle returning 0\nVectors:",vert,v1,v3)
        return 0
    return angle


import math


def calculate_average_moving_vector(vertices):
    """
    Calculate the average moving vector from a list of vertices in Blender.

    :param vertices: A list of vertices (bpy.types.MeshVertex)
    :return: A numpy array representing the average moving vector
    """
    # Ensure there are enough vertices to calculate vectors
    if len(vertices) < 2:
        raise ValueError("At least two vertices are required to calculate a moving vector")

    # Create a list of vertex coordinates
    coords = [v.co for v in vertices]
    total = len(coords)
    skip = int(total * 0.1)
    # Calculate the vectors between consecutive vertices
    vectors = [coords[i + 1] - coords[i] for i in range(skip, len(coords) - 1)]

    # Convert vectors to numpy arrays for easier calculation
    vectors_np = np.array([np.array(v) for v in vectors])

    # Calculate the average moving vector
    average_vector = vectors_np.mean(axis=0)

    return Vector(average_vector).normalized()


def calculate_alignment(edge, vert, average_vector):
    """
    Calculate the alignment of a given vector with the average moving vector using cosine similarity.

    :param given_vector: A numpy array representing the given vector
    :param average_vector: A numpy array representing the average moving vector
    :return: A float representing the cosine similarity between the two vectors
    """
    # Normalize the vectors
    # print("V",vert.co,"OV",edge.other_vert(vert).co)
    given_vector = vert.co - edge.other_vert(vert).co
    given_vector = given_vector.normalized()
    # print("GV",given_vector)
    norm_given = np.linalg.norm(given_vector)
    norm_average = np.linalg.norm(average_vector)

    if norm_given == 0 or norm_average == 0:
        raise ValueError("One of the vectors has zero length")

    normalized_given = given_vector / norm_given
    normalized_average = average_vector / norm_average

    # Calculate cosine similarity
    cosine_similarity = np.dot(normalized_given, normalized_average)

    inverse_alignment = 1 - cosine_similarity
    if inverse_alignment > 1:
        inverse_alignment = 2 - inverse_alignment
    # print(inverse_alignment)
    return inverse_alignment
    return cosine_similarity


def find_loops(edges):
    # Create a mapping from vertices to edges
    vertex_edge_map = {}
    for edge in edges:
        for vert in edge.verts:
            if vert not in vertex_edge_map:
                vertex_edge_map[vert] = set()
            vertex_edge_map[vert].add(edge)

    # Function to traverse the mesh and find loops
    def traverse_loop(start_edge, visited_edges):
        loop = []
        current_edge = start_edge
        # print("SE",start_edge)
        while current_edge not in visited_edges:
            visited_edges.add(current_edge)
            # print("CE",current_edge.index,"To",len(visited_edges))
            loop.append(current_edge)
            for vert in current_edge.verts:
                for edge in vertex_edge_map[vert]:
                    if edge != current_edge and edge not in visited_edges:
                        current_edge = edge
                        # print("set ce",current_edge)
                        break
                else:
                    # print("con",current_edge)
                    continue
                # print("Break",current_edge)
                break
        return loop

    # Find all loops
    visited_edges = set()
    loops = []
    for edge in edges:
        if edge not in visited_edges:
            loop = traverse_loop(edge, visited_edges)
            if loop and len(loop) > 2:
                loops.append(loop)

    return loops


# from collections import OrderedDict
# edges=OrderedDict()
#                     for a in sorted_edge:
#                         new_angle=get_angle(a,active_edge,vert)
#                         edges[str(round(new_angle,2))]=sorted(edges[str(round(new_angle,2))]+[a,],key =lambda x:True if x.index in new_selection else False) if str(round(new_angle,2)) in edges.keys() else [a,]


#                     sorted_edges=[]
#                     for key,value in edges.items():
#                         sorted_edges.extend(value)
def get_common_faces(active_edge, edge):
    return len([a for a in active_edge.link_faces if a in edge.link_faces])


class LS_OT_Select(bpy.types.Operator):
    bl_idname = "ls.select"
    bl_label = "Loop Select"
    bl_description = "Select Loop"
    bl_options = {"REGISTER", "UNDO"}
    edge_threshold: bpy.props.FloatProperty(default=math.radians(100), name="Edge Threshold", subtype="ANGLE")  # type: ignore
    face_threshold: bpy.props.FloatProperty(default=math.radians(60), name="Face Threshold", subtype="ANGLE")  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):

        active = context.active_object
        bm = bmesh.from_edit_mesh(active.data)
        bm.edges.ensure_lookup_table()
        # print([a for a in bm.verts if a.select])
        # if issubclass(type(bm.select_history.active),bmesh.types.BMVert) and bm.select_history.active.link_edges:
        #    bm.select_history.add(bm.select_history.active.link_edges[0])
        face_threshold = self.face_threshold
        if self.active_edge is not None:  # and issubclass(type(bm.select_history.active),bmesh.types.BMEdge):
            active_edge = bm.select_history.active

            context.scene.nls_state.active_edge = bm.select_history.active.index

            active_edge = bm.edges[self.active_edge]
            # print(active_edge)
            # bpy.ops.mesh.loop_multi_select(ring=False)
            # active.data.update()
            # bm=bmesh.from_edit_mesh(active.data)

            # new_selection=[a.index for a in bm.edges if a.select]
            # deselect_all()
            # active_edge=bm.edges[active_edge_index]
            # active_edge.select=True
            og_edge = active_edge
            if active_edge:
                if len(active_edge.link_faces) == 2:
                    angle = active_edge.calc_face_angle_signed()
                    vert = active_edge.other_vert(active_edge.verts[0])
                    og_vert = vert
                    other_vert = active_edge.verts[0]
                    used = []
                    used.append(active_edge.verts[0])
                    used.append(active_edge.verts[1])
                    verts_for_avg_vector = used
                    while vert:
                        # print("Used",[a.co for a in used])
                        avg_vector = calculate_average_moving_vector(verts_for_avg_vector)
                        # print("Avg",avg_vector)
                        # print("vert",vert.co)
                        # sorted_edge=sorted([e for e in vert.link_edges],key =lambda x:True if [f for f in x.link_faces if f in active_edge.link_faces] else False)
                        # sorted_edge=sorted([e for e in vert.link_edges if e!=active_edge],key =lambda x:(get_angle(x,active_edge,vert),get_common_faces(active_edge,x)))
                        # sorted_edge=sorted([e for e in vert.link_edges if e!=active_edge],key =lambda x:(get_common_faces(active_edge,x),get_angle(x,active_edge,vert)))
                        sorted_edge = sorted(
                            [e for e in vert.link_edges if e != active_edge],
                            key=lambda x: (
                                get_common_faces(active_edge, x),
                                get_angle(x, active_edge, vert),
                                calculate_alignment(x, vert, avg_vector),
                            ),
                        )
                        l = filter(lambda x: get_angle(x, active_edge, vert) < self.edge_threshold, sorted_edge)

                        for e in l:
                            if e != active_edge and len(e.link_faces) == 2:

                                if abs(e.calc_face_angle_signed() - angle) < face_threshold:
                                    e.select = True
                                    active_edge = e
                                    vert = [v for v in e.verts if v != vert and v not in used]
                                    if vert:
                                        vert = vert[0]
                                        used.append(vert)
                                        verts_for_avg_vector.append(vert)
                                    break
                        else:
                            vert = None

                    vert = other_vert
                    active_edge = og_edge
                    verts_for_avg_vector = []

                    verts_for_avg_vector.append(active_edge.verts[1])
                    verts_for_avg_vector.append(active_edge.verts[0])
                    while vert:
                        avg_vector = calculate_average_moving_vector(verts_for_avg_vector)
                        # print(avg_vector)
                        # sorted_edge=sorted([e for e in vert.link_edges if e!=active_edge],key =lambda x:(get_angle(x,active_edge,vert),get_common_faces(active_edge,x)))
                        # sorted_edge=sorted([e for e in vert.link_edges if e!=active_edge],key =lambda x:(get_common_faces(active_edge,x),get_angle(x,active_edge,vert)))
                        sorted_edge = sorted(
                            [e for e in vert.link_edges if e != active_edge],
                            key=lambda x: (
                                get_common_faces(active_edge, x),
                                get_angle(x, active_edge, vert),
                                calculate_alignment(x, vert, avg_vector),
                            ),
                        )
                        l = filter(lambda x: get_angle(x, active_edge, vert) < self.edge_threshold, sorted_edge)
                        for e in l:
                            if e != active_edge and len(e.link_faces) == 2:
                                if abs(e.calc_face_angle_signed() - angle) < face_threshold:
                                    e.select = True
                                    active_edge = e
                                    vert = [v for v in e.verts if v != vert and v not in used]
                                    if vert:
                                        vert = vert[0]
                                        used.append(vert)
                                        verts_for_avg_vector.append(vert)
                                    break
                        else:
                            vert = None
                    # context.tool_settings.mesh_select_mode=self.previous_selection_mode
                    # context.active_object.data.update()
                    # return {'FINISHED'}
                    selected_verts = [v for v in bm.verts if v.select]
                    vert = other_vert
                    active_edge = og_edge
                    # print(vert)
                    split_verts = get_split_vert(vert, active_edge)
                    edges_to_deselect = []
                    if split_verts:

                        for split_vert in split_verts:

                            deselect = False

                            for e in split_vert.link_edges:
                                if e.select:
                                    (length, edges) = get_path_to_self(vert, e, split_vert)

                                    if length < 99999:
                                        deselect = True
                                    else:
                                        edges_to_deselect.append((length, edges))
                        # print(edges_to_deselect)
                        edges_to_deselect = sorted(edges_to_deselect, key=lambda x: x[0])
                        if deselect:
                            for i, e in enumerate(edges_to_deselect):
                                for edge in e[1]:
                                    edge.select = False
                    vert = og_vert
                    active_edge = og_edge
                    # print(vert)
                    split_verts = get_split_vert(vert, active_edge)
                    edges_to_deselect = []
                    if split_verts:

                        for split_vert in split_verts:

                            deselect = False

                            for e in split_vert.link_edges:
                                if e.select:
                                    (length, edges) = get_path_to_self(vert, e, split_vert)

                                    if length < 99999:
                                        deselect = True
                                    else:
                                        edges_to_deselect.append((length, edges))
                        edges_to_deselect = sorted(edges_to_deselect, key=lambda x: x[0])
                        if deselect:
                            for i, e in enumerate(edges_to_deselect):
                                for edge in e[1]:
                                    edge.select = False
                    context.tool_settings.mesh_select_mode = self.previous_selection_mode
                    context.active_object.data.update()
                else:
                    if len(active_edge.link_faces) == 1:
                        # angle=active_edge.calc_face_angle_signed()
                        linked_faces = len(active_edge.link_faces)
                        vert = active_edge.other_vert(active_edge.verts[0])
                        og_vert = vert
                        other_vert = active_edge.verts[0]
                        used = []
                        used.append(active_edge.verts[0])
                        used.append(active_edge.verts[1])
                        while vert:
                            # sorted_edge=sorted([e for e in vert.link_edges],key =lambda x:True if [f for f in x.link_faces if f in active_edge.link_faces] else False)
                            sorted_edge = sorted(
                                [e for e in vert.link_edges], key=lambda x: get_angle(x, active_edge, vert)
                            )

                            l = filter(lambda x: get_angle(x, active_edge, vert) < self.edge_threshold, sorted_edge)

                            for e in l:
                                if e != active_edge:
                                    if len(e.link_faces) == linked_faces:
                                        e.select = True
                                        active_edge = e
                                        vert = [v for v in e.verts if v != vert and v not in used]
                                        if vert:
                                            vert = vert[0]
                                            used.append(vert)
                                        break
                            else:
                                vert = None
                        vert = other_vert
                        active_edge = og_edge
                        while vert:
                            sorted_edge = sorted(
                                [e for e in vert.link_edges], key=lambda x: get_angle(x, active_edge, vert)
                            )

                            l = filter(lambda x: get_angle(x, active_edge, vert) < self.edge_threshold, sorted_edge)
                            for e in l:
                                if e != active_edge:
                                    if len(e.link_faces) == linked_faces:
                                        e.select = True
                                        active_edge = e
                                        vert = [v for v in e.verts if v != vert and v not in used]
                                        if vert:
                                            vert = vert[0]
                                            used.append(vert)
                                        break
                            else:
                                vert = None
                        selected_verts = [v for v in bm.verts if v.select]
                        vert = other_vert
                        active_edge = og_edge
                        # print(vert)
                        split_verts = get_split_vert(vert, active_edge)
                        edges_to_deselect = []
                        if split_verts:

                            for split_vert in split_verts:

                                deselect = False

                                for e in split_vert.link_edges:
                                    if e.select:
                                        (length, edges) = get_path_to_self(vert, e, split_vert)

                                        if length < 99999:
                                            deselect = True
                                        else:
                                            edges_to_deselect.append((length, edges))
                            edges_to_deselect = sorted(edges_to_deselect, key=lambda x: x[0])
                            if deselect:
                                for i, e in enumerate(edges_to_deselect):
                                    for edge in e[1]:
                                        edge.select = False
                        vert = og_vert
                        active_edge = og_edge
                        # print(vert)
                        split_verts = get_split_vert(vert, active_edge)
                        edges_to_deselect = []
                        if split_verts:

                            for split_vert in split_verts:

                                deselect = False

                                for e in split_vert.link_edges:
                                    if e.select:
                                        (length, edges) = get_path_to_self(vert, e, split_vert)

                                        if length < 99999:
                                            deselect = True
                                        else:
                                            edges_to_deselect.append((length, edges))
                            edges_to_deselect = sorted(edges_to_deselect, key=lambda x: x[0])
                            if deselect:
                                for i, e in enumerate(edges_to_deselect):
                                    for edge in e[1]:
                                        edge.select = False
                        context.tool_settings.mesh_select_mode = self.previous_selection_mode
                        context.active_object.data.update()
                    else:
                        self.report({"WARNING"}, "Edge has more than 2 adjacent faces")

        else:
            self.report({"WARNING"}, "Active element must be an edge!")
            bpy.context.tool_settings.mesh_select_mode = self.previous_selection_mode
            return {"PASS_THROUGH"}

        return {"FINISHED"}

    def invoke(self, context, event):
        self.active_edge = None
        self.previous_selection_mode = context.tool_settings.mesh_select_mode[:]
        if self.previous_selection_mode == (False, False, True):
            return bpy.ops.mesh.loop_select("INVOKE_DEFAULT")
            # return {'PASS_THROUGH'}
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.view3d.select("INVOKE_DEFAULT", extend=True)
        bm = bmesh.from_edit_mesh(context.active_object.data)

        if issubclass(type(bm.select_history.active), bmesh.types.BMEdge):
            self.active_edge = bm.select_history.active.index
            if bm.select_history.active.index == context.scene.nls_state.active_edge:
                if round(context.scene.nls_state.last_face_threshold, 2) == round(math.radians(180), 2):
                    face_threshold = math.radians(60)
                else:
                    face_threshold = math.radians(180)
                context.scene.nls_state.last_face_threshold = face_threshold
                self.face_threshold = face_threshold
            else:
                self.face_threshold = math.radians(60)
        return self.execute(context)


class LS_OT_Select_Face_Loop(bpy.types.Operator):
    bl_idname = "ls.selectfaceloop"
    bl_label = "Face Boundary Loop Select"
    bl_description = "Face Boundary Loop Select"
    bl_options = {"REGISTER", "UNDO"}
    select_coplanar: bpy.props.BoolProperty(default=True, name="Select Coplanar Faces")  # type: ignore
    threshold: bpy.props.FloatProperty(default=0.01, name="Threshold", min=0.001, max=1, options={"SKIP_SAVE"})  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):
        context.tool_settings.mesh_select_mode = False, False, True
        bm = bmesh.from_edit_mesh(context.active_object.data)
        for f in bm.faces:
            if f.index in self.selected_faces:
                f.select = True
        context.active_object.data.update()
        if self.select_coplanar:
            bpy.ops.mesh.faces_select_linked_flat(sharpness=self.threshold)
        bpy.ops.mesh.region_to_loop()
        context.tool_settings.mesh_select_mode = False, True, False
        loops = find_loops([edge for edge in bm.edges if edge.select])
        loops = sorted(loops, key=lambda x: len(x), reverse=True)

        if len(loops) > 1:
            for loop in loops[1:]:
                for edge in loop:
                    edge.select = False
        context.active_object.data.update()
        return {"FINISHED"}

    def invoke(self, context, event):

        if context.tool_settings.mesh_select_mode[:] == (False, True, False):
            context.tool_settings.mesh_select_mode = False, False, True
            bpy.ops.view3d.select("INVOKE_DEFAULT")
            bm = bmesh.from_edit_mesh(context.active_object.data)
            self.bm = bm
            self.selected_faces = [f.index for f in bm.faces if f.select]
            # return {'FINISHED'}
            return self.execute(context)
        return {"PASS_THROUGH"}


def get_split_vert(vert, active_edge):
    used = []
    split_verts = []
    while vert:
        sorted_edge = [e for e in vert.link_edges if e.select]
        if sorted_edge:

            for e in sorted_edge:
                if e != active_edge:
                    active_edge = e
                    vert = [v for v in e.verts if v != vert and v not in used]
                    if vert:
                        vert = vert[0]
                        used.append(vert)
                        if len([e for e in vert.link_edges if e.select]) == 3:
                            split_verts.append(vert)
                            break

                    break
            else:
                vert = None
        else:
            vert = None
    return split_verts


def get_path_to_self(vert, active_edge, split_vert):
    og_vert = vert
    # print("Target",vert)
    vert = active_edge.other_vert(split_vert)
    # print("OG",vert)
    used = []
    length = 0
    edges = [
        active_edge,
    ]
    visited_edges = []
    if vert == og_vert:
        return (active_edge.calc_length(), [])
    while vert:
        sorted_edge = [e for e in vert.link_edges if e.select]
        if sorted_edge:

            for e in sorted_edge:
                if e != active_edge and e not in visited_edges:
                    length += e.calc_length()
                    active_edge = e
                    edges.append(e)
                    visited_edges.append(e)
                    # print("Used",used)
                    # print("All",[v for v in e.verts])
                    vert = [v for v in e.verts if v != vert and v not in used]
                    # print("Verts",vert)
                    if vert and vert[0] == og_vert:
                        return (length, edges)
                    if vert:
                        vert = vert[0]
                        used.append(vert)

                    break
            else:
                vert = None
        else:
            vert = None
    return (9999999999, edges)


class NLS_State(bpy.types.PropertyGroup):
    active_edge: bpy.props.IntProperty()  # type: ignore
    last_face_threshold: bpy.props.FloatProperty(default=math.radians(180), name="Face Threshold")  # type: ignore


classes = (
    LS_OT_Select,
    # LSPrefs,
    LS_OT_Select_Face_Loop,
    NLS_State,
)
icon_collection = {}
addon_keymaps = []


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    bpy.types.Scene.nls_state = bpy.props.PointerProperty(type=NLS_State)
    km = kc.keymaps.new(name="Mesh", space_type="EMPTY")
    if kc:

        # kmi = km.keymap_items.new(
        #     "ls.select",
        #     type='D',
        #     value="PRESS",
        # )
        # addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "ls.select",
            type="LEFTMOUSE",
            value="DOUBLE_CLICK",
        )
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("ls.select", type="LEFTMOUSE", value="DOUBLE_CLICK", shift=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("ls.selectfaceloop", type="LEFTMOUSE", value="DOUBLE_CLICK", ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))


def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    # for km, kmi in addon_keymaps:
    #     km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
