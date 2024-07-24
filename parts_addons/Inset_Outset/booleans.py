import bmesh
import bpy
from mathutils import Vector

factor = 100000000000000


class MESH_OT_booleans(bpy.types.Operator):
    """Chose 2 ore more faces that overlap, the last chosen is the 'tool'"""

    bl_idname = "mesh.tiem_bools"  # komy in de afdeling mesh en heet planken
    bl_label = "Booleans 2D"
    bl_options = {"REGISTER", "UNDO"}  # nodig voor menu in beeld te krijgen

    keuze: bpy.props.EnumProperty(
        name="Bool type",
        items=[("opl_1", "union", ""), ("opl_2", "difference", ""), ("opl_3", "XOR", ""), ("opl_4", "intersect", "")],
        default="opl_1",
        description="Shape of corners generated by offsetting",
    )  # type: ignore

    def execute(self, context):
        try:
            import pyclipper  # type: ignore
        except ImportError:
            self.report({"ERROR"}, "Please install dependencies in the Preferences panel.")
            return {"FINISHED"}
        keuze = self.keuze

        def selectie_bepalen(bm):
            # de selectie van vlakken, het laatst geselecteerde vlak is het clip vlak
            # het clip vlak is het knipvlak wat wordt toegepast op de andere vlakken
            hist = bm.select_history
            if len(hist) == 0:
                print("Er is niets geselecteedrd")
                return False
            if not isinstance(hist[-1], bmesh.types.BMFace):
                print("Er is geen vlak geselecteerd")
                return False
            clip_vlak = hist[-1]
            subj_vlakken = []
            for v in bm.faces:
                if v.select and v != clip_vlak:
                    subj_vlakken.append(v)
            if len(subj_vlakken) == 0:
                print("geen subj vlakken geselecteerd")
                return False

            bpy.ops.mesh.edge_split(type="EDGE")
            ges_vlakken = [clip_vlak, subj_vlakken]
            # bpy.ops.mesh.select_all(action='DESELECT')

            return ges_vlakken

        def plat_leggen(bm, g):
            # alle vlakken platleggen, maar niet verplaatsen naar nul
            Z_richting = Vector((0, 0, 1))
            bm.faces.ensure_lookup_table()
            clipvlak = g[0]
            subj_vlakken = g[1]

            normaal = clipvlak.normal
            verschil = normaal.rotation_difference(Z_richting)
            matrix_naar_xy = verschil.to_matrix().to_4x4()
            matrix_inv = matrix_naar_xy.inverted()
            for v in clipvlak.verts:
                v.co = v.co @ matrix_inv

            for f in subj_vlakken:
                for v in f.verts:
                    v.co = v.co @ matrix_inv

            hoogte_z_loc = clipvlak.verts[0].co[2]
            bm.faces.ensure_lookup_table()
            bmesh.update_edit_mesh(me)
            return (matrix_naar_xy, hoogte_z_loc)

        def op_volgorde(vlak, bm):

            # lijst maken van de coordinaten op volgorde in de rand
            # en omzetten naar coordinaten
            punten = []
            for p in vlak.verts:
                punten.append(p)

            bm.edges.ensure_lookup_table()

            eerste_punt = punten[0]
            lijn = eerste_punt.link_edges[0]
            doorgaan = True

            punt = eerste_punt
            punten_op_volgorde = [punt.co]

            while doorgaan:
                ander_punt = lijn.other_vert(punt)
                if ander_punt == eerste_punt:
                    break
                punten_op_volgorde.append(ander_punt.co)
                lijnen = ander_punt.link_edges

                if lijnen[0] == lijn:
                    lijn = lijnen[1]
                else:
                    lijn = lijnen[0]
                punt = ander_punt
            # bpy.ops.object.editmode_toggle()
            return punten_op_volgorde

        def punten_2D(punten_3d):
            # van alle 3D coordinaten een lijst maken van 2D integers
            punten = []
            for p in punten_3d:
                cx = int(p[0] * factor)
                cy = int(p[1] * factor)

                punt = (cx, cy)
                punten.append(punt)

            return punten

        def clipper_uitvoeren(clip, subj):

            pc = pyclipper.Pyclipper()
            pc.AddPath(clip, pyclipper.PT_CLIP, True)
            pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)

            # solution = pc.Execute(pyclipper.CT_UNION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
            if keuze == "opl_1":
                waarde = pyclipper.CT_UNION
            if keuze == "opl_2":
                waarde = pyclipper.CT_DIFFERENCE
            if keuze == "opl_3":
                waarde = pyclipper.CT_XOR
            if keuze == "opl_4":
                waarde = pyclipper.CT_INTERSECTION

            solution = pc.Execute(waarde, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)

            return solution

        def figuur_maken(solution):
            # van de clipper gegenereerde lijst weer een lijst van 3D float coordinaten maken

            figuren = []
            for s in solution:
                fig = []
                for f in s:
                    x = f[0] / factor
                    y = f[1] / factor
                    samen = (x, y, 0)
                    fig.append(samen)
                figuren.append(fig)

            return figuren

        def figuren_terugdraaien(hoogte_z_loc, ob, figuren, matrix):
            # fiuren terug draaien, ze moeten eers op de hoogte komen van het oorspronkelijke
            # gedraaide vlak, dat is de lokale z hoogte

            hoogte_z_loc = Vector((0, 0, hoogte_z_loc))
            figuren_nieuw = []
            for figuur in figuren:
                figuur_nieuw = []
                for v in figuur:
                    vec = Vector((v)) + hoogte_z_loc
                    vec = vec @ matrix
                    v = tuple(vec)
                    figuur_nieuw.append(v)
                figuren_nieuw.append(figuur_nieuw)
            return figuren_nieuw

        def figuren_teken(figuren_data, loc):

            bpy.ops.mesh.delete(type="FACE")
            ob = bpy.context.object
            me = ob.data
            bm = bmesh.from_edit_mesh(me)
            for f in figuren_data:
                vertices = []
                for p in f:
                    v = bm.verts.new(p)
                    vertices.append(v)

                for e in range(1, len(vertices)):
                    v1 = vertices[e - 1]
                    v2 = vertices[e]
                    e = bm.edges.new((v1, v2))
                    e.select_set(True)
                e = bm.edges.new((v2, vertices[0]))
                e.select_set(True)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
            # bpy.ops.mesh.edge_face_add()
            bm.verts.ensure_lookup_table()

            # bmesh.update_edit_mesh(me)
            bpy.ops.mesh.fill()
            bpy.ops.mesh.dissolve_limited()

        ###############################################################
        ############  PROGRAMMA   #####################################
        ###############################################################
        # bpy.ops.mesh.edge_split(type='EDGE')
        ob = bpy.context.object
        loc = ob.location
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        selectie_groep = selectie_bepalen(bm)
        if selectie_groep:
            matrix_terug, hoogte_z_loc = plat_leggen(bm, selectie_groep)

            punten_clip = op_volgorde(selectie_groep[0], bm)
            punten_clip = punten_2D(punten_clip)
            punten_subj = []
            for s in selectie_groep[1]:
                tijd_3D = op_volgorde(s, bm)
                punten_subj.append(tuple(punten_2D(tijd_3D)))

            solution = clipper_uitvoeren(punten_clip, punten_subj)
            figuren_data = figuur_maken(solution)  # weer terug naar 3D coordinaten en weer delen door factor

            figuren_nieuw = figuren_terugdraaien(hoogte_z_loc, ob, figuren_data, matrix_terug)
            figuren_teken(figuren_nieuw, loc)
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")

            # figuren_teken(figuren_data,loc)

        else:
            print("niet goed")

        return {"FINISHED"}