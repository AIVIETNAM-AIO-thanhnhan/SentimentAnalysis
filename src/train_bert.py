"""
train_bert.py — Fine-tune BERT cho Phân tích Cảm xúc Tiếng Việt
================================================================
Chế độ chạy:
  1. PhoBERT (thật):   python src/train_bert.py --model phobert
  2. mBERT (thật):     python src/train_bert.py --model mbert
  3. Demo (tiny BERT): python src/train_bert.py --model demo

Output:
  models/bert_sentiment/          ← model checkpoint
  models/bert_results.png         ← biểu đồ kết quả
"""

import os, sys, warnings, argparse, time
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings('ignore')

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, f1_score,
                              classification_report, confusion_matrix)
from sklearn.preprocessing import LabelEncoder

# ── Paths ─────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "data",   "cleaned_data.csv")
MDL_DIR   = os.path.join(BASE, "models", "bert_sentiment")
PLOT_PATH = os.path.join(BASE, "models", "bert_results.png")
os.makedirs(MDL_DIR, exist_ok=True)

LABEL_MAP = {"NEGATIVE": 0, "NEUTRAL": 1, "POSITIVE": 2}
ID2LABEL  = {v: k for k, v in LABEL_MAP.items()}
EMOJI     = {0: "😞", 1: "😐", 2: "😊"}

# ─────────────────────────────────────────────────────────────────
# 1. Dataset
# ─────────────────────────────────────────────────────────────────
class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts     = texts
        self.labels    = labels
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels":         torch.tensor(self.labels[idx], dtype=torch.long),
        }

# ─────────────────────────────────────────────────────────────────
# 2. Model wrapper
# ─────────────────────────────────────────────────────────────────
class BERTSentimentClassifier(nn.Module):
    def __init__(self, bert_model, num_labels=3, dropout=0.3):
        super().__init__()
        self.bert    = bert_model
        hidden = bert_model.config.hidden_size
        self.drop    = nn.Dropout(dropout)
        self.linear  = nn.Linear(hidden, num_labels)

    def forward(self, input_ids, attention_mask, labels=None):
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = out.last_hidden_state[:, 0, :]      # [CLS] token
        logits = self.linear(self.drop(pooled))
        loss = None
        if labels is not None:
            loss = nn.CrossEntropyLoss()(logits, labels)
        return loss, logits

# ─────────────────────────────────────────────────────────────────
# 3. Demo tokenizer (không cần HuggingFace)
# ─────────────────────────────────────────────────────────────────
class SimpleViTokenizer:
    """Tokenizer đơn giản word-level cho demo."""
    def __init__(self, vocab_size=5000, max_len=128):
        self.vocab_size = vocab_size
        self.max_len    = max_len
        self.word2id    = {"[PAD]": 0, "[UNK]": 1, "[CLS]": 2, "[SEP]": 3}
        self.fitted     = False

    def fit(self, texts):
        from collections import Counter
        words = []
        for t in texts:
            words.extend(t.lower().split())
        most_common = [w for w, _ in Counter(words).most_common(self.vocab_size - 4)]
        for w in most_common:
            self.word2id[w] = len(self.word2id)
        self.fitted = True
        print(f"   Vocabulary size: {len(self.word2id):,}")

    def __call__(self, text, max_length=128, padding="max_length",
                 truncation=True, return_tensors=None):
        tokens = [self.word2id.get("[CLS]", 2)]
        for w in text.lower().split():
            tokens.append(self.word2id.get(w, self.word2id["[UNK]"]))
        tokens.append(self.word2id.get("[SEP]", 3))
        if truncation and len(tokens) > max_length:
            tokens = tokens[:max_length]
        mask = [1] * len(tokens)
        while len(tokens) < max_length:
            tokens.append(0); mask.append(0)
        input_ids      = torch.tensor([tokens], dtype=torch.long)
        attention_mask = torch.tensor([mask],   dtype=torch.long)
        if return_tensors == "pt":
            return {"input_ids": input_ids, "attention_mask": attention_mask}
        return {"input_ids": input_ids, "attention_mask": attention_mask}

# ─────────────────────────────────────────────────────────────────
# 4. Demo BERT model (không cần HuggingFace)
# ─────────────────────────────────────────────────────────────────
def build_demo_bert(vocab_size=5000):
    """Tiny BERT khởi tạo ngẫu nhiên — chạy được ngay, không cần download."""
    from transformers import BertConfig, BertModel
    config = BertConfig(
        vocab_size       = vocab_size,
        hidden_size      = 128,
        num_hidden_layers= 2,
        num_attention_heads = 2,
        intermediate_size= 256,
        max_position_embeddings = 256,
        num_labels       = 3,
    )
    return BertModel(config)

