"""
bert_inference.py — Load và chạy BERT model
============================================
from src.bert_inference import BERTPredictor
p = BERTPredictor()
print(p.predict("giao hàng nhanh chất lượng tốt"))
"""
import os, json
import torch
import torch.nn as nn

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MDL_DIR  = os.path.join(BASE, "models", "bert_sentiment")
CKPT     = os.path.join(MDL_DIR, "bert_model.pt")

LABEL_MAP = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
EMOJI_MAP = {"NEGATIVE": "😞", "NEUTRAL": "😐", "POSITIVE": "😊"}


class SimpleViTokenizer:
    def __init__(self, word2id, max_len=128):
        self.word2id = word2id
        self.max_len = max_len

    def __call__(self, text, max_length=128, padding="max_length",
                 truncation=True, return_tensors=None):
        tokens = [self.word2id.get("[CLS]", 2)]
        for w in text.lower().split():
            tokens.append(self.word2id.get(w, self.word2id.get("[UNK]", 1)))
        tokens.append(self.word2id.get("[SEP]", 3))
        if truncation and len(tokens) > max_length:
            tokens = tokens[:max_length]
        mask = [1] * len(tokens)
        while len(tokens) < max_length:
            tokens.append(0); mask.append(0)
        input_ids      = torch.tensor([tokens], dtype=torch.long)
        attention_mask = torch.tensor([mask],   dtype=torch.long)
        return {"input_ids": input_ids, "attention_mask": attention_mask}


class _BERTClf(nn.Module):
    def __init__(self, bert_model, num_labels=3, dropout=0.3):
        super().__init__()
        self.bert   = bert_model
        hidden      = bert_model.config.hidden_size
        self.drop   = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden, num_labels)

    def forward(self, input_ids, attention_mask):
        out    = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = out.last_hidden_state[:, 0, :]
        return self.linear(self.drop(pooled))


class BERTPredictor:
    def __init__(self, ckpt_path=CKPT, device=None):
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(
                f"Chưa tìm thấy model: {ckpt_path}\n"
                "Chạy: python src/train_bert.py --model demo"
            )
        self.device = device or torch.device("cpu")
        ck = torch.load(ckpt_path, map_location=self.device)

        # Build model
        from transformers import BertConfig, BertModel
        cfg   = BertConfig(**ck["bert_config"])
        bert  = BertModel(cfg)
        clf   = _BERTClf(bert)
        clf.load_state_dict(ck["model_state"])
        clf.to(self.device).eval()
        self.model = clf

        # Load tokenizer
        vocab_path = os.path.join(MDL_DIR, "tokenizer_vocab.json")
        if os.path.exists(vocab_path):
            with open(vocab_path, encoding="utf-8") as f:
                word2id = json.load(f)
            self.tokenizer = SimpleViTokenizer(word2id)
        else:
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(MDL_DIR)

        self.label_map = LABEL_MAP
        self.accuracy  = ck.get("accuracy", 0)
        self.f1_macro  = ck.get("f1_macro",  0)
        self.model_key = ck.get("model_key", "unknown")

    @torch.no_grad()
    def predict(self, text: str) -> dict:
        enc    = self.tokenizer(text, max_length=128, return_tensors="pt")
        ids    = enc["input_ids"].to(self.device)
        mask   = enc["attention_mask"].to(self.device)
        logits = self.model(ids, mask)
        probs  = torch.softmax(logits, dim=1)
        idx    = probs.argmax(dim=1).item()
        label  = LABEL_MAP[idx]
        return {
            "label":      label,
            "sentiment":  f"{EMOJI_MAP[label]} {label}",
            "confidence": round(probs[0, idx].item(), 4),
            "scores": {
                "NEGATIVE": round(probs[0, 0].item(), 4),
                "NEUTRAL":  round(probs[0, 1].item(), 4),
                "POSITIVE": round(probs[0, 2].item(), 4),
            }
        }

    @torch.no_grad()
    def predict_batch(self, texts: list) -> list:
        return [self.predict(t) for t in texts]
