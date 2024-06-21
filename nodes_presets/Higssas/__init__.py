from pathlib import Path

from ...download import download_file

down_path = Path(__file__).parent
xz_url = "addons_file" + "/" + down_path.name + "/"

download_file(xz_url + "Higgsas Nodes v8.blend", down_path)
