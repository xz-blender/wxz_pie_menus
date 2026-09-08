"""Run with blender --background --factory-startup --python-exit-code 1 --python this_file."""

import importlib
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
import xml.etree.ElementTree as ET

import bpy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "parts_addons"))
addon = importlib.import_module("outline_to_svg")
assert Path(addon.__file__).resolve() == ROOT / "parts_addons" / "outline_to_svg" / "__init__.py"

with patch.object(addon.ui_helpers, "pop_message") as popup:
    addon.register()
    assert not popup.called, popup.call_args
    assert not addon.restart_required, "Outline To SVG failed to load"

from shapely.geometry import Polygon
from outline_to_svg.process_geo import poly_union
from outline_to_svg.write_to_svg import SvgWriter

try:
    assert addon.operators.EXPORT_OT_Export_Outline_SVG.is_registered
    assert addon.ui.VIEW3D_PT_Outline_To_SVG.is_registered
    assert hasattr(bpy.types.Scene, "outline_to_svg_props")
    polygons = poly_union(
        [Polygon([(0, 0), (2, 0), (2, 1), (0, 1)]), Polygon([(1, 0), (3, 0), (3, 1), (1, 1)])],
        0.00001,
    )
    assert len(polygons) == 1
    assert abs(polygons[0].area - 3.0) < 1e-6
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "outline.svg"
        with SvgWriter(output) as writer:
            writer.write_header(3, 1, "")
            writer.write_polygons(polygons)
        svg = ET.parse(output).getroot()
        assert svg.tag == "{http://www.w3.org/2000/svg}svg"
        assert svg.find(".//{http://www.w3.org/2000/svg}path") is not None
    print("PASS: Outline To SVG loads, registers, unions polygons, and writes SVG")
finally:
    addon.unregister()

assert not hasattr(bpy.types.Scene, "outline_to_svg_props")
addon.register()
addon.unregister()
print("PASS: Outline To SVG can be enabled again after unregistering")