# ─────────────────────────────────────────────────────────────────
# 5. Training loop
# ─────────────────────────────────────────────────────────────────
def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss, preds_all, labels_all = 0.0, [], []
    for batch in loader:
        ids   = batch["input_ids"].to(device)
        mask  = batch["attention_mask"].to(device)
        lbls  = batch["labels"].to(device)
        optimizer.zero_grad()
        loss, logits = model(ids, mask, lbls)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item()
        preds_all.extend(logits.argmax(dim=1).cpu().tolist())
        labels_all.extend(lbls.cpu().tolist())
    return (total_loss / len(loader),
            accuracy_score(labels_all, preds_all),
            f1_score(labels_all, preds_all, average='macro'))

@torch.no_grad()
def eval_epoch(model, loader, device):
    model.eval()
    total_loss, preds_all, labels_all = 0.0, [], []
    for batch in loader:
        ids   = batch["input_ids"].to(device)
        mask  = batch["attention_mask"].to(device)
        lbls  = batch["labels"].to(device)
        loss, logits = model(ids, mask, lbls)
        total_loss += loss.item()
        preds_all.extend(logits.argmax(dim=1).cpu().tolist())
        labels_all.extend(lbls.cpu().tolist())
    return (total_loss / len(loader),
            accuracy_score(labels_all, preds_all),
            f1_score(labels_all, preds_all, average='macro'),
            preds_all, labels_all)

