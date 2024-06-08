from pathlib import Path

from ...download import download_file

down_path = Path(__file__).parent
download_file("addons_file/wxz_pie_menus/Higgsas Nodes v8.blend", down_path)
