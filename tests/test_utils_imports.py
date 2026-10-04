"""Shared utility imports used by pie menus, without a Blender installation."""

import importlib
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
PACKAGE = "bl_ext.blender4_com.wxz_pie_menus"


class UtilsImportTests(unittest.TestCase):
    def test_pie_menu_can_import_keymap_helper(self):
        package = ModuleType(PACKAGE)
        package.__package__ = PACKAGE
        package.__path__ = [str(ROOT)]
        bpy = ModuleType("bpy")
        bpy_types = ModuleType("bpy.types")
        bpy_types.PointerProperty = object
        bpy_types.PropertyGroup = object
        handlers = ModuleType("bpy.app.handlers")
        handlers.persistent = lambda function: function
        mathutils = ModuleType("mathutils")
        for name in ("Euler", "Matrix", "Vector"):
            setattr(mathutils, name, type(name, (), {}))

        modules = {
            PACKAGE: package,
            "bpy": bpy,
            "bpy.types": bpy_types,
            "bpy.app.handlers": handlers,
            "mathutils": mathutils,
        }
        with patch.dict(sys.modules, modules):
            namespace = {"__package__": PACKAGE + ".pie"}
            exec("from ..utils import extend_keymaps_list", namespace)
            items = importlib.import_module(PACKAGE + ".items")
            keymaps = [(object(), object()), (object(), object())]
            namespace["extend_keymaps_list"](keymaps)
            self.assertEqual(items.All_Pie_keymaps, keymaps)


if __name__ == "__main__":
    unittest.main()
