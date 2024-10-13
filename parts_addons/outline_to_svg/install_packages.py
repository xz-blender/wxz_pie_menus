import importlib.util
import subprocess
import sys
from typing import Iterable, Tuple, Union
from pathlib import Path

import bpy


# TODO: Check this works for all blender versions
if bpy.app.version[1] < 92 and bpy.app.version[0] < 3:
    PYTHON_PATH = bpy.app.binary_path_python
else:
    PYTHON_PATH = sys.executable


# TODO: Better error handling
def _run(cmd):
    try:
        stdout = subprocess.check_output(cmd)
        return stdout
    except subprocess.CalledProcessError as e:
        print(e)
        pass


def ensure_pip():
    if not module_has_loader("pip"):
        print("Unable to find pip. Running ensurepip ")
        _run([PYTHON_PATH, "-m", "ensurepip"])


def module_has_loader(module_name) -> bool:
    """Test whether module is missing"""
    return importlib.find_loader(module_name) is not None


def install_package(package_name: str, location: Union[Path, None] = None):
    """Test whether module is missing"""
    if location is None:
        location = Path(bpy.utils.user_resource("SCRIPTS")) / "addons/modules"
    print(f'installing {package_name} to {location}')
    cmd = [
        PYTHON_PATH,
        "-m",
        "pip", "install",
        "--only-binary", "all",
        "--no-deps",
        "--upgrade",
        "-t",
        str(location),
        package_name,
    ]
    return _run(cmd)


def ensure_packages(package_pairs: Iterable[Tuple[str, str]]):
    """
    Install dependencies for package pairs
        package_pairs : A iterable of ('package_name', 'module_name')
    """
    installed_packages = []
    ensure_pip()
    for package, module in package_pairs:
        if module_has_loader(module):
            # print(package, " already preset")
            continue

        print(f"Installing: {package}")
        install_package(package)
        installed_packages.append(package)

    return installed_packages


# class FILE_OT_DownloadPipModules(Operator):
#     bl_options = {"HIDDEN"}

#     packages: StringProperty(
#         name="Required Packages and their root module",
#         description="Provide comma separated 'module_name:package_name'"
#     )

#     def _parse_packages_arg(self) -> Generator[PackageDef, None, None]:
#         """ Split the modules property into a dict of """
#         items = self.modules.split(",")
#         for item in items:
#             yield PackageDef(item.split(":"))

#     def execute(self):
#         packages = self._parse_packages_arg()
#         PipAssist.ensure_pip()
#         missing_packages = filterfalse(
#             lambda p: PipAssist.can_find_module(p.module), packages)
#         return {"FINISHED"}
