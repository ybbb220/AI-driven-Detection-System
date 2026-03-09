import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
import time
import os
import json


class AITextDetector:
    # 默认路径更新为我们刚刚训练的 RoBERTa 路径
    def __init__(self, model_path="./roberta_ai_text_classifier"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"AI文本检测器使用设备: {self.device}")

        # 使用 AutoTokenizer 和 AutoModel，兼容性更好
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
        # 【核心修改】：直接 tokenize 传入的纯文本，没有任何拼接伪装
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512  # 使用与训练时相同的 512 长度
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1).cpu().numpy()[0]

        # 获取概率
        ai_label_id = self.label2id.get("AI", 1)
        human_label_id = self.label2id.get("Human", 0)

        ai_prob = probabilities[ai_label_id]
        human_prob = probabilities[human_label_id]

        # 调试打印，确保一切正常
        preview = text[:40].replace('\n', ' ') + "..."
        print(f"[推理] {preview} | AI: {ai_prob:.2%} | Human: {human_prob:.2%}")

        return float(ai_prob)

    def detect(self, text):
        start_time = time.time()

        # 1. 整体文本分析
        overall_ai_prob = self._predict_single_text(text)
        overall_human_prob = 1.0 - overall_ai_prob

        # 2. 句子级别分析 (保留用于前端高亮展示)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        sentence_analysis = []
        for i, sentence in enumerate(sentences):
            if not sentence:
                continue

            # 句子太短（比如少于3个单词）其实没必要测，容易引入噪音，可以做个简单的过滤
            if len(sentence.split()) < 3:
                continue

            sentence_ai_prob = self._predict_single_text(sentence)

            sentence_analysis.append({
                'sentence_id': i + 1,
                'text': sentence,
                'ai_probability': round(sentence_ai_prob, 4),
                'human_probability': round(1.0 - sentence_ai_prob, 4),
                'is_ai_generated': bool(sentence_ai_prob > 0.5)
            })

        analysis_time = time.time() - start_time

        return {
            'ai_probability': round(overall_ai_prob, 4),
            'human_probability': round(overall_human_prob, 4),
            'sentence_analysis': sentence_analysis,
            'analysis_time': round(analysis_time, 3)
        }


if __name__ == '__main__':
    detector = AITextDetector()

    human_text = "I walked my dog in the park this morning. The weather was beautiful and we had a great time."
    ai_text = "The utilization of advanced neural networks facilitates superior pattern recognition in complex datasets, significantly enhancing the efficacy of analytical methodologies."

    print("\n--- 测试人类文本 ---")
    result_human = detector.detect(human_text)
    print(f"整体AI概率: {result_human['ai_probability']:.2%}")

    print("\n--- 测试AI文本 ---")
    result_ai = detector.detect(ai_text)
    print(f"整体AI概率: {result_ai['ai_probability']:.2%}")