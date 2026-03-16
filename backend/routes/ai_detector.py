import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
import time
import os
import json


class AITextDetector:
    def __init__(self, model_path="./roberta_ai_text_classifier"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"AI文本检测器使用设备: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

        label2id_path = os.path.join(model_path, "label2id.json")
        with open(label2id_path, 'r', encoding='utf-8') as f:
            self.label2id = json.load(f)
        self.id2label = {v: k for k, v in self.label2id.items()}

    def _predict_single_text(self, text):
        """对纯文本进行预测，返回AI概率"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1).cpu().numpy()[0]

        ai_label_id = self.label2id.get("AI", 1)

        ai_prob = probabilities[ai_label_id]

        # 调试打印，方便在控制台观察滑动窗口拼接后的文本
        preview = text[:60].replace('\n', ' ') + "..."
        print(f"[推理] {preview} | AI: {ai_prob:.2%}")

        return float(ai_prob)

    def detect(self, text, window_size=1):
        """
        核心检测逻辑（引入滑动窗口法 + 句子权重聚合全局概率）
        :param text: 完整文本
        :param window_size: 窗口大小。设为1表示包含前1句和后1句。
        """
        start_time = time.time()

        # 句子级别分析 (带上下文)
        sentences_raw = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences_raw if s.strip()]

        sentence_analysis = []
        num_sentences = len(sentences)

        for i, sentence in enumerate(sentences):
            if not sentence:
                continue

            # 过滤极短句，避免噪音
            if len(sentence.split()) < 3:
                continue

            # 构建滑动窗口上下文
            start_idx = max(0, i - window_size)
            end_idx = min(num_sentences, i + window_size + 1)

            # 将上下文句子拼接起来作为模型的真实输入
            context_text = " ".join(sentences[start_idx:end_idx])

            # 对拼接后的上下文块进行预测
            context_ai_prob = self._predict_single_text(context_text)

            sentence_analysis.append({
                'sentence_id': i + 1,
                'text': sentence,
                'ai_probability': round(context_ai_prob, 4),
                'human_probability': round(1.0 - context_ai_prob, 4),
                # 单句的判断阈值保持 0.75
                'is_ai_generated': bool(context_ai_prob > 0.75)
            })

        # 方案一：通过句子概率加权平均计算综合概率
        total_weight = 0
        weighted_ai_prob_sum = 0

        for item in sentence_analysis:
            # 使用该句子的单词数量作为权重
            weight = len(item['text'].split())
            weighted_ai_prob_sum += item['ai_probability'] * weight
            total_weight += weight

        # 计算加权平均概率，加入兜底逻辑以防全部是极短句被过滤
        if total_weight > 0:
            overall_ai_prob = weighted_ai_prob_sum / total_weight
        else:
            overall_ai_prob = self._predict_single_text(text)

        overall_human_prob = 1.0 - overall_ai_prob
        analysis_time = time.time() - start_time

        return {
            'ai_probability': round(overall_ai_prob, 4),
            'human_probability': round(overall_human_prob, 4),
            'sentence_analysis': sentence_analysis,
            'analysis_time': round(analysis_time, 3)
        }


if __name__ == '__main__':
    detector = AITextDetector()

    # 测试文本（替换为你截图中的中式英语样例）
    human_text = "I have a happy family. There is three people in my family: my father, my mother and I. My father is a work. He is very tall. He like play basketball. My mother have long hair. She is a teacher. She cook good food for we every day. I am a student. I go to school by foot. I very love my family. We are happy everydays."
    ai_text = "The utilization of advanced neural networks facilitates superior pattern recognition in complex datasets. Furthermore, it significantly enhances the efficacy of analytical methodologies. In conclusion, this approach represents a paradigm shift in computational linguistics."

    print("\n--- 测试截图中的人类文本 ---")
    result_human = detector.detect(human_text)
    print(f"综合 AI 概率: {result_human['ai_probability']:.2%}")

    print("\n--- 测试典型的 AI 文本 ---")
    result_ai = detector.detect(ai_text)
    print(f"综合 AI 概率: {result_ai['ai_probability']:.2%}")