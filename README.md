# 🛍️ Vietnamese AI Sentiment Analysis System

Phân tích cảm xúc đánh giá sản phẩm tiếng Việt với hỗ trợ:

- TF-IDF + Machine Learning (Logistic Regression / SVM / Naive Bayes)
- BERT (PhoBERT / mBERT / Demo model)
- FastAPI inference service
- Streamlit dashboard
- Automated testing
- Dockerized deployment
- CI/CD với GitHub Actions
- Auto-generated reports

![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)

---

# 📁 Project Structure

```text
SentimentAnalysis/
│
├── src/
│   ├── train.py                  # Train TF-IDF models
│   ├── train_bert.py             # Fine-tune BERT models
│   └── bert_inference.py         # BERT inference helper
│
├── api/
│   └── main.py                   # FastAPI backend
│
├── ui/
│   └── app.py                    # Streamlit dashboard
│
├── tests/
│   ├── test_model.py
│   ├── test_bert.py
│   └── test_api.py
│
├── data/
│   └── generate_sample.py
│
├── models/                       # Generated after training
│
├── reports/                      # Generated reports
│
├── ci.sh                         # Local CI pipeline
├── docker-compose.yml
├── requirements.txt
│
└── .github/
    └── workflows/
```

---

# ⚙️ Installation

## Clone repository

```bash
git clone https://github.com/<your-username>/SentimentAnalysis.git

cd SentimentAnalysis
```

## Create virtual environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

## Install dependencies

CPU:

```bash
pip install -r requirements.txt
```

GPU (NVIDIA):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt
```

---

# 🚀 Quick Start

## Step 1: Generate sample data

```bash
python data/generate_sample.py
```

## Step 2: Train BERT (Demo mode)

```bash
python src/train_bert.py --model demo --epochs 10
```

## Step 3: Run tests

```bash
python tests/test_bert.py
```

---

# 🤖 Train BERT Models

## Demo mode

No internet required:

```bash
python src/train_bert.py --model demo --epochs 10
```

## PhoBERT

Recommended for Vietnamese:

```bash
python src/train_bert.py \
--model phobert \
--epochs 5 \
--lr 2e-5
```

## mBERT

```bash
python src/train_bert.py \
--model mbert \
--epochs 5 \
--lr 2e-5
```

## Available Parameters

| Parameter | Default | Description |
|------------|----------|-------------|
| --model | demo | demo / phobert / mbert |
| --epochs | 10 | Number of epochs |
| --batch_size | 16 | Batch size |
| --lr | 2e-4 | Learning rate |

Generated output:

```text
models/
├── bert_sentiment/
│   ├── bert_model.pt
│   └── tokenizer_vocab.json
│
└── bert_results.png
```

---

# 📊 Train TF-IDF Models

```bash
python src/train.py
```

Models evaluated:

- Logistic Regression
- LinearSVC
- Naive Bayes

Generated:

```text
models/
└── sentiment_model.joblib
```

---

# 🌐 Run API

Start FastAPI server:

```bash
uvicorn api.main:app \
--host 0.0.0.0 \
--port 8000 \
--reload
```

Open:

```text
http://localhost:8000/docs
```

---

# 🖥️ Run Streamlit Dashboard

```bash
streamlit run ui/app.py
```

Open:

```text
http://localhost:8501
```

---

# 🐳 Run with Docker

## Build system

```bash
docker compose build
```

## Start services

```bash
docker compose up -d api ui
```

Services:

```text
API → http://localhost:8000/docs

UI → http://localhost:8501
```

---

## Train model manually

```bash
docker compose run --rm train-model
```

---

## Run tests manually

```bash
docker compose run --rm test-model

docker compose run --rm test-api

docker compose run --rm test-ui
```

---

# 🧪 Run Tests Locally

TF-IDF:

```bash
python tests/test_model.py
```

BERT:

```bash
python tests/test_bert.py
```

API:

```bash
python tests/test_api.py
```

Expected:

```text
🎉 ALL TESTS PASSED

✅ Accuracy=0.9531
✅ Macro-F1=0.9473
```

---

# ⚙️ Local CI Pipeline

Run:

```bash
bash ci.sh
```

Pipeline includes:

```text
✔ Build Docker images
✔ Start API + UI
✔ Wait for services
✔ Train model
✔ Run model tests
✔ Run API tests
✔ Run UI tests
✔ Generate reports
✔ Cleanup containers
```

---

# ⚙️ GitHub Actions CI/CD

Trigger events:

```text
✔ Push to main
✔ Pull Request
```

Pipeline:

```text
✔ Checkout code
✔ Build Docker images
✔ Start services
✔ Train model
✔ Run tests
✔ Generate reports
✔ Upload artifacts
✔ Cleanup
```

Download reports:

```text
GitHub
→ Actions
→ Latest workflow run
→ Download test-reports artifact
```

---

# 📊 Reports

Generated automatically:

```text
reports/
├── api_test_results.pdf
├── model_train_results.png
├── bert_results.png
```

---

# 🐍 System Requirements

| Component | Minimum | Recommended |
|------------|----------|-------------|
| Python | 3.9+ | 3.11 |
| RAM | 4 GB | 8 GB |
| GPU | Optional | NVIDIA ≥ 4GB VRAM |
| Disk | 500 MB | 2 GB |

---

# ❓ Common Issues

### ModuleNotFoundError: torch

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Could not connect to HuggingFace

```bash
python src/train_bert.py --model demo
```

### FileNotFoundError: data/cleaned_data.csv

```bash
python data/generate_sample.py
```

---

# 🧠 Summary

```text
✔ Vietnamese sentiment analysis
✔ TF-IDF + BERT support
✔ FastAPI backend
✔ Streamlit UI
✔ Docker deployment
✔ Automated testing
✔ CI/CD integration
✔ Report generation
✔ Production-ready structure
```