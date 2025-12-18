import fnmatch
import os
import platform
import shutil
import tempfile
import zipfile
from pathlib import Path

try:
    from .items import *
except ImportError:
    from items import *


def is_windows():
    return platform.system() == "Windows"


def is_macos():
    return platform.system() == "Darwin"


def get_desktop_path():
    """获取win桌面路径，即使路径被手动更改了(从注册表获取)"""
    if is_windows():
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        ) as key:
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            return os.path.expanduser(os.path.expandvars(desktop_path))
    elif is_macos():
        return os.path.join(os.path.expanduser("~"), "Desktop")


desktop_path = get_desktop_path()
source_dir = Path(__file__).parent
output_path = str(Path(desktop_path) / source_dir.name) + ".zip"
split_out_path = Path(get_desktop_path()) / "upload"


def remove_duplicates(lst):
    return list(dict.fromkeys(lst))


import fnmatch
import os
import shutil


def copy_excluded_files(source_dir, target_dir, exclude_list):
    def should_include(path, source_dir):
        rel_path = os.path.relpath(path, source_dir)
        for pattern in exclude_list:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
        return False

    for root, dirs, files in os.walk(source_dir):
        rel_root = os.path.relpath(root, source_dir)

        # 处理文件夹
        for d in dirs:
            dir_path = os.path.join(root, d)
            if should_include(dir_path, source_dir):
                target_path = os.path.join(target_dir, rel_root, d)
                if not os.path.exists(target_path):
                    os.makedirs(target_path)

        # 处理文件
        for f in files:
            file_path = os.path.join(root, f)
            if should_include(file_path, source_dir):
                target_path = os.path.join(target_dir, rel_root, f)
                target_dir_path = os.path.dirname(target_path)
                if not os.path.exists(target_dir_path):
                    os.makedirs(target_dir_path)
                shutil.copy2(file_path, target_path)


def load_gitignore(exclude_list):
    gitignore_path = os.path.join(os.path.dirname(__file__), ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    exclude_list.append(line)


def should_exclude(path, exclude_list):
    for pattern in exclude_list:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    return False


def zip_dir(zip_filename, source_dir, exclude_list):
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [
                d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), source_dir), exclude_list)
            ]
            files = [
                f for f in files if not should_exclude(os.path.relpath(os.path.join(root, f), source_dir), exclude_list)
            ]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join(os.path.basename(source_dir), os.path.relpath(file_path, source_dir))
                zipf.write(file_path, arcname)


def main_zip(exclude_list, source_dir, output_path, main=True):
    if main:
        load_gitignore(exclude_list)
        exclude_list += packup_split_file_list + packup_split_folder_list
        exclude_list = remove_duplicates(exclude_list)
    else:
        exclude_list = remove_duplicates(exclude_list)

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        temp_zip_filename = tmp_file.name

    try:
        zip_dir(temp_zip_filename, source_dir, exclude_list)
        output_path = os.path.expanduser(os.path.expandvars(str(output_path)))
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(temp_zip_filename, output_path)
        print(f"Created {output_path}")
    finally:
        if os.path.exists(temp_zip_filename):
            os.remove(temp_zip_filename)


if __name__ == "__main__":
    main_zip(packup_main_exclude_list, source_dir, output_path)

    if not os.path.exists(split_out_path):
        os.makedirs(split_out_path)
    for dir in packup_split_folder_list:
        input_path = Path(__file__).parent / dir
        output_path = str(split_out_path / dir) + ".zip"
        main_zip(packup_split_exclude_list, input_path, output_path, False)

    copy_excluded_files(source_dir, split_out_path, packup_split_file_list)
