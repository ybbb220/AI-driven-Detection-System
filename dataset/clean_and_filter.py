import json
import os
from collections import Counter


def clean_and_filter_dataset(input_path="final_dataset.json", output_path="final_dataset_filtered.json", max_words=400):
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    print(f"--- 开始清洗并过滤超长文本 (限制: {max_words} 词) ---")

    raw_data = []
    # 1. 加载数据 (兼容标准 JSON)
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except json.JSONDecodeError:
        # 如果是 JSONL 格式
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line: raw_data.append(json.loads(line))

    # 2. 过滤逻辑
    final_data = []
    stats = {
        "invalid_format": 0,
        "too_long": 0,
        "valid": 0
    }

    for item in raw_data:
        # 基本格式校验
        if not (isinstance(item, dict) and 'text' in item and 'label' in item):
            stats["invalid_format"] += 1
            continue

        # 长度校验 (按单词数)
        word_count = len(str(item['text']).split())
        if word_count > max_words:
            stats["too_long"] += 1
            continue

        # 经过所有检查，确认为合法且长度适中
        final_data.append(item)
        stats["valid"] += 1

    # 3. 输出统计结果
    print(f"\n[处理报告]")
    print(f"原始数据总数: {len(raw_data)}")
    print(f"剔除格式错误/缺失: {stats['invalid_format']} 条")
    print(f"剔除超长文本 (> {max_words} 词): {stats['too_long']} 条")
    print(f"保留合法数据总数: {stats['valid']} 条")

    # 4. 检查清洗后的标签分布
    labels = [d['label'] for d in final_data]
    label_counts = Counter(labels)
    print("\n[过滤后标签分布]")
    for label, count in label_counts.items():
        role = "Human" if label == 0 else "AI"
        print(f"  - {role} ({label}): {count} 条 ({(count / len(final_data)) * 100 :.2f}%)")

    # 5. 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"\n--- 处理完成！清洗后的数据已存入: {output_path} ---")


if __name__ == "__main__":
    clean_and_filter_dataset()