import pandas as pd
import json
import os


def convert_csv_to_json(csv_file_path, json_file_path):
    """
    将包含复杂文本的 CSV 文件转换为指定格式的 JSON 文件。
    """
    if not os.path.exists(csv_file_path):
        print(f"错误：找不到文件 '{csv_file_path}'。")
        return

    print(f"正在读取 CSV 文件: {csv_file_path} ...")
    # 使用 pandas 读取 CSV
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"读取 CSV 文件失败: {e}")
        return

    # 检查所需的列是否存在
    if 'text' not in df.columns or 'label' not in df.columns:
        print("错误：CSV 文件中缺失 'text' 或 'label' 列。")
        return

    print("正在提取并转换数据格式...")
    # 仅保留指定的两列
    df_filtered = df[['text', 'label']]

    # 将 label 列统一转换为字符串格式，确保生成 "0" 或 "1"
    df_filtered.loc[:, 'label'] = df_filtered['label'].astype(str)

    # 将 DataFrame 转换为字典列表
    records = df_filtered.to_dict(orient='records')

    print(f"正在保存为 JSON 文件: {json_file_path} ...")
    # 写入 JSON 文件
    with open(json_file_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 保证可能的非英文字符不被转义
        json.dump(records, f, ensure_ascii=False, indent=4)

    print(f"转换完成！共处理了 {len(records)} 条数据。")


if __name__ == "__main__":
    # 配置文件路径
    CSV_FILE = "train_v2_drcat_02.csv"
    JSON_FILE = "train_v2.json"  # 您可以自定义输出的文件名

    convert_csv_to_json(CSV_FILE, JSON_FILE)