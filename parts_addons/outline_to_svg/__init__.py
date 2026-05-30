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
import bpy

from . import install_packages, ui_helpers

restart_required = False
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
        print("遇到异常")
        print(e)
        print("需要重新启动")
        restart_required = True


def register():
    if restart_required:
        try:
            missing_text = ", ".join(MISSING_MODULES) if MISSING_MODULES else "pip 软件包"
            message = "".join(
                (
                    "Outline To SVG 依赖未就绪: ",
                    missing_text,
                    "，请安装后重新启动Blender",
                )
            )
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
