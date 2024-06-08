from ..download import download_file
from pathlib import Path

down_path = Path(__file__).parent / "Higssas"
download_file("addons_file/wxz_pie_menus/Higgsas Nodes v8.blend", down_path)

down_path = Path(__file__).parent / "wxz_nodes"
download_file("addons_file/wxz_pie_menus/GN_Nodes.blend", down_path)
download_file("addons_file/wxz_pie_menus/SN_Nodes.blend", down_path)
download_file("addons_file/wxz_pie_menus/CN_Nodes.blend", down_path)
