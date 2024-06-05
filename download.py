
def download_file(url, save_folder):
    import os

    import requests
    url = "https://vip.123pan.cn/1820333155/extensions_website/" + url
    save_path = os.path.join(save_folder,os.path.basename(url))
    # 检查文件是否已经存在
    if os.path.exists(save_path):
        return

    # 发送HTTP请求获取文件
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # 打开文件并写入内容
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"文件已下载: {save_path}")
    else:
        print(f"无法下载文件，状态码: {response.status_code}")
        
    del requests