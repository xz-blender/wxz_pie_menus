import bmesh
import bpy
import mathutils
from mathutils import Vector


class MESH_OT_inset_cl(bpy.types.Operator):
    """Inset in een polygon"""

    bl_idname = "mesh.inset_clipper"
    bl_label = "Inset clipper"
    bl_options = {"REGISTER", "UNDO"}

    dikte: bpy.props.FloatProperty(
        name="dikte",
        default=-0.4,
        subtype="DISTANCE",
    )  # type: ignore
    corner_shape: bpy.props.EnumProperty(
        name="Corner Shape",
        items=[("JT_ROUND", "Round", ""), ("JT_SQUARE", "Square", ""), ("JT_MITER", "Miter", "")],
        default="JT_ROUND",
        description="Shape of corners generated by offsetting",
    )  # type: ignore

    arc_t: bpy.props.FloatProperty(name="Arc Tollerance", default=2, min=0)  # type: ignore

    def execute(self, context):
        try:
            import pyclipper  # type: ignore

        except ImportError:
            self.report({"ERROR"}, "Please install dependencies in the Preferences panel.")
            return {"FINISHED"}
        factor = 100000000000000
        Z_richting = Vector((0, 0, 1))
        rand_breedte = self.dikte * factor
        corner_shape = self.corner_shape
        # arc_t = 1/(self.arc_t+0.001)*10000000000
        arc_t = self.arc_t

        class Voorbereiden:

            # Een gekozen vlak tot een nieuw object maken om te bewerken
            def vlak_appart(self):
                geselecteerd = bpy.context.selected_objects
                actief_oud = bpy.context.active_object
                # bpy.ops.mesh.duplicate()
                bpy.ops.mesh.separate(type="SELECTED")

                bpy.ops.object.editmode_toggle()
                laatste = bpy.context.selected_objects[-1]
                bpy.ops.object.select_all(action="DESELECT")
                laatste.select_set(True)
                bpy.context.view_layer.objects.active = laatste
                bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
                ob = bpy.context.object
                pos_oud = ob.location.copy()
                ob.location = (0, 0, 0)
                return (pos_oud, actief_oud)

            # Het object wat gemaakt is(moet een vlak zijn ) plat leggen voor pyclipper
            def plat_leggen(self, ob):

                bpy.ops.object.mode_set(mode="EDIT")
                me = ob.data
                bm = bmesh.from_edit_mesh(me)
                bm.faces.ensure_lookup_table()
                f = bm.faces[0]
                normaal = f.normal
                bpy.context.scene["normaal_vlak"] = normaal
                verschil = normaal.rotation_difference(Z_richting)
                matrix_naar_xy = verschil.to_matrix().to_4x4()
                matrix_inv = matrix_naar_xy.inverted()
                for v in bm.verts:
                    v.co = v.co @ matrix_inv
                bpy.ops.mesh.select_all(action="SELECT")

                bpy.ops.mesh.normals_make_consistent(inside=False)

                return matrix_naar_xy

            # Het uiteindelijke bewerkte vlak weer terug draaien en toevoegen aan het oorspronkelijke object
            def terug_draaien(self, ob, matrix, pos_oud, moeder_object):
                me = ob.data
                bm = bmesh.from_edit_mesh(me)

                for v in bm.verts:
                    v.co = v.co @ matrix
                ob.location = pos_oud
                bpy.ops.object.editmode_toggle()
                moeder_object.select_set(True)
                bpy.context.view_layer.objects.active = moeder_object
                bpy.ops.object.join()
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.remove_doubles()
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(type="FACE")

        class Bewerken:

            # van het vlak de edges bepalen
            def vlak_maken(self, bm):
                # bpy.ops.mesh.duplicate()
                ges_edges = []
                for e in bm.edges:
                    if e.select:
                        ges_edges.append(e)
                return ges_edges

            # de punten van het vlak op volgorde leggen, dus met de klok mee of tegen de klok in
            def punten_op_volgorde(self, bm, ges_edges):
                punten = []
                lijn = ges_edges[0]
                punt = lijn.verts[0]
                eerste_punt = punt
                punten.append(punt)
                ander_punt = lijn.other_vert(punt)
                punten.append(ander_punt)
                lijnen = ander_punt.link_edges
                if lijnen[0] == lijn:
                    nieuwe_lijn = lijnen[1]
                else:
                    nieuwe_lijn = lijnen[0]

                doorgaan = True
                teller = 0
                while doorgaan:
                    teller += 1
                    punt = ander_punt
                    if punt == eerste_punt:
                        break
                    lijn = nieuwe_lijn
                    ander_punt = lijn.other_vert(punt)
                    punten.append(punt)
                    lijnen = ander_punt.link_edges
                    if lijnen[0] == lijn:
                        nieuwe_lijn = lijnen[1]
                    else:
                        nieuwe_lijn = lijnen[0]
                    if teller > 100000:
                        print("teller groter dan 10000")
                        doorgaan = False

                return punten

            # een 2D array  maken en de coordinaten vergroten omdat pyclipper niet met float werkt
            def punten_naar_2D(self, punten):
                punten_2d = []
                for v in punten:
                    if v.select:
                        x = v.co[0] * factor
                        y = v.co[1] * factor

                        punt = (x, y)
                        punten_2d.append(punt)
                punten_2d = tuple(punten_2d)
                return punten_2d

            # de eigenlijke offset
            def clipper_offset(self, punten_2d, rand_breedte):
                subj = punten_2d
                pco = pyclipper.PyclipperOffset()
                pco.ArcTolerance = arc_t
                jt = pyclipper.JT_ROUND

                if corner_shape == "JT_SQUARE":
                    jt = pyclipper.JT_SQUARE
                elif corner_shape == "JT_MITER":
                    jt = pyclipper.JT_MITER

                pco.AddPath(subj, jt, pyclipper.ET_CLOSEDPOLYGON)
                # JT_ROUND   CLOSEDPOLYGON
                # JT_SQUARE, JT_MITTER
                solution = pco.Execute(rand_breedte)
                return solution

            # weer 3_D punten maken van de oplossing
            def terug_naar_3d(self, oplossing):
                coord_3D = []
                for s in oplossing:
                    naar_coord = []
                    for w in s:
                        x = w[0] / factor
                        y = w[1] / factor

                        coord = Vector((x, y, 0))
                        naar_coord.append(coord)
                    coord_3D.append(naar_coord)
                return coord_3D

            # vlakke meshes maken van de coordinaten
            def mesh_maken(self, coord_3D):
                alle_vertices = []

                for blok in coord_3D:

                    vertices = []
                    for c in blok:
                        v = bm.verts.new(c)
                        vertices.append(v)

                    for e in range(1, len(vertices)):
                        v1 = vertices[e - 1]
                        v2 = vertices[e]
                        bm.edges.new((v1, v2))

                    bm.edges.new((v2, vertices[0]))
                    bmesh.update_edit_mesh(me, loop_triangles=True)
                    alle_vertices = alle_vertices + vertices
                return alle_vertices

            # van de inset lijnen 3_d objecten maken om een boolean te kunnen uitvoeren met het vlak
            def vlak_maken_uitrekken(self, vertices):
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(type="VERT")
                for v in vertices:
                    v.select_set(True)

                bpy.ops.mesh.select_linked()
                bpy.ops.mesh.select_mode(type="EDGE")

                bpy.ops.mesh.edge_face_add()

                bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 1), "orient_type": "NORMAL"})
                bpy.ops.mesh.select_linked()

                bpy.ops.transform.resize(value=(1, 1, 1.27509), orient_type="GLOBAL")
                selectie = []
                for v in bm.verts:
                    if v.select:
                        selectie.append(v)

                # de boolean opdracht
                bpy.ops.mesh.intersect(solver="FAST")
                bpy.ops.mesh.select_all(action="DESELECT")
                bpy.ops.mesh.select_mode(type="VERT")
                for v in selectie:
                    v.select_set(True)

                bpy.ops.mesh.select_linked()
                # bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.delete(type="VERT")

        ###############################################################
        ############  PROGRAMMA   #####################################
        ###############################################################

        vb = Voorbereiden()
        bew = Bewerken()
        pos_oud, moeder_object = vb.vlak_appart()
        ob = bpy.context.object
        matrix = vb.plat_leggen(ob)

        ob = bpy.context.object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)

        ges_edges = bew.vlak_maken(bm)

        punten = bew.punten_op_volgorde(bm, ges_edges)
        punten_2d = bew.punten_naar_2D(punten)

        oplossing = bew.clipper_offset(punten_2d, rand_breedte)
        coord_3D = bew.terug_naar_3d(oplossing)
        alle_vertices = bew.mesh_maken(coord_3D)
        bew.vlak_maken_uitrekken(alle_vertices)
        ob = bpy.context.object
        vb.terug_draaien(ob, matrix, pos_oud, moeder_object)

        return {"FINISHED"}