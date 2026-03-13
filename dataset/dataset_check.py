import json
from collections import Counter
import pandas as pd
import os

def check_my_dataset(file_path="final_dataset_filtered.json"):
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return

    print(f"--- 开始检查数据集: {file_path} ---")

    data = []
    try:
        # 尝试作为标准 JSON 加载 (整个文件是一个 list)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("检测到格式：标准 JSON (List structure)")
    except json.JSONDecodeError:
        # 如果报错，尝试作为 JSONL 加载 (每一行是一个独立对象)
        print("尝试标准 JSON 加载失败，正在按 JSONL (行模式) 解析...")
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line: continue  # 跳过空行
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"严重错误：第 {line_number} 行格式损坏！")
                    print(f"内容预览: {line[:50]}...")
                    return

    if not isinstance(data, list):
        print("错误：加载的数据不是列表格式，请检查 JSON 结构。")
        return

    # --- 以下是数据质量检查部分 ---
    total = len(data)
    print(f"总样本数: {total}")

    if total == 0:
        print("数据为空，停止检查。")
        return

    # 检查字段完整性
    first_item = data[0]
    print(f"字段检查: {list(first_item.keys())}")
    if 'text' not in first_item or 'label' not in first_item:
        print("警告：数据中缺少 'text' 或 'label' 字段！")

    # 标签分布
    labels = [d.get('label', 'Missing') for d in data]
    label_counts = Counter(labels)
    print("\n标签分布:")
    for label, count in label_counts.items():
        role = "Human" if label == 0 else ("AI" if label == 1 else "Unknown")
        print(f"  - {role} ({label}): {count} 条 ({ (count/total)*100 :.2f}%)")

    # 长度分布
    lengths = [len(str(d.get('text', '')).split()) for d in data]
    df_len = pd.Series(lengths)
    print("\n文本长度分布 (单词数):")
    print(f"  - 平均: {df_len.mean():.2f} | 中位数: {df_len.median()} | 最长: {df_len.max()}")

    # 截断风险
    over_limit = sum(1 for l in lengths if l > 400)
    if over_limit > 0:
        print(f"\n注意: 有 {over_limit} 条文本超过 400 词，RoBERTa 训练时会只取前 512 Tokens。")

    print("\n--- 检查完成 ---")

if __name__ == "__main__":
    check_my_dataset()