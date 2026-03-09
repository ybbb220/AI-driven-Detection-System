import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_scheduler
from torch.optim import AdamW
from datasets import load_dataset
from tqdm.auto import tqdm
import os
import json


# --- 1. 准备数据集 ---
def prepare_dataset(file_path="english_essays.jsonl"):
    """
    加载纯文本数据集。
    假设格式为: {"text": "This is an essay...", "label": 0} (0: 人类, 1: AI)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"未找到数据文件 {file_path}，请准备好纯文本数据集。")

    # 根据你的文件扩展名，这里可以是 'json' 也可以是 'csv'
    dataset = load_dataset('json', data_files=file_path)
    return dataset['train']


# --- 2. 主训练流程 ---
def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"========== 使用设备: {device} ==========")

    full_dataset = prepare_dataset()
    train_val_split = full_dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = train_val_split['train']
    val_dataset = train_val_split['test']

    # 【核心修改 1】：更换为更适合英文自然语言理解的 RoBERTa
    model_name = "roberta-base"  # 也可以换成 "microsoft/deberta-v3-base"
    print(f"正在加载模型: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model.to(device)

    # 显式定义标签映射
    label2id = {"Human": 0, "AI": 1}

    def preprocess_function(examples):
        # 【核心修改 2】：彻底抛弃拼接，直接对纯文本进行 Tokenize
        # 截断到 512，这对于长 Essay 很重要
        tokenized_inputs = tokenizer(
            examples['text'],
            padding="max_length",
            truncation=True,
            max_length=512
        )

        # 确保 labels 字段存在且为整数
        tokenized_inputs["labels"] = examples["label"]
        return tokenized_inputs

    print("正在进行文本 Tokenization 处理...")
    tokenized_train_dataset = train_dataset.map(preprocess_function, batched=True)
    tokenized_val_dataset = val_dataset.map(preprocess_function, batched=True)

    # 移除不需要的列，只保留模型需要的 input_ids, attention_mask, labels
    columns_to_remove = [col for col in tokenized_train_dataset.column_names if
                         col not in ['input_ids', 'attention_mask', 'labels']]
    tokenized_train_dataset = tokenized_train_dataset.remove_columns(columns_to_remove)
    tokenized_train_dataset.set_format("torch")

    tokenized_val_dataset = tokenized_val_dataset.remove_columns(columns_to_remove)
    tokenized_val_dataset.set_format("torch")

    # 保持良好的防显存溢出设置
    train_dataloader = DataLoader(tokenized_train_dataset, shuffle=True, batch_size=4)
    val_dataloader = DataLoader(tokenized_val_dataset, batch_size=4)

    accumulation_steps = 4
    # 保持稳健的学习率
    optimizer = AdamW(model.parameters(), lr=2e-5)

    num_epochs = 3
    num_update_steps = (len(train_dataloader) // accumulation_steps) * num_epochs
    num_warmup_steps = int(num_update_steps * 0.1)

    lr_scheduler = get_scheduler(
        "linear",
        optimizer=optimizer,
        num_warmup_steps=num_warmup_steps,
        num_training_steps=num_update_steps
    )

    print("\n========== 开始训练 ==========")
    progress_bar = tqdm(total=num_update_steps, desc="Training")

    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0.0

        for step, batch in enumerate(train_dataloader):
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)

            loss = outputs.loss / accumulation_steps
            loss.backward()
            epoch_loss += loss.item() * accumulation_steps

            if (step + 1) % accumulation_steps == 0 or (step + 1) == len(train_dataloader):
                # 保持梯度裁剪
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()
                progress_bar.update(1)
                progress_bar.set_description(f"Epoch {epoch + 1} | Loss: {loss.item() * accumulation_steps:.4f}")

        print(f"\nEpoch {epoch + 1} 平均 Loss: {epoch_loss / len(train_dataloader):.4f}")

        # 验证集评估
        model.eval()
        total_correct = 0
        total_samples = 0
        for val_batch in val_dataloader:
            val_batch = {k: v.to(device) for k, v in val_batch.items()}
            with torch.no_grad():
                val_outputs = model(**val_batch)

            logits = val_outputs.logits
            predictions = torch.argmax(logits, dim=-1)
            total_correct += (predictions == val_batch["labels"]).sum().item()
            total_samples += len(val_batch["labels"])

        accuracy = total_correct / total_samples
        print(f"Epoch {epoch + 1} 验证集准确率: {accuracy:.4f}\n")

    # 更新保存路径名
    output_dir = "./roberta_ai_text_classifier"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    with open(os.path.join(output_dir, "label2id.json"), 'w', encoding='utf-8') as f:
        json.dump(label2id, f, ensure_ascii=False)

    print(f"========== 训练完成！模型已安全保存到: {output_dir} ==========")


if __name__ == "__main__":
    train_model()