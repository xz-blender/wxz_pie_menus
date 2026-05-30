import fnmatch
import os
import platform
import shutil
import tempfile
import zipfile
from pathlib import Path


DEFAULT_EXCLUDE_LIST = [
    ".git",
    ".git/*",
    ".genaiscript",
    ".genaiscript/*",
    ".venv",
    ".venv/*",
    ".vscode",
    ".vscode/*",
    "__pycache__",
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "._.DS_Store",
    ".gitignore",
    "*.downloaded_marker",
    "blender_assets.cats.txt~",
    "blends_savetime.txt",
    "test.py",
]


def is_windows():
    return platform.system() == "Windows"


def is_macos():
    return platform.system() == "Darwin"


def get_desktop_path():
    if is_windows():
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            ) as key:
                desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
                return Path(os.path.expanduser(os.path.expandvars(desktop_path)))
        except OSError:
            pass

    if is_macos():
        return Path.home() / "Desktop"

    return Path.home() / "Desktop"


source_dir = Path(__file__).resolve().parent
output_path = get_desktop_path() / f"{source_dir.name}.zip"


def remove_duplicates(items):
    return list(dict.fromkeys(items))


def normalize_path(path):
    return str(path).replace("\\", "/")


def normalize_pattern(pattern):
    return pattern.strip().replace("\\", "/").rstrip("/")


def should_exclude(rel_path, exclude_list):
    rel_path = normalize_path(rel_path)
    name = Path(rel_path).name
    parts = rel_path.split("/")

    for pattern in exclude_list:
        pattern = normalize_pattern(pattern)
        if not pattern:
            continue
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
            return True
        if "/" not in pattern and pattern in parts:
            return True
        if rel_path.startswith(pattern + "/"):
            return True

    return False


def zip_dir(zip_filename, source_dir, exclude_list, skip_files=None):
    source_dir = Path(source_dir).resolve()
    skip_files = {Path(path).resolve() for path in (skip_files or [])}

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            rel_root = root_path.relative_to(source_dir)

            dirs[:] = [
                dirname
                for dirname in dirs
                if not should_exclude(normalize_path(rel_root / dirname), exclude_list)
            ]

            for filename in files:
                file_path = root_path / filename
                if file_path.resolve() in skip_files:
                    continue

                rel_file = file_path.relative_to(source_dir)
                if should_exclude(normalize_path(rel_file), exclude_list):
                    continue

                arcname = Path(source_dir.name) / rel_file
                zipf.write(file_path, normalize_path(arcname))


def main_zip(exclude_list=None, source_dir=source_dir, output_path=output_path):
    exclude_list = remove_duplicates(DEFAULT_EXCLUDE_LIST + list(exclude_list or []))
    output_path = Path(os.path.expanduser(os.path.expandvars(str(output_path)))).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip", dir=output_path.parent) as tmp_file:
        temp_zip_filename = tmp_file.name

    try:
        zip_dir(temp_zip_filename, source_dir, exclude_list, [output_path, temp_zip_filename])
        shutil.move(temp_zip_filename, output_path)
        print(f"Created {output_path}")
    finally:
        if os.path.exists(temp_zip_filename):
            os.remove(temp_zip_filename)


if __name__ == "__main__":
    main_zip()
