# Built-ins
import os
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from itertools import repeat, chain
from typing import Any, Dict, List, Tuple
from pathlib import Path
from random import random
import logging

import bpy
from bpy.types import Context
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.utils import register_class, unregister_class
from mathutils import Vector, Color, Matrix
# import shapely
# from shapely.geometry.multipolygon import MultiPolygon

from . import get_geo
from . import write_to_svg
from .write_to_svg import SvgWriter
from . import process_geo
from . import filtering
from .consts import (
    METRIC_UNITS,
    IMPERIAL_UNITS,
    OUTLINE_GROUPING_ENUM,
    NODE_COLOR_SOURCES,
)

import logging
logger = logging.getLogger(f"{__name__}.rigging")
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

class EXPORT_OT_Export_Outline_SVG(bpy.types.Operator):
    bl_idname = "export_mesh.export_outline_svg"
    bl_label = "Export Outline to SVG"
    bl_options = {"REGISTER", "INTERNAL"}

    filepath: StringProperty(name="Output Path", subtype="FILE_PATH")
    grouping: EnumProperty(items=OUTLINE_GROUPING_ENUM)
    only_visible: BoolProperty(name="Only Visible", default=False)
    unique_colors: BoolProperty(default=False)
    holes_as_group: BoolProperty(name="Holes as Group", default=False)
    hole_exclusion: StringProperty(name="Hole Exclusion")
    append_mode: BoolProperty(name="Append Mode", default=False)

    @classmethod
    def poll(cls, context):
        return all((len(context.selected_objects) != 0, context.area.type == "VIEW_3D"))

    def region_perspective_type(self, context):
        """return one of ["PERSP", "ORTHO", "CAMERA"]"""
        area = context.area
        rv3d = area.spaces[0].region_3d
        return rv3d.view_perspective

    def is_ortho_projector(self, context):
        if self.region_perspective_type(context) == "ORTHO":
            return True
        if self.region_perspective_type(context) == "CAMERA":
            return context.scene.camera.data.type == "ORTHO"
        return False

    def is_cam_projection(self, context: Context):
        return self.region_perspective_type(context) == "CAMERA"

    def get_units_string(self, context):
        user_units = context.scene.unit_settings.length_unit
        unit_sys = context.scene.unit_settings.system
        if unit_sys == "METRIC" and user_units in METRIC_UNITS.keys():
            return METRIC_UNITS[user_units]
        elif unit_sys == "IMPERIAL" and user_units in IMPERIAL_UNITS.keys():
            return IMPERIAL_UNITS[user_units]
        else:
            return ""

    def validate_filepath(self):
        if self.filepath == "":
            self.report({"WARNING"}, "No filepath selected")
            return {"CANCELLED"}

        # Ensure valid filepath
        self.filepath = bpy.path.abspath(self.filepath)

        if os.path.isdir(self.filepath):
            self.filepath = os.path.join(self.filepath, "svg_export.svg")

        self.filepath = bpy.path.ensure_ext(self.filepath, ".svg")

    @classmethod
    def random_hex_color(cls):
        rgb = [random() for _ in range(3)]
        return cls.rgb_to_hex(rgb)

    @staticmethod
    def color_band(n: int):
        step_size = 1.0 / n
        hues = [step_size * step for step in range(n)]
        colors = []
        white = Color((1, 1, 1))
        for hue in hues:
            c = white.copy()
            c.hsv = (hue, 0.9, 0.9)
            colors.append(c)
        return colors

    @classmethod
    def find_material_color_to_write(cls, material) -> str:
        """Return appropriate material color as hex string"""

        def rgba_to_rgb(rgba):
            return rgba[:3]

        try:
            nodes = material.node_tree.nodes
            output_nodes = [node for node in nodes if node.type == "OUTPUT_MATERIAL"]
            active_output = next(
                (node for node in output_nodes if node.is_active_output)
            )
            linked_node = active_output.inputs["Surface"].links[0].from_node
            color_attr = NODE_COLOR_SOURCES[linked_node.type]
            rgba = linked_node.inputs[color_attr].default_value
        except Exception as e:
            rgba = material.diffuse_color[:]

        rgb = rgba_to_rgb(rgba)
        return cls.rgb_to_hex(rgb)

    @staticmethod
    def rgb_to_hex(rgb: Color):
        def _convert_val(val):
            scaled = int(val * 255)
            hex_val = hex(scaled).split("x")[-1].zfill(2)
            return hex_val

        hex_vals = map(_convert_val, rgb)
        hex_vals = list(hex_vals)
        return "".join(hex_vals)

    def _get_inverted_view_rot(self, context: Context) -> Matrix:
        area = context.area
        rv3d = area.spaces[0].region_3d
        view_rotation = rv3d.view_rotation
        return view_rotation.to_matrix().to_4x4().inverted()

    def _identify_target_groups(self, context) -> Tuple[List[bpy.types.Object], List[bpy.types.Object]]:
        """ Split targets between main grouping and hole exclusion """
        valid_target_types = (
            "MESH",
            "SURFACE",
            "CURVE",
            "META",
            "FONT",
        )

        valid_targets = [o for o in context.selected_objects if o.type in valid_target_types]
        targets = []
        group_excepted_targets = []

        if not valid_target_types:
            self.report({"WARNING"}, "No valid targets selected")
            return {"CANCELLED"}

        if self.holes_as_group and self.hole_exclusion != "":
            exclusion_substrings = self.hole_exclusion.split(',')
            for target in valid_targets:
                for s in exclusion_substrings:
                    if s in target.name:
                        group_excepted_targets.append(target)
                        break
                else:
                    targets.append(target)
        else:
            targets = valid_targets
        
        return targets, group_excepted_targets

    def _group_targets(self, targets: List[bpy.types.Object]) -> Dict[Any, List[bpy.types.Object]]:
        """ Group target objects by grouping property"""
        if self.grouping == "MATERIAL":
            target_collections = filtering.group_by_material(targets)
        elif self.grouping == "COLLECTION":
            target_collections = filtering.group_by_collection(targets)
        else:
            target_collections = self._create_none_grouping(targets)
        return target_collections

    def _create_none_grouping(self, targets) -> Dict[Any, List[bpy.types.Object]]:
        """ Create a dict of index: target """
        return {f"{indx}": target for indx, target in enumerate(targets)}

    def _face_sets_from_collection(self, context: Context, collections, force_none_group = False):
        inv_view_rot = self._get_inverted_view_rot(context)
        logger.debug(f"{bpy.app.version}: Inverted view rotation, face sets from collection: {inv_view_rot}")

        face_sets = defaultdict(list)
        for grouping, object_set in collections.items():
            if force_none_group:
                material_mask = None
            else:
                if self.grouping in ("NONE", "COLLECTION"):
                    material_mask = None
                else:
                    material_mask = grouping

            if self.is_ortho_projector(context):
                flattened = get_geo.get_flattened_faces(
                    context,
                    object_set,
                    xform=inv_view_rot,
                    only_visible=self.only_visible,
                    material_mask=material_mask,
                )
            else:
                logger.debug(f"{bpy.app.version}: Non ortho export")
                flattened = get_geo.get_flattened_faces(
                    context,
                    object_set,
                    screenspace=True,
                    only_visible=self.only_visible,
                    material_mask=material_mask,
                )
            face_sets[grouping] = flattened
        return face_sets

    def execute(self, context: bpy.types.Context):
        self.validate_filepath()
        targets, group_excepted_targets = self._identify_target_groups(context)

        # Create target Groups
        target_collections = self._group_targets(targets)
        group_excepted_collections = self._create_none_grouping(group_excepted_targets)

        inv_view_rot = self._get_inverted_view_rot(context)
        logger.debug(f"{bpy.app.version}Inverted view rotation: {inv_view_rot}")

        target_face_sets = self._face_sets_from_collection(context, target_collections)
        group_except_face_sets = self._face_sets_from_collection(context, group_excepted_collections, True)

        # face_sets = defaultdict(list)
        # for grouping, object_set in target_collections.items():
        #     if self.grouping in ("NONE", "COLLECTION"):
        #         material_mask = None
        #     else:
        #         material_mask = grouping

        #     if self.is_ortho_projector(context):
        #         flattened = get_geo.get_flattened_faces(
        #             context,
        #             object_set,
        #             xform=inv_view_rot,
        #             only_visible=self.only_visible,
        #             material_mask=material_mask,
        #         )
        #     else:
        #         flattened = get_geo.get_flattened_faces(
        #             context,
        #             object_set,
        #             screenspace=True,
        #             only_visible=self.only_visible,
        #             material_mask=material_mask,
        #         )
        #     face_sets[grouping] = flattened

        all_points = list()
        for face_set in target_face_sets.values():
            points = chain.from_iterable(face_set)
            all_points.extend(points)

        for face_set in group_except_face_sets.values():
            points = chain.from_iterable(face_set)
            all_points.extend(points)
        
        # Get point bounds
        min_xy, max_xy = get_geo.vector_bbox(all_points)
        logger.debug(f"{bpy.app.version}: Point bbox: {min_xy - max_xy}, min:{min_xy} max:{max_xy}")

        # Set origin
        if self.is_cam_projection(context):
            if self.is_ortho_projector(context):
                view_frame = get_geo.get_camera_frame(
                    context, inv_view_rot, flatten=True
                )
                cam_min_xy, cam_max_xy = get_geo.vector_bbox(view_frame)
            else:
                view_frame = get_geo.get_camera_frame(context, flatten=False)
                logger.debug(f"view frame: {view_frame}")
                view_min, view_max = view_frame[2], view_frame[0]
                logger.debug(f"view frame: {(view_min, view_max)}")
                screenspace_viewframe = [
                    get_geo.get_point_in_screenspace(v, context)
                    for v in (view_min, view_max)
                ]
                cam_min_xy, cam_max_xy = screenspace_viewframe
                logger.debug(f"screenspace_viewframe: {screenspace_viewframe}")

            offset = Vector((0, 0))
            offset.x = cam_min_xy.x * -1
            offset.y = cam_max_xy.y
            loc_correction = offset
        else:
            loc_correction = min_xy * -1

        # Make position and origin relative
        for v in all_points:
            v += loc_correction
        
        # Convert targets to shapely polygons
        target_poly_sets = [
            get_geo.faces_to_polygons(face_set) for face_set in target_face_sets.values()
        ]
        group_excepted_target_poly_sets = [
            get_geo.faces_to_polygons(face_set) for face_set in group_except_face_sets.values()
        ]

        # Perform union operation
        union_buffer = 0.00001
        with ThreadPoolExecutor() as executor:
            target_polygroups = executor.map(process_geo.poly_union, target_poly_sets, repeat(union_buffer))

        with ThreadPoolExecutor() as executor:
            excepted_target_polygroups = executor.map(process_geo.poly_union, group_excepted_target_poly_sets, repeat(union_buffer))

        # Flatten merged face sets
        target_polygroups = list(target_polygroups)
        excepted_target_polygroups = list(excepted_target_polygroups)

        # Determine output dimensions
        if not self.is_cam_projection(context):
            width = abs(min_xy.x - max_xy.x)
            height = abs(min_xy.y - max_xy.y)
        else:
            width = abs(cam_min_xy.x - cam_max_xy.x)
            height = abs(cam_min_xy.y - cam_max_xy.y)

        if self.grouping == "MATERIAL":
            colors = [self.find_material_color_to_write(mat) for mat in target_collections]
        elif self.unique_colors:
            n_colors = len(target_polygroups) + len(excepted_target_polygroups) + 1
            colors = self.color_band(n_colors)
            colors = (self.rgb_to_hex(c) for c in colors)
        else:
            colors = repeat("000000")

        write_mode = "a" if self.append_mode else "w"
        with SvgWriter(Path(self.filepath), write_mode) as svg_output:
            if write_mode == "w":
                units = self.get_units_string(context)
                svg_output.write_header(width, height, units)

            for color, polygroup in zip(colors, target_polygroups):
                svg_output.write_polygons(polygroup, color, True, self.holes_as_group)

            # Handle hole exception objects
            if self.grouping == "MATERIAL" and self.unique_colors:
                n_colors = len(excepted_target_polygroups) + 1
                colors = self.color_band(n_colors)
                colors = (self.rgb_to_hex(c) for c in colors)
            elif self.grouping == "MATERIAL":
                colors = repeat("000000")
            for color, polygroup in zip(colors, excepted_target_polygroups):
                svg_output.write_polygons(polygroup, color)

        return {"FINISHED"}


def register():
    register_class(EXPORT_OT_Export_Outline_SVG)


def unregister():
    unregister_class(EXPORT_OT_Export_Outline_SVG)
