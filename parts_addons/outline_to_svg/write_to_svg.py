from typing import Union, Tuple
from pathlib import Path
from contextlib import AbstractContextManager
import shapely
from shapely.geometry.multipolygon import MultiPolygon

class SvgWriter:
    def __init__(self, filepath: Union[str, Path], mode: str = "w"):
        if mode not in "wa":
            raise ValueError("invalid svg write mode")
        self.mode = mode
        self.filepath = filepath

    def __enter__(self):
        if self.mode == "a" and self.filepath.exists():
            temp_path = self.filepath.with_suffix(".temp")
            with open(self.filepath, 'r') as init_file:
                with open(temp_path, 'w') as newfile:
                    for line in init_file:
                        if line == "</svg>":
                            continue
                        newfile.write(line)

            self.filepath.unlink()
            temp_path.rename(self.filepath)
            self.svg_file = open(self.filepath, mode="a")
        else:
            self.svg_file = open(self.filepath, mode="w")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Write footer and close
        self.svg_file.write(r"</svg>")
        self.svg_file.close()

    def write_header(self, width, height, units: str):
        # width = abs(bbox_a[0] - bbox_b[0])
        # height = abs(bbox_a[1] - bbox_b[1])

        self.svg_file.writelines(
            [
                '<?xml version="1.0" standalone="no"?>\n',
                '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n',
                '  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n',
                f'<svg width="{width}{units}" height="{height}{units}" ',
                f'viewBox="{0} {0} {width} {height}"\n',
                '     xmlns="http://www.w3.org/2000/svg" version="1.1">\n',
                "<desc>Outline to SVG export</desc>\n",
            ]
        )

    def write_polygons(self, polygons, fill: str = "000000", grouped: bool = True, holes_as_group: bool = False):
        """Shapely polygons, color in hex without leading hash"""
        # TODO: Handling of second group is ugly, fix it

        second_group = None

        if holes_as_group:
            exteriors = []
            holes = []

            for polygon in polygons:
                # Handle multipolygons
                if isinstance(polygon, MultiPolygon):
                    polysets = polygon.geoms
                else:
                    polysets = [polygon]
                
                for polyset in polysets:
                    exteriors.append(shapely.Polygon(polyset.exterior.coords))
                    for interior in polyset.interiors:
                        holes.append(shapely.Polygon(interior.coords))
            polygons = exteriors
            second_group = holes

        if grouped:
            self.svg_file.write("<g>\n")

        for poly in polygons:
            poly_str = poly.svg()

            # Remove stroke
            poly_str = poly_str.replace('stroke-width="2.0"', 'stroke-width="0"')
            # Max Opacity
            poly_str = poly_str.replace('opacity="0.6"', 'opacity="1"')
            # Color Black
            poly_str = poly_str.replace('fill="#66cc99"', f'fill="#{fill}"')

            # Write line
            self.svg_file.write("".join(["\t", poly_str, "\n"]))

        if grouped:
            self.svg_file.write("</g>\n")

        if second_group is not None:
            offset_fill = list(fill)
            offset_fill[-2] = "9"
            # offset_fill[-4] = "b"
            # offset_fill[-6] = "c"
            offset_fill = "".join(offset_fill)

            if grouped:
                self.svg_file.write("<g>\n")

            for poly in second_group:
                poly_str = poly.svg()

                # Remove stroke
                poly_str = poly_str.replace('stroke-width="2.0"', 'stroke-width="0"')
                # Max Opacity
                poly_str = poly_str.replace('opacity="0.6"', 'opacity="1"')
                # Color Black
                poly_str = poly_str.replace('fill="#66cc99"', f'fill="#{offset_fill}"')

                # Write line
                self.svg_file.write("".join(["\t", poly_str, "\n"]))

            if grouped:
                self.svg_file.write("</g>\n")
