import platform


def get_sync_path():
    if platform.system() == "Windows":
        return r"D:/OneDrive/Sync/Blender/Assets Sync"
    elif platform.system() == "Darwin":
        return r"/Users/wangxianzhi/Library/CloudStorage/OneDrive-个人/Sync/Blender/Assets Sync"


def get_local_path():
    if platform.system() == "Windows":
        return r"F:/Blender Assets"
    elif platform.system() == "Darwin":
        return r"/Users/wangxianzhi/Blender Lib"
