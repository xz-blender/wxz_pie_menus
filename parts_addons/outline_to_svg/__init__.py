# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Outline To SVG",
    "author": "Missing Field <themissingfield.com>",
    "description": "Export outline of selected objects",
    "blender": (2, 83, 0),
    "version": (0, 0, 92),
    "location": "",
    "warning": "",
    "category": "Import-Export",
}
import traceback

import bpy

from . import install_packages, ui_helpers

restart_required = False
LOAD_ERROR = ""
registered_classes = ()
EXTRA_MODULES = [
    ("shapely", "shapely"),
    # ("loguru", "loguru"),
]
MISSING_MODULES = [module for _package, module in EXTRA_MODULES if not install_packages.module_has_loader(module)]
NEW_PACKAGES_INSTALLED = False

# Local Modules
if MISSING_MODULES:
    print("Outline To SVG 缺少依赖:", ", ".join(MISSING_MODULES))
    restart_required = True
else:
    try:
        from . import operators, props, ui

        registered_classes = (
            props,
            operators,
            ui,
        )

    except Exception as e:
        LOAD_ERROR = f"{type(e).__name__}: {e}"
        print("Outline To SVG 加载失败:", LOAD_ERROR)
        traceback.print_exc()
        restart_required = True


def register():
    if restart_required:
        try:
            if MISSING_MODULES:
                message = (
                    f"Outline To SVG 依赖未就绪: {', '.join(MISSING_MODULES)}"
                    "，请安装后重新启动Blender"
                )
            else:
                message = f"Outline To SVG 加载失败: {LOAD_ERROR}（详见系统控制台）"
            ui_helpers.pop_message(message)
        except Exception as e:
            print("Exception encountered in registration")
            print(e)
            return None
    else:
        try:
            for cls in registered_classes:
                cls.register()
        except Exception as e:
            print(e)
            return None


def unregister():
    try:
        for cls in registered_classes:
            cls.unregister()
    except Exception as e:
        print(e)
        return None
