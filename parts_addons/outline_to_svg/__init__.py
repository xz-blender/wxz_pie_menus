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
EXTRA_MODULES = [
    ("shapely", "shapely"),
    # ("loguru", "loguru"),
]
# install_packages.ensure_packages(extra_packages)
installed_packages = install_packages.ensure_packages(EXTRA_MODULES)
NEW_PACKAGES_INSTALLED = installed_packages != []
if NEW_PACKAGES_INSTALLED:
    for package in installed_packages:
        print("Installed", package)

# Local Modules
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
    if restart_required and NEW_PACKAGES_INSTALLED:
        try:
            message = "".join(
                (
                    "已安装但无法识别新的pip软件包,",
                    "请重新启动Blender",
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
