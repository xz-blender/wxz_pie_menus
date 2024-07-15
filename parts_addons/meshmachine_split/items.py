from mathutils import Vector
fuse_method_items = [("FUSE", "Fuse", ""),
                     ("BRIDGE", "Bridge", "")]
handle_method_items=[("FACE", "Face", ""),
                     ("LOOP", "Loop", "")]
tension_preset_items = [("CUSTOM", "Custom", ""),
                        ("0.55", "0.55", ""),
                        ("0.7", "0.7", ""),
                        ("1", "1", ""),
                        ("1.33", "1.33", "")]
boolean_solver_items = [("FAST", "Fast", ""),
                        ("EXACT", "Exact", "")]
turn_items = [("1", "1", ""),
              ("2", "2", ""),
              ("3", "3", "")]
side_selection_items = [("A", "A", ""),
                        ("B", "B", "")]
loop_mapping_dict = {"NEAREST FACE": "POLYINTERP_NEAREST",
                     "PROJECTED": "POLYINTERP_LNORPROJ",
                     "NEAREST NORMAL": "NEAREST_NORMAL",
                     "NEAREST POLY NORMAL": "NEAREST_POLYNOR"}
axis_mapping_dict = {"X": Vector((1, 0, 0)),
                     "Y": Vector((0, 1, 0)),
                     "Z": Vector((0, 0, 1))}
direction_items = [("POSITIVE", "+ to -", ""),
                   ("NEGATIVE", "- to +", "")]
axis_items = [("X", "X", ""),
              ("Y", "Y", ""),
              ("Z", "Z", "")]
custom_normal_mirror_method_items = [("INDEX", "Index", ""),
                                     ("LOCATION", "Location", "")]

fix_center_method_items = [("CLEAR", "Clear Normals", ""),
                           ("TRANSFER", "Transfer Normals", "")]