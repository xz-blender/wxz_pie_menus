import json


def sort_operator_id_file():
    from pathlib import Path

    op_id_filepath = Path(__file__).parent / "operator_id.json"
    # 读取JSON文件
    with open(op_id_filepath, "r") as file:
        data = json.load(file)
    # 对字典的键进行排序
    sorted_data = {key: sorted(value) for key, value in sorted(data.items())}
    # 将排序后的内容写回JSON文件
    with open(op_id_filepath, "w") as file:
        json.dump(sorted_data, file, indent=4)
    print("JSON内容已按名称排序并重新写入文件。")


if __name__ == "__main__":
    sort_operator_id_file()
