from pathlib import Path

from ...download import download_file

down_path = Path(__file__).parent
download_file("addons_file/wxz_pie_menus/GN_Nodes.blend", down_path)
download_file("addons_file/wxz_pie_menus/SN_Nodes.blend", down_path)
download_file("addons_file/wxz_pie_menus/CN_Nodes.blend", down_path)
