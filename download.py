import os
import zipfile

import requests  # type: ignore

my_url = "https://vip.123pan.cn/1820333155/extensions_website/"
headers = {
    "Accept": "application/zip, application/json, text/html, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


def download_file(url, save_folder):
    url = my_url + url
    save_path = os.path.join(save_folder, os.path.basename(url))
    # 检查文件是否已经存在
    if os.path.exists(save_path):
        return

    # 发送HTTP请求获取文件
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        # 打开文件并写入内容
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=16384):
                file.write(chunk)
        print(f"文件已下载: {save_path}")
    else:
        print(f"无法下载文件，状态码: {response.status_code}")


def download_zip(url, save_folder):
    url = my_url + url
    basename = os.path.basename(url)
    ex_name = os.path.splitext(basename)[0]
    save_path = os.path.join(save_folder, basename)
    downloaded = os.path.join(save_folder, ex_name)

    if not os.path.exists(downloaded):
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=16384):
                    f.write(chunk)

        with zipfile.ZipFile(save_path, "r") as zip_ref:
            zip_ref.extractall(save_folder)

        if os.path.exists(downloaded):
            # 去除只读属性
            os.chmod(downloaded, 0o777)

        if os.path.exists(save_path):
            os.remove(save_path)
