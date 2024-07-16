import fnmatch
import os
import shutil
import tempfile
import winreg
import zipfile
from pathlib import Path


def get_desktop_path():
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    ) as key:
        desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
        return desktop_path


desktop_path = get_desktop_path()
source_dir = Path(__file__).parent
output_path = str(Path(desktop_path) / source_dir.name) + ".zip"
split_out_path = Path(get_desktop_path()) / "upload"
# 初始化要排除的文件和文件夹
main_exclude_list = [
    "__pycache__",
    "README.md",
    "LISENSE",
    ".vscode",
    ".genaiscript",
    "packup.py",
    ".gitignore",
    ".git",
]
split_exclude_list = [
    "__pycache__",
    "blender_assets.cats.txt~",
    "blends_savetime.txt",
]
split_file_list = [
    "fonts/ui_font.ttf",
    "workspace.blend",
    "workspace_online.blend",
]
split_folder_list = ["nodes_presets", "parts_addons", ""]


def remove_duplicates(lst):
    return list(dict.fromkeys(lst))


def load_gitignore(exclude_list):
    gitignore_path = os.path.join(os.path.dirname(__file__), ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("*"):
                    exclude_list.append(line)


import shutil


def copy_excluded_files(source_dir, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for root, dirs, files in os.walk(source_dir):
        rel_root = os.path.relpath(root, source_dir)

        # 复制排除的文件夹
        for d in dirs:
            dir_path = os.path.join(rel_root, d)
            if should_exclude(dir_path, source_dir):
                src_path = os.path.join(source_dir, dir_path)
                dest_path = os.path.join(target_dir, dir_path)
                if not os.path.exists(dest_path):
                    shutil.copytree(src_path, dest_path)

        # 复制排除的文件
        for f in files:
            file_path = os.path.join(rel_root, f)
            if should_exclude(file_path, source_dir):
                src_path = os.path.join(source_dir, file_path)
                dest_path = os.path.join(target_dir, file_path)
                dest_dir = os.path.dirname(dest_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                shutil.copy2(src_path, dest_path)


# 示例调用
source_dir = "C:/test"
target_dir = "C:/upload"
copy_excluded_files(source_dir, target_dir)


def should_exclude(exclude_list, path):
    for pattern in exclude_list:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    return False


def zip_dir(zip_filename, source_dir, exclude_list):
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # 排除以点开头的文件夹
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            # 排除以".pyc"结尾的文件
            dirs[:] = [d for d in dirs if not d.endswith(".pyc")]
            # 排除指定的文件夹和文件
            dirs[:] = [
                d for d in dirs if not should_exclude(exclude_list, os.path.relpath(os.path.join(root, d), source_dir))
            ]
            files = [
                f for f in files if not should_exclude(exclude_list, os.path.relpath(os.path.join(root, f), source_dir))
            ]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)


def main_zip(main_exclude_list, source_dir, output_path, main=True):
    # 加载 .gitignore 文件中的排除规则
    if main:
        load_gitignore(main_exclude_list)
        main_exclude_list += split_file_list + split_folder_list
        main_exclude_list = remove_duplicates(main_exclude_list)
    else:
        main_exclude_list = remove_duplicates(main_exclude_list)

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        temp_zip_filename = tmp_file.name

    try:
        # 压缩目录到临时文件
        zip_dir(temp_zip_filename, source_dir, main_exclude_list)

        # 移动临时文件到目标位置
        shutil.move(temp_zip_filename, output_path)
        print(f"Created {output_path}")
    finally:
        # 删除临时文件（如果存在）
        if os.path.exists(temp_zip_filename):
            os.remove(temp_zip_filename)


if __name__ == "__main__":
    main_zip(main_exclude_list, source_dir, output_path)

    for dir in split_folder_list:
        input_path = Path(__file__).parent / dir
        output_path = str(split_out_path / dir) + ".zip"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        main_zip(split_exclude_list, input_path, output_path, False)
