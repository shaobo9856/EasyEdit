# -*- coding: utf-8 -*-
import json

# 定义函数来计算列表的平均值
def calculate_average(lst):
    if len(lst) == 0:
        return 0.0
    return sum(lst) / len(lst)

# 读取 JSON 文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 计算 post 部分的平均值
def calculate_post_averages(data):
    averages = {
        "rewrite_acc": [],
        "locality_neighborhood_acc": [],
        "portability_one_hop_acc": [],
        "rephrase_acc": []
    }

    for case in data:
        post = case.get("post", {})
        averages["rewrite_acc"].extend(post.get("rewrite_acc", []))
        averages["locality_neighborhood_acc"].extend(post.get("locality", {}).get("neighborhood_acc", []))
        averages["portability_one_hop_acc"].extend(post.get("portability", {}).get("one_hop_acc", []))
        averages["rephrase_acc"].extend(post.get("rephrase_acc", []))

    # 计算平均值
    for key in averages:
        averages[key] = calculate_average(averages[key])

    return averages

# 主程序入口
if __name__ == "__main__":
    file_path = "output/ROME_MzsR_vi_results.json"  # 替换成你的 JSON 文件路径
    data = read_json_file(file_path)
    averages = calculate_post_averages(data)

    print(f"{file_path}平均值:")
    print(f"rewrite_acc: {averages['rewrite_acc']}")
    print(f"rephrase_acc: {averages['rephrase_acc']}")
    print(f"locality_neighborhood_acc: {averages['locality_neighborhood_acc']}")
    print(f"portability_one_hop_acc: {averages['portability_one_hop_acc']}")
