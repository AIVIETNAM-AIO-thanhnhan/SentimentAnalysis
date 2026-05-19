# 🛍️ Vietnamese Sentiment Analysis

Phân tích cảm xúc đánh giá sản phẩm tiếng Việt — hỗ trợ **TF-IDF** và **BERT**.

---

## 📁 Cấu trúc project

```
SentimentAnalysis/
├── src/
│   ├── train.py              # Train TF-IDF (Logistic Regression / SVM / Naive Bayes)
│   ├── train_bert.py         # Fine-tune BERT (PhoBERT / mBERT / demo)
│   └── bert_inference.py     # Inference helper
├── api/
│   └── main.py               # FastAPI server
├── tests/
│   ├── test_model.py         # Test TF-IDF model
│   └── test_bert.py          # Test BERT model
├── data/
│   └── generate_sample.py    # Tạo dữ liệu mẫu
├── models/                   # Được tạo tự động sau khi train
├── requirements.txt
└── README.md
```

---

## ⚙️ Cài đặt

### Bước 1 — Clone repo

```bash
git clone https://github.com/<your-username>/SentimentAnalysis.git
cd SentimentAnalysis
```

### Bước 2 — Tạo virtual environment (khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Bước 3 — Cài thư viện

```bash
# CPU (máy thường)
pip install -r requirements.txt

# GPU NVIDIA (nếu có — train nhanh hơn ~10x)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

---

## 🚀 Chạy nhanh (3 bước)

```bash
# 1. Tạo dữ liệu mẫu
python data/generate_sample.py

# 2. Train BERT (demo mode — không cần internet)
python src/train_bert.py --model demo --epochs 10

# 3. Kiểm tra
python tests/test_bert.py
```

---

## 🤖 Train BERT

### Demo mode (không cần internet, chạy được ngay)

```bash
python src/train_bert.py --model demo --epochs 10
```

### PhoBERT (tiếng Việt, cần internet, kết quả tốt nhất)

```bash
python src/train_bert.py --model phobert --epochs 5 --lr 2e-5
```

### mBERT (đa ngôn ngữ, cần internet)

```bash
python src/train_bert.py --model mbert --epochs 5 --lr 2e-5
```

### Tùy chỉnh tham số

| Tham số | Mặc định | Mô tả |
|---|---|---|
| `--model` | `demo` | `demo` / `phobert` / `mbert` |
| `--epochs` | `10` | Số epoch huấn luyện |
| `--batch_size` | `16` | Batch size |
| `--lr` | `2e-4` | Learning rate |

Output sau khi train:
```
models/
├── bert_sentiment/
│   ├── bert_model.pt          ← checkpoint
│   └── tokenizer_vocab.json   ← vocabulary
└── bert_results.png           ← biểu đồ loss / accuracy
```

---

## 📊 Train TF-IDF

```bash
python src/train.py
```

So sánh 3 model: Logistic Regression, LinearSVC, Naive Bayes. Output: `models/sentiment_model.joblib`.

---

## 🧪 Chạy Tests

```bash
# Test TF-IDF
python tests/test_model.py

# Test BERT
python tests/test_bert.py
```

Kết quả kỳ vọng:
```
🎉 TẤT CẢ TESTS ĐỀU PASS
✅ Accuracy=0.9531  Macro-F1=0.9473
✅ BERT sẵn sàng đẩy lên GitHub!
```

---

## 🌐 Chạy API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Mở trình duyệt: `http://localhost:8000/docs`

---

## 🐍 Yêu cầu hệ thống

| Thành phần | Tối thiểu | Khuyến nghị |
|---|---|---|
| Python | 3.9+ | 3.11 |
| RAM | 4 GB | 8 GB |
| GPU | Không cần | NVIDIA ≥ 4GB VRAM |
| Disk | 500 MB | 2 GB (cho PhoBERT) |

---

## ❓ Lỗi thường gặp

**`ModuleNotFoundError: No module named 'torch'`**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**`We couldn't connect to huggingface.co`**
```bash
# Dùng demo mode thay thế
python src/train_bert.py --model demo
```

**`FileNotFoundError: data/cleaned_data.csv`**
```bash
python data/generate_sample.py
```
