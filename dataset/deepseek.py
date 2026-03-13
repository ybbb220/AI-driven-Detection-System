import json
import os
import re
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)


API_KEY = "sk-12cb9b24e0b9402c922f52753659deba"
# DeepSeek API 的基础 URL
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-reasoner"

INPUT_FILE = "title.txt"  # 读取的 txt 文件名
OUTPUT_FILE = "deepseek-reasoner.json"  # 输出的 json 文件名

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def generate_english_essay(topic):
    system_prompt = "你是一位正在学习英语的大学生。请根据提供的题目，撰写一篇结构合理、引人入胜的英语作文。注意：直接输出作文正文，不要使用 Markdown 标题（如 # 或 ##），不要对标题进行特殊格式化。"
    user_prompt = f"题目: {topic}\n\n请以此为主题写一篇英语作文，不要带 Markdown 格式或输出与正文内容无关的字符。"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                ChatCompletionSystemMessageParam(role="system", content=system_prompt),
                ChatCompletionUserMessageParam(role="user", content=user_prompt)
            ],
            temperature=0.7,  # 控制文本生成的随机性
            max_tokens=1500  # 限制生成的最大长度，可根据需要调整
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"调用 API 时发生错误: {e}")
        return None


def main():
    # 1. 读取 txt 文件
    if not os.path.exists(INPUT_FILE):
        print(f"错误：找不到文件 '{INPUT_FILE}'。请确保文件存在。")
        return

    print(f"正在读取 {INPUT_FILE}...")

    topics = []
    current_topic = []

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 清洗可能存在的标签
            line = re.sub(r'\\s*', '', line)

            # 使用正则表达式判断当前行是否是新题目的开头
            if re.match(r'^\d+\.', line):
                # 如果 current_topic 里面已经有内容，说明上一个题目收集完毕，合并后存入 topics
                if current_topic:
                    topics.append(" ".join(current_topic))
                # 开启一个新题目的收集
                current_topic = [line]
            else:
                # 如果不是数字开头，说明是当前题目的延续，继续追加
                if current_topic:
                    current_topic.append(line)
        if current_topic:
            topics.append(" ".join(current_topic))

    print(f"共读取到 {len(topics)} 个题目。开始生成作文...")

    # 2. 调用 API 生成作文并组装数据
    results = []
    for index, topic in enumerate(topics, 1):
        print(f"[{index}/{len(topics)}] 正在生成题目: '{topic}'...")
        essay = generate_english_essay(topic)

        if essay:
            item = {
                "text": essay,
                "label": "1"
            }
            results.append(item)
            print(" -> 生成成功！")
        else:
            print(" -> 生成失败，跳过该题目。")

    # 3. 将生成的内容输出为 json 文件
    print(f"\n所有题目处理完毕，正在保存到 {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("保存成功！程序运行结束。")

if __name__ == "__main__":
    main()