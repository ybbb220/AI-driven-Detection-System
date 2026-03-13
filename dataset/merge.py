import json
import random
import os


def merge_and_shuffle_json(input_files, output_file):
    """
    读取多个 JSON 文件，合并条目，打乱顺序并输出。
    """
    combined_data = []

    print("正在开始处理文件...")

    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"警告：找不到文件 {file_path}，已跳过。")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 确保读取的是列表格式（如上传的 deepseek-chat.json）
                if isinstance(data, list):
                    combined_data.extend(data)
                    print(f"成功加载文件：{file_path} (条目数: {len(data)})")
                else:
                    print(f"警告：{file_path} 的内容不是列表格式，已跳过。")
        except json.JSONDecodeError:
            print(f"错误：{file_path} 不是有效的 JSON 文件。")
        except Exception as e:
            print(f"处理 {file_path} 时发生未知错误: {e}")

    if not combined_data:
        print("没有可合并的数据。")
        return

    # 随机打乱条目顺序
    print(f"正在打乱共计 {len(combined_data)} 条数据...")
    random.shuffle(combined_data)

    # 将结果保存到输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # indent=4 使输出的 JSON 具有良好的可读性
            # ensure_ascii=False 确保中文字符不会被转义为 \uXXXX 格式
            json.dump(combined_data, f, ensure_ascii=False, indent=4)
        print(f"成功！合并后的数据已保存至：{output_file}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")


if __name__ == "__main__":
    # --- 你可以在这里修改配置 ---
    # 待合并的文件名列表
    files_to_process = [
        'deepseek-chat.json',
        'deepseek-reasoner.json',
        'qwen-max.json',
        'qwen-plus.json',
        'train_v2.json'
    ]

    # 输出的文件名
    output_name = 'final_dataset.json'

    # 执行合并
    merge_and_shuffle_json(files_to_process, output_name)