import importlib.util


def check_package_is_installed(pkg_name: str) -> bool:
    return importlib.util.find_spec(pkg_name) is not None