# ─────────────────────────────────────────────────────────────────
# 6. Main
# ─────────────────────────────────────────────────────────────────
def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Device : {device}")

    # ── Load data ────────────────────────────────────────────────
    print("\n📂 Loading data...")
    df = pd.read_csv(DATA_PATH)
    df.dropna(subset=["clean_comment","sentiment"], inplace=True)
    df["clean_comment"] = df["clean_comment"].astype(str).str.strip()
    df = df[df["clean_comment"].str.len() > 1]
    df["label"] = df["sentiment"].map(LABEL_MAP)
    print(f"   Samples : {len(df):,}")
    print(f"   Labels  : {df['sentiment'].value_counts().to_dict()}")

    texts  = df["clean_comment"].tolist()
    labels = df["label"].tolist()
    X_tr, X_te, y_tr, y_te = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels)

    # ── Tokenizer & Model ─────────────────────────────────────────
    MODEL_NAMES = {
        "phobert": "vinai/phobert-base",
        "mbert":   "bert-base-multilingual-cased",
        "demo":    "DEMO",
    }
    model_key  = args.model.lower()
    model_name = MODEL_NAMES.get(model_key, "DEMO")
    print(f"\n🤖 Model  : {model_name}")

    if model_key == "demo":
        print("⚡ Demo mode — khởi tạo TinyBERT ngẫu nhiên (không cần HuggingFace)")
        tokenizer  = SimpleViTokenizer(vocab_size=4000, max_len=128)
        tokenizer.fit(X_tr)
        bert_core  = build_demo_bert(vocab_size=len(tokenizer.word2id))
    else:
        print("⬇️  Tải model từ HuggingFace...")
        try:
            from transformers import AutoTokenizer, AutoModel
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            bert_core = AutoModel.from_pretrained(model_name)
            print(f"   ✅ Tải thành công: {model_name}")
        except Exception as e:
            print(f"   ❌ Không tải được ({e})")
            print("   ⚡ Fallback → Demo mode")
            tokenizer  = SimpleViTokenizer(vocab_size=4000, max_len=128)
            tokenizer.fit(X_tr)
            bert_core  = build_demo_bert(vocab_size=len(tokenizer.word2id))

    model = BERTSentimentClassifier(bert_core, num_labels=3).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"   Parameters: {n_params:,}")

    # ── DataLoaders ───────────────────────────────────────────────
    bs = args.batch_size
    train_ds = SentimentDataset(X_tr, y_tr, tokenizer, max_len=128)
    test_ds  = SentimentDataset(X_te, y_te, tokenizer, max_len=128)
    train_dl = DataLoader(train_ds, batch_size=bs, shuffle=True,  num_workers=0)
    test_dl  = DataLoader(test_ds,  batch_size=bs, shuffle=False, num_workers=0)
    print(f"\n   Train : {len(train_ds):,}  |  Test : {len(test_ds):,}")
    print(f"   Batch : {bs}  |  Steps/epoch : {len(train_dl)}")

    # ── Optimizer ─────────────────────────────────────────────────
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    # ── Training ──────────────────────────────────────────────────
    print(f"\n{'═'*54}")
    print(f"  🚀 BẮT ĐẦU TRAINING — {args.epochs} epochs")
    print(f"{'═'*54}")

    history = {"tr_loss":[], "tr_acc":[], "tr_f1":[],
               "va_loss":[], "va_acc":[], "va_f1":[]}
    best_f1, best_state = 0.0, None

    for epoch in range(1, args.epochs + 1):
        t0 = time.perf_counter()
        tr_loss, tr_acc, tr_f1 = train_epoch(model, train_dl, optimizer, device)
        va_loss, va_acc, va_f1, va_preds, va_labels = eval_epoch(model, test_dl, device)
        elapsed = time.perf_counter() - t0

        for k, v in zip(["tr_loss","tr_acc","tr_f1","va_loss","va_acc","va_f1"],
                        [tr_loss, tr_acc, tr_f1, va_loss, va_acc, va_f1]):
            history[k].append(v)

        flag = ""
        if va_f1 > best_f1:
            best_f1   = va_f1
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            flag = " 🏆"

        print(f"  Epoch {epoch:02d}/{args.epochs}  "
              f"[Train] loss={tr_loss:.4f} acc={tr_acc:.4f} f1={tr_f1:.4f}  "
              f"[Val] loss={va_loss:.4f} acc={va_acc:.4f} f1={va_f1:.4f}  "
              f"{elapsed:.1f}s{flag}")

    # ── Best model ────────────────────────────────────────────────
    model.load_state_dict(best_state)
    _, _, _, final_preds, final_labels = eval_epoch(model, test_dl, device)

    print(f"\n{'═'*54}")
    print(f"  ✅ BEST Val Macro-F1 : {best_f1:.4f}")
    print(f"{'═'*54}")
    print(classification_report(final_labels, final_preds,
          target_names=["NEGATIVE","NEUTRAL","POSITIVE"]))

    # ── Save ──────────────────────────────────────────────────────
    torch.save({
        "model_state": best_state,
        "bert_config": bert_core.config.to_dict(),
        "model_key":   model_key,
        "label_map":   LABEL_MAP,
        "accuracy":    accuracy_score(final_labels, final_preds),
        "f1_macro":    best_f1,
    }, os.path.join(MDL_DIR, "bert_model.pt"))

    # Lưu tokenizer
    if model_key == "demo":
        import json
        with open(os.path.join(MDL_DIR, "tokenizer_vocab.json"), "w", encoding="utf-8") as f:
            json.dump(tokenizer.word2id, f, ensure_ascii=False)
    else:
        tokenizer.save_pretrained(MDL_DIR)

    print(f"💾 Saved → {MDL_DIR}/")

    # ── Plot ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("BERT Vietnamese Sentiment — Training Results", fontsize=14, fontweight="bold")

    epochs_x = range(1, args.epochs + 1)

    # Loss curve
    ax = axes[0]
    ax.plot(epochs_x, history["tr_loss"], "b-o", label="Train", markersize=4)
    ax.plot(epochs_x, history["va_loss"], "r-o", label="Val",   markersize=4)
    ax.set_title("Loss"); ax.set_xlabel("Epoch"); ax.legend()
    ax.spines[["top","right"]].set_visible(False)

    # Accuracy & F1
    ax = axes[1]
    ax.plot(epochs_x, history["tr_acc"], "b-o",  label="Train Acc", markersize=4)
    ax.plot(epochs_x, history["va_acc"], "r-o",  label="Val Acc",   markersize=4)
    ax.plot(epochs_x, history["tr_f1"],  "b--s", label="Train F1",  markersize=4)
    ax.plot(epochs_x, history["va_f1"],  "r--s", label="Val F1",    markersize=4)
    ax.set_ylim(0, 1.05); ax.set_title("Accuracy & Macro-F1")
    ax.set_xlabel("Epoch"); ax.legend(fontsize=8)
    ax.spines[["top","right"]].set_visible(False)

    # Confusion matrix
    ax = axes[2]
    cm = confusion_matrix(final_labels, final_preds, labels=[0,1,2])
    sns.heatmap(cm.astype(float)/cm.sum(axis=1, keepdims=True)*100,
                annot=True, fmt=".1f", cmap="Blues", ax=ax,
                xticklabels=["NEG","NEU","POS"],
                yticklabels=["NEG","NEU","POS"],
                linewidths=0.5, cbar_kws={"label":"%"})
    ax.set_title(f"Confusion Matrix (Best F1={best_f1:.3f})")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")

    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150, bbox_inches="tight")
    print(f"📊 Plot   → {PLOT_PATH}")
    print("✅ Done!")
    return best_f1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",      default="demo",
                        choices=["phobert","mbert","demo"],
                        help="Model: phobert | mbert | demo")
    parser.add_argument("--epochs",     type=int,   default=10)
    parser.add_argument("--batch_size", type=int,   default=16)
    parser.add_argument("--lr",         type=float, default=2e-4)
    args = parser.parse_args()
    main(args)
