from pathlib import Path

from ...download import download_file

down_path = Path(__file__).parent
xz_url = "addons_file" + "/" + down_path.name + "/"

download_file(xz_url + "GN_Nodes.blend", down_path)
download_file(xz_url + "SN_Nodes.blend", down_path)
download_file(xz_url + "CN_Nodes.blend", down_path)
